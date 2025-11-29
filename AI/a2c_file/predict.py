# predict.py (수정본)
import os
import yaml
import numpy as np
import matplotlib.pyplot as plt
import shap
import torch
import warnings
import joblib

# --- 1. data_utils 임포트 ---
from data_utils import (
    download_data, 
    add_indicators, 
    train_test_split_by_ratio, 
    build_state,
    get_feature_names_with_position,
    FEATURES
)

# --- 2. ★★★ 누락된 임포트 추가 ★★★ ---
from trading_env import TradingEnv  # <-- 이 줄이 누락되었습니다.
from dqn_model import DQNAgent      # <-- 이 줄도 누락되었습니다.
# -----------------------------------


# --- 3. ★★★ 추천/설명 함수 정의 ★★★ ---
# (이 함수 정의가 코드에 포함되어야 합니다)
def get_recommendation_and_explanation(
    state: np.ndarray, 
    agent: DQNAgent, 
    explainer: shap.Explainer, 
    feature_names: list,
    save_path: str
) -> (str, dict):
    """
    하나의 state를 받아 [추천]과 [설명(SHAP 값)]을 반환하고,
    설명 그래프를 파일로 저장합니다.
    """
    # 1. 추천(Action) 결정
    with torch.no_grad():
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        qvals = agent.q(state_tensor).numpy()[0]
    action_idx = int(np.argmax(qvals))
    action_map = {0: "Long(매수)", 1: "Short(매도)", 2: "Hold(관망)"}
    recommendation = action_map[action_idx]

    # 2. 설명(SHAP) 계산
    shap_values_for_state = explainer(state.reshape(1, -1)) 
    
    # 3. 추천된 행동에 대한 SHAP 값만 추출
    shap_for_action = shap_values_for_state.values[0, :, action_idx]

    # 4. 결과 반환
    explanation = dict(zip(feature_names, shap_for_action))
    
    # 5. 시각화 및 파일 저장
    plt.figure(figsize=(10, 6))
    order = np.argsort(shap_for_action)
    plt.barh([feature_names[i] for i in order], shap_for_action[order])
    plt.title(f"'{recommendation}' 추천에 대한 SHAP 기여도")
    plt.xlabel("SHAP Value (기여도: +는 지지, -는 방해)")
    plt.tight_layout()
    
    try:
        plt.rcParams['font.family'] = 'AppleGothic'
        plt.rcParams['axes.unicode_minus'] = False 
    except Exception as e:
        print(f"폰트 설정 경고: {e} (한글이 깨질 수 있습니다)")

    plt.savefig(save_path, dpi=150)
    plt.close()
    
    return recommendation, explanation
# -----------------------------------


# --- 4. main 함수 (이하는 기존과 동일) ---
def main():
    # 경고 무시
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    
    # 1. 설정, 데이터 로드
    print("설정 및 데이터 로드 중...")
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    report_dir = cfg["report_dir"]
    os.makedirs(report_dir, exist_ok=True)

    raw = download_data(cfg["ticker"], cfg["kospi_ticker"], cfg["vix_ticker"],
                        cfg["start_date"], cfg["end_date"])
    
    raw_indexed = raw.copy() 
    df  = add_indicators(raw)
    
    train_df, test_df = train_test_split_by_ratio(df, cfg["train_ratio"])
    
    # --- (중요) 스케일러 로드 및 적용 ---
    scaler_path = os.path.join(report_dir, "scaler.joblib")
    try:
        scaler = joblib.load(scaler_path)
        print(f"Scaler 로드 완료: {scaler_path}")
    except FileNotFoundError:
        print(f"오류: Scaler 파일({scaler_path})을 찾을 수 없습니다.")
        print("먼저 'train.py'를 실행하여 모델과 스케일러를 생성해야 합니다.")
        return

    train_df[FEATURES] = scaler.transform(train_df[FEATURES])
    test_df[FEATURES] = scaler.transform(test_df[FEATURES])
    print("데이터 정규화 적용 완료.")
    # -----------------------------------

    # 2. 모델 로드
    print(f"학습된 모델('{cfg['model_path']}') 로드 중...")
    
    # ★★★ 이제 TradingEnv와 DQNAgent를 인식할 수 있습니다 ★★★
    dummy_env = TradingEnv(data=train_df, reward_cfg=cfg.get("reward", {}))
    agent = DQNAgent(
        state_dim=dummy_env.current_state_dim(),
        action_dim=3,
        device=cfg.get("device", "cpu")
    )
    agent.load(cfg["model_path"])
    agent.epsilon = 0.0
    print("모델 로드 완료.")

    # 3. SHAP 설명자 로드
    print("SHAP 배경 데이터(훈련 샘플) 생성 중...")
    bg_env = TradingEnv(data=train_df, reward_cfg=cfg.get("reward", {})) 
    bg_states = []
    bs = bg_env.reset()
    for _ in range(min(100, len(train_df)-1)): 
        bg_states.append(bs)
        ns, _, done2, _ = bg_env.step(2)
        if done2: break
        bs = ns
    bg_states = np.array(bg_states, dtype=np.float32)

    print("SHAP 설명자 생성 중...")
    model_f = lambda x: agent.q(torch.tensor(x, dtype=torch.float32)).detach().numpy()
    explainer = shap.Explainer(model_f, bg_states)
    feature_names = get_feature_names_with_position()
    print("--- 모든 준비 완료 ---")

    # 4. 예측 대상 상태(State) 선정
    target_idx = len(test_df) - 2 
    target_row = test_df.loc[test_df.index[target_idx]] # .loc[test_df.index[...]]로 수정
    
    original_index_pos = test_df.index[target_idx]
    target_date = raw_indexed.index[original_index_pos]

    current_position = 0 
    state_to_explain = build_state(target_row, current_position)

    # 5. 추천 및 설명 요청
    save_path = os.path.join(report_dir, "prediction_explanation.png")

    print(f"\n기준 날짜: {target_date.strftime('%Y-%m-%d')}")
    print(f"그래프 저장 위치: {save_path}")

    # ★★★ 이제 get_recommendation_and_explanation 함수를 인식할 수 있습니다 ★★★
    recommendation, explanation = get_recommendation_and_explanation(
        state_to_explain, agent, explainer, feature_names, save_path
    )

    print(f"\n[최종 추천]: {recommendation}")
    print("--- 추천 근거 (SHAP 값) ---")
    sorted_explanation = sorted(explanation.items(), key=lambda item: item[1], reverse=True)
    for feature, value in sorted_explanation:
        direction = '지지' if value > 0 else '방해'
        print(f"  {feature:<10}: {value:+.4f}  ({direction})")


if __name__ == "__main__":
    main()