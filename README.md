
  # 🚀 AI 주식 추천 웹사이트

투자 성향별 맞춤형 AI 모델을 활용한 주식 분석 및 추천 서비스

## ✨ 주요 기능

- **투자 성향별 AI 모델**: 공격형, 중간형, 안정형에 따른 맞춤 분석
- **실시간 주식 분석**: 기술 지표 기반 AI 예측
- **포트폴리오 관리**: 보유 종목 및 수익률 추적
- **AI 거래 내역**: 자동 매매 기록 및 성과 분석

## 🛠 기술 스택

### Frontend
- **React 18** + **TypeScript**
- **Vite** (빌드 도구)
- **Tailwind CSS** (스타일링)
- **Lightweight Charts** (차트 라이브러리)

### Backend
- **FastAPI** (Python)
- **SQLAlchemy** (ORM)
- **PostgreSQL** (데이터베이스)
- **OpenAI GPT** (AI 해석)

### AI Models
- **MARL 4-Agent**: 멀티 에이전트 강화학습 (중간형)
- **A2C Model**: Advantage Actor-Critic (공격형)
- **MARL 3-Agent**: 안정형 투자 전략

## 🚀 빠른 시작

### 프론트엔드 실행
```bash
npm install
npm run dev
```

### 백엔드 실행
```bash
cd back/2025-2-CSC4004-1-7-Libri-main/BE
pip install -r requirements.txt
python main.py
```

## 📱 화면 구성

1. **온보딩**: 종목 선택 및 투자 성향 설정
2. **홈**: 포트폴리오 현황 및 종목 목록
3. **종목 상세**: AI 분석 결과 및 기술 지표
4. **거래 내역**: AI 자동 매매 기록

## 🤖 AI 모델 특징

| 모델 | 투자 성향 | 특징 |
|------|----------|------|
| A2C | 공격형 | 높은 수익률 추구, 단기 변동성 활용 |
| MARL 4-Agent | 중간형 | 균형잡힌 리스크-수익 전략 |
| MARL 3-Agent | 안정형 | 안전한 장기 투자 전략 |

## 📊 API 엔드포인트

- `GET /health` - 서버 상태 확인
- `POST /predict/{model_type}` - AI 예측 요청
- `GET /investment/history` - 거래 내역 조회
- `GET /indicators/history` - 기술 지표 히스토리

## 🔧 환경 설정

### 환경 변수 (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your_api_key
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 👥 개발팀

- Frontend: React + TypeScript
- Backend: FastAPI + Python
- AI: 강화학습 모델 (MARL, A2C)

  This is a code bundle for 주식 추천 웹사이트 구현. The original project is available at https://www.figma.com/design/H2gJv5wAOk2MvcznPUtWfe/%EC%A3%BC%EC%8B%9D-%EC%B6%94%EC%B2%9C-%EC%9B%B9%EC%82%AC%EC%9D%B4%ED%8A%B8-%EA%B5%AC%ED%98%84.

  ## Running the code

  Run `npm i` to install the dependencies.

  Run `npm run dev` to start the development server.
  