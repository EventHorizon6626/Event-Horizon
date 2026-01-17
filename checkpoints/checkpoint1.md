# Checkpoint 1 Submission - Event Horizon AI

**Deadline**: Monday, January 19, 2026 at 12:59 PM (Europe/Paris)

---

## Core Project Details

### Project Name
**Event Horizon AI - Multi-Agent Financial Intelligence System**

### Team Members

1. **Lê Hoàng Triệu Vỹ** - Leader
2. **Pham Huy**

---

## Project Description

Event Horizon AI is an intelligent educational platform that empowers investors at every skill level—from beginners to experts—to understand and monitor their financial health through AI-powered feature extraction and progressive learning tools.

### The Problem
Most people struggle to learn investment and financial analysis because:
- **Information Overload**: Beginners are overwhelmed by fragmented data sources (news, earnings reports, market data, social media) without knowing what matters
- **Steep Learning Curve**: Understanding which financial metrics are meaningful requires years of domain expertise
- **Lack of Personalized Learning**: Existing tools either oversimplify (robo-advisors making all decisions) or assume expert knowledge (Bloomberg Terminal)
- **No Progressive Path**: There's no clear journey from "I want to learn investing" to "I can analyze companies and portfolios independently"
- **Hidden Complexity**: Investors can't see WHY certain features matter or HOW they relate to financial health

### Our Solution
A three-layer intelligent platform that grows with you, extracting and explaining meaningful features to help you monitor and understand your financial health—not to make decisions FOR you, but to help you make INFORMED decisions yourself:

**Layer 1 - Data Collection (The Foundation)**: Automated agents gather all relevant financial information:
- Market data (prices, volume, technical indicators)
- Company fundamentals (earnings, balance sheets, cash flow)
- News and sentiment (articles, social media, analyst opinions)
- Insider activity and institutional movements
- Macroeconomic context (interest rates, sector trends)

**Layer 2 - Smart Filtering & Standardization (Your Financial DNA)**: Transform messy data into clear, understandable health metrics:
- Organize data into 5 intuitive categories you can actually understand:
  - **Company Health**: Is the business strong? (revenue growth, profitability, debt levels)
  - **Market Sentiment**: What do others think? (news tone, social buzz, analyst ratings)
  - **Technical Signals**: What's the price telling us? (trends, momentum, support levels)
  - **External Factors**: What's happening in the bigger picture? (sector performance, economy)
  - **Risk Assessment**: How risky is this investment? (volatility, drawdowns, liquidity)
- Present 80+ meaningful features in simple, visual dashboards
- Explain WHAT each metric means and WHY it matters for your financial health

**Layer 3 - AI-Powered Learning & Insights (Your Investment Tutor)**:
- **For Beginners**: Highlight the top 5-10 most important features to watch, explain them in plain English
- **For Intermediate**: Show correlations and patterns ("When X happens, Y often follows")
- **For Advanced**: Provide deep analysis of complex relationships, regime detection, multi-factor insights
- **Never Makes Decisions**: Instead, the AI asks you questions: "Given these signals, what do YOU think?" and explains the reasoning behind different interpretations

### Progressive Learning Path

**Beginner Mode (Weeks 1-4)**: Learn the Basics
- Dashboard shows 5-10 key metrics with simple explanations
- Interactive tutorials: "What is P/E ratio?", "Why does debt matter?"
- Portfolio health score with color-coded indicators (green = healthy, red = warning)
- Daily insights: "Your tech stocks are down 2% today because..."

**Intermediate Mode (Months 2-6)**: Build Your Analysis Skills
- Unlock 20-30 metrics with deeper explanations
- Compare companies side-by-side on key metrics
- Learn to spot patterns: "Notice how high revenue growth + low margins often means..."
- Practice mode: AI shows you a scenario, you predict the outcome, then see the real result

**Expert Mode (6+ Months)**: Master Advanced Analysis
- Access all 80+ features with full technical documentation
- Custom feature builder: create your own derived metrics
- Backtesting playground: test your investment thesis on historical data
- AI as a research assistant: "Show me all companies with improving margins and declining debt"

### Technology Stack
- **Backend**: Python, FastAPI
- **Agents**: Multi-agent orchestration with async execution
- **AI/ML**: LLM-based explanations, neural feature extractors
- **Data**: Pandas, NumPy for processing
- **APIs**: Yahoo Finance, Alpha Vantage, News APIs
- **Frontend**: Interactive dashboards with educational tooltips
- **Infrastructure**: Docker, Kubernetes (for scaling)

### Current Progress
✅ Built foundational agent architecture (BaseAgent class)
✅ Implemented Candlestick Data Agent (Yahoo Finance integration)
✅ Implemented Earnings Report Agent (Alpha Vantage API)
✅ Implemented News Sentiment Agent (NewsAPI integration)
✅ Created configuration system (YAML-based)
✅ Documented three-layer architecture design
🔄 Building Layer 2 normalization pipeline
🔄 Researching tabular LLM frameworks for Layer 3

### What Makes Us Unique
1. **Education-First, Not Automation**: We don't make decisions for you—we teach you to make better decisions yourself
2. **Progressive Learning Journey**: Content and tools adapt to your skill level, from complete beginner to expert analyst
3. **Explain Everything**: Every metric, every insight comes with "Why this matters" and "How to interpret it"
4. **AI as a Tutor, Not a Black Box**: Our AI explains its reasoning, asks you questions, and helps you learn critical thinking
5. **Real-Time Financial Health Monitoring**: See your portfolio's health across 80+ metrics updated continuously
6. **Practice Makes Perfect**: Interactive scenarios and backtesting let you learn without risking real money

### Impact
- **For Beginners**: Learn to invest confidently without being overwhelmed or relying on "just trust the algorithm"
- **For Intermediate Investors**: Develop analytical skills to evaluate companies like a professional analyst
- **For Experienced Traders**: Access institutional-grade feature extraction and monitoring tools
- **For Educators**: Use as a teaching platform in finance courses and investment clubs
- **Long-term Vision**: Democratize financial literacy—help millions understand their money and build wealth intelligently

---

## Project Image - AI Generation Prompt

### Image Description for Generative AI

**Prompt for Image Generation:**

```
Create an inspiring, educational financial technology visualization showing a journey from beginner to expert investor.

Left side (beginner - soft blue glow): Simple, friendly dashboard with 5 large, clear metric cards (like health vitals), gentle icons, and a helpful AI assistant avatar with a welcoming expression. Show a person looking curious and engaged.

Center (intermediate - green/teal transition): More detailed analytics appearing, charts becoming visible, connections being drawn between metrics with glowing lines. The person now looks more confident, taking notes or analyzing.

Right side (expert - purple/gold mastery): Complex multi-layered dashboard with advanced charts, network graphs showing correlations, 80+ data points elegantly organized. The person appears confident and in control, making their own decisions.

Background: Deep space theme with a stylized event horizon (black hole accretion disk) representing the vast knowledge frontier. The event horizon glows at the center, symbolizing the journey toward financial mastery. Stars and subtle constellation patterns suggest unlimited potential.

Include: Floating UI elements showing "Company Health", "Sentiment Analysis", "Risk Metrics" with friendly explanations. Small AI tutor icons asking questions: "What do you think this means?"

Style: Modern, approachable yet professional. Balance between educational (warm, inviting) and high-tech (sleek, innovative). Use gradient from calming blues (beginner) to confident purples/golds (expert). Not intimidating—empowering.

Text overlay: "Event Horizon AI" in sleek, approachable font. Tagline: "Your Journey to Financial Mastery" or "Learn. Monitor. Master."

Aspect ratio: 16:9 landscape for presentation slides.
```

**Alternative Simplified Prompt:**
```
Split-screen image: Left shows a beginner investor with simple, colorful financial health dashboard (5 clear metrics with explanations). Right shows the same person months later, now confidently analyzing complex charts and patterns. Center shows an AI tutor guiding the transformation. Event horizon visual in background representing the knowledge journey. Modern fintech aesthetic with warm blues transitioning to confident purples. Educational, empowering mood.
```

---

## Hackathon Briefing

### Competition Alignment

**Track**: [Select applicable track - e.g., FinTech / EdTech / AI/ML / Social Impact]

**Why Event Horizon AI is Perfect for This Track:**

*If FinTech Track:*
- **Innovation**: Transforms fintech from automation to education—teaching users to fish instead of giving them fish
- **Financial Inclusion**: Democratizes access to institutional-grade analysis tools for everyday investors
- **Real-World Impact**: Addresses the massive financial literacy gap affecting millions of retail investors

*If EdTech Track:*
- **Progressive Learning**: Adaptive educational system that grows with the learner from beginner to expert
- **AI-Powered Tutoring**: LLM acts as a personalized financial education tutor, not a black box
- **Measurable Outcomes**: Users gain genuine financial literacy and analytical skills, not just returns

*If AI/ML Track:*
- **Novel AI Application**: Using LLMs for financial education and explanation, not just prediction
- **Multi-Agent Architecture**: Complex orchestration of data agents, normalization, and intelligent tutoring
- **Explainable AI**: Every AI output comes with reasoning and educational context

*If Social Impact:*
- **Financial Literacy Crisis**: Only 57% of adults are financially literate; we're addressing this at scale
- **Wealth Inequality**: Better financial education = better decisions = more equitable wealth building
- **Empowerment**: Teaching people to understand their money builds confidence and long-term security

### Key Differentiators from Competitors

1. **Not a Robo-Advisor**: Unlike Betterment or Wealthfront, we don't manage money—we teach you to understand it
2. **Not a Trading Bot**: Unlike algorithmic trading platforms, we don't give you signals—we help you learn to read them yourself
3. **Not Just Data Dashboards**: Unlike Yahoo Finance or TradingView, we EXPLAIN what the data means at your skill level
4. **Progressive Education**: Unlike Bloomberg Terminal (expert-only) or Robinhood (beginner-only), we grow with you from day 1 to expert
5. **AI as Teacher**: Our LLM doesn't predict—it educates, questions, and helps you develop investment judgment
6. **Financial Literacy Mission**: We measure success not by returns, but by how well users understand their investments

### Demonstration Plan

**What We'll Show at Checkpoint 1:**
1. Live demo of 3 working agents collecting real market data for a sample portfolio
2. Architecture diagram of three-layer educational system
3. Sample "Financial Health DNA" dashboard with beginner-friendly explanations
4. Interactive example: "Here's a metric—what do you think it means?" → AI provides explanation

**Final Presentation Goals:**
1. End-to-end user journey: Complete beginner → Analyzing first stock → Understanding portfolio health
2. Show all 3 learning modes: Beginner (simplified), Intermediate (comparative), Expert (full features)
3. Live demo: User asks "Why did my portfolio drop today?" → AI explains with context and education
4. Testimonial simulation: "Before Event Horizon, I didn't know what P/E meant. Now I can analyze companies confidently."

### Business Model (Optional)

**Freemium Education Platform:**

**Free Tier** (Build the community):
- Beginner mode with 5-10 key metrics
- Portfolio health monitoring for up to 5 stocks
- Basic educational content and tutorials
- Community forum access

**Premium Tier** ($9.99-$19.99/month):
- Intermediate + Expert modes unlocked
- Monitor unlimited stocks and portfolios
- Advanced AI tutor with personalized learning paths
- Backtesting and practice scenarios
- Priority support

**Pro Tier** ($49-$99/month) for serious investors:
- All 80+ features with real-time updates
- Custom feature builder and advanced analytics
- API access for integration with trading platforms
- Downloadable reports and data exports

**Enterprise/Educator Licensing:**
- Universities and financial education programs
- Corporate training for financial advisors
- White-label solution for brokerage platforms

**Go-to-Market:**
- Phase 1: Free tier launch to build user base and gather feedback
- Phase 2: Premium features for engaged learners
- Phase 3: Partner with finance educators and influencers
- Phase 4: Enterprise partnerships with brokerages (integrate into their apps)

---

## Progress Checklist

### Core Project Details
- [x] Project Name: Event Horizon AI
- [x] Team Members: Lê Hoàng Triệu Vỹ (Leader), Pham Huy
- [x] Project Description: Completed above
- [x] Project Image: AI generation prompt provided
- [x] Challenges & Tracks: Identified (AI/ML, FinTech)

### Technical Progress
- [x] Repository setup with documentation
- [x] Base agent architecture implemented
- [x] 3 data retrieval agents built and tested
- [x] Configuration system (YAML-based)
- [x] Three-layer architecture documented
- [ ] Layer 2 normalization pipeline (in progress)
- [ ] Layer 3 AI feature extractor (planned)
- [ ] End-to-end integration test (planned)

### Next Steps (Before Checkpoint 2)
1. Complete Layer 2 normalization agents
2. Define final DNA schema (80+ columns)
3. Build proof-of-concept Layer 3 feature extractor
4. Create demo dashboard for visualization
5. Run backtesting on historical data
6. Prepare slide deck and demo video

---

## Contact & Links

**GitHub Repository**: [Insert GitHub URL]
**Documentation**: `docs/architecture/multi-agent-design.md`
**Live Demo**: [Insert demo URL if available]

**Team Contact**:
- Lê Hoàng Triệu Vỹ (Leader): [Email/LinkedIn]
- Pham Huy: [Email/LinkedIn]

---

## Submission Confirmation

✅ Project name filled in
✅ Teammates added
✅ Track selected
✅ Progress shared
✅ Image prompt created
✅ Ready for Checkpoint 1 submission

**Submitted on**: [Insert submission date]
**Status**: Ready for Review 🚀
