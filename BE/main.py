from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import numpy as np

import config
from database import get_db, init_db, TechnicalIndicator, InvestmentRecord, Portfolio, StockPrice
from models import (
    MarketDataInput, ModelPredictionResponse, PortfolioCapitalRequest,
    PortfolioCapitalResponse, InvestmentHistoryQuery, InvestmentRecordResponse,
    PerformanceMetrics, IndicatorHistoryQuery, HealthCheckResponse, ModelStatusResponse,
    ModelInfo, ModelListResponse
)
from gpt_service import interpret_model_output
from model_loader import model_loader
from stock_data_fetcher import stock_fetcher

app = FastAPI(title="AI Trading Backend", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 시작 시 DB 초기화 및 모델 로드
@app.on_event("startup")
async def startup_event():
    init_db()
    model_loader.load_marl_model()
    model_loader.load_model_2()
    model_loader.load_model_3()

# API 키 인증
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not config.API_KEY:
        return True
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

@app.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """헬스 체크"""
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return HealthCheckResponse(
        status="ok",
        database=db_status,
        timestamp=datetime.utcnow()
    )

@app.get("/models/status", response_model=ModelStatusResponse)
async def get_models_status(authenticated: bool = Depends(verify_api_key)):
    """모델 상태 확인"""
    status = model_loader.get_model_status()
    return ModelStatusResponse(**status)

@app.get("/models/list", response_model=ModelListResponse)
async def get_models_list(authenticated: bool = Depends(verify_api_key)):
    """사용 가능한 모델 목록 조회 (FE에서 선택 UI용)"""
    status = model_loader.get_model_status()
    
    models = [
        ModelInfo(
            id="marl_4agent",
            name="MARL 4-Agent",
            description="4개 에이전트 기반 멀티 에이전트 강화학습 모델 (단기/장기/위험/감성)",
            endpoint="/predict/marl",
            status=status["marl_4agent"]
        ),
        ModelInfo(
            id="model_2",
            name="Model 2",
            description="두 번째 AI 트레이딩 모델",
            endpoint="/predict/model2",
            status=status["model_2"]
        ),
        ModelInfo(
            id="model_3",
            name="Model 3",
            description="세 번째 AI 트레이딩 모델",
            endpoint="/predict/model3",
            status=status["model_3"]
        )
    ]
    
    return ModelListResponse(models=models)

@app.post("/predict/marl", response_model=ModelPredictionResponse)
async def predict_marl(
    data: MarketDataInput,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """MARL 4-agent 모델 예측 (XAI 포함)"""
    try:
        signal, vote_sum, indicators, xai_explanation, xai_importance = model_loader.predict_marl(data.features)
        
        # vote_sum을 confidence_score로 변환 (-4~4 -> 0.0~1.0)
        confidence = (abs(vote_sum) / 4.0) * 0.5 + 0.5
        
        # GPT 해석
        gpt_explanation = await interpret_model_output(signal, indicators)
        
        # 기술 지표 저장
        tech_indicator = TechnicalIndicator(
            symbol=data.symbol,
            sma20=indicators.get("SMA20"),
            macd=indicators.get("MACD"),
            macd_signal=indicators.get("MACD_Signal"),
            rsi=indicators.get("RSI"),
            stoch_k=indicators.get("Stoch_K"),
            stoch_d=indicators.get("Stoch_D"),
            atr=indicators.get("ATR"),
            bollinger_b=indicators.get("Bollinger_B"),
            vix=indicators.get("VIX"),
            roa=indicators.get("ROA"),
            debt_ratio=indicators.get("DebtRatio"),
            analyst_rating=indicators.get("AnalystRating")
        )
        db.add(tech_indicator)
        db.commit()
        
        return ModelPredictionResponse(
            model_type="marl_4agent",
            signal=signal,
            confidence_score=confidence,
            technical_indicators=indicators,
            gpt_explanation=gpt_explanation,
            xai_explanation=xai_explanation,
            xai_feature_importance=xai_importance,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/model2", response_model=ModelPredictionResponse)
async def predict_model2(
    data: MarketDataInput,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """Model 2 예측"""
    try:
        signal, confidence, indicators = model_loader.predict_model_2(data.features)
        gpt_explanation = await interpret_model_output(signal, indicators)
        
        return ModelPredictionResponse(
            model_type="model_2",
            signal=signal,
            confidence_score=confidence,
            technical_indicators=indicators,
            gpt_explanation=gpt_explanation,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/model3", response_model=ModelPredictionResponse)
async def predict_model3(
    data: MarketDataInput,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """Model 3 예측"""
    try:
        signal, confidence, indicators = model_loader.predict_model_3(symbol=data.symbol)
        gpt_explanation = await interpret_model_output(signal, indicators)
        
        return ModelPredictionResponse(
            model_type="model_3",
            signal=signal,
            confidence_score=confidence,
            technical_indicators=indicators,
            gpt_explanation=gpt_explanation,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/portfolio/capital", response_model=PortfolioCapitalResponse)
async def set_portfolio_capital(
    request: PortfolioCapitalRequest,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """포트폴리오 초기 자본 설정"""
    portfolio = db.query(Portfolio).filter(Portfolio.portfolio_id == request.portfolio_id).first()
    
    if portfolio:
        portfolio.initial_capital = request.initial_capital
        portfolio.current_capital = request.initial_capital
        portfolio.shares_held = 0
        portfolio.average_entry_price = 0.0
        portfolio.updated_at = datetime.utcnow()
    else:
        portfolio = Portfolio(
            portfolio_id=request.portfolio_id,
            initial_capital=request.initial_capital,
            current_capital=request.initial_capital,
            shares_held=0,
            average_entry_price=0.0
        )
        db.add(portfolio)
    
    db.commit()
    db.refresh(portfolio)
    
    return PortfolioCapitalResponse(
        portfolio_id=portfolio.portfolio_id,
        initial_capital=portfolio.initial_capital,
        current_capital=portfolio.current_capital,
        shares_held=portfolio.shares_held,
        average_entry_price=portfolio.average_entry_price,
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at
    )

@app.get("/portfolio/{portfolio_id}", response_model=PortfolioCapitalResponse)
async def get_portfolio(
    portfolio_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """포트폴리오 정보 조회"""
    portfolio = db.query(Portfolio).filter(Portfolio.portfolio_id == portfolio_id).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return PortfolioCapitalResponse(
        portfolio_id=portfolio.portfolio_id,
        initial_capital=portfolio.initial_capital,
        current_capital=portfolio.current_capital,
        shares_held=portfolio.shares_held,
        average_entry_price=portfolio.average_entry_price,
        created_at=portfolio.created_at,
        updated_at=portfolio.updated_at
    )

@app.post("/investment/record")
async def create_investment_record(
    portfolio_id: str,
    model_type: str,
    signal: str,
    entry_price: float,
    shares: int,
    portfolio_value: float,
    pnl: float,
    confidence_score: float,
    gpt_explanation: Optional[str] = None,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """투자 내역 기록"""
    record = InvestmentRecord(
        portfolio_id=portfolio_id,
        model_type=model_type,
        signal=signal,
        entry_price=entry_price,
        shares=shares,
        portfolio_value=portfolio_value,
        pnl=pnl,
        confidence_score=confidence_score,
        gpt_explanation=gpt_explanation
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {"id": record.id, "message": "Investment record created"}

@app.get("/investment/history", response_model=List[InvestmentRecordResponse])
async def get_investment_history(
    portfolio_id: Optional[str] = None,
    model_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """투자 내역 조회"""
    query = db.query(InvestmentRecord)
    
    if portfolio_id:
        query = query.filter(InvestmentRecord.portfolio_id == portfolio_id)
    if model_type:
        query = query.filter(InvestmentRecord.model_type == model_type)
    if start_date:
        query = query.filter(InvestmentRecord.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(InvestmentRecord.timestamp <= datetime.fromisoformat(end_date))
    
    query = query.order_by(InvestmentRecord.timestamp.desc())
    
    offset = (page - 1) * page_size
    records = query.offset(offset).limit(page_size).all()
    
    return [
        InvestmentRecordResponse(
            id=r.id,
            timestamp=r.timestamp,
            portfolio_id=r.portfolio_id,
            model_type=r.model_type,
            signal=r.signal,
            entry_price=r.entry_price,
            shares=r.shares,
            portfolio_value=r.portfolio_value,
            pnl=r.pnl,
            confidence_score=r.confidence_score,
            gpt_explanation=r.gpt_explanation
        )
        for r in records
    ]

@app.get("/investment/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(
    portfolio_id: Optional[str] = None,
    model_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """성과 지표 조회"""
    query = db.query(InvestmentRecord)
    
    if portfolio_id:
        query = query.filter(InvestmentRecord.portfolio_id == portfolio_id)
    if model_type:
        query = query.filter(InvestmentRecord.model_type == model_type)
    if start_date:
        query = query.filter(InvestmentRecord.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(InvestmentRecord.timestamp <= datetime.fromisoformat(end_date))
    
    records = query.all()
    
    if not records:
        return PerformanceMetrics(
            total_pnl=0.0,
            win_rate=0.0,
            sharpe_ratio=0.0,
            total_trades=0
        )
    
    total_pnl = sum(r.pnl for r in records)
    win_trades = sum(1 for r in records if r.pnl > 0)
    win_rate = (win_trades / len(records)) * 100 if records else 0.0
    
    pnls = np.array([r.pnl for r in records])
    sharpe_ratio = (pnls.mean() / (pnls.std() + 1e-9)) * np.sqrt(252) if len(pnls) > 1 else 0.0
    
    return PerformanceMetrics(
        total_pnl=total_pnl,
        win_rate=win_rate,
        sharpe_ratio=float(sharpe_ratio),
        total_trades=len(records)
    )

@app.get("/indicators/history")
async def get_indicator_history(
    symbol: str = "005930",
    indicator_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    aggregation: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """기술 지표 내역 조회"""
    query = db.query(TechnicalIndicator).filter(TechnicalIndicator.symbol == symbol)
    
    if start_date:
        query = query.filter(TechnicalIndicator.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(TechnicalIndicator.timestamp <= datetime.fromisoformat(end_date))
    
    query = query.order_by(TechnicalIndicator.timestamp.desc()).limit(min(limit, 1000))
    
    indicators = query.all()
    
    result = []
    for ind in indicators:
        data = {
            "timestamp": ind.timestamp.isoformat(),
            "symbol": ind.symbol,
            "SMA20": ind.sma20,
            "MACD": ind.macd,
            "MACD_Signal": ind.macd_signal,
            "RSI": ind.rsi,
            "Stoch_K": ind.stoch_k,
            "Stoch_D": ind.stoch_d,
            "ATR": ind.atr,
            "Bollinger_B": ind.bollinger_b,
            "VIX": ind.vix,
            "ROA": ind.roa,
            "DebtRatio": ind.debt_ratio,
            "AnalystRating": ind.analyst_rating
        }
        
        if indicator_name:
            data = {k: v for k, v in data.items() if k in ["timestamp", "symbol", indicator_name]}
        
        result.append(data)
    
    return result

@app.post("/stock/fetch")
async def fetch_stock_data(
    symbol: str = "005930.KS",
    period: str = "1mo",
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """
    yfinance로 주가 데이터를 가져와서 DB에 저장
    
    Args:
        symbol: 주식 심볼 (예: "005930.KS" for 삼성전자)
        period: 기간 ("1mo", "3mo", "6mo", "1y" 등)
    """
    result = stock_fetcher.fetch_and_save_stock_data(db, symbol, period)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

@app.get("/stock/prices")
async def get_stock_prices(
    symbol: str = "005930",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """
    DB에서 주가 데이터 조회
    
    Args:
        symbol: 주식 심볼
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
        limit: 최대 레코드 수
    """
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    prices = stock_fetcher.get_stock_prices(db, symbol, start, end, limit)
    
    return [
        {
            "date": price.date.isoformat(),
            "symbol": price.symbol,
            "open": price.open,
            "high": price.high,
            "low": price.low,
            "close": price.close,
            "volume": price.volume,
            "adj_close": price.adj_close
        }
        for price in prices
    ]

@app.get("/stock/latest")
async def get_latest_stock_price(
    symbol: str = "005930",
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    """
    가장 최근 주가 데이터 조회
    
    Args:
        symbol: 주식 심볼
    """
    price = stock_fetcher.get_latest_price(db, symbol)
    
    if not price:
        raise HTTPException(status_code=404, detail=f"No price data found for symbol: {symbol}")
    
    return {
        "date": price.date.isoformat(),
        "symbol": price.symbol,
        "open": price.open,
        "high": price.high,
        "low": price.low,
        "close": price.close,
        "volume": price.volume,
        "adj_close": price.adj_close
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
