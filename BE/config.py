import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API 키 (선택사항 - 없으면 기본 설명 사용)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
