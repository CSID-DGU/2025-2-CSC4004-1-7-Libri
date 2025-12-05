import torch
import numpy as np
import pickle
import time
import os

from marl_config import (DEVICE, N_AGENTS, WINDOW_SIZE, BUFFER_SIZE, BATCH_SIZE, 
                   TARGET_UPDATE_FREQ, NUM_EPISODES, EPSILON_START, EPSILON_END, 
                   EPSILON_DECAY_STEPS, WARMUP_STEPS)
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner
from replay_buffer import ReplayBuffer

def test_model(learner, test_env, episodes=3):
    total_rewards = []
    for _ in range(episodes):
        obs_dict, info = test_env.reset()
        episode_reward = 0.0
        done = False
        while not done:
            actions_dict = learner.select_actions(obs_dict, epsilon=0.0)
            obs_dict, rewards_dict, dones_dict, _, info = test_env.step(actions_dict)
            episode_reward += rewards_dict['agent_0']
            done = dones_dict['__all__']
        total_rewards.append(episode_reward)
    return np.mean(total_rewards)

def train():
    start_time = time.time()
    print(f"--- 학습 시작 (Device: {DEVICE}) ---")

    # 1. 데이터 처리
    processor = DataProcessor()
    (features_unnormalized_df, prices_df, feature_names,
     agent_0_cols, agent_1_cols, agent_2_cols) = processor.process()

    split_idx = int(len(features_unnormalized_df) * 0.9)
    train_features_unnorm = features_unnormalized_df.iloc[:split_idx]
    train_prices = prices_df.iloc[:split_idx]
    test_features_unnorm = features_unnormalized_df.iloc[split_idx:]
    test_prices = prices_df.iloc[split_idx:]

    # 2. 정규화 및 스케일러 저장 (가장 중요!)
    train_features, test_features = processor.normalize_data(train_features_unnorm, test_features_unnorm)
    
    print("💾 스케일러 저장 중... (scaler.pkl)")
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(processor.scalers, f)

    # 3. 환경 설정
    train_env = MARLStockEnv(train_features, train_prices, agent_0_cols, agent_1_cols, agent_2_cols)
    test_env = MARLStockEnv(test_features, test_prices, agent_0_cols, agent_1_cols, agent_2_cols)

    # 4. 모델 설정
    obs_dims = [train_env.observation_dim_0, train_env.observation_dim_1, train_env.observation_dim_2]
    learner = QMIX_Learner(obs_dims, train_env.action_dim, train_env.state_dim, DEVICE)
    buffer = ReplayBuffer(BUFFER_SIZE, BATCH_SIZE, DEVICE)

    # 5. 학습 루프
    total_steps = 0
    best_test_reward = -np.inf
    
    for i_episode in range(NUM_EPISODES):
        obs_dict, info = train_env.reset()
        global_state = info["global_state"]
        episode_reward = 0
        done = False
        
        while not done:
            total_steps += 1
            if total_steps <= WARMUP_STEPS: epsilon = 1.0
            else: epsilon = max(EPSILON_END, EPSILON_START - (EPSILON_START - EPSILON_END) * (total_steps - WARMUP_STEPS) / EPSILON_DECAY_STEPS)
            
            actions_dict = learner.select_actions(obs_dict, epsilon)
            next_obs_dict, rewards_dict, dones_dict, _, info = train_env.step(actions_dict)
            next_global_state = info["global_state"]
            
            buffer.add(global_state, obs_dict, actions_dict, rewards_dict['agent_0'], next_global_state, next_obs_dict, dones_dict['__all__'])
            
            if total_steps > WARMUP_STEPS and len(buffer) >= BATCH_SIZE:
                learner.train(buffer)
                if total_steps % TARGET_UPDATE_FREQ == 0: learner.update_target_networks()

            obs_dict = next_obs_dict
            global_state = next_global_state
            episode_reward += rewards_dict['agent_0']
            done = dones_dict['__all__']

        # 검증 및 저장
        if (i_episode + 1) % 20 == 0:
            test_reward = test_model(learner, test_env)
            print(f"Ep {i_episode+1} | Train R: {episode_reward:.2f} | Test R: {test_reward:.2f}")
            if test_reward > best_test_reward:
                best_test_reward = test_reward
                torch.save(learner.state_dict(), 'best_model.pth')
                print("   ✅ 최고 모델 저장됨!")

    print(f"--- 학습 완료 (소요시간: {(time.time()-start_time)/60:.1f}분) ---")

if __name__ == "__main__":
    train()