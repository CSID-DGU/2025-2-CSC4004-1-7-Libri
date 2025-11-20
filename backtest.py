# backtest.py (A2C 수정본)
import os
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import warnings
import joblib

from data_utils import (
    download_data, add_indicators, train_test_split_by_ratio, 
    build_state, FEATURES
)
# (수정) A2CAgent 임포트
from ac_model import A2CAgent 

# --- 금융 성과 지표 계산 함수 (기존과 동일) ---
def calculate_metrics(portfolio_df: pd.DataFrame):
    returns = portfolio_df['A2C_Agent'].pct_change(1).dropna() # (수정) 레이블 변경
    
    sharpe_ratio = 0.0
    if returns.std() != 0:
        sharpe_ratio = (returns.mean() * np.sqrt(252)) / returns.std()
        
    cumulative = (1 + returns).cumprod()
    peak = cumulative.expanding(min_periods=1).max()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    
    negative_returns = returns[returns < 0]
    downside_std = 0.0
    if len(negative_returns) > 0 and negative_returns.std() != 0:
        downside_std = negative_returns.std()
    
    sortino_ratio = 0.0
    if downside_std != 0:
        sortino_ratio = (returns.mean() * np.sqrt(252)) / downside_std

    return {
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Max Drawdown (MDD)": max_drawdown
    }
# ------------------------------------

def run_backtest():
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    print("설정 및 데이터 로드 중...")
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    report_dir = cfg["report_dir"]
    window_size = cfg["window_size"]
    model_cfg = cfg["model_cfg"]

    raw = download_data(cfg["ticker"], cfg["kospi_ticker"], cfg["vix_ticker"],
                        cfg["start_date"], cfg["end_date"])
    df  = add_indicators(raw)
    df_raw_indexed = raw.loc[df.index] 
    train_df, test_df = train_test_split_by_ratio(df, cfg["train_ratio"])
    
    scaler_path = os.path.join(report_dir, "scaler.joblib")
    scaler = joblib.load(scaler_path)
    
    test_df_scaled = test_df.copy()
    test_df_scaled[FEATURES] = scaler.transform(test_df[FEATURES])
    
    test_period_indices = test_df.index
    test_dates = df_raw_indexed.index[test_period_indices]
    original_test_prices = test_df['Close'].values
    original_kospi_prices = test_df['KOSPI'].values

    # 3. (수정) A2C 에이전트 로드
    print(f"학습된 A2C 모델('{cfg['model_path']}') 로드 중...")
    
    dummy_state_dim = len(FEATURES) * window_size + 1
    
    # (수정) A2CAgent 생성
    agent = A2CAgent(
        state_dim=dummy_state_dim,
        action_dim=3,
        hidden_dims=model_cfg.get("hidden_dims", [128, 128]),
        device=cfg.get("device", "cpu")
        # (참고) 백테스트에는 학습 파라미터(gamma, lr 등)는 필요 없음
    )
    agent.load(cfg["model_path"])

    # 4. 백테스트 시뮬레이션
    print("백테스트 시뮬레이션 시작...")
    initial_balance = 10_000_000
    balance = initial_balance
    position_shares = 0.0
    portfolio_values = []
    
    for i in range(window_size - 1, len(test_df_scaled) - 1):
        current_price = original_test_prices[i]
        
        current_portfolio_value = balance + (position_shares * current_price)
        portfolio_values.append(current_portfolio_value)
        
        current_position_flag = 1 if position_shares > 0 else 0
        current_window = test_df_scaled.iloc[i - (window_size - 1) : i + 1]
        state = build_state(current_window, current_position_flag)
        
        # (수정) A2C의 deterministic act 사용
        action, _ = agent.act(state, deterministic=True)
        
        trade_penalty = cfg["trade_penalty"]
        if action == 0 and balance > 0: # Buy
            buy_shares = balance / (current_price * (1 + trade_penalty))
            if buy_shares > 0:
                position_shares += buy_shares
                balance = 0.0
        elif action == 1 and position_shares > 0: # Sell
            balance += position_shares * (current_price * (1 - trade_penalty))
            position_shares = 0.0
        # action == 2 (Hold)
        
    last_price = original_test_prices[-1]
    portfolio_values.append(balance + (position_shares * last_price))

    # 5. 성과 시각화
    print("백테스트 완료. 결과 시각화 중...")
    
    portfolio_df = pd.DataFrame({
        'Date': test_dates[window_size - 1:],
        'A2C_Agent': portfolio_values # (수정) 레이블 변경
    })
    portfolio_df = portfolio_df.set_index('Date')
    
    bh_prices = original_test_prices[window_size - 1:]
    buy_hold_value = (initial_balance / bh_prices[0]) * bh_prices
    portfolio_df['Buy_and_Hold'] = buy_hold_value
    
    kospi_prices = original_kospi_prices[window_size - 1:]
    benchmark_value = (initial_balance / kospi_prices[0]) * kospi_prices
    portfolio_df['KOSPI'] = benchmark_value
    
    metrics = calculate_metrics(portfolio_df) # (수정) 'A2C_Agent' 사용
    print("\n--- A2C 백테스트 성과 지표 ---")
    print(f"  Sharpe Ratio: {metrics['Sharpe Ratio']:.3f}")
    print(f"  Sortino Ratio: {metrics['Sortino Ratio']:.3f}")
    print(f"  Max Drawdown (MDD): {metrics['Max Drawdown (MDD)']:.2%}")
    print("--------------------------\n")

    plt.figure(figsize=(14, 7))
    try: plt.rcParams['font.family'] = 'AppleGothic'; plt.rcParams['axes.unicode_minus'] = False
    except Exception: pass
        
    final_dqn = portfolio_values[-1]
    final_bh = buy_hold_value[-1]
    final_kospi = benchmark_value[-1]

    plt.plot(portfolio_df['A2C_Agent'], label=f"A2C Agent (최종: {final_dqn:,.0f} 원)", linewidth=2)
    plt.plot(portfolio_df['Buy_and_Hold'], label=f"Buy & Hold (최종: {final_bh:,.0f} 원)", linestyle='--')
    plt.plot(portfolio_df['KOSPI'], label=f"KOSPI (최종: {final_kospi:,.0f} 원)", linestyle=':', color='grey')
    
    title = f"A2C 에이전트 백테스트 성과 (초기자본: {initial_balance:,.0f} 원)\n"
    title += f"Sharpe: {metrics['Sharpe Ratio']:.3f} | Sortino: {metrics['Sortino Ratio']:.3f} | MDD: {metrics['Max Drawdown (MDD)']:.2%}"
    
    plt.title(title)
    plt.xlabel("날짜"); plt.ylabel("포트폴리오 가치 (원)")
    plt.legend(); plt.grid(True)
    
    report_path = os.path.join(report_dir, "backtest_performance_a2c.png")
    plt.savefig(report_path, dpi=150)
    print(f"[OK] A2C 백테스트 결과 그래프 저장: {report_path}")

if __name__ == "__main__":
    run_backtest()