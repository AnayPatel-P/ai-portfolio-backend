from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from data_loader import fetch_price_data, calculate_return_stats
from optimizer import optimize_portfolio

app = FastAPI()

# Enable CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class OptimizeRequest(BaseModel):
    risk_level: str
    tickers: List[str]

# --- Portfolio Optimizer Endpoint ---
@app.post("/optimize")
def optimize(req: OptimizeRequest):
    prices = fetch_price_data(req.tickers)
    result = optimize_portfolio(prices, req.risk_level)

    # Normalize price history
    normalized = prices / prices.iloc[0]
    normalized = normalized.reset_index()
    normalized["Date"] = normalized["Date"].dt.strftime("%Y-%m-%d")
    history_dict = normalized.to_dict(orient="records")

    return {
        **result,
        "price_history": history_dict
    }

# --- Recommended Portfolio Endpoint ---
@app.get("/recommend")
def recommend_portfolio(risk_level: str):
    candidate_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'JNJ', 'XOM',
        'JPM', 'NVDA', 'PG', 'TSLA', 'UNH', 'HD', 'BAC', 'V'
    ]
    prices = fetch_price_data(candidate_tickers)
    stats = calculate_return_stats(prices)
    ranked = stats["annualized_returns"].sort_values(ascending=False)

    if risk_level == "low":
        recommended = ranked.tail(5).index.tolist()
    elif risk_level == "medium":
        recommended = ranked.iloc[5:10].index.tolist()
    else:  # high
        recommended = ranked.head(5).index.tolist()

    # Cross-reference with optimizer
    optimization_result = optimize_portfolio(prices[recommended], risk_level)
    weights = optimization_result["weights"]
    nonzero_recommendations = [ticker for ticker in recommended if weights.get(ticker, 0) > 0]

    return {"tickers": nonzero_recommendations}
