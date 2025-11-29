# BE/database.py

from datetime import datetime
from typing import Generator

# BE/database.py 일부 (상단 import 쪽에 Boolean, ForeignKey, relationship 추가)

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Text,
    Index,
    create_engine,
    Boolean,        # ← 추가
    ForeignKey,     # ← 추가
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship  # ← relationship 추가

from config import DATABASE_URL

# ---------------------------------------------------------------------
# 기본 설정 (Engine, Base, Session)
# ---------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,  # 디버깅용으로 보고 싶으면 True로 변경
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# --------------------------------------------------------
# 0) 사용자 테이블 (User) – 구글 로그인 / 온보딩용
# --------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String(128), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=True)

    onboarding_completed = Column(Boolean, default=False)
    investment_style = Column(String(20), nullable=True)  # 'stable' / 'aggressive'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    portfolios = relationship("Portfolio", back_populates="user")


# ---------------------------------------------------------------------
# 1) 기술 지표 테이블 (TechnicalIndicator)
# ---------------------------------------------------------------------
class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True)

    # 어떤 종목, 언제 기준의 지표인지
    symbol = Column(String(20), index=True)
    timestamp = Column(DateTime, index=True)

    # 가격 기반 지표
    sma20 = Column(Float, nullable=True)          # 20일 단순 이동평균
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    stoch_k = Column(Float, nullable=True)
    stoch_d = Column(Float, nullable=True)
    atr = Column(Float, nullable=True)

    # 밴드/변동성 지표
    bollinger_b = Column(Float, nullable=True)
    vix = Column(Float, nullable=True)

    # 재무/기초 지표
    roa = Column(Float, nullable=True)
    debt_ratio = Column(Float, nullable=True)
    analyst_rating = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# 심볼 + 시간으로 자주 조회하니까 인덱스 추가
Index(
    "idx_technical_indicator_symbol_timestamp",
    TechnicalIndicator.symbol,
    TechnicalIndicator.timestamp,
)


# ---------------------------------------------------------------------
# 2) 개별 투자 거래 기록 테이블 (InvestmentRecord)
# ---------------------------------------------------------------------
class InvestmentRecord(Base):
    __tablename__ = "investment_records"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime, index=True, default=datetime.utcnow)

    # 어떤 포트폴리오의 거래인지 (FE에서 portfolio_id를 문자열로 관리)
    portfolio_id = Column(String(50), index=True)

    # 어떤 모델/전략으로 한 거래인지 (예: "aggressive_a2c", "marl_4agent" 등)
    model_type = Column(String(50), index=True)

    # 매수/매도/보유 등 신호
    signal = Column(String(20), index=True)

    # 가격/수량/포트폴리오 가치
    entry_price = Column(Float, nullable=True)
    shares = Column(Float, nullable=True)
    portfolio_value = Column(Float, nullable=True)

    # 해당 거래의 손익
    pnl = Column(Float, nullable=True)

    # 모델 신뢰도와 GPT 설명
    confidence_score = Column(Float, nullable=True)
    gpt_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


Index(
    "idx_investment_record_portfolio_timestamp",
    InvestmentRecord.portfolio_id,
    InvestmentRecord.timestamp,
)
Index(
    "idx_investment_record_model_timestamp",
    InvestmentRecord.model_type,
    InvestmentRecord.timestamp,
)


# --------------------------------------------------------
# (기존) Portfolio 클래스에 user_id / holdings 관계 추가
# --------------------------------------------------------

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)

    # FE가 관리하는 포트폴리오 식별자 (예: "user_1_default")
    portfolio_id = Column(String(50), unique=True, index=True)

    # 🔥 여기 추가
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="portfolios")

    initial_capital = Column(Float, nullable=False)
    current_capital = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # 🔥 holdings 관계 추가
    holdings = relationship(
        "PortfolioHolding",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

# --------------------------------------------------------
# 3) 포트폴리오 내 종목 보유 테이블 (PortfolioHolding) – 온보딩/종목추가용
# --------------------------------------------------------
class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)

    symbol = Column(String(20), nullable=False)  # "005930"
    shares = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="holdings")

    __table_args__ = (
        Index("ix_holdings_portfolio_symbol", "portfolio_id", "symbol"),
    )


# ---------------------------------------------------------------------
# 4) 주가 히스토리 테이블 (StockPrice) – stock_data_fetcher용
# ---------------------------------------------------------------------
class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String(20), index=True)
    date = Column(DateTime, index=True)

    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


Index("idx_stock_price_symbol_date", StockPrice.symbol, StockPrice.date)


# ---------------------------------------------------------------------
# DB 유틸 함수들
# ---------------------------------------------------------------------
def init_db() -> None:
    """테이블 생성"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의존성에서 사용하는 DB 세션 헬퍼

    예:
        @app.get("/something")
        def read_something(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()