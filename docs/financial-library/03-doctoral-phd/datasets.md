# Doctoral / PhD Level - Research Datasets

Academic-grade datasets for rigorous empirical research and publications.

---

## 🏆 Gold Standard Academic Datasets

### 1. **CRSP (Center for Research in Security Prices)** ⭐
- **Access**: WRDS subscription (via university)
- **Coverage**: U.S. stocks 1926-present, full corporate action history
- **Data**: Daily/monthly returns, prices, volumes, delistings, dividends
- **Why Use**: Most cited dataset in finance research
- **Clean Data**: Survivor-bias free, point-in-time
- **Link**: Via WRDS

### 2. **Compustat**
- **Access**: WRDS
- **Coverage**: Fundamentals for 20,000+ U.S. companies, 1950-present
- **Data**: Income statement, balance sheet, cash flow
- **Why Use**: Standard for accounting/fundamentals research
- **Link**: Via WRDS

### 3. **IBES (I/B/E/S)**
- **Access**: WRDS
- **Coverage**: Analyst estimates and actuals, 1976-present
- **Data**: EPS forecasts, recommendations, target prices
- **Why Use**: Research on analyst behavior, expectations
- **Link**: Via WRDS

---

## ⚡ High-Quality Microstructure Data

### 4. **TAQ (Trade and Quote)**
- **Access**: WRDS (expensive, storage-intensive)
- **Coverage**: Intraday trades and quotes for all U.S. exchanges
- **Frequency**: Millisecond-level data
- **Size**: Terabytes per year
- **Why Use**: Market microstructure research
- **Note**: Requires significant computing resources

### 5. **OptionMetrics (IvyDB)**
- **Access**: WRDS
- **Coverage**: Options prices, implied volatility surfaces
- **Data**: Daily prices, greeks, IV, volume for all optionable stocks
- **Why Use**: Standard for options research
- **Link**: Via WRDS

### 6. **TRACE (Bond Transactions)**
- **Access**: WRDS
- **Coverage**: Corporate bond transactions, 2002-present
- **Why Use**: Fixed income microstructure
- **Link**: Via WRDS

---

## 🌍 International Data

### 7. **Datastream (Refinitiv)**
- **Access**: University subscription
- **Coverage**: Global stocks, bonds, currencies, commodities
- **Why Use**: International research, non-U.S. markets
- **Alternative**: Bloomberg

### 8. **Worldscope**
- **Access**: Via Refinitiv
- **Coverage**: Global fundamentals
- **Why Use**: International corporate finance

---

## 📊 Constructed Research Datasets

### 9. **Kenneth French Data Library** (FREE)
- **Data**: Factor returns, portfolio sorts, industry returns
- **Coverage**: 1926-present, updated monthly
- **Formats**: CSV, TXT
- **Link**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- **Why Use**: Standard factors for asset pricing research
- **Datasets**:
  - Fama-French 3/5 factors
  - Momentum factor
  - Industry portfolios
  - International factors

### 10. **AQR Capital Datasets** (FREE)
- **Data**: Factor returns, alternative risk premia
- **Coverage**: Global, 1985-present
- **Link**: https://www.aqr.com/Insights/Datasets
- **Datasets**:
  - Quality Minus Junk (QMJ)
  - Betting Against Beta (BAB)
  - Time-series momentum
  - Carry factors

### 11. **Nobel Prize Datasets**
- **Link**: Winners often post data from prize-winning papers
- **Examples**:
  - Shiller CAPE data
  - Campbell predictability data
  - Fama-French factor data

---

## 🗞️ Textual & Alternative Data

### 12. **EDGAR Full-Text Search**
- **Access**: SEC website, parsers available
- **Cost**: FREE
- **Data**: Full text of 10-K, 10-Q, 8-K filings
- **Why Use**: Textual analysis research
- **Tools**: Python libraries (sec-api, edgar)

### 13. **RavenPack News Analytics**
- **Access**: Commercial ($50k+/year)
- **Data**: Sentiment scores from news articles
- **Coverage**: Real-time and historical
- **Why Use**: Alternative data research
- **Academic Access**: Sometimes available via university

### 14. **GDELT (Global Database of Events, Language, and Tone)**
- **Access**: FREE
- **Data**: News events, sentiment, geopolitical data
- **Coverage**: 1979-present, real-time updates
- **Link**: https://www.gdeltproject.org
- **Why Use**: Large-scale textual analysis

---

## 📈 Proprietary & Specialty Data

### 15. **Markit Securities Lending**
- **Access**: IHS Markit (via WRDS for some schools)
- **Data**: Short interest, stock lending fees
- **Why Use**: Short-selling research

### 16. **13F Filings (Institutional Holdings)**
- **Access**: Thomson Reuters, WRDS
- **Data**: Quarterly institutional holdings (>$100M managers)
- **Why Use**: Fund flows, institutional behavior

### 17. **Form 4 (Insider Trading)**
- **Access**: SEC EDGAR, commercial vendors
- **Data**: Insider purchases/sales
- **Why Use**: Insider trading research

---

## 🔬 Constructed Datasets for Specific Research

### 18. **Hand-Collected Datasets**
- **When**: For novel research questions
- **Examples**:
  - IPO prospectuses (textual analysis)
  - Conference call transcripts
  - Proprietary survey data
- **Tools**: OCR, web scraping, manual coding
- **Note**: Time-intensive but highly valuable

### 19. **Merged CRSP-Compustat**
- **Access**: WRDS (CCM link available)
- **Why Use**: Combine prices with fundamentals
- **Note**: Be careful with linking (use PERMNO-GVKEY correctly)

---

## 💻 Data Processing Best Practices for Research

### Key Principles:
1. **Survivor-Bias Free**: Use all stocks, including delistings
2. **Point-in-Time**: Use data available at analyzer time (avoid look-ahead bias)
3. **Winsorize**: Handle outliers (typically 1% / 99%)
4. **Document**: Keep detailed notes on data filters
5. **Reproducible**: Save code, random seeds
6. **Validate**: Cross-check with published papers

### Standard Filters (Fama-French Style):
```
- Exclude financials (SIC 6000-6999)
- Exclude utilities (SIC 4900-4999)
- Require positive book equity
- Require NYSE/AMEX/NASDAQ listing
- Apply price filters (> $5)
- Require 12+ months of data
```

---

## 📊 Sample Research Projects

### Project 1: Replicate Fama-French (1993)
- **Data**: CRSP + Compustat
- **Time**: 2-3 months
- **Output**: Factor returns, portfolio sorts
- **Why**: Learn empirical asset pricing methods

### Project 2: Textual Analysis of 10-Ks
- **Data**: EDGAR filings
- **Tools**: Python (NLP libraries)
- **Time**: 3-6 months
- **Output**: Sentiment measures, tone variables

### Project 3: Options Market Anomaly
- **Data**: OptionMetrics + CRSP
- **Time**: 4-6 months
- **Output**: Trading strategy, risk-adjusted returns

---

## 🔐 Data Access for PhD Students

### Free/University Access:
- ✅ WRDS (most top schools)
- ✅ Bloomberg Terminal (on campus)
- ✅ Kenneth French Library
- ✅ AQR Datasets
- ✅ FRED, SEC EDGAR

### Paid (If University Doesn't Have):
- Negotiate with data vendor for academic pricing
- Apply for research grants to cover costs
- Co-author with faculty who have access
- Request sample data for pilot study

---

## 📝 Data Citation

Always cite datasets in papers:
```
"We obtain stock return data from the Center for Research
in Security Prices (CRSP) and accounting data from
Compustat via Wharton Research Data Services (WRDS)."
```

---

**Storage Requirements**: 1-10 TB for comprehensive historical data
**Computing**: High-performance cluster often needed for large-scale analysis

**Next**: [Professional Datasets](../04-professional-expert/datasets.md)
