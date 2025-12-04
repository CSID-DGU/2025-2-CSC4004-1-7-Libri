# BE/app/routers/portfolio.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)

@router.get("/{user_id}", response_model=schemas.PortfolioResponse)
def get_my_portfolio(user_id: int, db: Session = Depends(database.get_db)):
    """내 포트폴리오 조회 (수익률 자동 계산)"""
    portfolio = crud.get_portfolio_by_user(db, user_id)
    
    # [간이 수익률 계산 로직]
    # 실제로는 실시간 현재가를 가져와야 하지만, 지금은 테스트용으로 평단가 + 5% 상승했다고 가정
    total_stock_value = 0.0
    response_holdings = []
    
    for holding in portfolio.holdings:
        # stock_fetcher를 이용해 DB에서 해당 종목의 가장 최근 가격(close)을 조회합니다.
        latest_stock = stock_fetcher.get_latest_price(db, holding.symbol)
        current_price = latest_stock.close if latest_stock else holding.avg_price
        
        valuation = current_price_mock * holding.quantity
        total_stock_value += valuation
        
        # 수익률 계산: (현재가 - 평단가) / 평단가 * 100
        profit_rate = 0.0
        if holding.avg_price > 0:
            profit_rate = ((current_price_mock - holding.avg_price) / holding.avg_price) * 100
            
        response_holdings.append({
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "avg_price": holding.avg_price,
            "current_price": current_price_mock,
            "profit_rate": profit_rate
        })

    return {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "current_capital": portfolio.current_capital,
        "total_asset": portfolio.current_capital + total_stock_value,
        "holdings": response_holdings
    }

@router.post("/{user_id}/holdings")
def add_stock(user_id: int, holding: schemas.HoldingCreate, db: Session = Depends(database.get_db)):
    """보유 주식 추가 (매수)"""
    crud.add_holding(db, user_id, holding)
    return {"message": "주식이 성공적으로 추가되었습니다."}

@router.post("/{user_id}/sell")
def sell_stock(user_id: int, sell_data: schemas.HoldingSell, db: Session = Depends(database.get_db)):
    """주식 매도 (부분 매도 가능)"""
    result = crud.sell_holding(db, user_id, sell_data)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return {"message": result["message"]}