import torch
import torch.nn as nn
import torch.nn.functional as F
import copy
import random
import numpy as np
from config import N_AGENTS, LR, TAU, MIXER_EMBED_DIM, BATCH_SIZE, GAMMA

# --- [개선] Dueling DQN 구조 ---
class Q_Net(nn.Module):
    def __init__(self, state_dim, action_dim, hid_shape=(256, 128, 64)):
        super().__init__()
        
        # Shared Feature Extractor
        self.feature = nn.Sequential(
            nn.Linear(state_dim, hid_shape[0]),
            nn.LayerNorm(hid_shape[0]),  # Batch Norm 대신 Layer Norm
            nn.ReLU(),
            nn.Dropout(p=0.2),
            
            nn.Linear(hid_shape[0], hid_shape[1]),
            nn.LayerNorm(hid_shape[1]),
            nn.ReLU(),
            nn.Dropout(p=0.2),
        )
        
        # Value Stream (상태 가치)
        self.value_stream = nn.Sequential(
            nn.Linear(hid_shape[1], hid_shape[2]),
            nn.ReLU(),
            nn.Linear(hid_shape[2], 1)
        )
        
        # Advantage Stream (행동 우위)
        self.advantage_stream = nn.Sequential(
            nn.Linear(hid_shape[1], hid_shape[2]),
            nn.ReLU(),
            nn.Linear(hid_shape[2], action_dim)
        )
        
        # [개선] Xavier 초기화
        self.apply(self._init_weights)
    
    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
    
    def forward(self, state):
        features = self.feature(state)
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        
        # Dueling DQN 공식: Q = V + (A - mean(A))
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        return q_values


# --- DQN 에이전트 ---
class DQN_Agent:
    def __init__(self, agent_id, obs_dim, action_dim, device):
        self.agent_id_str = agent_id
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.dvc = device
        
        self.q_net = Q_Net(self.obs_dim, self.action_dim).to(self.dvc)
        self.target_q_net = copy.deepcopy(self.q_net)
        for p in self.target_q_net.parameters():
            p.requires_grad = False
            
        self.steps_done = 0

    def select_action(self, obs, epsilon):
        self.steps_done += 1
        if random.random() > epsilon:
            with torch.no_grad():
                obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.dvc)
                q_values = self.q_net(obs_tensor)
                action = q_values.argmax(dim=1).item()
                return action
        else:
            return random.randrange(self.action_dim)
            
    def get_q_values(self, obs_batch):
        return self.q_net(obs_batch)
        
    def get_target_q_values(self, obs_batch):
        return self.target_q_net(obs_batch)

    def update_target_net(self):
        for param, target_param in zip(self.q_net.parameters(), self.target_q_net.parameters()):
            target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)
            
    def parameters(self):
        return self.q_net.parameters()
        
    def get_prediction_with_reason(self, obs, feature_names, window_size, n_features):
        obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.dvc).requires_grad_()
        self.q_net.zero_grad()
        
        q_values = self.q_net(obs_tensor)
        action_idx = torch.argmax(q_values, dim=1).item()
        target_q_value = q_values[0, action_idx]
        
        target_q_value.backward()
        
        grads = obs_tensor.grad.squeeze(0)
        
        n_obs_features = window_size * n_features
        obs_grads = grads[:n_obs_features]
        
        grads_reshaped = obs_grads.view(window_size, n_features)
        
        feature_importance = grads_reshaped.abs().sum(dim=0).cpu().numpy()
        importance_dict = dict(zip(feature_names, feature_importance))
        sorted_importance = sorted(importance_dict.items(), key=lambda item: item[1], reverse=True)
        
        return action_idx, q_values.squeeze(0).detach().cpu(), sorted_importance


# --- [개선] 더 깊고 표현력 있는 Mixer ---
class Mixer(nn.Module):
    def __init__(self, n_agents, state_dim, embed_dim):
        super().__init__()
        self.n_agents = n_agents
        self.state_dim = state_dim
        self.embed_dim = embed_dim
        
        # Hypernet for W1 (더 깊은 구조)
        self.hyper_w1 = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, embed_dim * n_agents),
            nn.ReLU()
        )
        
        # Hypernet for b1
        self.hyper_b1 = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, embed_dim)
        )
        
        # Hypernet for W2 (더 깊은 구조)
        self.hyper_w2 = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, embed_dim),
            nn.ReLU()
        )
        
        # Hypernet for b2
        self.hyper_b2 = nn.Sequential(
            nn.Linear(state_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
        # [개선] Xavier 초기화
        self.apply(self._init_weights)
    
    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

    def forward(self, agent_q_values, states):
        B = agent_q_values.size(0)
        agent_q_values = agent_q_values.view(-1, 1, self.n_agents)
        
        w1 = torch.abs(self.hyper_w1(states).view(-1, self.n_agents, self.embed_dim))
        b1 = self.hyper_b1(states).view(-1, 1, self.embed_dim)
        
        hidden = F.elu(torch.bmm(agent_q_values, w1) + b1)
        
        w2 = torch.abs(self.hyper_w2(states).view(-1, self.embed_dim, 1))
        b2 = self.hyper_b2(states).view(-1, 1, 1)
        
        q_total = torch.bmm(hidden, w2) + b2
        
        return q_total.view(-1, 1)


# --- QMIX 학습 관리자 ---
class QMIX_Learner:
    def __init__(self, obs_dims_list, action_dim, state_dim, device):
        self.dvc = device
        self.n_agents = N_AGENTS
        self.action_dim = action_dim
        
        self.agents = []
        if len(obs_dims_list) != self.n_agents:
            raise ValueError(f"obs_dims_list의 길이({len(obs_dims_list)})가 "
                             f"N_AGENTS({self.n_agents})와 일치하지 않습니다.")
                             
        for i in range(self.n_agents):
            agent_obs_dim = obs_dims_list[i] 
            self.agents.append(DQN_Agent(f'agent_{i}', agent_obs_dim, action_dim, device))
        
        self.mixer = Mixer(self.n_agents, state_dim, MIXER_EMBED_DIM).to(self.dvc)
        self.target_mixer = copy.deepcopy(self.mixer)
        for p in self.target_mixer.parameters():
            p.requires_grad = False
            
        self.params = []
        for agent in self.agents:
            self.params += list(agent.parameters())
        self.params += list(self.mixer.parameters())
        
        # [개선] AdamW 옵티마이저 + 가중치 감쇠
        self.optimizer = torch.optim.AdamW(self.params, lr=LR, weight_decay=1e-5)
        
        # [개선] Learning Rate Scheduler
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=1000, eta_min=1e-6
        )
        
    def select_actions(self, obs_dict, epsilon):
        actions = {}
        for i, agent in enumerate(self.agents):
            agent_id = f'agent_{i}'
            action = agent.select_action(obs_dict[agent_id], epsilon)
            actions[agent_id] = action
        return actions

    def train(self, replay_buffer):
        if len(replay_buffer) < BATCH_SIZE:
            return None, None
            
        s, obs, a, r, s_next, obs_next, d = replay_buffer.sample()
        
        chosen_action_qvals = []
        for i, agent in enumerate(self.agents):
            q_values_all = agent.get_q_values(obs[i])
            q_chosen = torch.gather(q_values_all, dim=1, index=a[i])
            chosen_action_qvals.append(q_chosen)
            
        chosen_action_qvals = torch.cat(chosen_action_qvals, dim=1)
        q_total = self.mixer(chosen_action_qvals, s)

        with torch.no_grad():
            target_max_qvals = []
            for i, agent in enumerate(self.agents):
                target_q_values_all = agent.get_target_q_values(obs_next[i])
                target_q_max = target_q_values_all.max(dim=1, keepdim=True)[0]
                target_max_qvals.append(target_q_max)
                
            target_max_qvals = torch.cat(target_max_qvals, dim=1)
            q_total_next = self.target_mixer(target_max_qvals, s_next)
            target_y = r + (1.0 - d) * GAMMA * q_total_next

        # [개선] Huber Loss (outlier에 더 강건)
        loss = F.smooth_l1_loss(q_total, target_y.detach())
        
        self.optimizer.zero_grad()
        loss.backward()
        
        # [개선] Gradient Clipping (더 강력하게)
        torch.nn.utils.clip_grad_norm_(self.params, 5.0)
        
        self.optimizer.step()
        self.scheduler.step()
        
        return loss.item(), q_total.mean().item()  # Return loss and avg Q for monitoring

    def update_target_networks(self):
        for agent in self.agents:
            agent.update_target_net()
            
        for param, target_param in zip(self.mixer.parameters(), self.target_mixer.parameters()):
            target_param.data.copy_(TAU * param.data + (1 - TAU) * target_param.data)