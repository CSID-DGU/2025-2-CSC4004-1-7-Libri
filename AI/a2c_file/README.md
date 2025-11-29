# (개선판) 설명가능한 A2C 주식 거래 에이전트 (XAI: SHAP)

본 프로젝트는 PyTorch를 사용하여 **A2C (Advantage Actor-Critic)** 강화학습 에이전트를 학습시킵니다. 이는 **Windowed State** (시계열 흐름)를 기반으로 삼성전자 주식의 매수/매도/관망 정책(Policy)을 직접 학습합니다.

학습된 모델은 **복잡한 합성 보상함수(Composite Reward)**를 사용하도록 설계되었으며, **SHAP (KernelExplainer)**을 통해 AI의 **정책(Policy) 결정 근거**를 실시간으로 분석하고 API로 제공하는 것을 목표로 합니다.

## 1. 주요 개선 사항 (v3: DQN -> A2C)

* **Advantage Actor-Critic (A2C)**: DQN(가치 기반)과 달리, 정책(Actor)과 가치(Critic)를 모두 학습하여 더 안정적이고 SOTA에 근접한 성능을 보입니다.
* **On-Policy 학습**: 리플레이 버퍼를 제거하고, 에피소드 전체의 경험(Rollout)을 바탕으로 학습하여 시계열 데이터에 더 적합합니다.
* **엔트로피 보너스**: Actor가 너무 빨리 특정 정책에 수렴하는 것을 방지하고 지속적인 탐험을 장려하기 위해 엔트로피 손실 항을 추가했습니다.
* **XAI for Policy**: SHAP이 Q-value(DQN)가 아닌, Actor가 출력하는 **행동 확률(Policy)**을 직접 설명하도록 수정하여 "왜 이 행동을 다른 행동보다 선호했는지"를 명확히 분석합니다.

## 2. 설치

```bash
pip install -r requirements.txt