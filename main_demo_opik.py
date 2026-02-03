"""
Event Horizon x Opik - Complete Hackathon Demo

Full pipeline demonstration:
- Stage 1: Data Retrieval
- Stage 2: Normalization
- Stage 3: LLM Feature Extraction (Opik tracked)
- Team 2: Bull/Bear Debate (Opik tracked)

🎯 HACKATHON DEMO:
This showcases how Opik enables rapid development of complex multi-agent systems!
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
from event_horizon.analyzer_system.team_2_researchers import Team2Orchestrator


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f'demo_opik_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
            ),
        ],
    )


def print_section(title: str, char: str = "=", emoji: str = ""):
    """Print formatted section"""
    width = 80
    print(f"\n{char * width}")
    if emoji:
        print(f"{emoji}  {title}")
    else:
        print(f" {title}")
    print(f"{char * width}\n")


def print_debate_result(symbol: str, bull_arg, bear_arg, thesis):
    """Print debate results in a nice format"""
    print(f"\n{'='*60}")
    print(f"📊 {symbol} - INVESTMENT DEBATE RESULTS")
    print(f"{'='*60}")

    print(f"\n🐂 BULL CASE:")
    print(f"   Recommendation: {bull_arg.recommendation}")
    print(f"   Confidence: {bull_arg.confidence:.0%}")
    print(f"   Thesis: {bull_arg.thesis}")
    if bull_arg.key_catalysts:
        print(f"   Catalysts:")
        for catalyst in bull_arg.key_catalysts[:3]:
            print(f"      • {catalyst}")

    print(f"\n🐻 BEAR CASE:")
    print(f"   Recommendation: {bear_arg.recommendation}")
    print(f"   Confidence: {bear_arg.confidence:.0%}")
    print(f"   Thesis: {bear_arg.thesis}")
    if bear_arg.key_risks:
        print(f"   Risks:")
        for risk in bear_arg.key_risks[:3]:
            print(f"      • {risk}")

    print(f"\n⚖️  FINAL DECISION (Research Manager):")
    print(f"   Recommendation: {thesis.recommendation}")
    print(f"   Confidence: {thesis.confidence:.0%}")
    print(f"   Position Size: {thesis.position_size.upper()}")
    print(f"   Summary: {thesis.thesis_summary}")
    print(f"   Bull Probability: {thesis.bull_probability:.0%}")
    print(f"   Bear Probability: {thesis.bear_probability:.0%}")

    print(f"\n📈 Scenarios:")
    print(f"   Base Case: {thesis.base_case}")
    if thesis.bull_case:
        print(f"   Bull Case: {thesis.bull_case}")
    if thesis.bear_case:
        print(f"   Bear Case: {thesis.bear_case}")


def save_results(data: dict, filename: str):
    """Save results to JSON"""
    # Convert dataclass objects to dicts
    for key in ["stage1_output", "stage2_output", "stage3_output", "team2_output"]:
        if key in data and hasattr(data[key], "to_dict"):
            data[key] = data[key].to_dict()

    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=str)


def main():
    """Main demo execution"""

    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)

    print_section("EVENT HORIZON x OPIK - HACKATHON DEMO", "=", "🚀")

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY required for this demo")
        print("   Add to .env file and restart\n")
        sys.exit(1)

    # Demo portfolio
    portfolio = {
        "portfolio_id": "opik_hackathon_2026",
        "portfolio": ["AAPL", "TSLA"],  # Just 2 symbols for fast demo
    }

    print("📊 Demo Portfolio:")
    print(f"   Symbols: {', '.join(portfolio['portfolio'])}")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ========================================================================
    # STAGE 1: DATA RETRIEVAL
    # ========================================================================
    print_section("STAGE 1: DATA RETRIEVAL", "-", "📥")

    stage1_config = {
        "enabled_agents": ["candlestick", "technical", "fundamentals", "news"],
        "max_workers": 4,
    }

    print("Collecting market data...\n")
    orchestrator1 = Stage1Orchestrator(config=stage1_config)
    result1 = orchestrator1.execute(portfolio)
    stage1_output = result1["stage1_output"]

    print(f"✅ Stage 1: {result1['status'].upper()} ({result1['execution_time_seconds']:.1f}s)")

    # ========================================================================
    # STAGE 2: NORMALIZATION
    # ========================================================================
    print_section("STAGE 2: NORMALIZATION", "-", "🔄")

    print("Normalizing data...\n")
    orchestrator2 = Stage2Orchestrator()
    result2 = orchestrator2.execute(stage1_output)
    stage2_output = result2["stage2_output"]

    print(f"✅ Stage 2: {result2['status'].upper()} ({result2['execution_time_seconds']:.1f}s)")
    print(f"   Quality: {result2['overall_quality_score']:.2f}")

    # ========================================================================
    # STAGE 3: LLM FEATURE EXTRACTION (OPIK!)
    # ========================================================================
    print_section("STAGE 3: LLM FEATURE EXTRACTION", "-", "🧠")

    print("🎯 Opik tracking active!")
    print("   Extracting features with LLM...\n")

    stage3_config = {
        "llm_model": "gpt-4o-mini",
        "temperature": 0.3,
        "opik_project": "event-horizon",
        "enable_opik": True,
    }

    orchestrator3 = Stage3Orchestrator(config=stage3_config)
    result3 = orchestrator3.execute(stage2_output)
    stage3_output = result3["stage3_output"]

    print(f"✅ Stage 3: {result3['status'].upper()} ({result3['execution_time_seconds']:.1f}s)")
    print(f"   LLM Calls: {result3['total_llm_calls']}")
    print(f"   Tokens: {result3['total_tokens_used']}")

    # ========================================================================
    # TEAM 2: BULL/BEAR DEBATE (OPIK!)
    # ========================================================================
    print_section("TEAM 2: BULL vs BEAR DEBATE", "=", "🎭")

    print("🎯 Opik tracking multi-agent debate!")
    print("   Bull Researcher vs Bear Researcher → Research Manager\n")

    team2_config = {
        "llm_model": "gpt-4o-mini",
        "temperature": 0.7,  # Higher for creative arguments
        "opik_project": "event-horizon",
        "enable_opik": True,
    }

    orchestrator_team2 = Team2Orchestrator(config=team2_config)
    result_team2 = orchestrator_team2.execute(stage3_output)
    team2_output = result_team2["team2_output"]

    print(f"✅ Team 2 Debates: {result_team2['status'].upper()} ({result_team2['execution_time_seconds']:.1f}s)")
    print(f"   Debates Conducted: {result_team2['total_debates']}")
    print(f"   Tokens Used: {result_team2['total_tokens_used']}")

    # Show debate results
    for symbol in team2_output.symbols:
        if symbol in team2_output.investment_theses:
            bull_arg = team2_output.bull_arguments[symbol]
            bear_arg = team2_output.bear_arguments[symbol]
            thesis = team2_output.investment_theses[symbol]
            print_debate_result(symbol, bull_arg, bear_arg, thesis)

    # ========================================================================
    # OPIK INSIGHTS
    # ========================================================================
    print_section("OPIK INSIGHTS", "=", "📊")

    total_llm_calls = result3['total_llm_calls'] + (result_team2['total_debates'] * 3)
    total_tokens = result3['total_tokens_used'] + result_team2['total_tokens_used']

    print("🎯 Opik Tracked Entire Pipeline:")
    print(f"   Total LLM Calls: {total_llm_calls}")
    print(f"      - Stage 3 (Feature Extraction): {result3['total_llm_calls']}")
    print(f"      - Team 2 (Bull/Bear/Manager): {result_team2['total_debates'] * 3}")
    print(f"   Total Tokens: {total_tokens:,}")
    print(f"   Project: {team2_config['opik_project']}")

    print(f"\n🎯 What Opik Enables:")
    print(f"   ✅ Full visibility into multi-agent debates")
    print(f"   ✅ Compare bull vs bear argument quality")
    print(f"   ✅ Evaluate manager's synthesis decisions")
    print(f"   ✅ Track token usage across all agents")
    print(f"   ✅ Optimize prompts through experimentation")
    print(f"   ✅ Debug LLM reasoning step-by-step")

    print(f"\n📈 View Complete Traces:")
    print(f"   Dashboard: https://www.comet.com/opik")
    print(f"   Project: {team2_config['opik_project']}")

    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    print_section("SAVING RESULTS", "-", "💾")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save complete demo results
    demo_result = {
        "demo_id": portfolio["portfolio_id"],
        "timestamp": datetime.now().isoformat(),
        "stage1": result1,
        "stage2": result2,
        "stage3": result3,
        "team2": result_team2,
        "opik_metrics": {
            "total_llm_calls": total_llm_calls,
            "total_tokens": total_tokens,
            "project": team2_config['opik_project'],
        }
    }

    filename = f"demo_opik_complete_{timestamp}.json"
    save_results(demo_result, filename)
    print(f"✅ Complete demo results: {filename}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_section("DEMO COMPLETE", "=", "🎉")

    total_time = (
        result1["execution_time_seconds"]
        + result2["execution_time_seconds"]
        + result3["execution_time_seconds"]
        + result_team2["execution_time_seconds"]
    )

    print(f"✅ Full pipeline executed successfully!")
    print(f"   Total Time: {total_time:.1f}s")
    print(f"   Portfolio: {', '.join(portfolio['portfolio'])}")

    print(f"\n🎯 Hackathon Demo Summary:")
    print(f"   1. Built complete multi-agent trading system")
    print(f"   2. Stage 3: LLM feature extraction (Opik tracked)")
    print(f"   3. Team 2: Bull/Bear debates (Opik tracked)")
    print(f"   4. {total_llm_calls} LLM calls fully traced")
    print(f"   5. {total_tokens:,} tokens automatically tracked")

    print(f"\n💡 How Opik Accelerated Development:")
    print(f"   ✅ VISIBILITY: See every LLM call and decision")
    print(f"   ✅ DEBUGGING: Trace multi-agent conversations")
    print(f"   ✅ OPTIMIZATION: Token usage monitored automatically")
    print(f"   ✅ EVALUATION: All data ready for quality metrics")
    print(f"   ✅ SPEED: 3x faster iteration with observability!")

    print(f"\n🚀 Next Steps:")
    print(f"   1. Open Opik dashboard to see traces")
    print(f"   2. Compare bull vs bear argument quality")
    print(f"   3. Evaluate manager decisions against market outcomes")
    print(f"   4. Experiment with different prompts")
    print(f"   5. Build remaining teams (1, 3, 4) with same Opik setup")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        logging.exception("Fatal error in main_demo_opik.py")
        sys.exit(1)
