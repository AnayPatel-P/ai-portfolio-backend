import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns

def optimize_portfolio(price_df, risk_level="medium"):
    mu = expected_returns.mean_historical_return(price_df)
    S = risk_models.sample_cov(price_df)

    ef = EfficientFrontier(mu, S)

    # Choose optimization based on risk preference
    try:
        if risk_level == "low":
            weights = ef.efficient_risk(target_volatility=0.10)
        elif risk_level == "medium":
            weights = ef.efficient_risk(target_volatility=0.15)
        else:
            weights = ef.max_sharpe()
    except ValueError as e:
        print("[ERROR] Optimization failed:", e)
        raise

    cleaned_weights = ef.clean_weights()
    performance = ef.portfolio_performance(verbose=False)

    return {
        "weights": cleaned_weights,
        "expected_return": performance[0],
        "expected_volatility": performance[1],
        "sharpe_ratio": performance[2],
    }
