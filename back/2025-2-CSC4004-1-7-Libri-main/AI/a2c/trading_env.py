# trading_env.py

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

from data_utils import FEATURES, build_state


class TradingEnv:
    """
    단일 종목 + KOSPI + VIX 기반 트레이딩 환경.
    - 상태(state): 최근 window_size일의 기술지표 FEATURES + Position(현재 포지션)
    - 액션(action): 0=Long(매수), 1=Short(매도), 2=Hold(관망)
        * 포지션 값: +1 (Long), -1 (Short), 0 (미보유)
    - 보상(reward):
        1) base_reward: 포지션 * 당일 수익률 - 거래 비용
        2) composite_reward: Sharpe-like / Downside / Treynor 등
           → config.yaml의 reward 섹션에 따라 계산
    """

    def __init__(
        self,
        data: pd.DataFrame,
        window_size: int,
        trade_penalty: float = 0.001,
        use_daily_unrealized: bool = True,
        reward_cfg: Optional[Dict[str, Any]] = None,
    ):
        self.data = data.reset_index(drop=True)
        self.window_size = window_size
        self.trade_penalty = trade_penalty
        self.use_daily_unrealized = use_daily_unrealized
        self.reward_cfg = reward_cfg or {}

        # 가격/지수 배열
        self.close = self.data["Close"].values.astype(float)
        self.kospi = self.data["KOSPI"].values.astype(float)

        # 일별 수익률
        self.asset_ret = np.zeros(len(self.data), dtype=float)
        self.mkt_ret = np.zeros(len(self.data), dtype=float)
        self._compute_returns()

        # 에피소드 상태
        self.current_step: int = 0
        self.position: float = 0.0   # -1, 0, +1
        self.equity: float = 1.0
        self.bh_equity: float = 1.0
        self.total_reward: float = 0.0

        # 합성보상용 히스토리
        self.port_ret_hist = []
        self.mkt_ret_hist = []

        # 곡선 기록용
        self.equity_curve = []
        self.buyhold_curve = []

        # reward 설정 파싱
        self._parse_reward_cfg()

    # ------------------------------------------------------
    # 내부 유틸
    # ------------------------------------------------------
    def _compute_returns(self):
        """종목/코스피 일별 수익률 계산."""
        if len(self.close) < 2:
            return

        asset_ret = (self.close[1:] / self.close[:-1]) - 1.0
        mkt_ret = (self.kospi[1:] / self.kospi[:-1]) - 1.0

        self.asset_ret[1:] = asset_ret
        self.mkt_ret[1:] = mkt_ret

    def _parse_reward_cfg(self):
        cfg = self.reward_cfg

        self.use_composite: bool = cfg.get("use_composite", False)
        self.roll_window: int = cfg.get("roll_window", 63)
        self.ema_alpha: float = cfg.get("ema_alpha", 0.05)
        self.rf: float = cfg.get("rf", 0.0)

        # 가중치
        self.w1: float = cfg.get("w1", 0.35)
        self.w2: float = cfg.get("w2", 0.25)
        self.w3: float = cfg.get("w3", 0.20)
        self.w4: float = cfg.get("w4", 0.20)

        self.beta_eps: float = cfg.get("beta_eps", 0.2)

        # 스케일링
        scale_cfg = cfg.get("scale", {})
        self.scale_rann: float = scale_cfg.get("rann", 0.005)
        self.scale_ddown: float = scale_cfg.get("ddown", 0.02)
        self.scale_dret: float = scale_cfg.get("dret", 0.005)
        self.scale_treynor: float = scale_cfg.get("treynor", 0.005)

        self.clip: float = cfg.get("clip", 2.0)
        # 🔥 scale_factor는 "합성보상 크기"를 조절하는 레버
        # 1.0이면 composite_reward가 꽤 세게 들어가고,
        # 10.0이면 base_reward와 비슷한 수준이 되도록 줄어든다.
        self.scale_factor: float = cfg.get("scale_factor", 10.0)

    # ------------------------------------------------------
    # Gym 스타일 인터페이스
    # ------------------------------------------------------
    def reset(self):
        if len(self.data) < self.window_size + 1:
            raise ValueError("데이터 길이가 window_size + 1 보다 커야 합니다.")

        self.current_step = self.window_size - 1
        self.position = 0.0
        self.equity = 1.0
        self.bh_equity = 1.0
        self.total_reward = 0.0

        self.port_ret_hist = []
        self.mkt_ret_hist = []

        self.equity_curve = [self.equity]
        self.buyhold_curve = [self.bh_equity]

        window_df = self.data.iloc[
            self.current_step - (self.window_size - 1) : self.current_step + 1
        ]
        state = build_state(window_df, position_flag=self.position)
        return state

    def current_state_dim(self) -> int:
        return len(FEATURES) * self.window_size + 1

    def step(self, action: int):
        done = False
        info: Dict[str, float] = {}

        # 이미 끝난 경우 방어
        if self.current_step >= len(self.data) - 1:
            window_df = self.data.iloc[
                self.current_step - (self.window_size - 1) : self.current_step + 1
            ]
            state = build_state(window_df, position_flag=self.position)
            return state, 0.0, True, info

        # 1) 액션 → 포지션
        prev_position = self.position
        if action == 0:      # Long
            new_position = 1.0
        elif action == 1:    # Short
            new_position = -1.0
        else:                # Hold
            new_position = prev_position

        position_change = abs(new_position - prev_position)
        trade_cost = self.trade_penalty * position_change

        # 2) 다음 시점으로 이동
        prev_step = self.current_step
        next_step = self.current_step + 1

        r_asset = float(self.asset_ret[next_step])
        r_mkt = float(self.mkt_ret[next_step])

        if self.use_daily_unrealized:
            r_port = new_position * r_asset
        else:
            r_port = new_position * r_asset  # 필요하면 여기 실현손익만 반영하도록 변경

        self.equity = self.equity * (1.0 + r_port)
        self.bh_equity = self.bh_equity * (1.0 + r_asset)

        base_reward = r_port - trade_cost

        self.port_ret_hist.append(r_port)
        self.mkt_ret_hist.append(r_mkt)

        # 3) 합성 보상
        comp_beta = 0.0
        comp_R_raw = 0.0
        comp_Ddown_raw = 0.0
        comp_Dret_raw = 0.0
        comp_Try_raw = 0.0
        composite_reward = 0.0

        if self.use_composite and len(self.port_ret_hist) >= self.roll_window:
            port_window = np.array(self.port_ret_hist[-self.roll_window :], dtype=float)
            mkt_window = np.array(self.mkt_ret_hist[-self.roll_window :], dtype=float)

            mean_r = float(np.mean(port_window))
            downside = port_window[port_window < 0.0]
            if len(downside) > 1:
                downside_std = float(np.std(downside, ddof=1))
            else:
                downside_std = 0.0

            var_mkt = float(np.var(mkt_window, ddof=1)) if np.var(mkt_window) > 0 else 0.0
            if var_mkt > 0.0:
                cov_rm = float(np.cov(port_window, mkt_window)[0, 1])
                beta_est = cov_rm / (var_mkt + 1e-8)
            else:
                beta_est = 0.0

            abs_beta = max(self.beta_eps, abs(beta_est)) if self.beta_eps > 0 else (abs(beta_est) + 1e-8)

            # Rann-like
            if downside_std > 0.0:
                comp_R_raw = mean_r / (downside_std + 1e-8)
            else:
                comp_R_raw = 0.0

            comp_Ddown_raw = downside_std
            comp_Dret_raw = (mean_r - self.rf) / (abs_beta + 1e-8)
            comp_Try_raw = mean_r / (abs_beta + 1e-8)

            comp_R_scaled = comp_R_raw / self.scale_rann if self.scale_rann > 0 else comp_R_raw
            comp_Ddown_scaled = -comp_Ddown_raw / self.scale_ddown if self.scale_ddown > 0 else -comp_Ddown_raw
            comp_Dret_scaled = comp_Dret_raw / self.scale_dret if self.scale_dret > 0 else comp_Dret_raw
            comp_Try_scaled = comp_Try_raw / self.scale_treynor if self.scale_treynor > 0 else comp_Try_raw

            composite_raw = (
                self.w1 * comp_R_scaled
                + self.w2 * comp_Ddown_scaled
                + self.w3 * comp_Dret_scaled
                + self.w4 * comp_Try_scaled
            )

            composite_tanh = np.tanh(composite_raw / self.clip) if self.clip > 0 else np.tanh(composite_raw)
            composite_reward = float(composite_tanh / self.scale_factor)
            comp_beta = float(beta_est)

        reward = float(base_reward + composite_reward)
        self.total_reward += reward

        # 4) 다음 state, info 구성
        self.position = new_position
        self.current_step = next_step
        done = (self.current_step >= len(self.data) - 1)

        window_df = self.data.iloc[
            self.current_step - (self.window_size - 1) : self.current_step + 1
        ]
        next_state = build_state(window_df, position_flag=self.position)

        self.equity_curve.append(self.equity)
        self.buyhold_curve.append(self.bh_equity)

        info["base"] = float(base_reward)
        info["r_t"] = float(r_port)
        info["rb_t"] = float(r_asset)
        info["comp_beta"] = float(comp_beta)
        info["comp_R"] = float(comp_R_raw)
        info["comp_Ddown"] = float(comp_Ddown_raw)
        info["comp_Dret"] = float(comp_Dret_raw)
        info["comp_Try"] = float(comp_Try_raw)

        return next_state, reward, done, info