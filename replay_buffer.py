import random
import torch
import numpy as np
from collections import deque, namedtuple
from config import N_AGENTS

class ReplayBuffer:
    def __init__(self, buffer_size, batch_size, device):
        self.memory = deque(maxlen=buffer_size)
        self.batch_size = batch_size
        self.device = device
        self.experience = namedtuple("Experience", 
                                     field_names=["global_state", "obs", "actions", "reward", 
                                                  "next_global_state", "next_obs", "done"])

    def add(self, global_state, obs, actions, reward, next_global_state, next_obs, done):
        obs_list = [obs[f'agent_{i}'] for i in range(N_AGENTS)]
        actions_list = [actions[f'agent_{i}'] for i in range(N_AGENTS)]
        next_obs_list = [next_obs[f'agent_{i}'] for i in range(N_AGENTS)]
        
        e = self.experience(global_state, obs_list, actions_list, reward, 
                            next_global_state, next_obs_list, done)
        self.memory.append(e)

    def sample(self):
        experiences = random.sample(self.memory, k=self.batch_size)
        
        global_states = torch.from_numpy(np.vstack([e.global_state for e in experiences])).float().to(self.device)
        rewards = torch.from_numpy(np.vstack([e.reward for e in experiences])).float().to(self.device)
        next_global_states = torch.from_numpy(np.vstack([e.next_global_state for e in experiences])).float().to(self.device)
        dones = torch.from_numpy(np.vstack([e.done for e in experiences]).astype(np.float32)).float().to(self.device)
        
        obs_list = [torch.from_numpy(np.vstack([e.obs[i] for e in experiences])).float().to(self.device) for i in range(N_AGENTS)]
        actions_list = [torch.from_numpy(np.vstack([e.actions[i] for e in experiences])).long().to(self.device) for i in range(N_AGENTS)]
        next_obs_list = [torch.from_numpy(np.vstack([e.next_obs[i] for e in experiences])).float().to(self.device) for i in range(N_AGENTS)]
        
        return (global_states, obs_list, actions_list, rewards, next_global_states, next_obs_list, dones)

    def __len__(self):
        return len(self.memory)