"""
Event Horizon - Multi-Agent System

This script runs the Event Horizon multi-agent system.
Uses config.yaml to determine which agents to run.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from agents.news_agent import NewsAgent
from agents.report_agent import ReportAnalysisAgent


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f'event_horizon_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            ),
        ],
    )


def print_section(title: str, char: str = "="):
    """Print a formatted section header"""
    width = 70
    print(f"\n{char * width}")
    print(f" {title}")
    print(f"{char * width}\n")


def save_results(result: dict, filename: str = None) -> str:
    """Save results to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(result, f, indent=2)

    return filename


def display_news_results(result: dict):
    """Display news agent execution results"""
    print_section("NEWS AGENT RESULTS", "=")

    print(f"Status: {result['status'].upper()}")
    print(f"Execution Time: {result['execution_time_seconds']:.2f}s")

    if result["status"] == "failed":
        print(f"\n❌ ERROR: {result['error']}")
        return

    agent_result = result["result"]
    print(f"Total Articles: {agent_result['total_articles']}")
    print(f"Stocks Processed: {agent_result['stocks_processed']}")

    if agent_result.get("errors"):
        print(f"⚠️  Errors: {len(agent_result['errors'])}")

    # Show articles by symbol
    print_section("ARTICLES BY SYMBOL", "-")
    for symbol, articles in agent_result["news_by_stock"].items():
        print(f"\n📊 {symbol}: {len(articles)} articles")
        if articles:
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. {article['title']}")
                print(f"     📰 {article['source']} | {article['published_at'][:10]}")
        else:
            print("  ⚠️  No articles found")


def display_report_results(result: dict):
    """Display report agent execution results"""
    print_section("REPORT AGENT RESULTS", "=")

    print(f"Status: {result['status'].upper()}")
    print(f"Execution Time: {result['execution_time_seconds']:.2f}s")

    if result["status"] == "failed":
        print(f"\n❌ ERROR: {result['error']}")
        return

    agent_result = result["result"]
    print(f"Total Reports: {agent_result['total_reports']}")
    print(f"Securities Processed: {agent_result['stocks_processed']}")

    by_type = agent_result["securities_by_type"]
    print(f"\nBy Type:")
    print(f"  📊 Stocks: {by_type['stock']}")
    print(f"  📈 ETFs: {by_type['etf']}")
    print(f"  🏦 Mutual Funds: {by_type['mutual_fund']}")
    print(f"  ❓ Other: {by_type['other']}")

    if agent_result.get("errors"):
        print(f"⚠️  Errors: {len(agent_result['errors'])}")

    # Show reports by symbol
    print_section("REPORTS BY SYMBOL", "-")
    for symbol, report in agent_result["reports_by_symbol"].items():
        if report.get("error"):
            print(f"\n❌ {symbol}: {report['error']}")
            continue

        sec_type = report.get("security_type", "unknown")
        name = report.get("name", symbol)
        print(f"\n📊 {symbol} - {name} ({sec_type.upper()})")

        reports = report.get("reports", {})

        if sec_type == "stock":
            # Show earnings summary
            earnings = reports.get("earnings", {})
            quarterly = earnings.get("quarterly", [])
            if quarterly:
                latest = quarterly[0]
                revenue = latest.get("revenue")
                if revenue:
                    print(f"   Latest Revenue: ${revenue/1e9:.2f}B")

            metrics = reports.get("metrics", {})
            if metrics.get("market_cap"):
                print(f"   Market Cap: ${metrics['market_cap']/1e9:.2f}B")
            if metrics.get("pe_ratio"):
                print(f"   P/E Ratio: {metrics['pe_ratio']:.2f}")

        elif sec_type == "etf":
            # Show fund summary
            fund_info = reports.get("fund_info", {})
            if fund_info.get("total_assets"):
                print(f"   Total Assets: ${fund_info['total_assets']/1e9:.2f}B")
            if fund_info.get("expense_ratio"):
                print(f"   Expense Ratio: {fund_info['expense_ratio']*100:.2f}%")


def run_with_config():
    """Run agents using config.yaml"""
    try:
        from utils.config_loader import ConfigLoader

        config = ConfigLoader("config.yaml")
    except FileNotFoundError:
        return None
    except ImportError:
        print("⚠️  ConfigLoader not available. Install pyyaml: pip install pyyaml")
        return None

    print_section("EVENT HORIZON - MULTI-AGENT SYSTEM", "=")
    config.print_agent_status()

    enabled_agents = config.get_enabled_agents()
    if not enabled_agents:
        print("❌ No agents enabled in config.yaml")
        print("\nTo enable agents, edit config.yaml:")
        print("  agents:")
        print("    news_agent:")
        print("      enabled: true")
        print("    report_agent:")
        print("      enabled: true")
        return None

    # Test portfolio
    test_portfolio = {
        "portfolio_id": "test_001",
        "user_id": "user_demo",
        "portfolio": ["AAPL", "TSLA", "SPY", "QQQ"],
    }

    print("Test Portfolio:")
    print(f"  ID: {test_portfolio['portfolio_id']}")
    print(f"  Securities: {', '.join(test_portfolio['portfolio'])}")

    results = {}

    # Run News Agent if enabled
    if config.is_agent_enabled("news_agent"):
        if not os.getenv("NEWS_API_KEY"):
            print("\n⚠️  NEWS_API_KEY not found. Skipping News Agent.")
            print("To enable: Add NEWS_API_KEY to .env file")
        else:
            try:
                print_section("EXECUTING NEWS AGENT", "=")
                agent_config = config.get_agent_config("news_agent")
                news_agent = NewsAgent(config=agent_config)

                print("🔄 Running News Agent...")
                news_result = news_agent.execute(test_portfolio)
                results["news"] = news_result

                display_news_results(news_result)

                news_file = save_results(news_result, "news_results.json")
                print(f"\n💾 Saved: {news_file}")
            except Exception as e:
                print(f"❌ News Agent failed: {str(e)}")
                logging.error(f"News Agent error: {str(e)}", exc_info=True)

    # Run Report Agent if enabled
    if config.is_agent_enabled("report_agent"):
        try:
            print_section("EXECUTING REPORT AGENT", "=")
            agent_config = config.get_agent_config("report_agent")
            report_agent = ReportAnalysisAgent(config=agent_config)

            print("🔄 Running Report Agent...")
            report_result = report_agent.execute(test_portfolio)
            results["reports"] = report_result

            display_report_results(report_result)

            report_file = save_results(report_result, "report_results.json")
            print(f"\n💾 Saved: {report_file}")
        except Exception as e:
            print(f"❌ Report Agent failed: {str(e)}")
            logging.error(f"Report Agent error: {str(e)}", exc_info=True)

    # Summary
    print_section("EXECUTION COMPLETE", "=")
    if results:
        print("✅ Agents executed successfully!")
        print(f"\nExecuted: {', '.join(enabled_agents)}")
        if "news" in results:
            print(f"  📰 news_results.json")
        if "reports" in results:
            print(f"  📊 report_results.json")
    else:
        print("⚠️  No agents executed successfully")

    print(f"\n💡 To change agents: Edit config.yaml\n")

    return results


def run_interactive():
    """Run agents with interactive menu (fallback mode)"""
    print_section("EVENT HORIZON - MULTI-AGENT SYSTEM", "=")
    print("⚠️  config.yaml not found. Running in interactive mode.\n")
    print("💡 Tip: Create config.yaml for automated deployment")
    print("   See CONFIG_README.md for details\n")

    # Test portfolio
    test_portfolio = {
        "portfolio_id": "test_001",
        "user_id": "user_demo",
        "portfolio": ["AAPL", "TSLA", "SPY", "QQQ"],
    }

    print("Test Portfolio:")
    print(f"  ID: {test_portfolio['portfolio_id']}")
    print(f"  Securities: {', '.join(test_portfolio['portfolio'])}")

    # Interactive menu
    print("\n" + "=" * 70)
    print("Select agents to execute:")
    print("  1. News Agent only")
    print("  2. Report Agent only")
    print("  3. Both agents")
    print("=" * 70)

    choice = input("\nEnter choice (1-3) [default: 3]: ").strip() or "3"

    run_news = choice in ["1", "3"]
    run_reports = choice in ["2", "3"]

    results = {}

    # Run News Agent
    if run_news:
        if not os.getenv("NEWS_API_KEY"):
            print("\n⚠️  NEWS_API_KEY not found. Skipping News Agent.")
        else:
            try:
                print_section("EXECUTING NEWS AGENT", "=")
                news_config = {
                    "max_articles_per_stock": 5,
                    "days_back": 7,
                    "language": "en",
                }
                news_agent = NewsAgent(config=news_config)

                print("🔄 Running News Agent...")
                news_result = news_agent.execute(test_portfolio)
                results["news"] = news_result

                display_news_results(news_result)

                news_file = save_results(news_result, "news_results.json")
                print(f"\n💾 Saved: {news_file}")
            except Exception as e:
                print(f"❌ News Agent failed: {str(e)}")
                logging.error(f"News Agent error: {str(e)}", exc_info=True)

    # Run Report Agent
    if run_reports:
        try:
            print_section("EXECUTING REPORT AGENT", "=")
            report_config = {
                "include_financials": True,
                "earnings_periods": 4,
                "top_holdings": 10,
            }
            report_agent = ReportAnalysisAgent(config=report_config)

            print("🔄 Running Report Agent...")
            report_result = report_agent.execute(test_portfolio)
            results["reports"] = report_result

            display_report_results(report_result)

            report_file = save_results(report_result, "report_results.json")
            print(f"\n💾 Saved: {report_file}")
        except Exception as e:
            print(f"❌ Report Agent failed: {str(e)}")
            logging.error(f"Report Agent error: {str(e)}", exc_info=True)

    # Summary
    print_section("EXECUTION COMPLETE", "=")
    if results:
        print("✅ Agents executed successfully!")
        if "news" in results:
            print(f"  📰 news_results.json")
        if "reports" in results:
            print(f"  📊 report_results.json")

    print(f"\n💡 Create config.yaml for automated deployment")
    print(f"   See CONFIG_README.md for details\n")

    return results


def main():
    """Main execution function"""
    setup_logging()
    load_dotenv()

    # Check if config.yaml exists
    if Path("config.yaml").exists():
        # Use configuration mode
        results = run_with_config()
    else:
        # Fall back to interactive mode
        results = run_interactive()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Check the log file for details")
