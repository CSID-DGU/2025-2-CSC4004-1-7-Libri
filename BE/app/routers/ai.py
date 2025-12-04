from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Literal
from pydantic import BaseModel

# 상대 경로 기준: app/routers/ai.py → app/ai_wrapper.py
from ..ai_wrapper import a2c_wrapper, marl_wrapper, ai_service


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)


# ---------------------------
# 1) 히스토리/디버깅용 모델들
# ---------------------------

class HistoricalSignal(BaseModel):
    date: str
    signal: int
    daily_return: float
    strategy_return: float


class DailyPrediction(BaseModel):
    """
    /ai/signal 에서 사용하는 응답 스키마
    (기존 A2C/MARL predict_today() 결과 포맷)
    """
    date: str
    action: int
    action_str: Optional[str] = None   # MARL에서만 사용
    probs: Optional[List[float]] = None
    joint_action: Optional[List[int]] = None


# ---------------------------
# 2) 최종 /ai/predict 스펙
# ---------------------------

class AIPredictRequest(BaseModel):
    """
    프론트에서 보내는 요청 바디
    """
    symbol: str = "005930.KS"
    mode: Literal["a2c", "marl"] = "a2c"
    investment_style: Literal["aggressive", "conservative"] = "aggressive"


class AIPredictResponse(BaseModel):
    """
    백엔드_api.pdf 7~8페이지에 맞춰:
    - 오늘의 추천 행동
    - 승률
    - 설명
    등을 포함하는 응답 포맷
    """
    symbol: str
    model: str
    date: str
    action: str           # "BUY" / "SELL" / "HOLD"
    action_ko: str        # "매수" / "매도" / "관망"
    confidence: float     # 0.0 ~ 1.0
    win_rate: float       # 0.0 ~ 1.0
    investment_style: str
    indicators: List[str] = []
    xai_features: List[dict] = [] # Top 3 중요 지표 (XAI)
    explanation: str


# --------------------------------
# GET /ai/history  (기존 기능 유지)
# --------------------------------

@router.get("/history", response_model=List[HistoricalSignal])
def get_history(
    model_type: str = Query(..., description="Model type: 'a2c' or 'marl'"),
    start_date: str = Query("2025-10-01", description="Start date (YYYY-MM-DD)")
):
    """
    A2C / MARL 모델의 과거 시그널 & 전략 수익률 조회 (디버깅/분석용)
    """
    model_type = model_type.lower()
    if model_type == "a2c":
        return a2c_wrapper.get_historical_signals(start_date)
    elif model_type == "marl":
        return marl_wrapper.get_historical_signals(start_date)
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid model_type. Use 'a2c' or 'marl'.",
        )


# --------------------------------
# GET /ai/signal  (디버깅용 엔드포인트)
# --------------------------------

@router.get("/signal", response_model=DailyPrediction)
def get_today_signal(
    model_type: str = Query(..., description="Model type: 'a2c' or 'marl'")
):
    """
    모델 원본 출력 형식을 그대로 보고 싶을 때 사용하는 디버깅용 API.
    - A2C: date, action(int), probs
    - MARL: date, action(int), action_str, joint_action
    """
    model_type = model_type.lower()

    if model_type == "a2c":
        result = a2c_wrapper.predict_today()
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to get A2C prediction")

    elif model_type == "marl":
        result = marl_wrapper.predict_today()
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to get MARL prediction")

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid model_type. Use 'a2c' or 'marl'.",
        )


# --------------------------------
# POST /ai/predict  (B 파트 핵심)
# --------------------------------

@router.post("/predict", response_model=AIPredictResponse)
def predict(req: AIPredictRequest):
    """
    프론트엔드에서 실제로 사용할 메인 AI API.

    - Request Body:
        {
          "symbol": "005930.KS",
          "mode": "a2c",
          "investment_style": "aggressive"
        }

    - Response:
        {
          "symbol": "005930.KS",
          "model": "a2c",
          "date": "2025-12-04",
          "action": "BUY",
          "action_ko": "매수",
          "confidence": 0.78,
          "win_rate": 0.62,
          "investment_style": "aggressive",
          "indicators": [...],
          "xai_features": [...],
          "explanation": "..."
        }
    """
    result = ai_service.predict_today(
        symbol=req.symbol,
        mode=req.mode,
        investment_style=req.investment_style,
    )

    # ai_service.predict_today()는 내부에서 에러가 나도
    # 기본 HOLD 응답을 리턴하도록 구현했으므로,
    # 여기서는 보통 그대로 내려주면 된다.
    if not result:
        raise HTTPException(status_code=500, detail="Failed to get AI prediction")

    return result