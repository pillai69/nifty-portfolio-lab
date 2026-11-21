import streamlit as st
from style import inject_css

st.set_page_config(page_title="About | Nifty Portfolio Lab", page_icon="📈", layout="wide")
inject_css()

def card(col, emoji, title, text):
    col.markdown(f'<div class="card"><h4>{emoji} {title}</h4><p>{text}</p></div>',
                 unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>Nifty Portfolio Lab</h1>
  <p>Measure the risk of Indian large-cap stocks, build optimized portfolios, and test honestly
  whether they work on data they have never seen.</p>
  <p style="margin-top:16px;"><b>Developed by Anant Aravind Pillai</b> ·
  B.Sc. Economics with Data Science, CHRIST (Deemed to be University), Bengaluru</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Nifty 50 stocks", "24")
m2.metric("Risk measures", "7")
m3.metric("Strategies tested", "3")
m4.metric("Crash tests", "2")

t1, t2, t3, t4, t5 = st.tabs(
    ["🎯 The project", "⚙️ How it works", "📚 Key concepts", "⚠️ Limitations & FAQ", "👤 Developer"])

with t1:
    st.subheader("The research question")
    st.info("Does mean-variance optimization actually beat an equal-weight portfolio of "
            "Nifty 50 stocks when tested out of sample?")
    st.subheader("How to use the dashboard")
    st.markdown(
        "1. Open the **app** page and pick a **quick preset** or choose your own stocks in the sidebar\n"
        "2. Set the date range and the maximum weight per stock, then press **Run analysis**\n"
        "3. Explore the **Overview**, **Risk** and **Optimizer** tabs to see how the stocks behave\n"
        "4. Open the **Backtest** tab to see how the optimized portfolios would have performed on unseen data\n"
        "5. Check the **Stress Test** tab for the COVID-19 crash and the 2022 selloff"
    )

with t2:
    st.subheader("The pipeline")
    cols = st.columns(5)
    card(cols[0], "1️⃣", "Data", "Daily prices from Yahoo Finance via yfinance, with the Nifty 50 index as the benchmark.")
    card(cols[1], "2️⃣", "Risk", "Returns, volatility, Sharpe ratio, max drawdown, VaR, CVaR and correlations.")
    card(cols[2], "3️⃣", "Optimize", "Max Sharpe and Min Variance portfolios with weight caps, solved with SciPy.")
    card(cols[3], "4️⃣", "Backtest", "Walk-forward test on unseen data, including transaction costs.")
    card(cols[4], "5️⃣", "Stress test", "Performance in the COVID-19 crash and the 2022 selloff.")

    st.subheader("The walk-forward idea")
    st.write(
        "A normal optimizer is judged on the same data it learned from, which flatters it. "
        "Here, at every rebalance date the optimizer sees only the previous year of prices, picks "
        "weights, and those weights are then held on the next quarter, which it has never seen. "
        "Repeating this across the whole history gives an honest picture of what would have happened."
    )
    with st.expander("Technical details"):
        st.markdown(
            "- **Returns:** daily percentage changes of adjusted closing prices\n"
            "- **Volatility:** standard deviation of daily returns times the square root of 252\n"
            "- **Risk-free rate:** assumed 7% per year\n"
            "- **Optimizer:** SLSQP, long-only, weights sum to 100%, per-stock cap set by the user\n"
            "- **Transaction cost:** charged on the amount traded at each rebalance\n"
            "- **Data freshness:** daily closes, cached for one hour (not real-time)"
        )

with t3:
    st.subheader("Plain-English glossary")
    with st.expander("Volatility"):
        st.write("How much a price swings up and down. Higher volatility means a bumpier ride.")
    with st.expander("Sharpe ratio"):
        st.write("Return earned above a risk-free investment, per unit of risk taken. Higher is better.")
    with st.expander("Maximum drawdown"):
        st.write("The worst fall from a previous peak to a later low. It shows the real pain an investor would have felt.")
    with st.expander("VaR and CVaR"):
        st.write("Value at Risk is the daily loss that is exceeded only on the worst 5% of days. "
                 "CVaR is the average loss on those worst days.")
    with st.expander("Correlation and diversification"):
        st.write("Stocks that do not move together reduce portfolio risk without reducing expected return. "
                 "That is the core idea of Markowitz's Modern Portfolio Theory.")
    with st.expander("Efficient frontier"):
        st.write("The set of portfolios that give the highest return for each level of risk.")
    with st.expander("Out-of-sample testing"):
        st.write("Judging a strategy on data it did not use to make its decisions.")
    with st.expander("Survivorship bias"):
        st.write("Only looking at companies that are still around today, which makes past results look better than they were.")

with t4:
    st.subheader("Limitations")
    st.markdown(
        "- **Survivorship bias:** the stock universe is today's constituents, not the historical index membership\n"
        "- **Estimation error:** past returns are noisy predictors of the future, so optimized weights can be unstable\n"
        "- **Normality assumption:** return-based risk measures can understate extreme crashes\n"
        "- **Simplifications:** taxes, slippage and liquidity are not modelled"
    )
    st.warning("This is an educational project, not investment advice.")
    st.subheader("FAQ")
    with st.expander("Is the data real-time?"):
        st.write("No. It uses daily closing prices from Yahoo Finance, refreshed automatically at most once an hour.")
    with st.expander("Why doesn't the Max Sharpe portfolio always win?"):
        st.write("Because it is built from past returns, which are a noisy guide to the future. "
                 "This is a well-known weakness of mean-variance optimization, and it is exactly what the backtest is designed to reveal.")
    with st.expander("Why is there a maximum weight per stock?"):
        st.write("Without a cap, optimizers tend to put almost everything in one or two stocks, which is unrealistic and risky.")

with t5:
    left, right = st.columns([2, 1], gap="large")
    with left:
        st.markdown("### Anant Aravind Pillai")
        st.write("First-year B.Sc. Economics with Data Science student at CHRIST (Deemed to be University), Bengaluru. "
                 "Interested in quantitative finance, investment research, financial modeling and data visualization.")
        st.markdown("[GitHub](https://github.com/YOUR-USERNAME) · [LinkedIn](https://www.linkedin.com/in/pillaianant)")
    with right:
        st.markdown("**Built with**")
        st.markdown("`Python` `pandas` `NumPy` `SciPy` `Plotly` `Streamlit` `yfinance`")

st.divider()
st.caption("© 2026 Anant Aravind Pillai. Built as a data science and finance portfolio project.")