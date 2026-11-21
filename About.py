import streamlit as st
from style import masthead, note, footer

masthead("About this project",
         "What the analysis does, how it works, and what it cannot tell you.")

main, side = st.columns([3, 1], gap="large")

with main:
    note("Research question",
         ["Does mean-variance optimization beat an equal-weight portfolio of Nifty 50 stocks "
          "when it is tested on data it has not seen?"], bullets=False)

    st.subheader("Method")
    st.markdown(
        "1. **Data.** Daily adjusted closing prices for NSE-listed stocks come from Yahoo Finance, "
        "with the Nifty 50 index as the benchmark. Prices are daily, not real-time, and are cached for one hour.\n"
        "2. **Risk measures.** Each stock is measured on return, volatility, Sharpe ratio, maximum drawdown, "
        "and correlation with the others.\n"
        "3. **Optimization.** Max Sharpe and Min Variance portfolios are solved with SciPy (SLSQP). "
        "Weights are long-only, sum to 100%, and are capped per stock.\n"
        "4. **Walk-forward backtest.** At each rebalance date the optimizer sees only the previous "
        "lookback window, chooses weights, and holds them over the next period on data it has not seen. "
        "Transaction costs are charged on the amount traded.\n"
        "5. **Stress tests.** Out-of-sample returns are measured through the COVID-19 crash "
        "(20 Jan to 23 Mar 2020) and the 2022 selloff (1 Jan to 17 Jun 2022)."
    )

    st.subheader("Measures")
    st.markdown("""
| Measure | What it tells you | How it is calculated |
|---|---|---|
| Volatility | How much the price swings | Standard deviation of daily returns × √252 |
| Sharpe ratio | Return above a risk-free asset, per unit of risk | (Annual return − 7%) ÷ volatility |
| Maximum drawdown | The worst fall from a previous peak | Lowest value of price ÷ running peak − 1 |
| Value at Risk (95%) | A one-day loss exceeded on only 5% of days | 5th percentile of daily portfolio returns |
| CVaR (95%) | The average loss on those worst days | Mean of returns at or below the VaR |
| Correlation | How closely two stocks move together | Correlation of daily returns |
""")

    st.subheader("Limitations")
    st.markdown(
        "- **Survivorship bias.** The stock universe is today's constituents, not the index membership at each past date, "
        "which flatters historical results.\n"
        "- **Estimation error.** Past returns are a noisy guide to future returns, so optimized weights can be unstable.\n"
        "- **Distribution assumptions.** Return-based risk measures can understate extreme crashes.\n"
        "- **Simplifications.** Taxes, slippage and liquidity are not modelled."
    )
    st.warning("This is an educational project, not investment advice.")

    st.subheader("Questions")
    with st.expander("Is the data real-time?"):
        st.write("No. It uses daily closing prices from Yahoo Finance, refreshed at most once an hour.")
    with st.expander("Why doesn't the Max Sharpe portfolio always win?"):
        st.write("It is built from past returns, which are a noisy guide to the future. This is a well-known "
                 "weakness of mean-variance optimization, and it is what the backtest is designed to reveal.")
    with st.expander("Why is there a maximum weight per stock?"):
        st.write("Without a cap, optimizers tend to put almost everything into one or two stocks, "
                 "which is unrealistic and risky.")

with side:
    st.subheader("Author")
    st.markdown("**Anant Aravind Pillai**")
    st.write("B.Sc. Economics with Data Science, CHRIST (Deemed to be University), Bengaluru")
    st.markdown("[GitHub](https://github.com/pillai69)")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/YOUR-LINKEDIN)")
    st.markdown("[Source code](https://github.com/pillai69/nifty-portfolio-lab)")
    st.subheader("Built with")
    st.write("Python, pandas, NumPy, SciPy, Plotly, Streamlit, yfinance")

footer()