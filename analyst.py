import json
import re

import numpy as np
import pandas as pd
import requests
import streamlit as st

from data import NIFTY_STOCKS, load_prices, load_benchmark
from metrics import summary_table, daily_returns, optimize, RISK_FREE

MAX_AI_CALLS = 20  # AI explanations per visitor session, to protect the free quota

# ---------- Understanding the question ----------
ALIASES = {
    "hdfc bank": "HDFC Bank", "hdfcbank": "HDFC Bank", "hdfc": "HDFC Bank",
    "icici bank": "ICICI Bank", "icicibank": "ICICI Bank", "icici": "ICICI Bank",
    "infosys": "Infosys", "infy": "Infosys",
    "tcs": "TCS", "tata consultancy": "TCS",
    "reliance": "Reliance", "ril": "Reliance",
    "itc": "ITC",
    "hul": "HUL", "hindustan unilever": "HUL", "hindunilvr": "HUL",
    "sbi": "SBI", "state bank": "SBI",
    "bharti airtel": "Bharti Airtel", "airtel": "Bharti Airtel", "bhartiartl": "Bharti Airtel",
    "kotak bank": "Kotak Bank", "kotak mahindra": "Kotak Bank", "kotak": "Kotak Bank", "kotakbank": "Kotak Bank",
    "l&t": "L&T", "larsen": "L&T",
    "axis bank": "Axis Bank", "axisbank": "Axis Bank", "axis": "Axis Bank",
    "asian paints": "Asian Paints", "asianpaint": "Asian Paints",
    "maruti suzuki": "Maruti", "maruti": "Maruti",
    "sun pharma": "Sun Pharma", "sunpharma": "Sun Pharma",
    "titan": "Titan",
    "bajaj finance": "Bajaj Finance", "bajfinance": "Bajaj Finance", "bajaj": "Bajaj Finance",
    "nestle": "Nestle", "nestleind": "Nestle",
    "ntpc": "NTPC", "tata steel": "Tata Steel", "tatasteel": "Tata Steel",
    "wipro": "Wipro", "hcl tech": "HCL Tech", "hcltech": "HCL Tech", "hcl": "HCL Tech",
    "ongc": "ONGC", "coal india": "Coal India", "coalindia": "Coal India",
}
for _n in NIFTY_STOCKS:
    ALIASES.setdefault(_n.lower(), _n)

SECTORS = {
    "banking and finance": (["HDFC Bank", "ICICI Bank", "SBI", "Kotak Bank", "Axis Bank", "Bajaj Finance"],
                            r"\b(bank|banks|banking|financials?)\b"),
    "IT": (["TCS", "Infosys", "Wipro", "HCL Tech"],
           r"\b(it stocks|it sector|it companies|it shares|tech|technology|software)\b"),
    "defensive": (["HUL", "ITC", "Nestle", "Sun Pharma", "NTPC"],
                  r"\b(defensive|fmcg|consumer staples)\b"),
    "energy and metals": (["Reliance", "ONGC", "Coal India", "NTPC", "Tata Steel"],
                          r"\b(energy|oil|power|metals?|commodit\w+)\b"),
}
SCREEN = (r"\b(best|top|rank|ranking|screen|all stocks|every stock|all 24|nifty 50|which stocks?|"
          r"safest|riskiest|lowest risk|highest return)\b")

def find_stocks(text):
    # Stock names in the order the user mentioned them
    t = " " + text.lower() + " "
    hits = []
    for alias, name in sorted(ALIASES.items(), key=lambda kv: -len(kv[0])):
        pattern = r"(?<![a-z0-9&])" + re.escape(alias) + r"(?![a-z0-9&])"
        for m in list(re.finditer(pattern, t)):
            hits.append((m.start(), name))
            t = t[:m.start()] + " " * (m.end() - m.start()) + t[m.end():]
    found = []
    for _, name in sorted(hits):
        if name not in found:
            found.append(name)
    return found

def resolve_universe(text):
    # Returns (stock names, mode, label). Mode is named, sector or screen.
    stocks = find_stocks(text)
    if stocks:
        return stocks[:8], "named", ""
    t = text.lower()
    for label, (members, pattern) in SECTORS.items():
        if re.search(pattern, t):
            return members, "sector", label
    if re.search(SCREEN, t):
        return list(NIFTY_STOCKS), "screen", "all 24 stocks"
    return [], "none", ""

def detect_start(text):
    today = pd.Timestamp.today().normalize()
    t = text.lower()
    m = re.search(r"since\s+(20\d\d)", t)
    if m:
        return pd.Timestamp(year=min(int(m.group(1)), today.year - 1), month=1, day=1)
    m = re.search(r"(\d{1,2})\s*-?\s*(months?|mo|years?|yrs?|y)\b", t)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit.startswith("m"):
            return today - pd.DateOffset(months=min(max(n, 6), 120))
        return today - pd.DateOffset(years=min(max(n, 1), 10))
    if "last year" in t or "past year" in t:
        return today - pd.DateOffset(years=1)
    return today - pd.DateOffset(years=5)

# ---------- Running the analysis ----------
def _num(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None

def compute_result(names, start):
    end = pd.Timestamp.today().normalize()
    tick = {n: NIFTY_STOCKS[n].replace(".NS", "") for n in names}
    prices = load_prices(tuple(NIFTY_STOCKS[n] for n in names), str(start.date()), str(end.date()))
    if prices is None or prices.empty or len(prices) < 60:
        return None
    prices = prices.rename(columns={v: k for k, v in tick.items()})
    rets = daily_returns(prices)
    table = summary_table(prices)

    look = min(252, len(prices) - 1)
    extra = pd.DataFrame({
        "Last close": prices.iloc[-1],
        "1-day": prices.iloc[-1] / prices.iloc[-2] - 1,
        "1-year": prices.iloc[-1] / prices.iloc[-look - 1] - 1,
        "From 52-week high": prices.iloc[-1] / prices.iloc[-252:].max() - 1,
    })
    table = table.join(extra)

    beta = pd.Series(np.nan, index=prices.columns)
    try:
        b = load_benchmark(str(start.date()), str(end.date())).pct_change().dropna()
        b.index = pd.to_datetime(b.index).tz_localize(None)
        joined = rets.join(b.rename("__nifty__"), how="inner")
        var_b = joined["__nifty__"].var()
        beta = joined.drop(columns="__nifty__").apply(lambda c: c.cov(joined["__nifty__"]) / var_b)
    except Exception:
        pass
    table["Beta vs Nifty"] = beta

    n = prices.shape[1]
    corr_info = None
    if n > 1:
        corr = rets.corr()
        pairs = [(corr.iloc[i, j], corr.columns[i], corr.columns[j])
                 for i in range(n) for j in range(i + 1, n)]
        pairs.sort()
        corr_info = {"average": _num(np.mean([p[0] for p in pairs])),
                     "most_similar": [pairs[-1][1], pairs[-1][2], _num(pairs[-1][0])],
                     "least_similar": [pairs[0][1], pairs[0][2], _num(pairs[0][0])]}

    w_sharpe = w_minvar = None
    if 2 <= n <= 10 and len(rets) > 120:
        cap = min(1.0, max(0.5, 1.5 / n))
        w_sharpe = optimize(rets, "sharpe", cap)
        w_minvar = optimize(rets, "minvar", cap)

    stocks = []
    for name, row in table.iterrows():
        stocks.append({
            "name": name, "last_close": _num(row["Last close"]), "day_change": _num(row["1-day"]),
            "one_year_return": _num(row["1-year"]), "cagr": _num(row["Return (CAGR)"]),
            "volatility": _num(row["Volatility"]), "sharpe": _num(row["Sharpe"]),
            "max_drawdown": _num(row["Max Drawdown"]), "beta": _num(row["Beta vs Nifty"]),
            "from_52w_high": _num(row["From 52-week high"])})
    stocks.sort(key=lambda s: (s["sharpe"] is None, -(s["sharpe"] or 0)))

    facts = {
        "period": f"{prices.index[0]:%d %b %Y} to {prices.index[-1]:%d %b %Y}",
        "trading_days": int(len(prices)), "risk_free_rate": RISK_FREE, "stocks": stocks,
        "correlation": corr_info,
        "max_sharpe_mix": ({k: round(float(v), 3) for k, v in w_sharpe.items() if v > 0.01}
                           if w_sharpe is not None else None),
        "min_variance_mix": ({k: round(float(v), 3) for k, v in w_minvar.items() if v > 0.01}
                             if w_minvar is not None else None),
        "weight_cap": (cap if w_sharpe is not None else None),
    }
    return {"facts": facts, "table": table, "prices": prices}

# ---------- Explaining it without an AI (always works) ----------
def _pct(x, signed=False):
    return "n/a" if x is None else (f"{x:+.1%}" if signed else f"{x:.1%}")

def _sharpe_words(s):
    if s is None:
        return "not available"
    if s < 0:
        return "below the 7% risk-free rate, so the stock did not pay for the risk it carried"
    if s < 0.5:
        return "positive but modest"
    if s < 1:
        return "decent"
    return "strong"

def _beta_words(b):
    if b is None:
        return ""
    if b > 1.1:
        return f" Its beta of {b:.2f} means it tends to amplify market moves."
    if b < 0.9:
        return f" Its beta of {b:.2f} means it tends to move less than the market."
    return f" Its beta of {b:.2f} means it moves roughly in line with the market."

GLOSSARY = {
    "sharpe": "The Sharpe ratio is the return a stock earned above a risk-free investment (7% here), divided by its volatility. Higher means more reward per unit of risk. Below zero means it earned less than a safe investment.",
    "volatil": "Volatility is how much a price swings, measured as the standard deviation of daily returns scaled to a year. Higher volatility means a bumpier ride.",
    "drawdown": "Maximum drawdown is the worst fall from a previous peak to a later low. It shows the real pain an investor would have felt.",
    "cvar": "CVaR (expected shortfall) is the average loss on the worst 5% of days. It looks further into the tail than VaR.",
    "var": "Value at Risk (VaR) at 95% is the one-day loss that is exceeded on only 5% of days.",
    "beta": "Beta measures how much a stock moves compared with the Nifty 50. Above 1 means it amplifies market moves, below 1 means it moves less.",
    "correlation": "Correlation shows how closely two stocks move together. Stocks that do not move together reduce portfolio risk without reducing expected return.",
    "diversif": "Diversification means holding stocks that do not move together, which lowers portfolio risk without lowering expected return.",
    "cagr": "CAGR is the steady yearly growth rate that would turn the starting price into the ending price.",
    "frontier": "The efficient frontier is the set of portfolios that give the highest expected return for each level of risk.",
    "backtest": "A walk-forward backtest lets the optimizer see only past data, then holds its weights on data it has not seen, repeating through history.",
    "survivorship": "Survivorship bias means only looking at companies that are still around today, which makes past results look better than they were.",
}

HELP = ("I can analyse any of the 24 Nifty 50 stocks in this dashboard. Try asking something like "
        "\"Analyse TCS and Infosys\", \"Compare HDFC Bank and ICICI Bank over 3 years\", "
        "\"How risky are the banking stocks?\" or \"Which stocks have the best Sharpe ratio?\".")

def template_explain(question, result, mode, label):
    if result is None:
        t = question.lower()
        hits = [v for k, v in GLOSSARY.items() if k in t][:2]
        return "\n\n".join(hits + [HELP]) if hits else HELP

    f = result["facts"]
    S = f["stocks"]
    period = f["period"]
    out = []

    if len(S) == 1:
        s = S[0]
        out.append(f"**{s['name']}** over {period}: it grew {_pct(s['cagr'])} a year, with volatility of "
                   f"{_pct(s['volatility'])} and a worst peak-to-trough fall of {_pct(s['max_drawdown'])}.")
        out.append(f"Its Sharpe ratio is {s['sharpe']:.2f}, which is {_sharpe_words(s['sharpe'])}."
                   f"{_beta_words(s['beta'])}")
        out.append(f"The latest close was {s['last_close']:,.2f} ({_pct(s['day_change'], True)} on the day). "
                   f"Over the past year it moved {_pct(s['one_year_return'], True)}, and it sits "
                   f"{_pct(abs(s['from_52w_high']))} below its 52-week high.")
    elif mode == "screen":
        top = S[:3]
        calm = sorted(S, key=lambda s: s["volatility"] if s["volatility"] is not None else 9)[:3]
        deep = sorted(S, key=lambda s: s["max_drawdown"] if s["max_drawdown"] is not None else 0)[:3]
        out.append(f"I screened all {len(S)} stocks over {period}.")
        out.append("**Best risk-adjusted returns (Sharpe):** " +
                   ", ".join(f"{s['name']} ({s['sharpe']:.2f})" for s in top) + ".")
        out.append("**Calmest (lowest volatility):** " +
                   ", ".join(f"{s['name']} ({_pct(s['volatility'])})" for s in calm) + ".")
        out.append("**Deepest drawdowns:** " +
                   ", ".join(f"{s['name']} ({_pct(s['max_drawdown'])})" for s in deep) + ".")
    else:
        names_txt = ", ".join(s["name"] for s in S[:-1]) + f" and {S[-1]['name']}"
        head = f"I compared {names_txt} over {period}"
        head += f" (the {label} group)." if mode == "sector" else "."
        out.append(head)
        out.append("**By Sharpe ratio (best first):** " +
                   ", ".join(f"{s['name']} ({s['sharpe']:.2f})" for s in S) + ".")
        hi_ret = max(S, key=lambda s: s["cagr"] if s["cagr"] is not None else -9)
        lo_vol = min(S, key=lambda s: s["volatility"] if s["volatility"] is not None else 9)
        worst = min(S, key=lambda s: s["max_drawdown"] if s["max_drawdown"] is not None else 0)
        out.append(f"{hi_ret['name']} had the highest return ({_pct(hi_ret['cagr'])} a year), "
                   f"{lo_vol['name']} was the calmest ({_pct(lo_vol['volatility'])} volatility), and "
                   f"{worst['name']} suffered the deepest fall ({_pct(worst['max_drawdown'])}).")
        c = f["correlation"]
        if c and len(S) == 2:
            out.append(f"Their daily returns have a correlation of {c['average']:.2f}, so they "
                       f"{'move closely together' if c['average'] > 0.6 else 'diversify each other moderately' if c['average'] > 0.35 else 'diversify each other well'}.")
        elif c:
            level = "high" if c["average"] > 0.6 else "moderate" if c["average"] > 0.35 else "low"
            out.append(f"The stocks have {level} average correlation ({c['average']:.2f}). "
                       f"{c['most_similar'][0]} and {c['most_similar'][1]} move most alike "
                       f"({c['most_similar'][2]:.2f}); {c['least_similar'][0]} and {c['least_similar'][1]} "
                       f"are the best diversifiers of each other ({c['least_similar'][2]:.2f}).")
        if f["max_sharpe_mix"]:
            mix = ", ".join(f"{k} {v:.0%}" for k, v in sorted(f["max_sharpe_mix"].items(), key=lambda kv: -kv[1]))
            out.append(f"A max-Sharpe mix of these, capped at {f['weight_cap']:.0%} per stock, would hold {mix}. "
                       "This is fitted on past data, so treat it as an illustration, not a forecast.")
    out.append("This is based on historical daily prices and is not investment advice.")
    return "\n\n".join(out)

# ---------- Explaining it with a free AI model ----------
SYSTEM_PROMPT = (
    "You are the analyst inside Nifty Portfolio Lab, a student research dashboard for Nifty 50 stocks. "
    "Explain results in plain English for a smart beginner. Rules: use only the numbers in the DATA block; "
    "never invent prices, news or forecasts; do not give buy or sell advice or price targets, describe what "
    "the data shows instead; mention when a result is in-sample or based on a short history; keep it under "
    "220 words; use short paragraphs and at most one short list; no emojis; finish with one sentence on a "
    "limitation. If there is no DATA block, answer the question briefly and suggest asking about a specific stock."
)

def get_secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def ai_available():
    return bool(get_secret("LLM_API_KEY"))

def model_name():
    return get_secret("LLM_MODEL", "gemini-2.5-flash-lite")

def ask_llm(question, facts_json, history):
    # Works with any provider that offers an OpenAI-style chat endpoint
    key = get_secret("LLM_API_KEY")
    if not key:
        return None, "no key"
    base = get_secret("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history[-4:]:
        messages.append({"role": m["role"], "content": m["text"][:1200]})
    user = f"Question: {question[:400]}"
    if facts_json:
        user += f"\n\nDATA (computed by the dashboard):\n{facts_json}"
    messages.append({"role": "user", "content": user})
    try:
        r = requests.post(base.rstrip("/") + "/chat/completions",
                          headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                          json={"model": model_name(), "messages": messages, "temperature": 0.3, "max_tokens": 700},
                          timeout=40)
        if r.status_code == 429:
            return None, "rate limit"
        r.raise_for_status()
        text = (r.json()["choices"][0]["message"]["content"] or "").strip()
        return (text or None), ("" if text else "empty reply")
    except Exception as e:
        return None, type(e).__name__

def explain(question, result, mode, label, history, allow_ai):
    # Returns (text, source, note). Source is ai or builtin.
    facts_json = json.dumps(result["facts"]) if result else ""
    why = ""
    if allow_ai and ai_available():
        text, why = ask_llm(question, facts_json, history)
        if text:
            return text, "ai", ""
    note = ""
    if why and why != "no key":
        note = "The AI explanation was unavailable just now, so this is the built-in analysis."
    return template_explain(question, result, mode, label), "builtin", note