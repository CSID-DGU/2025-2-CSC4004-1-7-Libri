# AI Trading Backend

FastAPI 기반 AI 트레이딩 백엔드 시스템

## 주요 기능

- **다중 AI 모델 연결**: MARL 4-agent, Model 2, Model 3
- **GPT API 연동**: 모델 출력 자연어 해석
- **데이터베이스**: PostgreSQL을 통한 거래 내역 및 기술 지표 저장
- **RESTful API**: 모델 예측, 포트폴리오 관리, 성과 분석

## 설치

```bash
cd BE
pip install -r requirements.txt
```

## 환경 설정

`.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 수정:
- `DATABASE_URL`: PostgreSQL 연결 정보
- `OPENAI_API_KEY`: OpenAI API 키
- `API_KEY`: 백엔드 API 인증 키
- `CORS_ORIGINS`: 허용할 프론트엔드 도메인

## 데이터베이스 설정

PostgreSQL 설치 후:

```sql
CREATE DATABASE trading_db;
```

## 실행

```bash
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### 헬스 체크
- `GET /health` - 시스템 상태 확인
- `GET /models/status` - 모델 상태 확인
- `GET /models/list` - 사용 가능한 모델 목록 (FE 선택 UI용)

### 모델 예측 (FE에서 선택)
- `POST /predict/marl` - MARL 4-agent 예측
- `POST /predict/model2` - Model 2 예측
- `POST /predict/model3` - Model 3 예측

### 포트폴리오 관리
- `POST /portfolio/capital` - 초기 자본 설정
- `GET /portfolio/{portfolio_id}` - 포트폴리오 조회

### 투자 내역
- `POST /investment/record` - 투자 내역 기록
- `GET /investment/history` - 투자 내역 조회
- `GET /investment/metrics` - 성과 지표 조회

### 기술 지표
- `GET /indicators/history` - 기술 지표 내역 조회

## API 사용 예시

### 모델 예측 요청

```bash
curl -X POST "http://localhost:8000/predict/marl" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "symbol": "005930",
    "features": {
      "SMA20": 70000,
      "MACD": 500,
      "RSI": 65,
      "Stoch_K": 70,
      "Bollinger_B": 0.8
    }
  }'
```

### 포트폴리오 설정

```bash
curl -X POST "http://localhost:8000/portfolio/capital" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "portfolio_id": "user123",
    "initial_capital": 10000000
  }'
```

## 구조

```
BE/
├── main.py              # FastAPI 애플리케이션
├── config.py            # 설정 관리
├── database.py          # DB 모델 및 연결
├── models.py            # Pydantic 모델
├── model_loader.py      # AI 모델 로더
├── gpt_service.py       # GPT API 서비스
├── requirements.txt     # 의존성
├── .env.example         # 환경 변수 예시
└── README.md           # 문서
```

## 개발 노트

- Model 2, Model 3는 `model_loader.py`에서 구현 필요
- MARL 모델 가중치는 `../marl_4agent/saved_model.pth`에 저장
- Rate limiting은 추후 구현 예정
