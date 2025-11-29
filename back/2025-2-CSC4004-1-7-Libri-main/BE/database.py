from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    symbol = Column(String(20), index=True)
    sma20 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    rsi = Column(Float)
    stoch_k = Column(Float)
    stoch_d = Column(Float)
    atr = Column(Float)
    bollinger_b = Column(Float)
    vix = Column(Float)
    roa = Column(Float)
    debt_ratio = Column(Float)
    analyst_rating = Column(Float)
    
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )

class InvestmentRecord(Base):
    __tablename__ = "investment_records"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    portfolio_id = Column(String(50), index=True)
    model_type = Column(String(20), index=True)
    signal = Column(String(20))
    entry_price = Column(Float)
    shares = Column(Integer)
    portfolio_value = Column(Float)
    pnl = Column(Float)
    confidence_score = Column(Float)
    gpt_explanation = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('idx_portfolio_timestamp', 'portfolio_id', 'timestamp'),
        Index('idx_model_timestamp', 'model_type', 'timestamp'),
    )

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(String(50), unique=True, index=True)
    initial_capital = Column(Float)
    current_capital = Column(Float)
    shares_held = Column(Integer, default=0)
    average_entry_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
