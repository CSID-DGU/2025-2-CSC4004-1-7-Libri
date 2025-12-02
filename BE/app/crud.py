from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy.orm import Session
from . import models, schemas

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

# 포트폴리오 생성/조회
def get_portfolio_by_user(db: Session, user_id: int):
    # 유저의 포트폴리오 찾기
    return db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).first()

def create_portfolio(db: Session, user_id: int):
    # 포트폴리오가 없으면 기본값으로 생성
    db_portfolio = models.Portfolio(user_id=user_id, cash_balance=0.0)
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

# 보유 주식 추가/업데이트 (핵심 기능)
def add_or_update_holding(db: Session, portfolio_id: int, holding_data: schemas.HoldingCreate):
    # 이미 보유한 종목인지 확인
    existing_holding = db.query(models.Holding).filter(
        models.Holding.portfolio_id == portfolio_id,
        models.Holding.stock_symbol == holding_data.stock_symbol
    ).first()

    if existing_holding:
        # 이미 있으면 개수와 평단가 업데이트 (단순 덮어쓰기 로직, 필요시 가중평균 로직으로 변경 가능)
        existing_holding.quantity += holding_data.quantity
        existing_holding.avg_price = holding_data.avg_price # 예시: 평단가는 입력값으로 갱신
        # 실제 가중평균 로직: (기존총액 + 추가총액) / 전체수량
    else:
        # 없으면 새로 추가
        new_holding = models.Holding(
            portfolio_id=portfolio_id,
            stock_symbol=holding_data.stock_symbol,
            quantity=holding_data.quantity,
            avg_price=holding_data.avg_price
        )
        db.add(new_holding)
    
    db.commit()
    return get_portfolio_by_user(db, portfolio_id=db.query(models.Portfolio).filter(models.Portfolio.id==portfolio_id).first().user_id) # 갱신된 포트폴리오 반환

# 보유 주식 조회
def get_holdings(db: Session, portfolio_id: int):
    return db.query(models.Holding).filter(models.Holding.portfolio_id == portfolio_id).all()