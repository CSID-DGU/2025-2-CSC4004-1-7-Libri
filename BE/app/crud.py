from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email, 
        hashed_password=user.password,
        # investment_style은 나중에 설정
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_investment_style(db: Session, user_id: int, investment_style: str):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.investment_style = investment_style
        db.commit()
        db.refresh(db_user)
    return db_user

# 포트폴리오 가져오기 (없으면 자동 생성)
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

# 보유 주식 추가하기 (매수 로직)
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
    
    #투자 기록(History) 저장하기 
    history_record = models.InvestmentRecord(
        portfolio_id=portfolio.portfolio_id, # 문자열 ID 사용
        model_type="manual_trade",           # 사용자가 직접 매수함
        signal="BUY",
        entry_price=holding_data.avg_price,
        shares=holding_data.quantity,
        portfolio_value=portfolio.total_asset if hasattr(portfolio, 'total_asset') else 0, # 현재 가치는 계산 필요하지만 일단 0 또는 임시값
        confidence_score=1.0 # 사용자 직접 투자이므로 신뢰도 100%
    )
    db.add(history_record) # 기록 저장

    db.commit()
    return portfolio

#부분/전량 매도
def sell_holding(db: Session, user_id: int, sell_data: schemas.HoldingSell):
    portfolio = get_portfolio_by_user(db, user_id)
    
    # 1. 내 주식 찾기
    holding = db.query(models.Holding).filter(
        models.Holding.portfolio_id == portfolio.id,
        models.Holding.symbol == sell_data.symbol
    ).first()
    
    if not holding:
        return {"status": "error", "message": "보유하지 않은 주식입니다."}
    
    if holding.quantity < sell_data.quantity:
        return {"status": "error", "message": "보유 수량이 부족합니다."}

    # 2. 매도 금액 계산 (판매가 * 수량)
    revenue = sell_data.quantity * sell_data.sell_price
    
    # 3. 수익금 계산 (단순 참고용: 판매총액 - (평단가 * 수량))
    profit = revenue - (holding.avg_price * sell_data.quantity)

    # 4. 예수금 증가 (판 돈 입금)
    portfolio.current_capital += revenue
    portfolio.updated_at = datetime.utcnow()

    # 5. 매도 기록(History) 남기기
    sell_record = models.InvestmentRecord(
        portfolio_id=portfolio.portfolio_id,
        model_type="manual_trade",
        signal="SELL",
        entry_price=sell_data.sell_price,
        shares=sell_data.quantity,
        pnl=profit, # 이번 거래로 번 돈 (손익)
        confidence_score=1.0
    )
    db.add(sell_record)

    # 6. 수량 차감 로직 (핵심!)
    if holding.quantity == sell_data.quantity:
        # 전량 매도면 -> 데이터 삭제
        db.delete(holding)
        msg = "전량 매도 완료"
    else:
        # 부분 매도면 -> 수량만 감소
        holding.quantity -= sell_data.quantity
        msg = "부분 매도 완료"
    
    db.commit()
    return {"status": "success", "message": msg, "portfolio": portfolio}

# ---------------------------------------------------------------------
# 주가 데이터 저장
# ---------------------------------------------------------------------
def create_stock_price(db: Session, stock_price: schemas.StockPriceCreate):
    db_stock_price = models.StockPrice(**stock_price.dict())
    db.add(db_stock_price)
    db.commit()
    db.refresh(db_stock_price)
    return db_stock_price

def bulk_create_stock_prices(db: Session, stock_prices: list[schemas.StockPriceCreate]):
    if not stock_prices:
        return 0

    # 1. 입력된 데이터에서 (symbol, date) 목록 추출
    symbols = {sp.symbol for sp in stock_prices}
    dates = {sp.date for sp in stock_prices}
    
    # 2. DB에서 이미 존재하는 (symbol, date) 조회
    existing_records = db.query(models.StockPrice).filter(
        models.StockPrice.symbol.in_(symbols),
        models.StockPrice.date.in_(dates)
    ).all()
    
    existing_keys = {(r.symbol, r.date) for r in existing_records}
    
    # 3. 중복되지 않는 데이터만 필터링
    new_records = []
    for sp in stock_prices:
        if (sp.symbol, sp.date) not in existing_keys:
            new_records.append(models.StockPrice(**sp.dict()))
            # 중복 방지를 위해 추가한 키도 existing_keys에 등록 (입력 데이터 내 중복 방지)
            existing_keys.add((sp.symbol, sp.date))
            
    if new_records:
        db.add_all(new_records)
        db.commit()
        
    return len(new_records)

def get_stock_prices(db: Session, symbol: str, days: int = 30):
    return db.query(models.StockPrice)\
        .filter(models.StockPrice.symbol == symbol)\
        .order_by(models.StockPrice.date.desc())\
        .limit(days)\
        .all()

def get_latest_stock_date(db: Session, symbol: str):
    result = db.query(models.StockPrice.date)\
        .filter(models.StockPrice.symbol == symbol)\
        .order_by(models.StockPrice.date.desc())\
        .first()
    return result[0] if result else None

def get_investment_history(db: Session, user_id: int):
    # 1. 유저의 포트폴리오 정보 가져오기 (portfolio_id 문자열이 필요함)
    portfolio = get_portfolio_by_user(db, user_id)
    if not portfolio:
        return []
    
    # 2. 해당 포트폴리오의 거래 내역을 최신순으로 조회
    return db.query(models.InvestmentRecord).filter(
        models.InvestmentRecord.portfolio_id == portfolio.portfolio_id
    ).order_by(models.InvestmentRecord.timestamp.desc()).all()