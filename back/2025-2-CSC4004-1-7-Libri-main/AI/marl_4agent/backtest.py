import argparse
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
import random

from config import (
    DEVICE, N_AGENTS, WINDOW_SIZE
)
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner


# 랜덤 시드 고정 함수
def set_seed(seed=42):
    """재현 가능한 결과를 위한 랜덤 시드 고정"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

# --- 백테스트 결과 그래프 함수 (KOSPI 비교 포함) ---
def plot_backtest_results(portfolio_values, test_prices, initial_capital):
    """백테스트 결과를 시각화하는 함수 (KOSPI 지수 비교 포함)"""
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    dates = test_prices.index[:len(portfolio_values)]
    
    # QMIX Agent 포트폴리오 가치
    qmix_values = np.array(portfolio_values)
    
    # Buy & Hold (삼성전자)
    samsung_start = test_prices.iloc[0]
    shares_bought = initial_capital / samsung_start
    buyhold_values = np.array([shares_bought * price for price in test_prices.iloc[:len(portfolio_values)]])
    
    # KOSPI 지수 다운로드
    kospi_values = None
    try:
        test_start = test_prices.index[0]
        test_end = test_prices.index[len(portfolio_values) - 1]
        print(f"    KOSPI 지수 다운로드 중... ({test_start} ~ {test_end})")
        
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
            kospi_aligned = kospi_close.reindex(dates, method='ffill').fillna(method='bfill')
            
            kospi_start = float(kospi_aligned.iloc[0])
            kospi_values = np.array([initial_capital * (float(price) / kospi_start) for price in kospi_aligned])
            print(f"    ✅ KOSPI 로드 완료 (시작: {kospi_start:.2f})")
    except Exception as e:
        print(f"    ⚠️  KOSPI 로드 실패: {e}")
        kospi_values = buyhold_values.copy()  # 삼성전자로 대체
    
    # 성과 지표 계산
    qmix_returns = pd.Series(qmix_values).pct_change().dropna()
    sharpe = (qmix_returns.mean() / (qmix_returns.std() + 1e-9)) * np.sqrt(252)
    
    downside_returns = qmix_returns[qmix_returns < 0]
    sortino = (qmix_returns.mean() / (downside_returns.std() + 1e-9)) * np.sqrt(252) if len(downside_returns) > 0 else 0
    
    cumulative = pd.Series(qmix_values)
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max * 100
    mdd = drawdown.min()
    
    # 최종 수익률 계산
    qmix_return = (qmix_values[-1] - initial_capital) / initial_capital * 100
    buyhold_return = (buyhold_values[-1] - initial_capital) / initial_capital * 100
    kospi_return = (kospi_values[-1] - initial_capital) / initial_capital * 100 if kospi_values is not None else 0
    
    # 그래프 생성
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 제목
    title = f'QMIX 백테스트 성과 (초기자금: {initial_capital:,.0f} 원)\n'
    title += f'Sharpe: {sharpe:.3f} | Sortino: {sortino:.3f} | MDD: {mdd:.2f}%'
    ax.set_title(title, fontsize=13, pad=15)
    
    # 포트폴리오 가치 플롯
    ax.plot(dates, qmix_values, label=f'QMIX Agent (최종: {qmix_values[-1]:,.0f} 원)', 
            linewidth=2, color='#1f77b4', linestyle='-')
    ax.plot(dates, buyhold_values, label=f'Buy & Hold (최종: {buyhold_values[-1]:,.0f} 원)', 
            linewidth=2, linestyle='--', color='#ff7f0e')
    
    if kospi_values is not None:
        ax.plot(dates, kospi_values, label=f'KOSPI (최종: {kospi_values[-1]:,.0f} 원)', 
                linewidth=1.5, linestyle=':', color='#808080')
    
    # 축 설정
    ax.set_xlabel('날짜', fontsize=11)
    ax.set_ylabel('포트폴리오 가치 (원)', fontsize=11)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # X축 포맷
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    
    # Y축 포맷
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    plt.tight_layout()
    plt.savefig('backtest_result.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return sharpe, sortino, mdd, qmix_return, buyhold_return, kospi_return, qmix_returns, dates[1:]

# --- 일별 수익률 시각화 함수 ---
def plot_daily_returns(daily_returns, dates):
    """일별 수익률을 시각화하는 함수"""
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # 1. 일별 수익률 바 차트
    colors = ['#d62728' if x < 0 else '#2ca02c' for x in daily_returns]
    ax1.bar(dates, daily_returns * 100, color=colors, alpha=0.7, width=0.8)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax1.set_title('일별 수익률 (%)', fontsize=13, pad=15)
    ax1.set_xlabel('날짜', fontsize=11)
    ax1.set_ylabel('수익률 (%)', fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
    ax1.set_axisbelow(True)
    
    # X축 포맷
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0, ha='center')
    
    # 통계 정보 추가
    mean_return = daily_returns.mean() * 100
    std_return = daily_returns.std() * 100
    positive_days = (daily_returns > 0).sum()
    negative_days = (daily_returns < 0).sum()
    win_rate = (positive_days / len(daily_returns)) * 100
    
    textstr = f'평균: {mean_return:.2f}%\n표준편차: {std_return:.2f}%\n승률: {win_rate:.1f}%'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    # 2. 수익률 분포 히스토그램
    ax2.hist(daily_returns * 100, bins=30, color='#1f77b4', alpha=0.7, edgecolor='black')
    ax2.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='0%')
    ax2.axvline(x=mean_return, color='green', linestyle='--', linewidth=1.5, label=f'평균: {mean_return:.2f}%')
    ax2.set_title('수익률 분포', fontsize=13, pad=15)
    ax2.set_xlabel('수익률 (%)', fontsize=11)
    ax2.set_ylabel('빈도', fontsize=11)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, axis='y')
    ax2.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig('daily_returns.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return mean_return, std_return, win_rate

# --- 4개 에이전트의 신호 변환 ---
def convert_joint_action_to_signal(joint_action, action_map):
    action_to_score = {"Long": 1, "Hold": 0, "Short": -1}
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
    return "보유"

# --- AI 설명 생성 ---
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
def print_ui_output(final_signal, ai_explanation, current_indicators, best_q_total_value):
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

# --- 메인 백테스트 함수 ---
def main():
    parser = argparse.ArgumentParser(description="QMIX Stock Trading Backtest (Load Trained Model)")
    parser.add_argument('--capital', type=float, default=10000000, help="투자 금액 (원)")
    parser.add_argument('--model', type=str, default='qmix_model.pth', help="학습된 모델 파일 경로")
    parser.add_argument('--seed', type=int, default=42, help="랜덤 시드 (재현성)")
    args = parser.parse_args()
    
    CAPITAL = args.capital
    MODEL_PATH = args.model
    SEED = args.seed
    
    # 랜덤 시드 고정
    set_seed(SEED)
    
    print(f"\n=== 백테스트 설정 ===")
    print(f"투자 금액: {CAPITAL:,.0f}원")
    print(f"모델 파일: {MODEL_PATH}")
    print(f"랜덤 시드: {SEED}")
    print(f"사용 장치: {DEVICE}")

    # 데이터 로드
    processor = DataProcessor()
    (features_unnormalized_df, prices_df, feature_names,
     agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols) = processor.process()

    # 백테스팅 기간: 마지막 1년 (252 거래일)
    total_days = len(features_unnormalized_df)
    test_days = 252
    split_idx = total_days - test_days
    
    if split_idx < WINDOW_SIZE * 2:
        print("오류: 데이터가 너무 적어 백테스트가 불가능합니다.")
        return

    train_features_unnorm = features_unnormalized_df.iloc[:split_idx]
    test_features_unnorm = features_unnormalized_df.iloc[split_idx:]
    test_prices = prices_df.iloc[split_idx:]
    
    print(f"\n--- 데이터 분할 정보 ---")
    print(f"전체 데이터: {total_days}일")
    print(f"백테스팅 데이터: {len(test_features_unnorm)}일 ({test_prices.index[0]} ~ {test_prices.index[-1]})")

    # 정규화
    train_features, test_features = processor.normalize_data(train_features_unnorm, test_features_unnorm)

    # 환경 생성
    test_env = MARLStockEnv(
        test_features, test_prices, 
        agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols,
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    
    obs_dims_list = [
        test_env.observation_dim_0,
        test_env.observation_dim_1,
        test_env.observation_dim_2,
        test_env.observation_dim_3
    ]
    state_dim = test_env.state_dim
    action_dim = test_env.action_dim

    # 학습된 모델 로드
    print(f"\n--- 학습된 모델 로드 중: {MODEL_PATH} ---")
    learner = QMIX_Learner(obs_dims_list, action_dim, state_dim, DEVICE)
    learner.load_model(MODEL_PATH)

    # 포트폴리오 초기화
    user_portfolio = {
        'capital': CAPITAL,
        'positions': [0] * N_AGENTS,
        'entry_prices': [0.0] * N_AGENTS,
        'shares': 0
    }

    print("\n--- 백테스트 수행 중 ---")
    print(f"--- 초기 투자 금액: {CAPITAL:,.0f}원 ---")
        
    obs_dict, info = test_env.reset(initial_portfolio=user_portfolio)
    global_state = info["global_state"]
    all_team_rewards = []
    all_raw_pnls = []
    portfolio_values = [CAPITAL]
    current_step = 0
    
    while current_step < test_env.max_steps:
        actions_dict = learner.select_actions(obs_dict, 0.0)  # Epsilon = 0.0 (탐험 없음)
        obs_dict, rewards_dict, dones_dict, _, info = test_env.step(actions_dict)
        all_team_rewards.append(rewards_dict['agent_0'])
        all_raw_pnls.append(info["raw_pnl"])
        portfolio_values.append(info["portfolio_value"])
        global_state = info["global_state"]
        current_step += 1
        if dones_dict['__all__']:
            break
    
    final_portfolio_value = portfolio_values[-1]
    final_shares = info["shares"]
    final_cash = info["cash"]

    print("\n--- 백테스트 결과 그래프 생성 중 ---")
    test_days_actual = len(all_team_rewards)
    if test_days_actual > 0:
        try:
            # 포트폴리오 가치 그래프 생성
            sharpe, sortino, mdd, qmix_return, buyhold_return, kospi_return, daily_returns, return_dates = plot_backtest_results(
                portfolio_values, test_prices, CAPITAL
            )
            print("    ✅ 그래프 저장: backtest_result.png")
            
            # 일별 수익률 그래프 생성
            mean_return, std_return, daily_win_rate = plot_daily_returns(daily_returns, return_dates)
            print("    ✅ 그래프 저장: daily_returns.png")
            
            # 성능 비교 테이블
            print(f"\n--- Strategy Comparison ---")
            print(f"    {'Strategy':<20} {'Final Value':>18} {'Return':>10} {'vs KOSPI':>10}")
            print(f"    {'-'*65}")
            print(f"    {'QMIX Agent':<20} {final_portfolio_value:>18,.0f} {qmix_return:>9.2f}% {qmix_return - kospi_return:>9.2f}%")
            print(f"    {'Buy & Hold':<20} {(CAPITAL / test_prices.iloc[0]) * test_prices.iloc[len(portfolio_values)-1]:>18,.0f} {buyhold_return:>9.2f}% {buyhold_return - kospi_return:>9.2f}%")
            print(f"    {'KOSPI':<20} {CAPITAL * (1 + kospi_return/100):>18,.0f} {kospi_return:>9.2f}% {0:>9.2f}%")
            
            # 성능 지표
            print(f"\n    Performance Metrics:")
            print(f"    - Sharpe Ratio: {sharpe:.3f}")
            print(f"    - Sortino Ratio: {sortino:.3f}")
            print(f"    - Max Drawdown: {mdd:.2f}%")
            
            # 일별 수익률 통계
            print(f"\n    Daily Returns Statistics:")
            print(f"    - 평균 일별 수익률: {mean_return:.2f}%")
            print(f"    - 수익률 표준편차: {std_return:.2f}%")
            print(f"    - 일별 승률: {daily_win_rate:.2f}%")
            
            # 추가 통계
            all_raw_pnls_series = pd.Series(all_raw_pnls)
            win_days = (all_raw_pnls_series > 0).sum()
            
            print(f"\n    Trading Statistics:")
            print(f"    - 백테스트 기간: {test_days_actual} 일")
            print(f"    - 수익 발생일: {win_days}일 / 손실 발생일: {test_days_actual - win_days}일")
            print(f"    - 보유 주식: {final_shares} 주")
            print(f"    - 보유 현금: {final_cash:,.0f} 원")
            
        except Exception as e:
            print(f"    ⚠️  그래프 생성 실패: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("    - 백테스트 기간이 0일이어서 성능을 측정할 수 없습니다.")

    # --- 최종일 상세 분석 ---
    print("\n--- 최종일 예측 상세 분석 ---")
    
    final_obs_dict = obs_dict
    action_map = {0: "Long", 1: "Hold", 2: "Short"}
    action_indices = list(action_map.keys())
    
    obs_tensors = [
        torch.FloatTensor(final_obs_dict[f'agent_{i}']).unsqueeze(0).to(DEVICE) 
        for i in range(N_AGENTS)
    ]
    state_tensor = torch.FloatTensor(global_state).unsqueeze(0).to(DEVICE)
    
    q_vals_all_agents = []
    with torch.no_grad():
        for i, agent in enumerate(learner.agents):
            q_vals_all_agents.append(agent.get_q_values(obs_tensors[i]))

    # 4D 그리드 계산
    agent_q_inputs = []
    action_tuples = []
    
    q_vals_0 = q_vals_all_agents[0].squeeze(0)
    q_vals_1 = q_vals_all_agents[1].squeeze(0)
    q_vals_2 = q_vals_all_agents[2].squeeze(0)
    q_vals_3 = q_vals_all_agents[3].squeeze(0)

    for a0_idx in action_indices:
        for a1_idx in action_indices:
            for a2_idx in action_indices:
                for a3_idx in action_indices:
                    q0 = q_vals_0[a0_idx]
                    q1 = q_vals_1[a1_idx]
                    q2 = q_vals_2[a2_idx]
                    q3 = q_vals_3[a3_idx]
                    agent_q_inputs.append(torch.stack([q0, q1, q2, q3]))
                    action_tuples.append((a0_idx, a1_idx, a2_idx, a3_idx))
    
    agent_q_batch = torch.stack(agent_q_inputs) 
    state_batch = state_tensor.repeat(len(action_tuples), 1)

    with torch.no_grad():
        all_q_totals = learner.mixer(agent_q_batch, state_batch)
    
    best_q_total_value = all_q_totals.max().item()
    best_joint_action_idx_flat = all_q_totals.argmax().item()
    best_joint_action_indices = action_tuples[best_joint_action_idx_flat]
    
    # XAI 분석
    agent_analyses = []
    feature_names_list = [agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols]
    n_features_list = [
        test_env.n_features_agent_0, 
        test_env.n_features_agent_1, 
        test_env.n_features_agent_2,
        test_env.n_features_agent_3
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
    
    # UI 포맷으로 출력
    print_ui_output(
        final_signal=final_signal,
        ai_explanation=ai_explanation,
        current_indicators=current_indicator_values,
        best_q_total_value=best_q_total_value
    )

if __name__ == "__main__":
    main()
