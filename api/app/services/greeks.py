# app/services/greeks.py
import numpy as np
from scipy.stats import norm

def compute_greeks(S, K, T, r, sigma, call=True):
    """
    S: underlying price ($ per share)
    K: strike price ($ per share)
    T: time to expiration
    sigma: volatility
    r: continuously compounded risk_free interest rate
    call: true = call, false = put

    Greeks
    delta: sensitivity of option price to $1 move in S
    gamma: sensitivity of delta to $1 move in S
    vega: price change for 1% increase in sigma
    rho: price change for 1% rise in r
    theta: daily time decay of option's value. negative for long ones
    """
    if T <= 0 or sigma <= 0:
        zero = dict(delta = 0, gamma = 0, theta = 0, vega = 0, rho = 0)

    d1 = (np.log(S/K) + T * (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    delta = norm.cdf(d1) if call else norm.cdf(d1) - 1
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (-(S.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if call else -d2)) / 365.0
    vega = 0.01 * S * norm.pdf(d1) * np.sqrt(T)
    rho = K * T * np.exp(-r * T) * norm.cdf(d1 if call else -d2)

    return dict(delta = delta, gamma = gamma, theta = theta, vega = vega, rho = rho)