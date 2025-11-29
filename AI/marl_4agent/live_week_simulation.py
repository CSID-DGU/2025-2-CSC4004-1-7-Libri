"""
최근 일주일 실전 투자 시뮬레이션 (간소화 버전)
- yfinance에서 최근 7일 데이터 (저가, 고가 포함) 가져오기
- 저장된 scaler로 정규화
- 학습된 QMIX 모델로 매일 매수/매도 신호 생성
- 매수 시 저가에 매수, 매도 시 고가에 매도
"""

import torch
import numpy as np
import pandas as pd
import yfinance as yf
import pickle
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from config import DEVICE, N_AGENTS, WINDOW_SIZE, TICKER
from data_processor import DataProcessor
from environment import MARLStockEnv
from qmix_model import QMIX_Learner


def load_scaler(scaler_path='scaler.pkl'):
    """저장된 scaler 로드"""
    try:
        with open(scaler_path, 'rb') as f:
            scaler_data = pickle.load(f)
        print(f"Scaler 로드 완료: {scaler_path}")
        return scaler_data
    except FileNotFoundError:
        raise FileNotFoundError(
            f"\n오류: {scaler_path} 파일을 찾을 수 없습니다.\n"
            "먼저 'python main.py'로 모델을 학습하여 scaler를 생성하세요."
        )


def normalize_recent_data(df_recent, scaler_data):
    """저장된 scaler로 최근 데이터 정규화"""
    df_norm = df_recent.copy()
    scalers_dict = scaler_data['scalers']
    
    for col in df_norm.columns:
        if col not in scalers_dict:
            continue
            
        scaler_info = scalers_dict[col]
        
        # 1. 가격 기반 정규화
        if isinstance(scaler_info, dict) and scaler_info.get('type') == 'price':
            first_val = scaler_info['first_val']
            df_norm[col] = (df_norm[col] / first_val) - 1.0
            
        # 2. MinMaxScaler
        elif isinstance(scaler_info, MinMaxScaler):
            df_norm[col] = scaler_info.transform(df_norm[[col]])
            
        # 3. StandardScaler
        elif isinstance(scaler_info, StandardScaler):
            df_norm[col] = scaler_info.transform(df_norm[[col]])
            
        # 4. 비율 정규화
        elif isinstance(scaler_info, dict) and scaler_info.get('type') == 'ratio_100':
            df_norm[col] = df_norm[col] / 100.0
            
        # 5. Bollinger_B clipping
        elif isinstance(scaler_info, dict) and scaler_info.get('type') == 'clip_m1_2':
            df_norm[col] = np.clip(df_norm[col], -1, 2)
            
        # 6. Volume_Ratio clipping
        elif isinstance(scaler_info, dict) and scaler_info.get('type') == 'clip_0_5':
            df_norm[col] = np.clip(df_norm[col], 0, 5)
    
    df_norm = df_norm.fillna(0)
    return df_norm


def fetch_and_process_recent_data(days=7, scaler_data=None):
    """최근 데이터 다운로드 및 처리"""
    
    # 1. 최근 데이터 다운로드 (고가/저가 포함)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + WINDOW_SIZE + 90)  # 여유있게
    
    print(f"\n최근 데이터 다운로드 중... ({start_date.date()} ~ {end_date.date()})")
    
    processor = DataProcessor(
        ticker=TICKER,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d')
    )
    
    # 2. 데이터 다운로드 및 feature 계산
    df = processor.fetch_data()
    df_features = processor.calculate_features(df)
    
    # 3. 가격 정보 분리 (고가/저가 포함)
    prices = df_features['Close'].copy()
    high_prices = df_features['High'].copy() if 'High' in df_features else prices
    low_prices = df_features['Low'].copy() if 'Low' in df_features else prices
    
    # 4. Feature만 추출
    feature_names = scaler_data['feature_names']
    df_features = df_features[feature_names].fillna(method='ffill').fillna(0)
    
    # 5. 정규화
    df_features_norm = normalize_recent_data(df_features, scaler_data)
    
    # 6. 최근 N일 추출
    recent_dates = df_features_norm.index[-days:]
    
    if len(recent_dates) < days:
        print(f"경고: 요청한 {days}일 중 {len(recent_dates)}일만 사용 가능합니다.")
    
    # 가격 정보 DataFrame 생성
    price_info = pd.DataFrame({
        'Close': prices,
        'High': high_prices,
        'Low': low_prices
    })
    
    return df_features_norm, prices, price_info, recent_dates, scaler_data


def simulate_live_week(model_path='qmix_model.pth', scaler_path='scaler.pkl', 
                       initial_capital=10_000_000, days=7):
    """최근 일주일 실전 투자 시뮬레이션"""
    
    print("\n" + "="*60)
    print("  최근 일주일 AI 투자 시뮬레이션")
    print("="*60)
    print(f"초기 투자 금액: {initial_capital:,.0f}원")
    print(f"시뮬레이션 기간: 최근 {days}일")
    
    # 1. Scaler 로드
    scaler_data = load_scaler(scaler_path)
    agent_0_cols = scaler_data['agent_0_cols']
    agent_1_cols = scaler_data['agent_1_cols']
    agent_2_cols = scaler_data['agent_2_cols']
    agent_3_cols = scaler_data['agent_3_cols']
    
    # 2. 최근 데이터 가져오기 및 처리
    sim_features, sim_prices, price_info, sim_dates, _ = fetch_and_process_recent_data(
        days=days, 
        scaler_data=scaler_data
    )
    
    print(f"\n처리 완료: {len(sim_features)}일 ({sim_features.index[0].date()} ~ {sim_features.index[-1].date()})")
    print(f"거래 대상: {len(sim_dates)}일")
    
    # 3. 환경 생성
    sim_env = MARLStockEnv(
        sim_features, sim_prices,
        agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols,
        n_agents=N_AGENTS, window_size=WINDOW_SIZE
    )
    
    # 4. 모델 로드
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
        print(f"모델 로드 완료: {model_path}")
    except Exception as e:
        print(f"경고: 모델을 로드할 수 없습니다 ({e}). 랜덤 모델을 사용합니다.")
    
    # 5. 시뮬레이션 시작
    print("\n" + "-"*60)
    print("  일별 거래 시뮬레이션")
    print("-"*60)
    
    portfolio = {
        'capital': initial_capital,
        'shares': 0,
        'cash': initial_capital
    }
    
    obs_dict, info = sim_env.reset(initial_portfolio=portfolio)
    
    # 거래 시작일까지 환경 진행
    first_date = sim_dates[0]
    first_idx = sim_features.index.get_loc(first_date)
    start_idx = max(0, first_idx - WINDOW_SIZE)
    steps_to_skip = first_idx - start_idx
    
    if steps_to_skip > 0:
        for _ in range(steps_to_skip):
            actions_dict = {f'agent_{i}': 1 for i in range(N_AGENTS)}
            obs_dict, _, dones_dict, _, info = sim_env.step(actions_dict)
            if dones_dict['__all__']:
                print("경고: 환경이 예상보다 일찍 종료되었습니다.")
                return
    
    # 6. 실제 거래 시뮬레이션
    daily_results = []
    
    for day_idx, date in enumerate(sim_dates):
        # 현재 가격 정보
        current_prices = price_info.loc[date]
        close_price = current_prices['Close']
        high_price = current_prices['High']
        low_price = current_prices['Low']
        
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
        
        # 거래 실행
        old_portfolio_value = portfolio['cash'] + (portfolio['shares'] * close_price)
        trade_price = 0.0
        trade_shares = 0
        
        if final_signal == "매수":
            trade_price = low_price
            buy_ratio = signal_strength * 0.1
            buy_amount = old_portfolio_value * buy_ratio
            
            if buy_amount > trade_price and buy_amount <= portfolio['cash']:
                trade_shares = int(buy_amount / trade_price)
                cost = trade_shares * trade_price
                portfolio['shares'] += trade_shares
                portfolio['cash'] -= cost
                
        elif final_signal == "매도":
            trade_price = high_price
            if portfolio['shares'] > 0:
                sell_ratio = signal_strength * 0.3
                trade_shares = int(portfolio['shares'] * sell_ratio)
                
                if trade_shares > 0:
                    revenue = trade_shares * trade_price
                    portfolio['shares'] -= trade_shares
                    portfolio['cash'] += revenue
        
        # 포트폴리오 가치 계산
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
    
    # 7. 결과 출력
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
    
    # 8. 최종 결과 요약
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
    
    # 9. 벤치마크 비교
    first_close = price_info.loc[sim_dates[0], 'Close']
    last_close = price_info.loc[sim_dates[-1], 'Close']
    benchmark_return = ((last_close - first_close) / first_close) * 100
    
    print(f"\n[벤치마크] Buy & Hold 수익률: {benchmark_return:+.2f}%")
    print(f"[AI 전략] 초과 수익률: {total_return - benchmark_return:+.2f}%p")
    
    return daily_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="최근 일주일 실전 투자 시뮬레이션")
    parser.add_argument('--model', type=str, default='qmix_model.pth', 
                       help="학습된 모델 경로")
    parser.add_argument('--scaler', type=str, default='scaler.pkl',
                       help="저장된 scaler 경로")
    parser.add_argument('--capital', type=float, default=10_000_000, 
                       help="초기 투자 금액 (원)")
    parser.add_argument('--days', type=int, default=7, 
                       help="시뮬레이션 일수")
    
    args = parser.parse_args()
    
    simulate_live_week(
        model_path=args.model,
        scaler_path=args.scaler,
        initial_capital=args.capital,
        days=args.days
    )
