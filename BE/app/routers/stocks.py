from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, stock_service
from ..database import get_db

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
)

@router.get("/{symbol}/history", response_model=List[schemas.StockPrice])
def read_stock_history(symbol: str, days: int = 30, db: Session = Depends(get_db)):
    """
    Get stock history for a specific symbol.
    Fetches latest data from external API before returning.
    """
    # 1. Ensure data is up-to-date
    # We fetch slightly more data than requested to be safe, or just fetch recent data.
    # For simplicity, let's fetch '1mo' if days <= 30, else '3mo', '1y' etc.
    # Or just fetch '1mo' always to update recent prices.
    period = "1mo"
    if days > 30:
        period = "3mo" # Adjust as needed
    if days > 90:
        period = "1y"
        
    stock_service.fetch_and_save_historical_data(db, symbol, period=period)
    
    # 2. Query DB
    prices = crud.get_stock_prices(db, symbol=symbol, days=days)
    
    if not prices:
        # If still empty after fetch, maybe symbol is invalid
        raise HTTPException(status_code=404, detail="Stock data not found")
        
    return prices

