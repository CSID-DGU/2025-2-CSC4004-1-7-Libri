from pydantic import BaseModel
from typing import List, Optional
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    investment_style: str | None = "conservative"

class UserInvestmentUpdate(BaseModel):
    investment_style: str

class User(UserBase):
    id: int
    is_active: bool
    investment_style: str | None = None

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