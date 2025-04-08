import yfinance as yf
import pandas as pd

def fetch_price_data(tickers, start_date="2020-01-01", end_date=None):
    print("[INFO] Fetching price data...")
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)

    # If downloading multiple tickers, data is multi-level; else it's single-level
    if isinstance(data.columns, pd.MultiIndex):
        data = data['Close']  # Use Close since auto_adjust=True already adjusts
    else:
        data = data.to_frame(name='Close')

    # Drop tickers that failed to download
    data = data.dropna(axis=1, how='all')
    print(f"[INFO] Downloaded data for {len(data.columns)} tickers.")
    return data

def calculate_return_stats(price_df, frequency="biweekly"):
    if frequency == "biweekly":
        # Resample to biweekly using last Friday of each 2-week period
        resampled = price_df.resample('2W-FRI').last()
        factor = 26  # 26 biweekly periods in a year
    else:
        resampled = price_df
        factor = 252  # Trading days in a year

    returns = resampled.pct_change().dropna()

    if returns.empty:
        raise ValueError("No valid return data after resampling.")

    annualized_returns = returns.mean() * factor
    annualized_volatility = returns.std() * (factor ** 0.5)
    cov_matrix = returns.cov() * factor

    return {
        f"{frequency}_returns": returns,
        "annualized_returns": annualized_returns,
        "annualized_volatility": annualized_volatility,
        "cov_matrix": cov_matrix
    }

def export_returns_to_csv(returns_df, filename="biweekly_returns.csv"):
    returns_df.index = returns_df.index.strftime('%Y-%m-%d')  # Format index as string dates
    returns_df.to_csv(filename)
    print(f"[INFO] Exported biweekly returns to '{filename}'")

def generate_recommended_tickers(risk_level: str, universe: list[str], top_n: int = 10):
    """
    Dynamically selects top N tickers from a universe based on annualized returns,
    tailored by risk level (low/medium/high).
    """
    price_data = fetch_price_data(universe)
    stats = calculate_return_stats(price_data)
    returns = stats["annualized_returns"]
    volatility = stats["annualized_volatility"]

    # Adjust based on risk level
    if risk_level == "low":
        score = returns / (volatility + 1e-6)  # risk-adjusted (Sharpe-like)
    elif risk_level == "medium":
        score = returns
    elif risk_level == "high":
        score = returns * volatility  # aggressive blend
    else:
        raise ValueError("Invalid risk level. Choose from low, medium, high.")

    recommended = score.sort_values(ascending=False).head(top_n).index.tolist()
    print(f"[INFO] Recommended tickers for {risk_level} risk: {recommended}")
    return recommended
