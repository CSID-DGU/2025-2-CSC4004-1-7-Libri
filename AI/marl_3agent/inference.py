import os
import sys
import torch
import pandas as pd
import pickle
import numpy as np

# 🔹 이 파일이 있는 디렉토리 (scaler / best_model 등 위치 기준)
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from marl3_config import DEVICE, WINDOW_SIZE
from data_processor import DataProcessor
from qmix_model import QMIX_Learner
from environment import MARLStockEnv


# -------------------------------------------------------
# 1. utils.py 없으니까 여기서 직접 유틸 함수 구현
# -------------------------------------------------------
def convert_joint_action_to_signal(joint_action, action_map):
    """
    joint_action: [a0, a1, a2]  (각각 0/1/2 같은 액션 인덱스)
    action_map: {0: "Long", 1: "Hold", 2: "Short"}
    -> 최종 "Long"/"Hold"/"Short" 결정 (간단 다수결 룰)
    """
    actions = [action_map.get(a, "Hold") for a in joint_action]

    long_cnt = actions.count("Long")
    short_cnt = actions.count("Short")

    if long_cnt > short_cnt and long_cnt >= 2:
        return "Long"
    elif short_cnt > long_cnt and short_cnt >= 2:
        return "Short"
    else:
        return "Hold"


def generate_ai_explanation(final_signal, agent_analyses):
    """
    간단한 자연어 설명 생성.
    agent_analyses: [(action_idx, q_vals, importance_dict), ...] 형태라고 가정.
    """
    signal_kor = {
        "Long": "매수",
        "Short": "매도",
        "Hold": "관망",
    }.get(final_signal, "관망")

    # 중요한 피처 Top3 정도만 뽑아서 문장화
    reasons = []
    for i, (act_idx, q_vals, importance) in enumerate(agent_analyses):
        if isinstance(importance, dict) and importance:
            # 중요도 상위 2개만
            top_feats = sorted(
                importance.items(), key=lambda x: abs(x[1]), reverse=True
            )[:2]
            feat_desc = ", ".join(f"{k}({v:.2f})" for k, v in top_feats)
            reasons.append(f"에이전트 {i+1}: {feat_desc}")
        else:
            reasons.append(f"에이전트 {i+1}: 주요 지표 기반으로 판단함")

    reasons_text = " / ".join(reasons)

    explanation = (
        f"현재 시장 상황을 종합적으로 고려했을 때, 모델은 '{signal_kor}' 전략을 제안합니다. "
        f"각 에이전트는 자신에게 할당된 기술지표를 기반으로 Q값을 계산했으며, "
        f"주요 근거는 다음과 같습니다: {reasons_text}"
    )
    return explanation


def print_ui_output(
    final_signal,
    explanation,
    last_row_series,
    feature_importance,
    dummy_metric,
    action_labels,
):
    """
    콘솔 디버깅용 출력. (BE에서는 안 써도 되지만, 로컬 확인용으로 남겨둠)
    """
    print("=== [MARL 3-Agent 예측 결과] ===")
    print(f"최종 시그널: {final_signal}")
    print(f"설명: {explanation}")
    print("--- 마지막 날 주요 지표 ---")
    try:
        # pandas Series라고 가정
        for k, v in last_row_series.items():
            print(f"{k}: {v}")
    except Exception:
        print(last_row_series)
    print("=================================")


# -------------------------------------------------------
# 2. 메인 예측 함수
# -------------------------------------------------------
def predict_today():
    # 1. 데이터 준비 (가장 최신 데이터 가져오기)
    processor = DataProcessor()
    (features_df, _, _, a0_cols, a1_cols, a2_cols) = processor.process()
    
    # 2. 스케일러 로드 및 적용
    try:
        scaler_path = os.path.join(BASE_DIR, "scaler.pkl")
        with open(scaler_path, "rb") as f:
            processor.scalers = pickle.load(f)
    except Exception as e:
        print(f"스케일러 파일을 찾을 수 없습니다: {e}")
        return None, None, None

    # 전체 데이터를 정규화 (마지막 데이터가 필요하므로)
    norm_features, _ = processor.normalize_data(features_df, features_df)
    
    # 3. 모델 로드
    # Dummy Env를 만들어 차원 정보 획득
    dummy_env = MARLStockEnv(norm_features.iloc[-50:], None, a0_cols, a1_cols, a2_cols)
    learner = QMIX_Learner(
        [dummy_env.observation_dim_0, dummy_env.observation_dim_1, dummy_env.observation_dim_2],
        dummy_env.action_dim,
        dummy_env.state_dim,
        DEVICE,
    )

    model_path = os.path.join(BASE_DIR, "best_model.pth")
    learner.load_state_dict(torch.load(model_path, map_location=DEVICE))
    learner.eval()  # 평가 모드
    
    # 4. 마지막 시점의 Observation 생성
    last_obs_dict, last_state_info = dummy_env.reset()
    dummy_env.current_step = len(dummy_env.df) - WINDOW_SIZE - 1
    obs_dict, info = dummy_env._get_obs_and_state()
    global_state = info
    
    # 5. 예측 수행 (Q-value 계산)
    action_map = {0: "Long", 1: "Hold", 2: "Short"}
    agent_analyses = []
    
    with torch.no_grad():
        actions = learner.select_actions(obs_dict, epsilon=0.0)
        
        # 설명 가능성(XAI) 추출
        for i, agent in enumerate(learner.agents):
            obs = obs_dict[f"agent_{i}"]
            if i == 0:
                feats = a0_cols
            elif i == 1:
                feats = a1_cols
            else:
                feats = a2_cols
            
            _, q_vals, importance = agent.get_prediction_with_reason(
                obs, feats, WINDOW_SIZE, len(feats)
            )
            agent_analyses.append((actions[f"agent_{i}"], q_vals, importance))

        # Mixer를 통한 Global Q 계산 (여기서는 생략)
        # q_vals_tensor = ...
        # state_tensor = ...
        
    # 6. 결과 종합
    joint_action = [actions[f"agent_{i}"] for i in range(3)]
    final_signal = convert_joint_action_to_signal(joint_action, action_map)
    explanation = generate_ai_explanation(final_signal, agent_analyses)
    
    # 7. 콘솔 출력 (로컬 디버깅용)
    print_ui_output(
        final_signal, 
        explanation, 
        features_df.iloc[-1],
        None,
        0.0,
        ["Long", "Hold", "Short"],
    )

    # 8. 백엔드에서 사용할 수 있도록 결과 반환
    indicators_dict = features_df.iloc[-1].to_dict()
    return final_signal, explanation, indicators_dict


if __name__ == "__main__":
    predict_today()