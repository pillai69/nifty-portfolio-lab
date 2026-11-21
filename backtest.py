import numpy as np
import pandas as pd
from metrics import optimize, annual_return, annual_vol, sharpe

def walk_forward(returns, objective, max_weight, lookback=252, rebalance=63, cost=0.001):
    # objective: "sharpe", "minvar" or "equal"
    # lookback: days of past data the optimizer may see
    # rebalance: days we hold the weights before re-optimizing
    # cost: transaction cost per 1.0 of turnover (0.001 = 0.1%)
    n = returns.shape[1]
    prev_w = None
    pieces = []
    for t in range(lookback, len(returns), rebalance):
        train = returns.iloc[t - lookback:t]       # the past: optimizer sees this
        test = returns.iloc[t:t + rebalance]       # the future: optimizer never sees this

        if objective == "equal":
            w = pd.Series(1 / n, index=returns.columns)
        else:
            w = optimize(train, objective, max_weight)

        # Turnover = how much of the portfolio we had to trade
        turnover = w.abs().sum() if prev_w is None else (w - prev_w).abs().sum()

        # Buy and hold the chosen weights through the test period
        value = (1 + test).cumprod().mul(w, axis=1).sum(axis=1)
        daily = value / value.shift(1).fillna(1.0) - 1
        daily.iloc[0] -= turnover * cost           # pay trading costs on rebalance day

        pieces.append(daily)
        prev_w = w
    return pd.concat(pieces)

def perf_table(returns_df):
    # returns_df: one column of daily returns per strategy
    growth = (1 + returns_df).cumprod()
    return pd.DataFrame({
        "Return (CAGR)": annual_return(returns_df),
        "Volatility": annual_vol(returns_df),
        "Sharpe": sharpe(returns_df),
        "Max Drawdown": (growth / growth.cummax() - 1).min(),
    })