# Core References & Inspiration

This directory contains core references, research papers, and projects that inspire and inform the Event Horizon AI architecture and design.

---

## Research Papers

### TradingAgents: Multi-Agents LLM Financial Trading Framework

**Paper**: [https://arxiv.org/pdf/2412.20138](https://arxiv.org/pdf/2412.20138)

**Authors**: Yijia Xiao, Edward Sun, Di Luo, Wei Wang

**Summary**:
This research paper presents a novel stock trading framework inspired by professional trading firms. It features LLM-powered agents in specialized roles including fundamental analysts, sentiment analysts, technical analysts, and traders with varied risk profiles. The system includes risk management oversight and demonstrates improvements in cumulative returns, Sharpe ratio, and maximum drawdown compared to baseline approaches.

The framework leverages large language models to create a dynamic environment where agents debate market conditions and synthesize insights from multiple perspectives, ultimately outperforming traditional single-agent trading systems.

**Key Concepts**:
- Multi-agent collaboration for trading decisions
- Specialized agent roles (fundamental, sentiment, technical analysis)
- Risk management and portfolio oversight
- LLM-powered financial analysis
- Agent debate and consensus mechanisms

**Relevance to Event Horizon AI**:
- Validates our multi-agent architecture approach
- Provides research-backed evidence for specialized agent design
- Demonstrates effectiveness of collaborative agent systems in financial markets
- Informs our NewsAgent, ReportAgent, and ChartAgent specialization strategy

---

## Open Source Projects

### TradingAgents Framework

**Repository**: [https://github.com/TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)

**Description**:
Open-source implementation of the TradingAgents research paper. This framework provides a complete multi-agent system for financial trading research using LLMs.

**Architecture**:

1. **Analyst Team**:
   - Fundamental Analyst
   - Sentiment Analyst
   - News Analyst
   - Technical Analyst

2. **Researcher Team**:
   - Bullish Researcher
   - Bearish Researcher
   - Structured debate mechanism

3. **Trading Team**:
   - Trader Agent (synthesizes analysis for decisions)
   - Portfolio Manager (risk approval)
   - Risk Management (continuous monitoring)

**Key Features**:
- Real-time market analysis across multiple dimensions
- Collaborative agent discussions for optimal strategies
- Integration with yfinance and Alpha Vantage
- Configurable AI models and debate parameters
- Simulated trade execution

**Relevance to Event Horizon AI**:
- Reference implementation for multi-agent trading systems
- Demonstrates practical LLM integration patterns
- Shows how to structure agent collaboration
- Provides inspiration for expanding our agent ecosystem
- Example of production-ready agent framework

**Note**: Research purposes only, not financial advice.

---

## Implementation Learnings

### Agent Specialization
Both the paper and repository validate our approach of specialized agents:
- **NewsAgent** → Sentiment/News Analyst
- **ReportAgent** → Fundamental Analyst
- **ChartAgent** → Technical Analyst

### Future Enhancements Inspired
- Add debate/consensus mechanism between agents
- Implement risk management agent
- Create portfolio manager for trade approval
- Add bullish/bearish researcher roles
- Structured agent collaboration protocols

---

## Additional Resources

_Add more core references and inspiration sources below as the project evolves._

---

**Last Updated**: 2026-01-18
