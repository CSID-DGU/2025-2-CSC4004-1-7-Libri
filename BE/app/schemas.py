from pydantic import BaseModel
from typing import List, Optional
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    investment_style: str | None = "conservative"

class User(UserBase):
    id: int
    is_active: bool
    investment_style: str | None = None

    class Config:
        orm_mode = True
# 보유 주식 추가 요청용 (Request)
class HoldingCreate(BaseModel):
    stock_symbol: str
    quantity: int
    avg_price: float

# 보유 주식 응답용 (Response)
class HoldingResponse(BaseModel):
    stock_symbol: str
    quantity: int
    avg_price: float
    current_value: float = 0.0 # 현재 평가액
    profit_rate: float = 0.0   # 수익률

    class Config:
        from_attributes = True # or orm_mode = True (Pydantic 버전에 따라 다름)

# 포트폴리오 전체 요약 응답
class PortfolioResponse(BaseModel):
    id: int
    cash_balance: float
    total_asset: float = 0.0 # 총 자산 (현금 + 주식)
    holdings: List[HoldingResponse] = []

    class Config:
        from_attributes = True