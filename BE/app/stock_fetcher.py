import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional

def fetch_current_price(symbol: str) -> Optional[float]:
    """
    Fetches the current price of a stock.
    portfolio.py에서 이 함수를 직접 import해서 사용합니다.
    """
    try:
        # 한국 주식 심볼 보정 (숫자만 있으면 .KS 붙임)
        if symbol.isdigit():
            symbol = f"{symbol}.KS"
            
        ticker = yf.Ticker(symbol)
        
        # 1. Try fast_info first for real-time data
        price = ticker.fast_info.last_price
        
        # 2. Fallback to history if fast_info is not available or None
        if price is None or pd.isna(price):
            history = ticker.history(period="1d")
            if not history.empty:
                price = history["Close"].iloc[-1]
        
        return float(price) if price is not None else None
        
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return None

def fetch_historical_data(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical stock data.
    """
    try:
        if symbol.isdigit():
            symbol = f"{symbol}.KS"
            
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        return history
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """
    Fetches basic information about a stock.
    """
    try:
        if symbol.isdigit():
            symbol = f"{symbol}.KS"
            
        ticker = yf.Ticker(symbol)
        return ticker.info
    except Exception as e:
        print(f"Error fetching stock info for {symbol}: {e}")
        return {}