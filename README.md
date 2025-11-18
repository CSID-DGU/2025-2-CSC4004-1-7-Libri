# QMIX 기반 멀티에이전트 주식 트레이딩 봇

본 프로젝트는 QMIX (Multi-Agent Reinforcement Learning) 알고리즘을 활용하여 주식 트레이딩 결정을 내리는 AI 봇입니다.

**4개의 전문 에이전트**가 서로 다른 관점으로 시장을 분석하며, QMIX의 믹서 네트워크(Mixer Network)가 이들의 의견을 종합하여 최종 팀 보상을 극대화하는 방향으로 학습합니다.

## 📂 프로젝트 구조
```
.
├── main.py             # 메인 실행 파일 (학습 루프 및 결과 출력)
├── qmix_model.py       # QMIX 모델 (Q_Net, DQN_Agent, Mixer, QMIX_Learner)
├── environment.py      # 주식 거래 환경 (MARLStockEnv, Gymnasium 기반)
├── data_processor.py   # 데이터 수집, 가공, 정규화 (yfinance, pandas_ta)
├── replay_buffer.py    # 리플레이 버퍼
├── config.py           # 주요 하이퍼파라미터 및 설정
└── requirements.txt    # (필요시 생성)
```
## 🤖 에이전트 구성: 4개의 전문가

본 프로젝트는 MARL의 협력적 측면을 극대화하기 위해, 4개 에이전트에게 의도적으로 **서로 다른 역할**을 부여했습니다.

### Agent 0: 단기 트레이더 (Short-term Trader)
- **역할**: 변동성, 과매수/과매도 등 단기적인 모멘텀에 집중
- **주요 지표**: RSI, Stoch_K, Stoch_D, ATR, Bollinger_B + 가격 정보

### Agent 1: 장기 투자자 (Long-term Investor)
- **역할**: 이동평균, 추세 및 기업 펀더멘탈 등 중장기적인 흐름에 집중
- **주요 지표**: SMA20, MACD, ROA, DebtRatio, AnalystRating + 가격 정보

### Agent 2: 위험 관리자 (Risk Manager)
- **역할**: 시장 위험과 변동성 분석
- **주요 지표**: VIX, ATR, Bollinger_B + 가격 정보

### Agent 3: 시장 감성 분석가 (Sentiment Analyst)
- **역할**: 거래량, 모멘텀, 시장 강도 등 시장 감성 파악
- **주요 지표**: Volume_Ratio, Price_Momentum, Price_Volatility, Market_Strength, VIX_Change + 가격 정보

**학습 메커니즘**
  1. 두 에이전트는 각자 전문화된 정보(Observation)를 받아 개별 Q-Value (행동의 가치)를 계산합니다.
  
  2. **QMIX 믹서 네트워크**는 이 두 에이전트의 개별 Q-Value와 모든 정보가 포함된 **글로벌 상태(Global State)**를 함께 입력받습니다.
  
  3. 믹서는 "단기 트레이더는 '매수'를, 장기 추종자는 '보유'를 외치는데, 지금 글로벌 상태를 보니 단기 신호를 따르는 것이 팀 보상에 더 좋겠다"와 같은 고차원적인 협력 전략을 학습합니다.
  
  4. 최종적으로 '팀 Q-Value' (Q_total)를 출력하며, 이 Q_total이 최대가 되는 공동 행동(Joint Action)을 선택합니다.

## 🚀 실행 및 결과 출력
**1. 주요 라이브러리 설치**

```
# 1. Conda 환경 만들기
conda create -n qmix python=3.12.7 -y
conda activate qmix

# 2. requirements.txt 기반 설치
pip install -r requirements.txt
```
**2. 실행**
기본 실행 (현재 자산 1000만 원(현금) 가정 실행):

```
python main.py
```

**2-1. 계산 방법**
포트폴리오 가치 = 현금 + (보유 주식 수 × 현재 가격)

일 수익 = 오늘 포트폴리오 가치 - 어제 포트폴리오 가치

**2-2. 매수, 매도 수량**
(1) 매수 신호이면 보유 현금의 90% 매수
(2) 매도 신호이면 보유 현금의 90% 매도


**3. 출력 결과**
학습이 완료되면, 테스트 데이터의 최종일을 기준으로 분석 결과를 콘솔에 출력합니다.


**출력 해석**
1. **AI 최종 신호**: 두 에이전트의 행동(Long/Hold/Short)을 조합하여 계산된 최종 신호입니다. (e.g., Long + Long = "적극 매수")

2. **AI 설명 (XAI)**: get_prediction_with_reason 함수가 각 에이전트의 결정에 영향을 미친 입력 피처의 중요도를 Gradient 기반으로 계산합니다. 이 중요도를 두 에이전트에 걸쳐 합산하여 가장 영향력이 높았던 Top 3 지표를 보여줍니다.

3. **기술적 분석 상세**: AI가 최종 결정을 내린 시점의 정규화되지 않은(Unnormalized) 원본 지표 값입니다.

4. **상세 Q_total 그리드**: QMIX의 핵심 출력물입니다. agent_0 (단기)과 agent_1 (장기)이 취할 수 있는 9가지 (3x3) 모든 행동 조합에 대해 믹서가 예측한 **미래의 총 팀 보상(Q_total)**입니다. AI는 이 그리드에서 가장 높은 값(위 예시에서는 152.7314)을 선택하며, 이 값에 해당하는 행동 조합(Long/Long)을 최종 결정으로 내립니다.
---