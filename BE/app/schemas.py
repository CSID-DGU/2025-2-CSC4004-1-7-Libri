from pydantic import BaseModel
from typing import List, Optional
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserInvestmentUpdate(BaseModel):
    investment_style: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
# 주식 추가 요청
class HoldingCreate(BaseModel):
    symbol: str
    quantity: int
    avg_price: float

# 주식 정보 응답 (수익률 포함)
class HoldingResponse(BaseModel):
    symbol: str
    quantity: int
    avg_price: float
    current_price: float = 0.0 # 현재가
    profit_rate: float = 0.0   # 수익률 (%)

    class Config:
        from_attributes = True

# 포트폴리오 전체 응답
class PortfolioResponse(BaseModel):
    id: int
    user_id: int
    current_capital: float # 예수금 (남은 돈)
    total_asset: float     # 총 자산 (예수금 + 주식 평가액)
    holdings: List[HoldingResponse] = []

    class Config:
        from_attributes = True

# 매도 요청용 스키마
class HoldingSell(BaseModel):
    symbol: str
    quantity: int
    sell_price: float # 얼마에 팔았는지 입력 (수익률 확정용)

# ---------------------------------------------------------------------
# 주가 데이터 스키마
# ---------------------------------------------------------------------
from datetime import datetime

class StockPriceBase(BaseModel):
    symbol: str
    date: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None

class StockPriceCreate(StockPriceBase):
    pass

class StockPrice(StockPriceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
class InvestmentRecordResponse(BaseModel):
    id: int
    timestamp: datetime
    portfolio_id: str
    model_type: str
    signal: str
    entry_price: float
    shares: int
    portfolio_value: float
    pnl: float | None = None
    confidence_score: float
    gpt_explanation: str | None = None

    class Config:
        from_attributes = True