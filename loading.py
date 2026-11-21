import random
import streamlit as st

FACTS = [
    "Harry Markowitz published Modern Portfolio Theory in 1952 and won the Nobel Prize for it in 1990. The optimizer you built is based on his idea.",
    "The Sharpe ratio is named after William Sharpe, who shared that same 1990 Nobel Prize.",
    "Diversification is often called the only free lunch in finance: you can reduce risk without giving up expected return.",
    "The Bombay Stock Exchange was established in 1875, making it one of the oldest stock exchanges in Asia.",
    "The Nifty 50 index was launched in 1996 and tracks 50 of the largest companies listed on the NSE.",
    "In March 2020 the Nifty fell close to 40% from its January peak in about two months. That is the drawdown you see in the table.",
    "Volatility is multiplied by √252 to annualise it, because there are about 252 trading days in a year.",
    "Value at Risk (VaR) became famous in the 1990s when JP Morgan published its RiskMetrics system.",
    "Rule of 72: divide 72 by your annual return to estimate how many years it takes to double your money.",
    "Survivorship bias: in WWII, analysts wanted to armour the spots where returning planes were hit, until Abraham Wald pointed out the planes hit elsewhere never came back.",
]

def show_loading(slot, progress, message):
    # slot: an st.empty() placeholder; progress: 0.0 to 1.0
    with slot.container():
        st.markdown(f"### ⏳ {message}")
        st.progress(progress)
        st.info(f"💡 **Did you know?** {random.choice(FACTS)}")