# Event Horizon - Configuration Guide

Centralized configuration system for managing agents and deployment settings.

---

## Overview

Event Horizon uses a YAML-based configuration system that allows you to:
- Enable/disable agents without code changes
- Configure agent parameters and behavior
- Manage environment-specific settings
- Control data sources and API integrations

---

## Quick Start

### 1. Install Dependencies

```bash
pip install pyyaml
# or
pip install -r requirements.txt
```

### 2. Configure Agents

Edit `config.yaml`:

```yaml
agents:
  news_agent:
    enabled: false

  report_agent:
    enabled: true
    config:
      include_financials: true
      earnings_periods: 4
      top_holdings: 10
```

### 3. Run

```bash
python main.py
```

Enabled agents execute automatically. No manual menu selection required.

---

## Configuration File Structure

### Basic Structure

```yaml
# config.yaml
agents:
  <agent_name>:
    enabled: true|false
    config:
      <agent_specific_parameters>

logging:
  level: "INFO|DEBUG|WARNING|ERROR"
  file: "event_horizon.log"

output:
  json_directory: "./results"
  save_format: "json"
```

### Agent Configuration

Each agent section supports:

```yaml
agents:
  news_agent:
    enabled: true
    config:
      max_articles_per_stock: 20
      days_back: 7
      language: "en"

  report_agent:
    enabled: true
    config:
      include_financials: true
      earnings_periods: 4  # Number of quarters
      top_holdings: 10     # For ETFs
```

---

## Operation Modes

### Automated Mode (with config.yaml)

```bash
python main.py
```

- Runs enabled agents automatically
- No user interaction required
- Ideal for: Docker, cron jobs, CI/CD

### Interactive Mode (without config.yaml)

```bash
# Rename or remove config.yaml
python main.py
```

- Shows menu for manual agent selection
- Ideal for: Testing, exploration

---

## Environment Variables

API keys and secrets should be in `.env`:

```bash
NEWS_API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

Referenced in config:

```yaml
agents:
  news_agent:
    config:
      api_key: ${NEWS_API_KEY}
```

---

## Multiple Configuration Files

Use different configs for different environments:

```bash
# Development
cp config.yaml config.dev.yaml

# Production
cp config.yaml config.prod.yaml

# Staging
cp config.yaml config.staging.yaml
```

Specify config file:

```bash
python main.py --config config.prod.yaml
```

**Note**: Command-line config selection requires update to main.py

---

## Data Sources

### Report Agent Data Sources

**Current: yfinance (Yahoo Finance)**
- Free, no API key required
- Provides parsed financial data
- Fast access to earnings, metrics, fund info

**Alternative: SEC EDGAR**
- Official regulatory filings (PDF/HTML)
- Complete holdings data
- Free, no API key
- Requires parsing and storage

| Feature | yfinance | SEC EDGAR |
|---------|----------|-----------|
| Format | JSON (parsed) | PDF/HTML (raw) |
| Speed | Fast | Slower |
| Completeness | Summary | Complete |
| API Key | Not required | Not required |
| Use Case | Quick analysis | Official records |

For SEC EDGAR integration, see `docs/data-sources-explained.md`

---

## Agent Status Display

When running with config, you'll see:

```
======================================================================
 AGENT CONFIGURATION STATUS
======================================================================
news_agent          : ❌ DISABLED
report_agent        : ✅ ENABLED

Enabled Agents: report_agent
======================================================================

🤖 EXECUTING REPORT AGENT
...
```

---

## File Structure

```
Event-Horizon/
├── config.yaml              # Main configuration
├── config.dev.yaml          # Development config
├── config.prod.yaml         # Production config
├── main.py                  # Config-driven entry point
├── utils/
│   └── config_loader.py     # Configuration loader
└── docs/
    ├── configuration-guide.md
    └── data-sources-explained.md
```

---

## Common Patterns

### Disable News Agent, Enable Report Agent

```yaml
agents:
  news_agent:
    enabled: false
  report_agent:
    enabled: true
```

### Enable All Agents

```yaml
agents:
  news_agent:
    enabled: true
  report_agent:
    enabled: true
```

### Production Settings

```yaml
agents:
  news_agent:
    enabled: false
  report_agent:
    enabled: true
    config:
      include_financials: true
      earnings_periods: 8

logging:
  level: "INFO"

output:
  json_directory: "/app/data/results"
```

---

## FAQ

**Q: Do I need config.yaml?**
A: No. main.py works with or without it. Without config.yaml, it runs in interactive mode.

**Q: Can I have multiple configs?**
A: Yes. Create config.dev.yaml, config.prod.yaml, etc. Pass via --config flag.

**Q: What if both agents are enabled?**
A: Both run sequentially, producing separate JSON output files.

**Q: Do I need NEWS_API_KEY if news agent is disabled?**
A: No. Disabled agents don't require their dependencies.

**Q: Can Report Agent work without API keys?**
A: Yes. It uses yfinance which is free and keyless.

---

## Next Steps

- See `docs/configuration-guide.md` for detailed configuration options
- See `docs/data-sources-explained.md` for data source comparison
- See `DEPLOYMENT.md` for production deployment guides

---

## Summary

**Configuration System Features:**
- ✅ YAML-based configuration
- ✅ Easy agent enable/disable
- ✅ Environment variable support
- ✅ Multiple config file support
- ✅ No code changes for deployment
- ✅ Interactive fallback mode

**Usage:**
1. Edit `config.yaml`
2. Run `python main.py`
3. Check results in `./results/`
