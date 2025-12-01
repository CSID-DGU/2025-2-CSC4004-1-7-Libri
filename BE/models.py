from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class MarketDataInput(BaseModel):
    symbol: str = Field(default="005930", description="Stock symbol")
    # ✅ 수정: 기본값을 빈 dict로
    features: Dict[str, float] = Field(
        default_factory=dict,
        description="(선택) 프론트에서 계산한 지표; 비워두면 백엔드에서 계산"
    )
    
class ModelPredictionResponse(BaseModel):
    model_type: str
    signal: str
    confidence_score: float
    technical_indicators: Dict[str, float]
    gpt_explanation: Optional[str] = None
    xai_explanation: Optional[str] = None
    xai_feature_importance: Optional[List[Dict[str, float]]] = None
    timestamp: datetime

class PortfolioCapitalRequest(BaseModel):
    portfolio_id: str
    initial_capital: float = Field(gt=0, description="Initial capital must be greater than 0")

class PortfolioCapitalResponse(BaseModel):
    portfolio_id: str
    initial_capital: float
    current_capital: float
    shares_held: int
    average_entry_price: float
    created_at: datetime
    updated_at: datetime

class InvestmentHistoryQuery(BaseModel):
    portfolio_id: Optional[str] = None
    model_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)

class InvestmentRecordResponse(BaseModel):
    id: int
    timestamp: datetime
    portfolio_id: str
    model_type: str
    signal: str
    entry_price: float
    shares: int
    portfolio_value: float
    pnl: float
    confidence_score: float
    gpt_explanation: Optional[str]

class PerformanceMetrics(BaseModel):
    total_pnl: float
    win_rate: float
    sharpe_ratio: float
    total_trades: int

class IndicatorHistoryQuery(BaseModel):
    symbol: str = "005930"
    indicator_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    aggregation: Optional[str] = Field(default=None, pattern="^(daily_avg|min|max)$")
    limit: int = Field(default=100, ge=1, le=1000)

class HealthCheckResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime

class ModelStatusResponse(BaseModel):
    marl_4agent: str
    model_2: str
    model_3: str

class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    endpoint: str
    status: str

class ModelListResponse(BaseModel):
    models: List[ModelInfo]

# [신규] 온보딩 완료 시 보낼 데이터 형식
class PortfolioSetupRequest(BaseModel):
    portfolio_id: str
    initial_capital: float
    investment_style: str  # 'aggressive', 'moderate', 'stable'
    
    # 삼성전자 보유 정보
    shares_held: int
    average_entry_price: float