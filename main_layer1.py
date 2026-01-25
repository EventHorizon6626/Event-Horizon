"""
Event Horizon - Layer 1 Data Retrieval System

Demonstrates the complete Layer 1 data retrieval architecture with all agents.
Layer 1 is responsible for collecting heterogeneous data from multiple sources.

Enhanced with Tauric Research TradingAgents patterns:
- Technical indicators agent (SMA, EMA, RSI, MACD)
- Fundamentals analysis agent (P/E, ROE, financial ratios)
- Utility tools for stock data retrieval

Reference: https://github.com/TauricResearch/TradingAgents

Architecture:
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: DATA RETRIEVAL                  │
├─────────────────────────────────────────────────────────────┤
│  5 Specialized Agents Running in Parallel:                 │
│                                                             │
│  1. Candlestick Agent  → OHLCV price data                  │
│  2. Earnings Agent     → Financial reports & earnings       │
│  3. News Agent         → News articles & headlines          │
│  4. Technical Agent    → Technical indicators (SMA/RSI)     │
│  5. Fundamentals Agent → Fundamental metrics (P/E/ROE)      │
└─────────────────────────────────────────────────────────────┘
                          ↓
           Heterogeneous Data Collected
                          ↓
          Ready for Layer 2 (Normalization)
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
        result_dict = {
            **result,
            "layer1_output": layer1_output.to_dict() if hasattr(layer1_output, 'to_dict') else layer1_output
        }
    else:
        result_dict = result

    with open(filename, "w") as f:
        json.dump(result_dict, f, indent=2, default=str)

    return filename


def print_data_summary(layer1_output):
    """Print summary of retrieved data"""

    # News Data
    if hasattr(layer1_output, "news_data") and layer1_output.news_data:
        print(f"\n📰 News Data: {len(layer1_output.news_data)} symbols")
        total_articles = 0
        for symbol, data in list(layer1_output.news_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                articles = data.total_articles if hasattr(data, 'total_articles') else len(data.articles)
                total_articles += articles
                print(f"   ✓ {symbol}: {articles} articles")
        if total_articles > 0:
            print(f"   Total: {total_articles} articles across all symbols")

    # Earnings Data
    if hasattr(layer1_output, "earnings_data") and layer1_output.earnings_data:
        print(f"\n📊 Earnings Data: {len(layer1_output.earnings_data)} symbols")
        for symbol, data in list(layer1_output.earnings_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                company_name = data.name if hasattr(data, 'name') else symbol
                sec_type = data.security_type if hasattr(data, 'security_type') else 'unknown'
                print(f"   ✓ {symbol}: {company_name} ({sec_type})")

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
        print(f"\n🔧 Technical Indicators: {len(layer1_output.technical_data)} symbols")
        for symbol, data in list(layer1_output.technical_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                indicator_count = len(data.indicators) if hasattr(data, 'indicators') else 0
                indicator_names = ', '.join(data.indicators.keys()) if hasattr(data, 'indicators') else ''
                print(f"   ✓ {symbol}: {indicator_count} indicators ({indicator_names})")

    # Fundamentals Data (Tauric-inspired)
    if hasattr(layer1_output, "fundamentals_data") and layer1_output.fundamentals_data:
        print(f"\n💰 Fundamental Metrics: {len(layer1_output.fundamentals_data)} symbols")
        for symbol, data in list(layer1_output.fundamentals_data.items())[:3]:
            if data.error:
                print(f"   ✗ {symbol}: {data.error}")
            else:
                print(f"   ✓ {symbol}: Valuation, profitability, and financial health metrics")


def main():
    """Main execution function"""

    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    print_section("EVENT HORIZON - LAYER 1 DATA RETRIEVAL", "=")

    # Test portfolio
    test_portfolio = {
        "portfolio_id": "layer1_demo_2026",
        "portfolio": ["AAPL", "TSLA", "SPY", "NVDA"],
    }

    print("Test Portfolio:")
    print(f"  ID: {test_portfolio['portfolio_id']}")
    print(f"  Symbols: {', '.join(test_portfolio['portfolio'])}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d')}")

    # Configure Layer 1 Orchestrator
    # ALL 5 AGENTS: candlestick, earnings, news, technical, fundamentals
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

    print(f"\nEnabled Agents: {', '.join(layer1_config['enabled_agents'])}")
    print(f"Parallel Workers: {layer1_config['max_workers']}")

    print_section("EXECUTING LAYER 1 DATA RETRIEVAL", "=")

    # Create orchestrator
    orchestrator = Layer1Orchestrator(config=layer1_config)

    # Execute Layer 1
    print("🔄 Running Layer 1 agents in parallel...\n")
    result = orchestrator.execute(test_portfolio)

    # Get results
    layer1_output = result["layer1_output"]

    print_section("LAYER 1 DATA RETRIEVAL RESULTS", "=")

    # Print status
    print(f"Status: {result['status'].upper()}")
    print(f"Execution Time: {result['execution_time_seconds']:.2f}s")
    print(f"Agents Executed: {', '.join(result['agents_executed'])}")

    # Print errors if any
    if result.get("errors"):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for error in result["errors"][:5]:  # Show first 5 errors
            print(f"   - {error.get('agent', 'unknown')}: {error.get('error', 'Unknown error')}")

    # Print data summary
    print_data_summary(layer1_output)

    # Save results
    print_section("SAVING RESULTS", "=")
    output_file = save_results(result)
    print(f"💾 Results saved: {output_file}")

    # Summary
    print_section("LAYER 1 EXECUTION COMPLETE", "=")
    print("✅ Layer 1 data retrieval completed!")

    print(f"\nData Types Retrieved (5 Categories):")
    print("  ✓ Price Data (OHLCV candles)")
    print("  ✓ Earnings & Financial Reports")
    print("  ✓ News Articles & Headlines")
    print("  ✓ Technical Indicators (SMA, RSI, MACD) ← Tauric-inspired")
    print("  ✓ Fundamental Metrics (P/E, ROE, Debt/Equity) ← Tauric-inspired")

    print(f"\nNext Steps:")
    print("  1. Review the output file for complete heterogeneous data")
    print("  2. Layer 2 will normalize this data into unified 'DNA' format")
    print("  3. Layer 3 will extract features using LLM/Neural networks")
    print("  4. Financial Analysis System will make trading decisions")

    print("\n📚 Architecture: Combined Event Horizon + Tauric Research patterns")
    print("📖 Documentation: See LAYER1_UPDATE_SUMMARY.md for details")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        logging.exception("Fatal error in main_layer1.py")
        sys.exit(1)
