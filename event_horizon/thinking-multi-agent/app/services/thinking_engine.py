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
    "web_search": "Web search for general information: company history, background, industry context, non-market data",
}

THINK_PROMPT = """You are an intelligent financial analysis agent with access to data tools.

Your task: {system_prompt}

Available data tools:
{tools_description}

Current context:
- Stocks: {stocks}
- Data already collected: {collected_data_summary}

Decide your next action. You must respond in JSON only (no markdown, no explanation):

Option 1 - Need data from existing tool:
{{"action": "call_tool", "tool": "tool_name", "reasoning": "why I need this data"}}

Option 2 - Need specialized data that existing tools don't provide:
{{"action": "create_data_agent", "agent_name": "Name for the agent", "agent_description": "Describe what data this agent should fetch", "data_type": "what kind of data (e.g., options chain, insider trading, SEC filings)", "reasoning": "why existing tools don't have this data"}}

Option 3 - Ready to answer (have sufficient data):
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
    system_prompt: str, context: dict, available_tools: List[str]
) -> dict:
    """One iteration: ask LLM what action to take next."""
    stocks = context.get("stocks", [])
    collected_data = context.get("data", {})

    tools_desc = "\n".join(
        f"- {t}: {TOOLS_DESCRIPTION.get(t, 'Custom data tool')}" for t in available_tools
    )
    data_summary = summarize_data(collected_data)
    prompt = THINK_PROMPT.format(
        system_prompt=system_prompt,
        tools_description=tools_desc,
        stocks=stocks,
        collected_data_summary=data_summary,
    )
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


def generate_data_agent_prompt(thought: dict) -> str:
    """Generate system prompt for a suggested custom data agent."""
    data_type = thought.get("data_type", "specialized data")
    description = thought.get("agent_description", "Retrieve and process financial data")

    prompt = f"""You are a specialized data retrieval agent.

Your job is to fetch {data_type} data for the given stocks.

Data to retrieve: {description}

For each stock, retrieve the relevant data and return it in a structured JSON format.
Include timestamps and source information where available.

Output format:
{{
    "status": "success",
    "data": {{
        "<SYMBOL>": {{
            // relevant data fields
        }}
    }},
    "metadata": {{
        "retrieved_at": "ISO timestamp",
        "source": "data source name"
    }}
}}"""
    logger.info(
        "generate_data_agent_prompt: data_type=%s, description=%s, prompt_len=%d",
        data_type, description, len(prompt),
    )
    logger.debug("generate_data_agent_prompt: full prompt:\n%s", prompt)
    return prompt


async def run_thinking_loop(
    stocks: List[str],
    system_prompt: str,
    input_data: dict = None,
    max_iterations: int = 5,
    available_tools: List[str] = None,
) -> dict:
    """Execute the full ReAct thinking loop."""
    if available_tools is None:
        available_tools = ["candlestick", "earnings", "news", "technical", "fundamentals"]

    logger.info(
        "=== THINKING LOOP START === stocks=%s, max_iterations=%d, tools=%s, has_input_data=%s",
        stocks, max_iterations, available_tools, input_data is not None,
    )
    if input_data:
        logger.info("Thinking loop input_data keys: %s", list(input_data.keys()))
        logger.debug("Thinking loop input_data: %s", json.dumps(input_data, indent=2, default=str))

    thinking_steps = []
    context = {"stocks": stocks, "data": input_data.copy() if input_data else {}}
    final_result = None
    tools_used = []

    for iteration in range(1, max_iterations + 1):
        logger.info("=== ITERATION %d/%d ===", iteration, max_iterations)
        logger.info("Iteration %d: context data_keys=%s, tools_used_so_far=%s", iteration, list(context["data"].keys()), tools_used)

        thought = await think_step(system_prompt, context, available_tools)
        action = thought.get("action", "generate_response")
        reasoning = thought.get("reasoning", "")
        logger.info("Iteration %d: action=%s, tool=%s, reasoning=%s", iteration, action, thought.get("tool"), reasoning)

        if action == "call_tool":
            tool_name = thought.get("tool", "")

            if tool_name not in available_tools:
                logger.warning(
                    "Iteration %d: tool '%s' not in available tools %s — skipping",
                    iteration, tool_name, available_tools,
                )
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "error", "error": f"Tool '{tool_name}' not in available tools",
                })
                continue

            if tool_name in context["data"]:
                logger.info("Iteration %d: already have '%s' data — skipping", iteration, tool_name)
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "skip", "message": f"Already have {tool_name} data",
                })
                continue

            logger.info("Iteration %d: executing tool '%s' for stocks=%s", iteration, tool_name, stocks)
            tool_result = await execute_tool(tool_name, stocks)
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

            suggested_prompt = generate_data_agent_prompt(thought)
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
                "iterations_used": iteration,
            }

        else:
            # generate_response or unknown action
            logger.info("Iteration %d: generating final response (action=%s)", iteration, action)
            final_result = await generate_final_response(system_prompt, context)
            thinking_steps.append({
                "iteration": iteration, "thought": reasoning,
                "action": "generate_response", "result": final_result,
            })
            break

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
        "iterations_used": len(thinking_steps),
    }
