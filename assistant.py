import pandas as pd
import streamlit as st
import plotly.express as px

from analyst import (resolve_universe, detect_start, compute_result, explain,
                     ai_available, model_name, MAX_AI_CALLS)
from style import masthead, show, footer, COLORS

st.session_state.setdefault("chat", [])
st.session_state.setdefault("ai_calls", 0)

masthead("Assistant", "Ask about any Nifty 50 stock. It runs the analysis and explains what it finds.")

if ai_available():
    st.caption("Explanations are written by an AI model from numbers the dashboard calculates. "
               "Not investment advice.")
else:
    st.caption("The analysis is calculated live from daily price data. Not investment advice.")

FORMATS = {"Last close": "{:,.2f}", "1-day": "{:+.1%}", "1-year": "{:+.1%}", "Return (CAGR)": "{:.1%}",
           "Volatility": "{:.1%}", "Sharpe": "{:.2f}", "Max Drawdown": "{:.1%}",
           "From 52-week high": "{:.1%}", "Beta vs Nifty": "{:.2f}"}

def build_visuals(result, mode):
    # The analysis the assistant ran: a table, plus a chart suited to the question
    table = result["table"].sort_values("Sharpe", ascending=False)
    fig = None
    if mode == "screen":
        top = table.head(12).iloc[::-1]
        fig = px.bar(x=top["Sharpe"], y=top.index, orientation="h", labels={"x": "Sharpe ratio", "y": ""})
        fig.update_traces(marker_color=COLORS["accent"])
        table = table.head(8)
    else:
        prices = result["prices"]
        fig = px.line(prices / prices.iloc[0] * 100,
                      labels={"value": "Value of ₹100", "index": "", "variable": ""})
        fig.update_yaxes(tickprefix="₹")
        fig.update_layout(hovermode="x unified" if prices.shape[1] <= 8 else "closest")
    return table, fig

def render(m):
    st.markdown(m["text"])
    if m.get("note"):
        st.caption(m["note"])
    if m.get("table") is not None:
        st.dataframe(m["table"].style.format(FORMATS, na_rep="n/a"), width="stretch")
    if m.get("fig") is not None:
        show(m["fig"])

# ---------- Conversation so far ----------
for m in st.session_state["chat"]:
    with st.chat_message(m["role"], avatar=":material/person:" if m["role"] == "user" else ":material/insights:"):
        render(m)

# ---------- Starter questions ----------
STARTERS = ["Analyse TCS and Infosys", "Compare HDFC Bank and ICICI Bank",
            "Which stocks have the best Sharpe ratio?"]
if not st.session_state["chat"]:
    st.markdown("**Try one of these**")
    cols = st.columns(len(STARTERS))
    for col, text in zip(cols, STARTERS):
        if col.button(text, width="stretch"):
            st.session_state["queued"] = text
            st.rerun()

prompt = st.chat_input("Ask about a stock, for example: analyse Reliance and ITC") or st.session_state.pop("queued", None)

# ---------- A new question ----------
if prompt:
    prompt = prompt.strip()[:400]
    history = [{"role": m["role"], "text": m["text"]} for m in st.session_state["chat"]]
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/insights:"):
        result, table, fig, note = None, None, None, ""
        with st.status("Working on it", expanded=True) as status:
            names, mode, label = resolve_universe(prompt)
            if names:
                shown = ", ".join(names) if len(names) <= 8 else f"all {len(names)} stocks"
                st.write(f"Stocks found: {shown}")
                start = detect_start(prompt)
                st.write(f"Downloading prices from {start:%b %Y}")
                try:
                    result = compute_result(names, start)
                except Exception:
                    result = None
                if result is None:
                    st.write("Could not get enough price data for that request.")
                else:
                    st.write("Calculating return, risk, drawdown, beta and correlation")
                    table, fig = build_visuals(result, mode)
            else:
                st.write("No stock named, so I will answer the question directly.")
            st.write("Writing the explanation")
            allow_ai = st.session_state["ai_calls"] < MAX_AI_CALLS
            text, source, note = explain(prompt, result, mode, label, history, allow_ai)
            if source == "ai":
                st.session_state["ai_calls"] += 1
            if names and result is None:
                text = ("I could not get enough price data for that. Try different stocks, "
                        "a longer period, or ask again in a moment.")
            status.update(label="Analysis complete", state="complete", expanded=False)

        msg = {"role": "assistant", "text": text, "note": note, "table": table, "fig": fig}
        render(msg)

    st.session_state["chat"].append({"role": "user", "text": prompt})
    st.session_state["chat"].append(msg)

if st.session_state["chat"]:
    if st.button("Clear conversation"):
        st.session_state["chat"] = []
        st.rerun()
    if ai_available():
        st.caption(f"AI explanations used this session: {st.session_state['ai_calls']} of {MAX_AI_CALLS}. "
                   f"Model: {model_name()}.")

footer()