import time
import random
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data import NIFTY_STOCKS, load_prices, load_benchmark
from metrics import (summary_table, daily_returns, optimize, random_portfolios,
                     portfolio_stats, var_cvar, TRADING_DAYS, RISK_FREE)
from backtest import walk_forward, perf_table
from loading import show_loading, FACTS
from style import inject_css

st.set_page_config(page_title="Nifty Portfolio Lab", page_icon="📈", layout="wide")
inject_css()

PRESETS = {
    "Balanced mix": ["Reliance", "TCS", "HDFC Bank", "Infosys", "ITC", "L&T"],
    "Banks & finance": ["HDFC Bank", "ICICI Bank", "SBI", "Kotak Bank", "Axis Bank", "Bajaj Finance"],
    "IT & tech": ["TCS", "Infosys", "Wipro", "HCL Tech"],
    "Defensive": ["HUL", "ITC", "Nestle", "Sun Pharma", "NTPC"],
    "Cyclicals & energy": ["Reliance", "ONGC", "Coal India", "Tata Steel", "L&T", "NTPC"],
    "All 24 stocks": list(NIFTY_STOCKS),
}

# ---------- Cached heavy work (computed once, then remembered) ----------
@st.cache_data(show_spinner=False)
def get_optimal(rets, max_w):
    return optimize(rets, "sharpe", max_w), optimize(rets, "minvar", max_w)

@st.cache_data(show_spinner=False)
def get_frontier(rets):
    return random_portfolios(rets)

@st.cache_data(show_spinner="Running walk-forward backtest... 💡 " + random.choice(FACTS))
def run_backtests(rets, max_w, lookback, rebalance, cost):
    return pd.DataFrame({
        "Max Sharpe": walk_forward(rets, "sharpe", max_w, lookback, rebalance, cost),
        "Min Variance": walk_forward(rets, "minvar", max_w, lookback, rebalance, cost),
        "Equal Weight": walk_forward(rets, "equal", max_w, lookback, rebalance, cost),
    })

# ---------- Sidebar ----------
st.sidebar.title("📈 Nifty Portfolio Lab")
preset = st.sidebar.selectbox("Quick preset", list(PRESETS))
with st.sidebar.form("controls"):
    names = st.multiselect("Stocks (min 2)", list(NIFTY_STOCKS), default=PRESETS[preset])
    start = st.date_input("Start date", pd.Timestamp("2017-01-01"))
    end = st.date_input("End date", pd.Timestamp.today())
    max_w = st.slider("Max weight per stock", 0.10, 1.00, 0.30, 0.05)
    st.form_submit_button("🚀 Run analysis", use_container_width=True)

if len(names) < 2:
    st.warning("Pick at least 2 stocks in the sidebar, then press Run analysis.")
    st.stop()
if start >= end:
    st.error("Start date must be before the end date.")
    st.stop()
if len(names) * max_w < 1 - 1e-9:
    st.warning("Max weight is too low for this many stocks. Raise the slider or add stocks.")
    st.stop()

# ---------- First-run loading screen (only the very first time) ----------
first_run = "loaded" not in st.session_state
loader = st.empty()
def stage(progress, message):
    if first_run:
        show_loading(loader, progress, message)

stage(0.10, "Downloading stock prices...")
prices = load_prices(tuple(NIFTY_STOCKS[n] for n in names), str(start), str(end))
if prices.empty or prices.shape[1] < 2 or prices.shape[1] * max_w < 1 - 1e-9:
    loader.empty()
    st.error("Couldn't get enough price data for this selection. Try other stocks or an earlier start date.")
    st.stop()

st.sidebar.caption(f"Latest data: {prices.index[-1].date()} (daily closes)")
rets = daily_returns(prices)

stage(0.40, "Crunching risk numbers and optimizing portfolios...")
table = summary_table(prices)
w_sharpe, w_minvar = get_optimal(rets, max_w)
w_equal = pd.Series(1 / len(rets.columns), index=rets.columns)
mean_ret = (rets.mean() * TRADING_DAYS).values
cov = (rets.cov() * TRADING_DAYS).values

strategies = {"Max Sharpe": w_sharpe, "Min Variance": w_minvar, "Equal Weight": w_equal}
rows = {}
for label, w in strategies.items():
    r, v = portfolio_stats(w.values, mean_ret, cov)
    var, cvar = var_cvar((rets * w).sum(axis=1))
    rows[label] = {"Expected Return": r, "Volatility": v, "Sharpe": (r - RISK_FREE) / v,
                   "VaR 95% (1-day)": var, "CVaR 95% (1-day)": cvar}
summary = pd.DataFrame(rows).T

# ---------- Page ----------
st.title("Nifty Portfolio Lab")
st.caption("Risk analysis and portfolio optimization on Nifty 50 stocks · Developed by Anant Aravind Pillai")

tab_ov, tab_risk, tab_opt, tab_bt, tab_stress = st.tabs(
    ["📊 Overview", "⚠️ Risk", "🎯 Optimizer", "🔁 Backtest", "🌪️ Stress Test"])

# ----- Overview -----
with tab_ov:
    best = table["Sharpe"].idxmax()
    calmest = table["Volatility"].idxmin()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stocks analysed", len(prices.columns))
    c2.metric("Trading days", f"{len(prices):,}")
    c3.metric("Best Sharpe", best, f"{table.loc[best, 'Sharpe']:.2f}", delta_color="off")
    c4.metric("Lowest volatility", calmest, f"{table.loc[calmest, 'Volatility']:.1%}", delta_color="off")

    st.subheader("Growth of ₹100 invested")
    log_scale = st.toggle("Log scale", value=False)
    growth = prices / prices.iloc[0] * 100
    fig = px.line(growth, log_y=log_scale,
                  labels={"value": "Value of ₹100", "index": "Date", "variable": "Stock"})
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# ----- Risk -----
with tab_risk:
    st.subheader("Risk and return summary")
    st.dataframe(table.style.format({
        "Return (CAGR)": "{:.1%}", "Volatility": "{:.1%}",
        "Sharpe": "{:.2f}", "Max Drawdown": "{:.1%}"}), use_container_width=True)
    st.download_button("⬇ Download as CSV", table.to_csv().encode(),
                       "risk_summary.csv", "text/csv")

    st.subheader("Risk vs return")
    st.caption("Up and to the left is better: more return for less risk.")
    scat = px.scatter(table.reset_index(names="Stock"), x="Volatility", y="Return (CAGR)",
                      text="Stock", color="Sharpe", color_continuous_scale="Viridis")
    scat.update_traces(textposition="top center", marker=dict(size=12))
    scat.update_xaxes(tickformat=".0%")
    scat.update_yaxes(tickformat=".0%")
    st.plotly_chart(scat, use_container_width=True)

    st.subheader("Drawdown explorer")
    pick = st.selectbox("Choose a stock", list(prices.columns))
    dd = prices[pick] / prices[pick].cummax() - 1
    dd_fig = px.area(x=dd.index, y=dd.values, labels={"x": "Date", "y": "Drawdown"})
    dd_fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(dd_fig, use_container_width=True)

    st.subheader("Correlation between stocks")
    st.caption("Lower correlation = more diversification benefit.")
    st.plotly_chart(px.imshow(rets.corr(), text_auto=".2f", color_continuous_scale="RdBu_r",
                              zmin=-1, zmax=1), use_container_width=True)

# ----- Optimizer -----
with tab_opt:
    st.subheader("Portfolio comparison")
    st.dataframe(summary.style.format({
        "Expected Return": "{:.1%}", "Volatility": "{:.1%}", "Sharpe": "{:.2f}",
        "VaR 95% (1-day)": "{:.2%}", "CVaR 95% (1-day)": "{:.2%}"}), use_container_width=True)
    st.caption("In-sample results (fitted on the same data). The Backtest tab tests them properly.")

    st.subheader("Efficient frontier")
    sim = get_frontier(rets)
    ef = px.scatter(sim, x="Volatility", y="Return", color="Sharpe",
                    color_continuous_scale="Viridis", opacity=0.6)
    for label, color in [("Max Sharpe", "red"), ("Min Variance", "cyan"), ("Equal Weight", "white")]:
        ef.add_trace(go.Scatter(
            x=[summary.loc[label, "Volatility"]], y=[summary.loc[label, "Expected Return"]],
            mode="markers", name=label,
            marker=dict(size=15, symbol="star", color=color, line=dict(width=1, color="black"))))
    ef.update_xaxes(tickformat=".0%")
    ef.update_yaxes(tickformat=".0%")
    st.plotly_chart(ef, use_container_width=True)

    st.subheader("Optimal weights")
    choice = st.radio("Portfolio", ["Max Sharpe", "Min Variance"], horizontal=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Expected return", f"{summary.loc[choice, 'Expected Return']:.1%}")
    m2.metric("Volatility", f"{summary.loc[choice, 'Volatility']:.1%}")
    m3.metric("Sharpe ratio", f"{summary.loc[choice, 'Sharpe']:.2f}")

    wsel = (w_sharpe if choice == "Max Sharpe" else w_minvar)
    wsel = wsel[wsel > 0.005].sort_values(ascending=False)
    left, right = st.columns(2)
    left.plotly_chart(px.bar(x=wsel.index, y=wsel.values, labels={"x": "Stock", "y": "Weight"}),
                      use_container_width=True)
    right.plotly_chart(px.pie(names=wsel.index, values=wsel.values, hole=0.5),
                       use_container_width=True)

# ----- Backtest -----
results = None
with tab_bt:
    st.subheader("Walk-forward backtest (out-of-sample)")
    st.caption("At each rebalance the optimizer sees only past data, then holds the weights on unseen data.")
    b1, b2, b3 = st.columns(3)
    lookback = b1.selectbox("Lookback (trading days)", [126, 252, 504], index=1)
    rebalance = b2.selectbox("Rebalance every (trading days)", [21, 63, 126], index=1)
    cost_bps = b3.number_input("Transaction cost (bps)", 0, 50, 10)

    if len(rets) <= lookback + rebalance:
        st.warning("Not enough history for these settings. Use an earlier start date or a shorter lookback.")
    else:
        stage(0.70, "Running the walk-forward backtest (first run only)...")
        results = run_backtests(rets, max_w, lookback, rebalance, cost_bps / 10000)

        bench = load_benchmark(str(start), str(end)).pct_change().dropna()
        bench.index = pd.to_datetime(bench.index).tz_localize(None)
        results["Nifty 50 Index"] = bench.reindex(results.index)
        results = results.dropna()

        bt_fig = px.line((1 + results).cumprod() * 100,
                         labels={"value": "Growth of ₹100", "index": "Date", "variable": "Strategy"})
        bt_fig.update_layout(hovermode="x unified")
        st.plotly_chart(bt_fig, use_container_width=True)

        perf = perf_table(results)
        st.dataframe(perf.style.format({
            "Return (CAGR)": "{:.1%}", "Volatility": "{:.1%}",
            "Sharpe": "{:.2f}", "Max Drawdown": "{:.1%}"}), use_container_width=True)
        st.download_button("⬇ Download backtest results", perf.to_csv().encode(),
                           "backtest_results.csv", "text/csv")

# ----- Stress test -----
with tab_stress:
    st.subheader("Stress tests")
    st.caption("Total return of each strategy (out-of-sample) during real market crashes.")
    if results is None:
        st.info("Run the backtest first (see the Backtest tab settings).")
    else:
        CRISES = {
            "COVID crash (20 Jan - 23 Mar 2020)": ("2020-01-20", "2020-03-23"),
            "2022 selloff (1 Jan - 17 Jun 2022)": ("2022-01-01", "2022-06-17"),
        }
        stress_rows = {}
        for label, (s, e) in CRISES.items():
            window = results.loc[s:e]
            if len(window) < 20:
                stress_rows[label] = {c: np.nan for c in results.columns}
            else:
                stress_rows[label] = ((1 + window).prod() - 1).to_dict()
        stress = pd.DataFrame(stress_rows).T

        if stress.isna().all().all():
            st.info("The backtest period doesn't cover these crashes. Use an earlier start date or a shorter lookback.")
        else:
            st.dataframe(stress.style.format("{:.1%}", na_rep="n/a"), use_container_width=True)
            st.plotly_chart(px.bar(stress, barmode="group",
                                   labels={"value": "Total return", "index": ""}),
                            use_container_width=True)

# ---------- Finish loading screen ----------
if first_run:
    show_loading(loader, 1.0, "All done!")
    time.sleep(0.6)
loader.empty()
st.session_state["loaded"] = True

st.divider()
st.caption("Developed by Anant Aravind Pillai · Data: Yahoo Finance (daily closes) · "
           "Educational project, not investment advice.")