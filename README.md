# 🤖 MARL QMIX 주식 거래 AI

이 프로젝트는 **다중 에이전트 강화학습(MARL)** 기반의 AI 주식 거래 봇입니다.

**QMIX** 알고리즘을 사용하여 두 명의 협력 에이전트(Agent)가 하나의 '공동 포트폴리오'를 관리하도록 학습합니다. 삼성전자(005930.KS)의 주가, 기술적 지표, 재무 데이터를 분석하며, 사용자의 \*\*현재 보유 포트폴리오(보유 수량, 평단가)\*\*를 '상태(State)'에 포함하여 **미실현 수익률**을 고려한 지능적인 의사결정을 내립니다.

최종 분석 결과는 [제공된 UI 디자인 시안](https://www.google.com/search?q=%23-ui-%EC%B6%9C%EB%A0%A5-%EC%98%88%EC%8B%9C)에 맞춰 터미널에 출력됩니다.

-----

## 🚀 핵심 기능

  * **다중 에이전트 협력 (QMIX):** `N_AGENTS` (2명)의 에이전트가 `(매수, 매도)`와 같이 독립적인 행동을 제안하면, '믹서(Mixer)'가 이를 조합해 `"보유"`라는 단일 팀 행동의 가치(Q-Value)를 계산합니다. 이는 "팀"의 공동 보상을 최대화하는 방향으로 학습됩니다.
  * **포트폴리오 상태 확장:** AI가 단순히 시장만 보는 것이 아니라, \*\*"현재 나의 미실현 수익률이 +15%인가, -20%인가?"\*\*를 상태(State)의 일부로 인지합니다. 이를 통해 '익절'이나 '손절'과 같은 현실적인 전략을 학습할 수 있습니다.
  * **설명 가능한 AI (XAI):** AI가 "적극 매수"를 결정했다면, **"왜"** 그렇게 판단했는지 `(1. RSI, 2. ROA, 3. Volume)`와 같이 결정에 가장 큰 영향을 미친 지표(Top 3)를 그래디언트 분석을 통해 제공합니다.
  * **종합 데이터 활용:** `pandas-ta`와 `yfinance`를 활용하여 다음과 같은 3가지 유형의 데이터를 모두 사용합니다.
      * **기술적 지표:** `RSI`, `MACD`, `SMA20`, `Bollinger Bands` 등
      * **펀더멘탈 지표:** `ROA` (총자산순이익률), `DebtRatio` (부채비율)
      * **시장 심리 지표:** `VIX` (변동성 지수), `AnalystRating` (애널리스트 추천 점수)
  * **사용자 입력 지원:** 터미널 실행 시 `--quantity` (보유 수량)와 `--price` (평단가)를 인수로 전달하여, 현재 사용자의 포트폴리오를 기반으로 한 맞춤형 예측을 수행할 수 있습니다.

-----

## ⚙️ 프로젝트 아키텍처

코드는 6개의 파일로 분리되어 있습니다.

  * **`config.py`**: 모든 하이퍼파라미터 및 설정을 관리합니다.
  * **`data_processor.py`**: 데이터 수집, 지표 계산, 정규화를 담당하는 `DataProcessor` 클래스.
  * **`environment.py`**: AI가 상호작용하는 주식 시장 환경인 `MARLStockEnv` (Gymnasium) 클래스.
  * **`replay_buffer.py`**: AI의 경험을 저장하는 `ReplayBuffer` 클래스.
  * **`qmix_model.py`**: QMIX 아키텍처의 모든 신경망 모델 (`Q_Net`, `DQN_Agent`, `Mixer`, `QMIX_Learner`).
  * **`main.py`**: 모든 컴포넌트를 조립하고, 터미널 입력을 받아 학습 및 예측을 실행하는 메인 파일.

-----

## 💡 핵심 개념

### 1\. QMIX (Q-value Mixing)

QMIX는 **"중앙화된 학습, 분산된 실행 (CTDE)"** 패러다임을 따르는 협력적 MARL 알고리즘입니다.

  * **분산된 실행 (Decentralized Execution):** `Agent 0`과 `Agent 1`은 각자 **자신의 관측(Observation)**(시장 + 자신의 수익률)만 보고 `Q_i(o, a)` (개별 Q-Value)를 계산합니다.
  * **중앙화된 학습 (Centralized Training):** '믹서(Mixer)' 네트워크는 **글로벌 상태(State)**(시장 + *모든* 에이전트의 수익률) 정보와 모든 에이전트의 개별 Q-Value를 입력받아, 최종 \*\*팀 Q-Value ($Q_{total}$)\*\*를 계산합니다.

이 구조는 "팀 전체의 가치($Q_{total}$)가 오르면, 개별 에이전트의 가치($Q_i$)도 항상 오른다"는 \*\*단조성(Monotonicity)\*\*을 보장하여 안정적인 학습을 가능하게 합니다.

### 2\. 포트폴리오 상태 확장

기존 모델은 `position = 1` (롱)이라는 사실만 알았습니다. 이는 "80,000원에 산 롱"이든 "95,000원에 산 롱"이든 AI에게는 똑같은 상태였습니다.

이 프로젝트는 `environment.py`에서 \*\*미실현 수익률(P/L %)\*\*을 계산하여 관측(Observation)에 명시적으로 추가합니다.

  * `관측(Obs) = [ (10일치 시장 데이터), (내 포지션 신호), (내 미실현 수익률) ]`

이제 AI는 "95,000원에 샀는데 현재가가 85,000원이라 -10% 손실 중"임을 인지하고 "매도(손절)" 행동의 가치를 높게 평가할 수 있습니다.

-----

## 🛠️ 설치 및 실행

### 1\. 가상 환경 설정 (권장)

프로젝트 폴더에서 터미널을 열고 가상 환경을 생성 및 활성화합니다.

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate
```

### 2\. 필요 라이브러리 설치

`main.py`를 실행하기 위해 필요한 모든 라이브러리를 설치합니다.

```bash
pip install torch numpy pandas yfinance gymnasium pandas-ta ta
```

  * `torch`: 딥러닝 (QMIX 모델)
  * `numpy`, `pandas`: 데이터 처리
  * `yfinance`: 주가 및 재무 데이터 다운로드
  * `gymnasium`: 강화학습 환경
  * `pandas-ta`, `ta`: 기술적 지표 계산

### 3\. 실행 방법

터미널에서 `main.py`를 실행합니다.

#### A. 기본 실행 (포트폴리오 없음)

현재 보유한 주식이 없는 상태(0주, 평단가 0원)에서 분석을 시작합니다.

```bash
python main.py
```

#### B. 포트폴리오 입력 실행

`--quantity` (수량)와 `--price` (평단가) 인수를 사용하여 현재 포트폴리오를 AI에게 알려줍니다.

**예시: 삼성전자를 85,000원에 100주 보유 중일 때**

```bash
python main.py --quantity 100 --price 85000
```

**예시: 삼성전자를 92,000원에 50주 공매도(숏) 보유 중일 때**

```bash
python main.py --quantity -50 --price 92000
```

-----

## 📊 UI 출력 예시

`main.py`를 실행하면 학습(5 에피소드)이 완료된 후, 터미널에 다음과 같은 형식의 최종 분석 결과가 출력됩니다.

```
--- 최종일 예측 분석 중 ---
--- (입력된 포트폴리오: Qnt=100, Pos=Long, Price=85000.0) ---

=============================================
      [ 📱 리브리 AI 분석 결과 (삼성전자) ]
=============================================

--- 1. AI 최종 신호 ---
    보유
    (예상 팀 Q-Value: 586.6508)

--- 2. AI 설명 ---
AI가 '보유'을 결정한 주된 이유는 다음과 같습니다.

  1. 'ROA' 지표의 최근 움직임을 가장 중요하게 고려했습니다.
  2. 'ATR' 지표가 2순위로 결정에 영향을 미쳤습니다.
  3. 마지막으로 'RSI' 지표를 참고했습니다.

--- 3. 기술적 분석 상세 (최종일 기준) ---
    (AI가 입수하여 분석한 원본 데이터입니다.)

    - SMA20        : 93732.50
    - MACD         : 5660.41
    - MACD_Signal  : 5720.38
    - RSI          : 70.86
    ... (이하 생략) ...

    (펀더멘탈 및 기타 데이터)

    - ROA          : 0.12
    - DebtRatio    : 0.35
    - AnalystRating: 0.88

--- 4. (참고) 상세 Q_total 그리드 ---
    (모든 행동 조합의 Q_total 값입니다.)

     (A0)       |     Long     |     Hold     |    Short     (A1)
    --------------------------------------------------
     Long      |     202.2410 |     160.5336 |     135.1229 | 
     Hold      |     -19.7144 |     -19.8094 |     -19.8449 | 
     Short     |     628.3644 |     586.6508 |     561.1838 | 
=============================================
```

-----

## 📂 파일 상세 설명

  * **`main.py`**:

      * `argparse`를 사용해 터미널에서 `--quantity`와 `--price`를 받습니다.
      * `quantity` \> 0 이면 `pos_signal = 1`로 변환하는 등, 사용자 입력을 모델이 이해하는 `user_portfolio` 딕셔너리로 "번역"합니다.
      * `DataProcessor`를 실행해 4가지 데이터(정규화, 원본, 가격, 피처명)를 로드합니다.
      * `MARLStockEnv`와 `QMIX_Learner`를 초기화합니다.
      * `NUM_EPISODES` 만큼 학습 루프를 실행합니다. (이때 `env.reset(initial_portfolio=None)` 호출)
      * 학습 완료 후, `user_portfolio`를 주입하여 `test_env.reset(initial_portfolio=user_portfolio)`를 호출합니다.
      * `test_env`가 끝날 때까지 `epsilon=0.0` (탐욕적)으로 실행하여 최종 상태(`final_obs_dict`)를 얻습니다.
      * `final_obs_dict`를 기반으로 모든 Q-Value 조합과 XAI 분석(`agent_analyses`)을 수행합니다.
      * `print_ui_output` 헬퍼 함수를 호출해 결과를 출력합니다.

  * **`config.py`**:

      * `N_AGENTS`, `TICKER`, `START_DATE`, `LR` 등 모든 주요 설정값을 관리합니다. `NUM_EPISODES`를 500 등으로 늘리면 학습 성능이 향상됩니다.

  * **`data_processor.py`**:

      * `DataProcessor.process()`: `fetch_data` (yf 다운로드), `calculate_features` (지표 계산), `normalize_data` (정규화)를 순차 실행합니다.
      * `calculate_features` 내부에 `yfinance`의 항목명 변경에 대응하기 위한 `try-except` 오류 처리 로직이 포함되어 있습니다. (예: `Total Liabilities Net Minority Interest`)
      * 재무 데이터의 `NaN` 값은 `ffill().fillna(0.0)`을 통해 **미래 시점 누수(Lookahead Bias)** 없이 0으로 채웁니다.

  * **`environment.py`**:

      * `MARLStockEnv.__init__`: `observation_dim`과 `state_dim`을 포트폴리오 상태(`+2`, `+N*2`)만큼 확장합니다.
      * `MARLStockEnv._get_obs_and_state`: **(핵심)** `current_price` (원본 가격)와 `entry_prices`를 비교하여 `unrealized_return_pct`를 계산하고, `np.clip`으로 안정화합니다.
      * `MARLStockEnv.step`: '공동 포트폴리오' (`joint_position`)의 수익을 계산하여 `team_reward`로 반환합니다. 포지션이 **전환**될 때만 (예: -1 -\> 1) `entry_prices`를 `new_price`로 갱신합니다.

  * **`qmix_model.py`**:

      * `DQN_Agent.get_prediction_with_reason`: XAI 계산기. `target_q_value.backward()`를 호출하여 그래디언트를 계산하고, 시장 데이터 부분(`grads[:n_obs_features]`)만 추출하여 중요도를 반환합니다.
      * `Mixer`: `state`를 입력받아 하이퍼네트워크를 통과시켜 `w1`, `b1`, `w2`, `b2` 가중치를 생성합니다. 이 가중치와 개별 `agent_q_values`를 행렬 곱하여 `Q_total`을 계산합니다.
      * `QMIX_Learner.train`: `ReplayBuffer`에서 샘플링한 배치로 QMIX 손실(`F.mse_loss(q_total, target_y)`)을 계산하고, `loss.backward()`를 통해 **Mixer와 모든 Agent의 Q-Net 파라미터**를 동시에 업데이트합니다.

  * **`replay_buffer.py`**:

      * QMIX 학습에 필요한 `(state, [obs...], [actions...], reward, ...)` 튜플을 저장하고 샘플링합니다.
