
🏆 Tabular Foundation Models (TFMs)
TabPFN (Prior-data Fitted Network)

Latest: TabPFN-2.5 (November 2025)
Repository: PriorLabs/TabPFN
Key Features:

Zero-shot predictions (no training needed)
Pre-trained on 130M synthetic datasets
Handles up to 50,000 samples × 2,000 features (v2.5)
In-context learning via transformers
Distillation to compact MLPs


Papers:

Nature (2025): "Accurate predictions on small data with a tabular foundation model"
arXiv 2511.08667: "TabPFN-2.5: Advancing the State of the Art"


Best For: Small-to-medium datasets with zero training time

TabICL

Repository: soda-inria/tabicl
Features:

Scales to 500K samples (vs TabPFN's 10K)
10× faster than TabPFNv2
Column-then-row attention architecture
Pre-trained on datasets up to 60K samples


Paper: ICML 2025

TabuLa-8B

Repository: mlfoundations/rtfm
Features:

Based on Llama 3-8B
Language modeling approach to tabular data
Transfer learning across datasets
Zero-shot and few-shot capabilities


Paper: NeurIPS 2024 - "Large Scale Transfer Learning for Tabular Data via Language Modeling"
Limitation: 8K token context window limits large tables

CARTE (Context-Aware Tabular Representation)

Features: Pre-training and transfer learning for tabular data
Paper: ICML 2024

TabDPT (Tabular Discriminative Pre-trained Transformer)

Features: Self-supervised learning + in-context learning
Installation: Available via pip with scikit-learn API

Other Notable TFMs

TabM (ICLR 2025): Ensemble-like MLP architecture
Mitra: Mixed synthetic priors
LimiX: Unified architecture (prediction + imputation + causal inference)
Real-TabPFN: Enhanced TabPFNv2 for real-world data
TabAutoPNPNet: Periodicity-based (Fourier + Chebyshev)


🌲 Gradient Boosting Methods (Traditional ML Champions)
CatBoost (Yandex) ⭐ Currently Leading

Key Advantages:

Native categorical feature handling (no encoding needed)
Ordered boosting (prevents target leakage)
Symmetric trees (better generalization)
48× faster inference than XGBoost/LightGBM
Best out-of-the-box performance
GPU support


When to Use: Categorical-heavy data, minimal tuning time, production deployment
Benchmarks: 20%+ better than XGBoost on many datasets (TabArena, TALENT)

XGBoost

Key Advantages:

Most mature, largest community
Fine-grained hyperparameter control
Excellent sparsity handling
L1/L2 regularization


When to Use: Need precise control, strong community support
Tree Growth: Level-wise (depth-first)

LightGBM (Microsoft)

Key Advantages:

Fastest training on large datasets
Leaf-wise tree growth
GOSS (Gradient-based One-Side Sampling)
Excellent GPU efficiency


When to Use: Large datasets (millions of rows), speed-critical applications
Caution: More prone to overfitting without regularization

Performance Summary:

Speed: LightGBM > CatBoost > XGBoost
Categorical Data: CatBoost >> LightGBM > XGBoost
Accuracy: CatBoost ≥ XGBoost ≥ LightGBM (dataset-dependent)
Inference: CatBoost >> XGBoost ≈ LightGBM


🤖 AutoML Frameworks
AutoGluon (AWS) ⭐ Top Performance

Repository: autogluon/autogluon
Features:

Multi-layer model stacking/ensembling
Supports tabular, text, image, time-series
Deep learning integration
GPU support
3 lines of code: TabularPredictor().fit()


Performance: Consistently ranks #1 in benchmarks
Paper: "AutoGluon-Tabular: Robust and Accurate AutoML" (2020)

H2O AutoML

Features:

Distributed computing
Multiple language APIs (Python, R, Java, Scala)
Web GUI (H2O Flow)
Model stacking


Commercial: DriverlessAI for enterprise

PyCaret ⭐ Most User-Friendly

Features:

Low-code interface
25+ algorithms
Automated preprocessing
Interactive visualizations
Great for beginners


Limitation: May not match specialized AutoML performance

FLAML (Microsoft Research)

Features:

Fast, lightweight
Budget-aware optimization
Cost-effective hyperparameter tuning
Minimal computational cost



Other AutoML Tools:

auto-sklearn: Meta-learning + Bayesian optimization
TPOT: Genetic programming approach
MLJAR: User-friendly with great documentation
AutoKeras: Deep learning focus (based on Keras)
Lazy Predict: Quick baseline comparison


🔧 Feature Engineering Libraries
Featuretools (Alteryx)

Repository: alteryx/featuretools
Key Concept: Deep Feature Synthesis (DFS)
Features:

Automated feature creation from relational data
Aggregation + transformation primitives
Handles temporal relationships
Can integrate with tsfresh primitives


Use Cases: Multi-table datasets, temporal features

tsfresh (Time Series Feature Extraction)

Repository: blue-yonder/tsfresh
Features:

800+ time series features
63 characterization methods
Built-in feature selection (hypothesis testing)
Statistical, FFT, entropy, autocorrelation


Paper: Neurocomputing (2018)
Use Cases: Time series, sequential data, sensor data

autofeat

Features:

Non-linear feature generation (log, x², x³)
L1 regularization for selection
One-hot encoding for categoricals



Feature-engine

Features:

Scikit-learn compatible
Encoding, imputation, discretization
Outlier handling



Category Encoders

Encoders: Target, Binary, Hashing, WOE, James-Stein, Leave-one-out


📊 Comprehensive Toolkits & Benchmarks
TALENT (LAMDA-Tabular)

Repository: LAMDA-Tabular/TALENT
Features:

35+ deep learning methods
10+ classical methods
300+ benchmark datasets (basic) + 22 large datasets
Unified evaluation framework


Paper: JMLR 2025

TabReD (Yandex Research)

Repository: yandex-research/tabred
Features:

8 industry-grade datasets
Time-based splits (addresses distribution drift)
Feature-rich real-world data


Paper: ICLR 2025 Spotlight
Finding: Simple MLPs + GBDT work best on realistic datasets

TabArena

Paper: NeurIPS 2025
Features: Living benchmark for tabular ML


📚 Key Research Papers
Foundation Models

TabPFN-2.5 (2025): "Advancing the State of the Art in Tabular Foundation Models"
TabuLa-8B (NeurIPS 2024): "Large Scale Transfer Learning for Tabular Data"
TabICL (ICML 2025): "In-Context Learning on Large Data"
CARTE (ICML 2024): "Pre-training and Transfer for Tabular Learning"

Benchmarks & Analysis

TabReD (ICLR 2025): "Analyzing Pitfalls in Tabular Deep Learning Benchmarks"
TALENT (JMLR 2025): "A Tabular Analytics and Learning Toolbox"
"Why do tree-based models still outperform deep learning?" (NeurIPS 2022)
"Tabular Data: Deep Learning is Not All You Need" (highly cited)

Architectures

TabM (ICLR 2025): Ensemble-like MLP architecture
FT-Transformer (NeurIPS 2021): Feature tokenizer + transformer
TabNet (AAAI 2021): Attentive interpretable learning
SAINT: Row attention + contrastive pre-training
TabR: Nearest neighbors approach


🎯 Recommended Technology Stack by Use Case
Quick Prototyping

AutoML: AutoGluon or PyCaret
Traditional ML: CatBoost with defaults

Small Datasets (<10K rows)

Foundation Model: TabPFN-2.5 (zero-shot)
Traditional: CatBoost or XGBoost

Large Datasets (>100K rows)

Foundation Model: TabICL
Traditional: LightGBM (speed) or CatBoost (accuracy)
AutoML: AutoGluon

Time Series Features

Feature Engineering: tsfresh
Forecasting: AutoGluon-TimeSeries or TabPFN-TS

Multi-Table Relational Data

Feature Engineering: Featuretools (Deep Feature Synthesis)

Production Deployment

Inference Speed: CatBoost (48× faster)
Model Serving: XGBoost (most deployment tools)

Research & Experimentation

Benchmark: TALENT toolkit
Comprehensive Comparison: Train on TabReD datasets


📦 Essential Python Packages
python# Core Data Processing
pandas, numpy, scipy

# Traditional ML
xgboost, lightgbm, catboost
scikit-learn

# Foundation Models
pip install tabpfn  # TabPFN
# rtfm for TabuLa-8B

# AutoML
autogluon, pycaret, h2o, flaml

# Feature Engineering
featuretools, tsfresh, autofeat
feature-engine, category_encoders

# Visualization & Analysis
matplotlib, seaborn, plotly
shap, eli5 (interpretability)

# Deep Learning for Tabular
pytorch-tabular, pytorch-frame
tensorflow, keras

🔬 Current State (2024-2025)
Key Findings:

CatBoost is surging - outperforming XGBoost by 20%+ on many benchmarks
Foundation models are emerging - TabPFN-2.5 matches tuned AutoGluon
Industry ≠ Academic benchmarks - TabReD shows simpler models win on real data
Time-based splits matter - Distribution drift is underrepresented in benchmarks
Gradient boosting still dominates - especially on feature-rich, real-world data

Production Reality:

Simple MLPs + GBDT consistently win on industry datasets
Foundation models excel on smaller, cleaner datasets
Deep learning's advantage is less clear on heterogeneous tabular data



🤖 Financial Large Language Models (LLMs)
PIXIU & FinMA

Repository: The-FinAI/PIXIU
Models: FinMA-7B-NLP, FinMA-7B-full, FinMA-30B
Features:

Fine-tuned on LLaMA for financial tasks
128K instruction samples for training
8 tasks across 15 datasets
Sentiment analysis, NER, classification, stock prediction


Paper: "PIXIU: A Large Language Model, Instruction Data and Evaluation Benchmark for Finance" (NeurIPS 2023)

FinGPT (AI4Finance-Foundation)

Repository: AI4Finance-Foundation/FinGPT
Key Advantage: Democratized, low-cost alternative to BloombergGPT (~$300 vs $3M)
Features:

FinGPT v3 series (uses LoRA for efficient fine-tuning)
Real-time data integration (34+ sources)
RLHF (Reinforcement Learning from Human Feedback)
Sentiment analysis, robo-advising, algorithmic trading


Models: llama2-7b, llama2-13b, chatglm2-6B based

BloombergGPT

Paper: "BloombergGPT: A Large Language Model for Finance" (2023)
Specs: 50B parameters, 363B financial tokens + 345B general tokens
Status: Proprietary (not open-source)
Use Cases: Sentiment analysis, NER, news classification, Q&A

TabuLa-8B (RTFM)

Repository: mlfoundations/rtfm
Specialization: Tabular data (financial statements, structured data)
Features: Zero-shot and few-shot learning on tabular datasets


📊 Time Series & Forecasting Models
Transformer-Based Models

CNN-Transformer Hybrid (2023) - Combines CNNs for short-term and Transformers for long-term dependencies
LSTM-mTrans-MLP (2025) - Ensemble model integrating LSTM, modified Transformer, and MLP
Modality-aware Transformer (2024) - Multimodal approach combining text and numerical time series

Popular Architectures

LSTM/GRU: Traditional for sequential data
Autoformer: Best Sharpe ratio for trading
Non-Stationary Transformer: Highest prediction accuracy
Prophet (Meta): Simple, effective for forecasting with seasonality


🐍 Essential Python Libraries
Data Collection

yfinance: Yahoo Finance API (most popular)
pandas-datareader: Multiple data sources
alpha_vantage: Real-time and historical data
Quandl: Financial, economic datasets

Technical Analysis

TA-Lib: 150+ technical indicators (C++ with Python wrapper)
pandas_ta: 130+ indicators, pandas-native
technical-indicators: Pure Python implementation

Quantitative Finance

QuantLib: Derivatives pricing, risk management (industry standard)
PyQL: QuantLib Python port
FinancePy: Options, bonds, swaps pricing

Backtesting & Trading

Zipline: Event-driven backtesting (by Quantopian)
Backtrader: Flexible backtesting framework
VectorBT: High-performance vectorized backtesting
QSTrader: Event-driven backtesting

Portfolio Analysis

PyFolio: Portfolio performance & risk analytics
PyPortfolioOpt: Modern portfolio theory, efficient frontier
Riskfolio-Lib: Portfolio optimization

Machine Learning

scikit-learn: Traditional ML algorithms
TensorFlow/PyTorch: Deep learning
XGBoost/LightGBM: Gradient boosting
Prophet: Time series forecasting

Data Processing

pandas: Data manipulation (essential)
NumPy: Numerical operations
Dask: Large-scale data processing


📂 Notable GitHub Projects
Stock Analysis & Prediction

Stock-Price-Trade-Analyzer - TensorFlow-based LSTM/CNN models
stock-risk-analyzer - ML-powered risk assessment using Random Forest
machine-learning-for-financial-analysis - Comprehensive Python examples

Comprehensive Toolkits

awesome-quant - Curated list of 200+ quant finance resources
OpenBB Terminal - Open-source investment research terminal
ArcticDB - High-performance time series datastore


📄 Key Research Papers

"Large Scale Transfer Learning for Tabular Data via Language Modeling" (TabuLa-8B)
"FinGPT: Open-Source Financial Large Language Models" (arXiv:2306.06031)
"Financial Time Series Forecasting using CNN and Transformer" (arXiv:2304.04912)
"LSTM–Transformer-Based Robust Hybrid Deep Learning Model" (2025)
"Modality-aware Transformer for Financial Time series Forecasting" (ICAIF 2024)


🎯 Recommended Starting Point
For stock analysis and feature extraction, I recommend:

Start with: yfinance + pandas + TA-Lib for data and indicators
Add ML: scikit-learn or XGBoost for predictions
Advanced: FinGPT for sentiment analysis or TabuLa-8B for tabular features
Backtesting: Backtrader or Zipline
Portfolio: PyPortfolioOpt for optimization