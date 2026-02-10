# Thinking Agent System

## Overview

The Thinking Agent system implements a ReAct-style (Reasoning + Acting) iterative loop that allows agents to reason about what data they need, request tools, and refine their analysis before generating a final response.

## Architecture

```
Portfolio -> Thinking Agent -> [Iteration Loop] -> Final Output
                |
           +--------------------------------------------+
           |  1. Analyze input (portfolio or data)       |
           |  2. Decide: Need more data?                 |
           |     -> Yes: Select/create data agent        |
           |     -> No: Generate analysis                |
           |  3. Evaluate quality                        |
           |  4. Refine if needed (max N iterations)     |
           +--------------------------------------------+
```

## API Endpoint

### `POST /agents/think`

Execute a thinking agent with iterative ReAct-style reasoning loop.

#### Request Body

```json
{
  "stocks": ["AAPL", "TSLA"],
  "input_data": { ... },
  "system_prompt": "You are a dividend-focused analyst...",
  "max_iterations": 5,
  "available_tools": ["candlestick", "earnings", "news", "technical", "fundamentals", "web_search"]
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `stocks` | `List[str]` | Yes | - | List of stock symbols to analyze |
| `input_data` | `dict` | No | `null` | Optional data from prior agent in pipeline |
| `system_prompt` | `str` | Yes | - | The agent's system prompt defining its role |
| `max_iterations` | `int` | No | `5` | Maximum thinking iterations (1-10) |
| `available_tools` | `List[str]` | No | All tools | Tools the agent can use |

#### Response - Success

```json
{
  "status": "success",
  "final_result": {
    "summary": "Analysis summary...",
    "recommendations": ["Buy AAPL", "Hold TSLA"],
    "confidence": 0.85,
    "key_insights": ["Strong dividend growth", "..."],
    "risks": ["Market volatility"]
  },
  "thinking_steps": [
    {
      "iteration": 1,
      "thought": "I need price data to analyze trends",
      "action": "call_tool",
      "tool": "candlestick",
      "tool_result_summary": "Retrieved 5 items"
    },
    {
      "iteration": 2,
      "thought": "I have sufficient data because I have price and fundamentals",
      "action": "generate_response",
      "result": { ... }
    }
  ],
  "tools_used": ["candlestick", "fundamentals"],
  "iterations_used": 2
}
```

#### Response - Paused (Needs Custom Data Agent)

When the thinking agent needs data that built-in tools don't provide:

```json
{
  "status": "paused",
  "reason": "need_data_agent",
  "message": "Need data agent to fetch: options chain data",
  "final_result": null,
  "thinking_steps": [...],
  "suggested_data_agent": {
    "name": "Options Chain Agent",
    "description": "Fetches options chain data including strikes, expiration dates, and Greeks",
    "data_type": "options chain",
    "suggested_system_prompt": "You are a specialized data retrieval agent..."
  },
  "resume_context": {
    "stocks": ["AAPL"],
    "system_prompt": "...",
    "collected_data": { ... },
    "iteration": 2
  },
  "tools_used": ["candlestick"],
  "iterations_used": 2
}
```

## Available Tools

| Tool | Description | Data Returned |
|------|-------------|---------------|
| `candlestick` | OHLCV price data | Open, High, Low, Close, Volume per day |
| `earnings` | Financial reports | Quarterly earnings, EPS history, revenue |
| `news` | Recent news articles | Headlines, summaries, sentiment |
| `technical` | Technical indicators | RSI, MACD, SMA, EMA |
| `fundamentals` | Fundamental metrics | P/E, P/B, EPS, dividend yield, market cap |
| `web_search` | Web search (Tavily/Exa) | Search results, answers, URLs |

## Single-Shot Tool Discovery

The thinking engine includes `discover_required_tools()` -- a single LLM call that identifies all tools needed for a task upfront, without executing them. This is used by:

- The **bull-bear analyzer** endpoint (Path A) to tell the frontend what data agents to run
- The **custom agent** endpoint in discovery mode

```python
# Returns a list of required tool names in one LLM call
required_tools = await discover_required_tools(system_prompt, stocks, available_tools)
# e.g. ["candlestick", "earnings", "fundamentals"]
```

## Custom/Exotic Data Agent Creation

When the thinking agent encounters a need for data that built-in tools don't cover, it can request creation of a custom data agent. Custom data agents are **scoped to the `web_search` tool only** -- they use Tavily/Exa to retrieve specialized information.

The `generate_data_agent_prompt()` function uses LLM meta-prompting to create rich system prompts for these agents. If the LLM call fails, it falls back to an enhanced template.

## Think Step Prompt

The agent uses this prompt structure to decide its next action:

```
You are an intelligent financial analysis agent with access to data tools.

Your task: {system_prompt}

Available data tools:
- candlestick: OHLCV price data...
- earnings: Financial reports...
- web_search: Web search results...
...

Current context:
- Stocks: {stocks}
- Data already collected: {collected_data_summary}

Decide your next action. You must respond in JSON:

Option 1 - Need data from existing tool:
{"action": "call_tool", "tool": "tool_name", "reasoning": "why I need this data"}

Option 2 - Need specialized data that existing tools don't provide:
{"action": "create_data_agent", "agent_name": "...", "agent_description": "...", "data_type": "...", "reasoning": "..."}

Option 3 - Ready to answer (have sufficient data):
{"action": "generate_response", "reasoning": "I have sufficient data because..."}
```

## Implementation Details

### Core Functions

Located in `event_horizon/thinking-multi-agent/app/services/thinking_engine.py`:

#### `think_step(system_prompt, context, available_tools)`
Asks the LLM what action to take next based on current context and available tools.

#### `execute_tool(tool_name, stocks)`
Executes a built-in data tool and returns results. Also handles `web_search`.

#### `run_thinking_loop(system_prompt, stocks, ...)`
Full ReAct loop with max_iterations, tool execution, data accumulation.

#### `discover_required_tools(system_prompt, stocks, available_tools)`
Single-shot LLM call to discover all needed tools at once without executing them.

#### `generate_data_agent_prompt(thought, stocks, analyzer_task)` *(async)*
Generates a rich system prompt for a custom data agent via LLM meta-prompting. Falls back to an enhanced template if the LLM call fails.

### Iteration Flow

1. **Initialize**: Set up context with stocks and any input data
2. **Think**: Ask LLM what action to take
3. **Act**: Execute the chosen action
   - `call_tool`: Run the tool, add results to context. Tool is removed from available list.
   - `create_data_agent`: Pause and return suggestion (agent scoped to web_search only)
   - `generate_response`: Generate final analysis
4. **Guard**: Consecutive-skip guard breaks after 2 repeats of same tool
5. **Loop**: Repeat until max iterations or response generated

## Example Usage

### Python Client

```python
import requests

response = requests.post("http://localhost:8030/agents/think", json={
    "stocks": ["AAPL", "MSFT"],
    "system_prompt": "You are a dividend-focused analyst. Find stocks with sustainable high dividends.",
    "max_iterations": 5,
    "available_tools": ["fundamentals", "earnings", "candlestick", "web_search"]
})

result = response.json()
print(f"Status: {result['status']}")
print(f"Iterations: {result['iterations_used']}")
print(f"Tools used: {result['tools_used']}")
print(f"Final result: {result['final_result']}")
```

### cURL

```bash
curl -X POST http://localhost:8030/agents/think \
  -H "Content-Type: application/json" \
  -d '{
    "stocks": ["AAPL"],
    "system_prompt": "Analyze this stock for momentum trading opportunities",
    "max_iterations": 3
  }'
```

## Error Handling

- If JSON parsing fails during think step, defaults to `generate_response`
- If tool execution fails, error is logged and iteration continues
- If max iterations reached without response, final response is forced
- LLM errors are caught and a fallback response is generated

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BASE_URL` | `http://localhost:8000` | OpenAI-compatible LLM endpoint (e.g. vLLM) |
| `LLM_MODEL` | `mistralai/Ministral-3-14B-Reasoning-2512` | Model for thinking/analysis |
| `LLM_API_KEY` | `""` | API key if required |
| `LLM_TIMEOUT` | `300` | HTTP timeout in seconds |
| `TAVILY_API_KEY` | - | Required for web_search tool |
| `EXASEARCH_API_KEY` | - | Fallback for web_search (Exa) |

## See Also

- [Multi-Agent Architecture](../architecture/multi-agent-architecture.md)
- [System Architecture](../architecture/system-architecture.md)
- [Backend Integration](../architecture/backend-integration.md)
- [Stage 1 Guide](./stage-1-guide.md)
