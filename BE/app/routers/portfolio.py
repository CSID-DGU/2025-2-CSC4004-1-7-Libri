from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database
from ..stock_fetcher import fetch_current_price 
from typing import List

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
)

@router.get("/{user_id}", response_model=schemas.PortfolioResponse)
def get_my_portfolio(user_id: int, db: Session = Depends(database.get_db)):
    """내 포트폴리오 조회 (실시간 주가 연동 완료)"""
    portfolio = crud.get_portfolio_by_user(db, user_id)
    
    total_stock_value = 0.0
    response_holdings = []
    
    for holding in portfolio.holdings:
        # 👇 [수정] 실제 실시간 주가 가져오기 (stock_fetcher 활용)
        # 005930 -> 005930.KS 로 변환 (yfinance용)
        symbol_for_fetch = holding.symbol
        if symbol_for_fetch.isdigit():
            symbol_for_fetch = f"{symbol_for_fetch}.KS"
            
        real_current_price = fetch_current_price(symbol_for_fetch)
        
        # 만약 장마감/휴일 등으로 데이터를 못 가져오면 평단가로 대체 (에러 방지)
        if real_current_price is None:
            current_price = holding.avg_price
        else:
            current_price = real_current_price
        
        # 평가 금액 계산
        valuation = current_price * holding.quantity
        total_stock_value += valuation
        
        # 수익률 계산: (현재가 - 평단가) / 평단가 * 100
        profit_rate = 0.0
        if holding.avg_price > 0:
            profit_rate = ((current_price - holding.avg_price) / holding.avg_price) * 100
            
        response_holdings.append({
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "avg_price": holding.avg_price,
            "current_price": current_price,  # 실시간 가격 반영
            "profit_rate": profit_rate
        })

    return {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "current_capital": portfolio.current_capital,
        "total_asset": portfolio.current_capital + total_stock_value,
        "holdings": response_holdings
    }

# ... (아래 POST 메서드들은 기존과 동일하게 유지) ...
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

@router.get("/{user_id}/history", response_model=List[schemas.InvestmentRecordResponse])
def get_portfolio_history(user_id: int, db: Session = Depends(database.get_db)):
    """사용자의 투자(매매) 내역 조회"""
    return crud.get_investment_history(db, user_id)