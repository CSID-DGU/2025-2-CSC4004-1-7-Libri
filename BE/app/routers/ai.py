from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Literal, Dict, Any
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
    수정된 응답 포맷:
    - short_description 제거됨 (불필요)
    - xai_features 내부에 'explain' 필드가 포함되어 전달됨
    """
    symbol: str
    model: str
    date: str
    action: str           # "BUY" / "SELL" / "HOLD"
    action_ko: str        # "매수" / "매도" / "관망"
    investment_style: str
    xai_features: List[Dict[str, Any]] = []  # 지표별 설명('explain')이 포함된 리스트
    explanation: str      # 전체 종합 코멘트


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
# POST /ai/predict  (B 파트 메인 스펙)
# --------------------------------

@router.post("/predict", response_model=AIPredictResponse)
def predict(req: AIPredictRequest):
    """
    프론트엔드에서 실제로 사용할 메인 AI API.
    """
    result = ai_service.predict_today(
        symbol=req.symbol,
        mode=req.mode,
        investment_style=req.investment_style,
    )

    if not result:
        raise HTTPException(status_code=500, detail="Failed to get AI prediction")

    return result


# --------------------------------
# POST /ai/predict/{mode}
#  → 프론트 호환용 래거시 엔드포인트
# --------------------------------

@router.post("/predict/{mode}")
def legacy_predict(
    mode: str,
    payload: Dict[str, Any] = Body(...),
):
    """
    프론트엔드가 사용하는 옛날 형태의 예측 API를 위한 호환용 엔드포인트.
    """
    mode = mode.lower()
    if mode not in ("a2c", "marl"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode '{mode}'. Use 'a2c' or 'marl'.",
        )

    # 프론트에서 symbol을 "005930"만 보내는 경우 .KS 보정
    raw_symbol = payload.get("symbol", "005930.KS")
    if raw_symbol.isdigit():
        symbol = f"{raw_symbol}.KS"
    else:
        symbol = raw_symbol

    investment_style = payload.get("investment_style", "aggressive")

    result = ai_service.predict_today(
        symbol=symbol,
        mode=mode,
        investment_style=investment_style,
    )

    if not result:
        raise HTTPException(status_code=500, detail="Failed to get AI prediction")

    action_en = result.get("action", "HOLD")  # "BUY"/"SELL"/"HOLD"
    signal = action_en.lower()                # "buy"/"sell"/"hold"

    return {
        # 프론트 호환용 필드
        "signal": signal,
        "gpt_explanation": result.get("explanation", ""),
        # short_description 제거됨

        # 참고용: 원본 응답도 함께 포함 (디버깅/확장용)
        "symbol": result.get("symbol", symbol),
        "model": result.get("model", mode),
        "date": result.get("date"),
        "action": result.get("action"),
        "action_ko": result.get("action_ko"),
        "investment_style": result.get("investment_style", investment_style),
        "xai_features": result.get("xai_features", []),
    }