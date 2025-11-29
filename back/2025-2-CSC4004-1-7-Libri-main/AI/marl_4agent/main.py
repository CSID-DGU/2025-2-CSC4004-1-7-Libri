import argparse
import torch
from datetime import datetime
import os
import json

from config import (
    DEVICE, N_AGENTS, WINDOW_SIZE, BUFFER_SIZE, BATCH_SIZE, 
    TARGET_UPDATE_FREQ, NUM_EPISODES
)
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner
from replay_buffer import ReplayBuffer

# --- 메인 실행 함수 (학습 전용) ---
def save_checkpoint(learner, episode, total_steps, checkpoint_path='checkpoint.pth'):
    """학습 체크포인트 저장"""
    checkpoint = {
        'episode': episode,
        'total_steps': total_steps,
        'agents': [agent.q_net.state_dict() for agent in learner.agents],
        'mixer': learner.mixer.state_dict(),
        'optimizer': learner.optimizer.state_dict()
    }
    torch.save(checkpoint, checkpoint_path)
    
    # 메타 정보 저장 (JSON)
    meta_path = checkpoint_path.replace('.pth', '_meta.json')
    meta = {
        'episode': episode,
        'total_steps': total_steps,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    
    print(f"체크포인트 저장: Episode {episode}, Steps {total_steps}")

def load_checkpoint(learner, checkpoint_path='checkpoint.pth'):
    """학습 체크포인트 로드"""
    if not os.path.exists(checkpoint_path):
        return 0, 0
    
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    
    for i, agent in enumerate(learner.agents):
        agent.q_net.load_state_dict(checkpoint['agents'][i])
        agent.target_q_net.load_state_dict(checkpoint['agents'][i])
    
    learner.mixer.load_state_dict(checkpoint['mixer'])
    learner.target_mixer.load_state_dict(checkpoint['mixer'])
    learner.optimizer.load_state_dict(checkpoint['optimizer'])
    
    episode = checkpoint.get('episode', 0)
    total_steps = checkpoint.get('total_steps', 0)
    
    print(f"체크포인트 로드: Episode {episode}, Steps {total_steps}")
    return episode, total_steps

def main():
    parser = argparse.ArgumentParser(description="QMIX Stock Trading AI - Training Only")
    parser.add_argument('--load-model', type=str, default=None, help="학습된 모델 파일 경로 (예: qmix_model.pth)")
    parser.add_argument('--resume', action='store_true', help="중단된 학습 재개")
    parser.add_argument('--checkpoint-interval', type=int, default=10, help="체크포인트 저장 간격 (에피소드)")
    args = parser.parse_args()
    
    print(f"\n=== QMIX 학습 모드 ===")
    print(f"사용 장치: {DEVICE}")

    processor = DataProcessor()
    
    # processor.process() 반환값이 7개로 늘어남
    (features_unnormalized_df, prices_df, feature_names,
     agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols) = processor.process()

    # 학습 데이터만 사용 (전체 데이터)
    total_days = len(features_unnormalized_df)
    
    if total_days < WINDOW_SIZE * 2:
        print("오류: 데이터가 너무 적어 학습이 불가능합니다.")
        return

    train_features_unnorm = features_unnormalized_df
    train_prices = prices_df
    
    print(f"\n--- 데이터 정보 ---")
    print(f"학습 데이터: {len(train_features_unnorm)}일 ({train_prices.index[0]} ~ {train_prices.index[-1]})")

    # 정규화 (학습 데이터만)
    train_features, _ = processor.normalize_data(train_features_unnorm, train_features_unnorm)

    # Env 생성자에 피처 목록 전달 (agent_3_cols 추가)
    train_env = MARLStockEnv(
        train_features, train_prices, 
        agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols,
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    
    # obs_dim을 4개 리스트로 관리
    obs_dim_0 = train_env.observation_dim_0
    obs_dim_1 = train_env.observation_dim_1
    obs_dim_2 = train_env.observation_dim_2
    obs_dim_3 = train_env.observation_dim_3
    obs_dims_list = [obs_dim_0, obs_dim_1, obs_dim_2, obs_dim_3]
    
    state_dim = train_env.state_dim
    action_dim = train_env.action_dim
    n_features = train_env.n_features_global

    # Learner에 obs_dims_list 전달
    learner = QMIX_Learner(obs_dims_list, action_dim, state_dim, DEVICE)
    
    # 시작 에피소드 및 스텝 초기화
    start_episode = 0
    total_steps = 0
    
    # 모델 로드 옵션 처리
    if args.resume:
        print("\n--- 중단된 학습 재개 ---")
        start_episode, total_steps = load_checkpoint(learner, 'checkpoint.pth')
        if start_episode == 0:
            print("체크포인트를 찾을 수 없습니다. 처음부터 시작합니다.")
    elif args.load_model:
        print(f"\n--- 학습된 모델 로드 중: {args.load_model} ---")
        learner.load_model(args.load_model)
        print("--- 추가 학습 진행 ---")
    
    # 학습 수행
    buffer = ReplayBuffer(BUFFER_SIZE, BATCH_SIZE, DEVICE)
    
    print(f"\n--- QMIX {NUM_EPISODES} 에피소드 학습 시작 (총 지표: {n_features}개) ---")
    if start_episode > 0:
        print(f"--- Episode {start_episode}부터 재개 (총 스텝: {total_steps}) ---")
    print(f"--- Obs 차원: A0={obs_dim_0} (단기), A1={obs_dim_1} (장기), A2={obs_dim_2} (위험), A3={obs_dim_3} (감성) | 글로벌 상태 차원: {state_dim} ---")
    
    for i_episode in range(start_episode, NUM_EPISODES):
        obs_dict, info = train_env.reset(initial_portfolio=None) 
        global_state = info["global_state"]
        episode_team_reward = 0.0
        done = False
        
        while not done:
            total_steps += 1
            epsilon = max(0.01, 1.0 - total_steps / 50000)
            
            actions_dict = learner.select_actions(obs_dict, epsilon)
            next_obs_dict, rewards_dict, dones_dict, _, info = train_env.step(actions_dict)
            
            next_global_state = info["global_state"]
            team_reward = rewards_dict['agent_0']
            done = dones_dict['__all__']
            
            buffer.add(global_state, obs_dict, actions_dict, team_reward, 
                       next_global_state, next_obs_dict, done)
                       
            learner.train(buffer)
            
            episode_team_reward += team_reward
            obs_dict = next_obs_dict
            global_state = next_global_state

            if total_steps % TARGET_UPDATE_FREQ == 0:
                learner.update_target_networks()

        if (i_episode + 1) % 1 == 0:
            print(f"Episode {i_episode+1}/{NUM_EPISODES} | Epsilon: {epsilon:.3f} | Team Reward: {episode_team_reward:.2f}")
        
        # 체크포인트 저장
        if (i_episode + 1) % args.checkpoint_interval == 0:
            save_checkpoint(learner, i_episode + 1, total_steps, 'checkpoint.pth')

    print("--- 학습 완료 ---")
    
    # 최종 모델 저장
    learner.save_model('qmix_model.pth')
    print("최종 모델 저장 완료: qmix_model.pth")
    print("\n백테스트를 수행하려면 'python backtest.py --model qmix_model.pth' 명령을 실행하세요.")



if __name__ == "__main__":
    main()