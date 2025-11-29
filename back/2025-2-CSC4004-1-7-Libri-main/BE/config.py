import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/trading_db")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# API Security
API_KEY = os.getenv("API_KEY", "")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 100

# Model Paths
MARL_MODEL_PATH = "../marl_4agent"
MODEL_2_PATH = "../model_2"  # 추가할 모델 경로
MODEL_3_PATH = "../model_3"  # 추가할 모델 경로
