"""
Robust JSON parsing for LLM responses

Handles LLM outputs that contain:
- Markdown code blocks (```json ... ```)
- Thinking/reasoning text before or after JSON
- Multiple JSON objects (extracts the first valid one)
"""

import json
import re
from typing import Any, Dict, Optional


def extract_json_from_llm_response(content: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from LLM response that may contain reasoning text

    Tries multiple strategies:
    1. Direct JSON parsing
    2. Extract from markdown code blocks
    3. Find JSON object in text

    Args:
        content: Raw LLM response content

    Returns:
        Parsed JSON dict or None if no valid JSON found
    """
    if not content or not content.strip():
        return None

    # Strategy 1: Try direct JSON parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code blocks
    # Match ```json ... ``` or ``` ... ``` (more flexible patterns)
    code_block_patterns = [
        r'```json\s*(.*?)```',       # ```json ... ``` (flexible whitespace)
        r'```\s*(.*?)```',           # ``` ... ``` (flexible whitespace)
        r'`{3,}json\s*(.*?)`{3,}',   # Multiple backticks
        r'`{3,}\s*(.*?)`{3,}',       # Multiple backticks without json
    ]

    for pattern in code_block_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

    # Strategy 3: Find JSON object in text (look for { ... })
    # Find the longest valid JSON object
    brace_depth = 0
    start_idx = None
    best_json = None
    best_length = 0

    for i, char in enumerate(content):
        if char == '{':
            if brace_depth == 0:
                start_idx = i
            brace_depth += 1
        elif char == '}':
            brace_depth -= 1
            if brace_depth == 0 and start_idx is not None:
                # Try to parse this potential JSON
                candidate = content[start_idx:i+1]
                try:
                    parsed = json.loads(candidate)
                    if len(candidate) > best_length:
                        best_json = parsed
                        best_length = len(candidate)
                except json.JSONDecodeError:
                    pass
                start_idx = None

    return best_json


def parse_llm_json_response(
    content: str,
    fallback_message: str = "Error parsing response"
) -> Dict[str, Any]:
    """
    Parse LLM JSON response with fallback

    Args:
        content: Raw LLM response
        fallback_message: Error message if parsing fails

    Returns:
        Parsed JSON dict or empty dict with error message
    """
    parsed = extract_json_from_llm_response(content)

    if parsed is None:
        return {"error": fallback_message, "raw_content": content[:500]}

    return parsed
