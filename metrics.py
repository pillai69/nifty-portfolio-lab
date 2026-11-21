from scipy.optimize import minimize
import numpy as np
from scipy.optimize import minimize
import pandas as pd

TRADING_DAYS = 252      # trading days in a year
RISK_FREE = 0.07        # assumed 7% risk-free rate (approx. Indian G-sec yield)

def daily_returns(prices):
    # % change from one day to the next
    return prices.pct_change().dropna()

def annual_return(returns):
    # CAGR: compound growth rate, annualised
    return (1 + returns).prod() ** (TRADING_DAYS / len(returns)) - 1

def annual_vol(returns):
    # Volatility: std dev of daily returns, scaled to a year
    return returns.std() * np.sqrt(TRADING_DAYS)

def sharpe(returns, rf=RISK_FREE):
    # Return earned per unit of risk, above the risk-free rate
    return (annual_return(returns) - rf) / annual_vol(returns)

def max_drawdown(prices):
    # Worst fall from a previous peak
    return (prices / prices.cummax() - 1).min()

def summary_table(prices):
    r = daily_returns(prices)
    return pd.DataFrame({
        "Return (CAGR)": annual_return(r),
        "Volatility": annual_vol(r),
        "Sharpe": sharpe(r),
        "Max Drawdown": max_drawdown(prices),
    })
def portfolio_stats(weights, mean_ret, cov):
    # Expected return and volatility of a portfolio with given weights
    ret = np.dot(weights, mean_ret)
    vol = np.sqrt(weights @ cov @ weights)
    return ret, vol

def optimize(returns, objective="sharpe", max_weight=0.30):
    # Finds the weights that maximise Sharpe or minimise variance.
    # Long-only (no shorting), weights sum to 100%, capped per stock.
    mean_ret = (returns.mean() * TRADING_DAYS).values
    cov = (returns.cov() * TRADING_DAYS).values
    n = len(mean_ret)

    def neg_sharpe(w):
        r, v = portfolio_stats(w, mean_ret, cov)
        return -(r - RISK_FREE) / v

    def variance(w):
        return w @ cov @ w

    result = minimize(
        neg_sharpe if objective == "sharpe" else variance,
        x0=np.ones(n) / n,                                   # start from equal weights
        method="SLSQP",
        bounds=[(0, max_weight)] * n,                        # each weight between 0 and the cap
        constraints={"type": "eq", "fun": lambda w: w.sum() - 1},  # weights add up to 100%
    )
    return pd.Series(result.x, index=returns.columns)

def random_portfolios(returns, n=5000, seed=42):
    # Thousands of random portfolios; their cloud shows the efficient frontier
    rng = np.random.default_rng(seed)
    mean_ret = (returns.mean() * TRADING_DAYS).values
    cov = (returns.cov() * TRADING_DAYS).values
    W = rng.dirichlet(np.ones(len(mean_ret)), n)
    rets = W @ mean_ret
    vols = np.sqrt(np.einsum("ij,jk,ik->i", W, cov, W))
    return pd.DataFrame({"Return": rets, "Volatility": vols,
                         "Sharpe": (rets - RISK_FREE) / vols})

def var_cvar(port_returns, level=0.95):
    # VaR: the 1-day loss that is exceeded only 5% of the time
    # CVaR: the average loss on those worst 5% of days
    var = np.percentile(port_returns, (1 - level) * 100)
    cvar = port_returns[port_returns <= var].mean()
    return var, cvar