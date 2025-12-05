import torch
import pandas as pd
import pickle
import numpy as np
from marl_config import DEVICE, WINDOW_SIZE
from data_processor import DataProcessor
from qmix_model import QMIX_Learner
from environment import MARLStockEnv
from utils import convert_joint_action_to_signal, generate_ai_explanation, print_ui_output

def predict_today():
    # 1. 데이터 준비 (가장 최신 데이터 가져오기)
    processor = DataProcessor()
    (features_df, _, _, a0_cols, a1_cols, a2_cols) = processor.process()
    
    # 2. 스케일러 로드 및 적용
    try:
        with open('scaler.pkl', 'rb') as f:
            processor.scalers = pickle.load(f)
    except:
        print("스케일러 파일이 없습니다.")
        return

    # 전체 데이터를 정규화 (마지막 데이터가 필요하므로)
    # 실제로는 마지막 윈도우만큼만 필요하지만 편의상 전체 변환 후 마지막 사용
    norm_features, _ = processor.normalize_data(features_df, features_df)
    
    # 3. 모델 로드
    # Dummy Env를 만들어 차원 정보 획득
    dummy_env = MARLStockEnv(norm_features.iloc[-50:], None, a0_cols, a1_cols, a2_cols)
    learner = QMIX_Learner(
        [dummy_env.observation_dim_0, dummy_env.observation_dim_1, dummy_env.observation_dim_2],
        dummy_env.action_dim, dummy_env.state_dim, DEVICE
    )
    learner.load_state_dict(torch.load('best_model.pth', map_location=DEVICE))
    learner.eval() # 평가 모드
    
    # 4. 마지막 시점의 Observation 생성
    # (Environment의 내부 로직을 빌려 사용)
    last_obs_dict, last_state_info = dummy_env.reset()
    # 실제로는 reset이 아니라 마지막 데이터를 넣어야 함.
    # Env 구조상 마지막 step으로 강제 이동하거나 직접 텐서를 만들어야 함.
    # 여기서는 가장 간단하게 Env를 마지막 시점으로 이동시킴
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
            obs = obs_dict[f'agent_{i}']
            # 각 에이전트별 피처 이름 매핑
            if i==0: feats = a0_cols
            elif i==1: feats = a1_cols
            else: feats = a2_cols
            
            _, q_vals, importance = agent.get_prediction_with_reason(
                obs, feats, WINDOW_SIZE, len(feats)
            )
            agent_analyses.append((actions[f'agent_{i}'], q_vals, importance))

        # Mixer를 통한 Global Q 계산
        q_vals_tensor = torch.stack([a[1] for a in agent_analyses]).unsqueeze(0).to(DEVICE)
        state_tensor = torch.FloatTensor(global_state).unsqueeze(0).to(DEVICE)
        # (단순화를 위해 여기서는 Mixer 호출 생략하고 개별 액션만으로 판단 가능)
        # 정확한 팀 Q-Value는 Mixer를 통과해야 함
        
    # 6. 결과 종합
    joint_action = [actions[f'agent_{i}'] for i in range(3)]
    final_signal = convert_joint_action_to_signal(joint_action, action_map)
    explanation = generate_ai_explanation(final_signal, agent_analyses)
    
    # 7. 출력
    print_ui_output(
        final_signal, 
        explanation, 
        features_df.iloc[-1], # 정규화 안 된 원본 수치 출력
        None, 0.0, ["Long", "Hold", "Short"]
    )

if __name__ == "__main__":
    predict_today()