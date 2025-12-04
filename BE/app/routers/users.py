from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas, crud, models

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/login")
def login(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. 이메일로 유저 찾기
    user = crud.get_user_by_email(db, email=user_data.email)
    
    # 2. 유저가 없거나 비밀번호가 틀리면 에러
    if not user or user.hashed_password != user_data.password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # 3. 맞으면 user_id 리턴
    return {"user_id": user.id, "email": user.email}

@router.get("/me")
def read_users_me(user_id: int, db: Session = Depends(database.get_db)):
    # 토큰 없이 user_id로 조회 (단순화)
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/investment-style", response_model=schemas.User)
def update_investment_style(user_id: int, investment: schemas.UserInvestmentUpdate, db: Session = Depends(database.get_db)):
    db_user = crud.update_user_investment_style(db, user_id=user_id, investment_style=investment.investment_style)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user