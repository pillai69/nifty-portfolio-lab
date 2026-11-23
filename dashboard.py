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
from style import (show, range_buttons, stat_strip, note, masthead, ticker, footer,
                   COLORS, STRATEGY_COLORS)

PRESETS = {
    "Balanced mix": ["Reliance", "TCS", "HDFC Bank", "Infosys", "ITC", "L&T"],
    "Banks and finance": ["HDFC Bank", "ICICI Bank", "SBI", "Kotak Bank", "Axis Bank", "Bajaj Finance"],
    "IT and technology": ["TCS", "Infosys", "Wipro", "HCL Tech"],
    "Defensive": ["HUL", "ITC", "Nestle", "Sun Pharma", "NTPC"],
    "Cyclicals and energy": ["Reliance", "ONGC", "Coal India", "Tata Steel", "L&T", "NTPC"],
    "All 24 stocks": list(NIFTY_STOCKS),
}
CRISES = {
    "COVID-19 crash": ("2020-01-20", "2020-03-23"),
    "2022 selloff": ("2022-01-01", "2022-06-17"),
}

def mark_crashes(fig, index):
    # Shade the crash periods that fall inside the chart's date range
    for name, (s, e) in CRISES.items():
        if pd.Timestamp(s) >= index.min() and pd.Timestamp(e) <= index.max():
            fig.add_vrect(x0=s, x1=e, fillcolor=COLORS["rule"], opacity=0.6,
                          line_width=0, layer="below")
            fig.add_annotation(x=s, y=1.0, yref="paper", text=name, showarrow=False,
                               xanchor="left", yanchor="top",
                               font=dict(size=11, color=COLORS["muted"]))

def takeaways(perf):
    # Plain-English findings written from the backtest numbers
    strat = perf.drop(index="Nifty 50 Index", errors="ignore")
    out = []
    best = strat["Sharpe"].idxmax()
    out.append(f"{best} had the highest Sharpe ratio of the three strategies ({strat.loc[best, 'Sharpe']:.2f}).")
    shallow = strat["Max Drawdown"].idxmax()
    out.append(f"{shallow} had the shallowest maximum drawdown ({strat.loc[shallow, 'Max Drawdown']:.1%}).")
    if "Max Sharpe" in strat.index and "Equal Weight" in strat.index:
        diff = (strat.loc["Max Sharpe", "Return (CAGR)"] - strat.loc["Equal Weight", "Return (CAGR)"]) * 100
        out.append(f"After transaction costs, Max Sharpe earned {abs(diff):.1f} percentage points a year "
                   f"{'more' if diff > 0 else 'less'} than Equal Weight.")
    if "Nifty 50 Index" in perf.index:
        idx = perf.loc["Nifty 50 Index", "Sharpe"]
        verdict = "beat" if strat.loc[best, "Sharpe"] > idx else "trailed"
        out.append(f"The best strategy by Sharpe ({best}) {verdict} the Nifty 50 index "
                   f"({strat.loc[best, 'Sharpe']:.2f} against {idx:.2f}).")
    return out

# ---------- Cached heavy work ----------
@st.cache_data(show_spinner=False)
def get_optimal(rets, max_w):
    return optimize(rets, "sharpe", max_w), optimize(rets, "minvar", max_w)

@st.cache_data(show_spinner=False)
def get_frontier(rets):
    return random_portfolios(rets)

@st.cache_data(show_spinner="Running the walk-forward backtest. Did you know? " + random.choice(FACTS))
def run_backtests(rets, max_w, lookback, rebalance, cost):
    return pd.DataFrame({
        "Max Sharpe": walk_forward(rets, "sharpe", max_w, lookback, rebalance, cost),
        "Min Variance": walk_forward(rets, "minvar", max_w, lookback, rebalance, cost),
        "Equal Weight": walk_forward(rets, "equal", max_w, lookback, rebalance, cost),
    })

# ---------- Header and settings ----------
masthead("Risk and portfolio analysis",
         "Nifty 50 stocks, optimized and then tested on data the optimizer has not seen.")

with st.expander("Analysis settings", expanded=True):
    preset = st.selectbox("Starting set", list(PRESETS))
    with st.form("controls", border=False):
        names = st.multiselect("Stocks (minimum 2)", list(NIFTY_STOCKS), default=PRESETS[preset])
        c1, c2, c3, c4 = st.columns([1, 1, 1.4, 1], vertical_alignment="bottom")
        start = c1.date_input("Start date", pd.Timestamp("2017-01-01"))
        end = c2.date_input("End date", pd.Timestamp.today())
        max_w = c3.slider("Maximum weight per stock", 0.10, 1.00, 0.30, 0.05)
        c4.form_submit_button("Run analysis", width="stretch")

if len(names) < 2:
    st.warning("Choose at least 2 stocks, then select Run analysis.")
    st.stop()
if start >= end:
    st.error("The start date must be before the end date.")
    st.stop()
if len(names) * max_w < 1 - 1e-9:
    st.warning("The maximum weight is too low for this many stocks. Raise it or add more stocks.")
    st.stop()

# ---------- Loading screen (first visit only) ----------
first_run = "loaded" not in st.session_state
loader = st.empty()
def stage(progress, message):
    if first_run:
        show_loading(loader, progress, message)

stage(0.10, "Downloading stock prices")
prices = load_prices(tuple(NIFTY_STOCKS[n] for n in names), str(start), str(end))
if prices.empty or prices.shape[1] < 2 or prices.shape[1] * max_w < 1 - 1e-9:
    loader.empty()
    st.error("Not enough price data for this selection. Try other stocks or an earlier start date.")
    st.stop()

rets = daily_returns(prices)

stage(0.40, "Calculating risk and optimizing portfolios")
table = summary_table(prices)
w_sharpe, w_minvar = get_optimal(rets, max_w)
w_equal = pd.Series(1 / len(rets.columns), index=rets.columns)
mean_ret = (rets.mean() * TRADING_DAYS).values
cov = (rets.cov() * TRADING_DAYS).values

rows = {}
for label, w in {"Max Sharpe": w_sharpe, "Min Variance": w_minvar, "Equal Weight": w_equal}.items():
    r, v = portfolio_stats(w.values, mean_ret, cov)
    var, cvar = var_cvar((rets * w).sum(axis=1))
    rows[label] = {"Expected Return": r, "Volatility": v, "Sharpe": (r - RISK_FREE) / v,
                   "VaR 95% (1-day)": var, "CVaR 95% (1-day)": cvar}
summary = pd.DataFrame(rows).T

# ---------- Page ----------
ticker(prices)

tab_ov, tab_risk, tab_opt, tab_bt, tab_stress = st.tabs(
    ["Overview", "Risk", "Optimizer", "Backtest", "Stress test"])

# ----- Overview -----
with tab_ov:
    best = table["Sharpe"].idxmax()
    calmest = table["Volatility"].idxmin()
    stat_strip([
        ("Stocks analysed", f"{prices.shape[1]}", "Nifty 50 constituents"),
        ("Period", f"{prices.index[0]:%Y} to {prices.index[-1]:%Y}",
         f"{prices.index[0]:%b %Y} to {prices.index[-1]:%b %Y}, {len(prices):,} trading days"),
        ("Highest Sharpe ratio", best, f"{table.loc[best, 'Sharpe']:.2f}"),
        ("Lowest volatility", calmest, f"{table.loc[calmest, 'Volatility']:.1%} a year"),
    ])
    st.subheader("Growth of ₹100 invested")
    o1, o2 = st.columns(2)
    log_scale = o1.toggle("Log scale", value=False)
    show_index = o2.toggle("Compare with the Nifty 50 index", value=False)

    growth = prices / prices.iloc[0] * 100
    if show_index:
        b = load_benchmark(str(start), str(end))
        b.index = pd.to_datetime(b.index).tz_localize(None)
        b = b.reindex(prices.index).ffill().dropna()
        base = prices.loc[b.index]
        growth = base / base.iloc[0] * 100
        growth["Nifty 50 Index"] = b / b.iloc[0] * 100

    fig = px.line(growth, log_y=log_scale, labels={"value": "Value of ₹100", "index": "", "variable": ""},
                  color_discrete_map={"Nifty 50 Index": COLORS["gray"]})
    fig.for_each_trace(lambda t: t.update(line=dict(dash="dot", width=3)) if t.name == "Nifty 50 Index" else None)
    fig.update_layout(hovermode="x unified" if growth.shape[1] <= 8 else "closest")
    fig.update_yaxes(tickprefix="₹")
    range_buttons(fig)
    mark_crashes(fig, growth.index)
    show(fig)

# ----- Risk -----
with tab_risk:
    st.subheader("Risk and return by stock")
    st.dataframe(table.style.format({
        "Return (CAGR)": "{:.1%}", "Volatility": "{:.1%}",
        "Sharpe": "{:.2f}", "Max Drawdown": "{:.1%}"}), width="stretch")
    st.download_button("Download as CSV", table.to_csv().encode(), "risk_summary.csv", "text/csv")

    st.subheader("Risk against return")
    st.caption("Stocks toward the upper left earned more return for less risk.")
    sc = px.scatter(table.reset_index(names="Stock"), x="Volatility", y="Return (CAGR)",
                    text="Stock", color="Sharpe",
                    color_continuous_scale=["#B7C9C7", COLORS["accent"]])
    sc.update_traces(textposition="top center", marker=dict(size=11))
    sc.update_xaxes(tickformat=".0%")
    sc.update_yaxes(tickformat=".0%")
    sc.update_layout(coloraxis_colorbar=dict(thickness=12, title="Sharpe"))
    show(sc)

    st.subheader("Drawdown")
    pick = st.selectbox("Stock", list(prices.columns))
    dd = prices[pick] / prices[pick].cummax() - 1
    dd_fig = px.area(x=dd.index, y=dd.values, labels={"x": "", "y": "Fall from previous peak"})
    dd_fig.update_traces(line_color=COLORS["neg"], fillcolor="rgba(179,64,46,0.16)")
    dd_fig.update_yaxes(tickformat=".0%")
    range_buttons(dd_fig)
    show(dd_fig)

    st.subheader("Correlation")
    st.caption("Darker cells mean two stocks move together more closely. Lower values give more diversification.")
    corr = rets.corr()
    hm = px.imshow(corr, text_auto=".2f", color_continuous_scale=["#FFFFFF", COLORS["accent"]],
                   zmin=min(0.0, float(corr.min().min())), zmax=1)
    hm.update_layout(coloraxis_colorbar=dict(thickness=12, title=""))
    show(hm)

# ----- Optimizer -----
with tab_opt:
    st.subheader("Portfolio comparison")
    st.dataframe(summary.style.format({
        "Expected Return": "{:.1%}", "Volatility": "{:.1%}", "Sharpe": "{:.2f}",
        "VaR 95% (1-day)": "{:.2%}", "CVaR 95% (1-day)": "{:.2%}"}), width="stretch")
    st.caption("These results are in-sample: the optimizer was fitted on the same data. "
               "The Backtest tab tests it on data it has not seen.")

    st.subheader("Build your own portfolio")
    st.caption("Set a weight for each stock. The weights are rescaled to add up to 100%, "
               "and your portfolio appears on the efficient frontier below.")
    raw = {}
    wcols = st.columns(4)
    for i, name in enumerate(rets.columns):
        raw[name] = wcols[i % 4].slider(name, 0, 100, int(round(100 / len(rets.columns))), key=f"w_{name}")
    w_user = pd.Series(raw, dtype=float)
    w_user = w_user / w_user.sum() if w_user.sum() > 0 else w_equal
    r_u, v_u = portfolio_stats(w_user.values, mean_ret, cov)
    var_u, cvar_u = var_cvar((rets * w_user).sum(axis=1))
    stat_strip([
        ("Your expected return", f"{r_u:.1%}", "Per year"),
        ("Your volatility", f"{v_u:.1%}", "Per year"),
        ("Your Sharpe ratio", f"{(r_u - RISK_FREE) / v_u:.2f}",
         f"Max Sharpe portfolio: {summary.loc['Max Sharpe', 'Sharpe']:.2f}"),
        ("Worst 5% of days", f"{cvar_u:.2%}", "Average one-day loss (CVaR)"),
    ])

    st.subheader("Efficient frontier")
    sim = get_frontier(rets)
    ef = px.scatter(sim, x="Volatility", y="Return", color="Sharpe", opacity=0.6,
                    color_continuous_scale=["#D5DAD8", "#8C9895"])
    ef.update_traces(marker=dict(size=5))
    for label in ["Max Sharpe", "Min Variance", "Equal Weight"]:
        ef.add_trace(go.Scatter(
            x=[summary.loc[label, "Volatility"]], y=[summary.loc[label, "Expected Return"]],
            mode="markers", name=label,
            marker=dict(size=14, symbol="diamond", color=STRATEGY_COLORS[label],
                        line=dict(width=2, color="white"))))
    ef.add_trace(go.Scatter(x=[v_u], y=[r_u], mode="markers", name="Your portfolio",
                            marker=dict(size=13, symbol="circle", color=COLORS["ink"],
                                        line=dict(width=2, color="white"))))
    ef.update_xaxes(tickformat=".0%")
    ef.update_yaxes(tickformat=".0%")
    ef.update_layout(coloraxis_colorbar=dict(thickness=12, title="Sharpe"))
    show(ef)

    st.subheader("Optimized weights")
    choice = st.radio("Portfolio", ["Max Sharpe", "Min Variance"], horizontal=True)
    stat_strip([
        ("Expected return", f"{summary.loc[choice, 'Expected Return']:.1%}", "Per year"),
        ("Volatility", f"{summary.loc[choice, 'Volatility']:.1%}", "Per year"),
        ("Sharpe ratio", f"{summary.loc[choice, 'Sharpe']:.2f}", "Risk-free rate 7%"),
    ])
    wsel = (w_sharpe if choice == "Max Sharpe" else w_minvar)
    wsel = wsel[wsel > 0.005].sort_values(ascending=False)
    wb = px.bar(x=wsel.values[::-1], y=wsel.index[::-1], orientation="h",
                text=[f"{v:.1%}" for v in wsel.values[::-1]],
                labels={"x": "Weight", "y": ""})
    wb.update_traces(marker_color=STRATEGY_COLORS[choice], textposition="outside")
    wb.update_xaxes(tickformat=".0%")
    show(wb)

# ----- Backtest -----
results = None
with tab_bt:
    st.subheader("Walk-forward backtest")
    st.caption("At each rebalance the optimizer sees only past data, then holds its weights on data it has not seen.")
    b1, b2, b3 = st.columns(3)
    lookback = b1.selectbox("Lookback (trading days)", [126, 252, 504], index=1)
    rebalance = b2.selectbox("Rebalance every (trading days)", [21, 63, 126], index=1)
    cost_bps = b3.number_input("Transaction cost (basis points)", 0, 50, 10)

    if len(rets) <= lookback + rebalance:
        st.warning("There is not enough history for these settings. Use an earlier start date or a shorter lookback.")
    else:
        stage(0.70, "Running the walk-forward backtest")
        results = run_backtests(rets, max_w, lookback, rebalance, cost_bps / 10000)
        bench = load_benchmark(str(start), str(end)).pct_change().dropna()
        bench.index = pd.to_datetime(bench.index).tz_localize(None)
        results["Nifty 50 Index"] = bench.reindex(results.index)
        results = results.dropna()

        perf = perf_table(results)
        note("Key takeaways", takeaways(perf))

        bt = px.line((1 + results).cumprod() * 100, color_discrete_map=STRATEGY_COLORS,
                     labels={"value": "Value of ₹100", "index": "", "variable": ""})
        bt.for_each_trace(lambda t: t.update(line=dict(dash="dot", width=2))
                          if t.name == "Nifty 50 Index" else None)
        bt.update_layout(hovermode="x unified")
        bt.update_yaxes(tickprefix="₹")
        range_buttons(bt)
        mark_crashes(bt, results.index)
        show(bt)

        st.dataframe(perf.style.format({
            "Return (CAGR)": "{:.1%}", "Volatility": "{:.1%}",
            "Sharpe": "{:.2f}", "Max Drawdown": "{:.1%}"}), width="stretch")
        st.download_button("Download backtest results", perf.to_csv().encode(),
                           "backtest_results.csv", "text/csv")

# ----- Stress test -----
with tab_stress:
    st.subheader("Stress test")
    st.caption("Total return of each strategy, tested out of sample, during two market crashes.")
    if results is None:
        st.info("Set up the backtest first. See the Backtest tab.")
    else:
        stress_rows = {}
        for label, (s, e) in CRISES.items():
            window = results.loc[s:e]
            if len(window) < 20:
                stress_rows[label] = {c: np.nan for c in results.columns}
            else:
                stress_rows[label] = ((1 + window).prod() - 1).to_dict()
        stress = pd.DataFrame(stress_rows).T

        if stress.isna().all().all():
            st.info("The backtest period does not cover these crashes. Use an earlier start date or a shorter lookback.")
        else:
            st.dataframe(stress.style.format("{:.1%}", na_rep="n/a"), width="stretch")
            sb = px.bar(stress, barmode="group", color_discrete_map=STRATEGY_COLORS,
                        labels={"value": "Total return", "index": "", "variable": ""})
            sb.update_yaxes(tickformat=".0%")
            show(sb)

# ---------- Finish ----------
if first_run:
    show_loading(loader, 1.0, "Done")
    time.sleep(0.5)
loader.empty()
st.session_state["loaded"] = True
footer()