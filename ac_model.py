# ac_model.py

import random
from typing import List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical


class ActorCriticNet(nn.Module):
    """
    A2C를 위한 액터-크리틱 네트워크.
    공유 feature_layer + actor_head + critic_head 구조.
    """
    def __init__(self, state_dim: int, action_dim: int = 3, hidden_dims: List[int] = None):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [128, 128]

        layers = []
        in_dim = state_dim
        for h in hidden_dims:
            layers.append(nn.Linear(in_dim, h))
            layers.append(nn.ReLU())
            in_dim = h

        self.feature_layer = nn.Sequential(*layers)
        self.actor_head = nn.Linear(in_dim, action_dim)
        self.critic_head = nn.Linear(in_dim, 1)

    def forward(self, x: torch.Tensor):
        """
        x: [B, state_dim]
        return: (logits [B, action_dim], value [B, 1])
        """
        feat = self.feature_layer(x)
        logits = self.actor_head(feat)
        value = self.critic_head(feat)
        return logits, value


class A2CAgent:
    """
    A2C 에이전트.
    - act(): 정책에 따라 행동 샘플 또는 greedy 행동 선택
    - remember(): 롤아웃 버퍼에 transition 저장
    - train_step(): 에피소드 종료 후, 버퍼 기반 업데이트
    """
    def __init__(
        self,
        state_dim: int,
        action_dim: int = 3,
        hidden_dims: List[int] = None,
        gamma: float = 0.99,
        lr: float = 1e-3,
        value_loss_coeff: float = 0.5,
        entropy_coeff: float = 0.01,
        seed: int = 42,
        device: str = "cpu",
    ):
        if hidden_dims is None:
            hidden_dims = [128, 128]

        self.device = device
        self.gamma = gamma
        self.value_loss_coeff = value_loss_coeff
        self.entropy_coeff = entropy_coeff

        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)

        self.ac_net = ActorCriticNet(
            state_dim=state_dim,
            action_dim=action_dim,
            hidden_dims=hidden_dims,
        ).to(self.device)

        self.opt = optim.Adam(self.ac_net.parameters(), lr=lr)

        # (s, a, r, ns, done, log_prob, value) 를 저장하는 버퍼
        self.rollout_buffer: List[
            Tuple[np.ndarray, int, float, np.ndarray, bool, float, float]
        ] = []

    # ---------------------------------------------------
    # 행동 선택: act()
    # ---------------------------------------------------
    def act(self, state: np.ndarray, deterministic: bool = False):
        """
        state: env에서 나온 관측값 (np.ndarray)
        deterministic:
          - False: 정책 분포에서 샘플링
          - True : argmax 정책 (검증용)
        return: (action, log_prob)
        """
        state_t = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        logits, _ = self.ac_net(state_t)
        dist = Categorical(logits=logits)

        if deterministic:
            # 가장 확률이 높은 행동 선택
            probs = F.softmax(logits, dim=-1)
            action = torch.argmax(probs, dim=-1)
        else:
            action = dist.sample()

        log_prob = dist.log_prob(action)  # [1]

        return int(action.item()), float(log_prob.item())

    def get_value(self, state: np.ndarray) -> float:
        """
        현재 상태의 가치 V(s)를 추정
        """
        state_t = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            _, value = self.ac_net(state_t)
        return float(value.item())

    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        log_prob: float,
        value: float,
    ):
        """
        한 타임스텝 transition 저장.
        log_prob, value는 인터페이스 유지용으로 같이 저장하지만
        실제 train_step에서는 네트워크에서 다시 계산한다.
        """
        self.rollout_buffer.append(
            (state, action, reward, next_state, done, log_prob, value)
        )

    def clear_buffer(self):
        self.rollout_buffer = []

    # ---------------------------------------------------
    # 학습: train_step()
    # ---------------------------------------------------
    def train_step(self):
        """
        에피소드 종료 후, rollout buffer를 이용해 A2C 업데이트 수행.
        반환값: (actor_loss, critic_loss, entropy_loss) / 버퍼 없으면 None
        """
        if not self.rollout_buffer:
            return None

        # 1. 버퍼 → 텐서
        states, actions, rewards, next_states, dones, _, _ = zip(*self.rollout_buffer)

        states_t = torch.tensor(np.array(states), dtype=torch.float32, device=self.device)
        actions_t = torch.tensor(np.array(actions), dtype=torch.long, device=self.device)
        rewards_t = torch.tensor(np.array(rewards), dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(np.array(dones), dtype=torch.float32, device=self.device)

        # 2. 마지막 next_state의 V(s_T)를 이용해 부트스트랩 리턴 계산
        with torch.no_grad():
            last_state = next_states[-1]
            if last_state is not None:
                last_state_t = torch.tensor(last_state, dtype=torch.float32, device=self.device).unsqueeze(0)
                _, last_value_t = self.ac_net(last_state_t)  # [1, 1]
                last_value = float(last_value_t.squeeze(1).item())
            else:
                last_value = 0.0

        returns = []
        G = last_value
        for r, d in reversed(list(zip(rewards, dones))):
            G = r + self.gamma * G * (1.0 - d)
            returns.insert(0, G)

        returns_t = torch.tensor(returns, dtype=torch.float32, device=self.device)

        # 3. 현재 상태들에 대한 policy logits, value 예측
        policy_logits_t, values_pred_t = self.ac_net(states_t)  # values_pred_t: [T, 1]
        values_pred_t = values_pred_t.squeeze(1)                # [T]

        dist = Categorical(logits=policy_logits_t)
        log_probs_t = dist.log_prob(actions_t)                  # [T]
        entropy_t = dist.entropy().mean()                       # 스칼라

        # 4. Advantage 계산 + 정규화
        advantages_t = returns_t - values_pred_t
        advantages_t = (advantages_t - advantages_t.mean()) / (advantages_t.std() + 1e-8)

        # 5. 손실 계산
        # Actor: - E[log pi(a|s) * A]
        actor_loss = -(log_probs_t * advantages_t.detach()).mean()

        # Critic: Smooth L1 (Huber)로 폭주 완화
        critic_loss = F.smooth_l1_loss(values_pred_t, returns_t)

        # Entropy: 탐험 유지 (엔트로피 감소에 페널티)
        entropy_loss = -entropy_t

        total_loss = (
            actor_loss
            + self.value_loss_coeff * critic_loss
            + self.entropy_coeff * entropy_loss
        )

        # 6. 역전파 + grad clipping
        self.opt.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.ac_net.parameters(), max_norm=0.5)
        self.opt.step()

        # 7. 버퍼 초기화
        self.clear_buffer()

        return float(actor_loss.item()), float(critic_loss.item()), float(entropy_loss.item())

    # ---------------------------------------------------
    # 모델 저장/로드
    # ---------------------------------------------------
    def save(self, path: str):
        torch.save(self.ac_net.state_dict(), path)

    def load(self, path: str):
        self.ac_net.load_state_dict(torch.load(path, map_location=self.device))
        self.ac_net.to(self.device)
        self.ac_net.eval()