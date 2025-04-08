from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from data_loader import fetch_price_data, calculate_return_stats, generate_recommended_tickers
from optimizer import optimize_portfolio

app = FastAPI()

# Enable CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Models ---
class OptimizeRequest(BaseModel):
    risk_level: str
    tickers: List[str]

# --- Optimize Portfolio Endpoint ---
@app.post("/optimize")
def optimize(req: OptimizeRequest):
    prices = fetch_price_data(req.tickers)
    result = optimize_portfolio(prices, req.risk_level)

    # Normalize price history for chart
    normalized = prices / prices.iloc[0]
    normalized = normalized.reset_index()
    normalized["Date"] = normalized["Date"].dt.strftime("%Y-%m-%d")
    history_dict = normalized.to_dict(orient="records")

    return {
        **result,
        "price_history": history_dict
    }

# --- Recommended Tickers Endpoint ---
@app.get("/recommend")
def recommend_portfolio(risk_level: str):
    candidate_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'JNJ', 'XOM',
        'JPM', 'NVDA', 'PG', 'TSLA', 'UNH', 'HD', 'BAC', 'V'
    ]
    recommended = generate_recommended_tickers(risk_level, candidate_tickers, top_n=10)
    return {"tickers": recommended}
