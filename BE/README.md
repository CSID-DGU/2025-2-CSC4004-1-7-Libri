# AI Trading Backend

FastAPI 기반 AI 트레이딩 백엔드 시스템

## 주요 기능

- **다중 AI 모델 연결**:
  - **MARL 3-Agent (안정형)**: 3개 에이전트 기반 멀티에이전트 강화학습 - 안정적인 투자 전략
  - **A2C (공격형)**: 공격형 A2C 강화학습 모델 - 적극적인 매매 전략
- **GPT API 연동**: 모델 출력 자연어 해석
- **데이터베이스**: SQLite/PostgreSQL을 통한 거래 내역 및 기술 지표 저장
- **RESTful API**: 모델 예측, 포트폴리오 관리, 성과 분석

## 설치

### 1. 의존성 설치

```bash
cd BE
pip install -r requirements.txt
```

### 2. 환경 설정

`.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 수정:
```env
# 데이터베이스 (SQLite 사용 시 기본값 유지)
DATABASE_URL=sqlite:///./app.db

# PostgreSQL 사용 시
# DATABASE_URL=postgresql://user:password@localhost:5432/trading_db

# OpenAI API 키 (GPT 해석 기능 사용 시)
OPENAI_API_KEY=your_openai_api_key

# API 인증 키 (비워두면 인증 비활성화)
API_KEY=your_api_key

# CORS 허용 도메인
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 실행 방법

### 기본 실행

```bash
cd BE
python main.py
```

### 개발 모드 (자동 리로드)

```bash
cd BE
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면:
- API 문서: http://localhost:8000/docs
- 대체 API 문서: http://localhost:8000/redoc

## 테스트 방법

### 1. 테스트 스크립트 실행

```bash
cd BE
python test_api.py
```

### 2. 개별 API 테스트 (curl)

#### 헬스 체크
```bash
curl http://localhost:8000/health
```

#### 모델 상태 확인
```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/models/status
```

#### 모델 목록 조회
```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/models/list
```

#### MARL (안정형) 예측
```bash
curl -X POST "http://localhost:8000/predict/marl" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "symbol": "005930",
    "features": {
      "RSI": 45.0,
      "MACD": 100.0,
      "MACD_Signal": 80.0,
      "VIX": 18.0,
      "SMA20": 70000,
      "ATR": 1200,
      "Stoch_K": 55,
      "Stoch_D": 52,
      "Bollinger_B": 0.6
    }
  }'
```

#### A2C (공격형) 예측
```bash
curl -X POST "http://localhost:8000/predict/a2c" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "symbol": "005930",
    "features": {
      "RSI": 25.0,
      "MACD": 150.0,
      "MACD_Signal": 50.0,
      "Stoch_K": 18.0
    }
  }'
```

#### 포트폴리오 생성
```bash
curl -X POST "http://localhost:8000/portfolio/capital" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "portfolio_id": "user123",
    "initial_capital": 10000000
  }'
```

### 3. Python으로 테스트

```python
import requests

BASE_URL = "http://localhost:8000"
headers = {"X-API-Key": "your_api_key", "Content-Type": "application/json"}

# 모델 상태 확인
response = requests.get(f"{BASE_URL}/models/status", headers=headers)
print(response.json())

# MARL 예측
data = {
    "symbol": "005930",
    "features": {"RSI": 45.0, "MACD": 100.0, "MACD_Signal": 80.0, "VIX": 18.0}
}
response = requests.post(f"{BASE_URL}/predict/marl", json=data, headers=headers)
print(response.json())

# A2C 예측
response = requests.post(f"{BASE_URL}/predict/a2c", json=data, headers=headers)
print(response.json())
```

## API 엔드포인트

### 헬스 체크
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/health` | 시스템 상태 확인 |
| GET | `/models/status` | 모델 로드 상태 확인 |
| GET | `/models/list` | 사용 가능한 모델 목록 |

### 모델 예측
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/predict/marl` | MARL 3-Agent (안정형) 예측 |
| POST | `/predict/a2c` | A2C (공격형) 예측 |

### 포트폴리오 관리
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/portfolio/capital` | 초기 자본 설정 |
| GET | `/portfolio/{portfolio_id}` | 포트폴리오 조회 |

### 투자 내역
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/investment/record` | 투자 내역 기록 |
| GET | `/investment/history` | 투자 내역 조회 |
| GET | `/investment/metrics` | 성과 지표 조회 |

### 주가 데이터
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/stock/fetch` | yfinance로 주가 데이터 가져오기 |
| GET | `/stock/prices` | 저장된 주가 데이터 조회 |
| GET | `/stock/latest` | 최신 주가 조회 |

### 기술 지표
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/indicators/history` | 기술 지표 내역 조회 |

## 프로젝트 구조

```
BE/
├── main.py              # FastAPI 애플리케이션 (엔드포인트 정의)
├── config.py            # 환경 설정 관리
├── database.py          # DB 모델 및 연결 (SQLAlchemy)
├── models.py            # Pydantic 요청/응답 모델
├── model_loader.py      # AI 모델 로더 (MARL, A2C)
├── gpt_service.py       # GPT API 서비스
├── stock_data_fetcher.py # 주가 데이터 수집
├── test_api.py          # API 테스트 스크립트
├── requirements.txt     # Python 의존성
├── .env.example         # 환경 변수 예시
└── README.md            # 이 문서

AI/
├── marl_3agent/         # MARL 3-Agent 모델 (안정형)
│   ├── best_model.pth   # 학습된 모델 가중치
│   ├── qmix_model.py    # QMIX 모델 정의
│   ├── config.py        # 모델 설정
│   └── ...
│
└── a2c_11.29/           # A2C 모델 (공격형)
    ├── a2c_samsung.pt   # 학습된 모델 가중치
    ├── ac_model.py      # A2C 모델 정의
    ├── config.yaml      # 모델 설정
    ├── reports/
    │   └── scaler.joblib # 데이터 스케일러
    └── ...
```

## AI 모델 설명

### MARL 3-Agent (안정형)
- **구조**: QMIX 기반 멀티에이전트 강화학습
- **에이전트**:
  - 모멘텀 에이전트: RSI, Stochastic 기반
  - 추세 에이전트: MACD, SMA 기반
  - 변동성 에이전트: VIX, ATR 기반
- **특징**: 3개 에이전트의 투표를 합산하여 안정적인 의사결정

### A2C (공격형)
- **구조**: Advantage Actor-Critic 강화학습
- **특징**: 과매도/과매수 구간에서 적극적인 매매
- **전략**: 빠른 시장 변화에 대응하는 공격적 트레이딩

## 문제 해결

### 모델 로드 실패 시
```bash
# AI 모델 파일 확인
ls -la ../AI/marl_3agent/best_model.pth
ls -la ../AI/a2c_11.29/a2c_samsung.pt
ls -la ../AI/a2c_11.29/reports/scaler.joblib
```

### 데이터베이스 초기화
```bash
# SQLite 데이터베이스 삭제 후 재시작
rm app.db
python main.py
```

### 의존성 문제
```bash
pip install --upgrade -r requirements.txt
```
