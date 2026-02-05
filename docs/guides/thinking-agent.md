# Thinking Agent System

## Overview

The Thinking Agent system implements a ReAct-style (Reasoning + Acting) iterative loop that allows agents to reason about what data they need, request tools, and refine their analysis before generating a final response.

## Architecture

```
Portfolio → Thinking Agent → [Iteration Loop] → Final Output
                ↓
           ┌────────────────────────────────────────┐
           │  1. Analyze input (portfolio or data)  │
           │  2. Decide: Need more data?            │
           │     → Yes: Select/create data agent    │
           │     → No: Generate analysis            │
           │  3. Evaluate quality                   │
           │  4. Refine if needed (max N iterations)│
           └────────────────────────────────────────┘
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
  "available_tools": ["candlestick", "earnings", "news", "technical", "fundamentals"]
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
| `technical` | Technical indicators | RSI, MACD, SMA, EMA, Bollinger Bands |
| `fundamentals` | Fundamental metrics | P/E, P/B, EPS, dividend yield, market cap |

## Think Step Prompt

The agent uses this prompt structure to decide its next action:

```
You are an intelligent financial analysis agent with access to data tools.

Your task: {system_prompt}

Available data tools:
- candlestick: OHLCV price data...
- earnings: Financial reports...
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

#### `think_step(system_prompt, context, available_tools)`
Asks the LLM what action to take next based on current context and available tools.

#### `execute_tool(tool_name, stocks)`
Executes a built-in data tool and returns results.

#### `generate_final_response(system_prompt, context)`
Generates the final analysis response using all collected data.

#### `generate_data_agent_prompt(thought)`
Creates a system prompt for a suggested custom data agent.

### Iteration Flow

1. **Initialize**: Set up context with stocks and any input data
2. **Think**: Ask LLM what action to take
3. **Act**: Execute the chosen action
   - `call_tool`: Run the tool, add results to context
   - `create_data_agent`: Pause and return suggestion
   - `generate_response`: Generate final analysis
4. **Loop**: Repeat until max iterations or response generated

## Example Usage

### Python Client

```python
import requests

response = requests.post("http://localhost:8001/agents/think", json={
    "stocks": ["AAPL", "MSFT"],
    "system_prompt": "You are a dividend-focused analyst. Find stocks with sustainable high dividends.",
    "max_iterations": 5,
    "available_tools": ["fundamentals", "earnings", "candlestick"]
})

result = response.json()
print(f"Status: {result['status']}")
print(f"Iterations: {result['iterations_used']}")
print(f"Tools used: {result['tools_used']}")
print(f"Final result: {result['final_result']}")
```

### cURL

```bash
curl -X POST http://localhost:8001/agents/think \
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
| `GOOGLE_API_KEY` | - | Required for Gemini LLM calls |
| `DEFAULT_DEEP_THINK_MODEL` | `gemini-1.5-pro` | Model for thinking/analysis |

## See Also

- [Multi-Agent Architecture](../architecture/multi-agent-architecture.md)
- [System Architecture](../architecture/system-architecture.md)
- [Backend Integration](../architecture/backend-integration.md)
- [Stage 1 Guide](./stage-1-guide.md)
