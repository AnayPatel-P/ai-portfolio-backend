import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns

def optimize_portfolio(price_df, risk_level="medium"):
    mu = expected_returns.mean_historical_return(price_df)
    S = risk_models.sample_cov(price_df)

    ef = EfficientFrontier(mu, S)

    # Enforce that all tickers get at least a small allocation (optional)
    min_allocation = 0.05
    ef.add_constraint(lambda w: w >= min_allocation)

    # Set risk preference (after adding constraints)
    if risk_level == "low":
        weights = ef.efficient_risk(target_volatility=0.10)
    elif risk_level == "medium":
        weights = ef.efficient_risk(target_volatility=0.15)
    else:
        weights = ef.max_sharpe()

    cleaned_weights = ef.clean_weights()
    performance = ef.portfolio_performance(verbose=False)

    return {
        "weights": cleaned_weights,
        "expected_return": performance[0],
        "expected_volatility": performance[1],
        "sharpe_ratio": performance[2],
    }

def export_weights_to_csv(weights_dict, filename="optimized_weights.csv"):
    df = pd.DataFrame(list(weights_dict.items()), columns=["Ticker", "Weight"])
    df["Weight"] = (df["Weight"] * 100).round(2)
    df.to_csv(filename, index=False)
    print(f"[INFO] Exported optimized weights to '{filename}'")
