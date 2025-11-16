import argparse
import torch
import numpy as np
import pandas as pd
import time 

from config import (
    DEVICE, N_AGENTS, WINDOW_SIZE, BUFFER_SIZE, BATCH_SIZE, 
    TARGET_UPDATE_FREQ, NUM_EPISODES, EPSILON_START, EPSILON_END, EPSILON_DECAY_STEPS, WARMUP_STEPS
)
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner
from replay_buffer import ReplayBuffer

def convert_joint_action_to_signal(joint_action, action_map):
    action_to_score = {"Long": 1, "Hold": 0, "Short": -1}
    score = sum(action_to_score[action_map[a]] for a in joint_action)
    
    if score >= 3:
        return "적극 매수"
    elif score > 0:
        return "매수"
    elif score == 0:
        return "보유"
    elif score < 0 and score > -3:
        return "매도"
    elif score <= -3:
        return "적극 매도"
    return "보유"

def generate_ai_explanation(final_signal, agent_analyses):
    all_importances = {}
    for _, _, importance_list in agent_analyses:
        for feature, imp in importance_list:
            all_importances[feature] = all_importances.get(feature, 0.0) + imp
            
    sorted_features = sorted(all_importances.items(), key=lambda item: item[1], reverse=True)
    
    explanation = f"AI가 '{final_signal}'을 결정한 주된 이유는 다음과 같습니다.\n\n"
    
    if not sorted_features:
        return explanation + "데이터 분석 중입니다."
        
    top_feature_1 = sorted_features[0][0]
    explanation += f"  1. '{top_feature_1}' 지표의 최근 움직임을 가장 중요하게 고려했습니다.\n"
    
    if len(sorted_features) > 1:
        top_feature_2 = sorted_features[1][0]
        explanation += f"  2. '{top_feature_2}' 지표가 2순위로 결정에 영향을 미쳤습니다.\n"
        
    if len(sorted_features) > 2:
        top_feature_3 = sorted_features[2][0]
        explanation += f"  3. 마지막으로 '{top_feature_3}' 지표를 참고했습니다.\n"
        
    return explanation

def print_ui_output(
    final_signal, 
    ai_explanation, 
    current_indicators, 
    q_total_grid,
    best_q_total_value, 
    action_names
):
    print("\n\n=============================================")
    print("      [ 📱 리브리 AI 분석 결과 (삼성전자) ]")
    print("=============================================")
    
    print("\n--- 1. AI 최종 신호 ---")
    print(f"    {final_signal}")
    print(f"    (예상 팀 Q-Value: {best_q_total_value:.4f})")
    
    print("\n--- 2. AI 설명 ---")
    print(ai_explanation)
    
    print("\n--- 3. 기술적 분석 상세 (최종일 기준) ---")
    print("    (AI가 입수하여 분석한 원본 데이터입니다.)\n")
    technical_indicators = [
        'SMA20', 'MACD', 'MACD_Signal', 'RSI', 'Stoch_K', 'Stoch_D', 
        'ATR', 'Bollinger_B', 'VIX'
    ]
    fundamental_indicators = ['ROA', 'DebtRatio', 'AnalystRating']
    
    for indicator in technical_indicators:
        if indicator in current_indicators.index:
            print(f"    - {indicator:<13}: {current_indicators[indicator]:.2f}")
            
    print("\n    (펀더멘탈 및 기타 데이터)\n")
    for indicator in fundamental_indicators:
         if indicator in current_indicators.index:
            print(f"    - {indicator:<13}: {current_indicators[indicator]:.2f}")
            
    print("\n--- 4. (참고) 상세 Q_total 그리드 ---")
    print("    (모든 행동 조합의 Q_total 값입니다.)\n")
    
    for k, a2_name in enumerate(action_names):
        print(f"    --- [Agent 2 (시장/펀더멘탈) = {a2_name}] ---")
        col_names = " (A0)       | " + " | ".join([f"{name.center(10)}" for name in action_names]) + " (A1)"
        print("    " + col_names)
        print("    " + "-" * (11 + (13 * len(action_names))))
        
        for i, a0_name in enumerate(action_names):
            row_str = f" {a0_name:<9} | "
            for j in range(len(action_names)):
                row_str += f"{q_total_grid[i, j, k]:>10.4f} | "
            print("    " + row_str)
        print("") 
        
    print("=============================================")


def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="QMIX Stock Trading AI")
    parser.add_argument('--quantity', type=int, default=0, help="현재 보유 주식 수량")
    parser.add_argument('--price', type=float, default=0.0, help="평단가")
    args = parser.parse_args()
    
    pos_signal = 0
    entry_price = 0.0
    if args.quantity > 0: pos_signal = 1
    elif args.quantity < 0: 
        print("경고: 마이너스 수량 → 숏 포지션")
        pos_signal = -1
    if pos_signal != 0: entry_price = args.price
            
    user_portfolio = {
        'positions': [pos_signal] * N_AGENTS,
        'entry_prices': [entry_price] * N_AGENTS
    }

    print(f"사용 장치: {DEVICE}")

    processor = DataProcessor()
    
    (features_unnormalized_df, prices_df, feature_names,
     agent_0_cols, agent_1_cols, agent_2_cols) = processor.process() 

    split_idx = int(len(features_unnormalized_df) * 0.8)
    if split_idx < WINDOW_SIZE * 2:
        print("오류: 데이터가 너무 적습니다.")
        return

    train_features_unnorm = features_unnormalized_df.iloc[:split_idx]
    train_prices = prices_df.iloc[:split_idx]
    test_features_unnorm = features_unnormalized_df.iloc[split_idx:]
    test_prices = prices_df.iloc[split_idx:]

    train_features, test_features = processor.normalize_data(
        train_features_unnorm, 
        test_features_unnorm
    )

    train_env = MARLStockEnv(
        train_features, train_prices, 
        agent_0_cols, agent_1_cols, agent_2_cols,
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    test_env = MARLStockEnv(
        test_features, test_prices, 
        agent_0_cols, agent_1_cols, agent_2_cols,
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    
    obs_dim_0 = train_env.observation_dim_0
    obs_dim_1 = train_env.observation_dim_1
    obs_dim_2 = train_env.observation_dim_2 
    obs_dims_list = [obs_dim_0, obs_dim_1, obs_dim_2]
    
    state_dim = train_env.state_dim
    action_dim = train_env.action_dim
    n_features = train_env.n_features_global

    learner = QMIX_Learner(obs_dims_list, action_dim, state_dim, DEVICE)
    buffer = ReplayBuffer(BUFFER_SIZE, BATCH_SIZE, DEVICE)

    total_steps = 0
    warmup_done = False
    
    # [개선] 학습 통계 추적
    episode_rewards = []
    episode_losses = []
    episode_q_values = []
    best_reward = -np.inf
    
    print(f"\n--- QMIX {NUM_EPISODES} 에피소드 학습 시작 ---")
    print(f"--- Obs: A0={obs_dim_0}, A1={obs_dim_1}, A2={obs_dim_2} | State={state_dim} ---")
    print(f"--- Warmup: {WARMUP_STEPS} steps with random actions ---")
    
    for i_episode in range(NUM_EPISODES):
        obs_dict, info = train_env.reset(initial_portfolio=None) 
        global_state = info["global_state"]
        episode_team_reward = 0.0
        episode_loss = 0.0
        episode_q_val = 0.0
        train_count = 0
        
        done = False
        
        while not done:
            total_steps += 1
            
            # [개선] Warmup phase - random exploration
            if total_steps <= WARMUP_STEPS:
                epsilon = 1.0
                if total_steps == WARMUP_STEPS:
                    print(f"Warmup complete! Starting policy learning...")
                    warmup_done = True
            else:
                # [개선] 선형 감소 Epsilon
                epsilon = max(
                    EPSILON_END, 
                    EPSILON_START - (EPSILON_START - EPSILON_END) * (total_steps - WARMUP_STEPS) / EPSILON_DECAY_STEPS
                )
            
            actions_dict = learner.select_actions(obs_dict, epsilon)
            next_obs_dict, rewards_dict, dones_dict, _, info = train_env.step(actions_dict)
            
            next_global_state = info["global_state"]
            team_reward = rewards_dict['agent_0']
            done = dones_dict['__all__']
            
            buffer.add(global_state, obs_dict, actions_dict, team_reward, 
                       next_global_state, next_obs_dict, done)
                       
            # [개선] 학습은 warmup 후에만 시작
            if warmup_done and len(buffer) >= BATCH_SIZE * 2:
                # 초반에는 더 많이 학습
                num_updates = 8 if i_episode < 50 else 4
                for _ in range(num_updates):
                    loss, q_val = learner.train(buffer)
                    if loss is not None:
                        episode_loss += loss
                        episode_q_val += q_val
                        train_count += 1
            
            episode_team_reward += team_reward
            obs_dict = next_obs_dict
            global_state = next_global_state

            if warmup_done and total_steps % TARGET_UPDATE_FREQ == 0:
                learner.update_target_networks()
        
        episode_rewards.append(episode_team_reward)
        if train_count > 0:
            episode_losses.append(episode_loss / train_count)
            episode_q_values.append(episode_q_val / train_count)
        
        # [개선] Best 모델 저장
        if episode_team_reward > best_reward:
            best_reward = episode_team_reward
            # torch.save(learner.state_dict(), 'best_model.pth')

        # [수정] 매 에피소드마다 출력 + 시간 표시
        ep_time = time.time() - start_time
        
        if (i_episode + 1) <= 10 or (i_episode + 1) % 10 == 0:
            if len(episode_rewards) >= 10:
                avg_reward = np.mean(episode_rewards[-10:])
            else:
                avg_reward = np.mean(episode_rewards)
            
            # Q-value와 Loss 출력 추가
            if len(episode_q_values) > 0:
                avg_q = np.mean(episode_q_values[-10:]) if len(episode_q_values) >= 10 else np.mean(episode_q_values)
                avg_loss = np.mean(episode_losses[-10:]) if len(episode_losses) >= 10 else np.mean(episode_losses)
                print(f"Ep {i_episode+1}/{NUM_EPISODES} | "
                      f"Eps: {epsilon:.3f} | "
                      f"R: {episode_team_reward:.2f} | "
                      f"Avg: {avg_reward:.2f} | "
                      f"Best: {best_reward:.2f} | "
                      f"Q: {avg_q:.2f} | "
                      f"L: {avg_loss:.4f} | "
                      f"Time: {ep_time/60:.1f}m")
            else:
                print(f"Ep {i_episode+1}/{NUM_EPISODES} | "
                      f"Eps: {epsilon:.3f} | "
                      f"R: {episode_team_reward:.2f} | "
                      f"Avg: {avg_reward:.2f} | "
                      f"Best: {best_reward:.2f} | "
                      f"Time: {ep_time/60:.1f}m")

    print("--- 학습 완료 ---")

    # [개선] 학습 곡선 분석
    print("\n--- 학습 곡선 분석 ---")
    if len(episode_rewards) >= 100:
        print(f"    - 초기 100 에피소드 평균: {np.mean(episode_rewards[:100]):.2f}")
        print(f"    - 최종 100 에피소드 평균: {np.mean(episode_rewards[-100:]):.2f}")
    else:
        print(f"    - 초기 50 에피소드 평균: {np.mean(episode_rewards[:min(50, len(episode_rewards))]):.2f}")
        print(f"    - 최종 50 에피소드 평균: {np.mean(episode_rewards[-min(50, len(episode_rewards)):]):.2f}")
    print(f"    - 최고 에피소드 보상: {best_reward:.2f}")

    print("\n--- [1] 전체 테스트 기간 백테스트 ---")
    
    obs_dict, info = test_env.reset(initial_portfolio=user_portfolio)
    global_state = info["global_state"]
    
    all_team_rewards = []
    all_actions_log = []
    
    current_step = 0
    while current_step < test_env.max_steps:
        actions_dict = learner.select_actions(obs_dict, 0.0)
        all_actions_log.append(list(actions_dict.values()))
        
        obs_dict, rewards_dict, dones_dict, _, info = test_env.step(actions_dict)
        
        all_team_rewards.append(rewards_dict['agent_0'])
        
        global_state = info["global_state"]
        current_step += 1
        if dones_dict['__all__']:
            break

    print("\n--- [2] 백테스트 성능 지표 ---")
    test_days = len(all_team_rewards)
    if test_days > 0:
        reward_series = pd.Series(all_team_rewards)
        
        total_return = reward_series.sum()
        daily_std = reward_series.std() + 1e-9
        sharpe_ratio = (reward_series.mean() / daily_std) * np.sqrt(252)
        win_days = (reward_series > 0).sum()
        win_rate = (win_days / test_days) * 100.0
        
        # [개선] 추가 성능 지표
        max_drawdown = (reward_series.cumsum() - reward_series.cumsum().cummax()).min()
        
        print(f"    - 백테스트 기간: {test_days} 일")
        print(f"    - 누적 수익: {total_return:.2f}")
        print(f"    - 일 평균 수익: {reward_series.mean():.4f}")
        print(f"    - 일 수익 변동성: {daily_std:.4f}")
        print(f"    - 샤프 비율 (연환산): {sharpe_ratio:.3f}")
        print(f"    - 승률: {win_rate:.2f}% ({win_days}/{test_days} 일)")
        print(f"    - 최대 낙폭(MDD): {max_drawdown:.2f}")
        
        # [개선] 행동 분포 분석
        actions_array = np.array(all_actions_log)
        print(f"\n    - 행동 분포:")
        for i in range(N_AGENTS):
            agent_actions = actions_array[:, i]
            buy_pct = (agent_actions == 0).sum() / len(agent_actions) * 100
            hold_pct = (agent_actions == 1).sum() / len(agent_actions) * 100
            sell_pct = (agent_actions == 2).sum() / len(agent_actions) * 100
            print(f"      Agent {i}: Buy={buy_pct:.1f}% Hold={hold_pct:.1f}% Sell={sell_pct:.1f}%")
    else:
        print("    - 백테스트 기간이 0일입니다.")

    # --- 최종일 분석 (기존 코드 유지) ---
    print("\n--- [3] 최종일 예측 상세 분석 ---")
    
    final_obs_dict = obs_dict
    action_map = {0: "Long", 1: "Hold", 2: "Short"}
    action_indices = list(action_map.keys())
    action_names = list(action_map.values())
    
    obs_tensors = [torch.FloatTensor(final_obs_dict[f'agent_{i}']).unsqueeze(0).to(DEVICE) for i in range(N_AGENTS)]
    state_tensor = torch.FloatTensor(global_state).unsqueeze(0).to(DEVICE)
    
    q_vals_all_agents = []
    with torch.no_grad():
        for i, agent in enumerate(learner.agents):
            q_vals_all_agents.append(agent.get_q_values(obs_tensors[i]))

    agent_q_inputs = []
    action_tuples = []
    
    q_vals_0 = q_vals_all_agents[0].squeeze(0)
    q_vals_1 = q_vals_all_agents[1].squeeze(0)
    q_vals_2 = q_vals_all_agents[2].squeeze(0)

    for i, a0_idx in enumerate(action_indices):
        for j, a1_idx in enumerate(action_indices):
            for k, a2_idx in enumerate(action_indices): 
                q0 = q_vals_0[a0_idx]
                q1 = q_vals_1[a1_idx]
                q2 = q_vals_2[a2_idx]
                agent_q_inputs.append(torch.stack([q0, q1, q2])) 
                action_tuples.append((a0_idx, a1_idx, a2_idx))
    
    agent_q_batch = torch.stack(agent_q_inputs) 
    state_batch = state_tensor.repeat(len(action_tuples), 1)

    with torch.no_grad():
        all_q_totals = learner.mixer(agent_q_batch, state_batch)
    
    q_total_grid = all_q_totals.view(
        len(action_indices), len(action_indices), len(action_indices) 
    ).cpu().numpy()
    
    best_q_total_value = all_q_totals.max().item()
    best_joint_action_idx_flat = all_q_totals.argmax().item()
    best_joint_action_indices = action_tuples[best_joint_action_idx_flat]
    
    agent_analyses = []
    feature_names_list = [agent_0_cols, agent_1_cols, agent_2_cols] 
    n_features_list = [
        train_env.n_features_agent_0, 
        train_env.n_features_agent_1, 
        train_env.n_features_agent_2
    ]
    
    for i, agent in enumerate(learner.agents):
        obs = final_obs_dict[f'agent_{i}']
        agent_feature_names = feature_names_list[i]
        n_features_agent = n_features_list[i]

        action_idx, q_values, importance = agent.get_prediction_with_reason(
            obs, 
            agent_feature_names,
            WINDOW_SIZE, 
            n_features_agent
        )
        agent_analyses.append((action_idx, q_values, importance))
        
    final_signal = convert_joint_action_to_signal(best_joint_action_indices, action_map)
    ai_explanation = generate_ai_explanation(final_signal, agent_analyses)
    
    current_indicator_values = test_features_unnorm.iloc[-1]
    
    print_ui_output(
        final_signal=final_signal,
        ai_explanation=ai_explanation,
        current_indicators=current_indicator_values,
        q_total_grid=q_total_grid,
        best_q_total_value=best_q_total_value,
        action_names=action_names
    )
    
    end_time = time.time()
    total_time = end_time - start_time
    print("\n=============================================")
    print(f"  [ 📊 총 실행 시간 ]")
    print(f"    {total_time // 60:.0f} 분 {total_time % 60:.2f} 초")
    print("=============================================")


if __name__ == "__main__":
    main()