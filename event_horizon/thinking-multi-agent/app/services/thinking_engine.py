"""ReAct thinking loop — iterative tool-calling agent."""

import json
import logging
import re
from typing import Any, Dict, List

from services.data_agents import execute_tool, summarize_data, summarize_tool_result
from services.llm import call_llm

logger = logging.getLogger(__name__)

TOOLS_DESCRIPTION = {
    "candlestick": "OHLCV price data including open, high, low, close, volume for each trading day",
    "earnings": "Financial reports, quarterly earnings, EPS history, revenue data",
    "news": "Recent news articles, headlines, and press releases about the stocks",
    "technical": "Technical indicators including RSI, MACD, SMA, EMA, Bollinger Bands",
    "fundamentals": "Fundamental metrics like P/E ratio, P/B ratio, EPS, dividend yield, market cap",
    "web_search": "Web search for any topic: sentiment, analyst ratings, industry context, company background, etc. Specify the topic in your reasoning.",
}

THINK_PROMPT_BASE = """You are an intelligent financial analysis agent with access to data tools.

Your task: {system_prompt}

Available data tools (ONLY request tools from this list):
{tools_description}

Current context:
- Stocks: {stocks}
- Data already collected: {collected_data_summary}

IMPORTANT: Do NOT request a tool that is already listed in 'Data already collected'. Pick a DIFFERENT tool or generate your response.
IMPORTANT: If NONE of the available tools can provide the specific data your task requires, use generate_response immediately — do NOT call irrelevant tools hoping they might help.

Decide your next action. You must respond in JSON only (no markdown, no explanation):

Option 1 - Need more data (pick a tool from the available list above):
{{"action": "call_tool", "tool": "tool_name", "search_topic": "topic keywords for web_search (only needed for web_search tool)", "reasoning": "why I need this data"}}
"""

THINK_PROMPT_CREATE_AGENT = """
Option 2 - Need specialized data that existing tools don't provide:
{{"action": "create_data_agent", "agent_name": "Name for the agent", "agent_description": "Describe what data this agent should fetch", "data_type": "what kind of data (e.g., options chain, insider trading, SEC filings)", "reasoning": "why existing tools don't have this data"}}
"""

THINK_PROMPT_TAIL = """
Option {final_option_num} - Ready to answer (have sufficient data):
{{"action": "generate_response", "reasoning": "I have sufficient data because..."}}

Think step by step. What data do you need to complete the analysis?"""


def _clean_json(text: str) -> str:
    """Strip markdown fences from LLM output."""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t


async def think_step(
    system_prompt: str, context: dict, available_tools: List[str],
    allow_agent_creation: bool = True,
) -> dict:
    """One iteration: ask LLM what action to take next."""
    stocks = context.get("stocks", [])
    collected_data = context.get("data", {})

    if available_tools:
        tools_desc = "\n".join(
            f"- {t}: {TOOLS_DESCRIPTION.get(t, 'Custom data tool')}" for t in available_tools
        )
    else:
        tools_desc = "(No additional standard tools available — all data has been collected)"
    data_summary = summarize_data(collected_data)

    # Build prompt: include create_data_agent option only when allowed
    prompt = THINK_PROMPT_BASE.format(
        system_prompt=system_prompt,
        tools_description=tools_desc,
        stocks=stocks,
        collected_data_summary=data_summary,
    )
    if allow_agent_creation:
        prompt += THINK_PROMPT_CREATE_AGENT
        prompt += THINK_PROMPT_TAIL.format(final_option_num=3)
    else:
        prompt += THINK_PROMPT_TAIL.format(final_option_num=2)
    logger.info(
        "think_step: prompt_len=%d, stocks=%s, collected_data_keys=%s, available_tools=%s",
        len(prompt), stocks, list(collected_data.keys()), available_tools,
    )
    logger.debug("think_step: full prompt:\n%s", prompt)

    try:
        response = await call_llm(prompt)
        logger.info("think_step: raw LLM response:\n%s", response)
        thought = json.loads(_clean_json(response))
        logger.info(
            "think_step: parsed action=%s, tool=%s, reasoning=%s",
            thought.get("action"), thought.get("tool"), thought.get("reasoning"),
        )
        if thought.get("action") == "create_data_agent":
            logger.info(
                "think_step: create_data_agent details — agent_name=%s, data_type=%s, agent_description=%s",
                thought.get("agent_name"), thought.get("data_type"), thought.get("agent_description"),
            )
        return thought
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse thinking JSON: %s — raw response:\n%s", e, response)
        return {"action": "generate_response", "reasoning": "Could not parse LLM response, generating final response"}
    except Exception as e:
        logger.error("Think step failed: %s", e)
        return {"action": "generate_response", "reasoning": f"Error in thinking: {e}"}


async def generate_final_response(system_prompt: str, context: dict) -> dict:
    """Generate final analysis from collected data."""
    stocks = context.get("stocks", [])
    collected_data = context.get("data", {})
    data_json = json.dumps(collected_data, indent=2, default=str)
    logger.info(
        "generate_final_response: stocks=%s, data_keys=%s, total_data_len=%d",
        stocks, list(collected_data.keys()), len(data_json),
    )

    # Truncate for LLM but log full length
    truncated_data = data_json[:8000]
    if len(data_json) > 8000:
        logger.info(
            "generate_final_response: data truncated from %d to 8000 chars for LLM prompt",
            len(data_json),
        )

    prompt = f"""Based on the following data, provide your analysis.

Your role: {system_prompt}

Stocks: {stocks}

Available data:
{truncated_data}

Provide your final analysis in JSON format. Include:
- summary: Brief overview of your findings
- recommendations: List of actionable recommendations
- confidence: Your confidence level (0-1)
- key_insights: Most important findings
- risks: Any risks or caveats to note"""

    logger.debug("generate_final_response: full prompt:\n%s", prompt)

    try:
        response = await call_llm(prompt)
        logger.info("generate_final_response: raw LLM response:\n%s", response)
        try:
            parsed = json.loads(_clean_json(response))
            logger.info(
                "generate_final_response: parsed response keys=%s",
                list(parsed.keys()) if isinstance(parsed, dict) else type(parsed).__name__,
            )
            return parsed
        except json.JSONDecodeError:
            logger.warning(
                "generate_final_response: could not parse as JSON, returning raw. response_len=%d",
                len(response),
            )
            return {"summary": response, "raw_response": True}
    except Exception as e:
        logger.error("Final response generation failed: %s", e)
        return {"error": str(e)}


def _build_data_agent_prompt_template(
    thought: dict, stocks: List[str] = None, analyzer_task: str = "",
) -> str:
    """Build an enhanced fallback system prompt for a custom data agent.

    Used when the LLM meta-prompt call fails or returns an unusable result.
    """
    data_type = thought.get("data_type", "specialized data")
    agent_name = thought.get("agent_name", "Custom Data Agent")
    description = thought.get("agent_description", "Retrieve and process financial data")
    stocks_str = ", ".join(stocks) if stocks else "the given stocks"

    prompt = f"""You are a specialized {data_type} data retrieval agent ("{agent_name}").

Your job: {description}

Target stocks: {stocks_str}
{"Analysis context: " + analyzer_task if analyzer_task else ""}

## Data Retrieval Strategy

You have access to the `web_search` tool. Use it effectively:
1. Search for specific, targeted queries — e.g. "{stocks_str} {data_type} 2024 2025"
2. Try multiple search angles if the first query doesn't yield good results
3. Look for authoritative sources (SEC EDGAR, company IR pages, financial databases)
4. Extract specific numbers, dates, and facts — not just summaries

## Suggested search queries:
- "{stocks_str} {data_type} latest"
- "{stocks_str} {data_type} SEC filing"
- "{stocks_str} {data_type} financial data 2025"

## What to collect for each stock:
- Key data points relevant to {data_type}
- Dates and time periods covered
- Source URLs for verification
- Any notable trends or changes

## Output format:
Return structured JSON:
{{
    "status": "success",
    "data": {{
        "<SYMBOL>": {{
            "data_type": "{data_type}",
            "key_findings": ["finding1", "finding2"],
            "data_points": {{}},
            "sources": ["url1", "url2"],
            "period_covered": "date range"
        }}
    }},
    "metadata": {{
        "retrieved_at": "ISO timestamp",
        "source": "data source name",
        "query_strategy": "description of search approach"
    }}
}}"""
    logger.info(
        "_build_data_agent_prompt_template: data_type=%s, stocks=%s, prompt_len=%d",
        data_type, stocks, len(prompt),
    )
    return prompt


async def generate_data_agent_prompt(
    thought: dict, stocks: List[str] = None, analyzer_task: str = "",
) -> str:
    """Generate a rich system prompt for a custom data agent via LLM meta-prompting.

    Falls back to _build_data_agent_prompt_template() if the LLM call fails.
    """
    data_type = thought.get("data_type", "specialized data")
    agent_name = thought.get("agent_name", "Custom Data Agent")
    description = thought.get("agent_description", "Retrieve and process financial data")
    stocks_str = ", ".join(stocks) if stocks else "financial stocks"

    meta_prompt = (
        f"You are an expert at creating system prompts for AI data-retrieval agents in a financial analysis system.\n\n"
        f"Create a detailed system prompt for a data agent with these characteristics:\n\n"
        f"**Agent Name:** {agent_name}\n"
        f"**Data Type:** {data_type}\n"
        f"**Description:** {description}\n"
        f"**Target Stocks:** {stocks_str}\n"
        f"**Analysis Context:** {analyzer_task or 'General financial analysis'}\n\n"
        f"The agent has access to a `web_search` tool and must retrieve real data.\n\n"
        f"The system prompt MUST include:\n"
        f"1. Clear role definition — what specific {data_type} data to retrieve\n"
        f"2. Specific data points to look for (e.g., exact metrics, filing types, date ranges)\n"
        f"3. Search strategy — 3-5 concrete example search queries using the target stocks\n"
        f"4. Quality checks — how to validate the data is accurate and current\n"
        f"5. Structured JSON output format with fields specific to {data_type}\n"
        f"6. Instructions to include source URLs and retrieval timestamps\n\n"
        f'Write ONLY the system prompt. Start directly with "You are..."'
    )

    logger.info(
        "generate_data_agent_prompt: calling LLM meta-prompt for data_type=%s, stocks=%s",
        data_type, stocks,
    )

    try:
        result = await call_llm(meta_prompt)
        cleaned = result.strip() if result else ""

        if len(cleaned) >= 100:
            logger.info(
                "generate_data_agent_prompt: LLM meta-prompt success, prompt_len=%d",
                len(cleaned),
            )
            return cleaned

        logger.warning(
            "generate_data_agent_prompt: LLM returned short/empty result (len=%d), falling back to template",
            len(cleaned),
        )
    except Exception as e:
        logger.warning(
            "generate_data_agent_prompt: LLM meta-prompt failed (%s), falling back to template", e,
        )

    return _build_data_agent_prompt_template(thought, stocks, analyzer_task)


DISCOVER_TOOLS_PROMPT = """You are an intelligent financial analysis planner. Given an analysis task and available data tools, determine ALL data sources needed in a single response.

Your analysis task: {system_prompt}

Target stocks: {stocks}

Available standard data tools:
{tools_description}

Instructions:
1. Consider what data is needed to fully complete the analysis task.
2. Select ALL relevant standard tools from the list above — do not hold back, list every tool whose data would be useful.
3. If the task requires specialized data NOT covered by any standard tool (e.g., options chains, insider trading, SEC filings, alternative data), suggest custom data agents for those needs.

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "standard": ["tool_name_1", "tool_name_2", ...],
  "custom": [
    {{"name": "agent-name", "description": "what data it fetches", "data_type": "category of data"}},
    ...
  ],
  "reasoning": "brief explanation of why these tools were selected"
}}

Rules:
- "standard" must only contain names from the available tools list above
- "custom" should be an empty array [] if standard tools are sufficient
- Only suggest custom agents for truly exotic data needs that no standard tool covers
- Be thorough — include ALL tools that provide relevant data for the task"""


async def discover_required_tools(
    system_prompt: str,
    stocks: list[str],
    available_tools: list[str],
) -> dict:
    """Single-shot discovery: one LLM call returns all needed data sources.

    Returns {"standard": ["candlestick", ...], "custom": [{"name": ..., "description": ..., "data_type": ...}]}
    """
    tools_desc = "\n".join(
        f"- {t}: {TOOLS_DESCRIPTION.get(t, 'Custom data tool')}" for t in available_tools
    )
    prompt = DISCOVER_TOOLS_PROMPT.format(
        system_prompt=system_prompt,
        stocks=stocks,
        tools_description=tools_desc,
    )
    logger.info(
        "discover_required_tools: stocks=%s, available_tools=%s, prompt_len=%d",
        stocks, available_tools, len(prompt),
    )

    try:
        response = await call_llm(prompt)
        logger.info("discover_required_tools: raw LLM response:\n%s", response)
        parsed = json.loads(_clean_json(response))

        # Validate standard tools against available list
        standard = [t for t in parsed.get("standard", []) if t in available_tools]
        custom = parsed.get("custom", [])
        if not isinstance(custom, list):
            custom = []

        logger.info(
            "discover_required_tools: standard=%s, custom_count=%d, reasoning=%s",
            standard, len(custom), parsed.get("reasoning", ""),
        )
        return {"standard": standard, "custom": custom}
    except json.JSONDecodeError as e:
        logger.warning("discover_required_tools: JSON parse failed: %s — raw:\n%s", e, response)
        # Fallback: return all available tools as standard
        return {"standard": available_tools, "custom": []}
    except Exception as e:
        logger.error("discover_required_tools: failed: %s", e)
        return {"standard": available_tools, "custom": []}


async def run_thinking_loop(
    stocks: List[str],
    system_prompt: str,
    input_data: dict = None,
    max_iterations: int = 5,
    available_tools: List[str] = None,
    discovery_only: bool = False,
    allow_agent_creation: bool = True,
) -> dict:
    """Execute the full ReAct thinking loop.

    When discovery_only=True, tools are not executed — the loop only discovers
    which tools the LLM wants. Returns tools_discovered list instead of results.

    When allow_agent_creation=False, the LLM prompt omits the create_data_agent
    option, forcing it to use available tools (e.g. web_search) or generate a
    response directly. Used for exotic agent fetch mode.
    """
    if available_tools is None:
        available_tools = ["candlestick", "earnings", "news", "technical", "fundamentals"]

    logger.info(
        "=== THINKING LOOP START === stocks=%s, max_iterations=%d, tools=%s, has_input_data=%s, discovery_only=%s",
        stocks, max_iterations, available_tools, input_data is not None, discovery_only,
    )
    if input_data:
        logger.info("Thinking loop input_data keys: %s", list(input_data.keys()))
        logger.debug("Thinking loop input_data: %s", json.dumps(input_data, indent=2, default=str))

    thinking_steps = []
    context = {"stocks": stocks, "data": input_data.copy() if input_data else {}}
    final_result = None
    tools_used = []
    tools_discovered: List[str] = []
    consecutive_skip_count = 0
    last_skipped_tool = None

    for iteration in range(1, max_iterations + 1):
        logger.info("=== ITERATION %d/%d ===", iteration, max_iterations)
        logger.info("Iteration %d: context data_keys=%s, tools_used_so_far=%s", iteration, list(context["data"].keys()), tools_used)

        # Core fix: filter out already-collected tools so the LLM sees a shrinking list
        remaining_tools = [t for t in available_tools if t not in context["data"]]
        logger.info("Iteration %d: remaining_tools=%s (filtered from %s)", iteration, remaining_tools, available_tools)

        if not remaining_tools and not allow_agent_creation:
            # No tools left and can't create exotic agents — generate final response immediately
            logger.info("Iteration %d: no remaining tools and allow_agent_creation=False — forcing final response", iteration)
            if discovery_only:
                thinking_steps.append({
                    "iteration": iteration, "thought": "All standard tools discovered",
                    "action": "generate_response_discovery",
                })
            else:
                final_result = await generate_final_response(system_prompt, context)
                thinking_steps.append({
                    "iteration": iteration, "thought": "All available tools exhausted",
                    "action": "generate_response", "result": final_result,
                })
            break

        thought = await think_step(system_prompt, context, remaining_tools, allow_agent_creation=allow_agent_creation)
        action = thought.get("action", "generate_response")
        reasoning = thought.get("reasoning", "")
        logger.info("Iteration %d: action=%s, tool=%s, reasoning=%s", iteration, action, thought.get("tool"), reasoning)

        if action == "call_tool":
            tool_name = thought.get("tool", "")

            if tool_name not in remaining_tools:
                logger.warning(
                    "Iteration %d: tool '%s' not in remaining tools %s — skipping",
                    iteration, tool_name, remaining_tools,
                )
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "error", "error": f"Tool '{tool_name}' not in available tools",
                })
                continue

            if tool_name in context["data"]:
                # Consecutive-skip guard: break after 2 consecutive skips of already-discovered tools
                if tool_name == last_skipped_tool:
                    consecutive_skip_count += 1
                else:
                    consecutive_skip_count = 1
                    last_skipped_tool = tool_name

                logger.info(
                    "Iteration %d: already have '%s' data — skipping (consecutive_skip=%d)",
                    iteration, tool_name, consecutive_skip_count,
                )
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "skip", "message": f"Already have {tool_name} data",
                })

                if consecutive_skip_count >= 2:
                    logger.info(
                        "Iteration %d: breaking out — %d consecutive skips of '%s'",
                        iteration, consecutive_skip_count, tool_name,
                    )
                    break
                continue

            # Reset consecutive skip counter on successful new tool
            consecutive_skip_count = 0
            last_skipped_tool = None

            if discovery_only:
                # Discovery mode: don't execute the tool, just record it
                logger.info("Iteration %d: DISCOVERY — recording tool '%s' (not executing)", iteration, tool_name)
                tools_discovered.append(tool_name)
                context["data"][tool_name] = {"_discovered": True}
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "discover_tool", "tool": tool_name,
                })
            else:
                logger.info("Iteration %d: executing tool '%s' for stocks=%s", iteration, tool_name, stocks)
                # For web_search, use search_topic from LLM or fall back to reasoning
                overrides = {}
                if tool_name == "web_search":
                    search_topic = thought.get("search_topic") or reasoning or ""
                    if search_topic:
                        overrides["topic"] = search_topic[:200]
                tool_result = await execute_tool(tool_name, stocks, **overrides)
                context["data"][tool_name] = tool_result
                tools_used.append(tool_name)

                tool_summary = summarize_tool_result(tool_name, tool_result)
                logger.info("Iteration %d: tool '%s' complete — summary: %s", iteration, tool_name, tool_summary)
                logger.debug(
                    "Iteration %d: tool '%s' full result:\n%s",
                    iteration, tool_name, json.dumps(tool_result, indent=2, default=str)[:5000],
                )

                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "call_tool", "tool": tool_name,
                    "tool_result_summary": tool_summary,
                })

        elif action == "create_data_agent":
            if not allow_agent_creation:
                # Safety net: LLM chose create_data_agent despite prompt not offering it
                logger.warning(
                    "Iteration %d: LLM chose create_data_agent but allow_agent_creation=False — forcing final response",
                    iteration,
                )
                final_result = await generate_final_response(system_prompt, context)
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "generate_response", "result": final_result,
                })
                break

            agent_name = thought.get("agent_name", "Custom Data Agent")
            agent_description = thought.get("agent_description", "")
            data_type = thought.get("data_type", "specialized data")

            logger.info(
                "=== CREATE_DATA_AGENT DECISION (iteration %d) === "
                "agent_name=%s, data_type=%s, agent_description=%s, reasoning=%s",
                iteration, agent_name, data_type, agent_description, reasoning,
            )

            thinking_steps.append({
                "iteration": iteration, "thought": reasoning,
                "action": "need_custom_data_agent",
                "suggested_data_agent": {
                    "name": agent_name, "description": agent_description, "data_type": data_type,
                },
            })

            suggested_prompt = await generate_data_agent_prompt(thought, stocks, system_prompt)
            logger.info(
                "=== PAUSING THINKING LOOP === reason=need_data_agent, "
                "suggested_agent_name=%s, suggested_prompt_len=%d, tools_used=%s, iteration=%d",
                agent_name, len(suggested_prompt), tools_used, iteration,
            )
            logger.info("Suggested system prompt for data agent:\n%s", suggested_prompt)

            return {
                "status": "paused",
                "reason": "need_data_agent",
                "message": f"Need data agent to fetch: {data_type}",
                "final_result": None,
                "thinking_steps": thinking_steps,
                "suggested_data_agent": {
                    "name": agent_name,
                    "description": agent_description,
                    "data_type": data_type,
                    "suggested_system_prompt": suggested_prompt,
                },
                "resume_context": {
                    "stocks": stocks,
                    "system_prompt": system_prompt,
                    "collected_data": context["data"],
                    "iteration": iteration,
                },
                "tools_used": tools_used,
                "tools_discovered": tools_discovered,
                "iterations_used": iteration,
            }

        else:
            # generate_response or unknown action
            if discovery_only:
                logger.info(
                    "Iteration %d: discovery mode — LLM wants to generate response, no more tools needed. "
                    "tools_discovered=%s", iteration, tools_discovered,
                )
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "generate_response_discovery",
                })
                break
            else:
                logger.info("Iteration %d: generating final response (action=%s)", iteration, action)
                final_result = await generate_final_response(system_prompt, context)
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "generate_response", "result": final_result,
                })
                break

    # Discovery mode: return discovered tools without generating a response
    if discovery_only:
        logger.info(
            "=== THINKING LOOP COMPLETE (discovery) === tools_discovered=%s, iterations=%d",
            tools_discovered, len(thinking_steps),
        )
        return {
            "status": "discovery_complete",
            "tools_discovered": tools_discovered,
            "thinking_steps": thinking_steps,
            "iterations_used": len(thinking_steps),
        }

    if final_result is None:
        logger.info("Max iterations (%d) reached without final response — generating now", max_iterations)
        final_result = await generate_final_response(system_prompt, context)
        thinking_steps.append({
            "iteration": max_iterations,
            "thought": "Max iterations reached, generating final response",
            "action": "generate_response", "result": final_result,
        })

    logger.info(
        "=== THINKING LOOP COMPLETE === status=success, tools_used=%s, iterations=%d, "
        "thinking_steps_count=%d, final_result_keys=%s",
        list(set(tools_used)), len(thinking_steps), len(thinking_steps),
        list(final_result.keys()) if isinstance(final_result, dict) else type(final_result).__name__,
    )
    logger.info("Final result:\n%s", json.dumps(final_result, indent=2, default=str))

    return {
        "status": "success",
        "final_result": final_result,
        "thinking_steps": thinking_steps,
        "tools_used": list(set(tools_used)),
        "tools_discovered": tools_discovered,
        "iterations_used": len(thinking_steps),
    }
