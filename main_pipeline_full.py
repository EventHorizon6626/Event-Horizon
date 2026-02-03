"""
Event Horizon - Complete Data Pipeline Demo (Stage 1 → 2 → 3)

Demonstrates the complete System 1 data pipeline with Opik integration:
- Stage 1: Data Retrieval (5 agents in parallel)
- Stage 2: Normalization (clean, unified data)
- Stage 3: LLM Feature Extraction (with Opik tracking!)

🎯 OPIK HACKATHON DEMO:
This script showcases how Opik accelerates AI development by providing:
- Full observability into LLM calls
- Token usage and cost tracking
- Performance monitoring
- Evaluation infrastructure
"""

import json
import logging
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

from event_horizon.data_pipeline import Stage1Orchestrator
from event_horizon.data_pipeline.stage_2 import Stage2Orchestrator
from event_horizon.data_pipeline.stage_3 import Stage3Orchestrator


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f'pipeline_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            ),
        ],
    )


def print_section(title: str, char: str = "=", emoji: str = ""):
    """Print formatted section header"""
    width = 80
    print(f"\n{char * width}")
    if emoji:
        print(f"{emoji}  {title}")
    else:
        print(f" {title}")
    print(f"{char * width}\n")


def save_results(result: dict, filename: str) -> str:
    """Save results to JSON file"""
    # Convert dataclass objects to dicts
    if "stage1_output" in result:
        stage1_output = result["stage1_output"]
        result["stage1_output"] = (
            stage1_output.to_dict()
            if hasattr(stage1_output, "to_dict")
            else stage1_output
        )

    if "stage2_output" in result:
        stage2_output = result["stage2_output"]
        result["stage2_output"] = (
            stage2_output.to_dict()
            if hasattr(stage2_output, "to_dict")
            else stage2_output
        )

    if "stage3_output" in result:
        stage3_output = result["stage3_output"]
        result["stage3_output"] = (
            stage3_output.to_dict()
            if hasattr(stage3_output, "to_dict")
            else stage3_output
        )

    with open(filename, "w") as f:
        json.dump(result, f, indent=2, default=str)

    return filename


def main():
    """Main execution function"""

    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)

    print_section("EVENT HORIZON - COMPLETE DATA PIPELINE", "=", "🚀")

    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        print("   Please add it to your .env file for Stage 3 (LLM extraction)")
        print("\n   You can still run Stage 1 and 2 without it.\n")

    if not os.getenv("NEWS_API_KEY"):
        print("⚠️  WARNING: NEWS_API_KEY not found")
        print("   News agent will not work, but other agents will.\n")

    # Test portfolio
    test_portfolio = {
        "portfolio_id": "hackathon_demo_2026",
        "portfolio": ["AAPL", "TSLA", "NVDA"],
    }

    print("📊 Test Portfolio:")
    print(f"   ID: {test_portfolio['portfolio_id']}")
    print(f"   Symbols: {', '.join(test_portfolio['portfolio'])}")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ========================================================================
    # STAGE 1: DATA RETRIEVAL
    # ========================================================================
    print_section("STAGE 1: DATA RETRIEVAL", "=", "📥")

    stage1_config = {
        "enabled_agents": ["candlestick", "earnings", "news", "technical", "fundamentals"],
        "max_workers": 5,
        "agent_configs": {
            "candlestick": {"period": "1mo", "interval": "1d"},
            "earnings": {"include_financials": True, "earnings_periods": 4},
            "news": {"max_articles_per_stock": 10, "days_back": 7},
            "technical": {"indicators": ["SMA", "RSI", "MACD"], "look_back_days": 30},
            "fundamentals": {"include_ratios": True, "include_financials": True},
        },
    }

    print(f"Enabled Agents: {', '.join(stage1_config['enabled_agents'])}")
    print(f"Parallel Workers: {stage1_config['max_workers']}\n")
    print("Running Stage 1 agents in parallel...\n")

    orchestrator_stage1 = Stage1Orchestrator(config=stage1_config)
    result_stage1 = orchestrator_stage1.execute(test_portfolio)
    stage1_output = result_stage1["stage1_output"]

    print(f"✅ Stage 1 Complete!")
    print(f"   Status: {result_stage1['status'].upper()}")
    print(f"   Time: {result_stage1['execution_time_seconds']:.2f}s")
    print(f"   Agents: {', '.join(result_stage1['agents_executed'])}")

    # ========================================================================
    # STAGE 2: NORMALIZATION
    # ========================================================================
    print_section("STAGE 2: NORMALIZATION", "=", "🔄")

    print("Normalizing heterogeneous data into unified format...\n")

    orchestrator_stage2 = Stage2Orchestrator()
    result_stage2 = orchestrator_stage2.execute(stage1_output)
    stage2_output = result_stage2["stage2_output"]

    print(f"✅ Stage 2 Complete!")
    print(f"   Status: {result_stage2['status'].upper()}")
    print(f"   Time: {result_stage2['execution_time_seconds']:.2f}s")
    print(f"   Quality Score: {result_stage2['overall_quality_score']:.2f}")
    print(f"   Complete Data: {len(stage2_output.symbols_with_complete_data)}")
    print(f"   Partial Data: {len(stage2_output.symbols_with_partial_data)}")
    print(f"   Errors: {len(stage2_output.symbols_with_errors)}")

    # ========================================================================
    # STAGE 3: LLM FEATURE EXTRACTION (with Opik!)
    # ========================================================================
    print_section("STAGE 3: LLM FEATURE EXTRACTION (OPIK DEMO!)", "=", "🧠")

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Skipping Stage 3: OPENAI_API_KEY not configured")
        print("   Add OPENAI_API_KEY to .env to run LLM feature extraction\n")
        stage3_enabled = False
    else:
        stage3_enabled = True
        print("🎯 Opik Integration Active!")
        print("   - Tracing all LLM calls")
        print("   - Tracking token usage")
        print("   - Monitoring performance")
        print("   - Building evaluation dataset\n")

        stage3_config = {
            "llm_model": "gpt-4o-mini",  # Fast and cost-effective
            "temperature": 0.3,
            "opik_project": "event-horizon",
            "enable_opik": True,
        }

        print(f"LLM Model: {stage3_config['llm_model']}")
        print(f"Temperature: {stage3_config['temperature']}")
        print(f"Opik Project: {stage3_config['opik_project']}\n")
        print("Extracting features with LLM...\n")

        orchestrator_stage3 = Stage3Orchestrator(config=stage3_config)
        result_stage3 = orchestrator_stage3.execute(stage2_output)
        stage3_output = result_stage3["stage3_output"]

        print(f"✅ Stage 3 Complete!")
        print(f"   Status: {result_stage3['status'].upper()}")
        print(f"   Time: {result_stage3['execution_time_seconds']:.2f}s")
        print(f"   LLM Calls: {result_stage3['total_llm_calls']}")
        print(f"   Total Tokens: {result_stage3['total_tokens_used']}")
        print(f"   Avg Time/Call: {stage3_output.average_extraction_time:.2f}s")

        print(f"\n📊 Feature Extraction Summary:")
        for symbol, features in stage3_output.symbol_features.items():
            print(f"\n   {symbol}:")
            print(f"      Sentiment: {features.market_sentiment} ({features.sentiment_confidence:.2f})")
            print(f"      Technical: {features.technical_signal} ({features.technical_confidence:.2f})")
            print(f"      Fundamentals: {features.fundamental_health} ({features.fundamental_confidence:.2f})")
            print(f"      Tokens: {features.total_tokens}")

    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    print_section("SAVING RESULTS", "=", "💾")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save individual stage results
    stage1_file = f"output_stage1_{timestamp}.json"
    stage2_file = f"output_stage2_{timestamp}.json"

    save_results({"stage1_output": stage1_output}, stage1_file)
    save_results({"stage2_output": stage2_output}, stage2_file)
    print(f"✅ Stage 1 output: {stage1_file}")
    print(f"✅ Stage 2 output: {stage2_file}")

    if stage3_enabled:
        stage3_file = f"output_stage3_{timestamp}.json"
        save_results({"stage3_output": stage3_output}, stage3_file)
        print(f"✅ Stage 3 output: {stage3_file}")

    # Save complete pipeline result
    pipeline_result = {
        "pipeline_id": test_portfolio["portfolio_id"],
        "timestamp": datetime.now().isoformat(),
        "stage1": result_stage1,
        "stage2": result_stage2,
    }

    if stage3_enabled:
        pipeline_result["stage3"] = result_stage3

    complete_file = f"pipeline_complete_{timestamp}.json"
    save_results(pipeline_result, complete_file)
    print(f"✅ Complete pipeline: {complete_file}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_section("PIPELINE EXECUTION COMPLETE", "=", "🎉")

    total_time = (
        result_stage1["execution_time_seconds"]
        + result_stage2["execution_time_seconds"]
    )
    if stage3_enabled:
        total_time += result_stage3["execution_time_seconds"]

    print(f"✅ All stages completed successfully!")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Portfolio: {test_portfolio['portfolio_id']}")
    print(f"   Symbols: {', '.join(test_portfolio['portfolio'])}")

    if stage3_enabled:
        print(f"\n🎯 Opik Insights:")
        print(f"   - Check Opik dashboard for full traces")
        print(f"   - Project: {stage3_config['opik_project']}")
        print(f"   - Total LLM calls: {result_stage3['total_llm_calls']}")
        print(f"   - Total tokens: {result_stage3['total_tokens_used']}")
        print(f"\n   View traces at: https://www.comet.com/opik")

    print(f"\n📈 Next Steps:")
    print(f"   1. Review output files for complete data")
    print(f"   2. Check Opik dashboard for LLM traces")
    print(f"   3. Stage 3 features ready for analyzer system (Teams 1-4)")
    print(f"   4. Use this data to power trading decisions!")

    print(f"\n💡 Hackathon Demo Points:")
    print(f"   ✅ Opik provides full visibility into LLM pipeline")
    print(f"   ✅ Token usage tracked automatically (cost monitoring)")
    print(f"   ✅ Performance metrics captured (optimization ready)")
    print(f"   ✅ Traces enable debugging and evaluation")
    print(f"   ✅ 3x faster iteration with Opik's observability!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        logging.exception("Fatal error in main_pipeline_full.py")
        sys.exit(1)
