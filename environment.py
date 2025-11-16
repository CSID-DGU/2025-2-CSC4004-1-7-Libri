import gymnasium as gym
from gymnasium import spaces
import numpy as np
from config import N_AGENTS, WINDOW_SIZE, REWARD_SCALE

class MARLStockEnv(gym.Env):
    def __init__(self, features_df, prices_df, 
                 agent_0_cols, agent_1_cols, agent_2_cols, 
                 n_agents=N_AGENTS, window_size=WINDOW_SIZE):
        super().__init__()
        
        if n_agents != 3:
            print(f"경고: N_AGENTS({n_agents})가 3이 아닙니다.")
            
        self.df = features_df
        self.prices = prices_df
        self.window_size = window_size
        self.n_agents = n_agents
        self.max_steps = len(self.df) - self.window_size - 1
        
        all_feature_cols = list(features_df.columns)
        self.agent_0_indices = [all_feature_cols.index(col) for col in agent_0_cols if col in all_feature_cols]
        self.agent_1_indices = [all_feature_cols.index(col) for col in agent_1_cols if col in all_feature_cols]
        self.agent_2_indices = [all_feature_cols.index(col) for col in agent_2_cols if col in all_feature_cols]
        
        self.n_features_agent_0 = len(self.agent_0_indices)
        self.n_features_agent_1 = len(self.agent_1_indices)
        self.n_features_agent_2 = len(self.agent_2_indices)
        self.n_features_global = len(all_feature_cols)

        self.observation_dim_0 = self.window_size * self.n_features_agent_0 + 2
        self.observation_dim_1 = self.window_size * self.n_features_agent_1 + 2
        self.observation_dim_2 = self.window_size * self.n_features_agent_2 + 2
        
        self.state_dim = self.window_size * self.n_features_global + (self.n_agents * 2)
        
        self.observation_space = spaces.Dict({
            'agent_0': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_0,), dtype=np.float32),
            'agent_1': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_1,), dtype=np.float32),
            'agent_2': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim_2,), dtype=np.float32)
        })
        
        self.action_dim = 3
        self.action_space = spaces.Dict({
            f'agent_{i}': spaces.Discrete(self.action_dim) for i in range(self.n_agents)
        })
        
        self.current_step = 0
        self.positions = [0] * self.n_agents
        self.entry_prices = [0.0] * self.n_agents
        
        # [개선] 누적 보상 추적
        self.episode_returns = []

    def _get_obs_and_state(self):
        start = self.current_step
        end = start + self.window_size
        
        market_data_global_windowed = self.df.iloc[start:end].values
        
        market_data_agent_0 = market_data_global_windowed[:, self.agent_0_indices]
        market_data_agent_1 = market_data_global_windowed[:, self.agent_1_indices]
        market_data_agent_2 = market_data_global_windowed[:, self.agent_2_indices]

        market_data_global_flat = market_data_global_windowed.flatten()
        market_data_agent_0_flat = market_data_agent_0.flatten()
        market_data_agent_1_flat = market_data_agent_1.flatten()
        market_data_agent_2_flat = market_data_agent_2.flatten()
            
        current_price = self.prices.iloc[self.current_step + self.window_size - 1]
        
        global_portfolio_state = []
        observations = {}
        
        for i in range(self.n_agents):
            pos_signal = self.positions[i]
            entry_price = self.entry_prices[i]
            
            unrealized_return_pct = 0.0
            if pos_signal == 1 and entry_price != 0:
                unrealized_return_pct = (current_price - entry_price) / (entry_price + 1e-9)
            elif pos_signal == -1 and entry_price != 0:
                unrealized_return_pct = (entry_price - current_price) / (entry_price + 1e-9)
            unrealized_return_pct = np.clip(unrealized_return_pct, -1.0, 1.0)
            
            own_portfolio_state = np.array([pos_signal, unrealized_return_pct], dtype=np.float32)
            
            if i == 0:
                obs_flat = market_data_agent_0_flat
            elif i == 1:
                obs_flat = market_data_agent_1_flat
            elif i == 2:
                obs_flat = market_data_agent_2_flat
            else:
                obs_flat = market_data_global_flat
                
            observations[f'agent_{i}'] = np.concatenate([obs_flat, own_portfolio_state])
            global_portfolio_state.append(own_portfolio_state)
            
        global_state = np.concatenate([market_data_global_flat, np.concatenate(global_portfolio_state)])
        return observations, global_state

    def reset(self, seed=None, initial_portfolio=None):
        super().reset(seed=seed)
        self.current_step = 0
        
        if initial_portfolio:
            self.positions = initial_portfolio['positions']
            self.entry_prices = initial_portfolio['entry_prices']
        else:
            self.positions = [0] * self.n_agents
            self.entry_prices = [0.0] * self.n_agents
            
        self.episode_returns = []
            
        obs, state = self._get_obs_and_state()
        return obs, {"global_state": state}

    def get_state(self):
        _, state = self._get_obs_and_state()
        return state

    def step(self, actions):
        old_price = self.prices.iloc[self.current_step + self.window_size - 1]
        self.current_step += 1
        new_price = self.prices.iloc[self.current_step + self.window_size - 1]
        
        # [개선] 비율 기반 수익률 계산
        price_return = (new_price - old_price) / (old_price + 1e-9)

        instant_rewards = 0.0
        transaction_costs = 0.0
        
        for i in range(self.n_agents):
            action = actions[f'agent_{i}']
            current_pos = self.positions[i]

            if action == 0:  # Buy
                if current_pos == -1:
                    # 숏 포지션 청산
                    realized_return = (self.entry_prices[i] - new_price) / (self.entry_prices[i] + 1e-9)
                    instant_rewards += realized_return
                    transaction_costs += 0.003  # 0.3% 거래 비용
                    
                self.positions[i] = 1
                if current_pos != 1: 
                    self.entry_prices[i] = float(new_price)
                    transaction_costs += 0.003
                    
            elif action == 1:  # Hold
                pass
                
            elif action == 2:  # Sell
                if current_pos == 1:
                    # 롱 포지션 청산
                    realized_return = (new_price - self.entry_prices[i]) / (self.entry_prices[i] + 1e-9)
                    instant_rewards += realized_return
                    transaction_costs += 0.003
                    
                self.positions[i] = -1
                if current_pos != -1:
                    self.entry_prices[i] = float(new_price)
                    transaction_costs += 0.003

        # [개선] 보상 계산 - 더 강한 시그널
        joint_position = sum(self.positions)
        
        # 1. 비율 기반 홀딩 보상 (메인 시그널)
        holding_reward = float(joint_position * price_return)
        
        # 2. 즉시 실현 수익 (강화)
        instant_rewards = instant_rewards * 2.0  # 실현 수익에 더 큰 가중치
        
        # 3. 거래 비용 페널티 감소 (너무 강한 페널티는 학습 방해)
        transaction_costs = transaction_costs * 0.5
        
        # 4. 다양성 보너스 (에이전트들이 다른 행동을 하도록 유도)
        unique_actions = len(set(actions.values()))
        diversity_bonus = 0.01 * (unique_actions - 1)  # 0 ~ 0.02
        
        # 5. 포지션 유지 페널티 완화
        hold_count = sum(1 for a in actions.values() if a == 1)
        hold_penalty = -0.001 * hold_count if hold_count == self.n_agents else 0.0
        
        # 6. 최종 보상 (스케일 조정 전)
        raw_team_reward = (
            holding_reward + 
            instant_rewards - 
            transaction_costs + 
            diversity_bonus + 
            hold_penalty
        )
        
        # 7. REWARD_SCALE 적용
        team_reward = raw_team_reward * REWARD_SCALE
        
        # [개선] 보상 클리핑 제거 - 학습 시그널 유지
        # team_reward = np.clip(team_reward, -1.0, 1.0)  # 제거
        
        self.episode_returns.append(team_reward)

        rewards = {f'agent_{i}': team_reward for i in range(self.n_agents)}
        
        next_obs, next_state = self._get_obs_and_state()
        done = self.current_step >= self.max_steps
        dones = {f'agent_{i}': done for i in range(self.n_agents)}
        dones['__all__'] = done
        
        info = {
            "global_state": next_state, 
            "raw_pnl": team_reward,
            "price_return": price_return,
            "instant_reward": instant_rewards,
            "transaction_cost": transaction_costs
        }
        
        return next_obs, rewards, dones, False, info