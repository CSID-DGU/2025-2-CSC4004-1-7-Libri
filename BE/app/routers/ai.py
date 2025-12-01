from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from ..ai_wrapper import a2c_wrapper, marl_wrapper

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
    responses={404: {"description": "Not found"}},
)

class HistoricalSignal(BaseModel):
    date: str
    signal: int
    daily_return: float
    strategy_return: float

class DailyPrediction(BaseModel):
    date: str
    action: int
    action_str: Optional[str] = None
    probs: Optional[List[float]] = None
    joint_action: Optional[List[int]] = None

@router.get("/history", response_model=List[HistoricalSignal])
def get_history(
    model_type: str = Query(..., description="Model type: 'a2c' or 'marl'"),
    start_date: str = Query("2025-10-01", description="Start date (YYYY-MM-DD)")
):
    if model_type.lower() == "a2c":
        return a2c_wrapper.get_historical_signals(start_date)
    elif model_type.lower() == "marl":
        return marl_wrapper.get_historical_signals(start_date)
    else:
        raise HTTPException(status_code=400, detail="Invalid model_type. Use 'a2c' or 'marl'.")

@router.get("/signal", response_model=DailyPrediction)
def get_today_signal(
    model_type: str = Query(..., description="Model type: 'a2c' or 'marl'")
):
    if model_type.lower() == "a2c":
        result = a2c_wrapper.predict_today()
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to get A2C prediction")
    elif model_type.lower() == "marl":
        result = marl_wrapper.predict_today()
        if result:
            return result
        raise HTTPException(status_code=500, detail="Failed to get MARL prediction")
    else:
        raise HTTPException(status_code=400, detail="Invalid model_type. Use 'a2c' or 'marl'.")
