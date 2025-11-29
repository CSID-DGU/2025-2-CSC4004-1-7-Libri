import gymnasium as gym
from gymnasium import spaces
import numpy as np
from config import N_AGENTS, WINDOW_SIZE
from collections import deque

class MARLStockEnv(gym.Env):
    def __init__(self, features_df, prices_df, 
                 agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols,
                 n_agents=N_AGENTS, window_size=WINDOW_SIZE):
        super().__init__()
        
        if n_agents != 4:
            print(f"경고: N_AGENTS({n_agents})가 4가 아닙니다. 이 Env 코드는 4-Agent에 맞게 수정되었습니다.")
            
        self.df = features_df
        self.prices = prices_df
        self.window_size = window_size
        self.n_agents = n_agents
        self.max_steps = len(self.df) - self.window_size - 1
        
        all_feature_cols = list(features_df.columns)
        self.agent_0_indices = [all_feature_cols.index(col) for col in agent_0_cols if col in all_feature_cols]
        self.agent_1_indices = [all_feature_cols.index(col) for col in agent_1_cols if col in all_feature_cols]
        self.agent_2_indices = [all_feature_cols.index(col) for col in agent_2_cols if col in all_feature_cols]
        self.agent_3_indices = [all_feature_cols.index(col) for col in agent_3_cols if col in all_feature_cols]
        
        self.n_features_agent_0 = len(self.agent_0_indices)
        self.n_features_agent_1 = len(self.agent_1_indices)
        self.n_features_agent_2 = len(self.agent_2_indices)
        self.n_features_agent_3 = len(self.agent_3_indices)
        self.n_features_global = len(all_feature_cols)

        self.observation_dim_0 = self.window_size * self.n_features_agent_0 + 2
        self.observation_dim_1 = self.window_size * self.n_features_agent_1 + 2
        self.observation_dim_2 = self.window_size * self.n_features_agent_2 + 2
        self.observation_dim_3 = self.window_size * self.n_features_agent_3 + 2
        
        self.state_dim = self.window_size * self.n_features_global + (self.n_agents * 2)
        
        self.observation_space = spaces.Dict({
            'agent_0': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_0,), dtype=np.float32),
            'agent_1': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_1,), dtype=np.float32),
            'agent_2': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_2,), dtype=np.float32),
            'agent_3': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_3,), dtype=np.float32)
        })
        
        self.action_dim = 3
        self.action_space = spaces.Dict({
            f'agent_{i}': spaces.Discrete(self.action_dim) for i in range(self.n_agents)
        })
        
        self.current_step = 0
        self.positions = [0] * self.n_agents
        self.entry_prices = [0.0] * self.n_agents
        
        # 실제 거래 관리
        self.capital = 0.0  # 투자 가능 금액
        self.shares = 0  # 보유 주식 수
        self.cash = 0.0  # 현금 보유액
        
        #샤프 비율 보상을 위한 변동성 계산기
        self.reward_history = deque(maxlen=20) # 최근 20일간의 팀 수익률을 저장
        self.reward_history.append(0.0) # 초기값

    def _get_obs_and_state(self):
        start = self.current_step
        end = start + self.window_size
        
        market_data_global_windowed = self.df.iloc[start:end].values
        
        market_data_agent_0 = market_data_global_windowed[:, self.agent_0_indices]
        market_data_agent_1 = market_data_global_windowed[:, self.agent_1_indices]
        market_data_agent_2 = market_data_global_windowed[:, self.agent_2_indices]
        market_data_agent_3 = market_data_global_windowed[:, self.agent_3_indices]

        market_data_global_flat = market_data_global_windowed.flatten()
        market_data_agent_0_flat = market_data_agent_0.flatten()
        market_data_agent_1_flat = market_data_agent_1.flatten()
        market_data_agent_2_flat = market_data_agent_2.flatten()
        market_data_agent_3_flat = market_data_agent_3.flatten()
            
        current_price = self.prices.iloc[self.current_step + self.window_size - 1]
        
        global_portfolio_state = []
        observations = {}
        
        for i in range(self.n_agents):
            pos_signal = self.positions[i]
            entry_price = self.entry_prices[i]
            
            unrealized_return_pct = 0.0
            if pos_signal == 1 and entry_price != 0:
                unrealized_return_pct = (current_price - entry_price) / entry_price
            elif pos_signal == -1 and entry_price != 0:
                unrealized_return_pct = (entry_price - current_price) / entry_price
            unrealized_return_pct = np.clip(unrealized_return_pct, -1.0, 1.0)
            
            own_portfolio_state = np.array([pos_signal, unrealized_return_pct], dtype=np.float32)
            
            if i == 0:
                obs_flat = market_data_agent_0_flat
            elif i == 1:
                obs_flat = market_data_agent_1_flat
            elif i == 2:
                obs_flat = market_data_agent_2_flat
            else:  # i == 3
                obs_flat = market_data_agent_3_flat
                
            observations[f'agent_{i}'] = np.concatenate([obs_flat, own_portfolio_state])
            global_portfolio_state.append(own_portfolio_state)
            
        global_state = np.concatenate([market_data_global_flat, np.concatenate(global_portfolio_state)])
        return observations, global_state

    def reset(self, seed=None, initial_portfolio=None):
        super().reset(seed=seed)
        self.current_step = 0
        
        if initial_portfolio and 'capital' in initial_portfolio:
            self.capital = initial_portfolio['capital']
            self.shares = initial_portfolio.get('shares', 0)
            self.cash = self.capital  # 초기에는 모두 현금
            
            # 기존 보유 주식이 있다면
            if self.shares > 0:
                current_price = self.prices.iloc[self.current_step + self.window_size - 1]
                self.cash = self.capital - (self.shares * current_price)
        else:
            self.capital = 10_000_000  # 기본 1000만원
            self.shares = 0
            self.cash = self.capital
            
        self.positions = [0] * self.n_agents
        self.entry_prices = [0.0] * self.n_agents
        self.reward_history.clear()
        self.reward_history.append(0.0)
            
        obs, state = self._get_obs_and_state()
        return obs, {"global_state": state}

    def get_state(self):
        _, state = self._get_obs_and_state()
        return state

    def step(self, actions):
        old_price = self.prices.iloc[self.current_step + self.window_size - 1]
        self.current_step += 1
        new_price = self.prices.iloc[self.current_step + self.window_size - 1]
        price_change = new_price - old_price

        # 에이전트들의 투표로 최종 행동 결정
        votes = []
        for i in range(self.n_agents):
            action = actions[f'agent_{i}']
            if action == 0:  # Buy
                votes.append(1)
            elif action == 2:  # Sell
                votes.append(-1)
            else:  # Hold
                votes.append(0)
        
        # 투표 합산 및 신호 강도 계산
        vote_sum = sum(votes)
        
        # 신호 강도에 따른 행동 결정 (2표 이상부터 매수/매도)
        if vote_sum >= 2:
            final_action = 0  # Buy
            signal_strength = vote_sum / self.n_agents  # 0.5 ~ 1.0 (2~4표)
        elif vote_sum <= -2:
            final_action = 2  # Sell
            signal_strength = abs(vote_sum) / self.n_agents  # 0.5 ~ 1.0 (2~4표)
        else:
            final_action = 1  # Hold (투표 -1 ~ +1은 관망)
            signal_strength = 0.0
        
        # 실제 거래 실행
        old_portfolio_value = self.cash + (self.shares * old_price)
        
        if final_action == 0:  # Buy
            # 신호 강도에 비례해서 매수 (총 자산의 최대 15%)
            # 2표=5%, 3표=7.5%, 4표=10%
            buy_ratio = signal_strength * 0.1  # 총 자산 대비
            buy_amount = old_portfolio_value * buy_ratio
            if buy_amount > new_price and buy_amount <= self.cash:
                buy_shares = int(buy_amount / new_price)
                cost = buy_shares * new_price
                self.shares += buy_shares
                self.cash -= cost
                
        elif final_action == 2:  # Sell
            # 신호 강도에 비례해서 매도 (보유 주식의 최대 15%)
            # 2표=15%, 3표=22.5%, 4표=30%
            if self.shares > 0:
                sell_ratio = signal_strength * 0.3
                sell_shares = int(self.shares * sell_ratio)
                if sell_shares > 0:
                    revenue = sell_shares * new_price
                    self.shares -= sell_shares
                    self.cash += revenue
        
        # 1. 포트폴리오 가치 변화로 수익 계산
        new_portfolio_value = self.cash + (self.shares * new_price)
        team_reward_raw = new_portfolio_value - old_portfolio_value  # 실제 금액 수익

        # 2. 수익률(Return) 계산 - 초기 자본 대비로 정규화
        team_return_pct = 0.0
        if self.capital > 1e-6:
            team_return_pct = team_reward_raw / self.capital  # 초기 자본 대비 수익률
        
        self.reward_history.append(team_return_pct)

        # 3. 최근 20일간의 수익 변동성(표준편차) 계산
        daily_volatility = np.std(self.reward_history) + 1e-6

        # 4. 균형잡힌 보상 함수
        # - 수익률에 적절한 가중치 (수익 극대화)
        # - Sharpe 비율 클리핑으로 안정성 확보
        # - 최종 리워드 클리핑으로 학습 안정화
        sharpe_component = team_return_pct / daily_volatility
        sharpe_component = np.clip(sharpe_component, -3.0, 3.0)  # 극단값 방지
        team_reward = (team_return_pct * 1000.0) + (sharpe_component * 0.5)
        team_reward = np.clip(team_reward, -10.0, 10.0)  # 리워드 범위 제한

        rewards = {f'agent_{i}': team_reward for i in range(self.n_agents)}
        
        next_obs, next_state = self._get_obs_and_state()
        done = self.current_step >= self.max_steps
        dones = {f'agent_{i}': done for i in range(self.n_agents)}
        dones['__all__'] = done
        
        info = {
            "global_state": next_state, 
            "raw_pnl": team_reward_raw,
            "portfolio_value": new_portfolio_value,
            "shares": self.shares,
            "cash": self.cash
        }
        
        return next_obs, rewards, dones, False, info
