# Nifty Portfolio Lab

Interactive dashboard for risk analysis and portfolio optimization on Nifty 50 stocks, with an out-of-sample walk-forward backtest.

**Live app:** [paste your Streamlit link here]

## Research question
Does mean-variance optimization actually beat an equal-weight portfolio of Nifty 50 stocks when tested on data it has not seen?

## What it does
- Downloads NSE price data (yfinance) for 24 Nifty 50 stocks
- Risk metrics: CAGR, volatility, Sharpe ratio (7% risk-free rate), max drawdown, VaR/CVaR (95%), correlation matrix
- Optimizer (Max Sharpe and Min Variance) with a per-stock weight cap, plus an efficient frontier
- Walk-forward backtest with transaction costs, compared against Equal Weight and the Nifty 50 index
- Stress tests on the COVID-19 crash and the 2022 selloff

## Key findings
- [e.g. Which strategy had the highest Sharpe out-of-sample, with the number]
- [e.g. Which strategy had the smallest drawdown, with the number]
- [e.g. How strategies behaved in COVID vs 2022]

## Limitations
- Survivorship bias: uses today's constituents, not the historical index membership
- Past returns are noisy predictors of future returns, so optimizer weights are unstable
- Returns assume normality for risk estimates, which understates extreme crashes
- Educational project, not investment advice

## Tech stack
Python, pandas, NumPy, SciPy (SLSQP optimization), Plotly, Streamlit, yfinance

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Author
Anant Pillai, B.Sc. Economics with Data Science, CHRIST (Deemed to be University)