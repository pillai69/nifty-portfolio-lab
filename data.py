import pandas as pd
import yfinance as yf
import pandas as pd
import streamlit as st

# Company name -> Yahoo Finance ticker (".NS" means NSE India)
NIFTY_STOCKS = {
    "Reliance": "RELIANCE.NS", "TCS": "TCS.NS", "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS", "ICICI Bank": "ICICIBANK.NS", "ITC": "ITC.NS",
    "HUL": "HINDUNILVR.NS", "SBI": "SBIN.NS", "Bharti Airtel": "BHARTIARTL.NS",
    "Kotak Bank": "KOTAKBANK.NS", "L&T": "LT.NS", "Axis Bank": "AXISBANK.NS",
    "Asian Paints": "ASIANPAINT.NS", "Maruti": "MARUTI.NS",
    "Sun Pharma": "SUNPHARMA.NS", "Titan": "TITAN.NS",
    "Bajaj Finance": "BAJFINANCE.NS", "Nestle": "NESTLEIND.NS",
    "NTPC": "NTPC.NS", "Tata Steel": "TATASTEEL.NS", "Wipro": "WIPRO.NS",
    "HCL Tech": "HCLTECH.NS", "ONGC": "ONGC.NS", "Coal India": "COALINDIA.NS",
}

@st.cache_data(ttl=3600)  # remember results for 1 hour so it doesn't re-download every click
def load_prices(tickers, start, end):
    data = yf.download(list(tickers), start=start, end=end,
                       auto_adjust=True, progress=False)["Close"]
    data = data.dropna(axis=1, how="all").ffill().dropna()
    data.columns = [c.replace(".NS", "") for c in data.columns]
    return data
@st.cache_data(ttl=3600)
def load_benchmark(start, end):
    # ^NSEI is the Nifty 50 index itself
    d = yf.download("^NSEI", start=start, end=end, auto_adjust=True, progress=False)["Close"]
    return d.squeeze().dropna()