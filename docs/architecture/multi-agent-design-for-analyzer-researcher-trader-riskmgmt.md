# Event Horizon - Financial Analysis Multi-Agent System

Multi-agent architecture for financial analysis, research, trading decisions, and risk management.

**Note**: This system operates **AFTER** the 3-layer data processing pipeline completes. It consumes the output from Layer 3 (feature-extracted data) to make intelligent trading decisions.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Agent Teams](#agent-teams)
3. [Workflow & Communication](#workflow--communication)
4. [Integration with Data Pipeline](#integration-with-data-pipeline)
5. [Tauric Research Patterns](#tauric-research-patterns)
6. [Implementation Roadmap](#implementation-roadmap)

---

## Architecture Overview

### System Position in Event Horizon

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EVENT HORIZON DATA PIPELINE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Layer 1: Data Retrieval    (candlestick, news, earnings, etc.)       │
│           ↓                                                             │
│  Layer 2: Normalization     (standardized "DNA" dataset)               │
│           ↓                                                             │
│  Layer 3: Feature Extraction (LLM/Neural feature discovery)            │
│           ↓                                                             │
│  📊 Feature-Extracted Dataset Ready                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│              FINANCIAL ANALYSIS MULTI-AGENT SYSTEM                      │
│                   (This Document's Scope)                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      ANALYST TEAM                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │ Fundamentals │  │    Market    │  │     News     │          │  │
│  │  │   Analyst    │  │   Analyst    │  │   Analyst    │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │  ┌──────────────┐                                               │  │
│  │  │ Social Media │                                               │  │
│  │  │   Analyst    │                                               │  │
│  │  └──────────────┘                                               │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    RESEARCHER TEAM                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │     Bull     │  │     Bear     │  │   Research   │          │  │
│  │  │  Researcher  │  │  Researcher  │  │   Manager    │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │                 (Debate & Consensus)                             │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                   RISK MANAGEMENT TEAM                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │ Conservative │  │   Neutral    │  │  Aggressive  │          │  │
│  │  │   Debator    │  │   Debator    │  │   Debator    │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │                 (Risk Assessment & Position Sizing)              │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      TRADER AGENT                                │  │
│  │                                                                  │  │
│  │  • Final trading decision                                       │  │
│  │  • Portfolio allocation                                         │  │
│  │  • Order execution strategy                                     │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│                     🎯 Trading Actions                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Teams

### 1. Analyst Team

**Purpose**: Analyze different aspects of market data and provide specialized insights

**Agents**:

#### Fundamentals Analyst
- **Input**: Company financial data, earnings reports, balance sheets
- **Analysis**: Financial health, valuation ratios, growth metrics
- **Output**: Fundamental strength score and reasoning

#### Market Analyst
- **Input**: Price action, technical indicators, volume patterns
- **Analysis**: Trend identification, support/resistance, momentum
- **Output**: Technical outlook and key levels

#### News Analyst
- **Input**: News articles, headlines, sentiment
- **Analysis**: News impact, sentiment shift, event catalysis
- **Output**: News sentiment score and key narratives

#### Social Media Analyst
- **Input**: Twitter/Reddit mentions, sentiment, trending topics
- **Analysis**: Retail sentiment, hype detection, community pulse
- **Output**: Social sentiment score and viral trends

**Team Output**: Multi-dimensional analysis report consolidating all perspectives

---

### 2. Researcher Team

**Purpose**: Debate investment thesis from bull and bear perspectives to reach balanced conclusion

**Agents**:

#### Bull Researcher
- **Role**: Advocate for long positions
- **Analysis**: Find positive catalysts, growth opportunities, upside potential
- **Stance**: Optimistic, growth-focused

#### Bear Researcher
- **Role**: Advocate for short positions or caution
- **Analysis**: Identify risks, overvaluation, downside scenarios
- **Stance**: Skeptical, risk-focused

#### Research Manager
- **Role**: Facilitate debate, synthesize perspectives
- **Process**:
  1. Present analyst team findings to bull/bear researchers
  2. Conduct multi-round debate (configurable rounds)
  3. Weigh arguments based on data strength
  4. Generate consensus investment thesis

**Team Output**: Balanced investment recommendation with bull/bear case and probability-weighted scenarios

---

### 3. Risk Management Team

**Purpose**: Assess risk and determine appropriate position sizing through multi-perspective debate

**Agents**:

#### Conservative Debator
- **Stance**: Risk-averse, capital preservation focused
- **Analysis**: Downside protection, worst-case scenarios
- **Recommendation**: Smaller positions, tight stops

#### Neutral Debator
- **Stance**: Balanced risk-reward assessment
- **Analysis**: Expected value, risk-adjusted returns
- **Recommendation**: Moderate positions, standard risk parameters

#### Aggressive Debator
- **Stance**: Return-maximizing, higher risk tolerance
- **Analysis**: Upside potential, asymmetric opportunities
- **Recommendation**: Larger positions, wider stops

#### Risk Manager (Orchestrator)
- **Role**: Facilitate risk debate, determine final risk parameters
- **Process**:
  1. Present investment thesis from researcher team
  2. Conduct risk assessment debate
  3. Synthesize risk perspectives
  4. Set position size, stop loss, take profit levels

**Team Output**: Risk-adjusted position sizing with entry/exit parameters

---

### 4. Trader Agent

**Purpose**: Execute final trading decision based on all team inputs

**Responsibilities**:
- Review all team outputs (analyst, researcher, risk management)
- Make final go/no-go decision
- Determine exact position sizing within risk parameters
- Generate order execution strategy
- Monitor position post-entry

**Decision Framework**:
```python
if analyst_score > threshold and investment_thesis == "BUY":
    if risk_parameters.acceptable:
        execute_trade(
            symbol=symbol,
            direction=direction,
            size=risk_parameters.position_size,
            entry=entry_price,
            stop_loss=risk_parameters.stop_loss,
            take_profit=risk_parameters.take_profit
        )
```

---

## Workflow & Communication

### Sequential Team Execution

```
1. Data Ingestion
   ↓
2. Analyst Team (Parallel)
   - All 4 analysts run simultaneously
   - Consolidate findings
   ↓
3. Researcher Team (Sequential Debate)
   - Bull/Bear debate in rounds
   - Research Manager synthesizes
   ↓
4. Risk Management Team (Sequential Debate)
   - Conservative/Neutral/Aggressive debate
   - Risk Manager sets parameters
   ↓
5. Trader Agent (Final Decision)
   - Review all inputs
   - Execute or reject trade
```

### Communication Pattern

**Framework**: LangGraph for state management and workflow orchestration

**State Object**:
```python
class TradingAgentState:
    # Input
    portfolio: List[str]
    layer3_features: Dict[str, Any]  # From data pipeline

    # Analyst Team Output
    analyst_reports: Dict[str, AnalystReport]

    # Researcher Team Output
    investment_thesis: InvestmentThesis
    bull_case: str
    bear_case: str
    confidence: float

    # Risk Management Output
    risk_parameters: RiskParameters
    position_size: float
    stop_loss: float
    take_profit: float

    # Trader Output
    trading_decision: TradingDecision
    execution_plan: ExecutionPlan
```

---

## Integration with Data Pipeline

### Data Flow

```
Layer 1 → Layer 2 → Layer 3 → Financial Analysis Agents
  ↓         ↓         ↓              ↓
Raw      Standard   Features    Trading Decisions
Data       DNA      Extracted
```

### Interface Contract

**Input to Financial Analysis System**:
```python
# Layer 3 Output (Feature-Extracted Dataset)
{
    "portfolio_id": "...",
    "symbols": ["AAPL", "TSLA"],
    "features": {
        "AAPL": {
            "company_health_score": 0.85,
            "investor_sentiment_score": 0.72,
            "technical_momentum_score": 0.68,
            "macro_alignment_score": 0.55,
            "risk_score": 0.33,
            # ... extracted features
        }
    },
    "metadata": {...}
}
```

**Output from Financial Analysis System**:
```python
{
    "trading_decisions": [
        {
            "symbol": "AAPL",
            "action": "BUY",
            "position_size": 100,
            "entry_price": 185.50,
            "stop_loss": 178.00,
            "take_profit": 198.00,
            "confidence": 0.78,
            "rationale": "Strong fundamentals + bullish technical setup..."
        }
    ]
}
```

---

## Tauric Research Patterns

This architecture is inspired by the [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) framework.

### Key Patterns Adopted

1. **Multi-Agent Debate**: Bull/Bear researchers and risk debators engage in structured debate
2. **Hierarchical Teams**: Analysts → Researchers → Risk Management → Trader
3. **State Management**: LangGraph for workflow orchestration
4. **Tool-Based Agents**: Agents use specialized tools for data analysis
5. **Configurable Rounds**: Debate rounds are configurable (max_debate_rounds, max_risk_discuss_rounds)

### Tauric Agent Mapping

| Tauric Agent | Event Horizon Equivalent |
|--------------|-------------------------|
| fundamentals_analyst | Fundamentals Analyst |
| market_analyst | Market Analyst |
| news_analyst | News Analyst |
| social_media_analyst | Social Media Analyst |
| bull_researcher | Bull Researcher |
| bear_researcher | Bear Researcher |
| research_manager | Research Manager |
| safe_debator | Conservative Debator |
| neutral_debator | Neutral Debator |
| risky_debator | Aggressive Debator |
| risk_manager | Risk Manager |
| trader | Trader Agent |

### Reference Location

Full Tauric codebase cloned to: `core_refs/TradingAgents/`

---

## Implementation Roadmap

### Phase 1: Foundation (Current)
- ✅ Layer 1 data retrieval agents implemented
- ✅ Tauric repository cloned for reference
- ⏳ Layer 2 normalization (in progress)
- ⏳ Layer 3 feature extraction (planned)

### Phase 2: Analyst Team
- [ ] Implement 4 analyst agents (fundamentals, market, news, social)
- [ ] Create analyst orchestrator for parallel execution
- [ ] Define analyst report schema
- [ ] Test analyst team on sample data

### Phase 3: Researcher Team
- [ ] Implement bull/bear researchers
- [ ] Implement research manager with debate logic
- [ ] Create investment thesis schema
- [ ] Test multi-round debate mechanism

### Phase 4: Risk Management Team
- [ ] Implement 3 risk debators (conservative, neutral, aggressive)
- [ ] Implement risk manager with debate orchestration
- [ ] Define risk parameters schema
- [ ] Test position sizing logic

### Phase 5: Trader Agent
- [ ] Implement trader agent decision logic
- [ ] Create execution plan generator
- [ ] Integrate with all upstream teams
- [ ] End-to-end system testing

### Phase 6: LangGraph Integration
- [ ] Design state machine for workflow
- [ ] Implement LangGraph orchestration
- [ ] Add checkpointing and retry logic
- [ ] Performance optimization

---

## Future Enhancements

### Advanced Features
- **Portfolio-Level Analysis**: Multi-stock correlation and portfolio construction
- **Continuous Learning**: Agent performance tracking and strategy refinement
- **Market Regime Detection**: Adapt strategy based on market conditions
- **Backtesting Integration**: Historical simulation of agent decisions
- **Real-Time Monitoring**: Live position tracking and dynamic adjustment

### Scalability
- **Agent Versioning**: A/B test different agent implementations
- **Parallel Portfolio Processing**: Handle multiple portfolios simultaneously
- **Distributed Execution**: Scale agents across multiple machines
- **Caching & Optimization**: Reduce redundant computation

---

## Summary

The Financial Analysis Multi-Agent System is a **separate layer** from the data processing pipeline (Layers 1-3). It consumes feature-extracted data and uses a team-based approach inspired by Tauric Research to make intelligent trading decisions.

**Key Principles**:
1. **Separation of Concerns**: Data processing ≠ Decision making
2. **Multi-Perspective Analysis**: Debate and consensus for robust decisions
3. **Risk-Aware**: Explicit risk management team prevents reckless trades
4. **Inspired by Research**: Leverages proven patterns from Tauric framework
5. **Extensible Architecture**: Easy to add new agent types and capabilities

This system will be implemented **after** the 3-layer data pipeline is complete and stable.
