"""
Event Horizon - Layer 1 Data Retrieval System

This script demonstrates the Layer 1 data retrieval architecture.
Uses the Layer1Orchestrator to run agents in parallel.

Enhanced with Tauric Research TradingAgents patterns:
- Technical indicators agent (SMA, EMA, RSI, MACD)
- Fundamentals analysis agent (P/E, ROE, financial ratios)
- Utility tools for stock data retrieval

Reference: https://github.com/TauricResearch/TradingAgents
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from layer_1 import Layer1Orchestrator


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f'layer1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            ),
        ],
    )


def print_section(title: str, char: str = "="):
    """Print a formatted section header"""
    width = 80
    print(f"\n{char * width}")
    print(f" {title}")
    print(f"{char * width}\n")


def save_results(result: dict, filename: str = None) -> str:
    """Save results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"layer1_output_{timestamp}.json"

    # Convert Layer1Output to dict if needed
    if "layer1_output" in result:
        layer1_output = result["layer1_output"]
        if hasattr(layer1_output, "to_dict"):
            result["layer1_output"] = layer1_output.to_dict()

    with open(filename, "w") as f:
        json.dump(result, f, indent=2, default=str)

    return filename


def display_layer1_results(result: dict):
    """Display Layer 1 execution results"""
    print_section("LAYER 1 DATA RETRIEVAL RESULTS", "=")

    print(f"Status: {result['status'].upper()}")
    print(f"Execution Time: {result['execution_time_seconds']:.2f}s")
    print(f"Agents Executed: {', '.join(result['agents_executed'])}")

    if result.get("errors"):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for error in result["errors"][:5]:  # Show first 5 errors
            print(f"  - {error.get('agent', 'unknown')}: {error.get('error', 'Unknown')}")

    layer1_output = result.get("layer1_output")
    if not layer1_output:
        return

    # Display summary by data type
    print_section("DATA RETRIEVAL SUMMARY", "-")

    # News Data
    if hasattr(layer1_output, "news_data") and layer1_output.news_data:
        total_articles = sum(
            data.total_articles for data in layer1_output.news_data.values()
        )
        print(f"📰 News Data: {len(layer1_output.news_data)} symbols, {total_articles} articles")
        for symbol, data in list(layer1_output.news_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                print(f"   ✓ {symbol}: {data.total_articles} articles")

    # Earnings Data
    if hasattr(layer1_output, "earnings_data") and layer1_output.earnings_data:
        print(f"\n📊 Earnings Data: {len(layer1_output.earnings_data)} symbols")
        for symbol, data in list(layer1_output.earnings_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                print(f"   ✓ {symbol}: {data.security_type} - {data.name or symbol}")

    # Chart Data
    if hasattr(layer1_output, "chart_data") and layer1_output.chart_data:
        print(f"\n📈 Chart Data: {len(layer1_output.chart_data)} symbols")
        for symbol, data in list(layer1_output.chart_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                candle_count = len(data.candles) if hasattr(data, 'candles') else 0
                print(f"   ✓ {symbol}: {candle_count} candles ({data.period}, {data.interval})")

    # Technical Data (Tauric-inspired)
    if hasattr(layer1_output, "technical_data") and layer1_output.technical_data:
        print(f"\n📊 Technical Data: {len(layer1_output.technical_data)} symbols")
        for symbol, data in list(layer1_output.technical_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                indicator_count = len(data.indicators) if hasattr(data, 'indicators') else 0
                print(f"   ✓ {symbol}: {indicator_count} indicators")

    # Fundamentals Data (Tauric-inspired)
    if hasattr(layer1_output, "fundamentals_data") and layer1_output.fundamentals_data:
        print(f"\n💰 Fundamentals Data: {len(layer1_output.fundamentals_data)} symbols")
        for symbol, data in list(layer1_output.fundamentals_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                print(f"   ✓ {symbol}: Fundamental metrics retrieved")


def main():
    """Main execution function"""
    setup_logging()
    load_dotenv()

    print_section("EVENT HORIZON - LAYER 1 DATA RETRIEVAL", "=")

    # Test portfolio
    test_portfolio = {
        "portfolio_id": "layer1_test_001",
        "portfolio": ["AAPL", "TSLA", "SPY", "NVDA"],
    }

    print("Test Portfolio:")
    print(f"  ID: {test_portfolio['portfolio_id']}")
    print(f"  Symbols: {', '.join(test_portfolio['portfolio'])}")

    # Configure Layer 1 Orchestrator
    # Now includes Tauric-inspired technical and fundamentals agents
    layer1_config = {
        "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
        "max_workers": 5,
        "agent_configs": {
            "candlestick": {
                "period": "1mo",
                "interval": "1d",
            },
            "earnings": {
                "include_financials": True,
                "earnings_periods": 4,
            },
            "news": {
                "max_articles_per_stock": 10,
                "days_back": 7,
            },
            "technical": {
                "indicators": ["SMA", "RSI", "MACD"],
                "look_back_days": 30,
            },
            "fundamentals": {
                "include_ratios": True,
                "include_financials": True,
            },
        },
    }

    # Check for required API keys
    if "news" in layer1_config["enabled_agents"] and not os.getenv("NEWS_API_KEY"):
        print("\n⚠️  NEWS_API_KEY not found. Removing news agent.")
        layer1_config["enabled_agents"].remove("news")

    print(f"\nEnabled Agents: {', '.join(layer1_config['enabled_agents'])}")

    # Initialize and execute Layer 1 Orchestrator
    try:
        print_section("EXECUTING LAYER 1 DATA RETRIEVAL", "=")

        orchestrator = Layer1Orchestrator(config=layer1_config)

        print("🔄 Running Layer 1 agents in parallel...")
        result = orchestrator.execute(test_portfolio)

        # Display results
        display_layer1_results(result)

        # Save results
        output_file = save_results(result)
        print(f"\n💾 Results saved: {output_file}")

    except Exception as e:
        print(f"\n❌ Layer 1 execution failed: {str(e)}")
        logging.error(f"Layer 1 error: {str(e)}", exc_info=True)
        return

    # Summary
    print_section("LAYER 1 EXECUTION COMPLETE", "=")
    print("✅ Layer 1 data retrieval completed!")
    print(f"\nData Retrieved (Tauric-inspired architecture):")
    print("  ✓ Price Data (OHLCV candles)")
    print("  ✓ Earnings & Financial Reports")
    print("  ✓ News Articles & Headlines")
    print("  ✓ Technical Indicators (SMA, RSI, MACD)")
    print("  ✓ Fundamental Metrics (P/E, ROE, Debt/Equity)")
    print(f"\nNext Steps:")
    print("  1. Review the output file for complete data")
    print("  2. Layer 2 will normalize this heterogeneous data")
    print("  3. Layer 3 will extract features for trading signals")
    print("\n📚 Integration: Combined Event Horizon + Tauric Research patterns")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Check the log file for details")
