"""
최근 일주일 실전 투자 시뮬레이션
- yfinance에서 최근 7일 데이터 (저가, 고가 포함) 가져오기
- 학습된 QMIX 모델로 매일 매수/매도 신호 생성
- 매수 시 저가에 매수, 매도 시 고가에 매도
- 일주일 수익률 계산 및 출력
"""

import torch
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from config import DEVICE, N_AGENTS, WINDOW_SIZE, TICKER
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner


def fetch_recent_week_data(ticker=TICKER, days=7):
    """최근 N일 데이터 가져오기 (저가, 고가 포함)"""
    end_date = datetime.now()
    # 주말 포함해서 여유있게 가져오기
    start_date = end_date - timedelta(days=days*2)
    
    print(f"\n최근 {days}일 데이터 다운로드 중... ({ticker})")
    df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), 
                     end=end_date.strftime('%Y-%m-%d'), progress=False)
    
    if df.empty:
        raise RuntimeError(f"데이터를 가져올 수 없습니다: {ticker}")
    
    # 최근 N일만 선택
    df = df.tail(days)
    
    print(f"가져온 데이터: {len(df)}일 ({df.index[0].date()} ~ {df.index[-1].date()})")
    return df


def simulate_live_week(model_path='qmix_model.pth', initial_capital=10_000_000, days=7):
    """
    최근 일주일 실전 투자 시뮬레이션
    
    Args:
        model_path: 학습된 모델 경로
        initial_capital: 초기 투자 금액
        days: 시뮬레이션 일수 (기본 7일)
    """
    
    print("\n" + "="*60)
    print("  최근 일주일 AI 투자 시뮬레이션")
    print("="*60)
    print(f"초기 투자 금액: {initial_capital:,.0f}원")
    print(f"시뮬레이션 기간: 최근 {days}일")
    
    # 1. 최근 일주일 실제 데이터 가져오기
    recent_df = fetch_recent_week_data(TICKER, days)
    
    # 2. 학습 데이터로 scaler를 fit하기 위해 과거 데이터 가져오기
    print("\n학습용 과거 데이터 로드 중...")
    processor_train = DataProcessor()
    (train_features_unnorm, train_prices, feature_names,
     agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols) = processor_train.process()
    
    # 3. 최근 일주일 데이터를 동일한 방식으로 새로 처리
    print("\n최근 일주일 데이터를 새로 다운로드하고 처리 중...")
    
    # 최근 데이터의 시작일과 종료일 계산 (WINDOW_SIZE 고려)
    end_date = recent_df.index[-1]
    start_date = end_date - timedelta(days=days + WINDOW_SIZE + 30)  # 여유있게
    
    # 최근 데이터용 processor 생성 (새로 다운로드)
    processor_recent = DataProcessor(
        ticker=TICKER,
        vix_ticker=processor_train.vix_ticker,
        start=start_date.strftime('%Y-%m-%d'),
        end=(end_date + timedelta(days=1)).strftime('%Y-%m-%d')
    )
    
    # 최근 데이터 새로 다운로드 및 처리
    recent_full_df = processor_recent.fetch_data()
    recent_features_unnorm = processor_recent.calculate_features(recent_full_df)
    recent_prices = recent_features_unnorm['Close'].copy()
    recent_features_unnorm = recent_features_unnorm[feature_names]
    
    # 4. 정규화 (학습 데이터로 fit한 scaler 사용)
    print("\n데이터 정규화 중...")
    
    # 학습 데이터의 일부를 train으로 사용 (scaler fit용)
    total_days = len(train_features_unnorm)
    test_days = 252
    split_idx = total_days - test_days
    
    train_for_scaler = train_features_unnorm.iloc[:split_idx]
    
    # Scaler fit & transform
    _, recent_features_norm = processor_train.normalize_data(
        train_for_scaler, 
        recent_features_unnorm
    )
    
    # 5. 최근 일주일만 추출
    available_dates = [d for d in recent_df.index if d in recent_features_norm.index]
    
    if len(available_dates) == 0:
        print("\n오류: 최근 데이터를 처리할 수 없습니다.")
        print(f"요청한 날짜 범위: {recent_df.index[0]} ~ {recent_df.index[-1]}")
        print(f"처리된 데이터 범위: {recent_features_norm.index[0]} ~ {recent_features_norm.index[-1]}")
        return
    
    print(f"\n사용 가능한 날짜: {len(available_dates)}일")
    
    # WINDOW_SIZE를 고려한 데이터 추출
    # 환경이 제대로 작동하려면: WINDOW_SIZE + 시뮬레이션 일수 + 1 이상 필요
    last_date = available_dates[-1]
    last_idx = recent_features_norm.index.get_loc(last_date)
    
    # 필요한 최소 데이터 길이 계산
    required_length = WINDOW_SIZE + len(available_dates) + 1
    start_idx = max(0, last_idx - required_length + 1)
    
    sim_features_norm = recent_features_norm.iloc[start_idx:last_idx+1]
    sim_prices = recent_prices.iloc[start_idx:last_idx+1]
    
    # 데이터 길이 검증
    if len(sim_features_norm) < WINDOW_SIZE + 1:
        print(f"\n오류: 데이터가 부족합니다. 필요: {WINDOW_SIZE + 1}일, 실제: {len(sim_features_norm)}일")
        return
    
    # 6. 환경 생성
    sim_env = MARLStockEnv(
        sim_features_norm, sim_prices,
        agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols,
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    
    # 7. 모델 로드
    obs_dims_list = [
        sim_env.observation_dim_0,
        sim_env.observation_dim_1,
        sim_env.observation_dim_2,
        sim_env.observation_dim_3
    ]
    state_dim = sim_env.state_dim
    action_dim = sim_env.action_dim
    
    learner = QMIX_Learner(obs_dims_list, action_dim, state_dim, DEVICE)
    
    try:
        learner.load_model(model_path)
        print(f"\n모델 로드 완료: {model_path}")
    except Exception as e:
        print(f"\n경고: 모델을 로드할 수 없습니다 ({e}). 랜덤 모델을 사용합니다.")
    
    # 8. 시뮬레이션 실행
    print("\n" + "-"*60)
    print("  일별 거래 시뮬레이션")
    print("-"*60)
    
    # 초기 포트폴리오 설정
    portfolio = {
        'capital': initial_capital,
        'shares': 0,
        'cash': initial_capital
    }
    
    obs_dict, info = sim_env.reset(initial_portfolio=portfolio)
    
    # 시뮬레이션 시작 인덱스 계산
    # 환경의 max_steps = len(data) - WINDOW_SIZE - 1
    # available_dates 시작 지점까지 진행해야 함
    total_data_length = len(sim_features_norm)
    sim_start_step = total_data_length - len(available_dates) - WINDOW_SIZE
    
    # 해당 스텝까지 환경을 진행
    if sim_start_step > 0:
        for _ in range(sim_start_step):
            # Hold 액션으로 진행
            actions_dict = {f'agent_{i}': 1 for i in range(N_AGENTS)}
            obs_dict, _, dones_dict, _, info = sim_env.step(actions_dict)
            if dones_dict['__all__']:
                print("\n경고: 시뮬레이션 시작 전에 환경이 종료되었습니다.")
                return
    
    # 실제 시뮬레이션 기록
    daily_results = []
    action_map = {0: "매수", 1: "보유", 2: "매도"}
    
    for day_idx, date in enumerate(available_dates):
        # 현재 가격 정보
        current_data = recent_df.loc[date]
        close_price = current_data['Close']
        high_price = current_data['High']
        low_price = current_data['Low']
        
        # AI 신호 생성
        actions_dict = learner.select_actions(obs_dict, epsilon=0.0)
        
        # 투표 집계
        votes = []
        for i in range(N_AGENTS):
            action = actions_dict[f'agent_{i}']
            if action == 0:  # Buy
                votes.append(1)
            elif action == 2:  # Sell
                votes.append(-1)
            else:  # Hold
                votes.append(0)
        
        vote_sum = sum(votes)
        
        # 신호 결정
        if vote_sum >= 2:
            final_signal = "매수"
            signal_strength = vote_sum / N_AGENTS
        elif vote_sum <= -2:
            final_signal = "매도"
            signal_strength = abs(vote_sum) / N_AGENTS
        else:
            final_signal = "보유"
            signal_strength = 0.0
        
        # 거래 실행 (저가 매수, 고가 매도)
        old_portfolio_value = portfolio['cash'] + (portfolio['shares'] * close_price)
        trade_price = 0.0
        trade_shares = 0
        
        if final_signal == "매수":
            # 저가에 매수
            trade_price = low_price
            buy_ratio = signal_strength * 0.1  # 총 자산 대비
            buy_amount = old_portfolio_value * buy_ratio
            
            if buy_amount > trade_price and buy_amount <= portfolio['cash']:
                trade_shares = int(buy_amount / trade_price)
                cost = trade_shares * trade_price
                portfolio['shares'] += trade_shares
                portfolio['cash'] -= cost
                
        elif final_signal == "매도":
            # 고가에 매도
            trade_price = high_price
            if portfolio['shares'] > 0:
                sell_ratio = signal_strength * 0.3
                trade_shares = int(portfolio['shares'] * sell_ratio)
                
                if trade_shares > 0:
                    revenue = trade_shares * trade_price
                    portfolio['shares'] -= trade_shares
                    portfolio['cash'] += revenue
        
        # 포트폴리오 가치 계산 (종가 기준)
        new_portfolio_value = portfolio['cash'] + (portfolio['shares'] * close_price)
        daily_pnl = new_portfolio_value - old_portfolio_value
        daily_return = (daily_pnl / old_portfolio_value) * 100 if old_portfolio_value > 0 else 0.0
        
        # 결과 기록
        daily_results.append({
            'date': date.strftime('%Y-%m-%d'),
            'signal': final_signal,
            'votes': f"{vote_sum:+d}",
            'trade_price': trade_price if trade_shares > 0 else 0,
            'trade_shares': trade_shares,
            'close_price': close_price,
            'shares': portfolio['shares'],
            'cash': portfolio['cash'],
            'portfolio_value': new_portfolio_value,
            'daily_pnl': daily_pnl,
            'daily_return': daily_return
        })
        
        # 환경 진행
        obs_dict, _, dones_dict, _, info = sim_env.step(actions_dict)
        
        if dones_dict['__all__']:
            break
    
    # 9. 결과 출력
    print(f"\n{'날짜':<12} {'신호':<6} {'투표':<6} {'거래가':<10} {'거래량':<8} {'종가':<10} {'보유주식':<8} {'현금':<12} {'포트폴리오':<14} {'일수익':<12} {'수익률':<8}")
    print("-"*130)
    
    for result in daily_results:
        print(f"{result['date']:<12} "
              f"{result['signal']:<6} "
              f"{result['votes']:<6} "
              f"{result['trade_price']:>10,.0f} "
              f"{result['trade_shares']:>8,} "
              f"{result['close_price']:>10,.0f} "
              f"{result['shares']:>8,} "
              f"{result['cash']:>12,.0f} "
              f"{result['portfolio_value']:>14,.0f} "
              f"{result['daily_pnl']:>+12,.0f} "
              f"{result['daily_return']:>+7.2f}%")
    
    # 10. 최종 결과 요약
    print("\n" + "="*60)
    print("  최종 결과 요약")
    print("="*60)
    
    final_value = daily_results[-1]['portfolio_value']
    total_pnl = final_value - initial_capital
    total_return = (total_pnl / initial_capital) * 100
    
    win_days = sum(1 for r in daily_results if r['daily_pnl'] > 0)
    lose_days = sum(1 for r in daily_results if r['daily_pnl'] < 0)
    win_rate = (win_days / len(daily_results)) * 100 if daily_results else 0
    
    avg_daily_return = np.mean([r['daily_return'] for r in daily_results])
    
    print(f"초기 투자 금액    : {initial_capital:>14,.0f}원")
    print(f"최종 포트폴리오  : {final_value:>14,.0f}원")
    print(f"총 수익(PnL)     : {total_pnl:>+14,.0f}원")
    print(f"총 수익률        : {total_return:>+13.2f}%")
    print(f"평균 일 수익률   : {avg_daily_return:>+13.2f}%")
    print(f"승률             : {win_rate:>13.1f}% ({win_days}승 {lose_days}패)")
    print(f"최종 보유 주식   : {portfolio['shares']:>14,}주")
    print(f"최종 보유 현금   : {portfolio['cash']:>14,.0f}원")
    print("="*60)
    
    # 11. 벤치마크 비교 (Buy & Hold)
    first_close = recent_df.iloc[0]['Close']
    last_close = recent_df.iloc[-1]['Close']
    benchmark_return = ((last_close - first_close) / first_close) * 100
    
    print(f"\n[벤치마크] Buy & Hold 수익률: {benchmark_return:+.2f}%")
    print(f"[AI 전략] 초과 수익률: {total_return - benchmark_return:+.2f}%p")
    
    return daily_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="최근 일주일 실전 투자 시뮬레이션")
    parser.add_argument('--model', type=str, default='qmix_model.pth', 
                       help="학습된 모델 경로")
    parser.add_argument('--capital', type=float, default=10_000_000, 
                       help="초기 투자 금액 (원)")
    parser.add_argument('--days', type=int, default=7, 
                       help="시뮬레이션 일수")
    
    args = parser.parse_args()
    
    simulate_live_week(
        model_path=args.model,
        initial_capital=args.capital,
        days=args.days
    )
