from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    investment_style = Column(String, default=None, nullable=True)
    onboarding_completed = Column(Boolean, default=False)  # 온보딩 완료 여부

    # [추가] 유저와 포트폴리오 1:1 연결
    portfolio = relationship("Portfolio", back_populates="owner", uselist=False)
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

    # 어떤 모델/전략으로 한 거래인지 (예: "aggressive_a2c", "marl_3agent" 등)
    model_type = Column(String(50), index=True)

    # 매수/매도/보유 등 신호
    signal = Column(String(20), index=True)

    # 가격/수량/포트폴리오 가치
    entry_price = Column(Float, nullable=True)
    shares = Column(Float, nullable=True)
    portfolio_value = Column(Float, nullable=True)

    # 해당 거래의 손익
    pnl = Column(Float, nullable=True)

    # GPT 설명
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


# ---------------------------------------------------------------------
# 3) 포트폴리오 테이블 (Portfolio)
# ---------------------------------------------------------------------
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    # [수정/추가] 유저 ID와 연결 (Foreign Key)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    

    portfolio_id = Column(String(50), unique=True, index=True)
    initial_capital = Column(Float, nullable=False)
    current_capital = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # [추가] 관계 설정
    owner = relationship("User", back_populates="portfolio")
    holdings = relationship("Holding", back_populates="portfolio")

# ---------------------------------------------------------------------
# [신규] 보유 주식 테이블 (Holding) - 새로 추가
# ---------------------------------------------------------------------
class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    
    symbol = Column(String, index=True)       # 종목 코드 (예: 005930)
    quantity = Column(Integer, default=0)     # 보유 수량
    avg_price = Column(Float, default=0.0)    # 평균 단가

    portfolio = relationship("Portfolio", back_populates="holdings")

# ---------------------------------------------------------------------
# 4) 주가 히스토리 테이블 (StockPrice)
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
