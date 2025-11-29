# BE/models.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


# ----------------------------------------------------------
# 1) 기본 입력 / 예측 응답
# ----------------------------------------------------------
class MarketDataInput(BaseModel):
    symbol: str = Field(default="005930", description="Stock symbol (e.g., 삼성전자)")
    # 프론트에서 지표를 계산해서 넘길 수도 있고, 비워두면 백엔드에서 계산 가능
    features: Dict[str, float] = Field(
        default_factory=dict,
        description="(선택) 프론트에서 계산한 지표; 비워두면 백엔드에서 계산",
    )


class ModelPredictionResponse(BaseModel):
    model_type: str  # "stable" / "aggressive"
    signal: str      # "BUY" / "SELL" / "HOLD"
    confidence_score: float
    gpt_explanation: str
    top_indicators: Dict[str, float] = Field(
        default_factory=dict, description="상위 핵심 지표 (지표명 -> 값)"
    )
    feature_importance: Dict[str, float] = Field(
        default_factory=dict, description="지표 중요도 (지표명 -> 중요도 점수)"
    )


# ----------------------------------------------------------
# 2) 포트폴리오 / AI 거래 기록 / 성과
# ----------------------------------------------------------
class PortfolioCapitalRequest(BaseModel):
    portfolio_id: str
    initial_capital: float


class PortfolioCapitalResponse(BaseModel):
    portfolio_id: str
    initial_capital: float
    current_capital: float


class InvestmentRecordResponse(BaseModel):
    id: int
    portfolio_id: str
    model_type: str
    symbol: str
    signal: str
    entry_price: float
    shares: float
    pnl: float
    confidence_score: float
    executed_at: datetime
    gpt_explanation: Optional[str] = None


class InvestmentHistoryQuery(BaseModel):
    portfolio_id: Optional[str] = None
    model_type: Optional[str] = None  # "stable" / "aggressive"
    limit: int = 50


class PerformanceMetrics(BaseModel):
    total_pnl: float
    win_rate: float
    sharpe_ratio: float
    total_trades: int


# ----------------------------------------------------------
# 3) 지표/주가 조회용
# ----------------------------------------------------------
class IndicatorHistoryQuery(BaseModel):
    symbol: str = "005930"
    indicator_name: str = "macd"  # ex) "macd", "rsi", "bb_b"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class StockPriceResponse(BaseModel):
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


# ----------------------------------------------------------
# 4) 헬스체크 / 모델 상태
# ----------------------------------------------------------
class HealthCheckResponse(BaseModel):
    status: str
    db_ok: bool
    models: Dict[str, str]


class ModelStatusResponse(BaseModel):
    models: Dict[str, str]


class ModelInfo(BaseModel):
    name: str           # "안정형", "공격형"
    model_type: str     # "stable", "aggressive"
    description: str
    endpoint: str       # "/predict/stable", "/predict/aggressive"
    status: str         # "available", "unavailable"


class ModelListResponse(BaseModel):
    models: List[ModelInfo]


# ----------------------------------------------------------
# 5) 회원 / 온보딩 / 보유종목 (요구사항 대응)
# ----------------------------------------------------------
class UserInfo(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    onboarding_completed: bool
    investment_style: Optional[str] = None  # 'stable' / 'aggressive'


class GoogleAuthRequest(BaseModel):
    """
    FE에서 구글 로그인 완료 후, 백엔드에 주는 정보 형식.
    실제 프로덕션이면 id_token(JWT)를 넘겨서 검증하지만,
    이번 프로젝트에서는 email + google_id 정도로 단순화 가능.
    """
    google_id: Optional[str] = None
    email: str
    name: Optional[str] = None


class GoogleAuthResponse(BaseModel):
    is_new_user: bool
    needs_onboarding: bool
    user: UserInfo
    default_portfolio_id: Optional[str] = None


class OnboardingCompleteRequest(BaseModel):
    """
    온보딩 화면에서 최종 제출할 정보들.
    """
    user_id: int
    investment_style: str  # 'stable' or 'aggressive'
    initial_capital: float
    # 필요시 기간, 목적 등 추가 가능
    investment_horizon_months: Optional[int] = None


class OnboardingCompleteResponse(BaseModel):
    user: UserInfo
    portfolio_id: str


class HoldingUpsertRequest(BaseModel):
    """
    사용자의 포트폴리오에 특정 종목(예: 삼성전자)에 대한
    보유 수량 / 평균단가를 저장하거나 수정할 때 사용.
    """
    portfolio_id: str
    symbol: str = "005930"
    shares: float
    average_price: float


class HoldingResponse(BaseModel):
    portfolio_id: str
    symbol: str
    shares: float
    average_price: float


# ----------------------------------------------------------
# 6) 온보딩에서 사용했던 포트폴리오 세팅 (기존 구조 유지용)
# ----------------------------------------------------------
class PortfolioSetupRequest(BaseModel):
    portfolio_id: str
    initial_capital: float
    investment_style: str  # 'aggressive', 'moderate', 'stable'

    # 삼성전자 보유 정보
    shares_held: int
    average_entry_price: float