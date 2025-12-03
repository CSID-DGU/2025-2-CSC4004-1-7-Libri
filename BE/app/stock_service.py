from sqlalchemy.orm import Session
from . import crud, schemas, stock_fetcher
import pandas as pd
from datetime import datetime

def fetch_and_save_historical_data(db: Session, symbol: str, period: str = "1mo", interval: str = "1d"):
    """
    Fetches historical data for a symbol and saves it to the database.
    """
    # 1. Fetch data
    df = stock_fetcher.fetch_historical_data(symbol, period=period, interval=interval)
    
    # Check latest date in DB
    latest_date = crud.get_latest_stock_date(db, symbol)
    
    if df.empty:
        print(f"No data found for {symbol}")
        return 0

    # 2. Convert to list of schemas.StockPriceCreate
    stock_prices = []
    for index, row in df.iterrows():
        # yfinance returns index as Timestamp
        date_val = index.to_pydatetime() if isinstance(index, pd.Timestamp) else index
        # Normalize to naive datetime (remove timezone) to match DB
        if date_val.tzinfo is not None:
            date_val = date_val.replace(tzinfo=None)

        # Skip if data is not newer than latest_date
        if latest_date and date_val <= latest_date:
            continue

        
        # Check if data already exists (optional optimization: check max date in DB first)
        # For now, we rely on the fact that we are just inserting. 
        # Ideally, we should handle duplicates.
        
        sp = schemas.StockPriceCreate(
            symbol=symbol,
            date=date_val,
            open=row.get("Open"),
            high=row.get("High"),
            low=row.get("Low"),
            close=row.get("Close"),
            volume=row.get("Volume")
        )
        stock_prices.append(sp)

    # 3. Save to DB
    # Note: This might fail if unique constraint (symbol, date) exists and we try to insert duplicates.
    # We should probably check for existence or use upsert.
    # For this MVP, let's assume we are fetching new data or handling errors gracefully.
    
    try:
        count = crud.bulk_create_stock_prices(db, stock_prices)
        print(f"Saved {count} records for {symbol}")
        return count
    except Exception as e:
        print(f"Error saving stock prices: {e}")
        db.rollback()
        return 0
