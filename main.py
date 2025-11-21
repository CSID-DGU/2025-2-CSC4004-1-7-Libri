import argparse
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from config import (
    DEVICE, N_AGENTS, WINDOW_SIZE, BUFFER_SIZE, BATCH_SIZE, 
    TARGET_UPDATE_FREQ, NUM_EPISODES
)
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner
from replay_buffer import ReplayBuffer

# --- 백테스트 결과 그래프 함수 ---
def plot_backtest_results(portfolio_values, daily_pnls, test_prices, initial_capital):
    """백테스트 결과를 시각화하는 함수"""
    dates = test_prices.index[:len(portfolio_values)]
    
    # 성과 지표 계산
    returns = pd.Series(daily_pnls) / initial_capital
    
    # Sharpe Ratio
    sharpe = (returns.mean() / (returns.std() + 1e-9)) * np.sqrt(252)
    
    # Sortino Ratio (하방 변동성만 고려)
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std() if len(downside_returns) > 0 else 1e-9
    sortino = (returns.mean() / (downside_std + 1e-9)) * np.sqrt(252)
    
    # MDD (Maximum Drawdown)
    cumulative = np.array(portfolio_values)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    mdd = drawdown.min() * 100
    
    # KOSPI 벤치마크 (Buy & Hold)
    kospi_start = test_prices.iloc[0]
    kospi_values = [(initial_capital / kospi_start) * price for price in test_prices.iloc[:len(portfolio_values)]]
    
    # 그래프 생성
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 제목과 성과 지표
    title = f'QMIX 4-Agent 백테스트 성과\n초기자금: {initial_capital:,.0f}원 | Sharpe: {sharpe:.3f} | Sortino: {sortino:.3f} | MDD: {mdd:.2f}%'
    fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
    
    # QMIX Agent 포트폴리오
    ax.plot(dates, portfolio_values, label='QMIX Agent', color='#2E86AB', linewidth=2.5, zorder=3)
    
    # KOSPI 벤치마크
    ax.plot(dates, kospi_values, label='KOSPI (Buy & Hold)', color='#A23B72', linewidth=2, linestyle='--', alpha=0.8, zorder=2)
    
    # 초기 자본 기준선
    ax.axhline(y=initial_capital, color='gray', linestyle=':', linewidth=1.5, alpha=0.5, label='초기 자본')
    
    # 축 설정
    ax.set_xlabel('날짜', fontsize=12, fontweight='bold')
    ax.set_ylabel('포트폴리오 가치 (원)', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Y축 포맷 (백만 원 단위)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
    
    # X축 포맷 (2개월 간격)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('backtest_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return sharpe, sortino, mdd

# --- [수정] 4개 에이전트의 신호 변환 ---
def convert_joint_action_to_signal(joint_action, action_map):
    action_to_score = {"Long": 1, "Hold": 0, "Short": -1}
    # (joint_action은 (a0, a1, a2, a3) 튜플이 됨)
    score = sum(action_to_score[action_map[a]] for a in joint_action)
    
    if score >= 3:
        return "적극 매수"
    elif score == 2 or score == 1:
        return "매수"
    elif score == 0:
        return "보유"
    elif score == -1 or score == -2:
        return "매도"
    elif score <= -3:
        return "적극 매도"
    return "보유" # 기본값

# --- (generate_ai_explanation 함수는 수정 불필요) ---
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

# --- UI 출력 함수 ---
def print_ui_output(
    final_signal, 
    ai_explanation, 
    current_indicators, 
    best_q_total_value
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
        
    print("=============================================")


# --- 메인 실행 함수 ---
def main():
    parser = argparse.ArgumentParser(description="QMIX Stock Trading AI")
    parser.add_argument('--capital', type=float, default=10000000, help="투자 금액 (원) (예: 10000000 = 1000만원)")
    args = parser.parse_args()
    
    # 투자 금액 저장
    CAPITAL = args.capital
    print(f"\n=== 투자 설정 ===")
    print(f"투자 금액: {CAPITAL:,.0f}원")
            
    # 포트폴리오는 환경에서 자동 관리
    user_portfolio = {
        'capital': CAPITAL,
        'positions': [0] * N_AGENTS,
        'entry_prices': [0.0] * N_AGENTS,
        'shares': 0  # 보유 주식 수
    }

    print(f"사용 장치: {DEVICE}")

    processor = DataProcessor()
    
    # [수정] 1. processor.process() 반환값이 7개로 늘어남
    (features_unnormalized_df, prices_df, feature_names,
     agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols) = processor.process() # <-- 수정

    # 백테스팅 기간: 마지막 1년 (252 거래일)
    # 학습 기간: 나머지 약 10년
    total_days = len(features_unnormalized_df)
    test_days = 252  # 1년 (약 252 거래일)
    split_idx = total_days - test_days
    
    if split_idx < WINDOW_SIZE * 2:
        print("오류: 데이터가 너무 적어 훈련/테스트 분리가 불가능합니다.")
        return

    train_features_unnorm = features_unnormalized_df.iloc[:split_idx]
    train_prices = prices_df.iloc[:split_idx]
    test_features_unnorm = features_unnormalized_df.iloc[split_idx:]
    test_prices = prices_df.iloc[split_idx:]
    
    print(f"\n--- 데이터 분할 정보 ---")
    print(f"전체 데이터: {total_days}일")
    print(f"학습 데이터: {len(train_features_unnorm)}일 ({train_prices.index[0]} ~ {train_prices.index[-1]})")
    print(f"백테스팅 데이터: {len(test_features_unnorm)}일 ({test_prices.index[0]} ~ {test_prices.index[-1]})")

    # [수정] 2. 정규화
    train_features, test_features = processor.normalize_data(
        train_features_unnorm, 
        test_features_unnorm
    )

    # [수정] 3. Env 생성자에 피처 목록 전달 (agent_3_cols 추가)
    train_env = MARLStockEnv(
        train_features, train_prices, 
        agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols, # <--- 수정
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    test_env = MARLStockEnv(
        test_features, test_prices, 
        agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols, # <--- 수정
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    
    # [수정] 4. obs_dim을 4개 리스트로 관리
    obs_dim_0 = train_env.observation_dim_0
    obs_dim_1 = train_env.observation_dim_1
    obs_dim_2 = train_env.observation_dim_2
    obs_dim_3 = train_env.observation_dim_3 # <--- 추가
    obs_dims_list = [obs_dim_0, obs_dim_1, obs_dim_2, obs_dim_3] # <--- 수정
    
    state_dim = train_env.state_dim
    action_dim = train_env.action_dim
    n_features = train_env.n_features_global

    # [수정] 5. Learner에 obs_dims_list 전달
    learner = QMIX_Learner(obs_dims_list, action_dim, state_dim, DEVICE)
    buffer = ReplayBuffer(BUFFER_SIZE, BATCH_SIZE, DEVICE)

    total_steps = 0
    
    print(f"\n--- QMIX {NUM_EPISODES} 에피소드 학습 시작 (총 지표: {n_features}개) ---")
    # [수정] Obs 차원 4개 출력
    print(f"--- Obs 차원: A0={obs_dim_0} (단기), A1={obs_dim_1} (장기), A2={obs_dim_2} (위험), A3={obs_dim_3} (감성) | 글로벌 상태 차원: {state_dim} ---")
    
    # (학습 루프는 N_AGENTS=3으로 일반화되어 있으므로 수정 불필요)
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

    print("\n--- [1] 전체 테스트 기간 백테스트 수행 중 ---")
    print(f"--- 초기 투자 금액: {CAPITAL:,.0f}원 ---")
        
    obs_dict, info = test_env.reset(initial_portfolio=user_portfolio)
    global_state = info["global_state"]
    all_team_rewards = []
    all_raw_pnls = []  # 실제 금액 기준 수익 추적
    portfolio_values = [CAPITAL]  # 포트폴리오 가치 추적
    current_step = 0
    while current_step < test_env.max_steps:
        actions_dict = learner.select_actions(obs_dict, 0.0) # Epsilon = 0.0
        obs_dict, rewards_dict, dones_dict, _, info = test_env.step(actions_dict)
        all_team_rewards.append(rewards_dict['agent_0'])
        all_raw_pnls.append(info["raw_pnl"])  # 실제 금액 수익 저장
        portfolio_values.append(info["portfolio_value"])
        global_state = info["global_state"]
        current_step += 1
        if dones_dict['__all__']:
            break
    
    final_portfolio_value = portfolio_values[-1]
    final_shares = info["shares"]
    final_cash = info["cash"]

    print("\n--- [2] 백테스트 성능 지표 (신뢰도/정확도) ---")
    test_days = len(all_team_rewards)
    if test_days > 0:
        all_rewards_series = pd.Series(all_team_rewards)
        all_raw_pnls_series = pd.Series(all_raw_pnls)  # 실제 금액 시리즈
        
        total_pnl = all_raw_pnls_series.sum()  # 실제 금액 기준 누적 수익
        daily_avg_pnl = all_raw_pnls_series.mean()  # 실제 금액 기준 일 평균
        daily_std = all_rewards_series.std() + 1e-9
        sharpe_ratio = (all_rewards_series.mean() / daily_std) * np.sqrt(252)
        win_days = (all_raw_pnls_series > 0).sum()  # 실제 수익 기준 승률
        win_rate = (win_days / test_days) * 100.0
        
        total_return_pct = ((final_portfolio_value - CAPITAL) / CAPITAL) * 100
        
        print(f"    - 백테스트 기간    : {test_days} 일")
        print(f"    - 초기 투자 금액   : {CAPITAL:,.0f} 원")
        print(f"    - 최종 포트폴리오  : {final_portfolio_value:,.0f} 원")
        print(f"    - 보유 주식        : {final_shares} 주")
        print(f"    - 보유 현금        : {final_cash:,.0f} 원")
        print(f"    - 누적 수익(PnL)   : {total_pnl:,.0f} 원 ({total_return_pct:+.2f}%)")
        print(f"    - 일 평균 수익     : {daily_avg_pnl:,.0f} 원")
        print(f"    - 일 수익 변동성   : {daily_std:.4f}")
        print(f"    - 샤프 비율 (연환산): {sharpe_ratio:.3f}")
        print(f"    - 승률 (일별)      : {win_rate:.2f}% ({win_days}/{test_days}일)")
        
        # 그래프 출력
        print("\n--- [3] 백테스트 결과 그래프 생성 중 ---")
        graph_sharpe, graph_sortino, graph_mdd = plot_backtest_results(portfolio_values, all_raw_pnls, test_prices, CAPITAL)
        print(f"    Sharpe Ratio: {graph_sharpe:.3f}")
        print(f"    Sortino Ratio: {graph_sortino:.3f}")
        print(f"    MDD: {graph_mdd:.2f}%")
        print("    그래프가 저장되었습니다: backtest_results.png")
    else:
        print("    - 백테스트 기간이 0일이어서 성능을 측정할 수 없습니다.")

    # --- [3] 최종일 상세 분석 ---
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

    # --- [수정] 3D 그리드 계산 (3중 for-loop) ---
    agent_q_inputs = []
    action_tuples = [] # (a0, a1, a2)
    
    q_vals_0 = q_vals_all_agents[0].squeeze(0)
    q_vals_1 = q_vals_all_agents[1].squeeze(0)
    q_vals_2 = q_vals_all_agents[2].squeeze(0)
    q_vals_3 = q_vals_all_agents[3].squeeze(0) # <-- 추가

    for i, a0_idx in enumerate(action_indices):
        for j, a1_idx in enumerate(action_indices):
            for k, a2_idx in enumerate(action_indices):
                for l, a3_idx in enumerate(action_indices): # <-- 추가
                    q0 = q_vals_0[a0_idx]
                    q1 = q_vals_1[a1_idx]
                    q2 = q_vals_2[a2_idx]
                    q3 = q_vals_3[a3_idx] # <-- 추가
                    agent_q_inputs.append(torch.stack([q0, q1, q2, q3])) # <-- 수정
                    action_tuples.append((a0_idx, a1_idx, a2_idx, a3_idx)) # <-- 수정
    
    agent_q_batch = torch.stack(agent_q_inputs) 
    state_batch = state_tensor.repeat(len(action_tuples), 1)

    with torch.no_grad():
        all_q_totals = learner.mixer(agent_q_batch, state_batch)
    
    # [수정] 그리드를 4D (A0, A1, A2, A3)로 변경
    q_total_grid = all_q_totals.view(
        len(action_indices), len(action_indices), len(action_indices), len(action_indices)
    ).cpu().numpy()
    
    best_q_total_value = all_q_totals.max().item()
    best_joint_action_idx_flat = all_q_totals.argmax().item()
    best_joint_action_indices = action_tuples[best_joint_action_idx_flat] # (a0, a1, a2) 튜플
    
    # --- [수정] XAI 파트 4개 에이전트 리스트 ---
    agent_analyses = []
    feature_names_list = [agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols] # <-- 수정
    n_features_list = [
        train_env.n_features_agent_0, 
        train_env.n_features_agent_1, 
        train_env.n_features_agent_2,
        train_env.n_features_agent_3 # <-- 추가
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
    
    # --- UI 포맷으로 출력 ---
    print_ui_output(
        final_signal=final_signal,
        ai_explanation=ai_explanation,
        current_indicators=current_indicator_values,
        best_q_total_value=best_q_total_value
    )

if __name__ == "__main__":
    main()