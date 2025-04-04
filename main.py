from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from data_loader import fetch_price_data
from optimizer import optimize_portfolio

app = FastAPI()

# Enable CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace with specific domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model expects a risk level and a list of tickers
class OptimizeRequest(BaseModel):
    risk_level: str
    tickers: List[str]

# POST endpoint for optimization
@app.post("/optimize")
def optimize(req: OptimizeRequest):
    prices = fetch_price_data(req.tickers)
    result = optimize_portfolio(prices, req.risk_level)

    # Convert price history DataFrame to dict (for JSON serialization)
    price_history = prices.reset_index()
    price_history["Date"] = price_history["Date"].dt.strftime("%Y-%m-%d")
    history_dict = price_history.to_dict(orient="records")

    return {
        **result,
        "price_history": history_dict
    }

