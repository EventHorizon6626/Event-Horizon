# Event Horizon - Usage Guide

## Simple: Just One main.py

There is **only one** `main.py` file. It works in two modes automatically.

---

## Mode 1: With config.yaml (Automated)

**Best for**: Deployment, automation, Docker, cron jobs

### Setup:
```bash
# 1. Edit config.yaml
vim config.yaml
```

```yaml
agents:
  news_agent:
    enabled: false  # ← Turn off

  report_agent:
    enabled: true   # ← Turn on
```

### Run:
```bash
python main.py
```

### Output:
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
✅ Agents executed successfully!
📊 report_results.json
```

**No interaction needed!** Perfect for automation.

---

## Mode 2: Without config.yaml (Interactive)

**Best for**: Testing, exploration, manual runs

### Run:
```bash
# If config.yaml doesn't exist, you get a menu
python main.py
```

### Output:
```
======================================================================
 EVENT HORIZON - MULTI-AGENT SYSTEM
======================================================================
⚠️  config.yaml not found. Running in interactive mode.

💡 Tip: Create config.yaml for automated deployment

Select agents to execute:
  1. News Agent only
  2. Report Agent only
  3. Both agents
======================================================================

Enter choice (1-3) [default: 3]:
```

You choose which agents to run **interactively**.

---

## Quick Commands

### Current Setup (Your Request)

```bash
# Install dependencies
pip install -r requirements.txt

# Run (with config.yaml already set to Report Agent only)
python main.py
```

That's it! You get `report_results.json` with earnings and fund data.

---

## Switching Between Modes

### To use Automated Mode:
```bash
# Make sure config.yaml exists
ls config.yaml

# Run
python main.py
```

### To use Interactive Mode:
```bash
# Temporarily rename config.yaml
mv config.yaml config.yaml.backup

# Run (will show menu)
python main.py

# Restore config
mv config.yaml.backup config.yaml
```

---

## What Changed?

### Before (Confusing):
- ❌ `main.py` - Old version with manual menu
- ❌ `main_v2.py` - New version with config
- ❌ User confused: "Which one do I use?"

### Now (Simple):
- ✅ `main.py` - **ONE FILE**, works both ways
  - Has config.yaml → Automated mode
  - No config.yaml → Interactive mode

---

## File Structure

```
Event-Horizon/
├── main.py              # ← Just run this
├── config.yaml          # ← Optional: For automated mode
├── .env                 # ← Optional: API keys
│
├── agents/              # Agent implementations
│   ├── news_agent.py
│   └── report_agent.py
│
├── services/            # Data clients
│   ├── news_api_client.py
│   └── financial_data_client.py
│
└── utils/               # Configuration loader
    └── config_loader.py
```

---

## Configuration Reference

### Enable/Disable Agents

Edit `config.yaml`:

```yaml
agents:
  news_agent:
    enabled: false  # false = OFF, true = ON

  report_agent:
    enabled: true   # false = OFF, true = ON
```

### Configure Agent Behavior

```yaml
agents:
  news_agent:
    enabled: true
    config:
      max_articles_per_stock: 5   # How many articles
      days_back: 7                # How far back
      language: "en"              # Language

  report_agent:
    enabled: true
    config:
      include_financials: true    # Include financial statements
      earnings_periods: 4         # Quarters to retrieve
      top_holdings: 10           # Holdings to show
```

---

## Examples

### Example 1: Only Report Agent (Your Request)

**config.yaml**:
```yaml
agents:
  news_agent:
    enabled: false

  report_agent:
    enabled: true
```

**Command**:
```bash
python main.py
```

**Result**: Only `report_results.json` is created

---

### Example 2: Only News Agent

**config.yaml**:
```yaml
agents:
  news_agent:
    enabled: true

  report_agent:
    enabled: false
```

**Command**:
```bash
python main.py
```

**Result**: Only `news_results.json` is created (requires NEWS_API_KEY)

---

### Example 3: Both Agents

**config.yaml**:
```yaml
agents:
  news_agent:
    enabled: true

  report_agent:
    enabled: true
```

**Command**:
```bash
python main.py
```

**Result**: Both `news_results.json` and `report_results.json` are created

---

### Example 4: Interactive Testing

**Command**:
```bash
# Remove config.yaml temporarily
mv config.yaml config.yaml.backup

# Run interactively
python main.py

# You'll get a menu to choose agents
```

---

## Deployment

### Local Development

```bash
# Edit config for what you need
vim config.yaml

# Run
python main.py
```

### Docker

```dockerfile
FROM python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Copy your production config
COPY config.prod.yaml config.yaml

CMD ["python", "main.py"]
```

### Kubernetes / Cloud

```bash
# Build image with config
docker build -t event-horizon:v1 .

# Deploy (no interaction needed, uses config.yaml)
kubectl apply -f deployment.yaml
```

### Cron Job

```bash
# Daily at 9 AM
0 9 * * * cd /app/event-horizon && python main.py >> logs/daily.log 2>&1
```

---

## Troubleshooting

### "config.yaml not found" but I want automated mode

**Solution**: Create config.yaml
```bash
cp config.yaml.example config.yaml
vim config.yaml
```

### Interactive menu appears but I don't want it

**Solution**: Make sure config.yaml exists
```bash
ls config.yaml  # Should show the file
```

### Agent not running

**Solution**: Check config.yaml
```bash
cat config.yaml

# Make sure agent is enabled:
#   enabled: true  ← Not false
```

### "pyyaml not installed"

**Solution**: Install dependencies
```bash
pip install pyyaml
# or
pip install -r requirements.txt
```

---

## Summary

**One file**: `main.py`

**Two modes**:
1. **With config.yaml**: Automated (for deployment)
2. **Without config.yaml**: Interactive (for testing)

**Current setup** (as you requested):
- News Agent: **OFF**
- Report Agent: **ON**

**Run**:
```bash
python main.py
```

**Done!** 🎉
