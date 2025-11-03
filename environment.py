import gymnasium as gym
from gymnasium import spaces
import numpy as np
from config import N_AGENTS, WINDOW_SIZE

class MARLStockEnv(gym.Env):
    # [수정] 생성자 인자에 agent_0_cols, agent_1_cols 추가
    def __init__(self, features_df, prices_df, agent_0_cols, agent_1_cols, 
                 n_agents=N_AGENTS, window_size=WINDOW_SIZE):
        super().__init__()
        self.df = features_df
        self.prices = prices_df
        self.window_size = window_size
        self.n_agents = n_agents
        self.max_steps = len(self.df) - self.window_size - 1
        
        # [수정] 에이전트별 피처 인덱스 저장
        all_feature_cols = list(features_df.columns)
        self.agent_0_indices = [all_feature_cols.index(col) for col in agent_0_cols if col in all_feature_cols]
        self.agent_1_indices = [all_feature_cols.index(col) for col in agent_1_cols if col in all_feature_cols]
        
        self.n_features_agent_0 = len(self.agent_0_indices)
        self.n_features_agent_1 = len(self.agent_1_indices)
        self.n_features_global = len(all_feature_cols) # 글로벌 상태용

        # [수정] Obs 차원이 에이전트별로 달라짐
        # Obs: Market Data (Sub-set) + Pos Signal (1) + P/L (1)
        self.observation_dim_0 = self.window_size * self.n_features_agent_0 + 2
        self.observation_dim_1 = self.window_size * self.n_features_agent_1 + 2
        
        # State: Market Data (Full-set) + All Agents [Pos Signal(N), P/L(N)]
        self.state_dim = self.window_size * self.n_features_global + (self.n_agents * 2)
        
        # [수정] Observation Space가 에이전트별로 달라짐
        self.observation_space = spaces.Dict({
            'agent_0': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_0,), dtype=np.float32),
            'agent_1': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_1,), dtype=np.float32)
        })
        
        self.action_dim = 3 # (행동은 동일)
        self.action_space = spaces.Dict({
            f'agent_{i}': spaces.Discrete(self.action_dim) for i in range(self.n_agents)
        })
        
        self.current_step = 0
        self.positions = [0] * self.n_agents
        self.entry_prices = [0.0] * self.n_agents
        
    def _get_obs_and_state(self):
        start = self.current_step
        end = start + self.window_size
        
        # (1) 글로벌 상태용 전체 데이터 (Window, N_features_global)
        market_data_global_windowed = self.df.iloc[start:end].values
        
        # (2) 에이전트 0 (단기) 데이터 (Window, N_features_agent_0)
        market_data_agent_0 = market_data_global_windowed[:, self.agent_0_indices]
        
        # (3) 에이전트 1 (장기) 데이터 (Window, N_features_agent_1)
        market_data_agent_1 = market_data_global_windowed[:, self.agent_1_indices]

        # (4) 1차원으로 Flatten
        market_data_global_flat = market_data_global_windowed.flatten()
        market_data_agent_0_flat = market_data_agent_0.flatten()
        market_data_agent_1_flat = market_data_agent_1.flatten()
            
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
            
            # [수정] 에이전트별로 다른 Market Data 주입
            if i == 0:
                observations[f'agent_{i}'] = np.concatenate([market_data_agent_0_flat, own_portfolio_state])
            elif i == 1:
                observations[f'agent_{i}'] = np.concatenate([market_data_agent_1_flat, own_portfolio_state])
            # (N_AGENTS가 2 이상일 경우를 대비한 else/elif 추가 가능)
                
            global_portfolio_state.append(own_portfolio_state)
            
        # 글로벌 상태는 *전체* 마켓 데이터 + *전체* 포트폴리오
        global_state = np.concatenate([market_data_global_flat, np.concatenate(global_portfolio_state)])
            
        return observations, global_state

    def reset(self, seed=None, initial_portfolio=None):
        """
        initial_portfolio (dict, optional): 
            {'positions': [1, 1], 'entry_prices': [80000.0, 80000.0]}
        """
        super().reset(seed=seed)
        self.current_step = 0
        
        if initial_portfolio:
            self.positions = initial_portfolio['positions']
            self.entry_prices = initial_portfolio['entry_prices']
        else:
            self.positions = [0] * self.n_agents
            self.entry_prices = [0.0] * self.n_agents
            
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

        instant_rewards = 0.0
        
        for i in range(self.n_agents):
            action = actions[f'agent_{i}']
            current_pos = self.positions[i]

            if action == 0: # Buy
                if current_pos == -1:
                    instant_rewards += -(new_price - self.entry_prices[i])
                self.positions[i] = 1
                if current_pos != 1: 
                    self.entry_prices[i] = float(new_price)
            elif action == 1: # Hold
                pass
            elif action == 2: # Sell
                if current_pos == 1:
                    instant_rewards += (new_price - self.entry_prices[i])
                self.positions[i] = -1
                if current_pos != -1:
                    self.entry_prices[i] = float(new_price)

        joint_position = sum(self.positions)
        holding_reward = float(joint_position * price_change)
        team_reward = holding_reward + instant_rewards

        rewards = {f'agent_{i}': team_reward for i in range(self.n_agents)}
        
        next_obs, next_state = self._get_obs_and_state()
        done = self.current_step >= self.max_steps
        dones = {f'agent_{i}': done for i in range(self.n_agents)}
        dones['__all__'] = done
        
        return next_obs, rewards, dones, False, {"global_state": next_state}