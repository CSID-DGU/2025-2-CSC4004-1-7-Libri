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

def update_user_investment_style(db: Session, user_id: int, investment_style: str):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.investment_style = investment_style
        db.commit()
        db.refresh(db_user)
    return db_user
