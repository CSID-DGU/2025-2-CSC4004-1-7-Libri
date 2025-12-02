from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    investment_style: str | None = None

class UserInvestmentUpdate(BaseModel):
    investment_style: str

class User(UserBase):
    id: int
    is_active: bool
    investment_style: str | None = None

    class Config:
        orm_mode = True
