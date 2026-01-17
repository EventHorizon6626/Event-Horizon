# Massive.com API Setup Guide

Setup Massive.com as your candlestick chart data provider.

---

## What is Massive.com?

Massive.com provides professional-grade market data API:
- ✅ Real-time & historical OHLCV data
- ✅ Stocks, options, forex, crypto
- ✅ High rate limits
- ✅ Better reliability than free sources
- ✅ Multiple subscription tiers

**Website:** https://massive.com
**Documentation:** https://massive.com/docs

---

## Step 1: Get API Key

1. Go to https://massive.com
2. **Sign up** for an account
3. Go to **Dashboard**: https://massive.com/dashboard
4. Find your **API Key**
5. Copy it

---

## Step 2: Configure Environment

On your VPS:

```bash
cd ~/EventHorizon/Event-Horizon-AI
nano .env
```

Add these lines:

```bash
# Massive.com API Configuration
MASSIVE_API_KEY=your_actual_api_key_here
USE_MASSIVE_API=true

# Keep chart agent enabled
ENABLE_CHART_AGENT=true
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 3: Rebuild and Deploy

```bash
# Rebuild Docker container
docker-compose down
docker-compose up -d --build

# Check logs
docker logs -f event-horizon-ai
```

You should see:
```
INFO - Using Massive.com API for chart data
```

---

## Step 4: Test

```bash
curl -X POST http://localhost:5000/api/chart \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"]}'
```

Expected response:
```json
{
  "status": "success",
  "chart_data": {
    "AAPL": {
      "symbol": "AAPL",
      "source": "massive.com",
      "candles": [
        {
          "date": "2024-12-17T00:00:00",
          "timestamp": 1702771200000,
          "open": 195.50,
          "high": 197.30,
          "low": 194.80,
          "close": 196.45,
          "volume": 52000000,
          "vwap": 196.10,
          "transactions": 125000
        }
      ],
      "total_candles": 30
    }
  }
}
```

---

## API Endpoint Format

Massive.com uses Polygon.io-style endpoints:

```
GET /v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from}/{to}
```

**Parameters:**
- `symbol`: Stock ticker (e.g., AAPL)
- `multiplier`: Number of units (e.g., 1, 5, 15)
- `timespan`: minute, hour, day, week, month
- `from`: Start date (YYYY-MM-DD)
- `to`: End date (YYYY-MM-DD)

**Example:**
```
/v2/aggs/ticker/AAPL/range/1/day/2024-11-01/2024-12-01
```

---

## Supported Timeframes

### Intervals
- `1m` - 1 minute (intraday only)
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `4h` - 4 hours
- `1d` - 1 day (default)
- `1wk` - 1 week
- `1mo` - 1 month

### Periods
- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month (default)
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year
- `2y` - 2 years
- `5y` - 5 years
- `max` - Maximum history (~20 years)

---

## Rate Limits

Depends on your Massive.com subscription plan:

| Plan | Rate Limit | Historical Data |
|------|-----------|----------------|
| Basic | Limited | 2 years |
| Advanced | Higher | All history |
| Business | Highest | All history + real-time |

Check your plan at: https://massive.com/pricing

---

## Switching Between Yahoo Finance and Massive.com

### Use Yahoo Finance (Free)
```bash
USE_MASSIVE_API=false
```

### Use Massive.com (Paid)
```bash
USE_MASSIVE_API=true
MASSIVE_API_KEY=your_key_here
```

The system automatically uses the configured source!

---

## Advantages of Massive.com

**vs Yahoo Finance:**
- ✅ Higher rate limits
- ✅ More reliable (no 429 errors)
- ✅ Real-time data (with premium plan)
- ✅ Better historical coverage
- ✅ More granular intervals (1m, 5m)
- ✅ Additional data (VWAP, transaction count)
- ✅ Professional support

**Costs:**
- Basic: ~$25-50/month
- Advanced: ~$100-200/month
- Business: Custom pricing

---

## Troubleshooting

### Error: "Invalid Massive.com API key"

```bash
# Check your API key
echo $MASSIVE_API_KEY

# Make sure it's in .env
cat .env | grep MASSIVE_API_KEY

# Restart container
docker-compose restart
```

### Error: "Rate limit exceeded"

Your plan's rate limit is reached. Options:
1. Wait for limit to reset
2. Upgrade to higher tier plan
3. Switch to Yahoo Finance temporarily

### No data returned

```bash
# Check logs
docker logs event-horizon-ai

# Test connection
docker exec event-horizon-ai python -c "
from services.massive_chart_client import MassiveChartClient
client = MassiveChartClient()
print(client.test_connection())
"
```

---

## Example Use Cases

### Intraday Trading (1-minute candles)
```bash
curl -X POST http://localhost:5000/api/chart \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL"], "period": "1d", "interval": "1m"}'
```

### Long-term Analysis (weekly candles)
```bash
curl -X POST http://localhost:5000/api/chart \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["GOOGL"], "period": "5y", "interval": "1wk"}'
```

### Multiple Stocks
```bash
curl -X POST http://localhost:5000/api/chart \
  -H "Content-Type: application/json" \
  -d '{"stocks": ["AAPL", "GOOGL", "MSFT"], "period": "1mo", "interval": "1d"}'
```

---

## Summary

1. **Sign up** at https://massive.com
2. **Get API key** from dashboard
3. **Configure** `.env` with `MASSIVE_API_KEY` and `USE_MASSIVE_API=true`
4. **Rebuild** Docker container
5. **Test** with `/api/chart` endpoint

**That's it!** You now have professional-grade candlestick data! 📊

---

**Need help?** Check Massive.com documentation: https://massive.com/docs
