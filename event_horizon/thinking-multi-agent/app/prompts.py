from typing import Any, Dict, List, Optional


SYSTEM_PROMPT = """You are an expert financial analyst AI with deep expertise in:
- Fundamental analysis (financial statements, earnings, valuations)
- Technical analysis (price trends, volume patterns, indicators)
- Sentiment analysis (news impact, market psychology)
- Risk assessment and portfolio analysis

When provided with financial data, earnings reports, or news:
1. Carefully examine all data points and identify key patterns
2. Cross-reference data across different sources when available
3. Provide clear, actionable insights with supporting evidence
4. Quantify findings with specific numbers from the data
5. Flag any risks, anomalies, or data quality concerns

Always structure your analysis clearly with sections and be precise with numbers."""


def format_tabular_data(data: List[Dict[str, Any]], title: str) -> str:
    """Convert a list of dicts (tabular JSON) into a readable markdown table."""
    if not data:
        return ""

    # Collect all unique keys across all rows
    all_keys = []
    seen = set()
    for row in data:
        for key in row.keys():
            if key not in seen:
                all_keys.append(key)
                seen.add(key)

    # Build markdown table
    header = "| " + " | ".join(str(k) for k in all_keys) + " |"
    separator = "| " + " | ".join("---" for _ in all_keys) + " |"

    rows = []
    for row in data:
        row_str = "| " + " | ".join(str(row.get(k, "")) for k in all_keys) + " |"
        rows.append(row_str)

    table = "\n".join([header, separator] + rows)
    return f"### {title}\n\n{table}"


def format_nested_metadata(metadata: Dict[str, Any]) -> str:
    """Format nested metadata from Event-Horizon data agents into readable sections.

    Handles the EH nested format where each key maps to a dict of per-symbol data:
      {"earnings": {"AAPL": {...}}, "prices": {"AAPL": {...}}, ...}
    """
    if not metadata:
        return ""

    sections: List[str] = []

    # Map of metadata keys to display titles
    key_labels = {
        "earnings": "Earnings Data",
        "prices": "Price / Chart Data",
        "chart_data": "Price / Chart Data",
        "news": "News Data",
        "technical": "Technical Indicators",
        "fundamentals": "Fundamentals",
    }

    for key, label in key_labels.items():
        data = metadata.get(key)
        if not data:
            continue

        # data should be a dict keyed by symbol
        if not isinstance(data, dict):
            sections.append(f"### {label}\n\n{data}")
            continue

        for symbol, symbol_data in data.items():
            section_title = f"{label} — {symbol}"

            if isinstance(symbol_data, dict):
                # Special handling for nested structures
                if "articles" in symbol_data and isinstance(symbol_data["articles"], list):
                    # News: render articles as a table
                    articles = symbol_data["articles"]
                    if articles:
                        sections.append(format_tabular_data(articles, section_title))
                    else:
                        sections.append(f"### {section_title}\n\nNo articles available.")
                elif "indicators" in symbol_data and isinstance(symbol_data["indicators"], dict):
                    # Technical: render indicators as key-value pairs
                    lines = [f"### {section_title}\n"]
                    for ind_name, ind_val in symbol_data["indicators"].items():
                        lines.append(f"- **{ind_name}**: {ind_val}")
                    sections.append("\n".join(lines))
                elif "candles" in symbol_data and isinstance(symbol_data["candles"], list):
                    # Candlestick: render candles as a table
                    candles = symbol_data["candles"]
                    if candles:
                        sections.append(format_tabular_data(candles, section_title))
                    else:
                        sections.append(f"### {section_title}\n\nNo candle data available.")
                elif "fundamentals_text" in symbol_data:
                    # Fundamentals: plain text
                    sections.append(f"### {section_title}\n\n{symbol_data['fundamentals_text']}")
                else:
                    # Generic dict: render as key-value pairs
                    lines = [f"### {section_title}\n"]
                    for k, v in symbol_data.items():
                        if k in ("symbol", "data_source", "retrieved_at"):
                            continue
                        lines.append(f"- **{k}**: {v}")
                    sections.append("\n".join(lines))
            else:
                sections.append(f"### {section_title}\n\n{symbol_data}")

    # Handle any unrecognized top-level keys
    known_keys = set(key_labels.keys())
    for key, data in metadata.items():
        if key in known_keys or not data:
            continue
        sections.append(f"### {key}\n\n{data}")

    return "\n\n".join(sections)


def build_user_prompt(
    task: str,
    financial_data: Optional[List[Dict[str, Any]]] = None,
    earnings_data: Optional[List[Dict[str, Any]]] = None,
    news_data: Optional[List[Dict[str, Any]]] = None,
    additional_context: Optional[str] = None,
    stocks: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Build the full user prompt with formatted data sections."""
    sections = [f"## Task\n\n{task}"]

    if stocks:
        sections.append(f"### Stocks: {', '.join(stocks)}")

    if financial_data:
        sections.append(format_tabular_data(financial_data, "Financial Data"))

    if earnings_data:
        sections.append(format_tabular_data(earnings_data, "Earnings Data"))

    if news_data:
        sections.append(format_tabular_data(news_data, "News Data"))

    if metadata:
        nested_section = format_nested_metadata(metadata)
        if nested_section:
            sections.append(nested_section)

    if additional_context:
        sections.append(f"### Additional Context\n\n{additional_context}")

    sections.append(
        "## Instructions\n\n"
        "Analyze the provided data thoroughly. Show your reasoning step by step, "
        "then provide a structured final analysis with clear conclusions and actionable insights."
    )

    return "\n\n".join(sections)
