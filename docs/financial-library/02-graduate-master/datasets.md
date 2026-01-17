# Graduate / Master Level - Datasets & Data Sources

Premium data sources, high-frequency data, and alternative datasets for advanced research.

---

## 🏆 Academic Research Databases

### 1. **WRDS (Wharton Research Data Services)** ⭐ GOLD STANDARD
- **Access**: University subscription required
- **Datasets**: CRSP, Compustat, IBES, OptionMetrics, TAQ, more
- **Cost**: University subscription (~$50k/year for institution)
- **Link**: https://wrds-www.wharton.upenn.edu/
- **Why Use**: Comprehensive, clean, standardized data
- **Student Access**: FREE if your school subscribes

**Key Datasets on WRDS**:
- **CRSP**: Historical stock prices, returns, market cap (1926-present)
- **Compustat**: Financial statements, fundamentals
- **IBES**: Analyst estimates and actuals
- **OptionMetrics**: Options prices, implied volatility surfaces
- **TAQ (Tick Data)**: Intraday trades and quotes
- **Eventus**: Event study tool

---

## 📊 Premium Market Data

### 2. **Bloomberg Terminal**
- **Access**: $24,000/year per user
- **Data**: Everything - prices, fundamentals, news, analytics
- **Why Use**: Industry standard, most comprehensive
- **Student Access**: FREE terminal access at most business schools

### 3. **Refinitiv Eikon / Workspace**
- **Access**: ~$20,000-$30,000/year
- **Data**: Similar to Bloomberg
- **Why Use**: Alternative to Bloomberg, strong in fixed income

### 4. **FactSet**
- **Access**: ~$15,000-$25,000/year
- **Data**: Fundamentals, ownership, estimates
- **Why Use**: Strong in equity research, easy to use

---

## ⚡ High-Frequency & Tick Data

### 5. **IQFeed (DTN)**
- **Access**: API subscription
- **Data**: Real-time and historical tick data
- **Cost**: $80-$400/month
- **Link**: http://www.iqfeed.net/
- **Why Use**: Affordable tick data for retail

### 6. **Polygon.io**
- **Access**: API
- **Data**: Stocks, options, crypto, forex tick data
- **Cost**: FREE (limited) to $200/month
- **Link**: https://polygon.io
- **Why Use**: Modern API, good for algo trading

### 7. **Tick Data LLC**
- **Access**: Purchase historical tick data
- **Data**: Futures, equities, forex
- **Cost**: $500-$5,000+ per dataset
- **Link**: https://www.tickdata.com
- **Why Use**: Clean historical tick data

---

## 🔬 Alternative Data Sources

### 8. **Quiver Quantitative**
- **Access**: API, web platform
- **Data**: Congressional trading, insider trades, Reddit sentiment
- **Cost**: $20-$100/month
- **Link**: https://www.quiverquant.com
- **Why Use**: Alternative data for retail traders

### 9. **Sentiment Analysis Data**
- **RavenPack**: News analytics, sentiment ($$$)
- **PsychSignal**: Social media sentiment
- **StockTwits API**: Social sentiment (free/paid)

### 10. **Satellite Data**
- **Orbital Insight**: Retail foot traffic from satellites
- **Descartes Labs**: Agricultural/commodity data
- **RS Metrics**: Alternative economic indicators
- **Note**: Very expensive ($50k-$500k/year)

---

## 📈 Options & Derivatives Data

### 11. **CBOE Data Shop**
- **Access**: Website, API
- **Data**: VIX, options volume, skew data
- **Cost**: FREE to moderate
- **Link**: https://www.cboe.com/data/
- **Why Use**: Official exchange data

### 12. **Historical Options Data**
- **ORATS**: Options data ($50-$500/month)
- **DiscountOptionData**: Cheap historical options (~$50-$300)
- **iVolatility**: IV surfaces, Greeks

---

## 🌍 International & Global Data

### 13. **World Bank Open Data**
- **Access**: FREE API
- **Data**: Global economic indicators, poverty, development
- **Link**: https://data.worldbank.org

### 14. **IMF Data**
- **Access**: FREE
- **Data**: International financial statistics, balance of payments
- **Link**: https://data.imf.org

### 15. **BIS (Bank for International Settlements)**
- **Access**: FREE
- **Data**: Central bank data, credit, derivatives
- **Link**: https://www.bis.org/statistics/

---

## 🤖 Machine Learning Datasets

### 16. **Numerai**
- **Type**: Encrypted trading data + competition
- **Cost**: FREE
- **Link**: https://numer.ai
- **Why Use**: Train ML models, win crypto prizes

### 17. **QuantConnect Datasets**
- **Access**: QuantConnect platform
- **Data**: Equities, options, futures, alt data
- **Cost**: FREE (basic) to $500+/month
- **Link**: https://www.quantconnect.com/datasets

---

## 📚 Recommended Data Stack for Projects

### Project 1: Factor Investing Research
**Data**:
- WRDS CRSP (prices)
- WRDS Compustat (fundamentals)
- Kenneth French Library (factors)
**Cost**: FREE (university access)

### Project 2: Options Pricing Model
**Data**:
- WRDS OptionMetrics (options)
- Yahoo Finance (underlying prices)
- FRED (risk-free rate)
**Cost**: FREE (university access)

### Project 3: High-Frequency Trading Strategy
**Data**:
- Polygon.io (tick data)
- IQFeed (real-time)
**Cost**: $100-$300/month

### Project 4: Alternative Data Strategy
**Data**:
- Quiver Quant (alt data)
- Reddit API (sentiment)
- Yahoo Finance (prices)
**Cost**: $20-$50/month

---

## 💻 Data Access Code Examples

### WRDS via Python:
```python
import wrds

# Connect (requires WRDS account)
db = wrds.Connection()

# Query CRSP
crsp = db.raw_sql("""
    SELECT date, permno, ret
    FROM crsp.dsf
    WHERE date BETWEEN '2020-01-01' AND '2023-12-31'
""")

# Query Compustat
comp = db.raw_sql("""
    SELECT datadate, gvkey, at, lt, sale
    FROM comp.funda
    WHERE fyear >= 2020
""")
```

### Polygon.io:
```python
from polygon import RESTClient

client = RESTClient(api_key='YOUR_KEY')

# Get trades
trades = client.get_trades('AAPL', '2023-01-01')
for trade in trades:
    print(f"{trade.timestamp}: ${trade.price} x {trade.size}")
```

---

## 🔐 Data Access Strategies

**If you're a student**:
- Use WRDS through university (FREE, best data)
- Bloomberg terminal on campus
- Compustat via university library

**If you're a professional without Bloomberg**:
- Polygon.io for tick data
- Financial Modeling Prep for fundamentals
- FRED for macro data
- Quiver Quant for alt data

**If you have a budget ($500-1k/month)**:
- QuantConnect full data library
- Polygon.io premium
- ORATS options data
- One alternative data provider

---

**Next Level**: [Doctoral Datasets](../03-doctoral-phd/datasets.md)
