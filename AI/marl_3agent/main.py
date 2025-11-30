import argparse
import torch
import numpy as np
import pandas as pd
import time 
import os # 파일 존재 여부 확인용

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


def test_model(learner, test_env, episodes=5):
    """모델 성능을 테스트하는 함수"""
    total_rewards = []
    
    for _ in range(episodes):
        obs_dict, info = test_env.reset(initial_portfolio=None)
        episode_reward = 0.0
        done = False
        
        while not done:
            actions_dict = learner.select_actions(obs_dict, epsilon=0.0)  # greedy
            obs_dict, rewards_dict, dones_dict, _, info = test_env.step(actions_dict)
            episode_reward += rewards_dict['agent_0']
            done = dones_dict['__all__']
        
        total_rewards.append(episode_reward)
    
    return np.mean(total_rewards)


def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="QMIX Stock Trading AI")
    parser.add_argument('--quantity', type=int, default=0, help="현재 보유 주식 수량")
    parser.add_argument('--price', type=float, default=0.0, help="평단가")
    # [추가] test_only 옵션 추가
    parser.add_argument('--test_only', action='store_true', help="학습을 건너뛰고 백테스트만 실행")
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

    split_idx = int(len(features_unnormalized_df) * 0.9)
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

    processor.save_scalers('scalers.pkl')

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

    # ==========================================
    # [수정] 학습 루프 (test_only가 아닐 때만 실행)
    # ==========================================
    if not args.test_only:
        total_steps = 0
        warmup_done = False
        
        episode_rewards = []
        episode_losses = []
        episode_q_values = []
        best_reward = -np.inf
        
        best_test_reward = -np.inf
        no_improve_count = 0
        patience = 5  
        validation_interval = 20  
        early_stop = False
        
        print(f"\n--- QMIX {NUM_EPISODES} 에피소드 학습 시작 ---")
        print(f"--- Obs: A0={obs_dim_0}, A1={obs_dim_1}, A2={obs_dim_2} | State={state_dim} ---")
        print(f"--- Warmup: {WARMUP_STEPS} steps with random actions ---")
        print(f"--- 조기 종료: {validation_interval} 에피소드마다 검증, patience={patience} ---")
        
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
                
                if total_steps <= WARMUP_STEPS:
                    epsilon = 1.0
                    if total_steps == WARMUP_STEPS:
                        print(f"Warmup complete! Starting policy learning...")
                        warmup_done = True
                else:
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
                           
                if warmup_done and len(buffer) >= BATCH_SIZE * 2:
                    num_updates = 2 
                    
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
            
            if episode_team_reward > best_reward:
                best_reward = episode_team_reward

            if warmup_done and i_episode >= 50 and (i_episode + 1) % validation_interval == 0:
                print(f"\n[검증 중... Ep {i_episode+1}]")
                test_reward = test_model(learner, test_env, episodes=3)
                
                if test_reward > best_test_reward:
                    best_test_reward = test_reward
                    torch.save(learner.state_dict(), 'best_model.pth')
                    no_improve_count = 0
                    print(f"✅ 새로운 최고 검증 성능: {test_reward:.2f} (모델 저장됨)")
                else:
                    no_improve_count += 1
                    print(f"⚠️  검증 성능: {test_reward:.2f} (최고: {best_test_reward:.2f}, 정체: {no_improve_count}/{patience})")
                
                if no_improve_count >= patience:
                    print(f"\n🛑 조기 종료: {i_episode + 1} 에피소드에서 학습 중단 (성능 정체)")
                    early_stop = True

            ep_time = time.time() - start_time
            
            if (i_episode + 1) <= 10 or (i_episode + 1) % 10 == 0:
                if len(episode_rewards) >= 10:
                    avg_reward = np.mean(episode_rewards[-10:])
                else:
                    avg_reward = np.mean(episode_rewards)
                
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
            
            if early_stop:
                break
        
        print("--- 학습 완료 ---")
        
        # 학습 곡선 분석 출력
        print("\n--- 학습 곡선 분석 ---")
        if len(episode_rewards) >= 100:
            print(f"    - 초기 100 에피소드 평균: {np.mean(episode_rewards[:100]):.2f}")
            print(f"    - 최종 100 에피소드 평균: {np.mean(episode_rewards[-100:]):.2f}")
        else:
            if len(episode_rewards) > 0:
                print(f"    - 초기 에피소드 평균: {np.mean(episode_rewards[:min(50, len(episode_rewards))]):.2f}")
                print(f"    - 최종 에피소드 평균: {np.mean(episode_rewards[-min(50, len(episode_rewards)):]):.2f}")
        print(f"    - 최고 에피소드 보상: {best_reward:.2f}")
        print(f"    - 최고 검증 보상: {best_test_reward:.2f}")

    else:
        print("\n[알림] '--test_only' 모드: 학습을 건너뜁니다.")

    # ==========================================
    # [수정] 모델 로드 (학습 여부와 상관없이 실행)
    # ==========================================
    model_path = 'best_model.pth'
    if os.path.exists(model_path):
        try:
            print(f"\n모델 로드 중: {model_path}...")
            learner.load_state_dict(torch.load(model_path, map_location=DEVICE))
            print("✅ 모델 로드 성공!")
        except Exception as e:
            print(f"⚠️ 모델 로드 실패: {e}")
            if args.test_only:
                print("오류: 테스트 모드인데 모델을 로드할 수 없습니다.")
                return
    else:
        print(f"⚠️ 경고: {model_path} 파일이 없습니다.")
        if args.test_only:
            print("오류: 테스트 모드인데 모델 파일이 없습니다.")
            return

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
        
        max_drawdown = (reward_series.cumsum() - reward_series.cumsum().cummax()).min()
        
        print(f"    - 백테스트 기간: {test_days} 일")
        print(f"    - 누적 수익: {total_return:.2f}")
        print(f"    - 일 평균 수익: {reward_series.mean():.4f}")
        print(f"    - 일 수익 변동성: {daily_std:.4f}")
        print(f"    - 샤프 비율 (연환산): {sharpe_ratio:.3f}")
        print(f"    - 승률: {win_rate:.2f}% ({win_days}/{test_days} 일)")
        print(f"    - 최대 낙폭(MDD): {max_drawdown:.2f}")
        
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
    
    if test_days > 0:
        print("\n--- [3] Backtest Visualization ---")
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            import matplotlib.font_manager as fm
            import yfinance as yf
            
            # 한글 폰트 설정 (환경에 따라 다를 수 있음)
            try:
                fm.fontManager = fm.FontManager()
                plt.rcParams['font.family'] = 'NanumGothic'
                plt.rcParams['axes.unicode_minus'] = False
            except:
                pass
            
            initial_capital = 10_000_000
            
            cash = initial_capital
            position = 0
            ai_values = [initial_capital]
            
            for step in range(test_days - 1):
                current_price = test_prices.iloc[step + WINDOW_SIZE]
                
                actions = all_actions_log[step]
                joint_action = sum([1 if a == 0 else (-1 if a == 2 else 0) for a in actions])
                
                if joint_action >= 2 and position == 0:
                    shares = cash // current_price
                    position = shares
                    cash -= shares * current_price
                elif joint_action <= -2 and position > 0:
                    cash += position * current_price
                    position = 0
                
                next_price = test_prices.iloc[step + WINDOW_SIZE + 1]
                portfolio_value = cash + (position * next_price)
                ai_values.append(portfolio_value)
            
            initial_shares = initial_capital // test_prices.iloc[WINDOW_SIZE]
            buy_hold_values = []
            for step in range(test_days):
                price = test_prices.iloc[step + WINDOW_SIZE]
                buy_hold_values.append(initial_shares * price)
            
            kospi_values = []
            try:
                test_start = test_prices.index[WINDOW_SIZE]
                test_end = test_prices.index[WINDOW_SIZE + test_days - 1]
                
                print(f"    KOSPI 지수 다운로드 중...")
                
                kospi_df = yf.download('^KS11', 
                                      start=test_start - pd.Timedelta(days=10), 
                                      end=test_end + pd.Timedelta(days=2),
                                      progress=False,
                                      auto_adjust=True)
                
                if not kospi_df.empty:
                    if isinstance(kospi_df.columns, pd.MultiIndex):
                        kospi_close = kospi_df['Close'].iloc[:, 0]
                    else:
                        kospi_close = kospi_df['Close']
                    
                    kospi_df.index = pd.to_datetime(kospi_df.index).tz_localize(None)
                    
                    kospi_aligned = kospi_close.reindex(
                        test_prices.index[WINDOW_SIZE:WINDOW_SIZE + test_days],
                        method='ffill'
                    ).fillna(method='bfill')
                    
                    kospi_start = float(kospi_aligned.iloc[0])
                    
                    for step in range(test_days):
                        kospi_price = float(kospi_aligned.iloc[step])
                        kospi_values.append(initial_capital * (kospi_price / kospi_start))
                    
                    print(f"    ✅ KOSPI 로드 완료 (시작: {kospi_start:.2f})")
                else:
                    raise Exception("KOSPI 데이터 없음")
                
            except Exception as e:
                print(f"    ⚠️  KOSPI 로드 실패: {e}")
                samsung_start = float(test_prices.iloc[WINDOW_SIZE])
                kospi_values = [initial_capital * (float(test_prices.iloc[step + WINDOW_SIZE]) / samsung_start) 
                               for step in range(test_days)]
            
            if isinstance(test_prices.index, pd.DatetimeIndex):
                test_dates = test_prices.iloc[WINDOW_SIZE:WINDOW_SIZE + test_days].index
                use_dates = True
            else:
                test_dates = pd.date_range(start='2024-01-01', periods=test_days, freq='D')
                use_dates = True
            
            ai_final = ai_values[-1]
            bh_final = buy_hold_values[-1]
            kospi_final = kospi_values[-1] if kospi_values else initial_capital
            
            ai_return = (ai_final - initial_capital) / initial_capital * 100
            bh_return = (bh_final - initial_capital) / initial_capital * 100
            kospi_return = (kospi_final - initial_capital) / initial_capital * 100
            
            ai_returns = pd.Series(ai_values).pct_change().dropna()
            sharpe = (ai_returns.mean() / ai_returns.std()) * np.sqrt(252) if len(ai_returns) > 0 else 0
            
            downside_returns = ai_returns[ai_returns < 0]
            sortino = (ai_returns.mean() / downside_returns.std()) * np.sqrt(252) if len(downside_returns) > 0 else 0
            
            cumulative = pd.Series(ai_values)
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max * 100
            mdd = drawdown.min()
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            ax.plot(test_dates, ai_values[:len(test_dates)], 
                   label=f'QMIX Agent (최종: {ai_final:,.0f} 원)', 
                   linewidth=2, color='#1f77b4', linestyle='-')
            ax.plot(test_dates, buy_hold_values[:len(test_dates)], 
                   label=f'Buy & Hold (최종: {bh_final:,.0f} 원)', 
                   linewidth=2, linestyle='--', color='#ff7f0e')
            ax.plot(test_dates, kospi_values[:len(test_dates)], 
                   label=f'KOSPI (최종: {kospi_final:,.0f} 원)', 
                   linewidth=1.5, linestyle=':', color='#808080')
            
            title_text = f'QMIX 백테스트 성과 (초기자금: {initial_capital:,} 원)\n'
            title_text += f'Sharpe: {sharpe:.3f} | Sortino: {sortino:.3f} | MDD: {mdd:.2f}%'
            ax.set_title(title_text, fontsize=13, pad=15)
            
            ax.set_xlabel('날짜', fontsize=11)
            ax.set_ylabel('포트폴리오 가치 (원)', fontsize=11)
            ax.legend(loc='upper left', fontsize=9, framealpha=0.95, fancybox=True, shadow=True)
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)
            
            if use_dates:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
            
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
            
            plt.tight_layout()
            plt.savefig('backtest_result.png', dpi=300, bbox_inches='tight', facecolor='white')
            print("    ✅ 그래프 저장: backtest_result.png")
            plt.close()
            
            daily_profits = np.diff(ai_values)
            plot_dates = test_dates[1:]
            
            if len(plot_dates) == len(daily_profits):
                fig2, ax2 = plt.subplots(figsize=(14, 6))
                colors = ['red' if p > 0 else 'blue' for p in daily_profits]
                ax2.bar(plot_dates, daily_profits, color=colors, alpha=0.7, width=0.8)
                
                ax2.set_title('일별 수익금 추이 (Daily Profit/Loss)', fontsize=15, pad=15)
                ax2.set_ylabel('일별 손익 (원)', fontsize=12)
                ax2.set_xlabel('날짜', fontsize=12)
                
                ax2.axhline(0, color='black', linewidth=0.8, linestyle='-')
                ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
                
                if use_dates:
                    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1)) 
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
                
                max_profit = np.max(daily_profits)
                min_profit = np.min(daily_profits)
                ax2.text(plot_dates[np.argmax(daily_profits)], max_profit, f'{int(max_profit):,}', 
                         ha='center', va='bottom', fontsize=8, color='red')
                ax2.text(plot_dates[np.argmin(daily_profits)], min_profit, f'{int(min_profit):,}', 
                         ha='center', va='top', fontsize=8, color='blue')

                plt.tight_layout()
                plt.savefig('daily_pnl_result.png', dpi=300, bbox_inches='tight', facecolor='white')
                print("    ✅ 그래프 저장: daily_pnl_result.png")
                plt.close()
            else:
                print("    ⚠️  데이터 길이 불일치로 일별 수익금 그래프를 건너뜁니다.")

            print(f"\n--- [3-1] Strategy Comparison ---")
            print(f"    {'Strategy':<20} {'Final Value':>18} {'Return':>10} {'vs KOSPI':>10}")
            print(f"    {'-'*65}")
            print(f"    {'QMIX Agent':<20} {ai_final:>18,.0f} {ai_return:>9.2f}% {ai_return - kospi_return:>9.2f}%")
            print(f"    {'Buy & Hold':<20} {bh_final:>18,.0f} {bh_return:>9.2f}% {bh_return - kospi_return:>9.2f}%")
            print(f"    {'KOSPI':<20} {kospi_final:>18,.0f} {kospi_return:>9.2f}% {0:>9.2f}%")
            print(f"\n    Performance Metrics:")
            print(f"    - Sharpe Ratio: {sharpe:.3f}")
            print(f"    - Sortino Ratio: {sortino:.3f}")
            print(f"    - Max Drawdown: {mdd:.2f}%")
            
        except Exception as e:
            print(f"    ⚠️  그래프 생성 실패: {e}")
            import traceback
            traceback.print_exc()

    print("\n--- [4] 최종일 예측 상세 분석 ---")
    
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