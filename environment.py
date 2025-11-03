import gymnasium as gym
from gymnasium import spaces
import numpy as np
from config import N_AGENTS, WINDOW_SIZE

class MARLStockEnv(gym.Env):
    def __init__(self, features_df, prices_df, n_agents=N_AGENTS, window_size=WINDOW_SIZE):
        super().__init__()
        self.df = features_df
        self.prices = prices_df
        self.window_size = window_size
        self.n_agents = n_agents
        self.n_features = len(features_df.columns)
        self.max_steps = len(self.df) - self.window_size - 1

        # Obs: Market Data + Pos Signal (1) + P/L (1)
        self.observation_dim = self.window_size * self.n_features + 2
        # State: Market Data + All Agents [Pos Signal(N), P/L(N)]
        self.state_dim = self.window_size * self.n_features + (self.n_agents * 2)
        
        self.observation_space = spaces.Dict({
            f'agent_{i}': spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim,), dtype=np.float32)
            for i in range(self.n_agents)
        })
        self.action_dim = 3
        self.action_space = spaces.Dict({
            f'agent_{i}': spaces.Discrete(self.action_dim) for i in range(self.n_agents)
        })
        
        self.current_step = 0
        self.positions = [0] * self.n_agents
        self.entry_prices = [0.0] * self.n_agents
        
    def _get_obs_and_state(self):
        start = self.current_step
        end = start + self.window_size
        market_data = self.df.iloc[start:end].values.flatten()
        
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
            observations[f'agent_{i}'] = np.concatenate([market_data, own_portfolio_state])
            global_portfolio_state.append(own_portfolio_state)
            
        global_state = np.concatenate([market_data, np.concatenate(global_portfolio_state)])
            
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