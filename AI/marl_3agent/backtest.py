import torch
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from marl_config import DEVICE, N_AGENTS, WINDOW_SIZE
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner

def run_backtest():
    # 1. 데이터 로드 및 전처리 (학습 없이)
    processor = DataProcessor()
    (features_df, prices_df, _, a0_cols, a1_cols, a2_cols) = processor.process()
    
    # 2. 스케일러 로드 (중요!)
    try:
        with open('scaler.pkl', 'rb') as f:
            saved_scalers = pickle.load(f)
            processor.scalers = saved_scalers # 프로세서에 주입
            print("✅ 스케일러 로드 성공")
    except FileNotFoundError:
        print("❌ scaler.pkl 파일이 없습니다. train.py를 먼저 실행하세요.")
        return

    # 테스트 데이터셋 준비 (마지막 10% 또는 전체)
    split_idx = int(len(features_df) * 0.9)
    test_features_unnorm = features_df.iloc[split_idx:]
    test_prices = prices_df.iloc[split_idx:]
    
    # 저장된 스케일러로 정규화만 수행
    _, test_features = processor.normalize_data(features_df.iloc[:split_idx], test_features_unnorm)

    # 3. 환경 및 모델 로드
    env = MARLStockEnv(test_features, test_prices, a0_cols, a1_cols, a2_cols)
    obs_dims = [env.observation_dim_0, env.observation_dim_1, env.observation_dim_2]
    
    learner = QMIX_Learner(obs_dims, env.action_dim, env.state_dim, DEVICE)
    try:
        learner.load_state_dict(torch.load('best_model.pth', map_location=DEVICE))
        print("✅ 모델 로드 성공 (best_model.pth)")
    except FileNotFoundError:
        print("❌ best_model.pth 파일이 없습니다.")
        return

    # 4. 백테스트 실행
    obs_dict, info = env.reset(initial_portfolio={'positions': [0]*3, 'entry_prices': [0.0]*3})
    
    portfolio_values = [10_000_000] # 초기 자금 1000만원
    cash = 10_000_000
    position = 0 # 보유 주식 수
    
    print("--- 백테스트 시작 ---")
    steps = 0
    while True:
        actions = learner.select_actions(obs_dict, epsilon=0.0)
        obs_dict, _, dones, _, info = env.step(actions)
        
        # 간단한 포트폴리오 가치 계산 (검증용)
        current_price = test_prices.iloc[steps + WINDOW_SIZE]
        
        # 합산 행동 계산 (매수/매도 로직은 main.py의 그래프 부분 참조)
        joint_action_score = sum([1 if v==0 else (-1 if v==2 else 0) for v in actions.values()])
        
        if joint_action_score >= 2 and cash > 0: # 매수
            position = cash / current_price
            cash = 0
        elif joint_action_score <= -2 and position > 0: # 매도
            cash = position * current_price
            position = 0
            
        val = cash + (position * current_price)
        portfolio_values.append(val)
        
        steps += 1
        if dones['__all__']: break
        
    # 5. 결과 시각화
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_values, label='AI Portfolio')
    plt.title('Backtest Result')
    plt.legend()
    plt.savefig('backtest_result.png')
    print("📊 그래프 저장 완료: backtest_result.png")

if __name__ == "__main__":
    run_backtest()