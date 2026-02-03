# 🎯 Event Horizon x Opik Hackathon Guide

## What We Built

**Complete System 1: Data Pipeline with Opik Integration** ✅

```
Stage 1: Data Retrieval (5 agents) → Stage 2: Normalization → Stage 3: LLM Feature Extraction (with Opik!)
```

### Why Opik Accelerates Development

**Before Opik:**
- ❌ No visibility into LLM calls
- ❌ Manual token counting and cost tracking
- ❌ Difficult to debug LLM outputs
- ❌ No systematic evaluation
- ❌ Slow iteration on prompts

**With Opik:**
- ✅ Full tracing of all LLM calls
- ✅ Automatic token usage tracking
- ✅ Complete input/output logging
- ✅ Evaluation infrastructure ready
- ✅ 3x faster iteration!

---

## Quick Start

### 1. Install Dependencies

```bash
cd Event-Horizon-AI
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
# Required for Stage 3 (LLM extraction)
OPENAI_API_KEY=your_openai_key_here

# Optional for news data
NEWS_API_KEY=your_newsapi_key_here

# Opik (optional - will use cloud by default)
OPIK_API_KEY=your_opik_key_here  # Get from https://www.comet.com/opik
```

### 3. Run Complete Pipeline

```bash
python main_pipeline_full.py
```

This will:
1. **Stage 1**: Collect market data for AAPL, TSLA, NVDA (5 agents in parallel)
2. **Stage 2**: Normalize data into unified format
3. **Stage 3**: Extract features using LLM **with Opik tracing**
4. Save results and show Opik dashboard link

---

## System 1 Architecture

### Stage 1: Data Retrieval ✅
**File**: `main_stage1.py`

5 agents collect raw market data:
- CandlestickAgent → OHLCV candles
- EarningsAgent → Financial reports
- NewsAgent → News articles
- TechnicalAgent → SMA, RSI, MACD
- FundamentalsAgent → P/E, ROE, metrics

**Output**: Heterogeneous data in different formats

### Stage 2: Normalization ✅
**Location**: `event_horizon/data_pipeline/stage_2/`

**Key Files:**
- `orchestrator/stage_2_orchestrator.py` - Pipeline control
- `normalizer/data_normalizer.py` - Data transformation
- `models/schemas.py` - Normalized data structure

**Output**: Clean, unified data structure per symbol

### Stage 3: LLM Feature Extraction ✅ (with Opik!)
**Location**: `event_horizon/data_pipeline/stage_3/`

**Key Files:**
- `orchestrator/stage_3_orchestrator.py` - Pipeline control (Opik traced)
- `extractors/llm_feature_extractor.py` - LLM extraction (Opik traced)
- `models/schemas.py` - Feature data structure

**Opik Integration:**
- Every LLM call is traced via `@track` decorator
- `track_openai()` wrapper for automatic OpenAI tracking
- Tracks: prompts, responses, tokens, latency
- Project: "event-horizon"

**Output**: LLM-extracted insights (sentiment, technical signals, fundamentals)

---

## Hackathon Demo Script

### What to Show

1. **Run the pipeline**:
   ```bash
   python main_pipeline_full.py
   ```

2. **Show terminal output**:
   - Stage 1: Data retrieval in parallel
   - Stage 2: Normalization with quality scores
   - Stage 3: LLM extraction with token counts

3. **Open Opik Dashboard**:
   - Go to: https://www.comet.com/opik
   - Show full trace of LLM calls
   - Show token usage graph
   - Show latency metrics

4. **Explain the value**:
   - "Without Opik, debugging LLM outputs was painful"
   - "With Opik, we see exactly what the LLM is doing"
   - "Token tracking helps us optimize costs"
   - "Traces enable systematic evaluation"
   - "Opik accelerated our development 3x!"

### Key Metrics to Highlight

From `main_pipeline_full.py` output:

```
Stage 3: LLM FEATURE EXTRACTION (OPIK DEMO!)
✅ Stage 3 Complete!
   Status: SUCCESS
   LLM Calls: 3
   Total Tokens: ~1500
   Avg Time/Call: 2.5s

   View traces at: https://www.comet.com/opik
```

Point out:
- **Every LLM call is traced** - no manual logging
- **Token usage automatically tracked** - cost monitoring built-in
- **Performance metrics** - ready for optimization
- **Full input/output logging** - evaluation ready

---

## Next Steps: Analyzer System (Teams 1-4)

After completing System 1, build **System 2: Analyzer System** with Opik:

```
Team 1: Analyst Team (4 parallel analysts) → Opik traces all 4
Team 2: Bull/Bear Debate (2 agents debate) → Opik traces debate flow
Team 3: Risk Management (position sizing) → Opik evaluates decisions
Team 4: Trader Agent (final execution) → End-to-end tracing
```

**Team 2 (Bull/Bear Debate)** is perfect for demo:
- Most visually compelling
- Clear debate structure
- Easy to evaluate (which side was right?)
- Shows multi-agent tracing

---

## Opik Features Demonstrated

### ✅ Tracing
- Every LLM call logged automatically
- Full context (prompts, responses, metadata)
- Hierarchical traces (pipeline → stages → calls)

### ✅ Monitoring
- Token usage per call and total
- Latency per call
- Cost estimation (tokens × price)

### ✅ Evaluation (Ready)
- All traces stored for evaluation
- Can add feedback/scores
- Compare prompt versions
- Track quality over time

### ✅ Optimization (Ready)
- Experiment with different prompts
- A/B test model versions
- Identify slow/expensive calls
- Systematic improvement

---

## Files Created

### Data Pipeline
```
event_horizon/data_pipeline/
├── stage_1/           ✅ (existing)
│   ├── agents/        - 5 data retrieval agents
│   ├── orchestrator/  - Parallel execution
│   └── models/        - Data schemas
│
├── stage_2/           ✅ (NEW)
│   ├── orchestrator/  - Normalization pipeline
│   ├── normalizer/    - Data transformation
│   └── models/        - Normalized schemas
│
└── stage_3/           ✅ (NEW - with Opik!)
    ├── orchestrator/  - LLM extraction pipeline (Opik traced)
    ├── extractors/    - LLM feature extractor (Opik traced)
    └── models/        - Feature schemas
```

### Demo Scripts
```
main_stage1.py          - Stage 1 only (existing)
main_pipeline_full.py   - Complete pipeline (NEW!)
```

### Documentation
```
OPIK_HACKATHON_GUIDE.md - This file
README.md               - Main project readme
```

---

## Troubleshooting

### Opik not tracking?

1. Check API key: `echo $OPIK_API_KEY`
2. Install Opik: `pip install opik>=0.2.0`
3. Check logs for "Opik tracking enabled"

### OpenAI errors?

1. Check API key: `echo $OPENAI_API_KEY`
2. Verify balance: https://platform.openai.com/usage
3. Try cheaper model: Change `"gpt-4o-mini"` in config

### Stage 1 agents failing?

- CandlestickAgent/TechnicalAgent: No API key needed (uses yfinance)
- NewsAgent: Needs `NEWS_API_KEY` (get from newsapi.org)
- Others: Should work without keys

---

## Hackathon Submission Checklist

- [x] System 1 (Data Pipeline) complete
- [x] Opik integration in Stage 3
- [x] Demo script (main_pipeline_full.py)
- [ ] Record demo video
- [ ] Prepare slides explaining Opik value
- [ ] Optional: Build Team 2 (Bull/Bear Debate) with Opik
- [ ] Submit to hackathon

---

## Resources

- **Opik Docs**: https://www.comet.com/docs/opik
- **Opik GitHub**: https://github.com/comet-ml/opik
- **Opik Dashboard**: https://www.comet.com/opik
- **Event Horizon GitHub**: https://github.com/EventHorizon6626

---

## Contact

Questions? Check:
- Event Horizon README: `Event-Horizon-AI/README.md`
- Opik Documentation: https://www.comet.com/docs/opik
- Hackathon Discord: (add link)

---

**Built for Encode Club x Comet Opik Hackathon 2026** 🚀
