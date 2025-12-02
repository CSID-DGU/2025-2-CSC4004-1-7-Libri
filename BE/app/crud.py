from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        email=user.email, 
        hashed_password=fake_hashed_password,
        investment_style=user.investment_style
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 1. 포트폴리오 가져오기 (없으면 자동 생성)
def get_portfolio_by_user(db: Session, user_id: int):
    portfolio = db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).first()
    if not portfolio:
        # 포트폴리오가 없으면 기본값으로 생성해버림 (편의성)
        portfolio = models.Portfolio(
            user_id=user_id,
            portfolio_id=f"user_{user_id}_default",
            initial_capital=10000000.0,
            current_capital=10000000.0
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    return portfolio

# 2. 보유 주식 추가하기 (매수 로직)
def add_holding(db: Session, user_id: int, holding_data: schemas.HoldingCreate):
    portfolio = get_portfolio_by_user(db, user_id)
    
    # 이미 보유 중인지 확인
    existing = db.query(models.Holding).filter(
        models.Holding.portfolio_id == portfolio.id,
        models.Holding.symbol == holding_data.symbol
    ).first()

    cost = holding_data.quantity * holding_data.avg_price

    if existing:
        # 물타기 (평단가 재계산): 총매입금액 / 총수량
        total_quantity = existing.quantity + holding_data.quantity
        total_cost = (existing.quantity * existing.avg_price) + cost
        existing.avg_price = total_cost / total_quantity
        existing.quantity = total_quantity
    else:
        # 신규 추가
        new_holding = models.Holding(
            portfolio_id=portfolio.id,
            symbol=holding_data.symbol,
            quantity=holding_data.quantity,
            avg_price=holding_data.avg_price
        )
        db.add(new_holding)
    
    # 예수금 차감
    portfolio.current_capital -= cost
    portfolio.updated_at = datetime.utcnow()
    
    db.commit()
    return portfolio