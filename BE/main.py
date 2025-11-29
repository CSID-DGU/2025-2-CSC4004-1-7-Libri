# BE/main.py

from typing import List, Dict, Optional

from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import API_KEY, CORS_ORIGINS
from database import (
    SessionLocal,
    init_db,
    get_db,
    User,
    Portfolio,
    PortfolioHolding,
    InvestmentRecord,
    TechnicalIndicator,
    StockPrice,
)
from model_loader import model_loader
from gpt_service import interpret_model_output
from models import (
    MarketDataInput,
    ModelPredictionResponse,
    ModelListResponse,
    ModelInfo,
    HealthCheckResponse,
    ModelStatusResponse,
    GoogleAuthRequest,
    GoogleAuthResponse,
    OnboardingCompleteRequest,
    OnboardingCompleteResponse,
    HoldingUpsertRequest,
    HoldingResponse,
    InvestmentHistoryQuery,
    InvestmentRecordResponse,
    PerformanceMetrics,
    StockPriceResponse,
)

# --------------------------------------------------------
# FastAPI 앱 설정
# --------------------------------------------------------
app = FastAPI(title="Libri AI Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------
# 공통 의존성
# --------------------------------------------------------
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )


# --------------------------------------------------------
# 이벤트 훅
# --------------------------------------------------------
@app.on_event("startup")
def on_startup():
    # DB 테이블 생성
    init_db()
    # 모델 로드
    model_loader.load_models()


# --------------------------------------------------------
# 헬스체크 / 모델 목록
# --------------------------------------------------------
@app.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        # 간단한 쿼리로 DB 연결 확인
        db.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False

    return HealthCheckResponse(
        status="ok",
        db_ok=db_ok,
        models=model_loader.get_model_status(),
    )


@app.get("/models/status", response_model=ModelStatusResponse)
def get_model_status():
    return ModelStatusResponse(models=model_loader.get_model_status())


@app.get("/models/list", response_model=ModelListResponse)
def get_model_list():
    status_map = model_loader.get_model_status()

    models: List[ModelInfo] = [
        ModelInfo(
            name="안정형 (marl_3agent)",
            model_type="stable",
            description="3-agent MARL 기반 안정형 전략",
            endpoint="/predict/stable",
            status=status_map.get("stable", "unavailable"),
        ),
        ModelInfo(
            name="공격형 (A2C)",
            model_type="aggressive",
            description="A2C 기반 공격형 전략",
            endpoint="/predict/aggressive",
            status=status_map.get("aggressive", "unavailable"),
        ),
    ]
    return ModelListResponse(models=models)


# --------------------------------------------------------
# 회원 / 온보딩
# --------------------------------------------------------
@app.post(
    "/auth/google",
    response_model=GoogleAuthResponse,
    dependencies=[Depends(verify_api_key)],
)
def google_auth(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    """
    FE에서 구글 로그인 완료 후 이메일/이름/구글ID를 백엔드로 넘기면,
    - 기존 회원이면: is_new_user=False
    - 신규면: 새 User 생성 후 is_new_user=True
    """
    user = db.query(User).filter(User.email == payload.email).first()

    is_new = False
    if user is None:
        user = User(
            email=payload.email,
            name=payload.name,
            google_id=payload.google_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True
    else:
        # 이름/구글ID 업데이트
        if payload.name and user.name != payload.name:
            user.name = payload.name
        if payload.google_id and user.google_id != payload.google_id:
            user.google_id = payload.google_id
        db.commit()
        db.refresh(user)

    # 기본 포트폴리오 (예: "user_{id}_default")를 하나 보장
    default_portfolio_id = f"user_{user.id}_default"
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.portfolio_id == default_portfolio_id)
        .first()
    )
    if portfolio is None:
        portfolio = Portfolio(
            portfolio_id=default_portfolio_id,
            user_id=user.id,
            initial_capital=0.0,
            current_capital=0.0,
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    needs_onboarding = not bool(user.onboarding_completed)

    return GoogleAuthResponse(
        is_new_user=is_new,
        needs_onboarding=needs_onboarding,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "onboarding_completed": bool(user.onboarding_completed),
            "investment_style": user.investment_style,
        },
        default_portfolio_id=default_portfolio_id,
    )


@app.post(
    "/onboarding/complete",
    response_model=OnboardingCompleteResponse,
    dependencies=[Depends(verify_api_key)],
)
def onboarding_complete(
    payload: OnboardingCompleteRequest,
    db: Session = Depends(get_db),
):
    """
    온보딩 화면에서 최종 제출 시 호출:
      - 투자 성향, 초기 자본 설정
      - 기본 포트폴리오 초기화
    """
    user = db.query(User).filter(User.id == payload.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    default_portfolio_id = f"user_{user.id}_default"
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.portfolio_id == default_portfolio_id)
        .first()
    )
    if portfolio is None:
        portfolio = Portfolio(
            portfolio_id=default_portfolio_id,
            user_id=user.id,
            initial_capital=payload.initial_capital,
            current_capital=payload.initial_capital,
        )
        db.add(portfolio)
    else:
        portfolio.initial_capital = payload.initial_capital
        portfolio.current_capital = payload.initial_capital

    user.investment_style = payload.investment_style
    user.onboarding_completed = True

    db.commit()
    db.refresh(user)
    db.refresh(portfolio)

    return OnboardingCompleteResponse(
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "onboarding_completed": True,
            "investment_style": user.investment_style,
        },
        portfolio_id=portfolio.portfolio_id,
    )


# --------------------------------------------------------
# 보유 종목(삼성전자 등) 저장 / 수정
# --------------------------------------------------------
@app.post(
    "/portfolio/holdings",
    response_model=HoldingResponse,
    dependencies=[Depends(verify_api_key)],
)
def upsert_holding(
    payload: HoldingUpsertRequest,
    db: Session = Depends(get_db),
):
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.portfolio_id == payload.portfolio_id)
        .first()
    )
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holding = (
        db.query(PortfolioHolding)
        .filter(
            PortfolioHolding.portfolio_id == portfolio.id,
            PortfolioHolding.symbol == payload.symbol,
        )
        .first()
    )
    if holding is None:
        holding = PortfolioHolding(
            portfolio_id=portfolio.id,
            symbol=payload.symbol,
            shares=payload.shares,
            average_price=payload.average_price,
        )
        db.add(holding)
    else:
        holding.shares = payload.shares
        holding.average_price = payload.average_price

    db.commit()
    db.refresh(holding)

    return HoldingResponse(
        portfolio_id=payload.portfolio_id,
        symbol=holding.symbol,
        shares=holding.shares,
        average_price=holding.average_price,
    )


# --------------------------------------------------------
# 안정형 / 공격형 예측 API
# --------------------------------------------------------
async def _run_prediction_common(
    model_type: str,
    data: MarketDataInput,
    db: Session,
) -> ModelPredictionResponse:
    """
    안정형(stable) / 공격형(aggressive) 예측 공용 로직.
    """
    if model_type == "stable":
        signal, confidence, indicators, feature_importance = model_loader.predict_stable(
            symbol=data.symbol
        )
    elif model_type == "aggressive":
        signal, confidence, indicators, feature_importance = model_loader.predict_aggressive(
            symbol=data.symbol
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported model_type")

    # GPT 설명 생성
    explanation = await interpret_model_output(
        signal=signal,
        technical_indicators=indicators,
        feature_importance=feature_importance,
    )

    # 상위 TOP3 지표 (feature_importance 기준)
    top3: Dict[str, float] = {}
    if feature_importance:
        sorted_items = sorted(
            feature_importance.items(), key=lambda x: x[1], reverse=True
        )[:3]
        top3 = {k: indicators.get(k, 0.0) for k, _ in sorted_items}

    # 거래 로그 저장 (간단 버전)
    # 필요하면 실제 매수/매도 실행 시점과 분리 가능
    default_portfolio_id = "demo_portfolio"
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.portfolio_id == default_portfolio_id)
        .first()
    )
    if portfolio is None:
        portfolio = Portfolio(
            portfolio_id=default_portfolio_id,
            initial_capital=0.0,
            current_capital=0.0,
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    record = InvestmentRecord(
        portfolio_id=portfolio.portfolio_id,
        model_type=model_type,
        symbol=data.symbol,
        signal=signal,
        entry_price=indicators.get("close", 0.0),
        shares=0.0,  # 실제 체결이 아니므로 0
        pnl=0.0,
        confidence_score=confidence,
        gpt_explanation=explanation,
    )
    db.add(record)
    db.commit()

    return ModelPredictionResponse(
        model_type=model_type,
        signal=signal,
        confidence_score=confidence,
        gpt_explanation=explanation,
        top_indicators=top3,
        feature_importance=feature_importance,
    )


@app.post(
    "/predict/stable",
    response_model=ModelPredictionResponse,
    dependencies=[Depends(verify_api_key)],
)
async def predict_stable(
    data: MarketDataInput,
    db: Session = Depends(get_db),
):
    return await _run_prediction_common("stable", data, db)


@app.post(
    "/predict/aggressive",
    response_model=ModelPredictionResponse,
    dependencies=[Depends(verify_api_key)],
)
async def predict_aggressive(
    data: MarketDataInput,
    db: Session = Depends(get_db),
):
    return await _run_prediction_common("aggressive", data, db)


# --------------------------------------------------------
# AI 거래 내역 탭 (모델별 추천 행동 조회)
# --------------------------------------------------------
@app.post(
    "/ai/history",
    response_model=List[InvestmentRecordResponse],
    dependencies=[Depends(verify_api_key)],
)
def get_ai_history(
    query: InvestmentHistoryQuery,
    db: Session = Depends(get_db),
):
    q = db.query(InvestmentRecord)
    if query.portfolio_id:
        q = q.filter(InvestmentRecord.portfolio_id == query.portfolio_id)
    if query.model_type:
        q = q.filter(InvestmentRecord.model_type == query.model_type)

    q = q.order_by(InvestmentRecord.executed_at.desc()).limit(query.limit)
    rows = q.all()

    return [
        InvestmentRecordResponse(
            id=row.id,
            portfolio_id=row.portfolio_id,
            model_type=row.model_type,
            symbol=row.symbol,
            signal=row.signal,
            entry_price=row.entry_price,
            shares=row.shares,
            pnl=row.pnl,
            confidence_score=row.confidence_score,
            executed_at=row.executed_at,
            gpt_explanation=row.gpt_explanation,
        )
        for row in rows
    ]