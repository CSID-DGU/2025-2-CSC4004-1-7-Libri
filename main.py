import argparse
import torch

from config import (
    DEVICE, N_AGENTS, WINDOW_SIZE, BUFFER_SIZE, BATCH_SIZE, 
    TARGET_UPDATE_FREQ, NUM_EPISODES
)
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner
from replay_buffer import ReplayBuffer

# --- UI 출력 헬퍼 함수 ---
def convert_joint_action_to_signal(joint_action, action_map):
    action_to_score = {"Long": 1, "Hold": 0, "Short": -1}
    score = sum(action_to_score[action_map[a]] for a in joint_action)
    
    if score == 2:
        return "적극 매수"
    elif score == 1:
        return "매수"
    elif score == 0:
        return "보유"
    elif score == -1:
        return "매도"
    elif score == -2:
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
        if indicator in current_indicators:
            print(f"    - {indicator:<13}: {current_indicators[indicator]:.2f}")
            
    print("\n    (펀더멘탈 및 기타 데이터)\n")
    for indicator in fundamental_indicators:
        if indicator in current_indicators:
            print(f"    - {indicator:<13}: {current_indicators[indicator]:.2f}")
            
    print("\n--- 4. (참고) 상세 Q_total 그리드 ---")
    print("    (모든 행동 조합의 Q_total 값입니다.)\n")
    
    col_names = " (A0)       | " + " | ".join([f"{name.center(10)}" for name in action_names]) + " (A1)"
    print("    " + col_names)
    print("    " + "-" * (11 + (13 * len(action_names))))
    
    for i, a0_name in enumerate(action_names):
        row_str = f" {a0_name:<9} | "
        for j in range(len(action_names)):
            row_str += f"{q_total_grid[i, j]:>10.4f} | "
        print("    " + row_str)
        
    print("=============================================")


# --- 메인 실행 함수 ---
def main():
    # '수량'과 '평단가' 터미널 인수 파서
    parser = argparse.ArgumentParser(description="QMIX Stock Trading AI")
    parser.add_argument(
        '--quantity', 
        type=int, 
        default=0, 
        help="사용자의 현재 보유 주식 수량 (예: 100)"
    )
    parser.add_argument(
        '--price', 
        type=float, 
        default=0.0, 
        help="사용자의 평단가 (예: 85000)"
    )
    args = parser.parse_args()
    
    # 입력된 인수를 모델 내부 포맷으로 변환
    pos_signal = 0
    entry_price = 0.0
    
    if args.quantity > 0:
        pos_signal = 1
        entry_price = args.price
    elif args.quantity < 0:
        print("경고: 마이너스 수량이 입력되었습니다. '숏' 포지션으로 간주합니다.")
        pos_signal = -1
        entry_price = args.price
    else: # quantity == 0
        pos_signal = 0
        entry_price = 0.0
            
    user_portfolio = {
        'positions': [pos_signal] * N_AGENTS,
        'entry_prices': [entry_price] * N_AGENTS
    }

    print(f"사용 장치: {DEVICE}")

    processor = DataProcessor()
    features_df, features_unnormalized_df, prices_df, feature_names = processor.process()

    split_idx = int(len(features_df) * 0.8)
    if split_idx < WINDOW_SIZE * 2:
        print("오류: 데이터가 너무 적어 훈련/테스트 분리가 불가능합니다.")
        return

    train_features = features_df.iloc[:split_idx]
    train_prices = prices_df.iloc[:split_idx]
    
    test_features = features_df.iloc[split_idx:]
    test_prices = prices_df.iloc[split_idx:]
    test_features_unnormalized = features_unnormalized_df.iloc[split_idx:]

    train_env = MARLStockEnv(train_features, train_prices, n_agents=N_AGENTS, window_size=WINDOW_SIZE)
    test_env = MARLStockEnv(test_features, test_prices, n_agents=N_AGENTS, window_size=WINDOW_SIZE)
    
    obs_dim = train_env.observation_dim
    state_dim = train_env.state_dim
    action_dim = train_env.action_dim
    n_features = train_env.n_features

    learner = QMIX_Learner(obs_dim, action_dim, state_dim, DEVICE)
    buffer = ReplayBuffer(BUFFER_SIZE, BATCH_SIZE, DEVICE)

    total_steps = 0

    print(f"\n--- QMIX {NUM_EPISODES} 에피소드 학습 시작 (총 지표: {n_features}개) ---")
    print(f"--- (확장된) 관측(Obs) 차원: {obs_dim}, 글로벌 상태(State) 차원: {state_dim} ---")
    
    for i_episode in range(NUM_EPISODES):
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

    print("--- 학습 완료 ---")

    print("\n--- 최종일 예측 분석 중 ---")
    
    if user_portfolio['positions'][0] != 0:
        pos_str = "Long" if user_portfolio['positions'][0] == 1 else "Short"
        print(f"--- (입력된 포트폴리오: Qnt={args.quantity}, Pos={pos_str}, Price={args.price}) ---")
    else:
        print("--- (입력된 포트폴리오 없음. 0에서 시작) ---")

    obs_dict, info = test_env.reset(initial_portfolio=user_portfolio)
    global_state = info["global_state"]
    
    current_step = 0
    while current_step < test_env.max_steps:
        actions_dict = learner.select_actions(obs_dict, 0.0) # Epsilon = 0.0
        obs_dict, _, dones_dict, _, info = test_env.step(actions_dict)
        global_state = info["global_state"]
        current_step += 1
        if dones_dict['__all__']:
            break

    # --- 1. UI에 필요한 데이터 계산 ---
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
    action_pairs = []
    
    q_vals_0 = q_vals_all_agents[0].squeeze(0)
    q_vals_1 = q_vals_all_agents[1].squeeze(0)

    for a0_idx in action_indices:
        for a1_idx in action_indices:
            q0 = q_vals_0[a0_idx]
            q1 = q_vals_1[a1_idx]
            agent_q_inputs.append(torch.stack([q0, q1])) 
            action_pairs.append((a0_idx, a1_idx))
    
    agent_q_batch = torch.stack(agent_q_inputs) 
    state_batch = state_tensor.repeat(len(action_pairs), 1)

    with torch.no_grad():
        all_q_totals = learner.mixer(agent_q_batch, state_batch)
    
    q_total_grid = all_q_totals.view(len(action_indices), len(action_indices)).cpu().numpy()
    
    best_q_total_value = all_q_totals.max().item()
    best_joint_action_idx_flat = all_q_totals.argmax().item()
    best_joint_action_indices = action_pairs[best_joint_action_idx_flat]

    agent_analyses = []
    for i, agent in enumerate(learner.agents):
        obs = final_obs_dict[f'agent_{i}']
        action_idx, q_values, importance = agent.get_prediction_with_reason(obs, feature_names, WINDOW_SIZE, n_features)
        agent_analyses.append((action_idx, q_values, importance))

    final_signal = convert_joint_action_to_signal(best_joint_action_indices, action_map)
    ai_explanation = generate_ai_explanation(final_signal, agent_analyses)
    current_indicator_values = test_features_unnormalized.iloc[-1]
    
    # --- 2. UI 포맷으로 출력 ---
    print_ui_output(
        final_signal=final_signal,
        ai_explanation=ai_explanation,
        current_indicators=current_indicator_values,
        q_total_grid=q_total_grid,
        best_q_total_value=best_q_total_value,
        action_names=action_names
    )

if __name__ == "__main__":
    main()