import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional

def fetch_current_price(symbol: str) -> Optional[float]:
    """
    Fetches the current price of a stock.
    
    Args:
        symbol (str): The stock symbol (e.g., "005930.KS", "AAPL").
        
    Returns:
        float: The current price, or None if fetching fails.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Try fast_info first for real-time data
        price = ticker.fast_info.last_price
        if price is None:
             # Fallback to history if fast_info is not available
            history = ticker.history(period="1d")
            if not history.empty:
                price = history["Close"].iloc[-1]
        return price
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return None

def fetch_historical_data(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical stock data.
    
    Args:
        symbol (str): The stock symbol.
        period (str): The data period (e.g., "1d", "5d", "1mo", "1y", "max").
        interval (str): The data interval (e.g., "1m", "1h", "1d", "1wk", "1mo").
        
    Returns:
        pd.DataFrame: A DataFrame containing historical data (Open, High, Low, Close, Volume, etc.).
                      Returns empty DataFrame on failure.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        return history
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """
    Fetches basic information about a stock.
    
    Args:
        symbol (str): The stock symbol.
        
    Returns:
        dict: A dictionary containing stock info. Returns empty dict on failure.
    """
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except Exception as e:
        print(f"Error fetching stock info for {symbol}: {e}")
        return {}
