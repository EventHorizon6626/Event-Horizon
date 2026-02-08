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
    prompt = THINK_PROMPT.format(
        system_prompt=system_prompt,
        tools_description=tools_desc,
        stocks=stocks,
        collected_data_summary=summarize_data(collected_data),
    )

    try:
        response = await call_llm(prompt)
        thought = json.loads(_clean_json(response))
        return thought
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse thinking JSON: {e}")
        return {"action": "generate_response", "reasoning": "Could not parse LLM response, generating final response"}
    except Exception as e:
        logger.error(f"Think step failed: {e}")
        return {"action": "generate_response", "reasoning": f"Error in thinking: {e}"}


async def generate_final_response(system_prompt: str, context: dict) -> dict:
    """Generate final analysis from collected data."""
    stocks = context.get("stocks", [])
    collected_data = context.get("data", {})

    prompt = f"""Based on the following data, provide your analysis.

Your role: {system_prompt}

Stocks: {stocks}

Available data:
{json.dumps(collected_data, indent=2, default=str)[:8000]}

Provide your final analysis in JSON format. Include:
- summary: Brief overview of your findings
- recommendations: List of actionable recommendations
- confidence: Your confidence level (0-1)
- key_insights: Most important findings
- risks: Any risks or caveats to note"""

    try:
        response = await call_llm(prompt)
        try:
            return json.loads(_clean_json(response))
        except json.JSONDecodeError:
            return {"summary": response, "raw_response": True}
    except Exception as e:
        logger.error(f"Final response generation failed: {e}")
        return {"error": str(e)}


def generate_data_agent_prompt(thought: dict) -> str:
    """Generate system prompt for a suggested custom data agent."""
    data_type = thought.get("data_type", "specialized data")
    description = thought.get("agent_description", "Retrieve and process financial data")

    return f"""You are a specialized data retrieval agent.

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

    thinking_steps = []
    context = {"stocks": stocks, "data": input_data.copy() if input_data else {}}
    final_result = None
    tools_used = []

    for iteration in range(1, max_iterations + 1):
        logger.info(f"Thinking iteration {iteration}/{max_iterations}")

        thought = await think_step(system_prompt, context, available_tools)
        action = thought.get("action", "generate_response")
        reasoning = thought.get("reasoning", "")

        if action == "call_tool":
            tool_name = thought.get("tool", "")

            if tool_name not in available_tools:
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "error", "error": f"Tool '{tool_name}' not in available tools",
                })
                continue

            if tool_name in context["data"]:
                thinking_steps.append({
                    "iteration": iteration, "thought": reasoning,
                    "action": "skip", "message": f"Already have {tool_name} data",
                })
                continue

            tool_result = await execute_tool(tool_name, stocks)
            context["data"][tool_name] = tool_result
            tools_used.append(tool_name)

            thinking_steps.append({
                "iteration": iteration, "thought": reasoning,
                "action": "call_tool", "tool": tool_name,
                "tool_result_summary": summarize_tool_result(tool_name, tool_result),
            })

        elif action == "create_data_agent":
            agent_name = thought.get("agent_name", "Custom Data Agent")
            agent_description = thought.get("agent_description", "")
            data_type = thought.get("data_type", "specialized data")

            thinking_steps.append({
                "iteration": iteration, "thought": reasoning,
                "action": "need_custom_data_agent",
                "suggested_data_agent": {
                    "name": agent_name, "description": agent_description, "data_type": data_type,
                },
            })

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
                    "suggested_system_prompt": generate_data_agent_prompt(thought),
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
            final_result = await generate_final_response(system_prompt, context)
            thinking_steps.append({
                "iteration": iteration, "thought": reasoning,
                "action": "generate_response", "result": final_result,
            })
            break

    if final_result is None:
        final_result = await generate_final_response(system_prompt, context)
        thinking_steps.append({
            "iteration": max_iterations,
            "thought": "Max iterations reached, generating final response",
            "action": "generate_response", "result": final_result,
        })

    return {
        "status": "success",
        "final_result": final_result,
        "thinking_steps": thinking_steps,
        "tools_used": list(set(tools_used)),
        "iterations_used": len(thinking_steps),
    }
