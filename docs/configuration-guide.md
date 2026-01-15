# Event Horizon - Configuration Guide

## Easy Agent Activation/Deactivation

Event Horizon uses `config.yaml` to control which agents run during deployment. This makes it easy to enable/disable agents without changing code.

---

## Quick Start

### 1. View Current Configuration

```bash
cat config.yaml
```

### 2. Enable/Disable Agents

Edit `config.yaml`:

```yaml
agents:
  news_agent:
    enabled: false  # ← Set to true to enable

  report_agent:
    enabled: true   # ← Set to false to disable
```

### 3. Run the System

```bash
python main.py
```

The system will automatically run only the enabled agents!

---

## Configuration File Structure

### config.yaml

```yaml
# ==========================================
# AGENT CONFIGURATION
# ==========================================
agents:

  # News Agent - Retrieves financial news
  news_agent:
    enabled: false              # true = run, false = skip
    config:
      max_articles_per_stock: 5
      days_back: 7
      language: "en"

  # Report Agent - Earnings and fund reports
  report_agent:
    enabled: true               # true = run, false = skip
    config:
      include_financials: true
      earnings_periods: 4
      top_holdings: 10
      download_sec_filings: false  # Future feature

# ==========================================
# DATA SOURCES
# ==========================================
data_sources:

  yfinance:
    enabled: true
    description: "Yahoo Finance data (free, parsed)"

  sec_edgar:
    enabled: false
    description: "SEC official filings (future feature)"

# ==========================================
# API KEYS
# ==========================================
api_keys:
  news_api_key: ${NEWS_API_KEY}  # Reads from .env file

# ==========================================
# OUTPUT SETTINGS
# ==========================================
output:
  save_json: true
  json_directory: "."
  pretty_print: true

# ==========================================
# LOGGING
# ==========================================
logging:
  level: "INFO"      # DEBUG, INFO, WARNING, ERROR
  save_to_file: true
```

---

## Common Deployment Scenarios

### Scenario 1: Only Report Agent (Current Request)

**Use Case**: You only want earnings/fund reports, no news articles.

**Configuration**:
```yaml
agents:
  news_agent:
    enabled: false  # ← Disabled

  report_agent:
    enabled: true   # ← Enabled
```

**Command**:
```bash
python main.py
```

**Output**:
```
======================================================================
 AGENT CONFIGURATION STATUS
======================================================================
news_agent          : ❌ DISABLED
report_agent        : ✅ ENABLED

Enabled Agents: report_agent
======================================================================

🤖 EXECUTING REPORT AGENT
📊 Report results: report_results.json
```

---

### Scenario 2: Only News Agent

**Use Case**: You only want news articles, no earnings reports.

**Configuration**:
```yaml
agents:
  news_agent:
    enabled: true   # ← Enabled

  report_agent:
    enabled: false  # ← Disabled
```

---

### Scenario 3: Both Agents

**Use Case**: Full analysis with both news and reports.

**Configuration**:
```yaml
agents:
  news_agent:
    enabled: true   # ← Enabled

  report_agent:
    enabled: true   # ← Enabled
```

---

### Scenario 4: Development Mode (All Disabled)

**Use Case**: Testing configuration, no agent execution.

**Configuration**:
```yaml
agents:
  news_agent:
    enabled: false

  report_agent:
    enabled: false
```

**Output**:
```
❌ No agents enabled in config.yaml
```

---

## Environment-Specific Configurations

### Development Environment

**config.dev.yaml**:
```yaml
agents:
  news_agent:
    enabled: true
    config:
      max_articles_per_stock: 3  # Fewer articles for testing
      days_back: 3

  report_agent:
    enabled: true
    config:
      earnings_periods: 2  # Less data for faster testing

logging:
  level: "DEBUG"  # Verbose logging
```

**Run with**:
```bash
python main.py --config config.dev.yaml
```

### Production Environment

**config.prod.yaml**:
```yaml
agents:
  news_agent:
    enabled: false  # Disabled in production

  report_agent:
    enabled: true   # Only report agent in production
    config:
      earnings_periods: 8  # More historical data

logging:
  level: "INFO"  # Less verbose
  save_to_file: true

output:
  json_directory: "/var/app/data/results"  # Production path
```

---

## Configuration Priority

The system loads configuration in this order:

1. **config.yaml** - Main configuration file
2. **Environment Variables** - Override values (e.g., `${NEWS_API_KEY}`)
3. **.env file** - API keys and secrets

Example:
```yaml
api_keys:
  news_api_key: ${NEWS_API_KEY}  # Reads from environment/env file
```

---

## API Key Management

### Option 1: .env File (Recommended)

**.env**:
```bash
NEWS_API_KEY=your_key_here
```

**config.yaml**:
```yaml
api_keys:
  news_api_key: ${NEWS_API_KEY}
```

### Option 2: Environment Variable

```bash
export NEWS_API_KEY=your_key_here
python main.py
```

### Option 3: Direct in config.yaml (Not Recommended)

```yaml
api_keys:
  news_api_key: "abc123xyz"  # Don't commit this to git!
```

---

## Changing Agent Configuration

### Adjust Agent Behavior

You can change how agents work without modifying code:

```yaml
agents:
  news_agent:
    enabled: true
    config:
      max_articles_per_stock: 20  # ← Increase from 5 to 20
      days_back: 30               # ← Look back 30 days instead of 7
      language: "en"

  report_agent:
    enabled: true
    config:
      include_financials: false   # ← Skip detailed financials
      earnings_periods: 8         # ← Get 8 quarters instead of 4
      top_holdings: 20            # ← Show top 20 holdings
```

---

## Programmatic Access

### Using ConfigLoader in Your Code

```python
from utils.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader("config.yaml")

# Check if agent is enabled
if config.is_agent_enabled('report_agent'):
    # Get agent configuration
    agent_config = config.get_agent_config('report_agent')

    # Run agent
    from agents.report_agent import ReportAnalysisAgent
    agent = ReportAnalysisAgent(config=agent_config)
    result = agent.execute(portfolio)
```

### ConfigLoader Methods

```python
# Agent status
config.is_agent_enabled('news_agent')  # Returns bool
config.get_enabled_agents()             # Returns list
config.get_agent_config('news_agent')  # Returns dict

# Data sources
config.is_data_source_enabled('yfinance')  # Returns bool
config.get_data_source_config('yfinance')  # Returns dict

# API keys
config.get_api_key('news_api_key')  # Returns string

# Other config
config.get_logging_config()  # Returns dict
config.get_output_config()   # Returns dict
config.get_full_config()     # Returns complete config dict

# Display status
config.print_agent_status()  # Prints formatted status
```

---

## Migration from Old main.py

### Old Approach (main.py)

```python
# Hard-coded menu
print("1. News Agent only")
print("2. Report Agent only")
print("3. Both agents")
choice = input("Enter choice: ")

if choice == "1":
    run_news_agent()
elif choice == "2":
    run_report_agent()
else:
    run_both_agents()
```

**Problems:**
- Need to change code to change behavior
- Manual selection required
- Difficult to automate deployments

### New Approach (main.py)

```python
# Configuration-driven
config = ConfigLoader("config.yaml")

if config.is_agent_enabled('news_agent'):
    run_news_agent()

if config.is_agent_enabled('report_agent'):
    run_report_agent()
```

**Benefits:**
- ✅ No code changes needed
- ✅ No manual input required
- ✅ Easy to automate
- ✅ Environment-specific configs
- ✅ Version control friendly

---

## Best Practices

### 1. Use Environment-Specific Configs

```
config.yaml          # Default/base config
config.dev.yaml      # Development overrides
config.prod.yaml     # Production overrides
config.test.yaml     # Testing overrides
```

### 2. Never Commit API Keys

```yaml
# ❌ Bad
api_keys:
  news_api_key: "abc123xyz"

# ✅ Good
api_keys:
  news_api_key: ${NEWS_API_KEY}
```

### 3. Document Configuration Changes

Add comments in config.yaml:
```yaml
agents:
  report_agent:
    enabled: true
    config:
      earnings_periods: 8  # Increased from 4 for better historical analysis
```

### 4. Version Control

**.gitignore**:
```
.env
config.local.yaml
*_results.json
```

**Commit**:
```
config.yaml           # ✅ Commit
config.example.yaml   # ✅ Commit
config.prod.yaml      # ✅ Commit (without secrets)
.env                  # ❌ Don't commit
```

---

## Troubleshooting

### Error: "Configuration file not found"

**Problem**: config.yaml doesn't exist

**Solution**:
```bash
# Check if file exists
ls config.yaml

# Create if missing
cp config.example.yaml config.yaml
```

### Error: "No agents enabled"

**Problem**: All agents are disabled

**Solution**: Edit config.yaml and set at least one agent to `enabled: true`

### Error: "yaml.parser.ParserError"

**Problem**: Invalid YAML syntax

**Solution**: Check indentation (use spaces, not tabs)

```yaml
# ❌ Wrong (mixed indentation)
agents:
	news_agent:
        enabled: true

# ✅ Correct (consistent spaces)
agents:
  news_agent:
    enabled: true
```

### Error: "NEWS_API_KEY not found"

**Problem**: News Agent enabled but no API key

**Solutions**:
1. Disable News Agent: `enabled: false`
2. Add API key to .env file
3. Set environment variable

---

## Deployment Checklist

### Pre-Deployment

- [ ] Set correct agents to `enabled: true/false`
- [ ] Configure agent parameters for production
- [ ] Set logging level appropriately
- [ ] Configure output directory
- [ ] Verify API keys in environment
- [ ] Test with sample portfolio
- [ ] Check disk space for JSON output

### Production Deployment

```bash
# 1. Copy production config
cp config.prod.yaml config.yaml

# 2. Set environment variables
export NEWS_API_KEY=your_production_key

# 3. Run system
python main.py

# 4. Verify output
ls -la *_results.json
```

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Use environment-specific config
COPY config.prod.yaml config.yaml

CMD ["python", "main.py"]
```

**docker-compose.yml**:
```yaml
version: '3'
services:
  event-horizon:
    build: .
    environment:
      - NEWS_API_KEY=${NEWS_API_KEY}
    volumes:
      - ./config.prod.yaml:/app/config.yaml
      - ./results:/app/results
```

---

## Summary

### To Activate/Deactivate Agents:

1. Edit `config.yaml`
2. Set `enabled: true` or `enabled: false`
3. Run `python main.py`

**That's it!** No code changes needed.

### Current Setup (Per Your Request):

```yaml
agents:
  news_agent:
    enabled: false  # ✅ Deactivated

  report_agent:
    enabled: true   # ✅ Activated
```

Run:
```bash
python main.py
```

You'll get only the Report Agent output with earnings and fund data!
