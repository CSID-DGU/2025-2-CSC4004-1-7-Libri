from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db
from .routers import portfolio, stocks, ai, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(portfolio.router)
app.include_router(stocks.router)
app.include_router(ai.router)
app.include_router(users.router)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Database is set up!"}