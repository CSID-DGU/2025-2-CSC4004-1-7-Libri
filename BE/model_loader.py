import sys
import os
from typing import Dict, Tuple, Optional, List

import numpy as np
import torch
import yaml
import joblib

# 현재 파일 기준 경로 설정
BASE_DIR = os.path.dirname(__file__)                     # .../main_11.29/BE
A2C_DIR = os.path.join(BASE_DIR, "..", "AI", "a2c_11.29")  # .../main_11.29/AI/a2c_11.29

# A2C 프로젝트를 파이썬 모듈 경로에 추가
sys.path.append(os.path.abspath(A2C_DIR))

from ac_model import A2CAgent
from data_utils import FEATURES, download_data, add_indicators, build_state

# MARL 3-agent 모델 설정 상수 (marl_3agent/data_processor.py와 동기화 필요)
MARL_N_FEATURES_AGENT_0 = 9  # Close, High, Low, Volume + RSI, Stoch_K, Stoch_D, ATR, Bollinger_B
MARL_N_FEATURES_AGENT_1 = 7  # Close, High, Low, Volume + SMA20, MACD, MACD_Signal
MARL_N_FEATURES_AGENT_2 = 8  # Close, High, Low, Volume + VIX, ROA, DebtRatio, AnalystRating
MARL_N_FEATURES_GLOBAL = 16  # 전체 고유 피처 수


class ModelLoader:
    """
    세 가지 모델을 관리하는 로더.

    - marl_model : 3-agent MARL (QMIX 기반 멀티에이전트 강화학습)
    - model_2    : 두 번째 모델 (TODO)
    - model_3    : 공격형 A2C 모델
    """
    def __init__(self) -> None:
        self.marl_model: Optional[object] = None
        self.model_2: Optional[object] = None

        # 공격형 A2C 관련 필드
        self.model_3: Optional[A2CAgent] = None
        self.a2c_cfg: Optional[dict] = None
        self.a2c_window_size: Optional[int] = None
        self.a2c_scaler: Optional[object] = None
        self.a2c_device: str = "cpu"

    # ------------------------------------------------------------------
    # 1) MARL 3-agent (marl_3agent 폴더 사용)
    # ------------------------------------------------------------------
    def load_marl_model(self) -> bool:
        """MARL 3-agent 모델 로드"""
        try:
            import importlib.util
            
            marl_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "AI", "marl_3agent"))
            
            # marl_3agent의 config.py를 명시적으로 로드
            marl_config_path = os.path.join(marl_dir, "config.py")
            spec = importlib.util.spec_from_file_location("marl_config", marl_config_path)
            marl_config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(marl_config)
            
            DEVICE = marl_config.DEVICE
            N_AGENTS = marl_config.N_AGENTS
            WINDOW_SIZE = marl_config.WINDOW_SIZE
            
            # marl_3agent 폴더를 path에 추가 (qmix_model import용)
            if marl_dir not in sys.path:
                sys.path.insert(0, marl_dir)
            
            # BE의 config가 sys.modules에 캐시되어 있으면 임시로 제거
            # (qmix_model.py가 from config import ...를 사용하기 때문)
            be_config = sys.modules.get('config')
            if be_config is not None:
                del sys.modules['config']
            
            # marl_3agent의 config를 sys.modules에 등록
            sys.modules['config'] = marl_config
            
            try:
                from qmix_model import QMIX_Learner  # type: ignore
            finally:
                # BE의 config 복구
                if be_config is not None:
                    sys.modules['config'] = be_config

            # 모듈 상단에 정의된 상수 사용
            # obs_dim = window_size * n_features + 2 (position + unrealized_return)
            obs_dim_0 = WINDOW_SIZE * MARL_N_FEATURES_AGENT_0 + 2  # 10 * 9 + 2 = 92
            obs_dim_1 = WINDOW_SIZE * MARL_N_FEATURES_AGENT_1 + 2  # 10 * 7 + 2 = 72
            obs_dim_2 = WINDOW_SIZE * MARL_N_FEATURES_AGENT_2 + 2  # 10 * 8 + 2 = 82
            
            obs_dims_list = [obs_dim_0, obs_dim_1, obs_dim_2]  # [92, 72, 82]
            action_dim = 3
            
            # state_dim = window_size * n_features_global + (n_agents * 2)
            # 10 * 16 + (3 * 2) = 160 + 6 = 166
            state_dim = WINDOW_SIZE * MARL_N_FEATURES_GLOBAL + (N_AGENTS * 2)

            self.marl_model = QMIX_Learner(obs_dims_list, action_dim, state_dim, DEVICE)

            model_path = os.path.join(marl_dir, "best_model.pth")

            if os.path.exists(model_path):
                self.marl_model.load_state_dict(torch.load(model_path, map_location=DEVICE))
                print(f"[MARL] best_model.pth 로드 완료: {model_path}")
            else:
                print(f"[MARL] 경고: {model_path} 를 찾을 수 없습니다. 초기화된 모델 사용")

            return True
        except Exception as e:
            print(f"[MARL] 모델 로드 실패: {e}")
            self.marl_model = None
            return False

    def load_model_2(self) -> bool:
        """두 번째 RL/전략 모델 (TODO)"""
        try:
            # TODO: 실제 model_2 로드 로직 구현
            self.model_2 = "Model 2 Placeholder"
            print("[Model 2] Placeholder 로드 (실제 모델 연결 필요)")
            return True
        except Exception as e:
            print(f"[Model 2] 로드 실패: {e}")
            self.model_2 = None
            return False

    # ------------------------------------------------------------------
    # 2) 공격형 A2C (Model 3) 로드 / 예측
    # ------------------------------------------------------------------
    def load_model_3(self, config_path: str = None) -> bool:
        """
        공격형 A2C 모델 로드.

        - AI/a2c_11.29/config.yaml 읽기
        - reports/scaler.joblib 로드
        - A2CAgent 생성 + a2c_samsung.pt 가중치 로드
        """
        try:
            if config_path is None:
                config_path = os.path.join(A2C_DIR, "config.yaml")
            config_path = os.path.abspath(config_path)

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"A2C 설정 파일을 찾을 수 없습니다: {config_path}")

            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)

            self.a2c_cfg = cfg
            self.a2c_window_size = int(cfg["window_size"])
            self.a2c_device = cfg.get("device", "cpu")

            # 경로들(A2C 디렉토리 기준)
            model_rel = cfg["model_path"]          # 예: "a2c_samsung.pt"
            report_dir_rel = cfg["report_dir"]     # 예: "reports"

            model_path = os.path.join(A2C_DIR, model_rel)
            scaler_path = os.path.join(A2C_DIR, report_dir_rel, "scaler.joblib")

            model_path = os.path.abspath(model_path)
            scaler_path = os.path.abspath(scaler_path)

            if not os.path.exists(scaler_path):
                raise FileNotFoundError(f"A2C 스케일러 파일을 찾을 수 없습니다: {scaler_path}")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"A2C 모델 가중치 파일을 찾을 수 없습니다: {model_path}")

            # 1) 스케일러 로드
            self.a2c_scaler = joblib.load(scaler_path)
            print(f"[A2C] scaler 로드 완료: {scaler_path}")

            # 2) A2C 에이전트 생성 + 가중치 로드
            state_dim = len(FEATURES) * self.a2c_window_size + 1  # +1 = Position
            model_cfg = cfg.get("model_cfg", {})
            hidden_dims = model_cfg.get("hidden_dims", [128, 128])

            agent = A2CAgent(
                state_dim=state_dim,
                action_dim=3,
                hidden_dims=hidden_dims,
                gamma=model_cfg.get("gamma", 0.99),
                lr=model_cfg.get("lr", 1e-3),
                value_loss_coeff=model_cfg.get("value_loss_coeff", 0.5),
                entropy_coeff=model_cfg.get("entropy_coeff", 0.01),
                device=self.a2c_device,
            )
            agent.load(model_path)

            self.model_3 = agent
            print(f"[A2C] 공격형 A2C 모델 로드 완료: {model_path}")
            return True
        except Exception as e:
            print(f"[A2C] Model 3 로드 실패: {e}")
            self.model_3 = None
            self.a2c_scaler = None
            return False

    def _build_latest_state_and_indicators(self) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        config.yaml 설정에 따라:
        - 삼성전자 + KOSPI + VIX 데이터를 다운로드
        - 기술지표 계산 후 scaler로 정규화
        - 최근 window_size일을 사용해 state 벡터 생성
        - 마지막 날짜의 indicator dict 생성
        """
        if self.a2c_cfg is None or self.a2c_window_size is None or self.a2c_scaler is None:
            raise RuntimeError("A2C 설정/스케일러가 초기화되지 않았습니다. load_model_3()을 먼저 호출해야 합니다.")

        cfg = self.a2c_cfg

        raw = download_data(
            cfg["ticker"],
            cfg["kospi_ticker"],
            cfg["vix_ticker"],
            cfg["start_date"],
            cfg["end_date"],
        )
        df = add_indicators(raw)
        df = df.dropna().sort_index()

        if len(df) < self.a2c_window_size:
            raise ValueError(f"데이터 길이가 window_size({self.a2c_window_size}) 보다 짧습니다.")

        # FEATURES 스케일링
        df[FEATURES] = self.a2c_scaler.transform(df[FEATURES])

        window_df = df.iloc[-self.a2c_window_size :]
        state = build_state(window_df, position_flag=0)  # 웹 기준: 기본 포지션 = 미보유(0)

        latest_row = window_df.iloc[-1]
        indicators: Dict[str, float] = {feat: float(latest_row[feat]) for feat in FEATURES}

        return state, indicators

    def predict_marl(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, float], Optional[str], Optional[list]]:
        """
        MARL 3-agent 모델 예측
        
        Returns:
            signal: 매매 신호 (매수/매도/보유)
            vote_sum: 에이전트 투표 합계 (-3 ~ +3)
            indicators: 기술 지표 딕셔너리
            xai_explanation: XAI 설명 문자열
            xai_importance: 피처 중요도 리스트
        """
        if self.marl_model is None:
            raise ValueError("MARL 모델이 로드되지 않았습니다.")

        # features가 비어있으면 기본 지표 생성
        if not features:
            features = {
                "SMA20": 0.0,
                "MACD": 0.0,
                "MACD_Signal": 0.0,
                "RSI": 50.0,
                "Stoch_K": 50.0,
                "Stoch_D": 50.0,
                "ATR": 0.0,
                "Bollinger_B": 0.5,
                "VIX": 15.0,
                "ROA": 0.0,
                "DebtRatio": 0.0,
                "AnalystRating": 3.0
            }

        # 3-agent 투표 시스템 시뮬레이션
        # 실제 구현에서는 MARL 모델을 사용하여 각 에이전트의 행동을 결정
        # 현재는 기술 지표 기반 규칙으로 투표 시뮬레이션
        
        votes = []
        xai_importance = []
        
        # 에이전트 1: RSI 기반 (모멘텀)
        rsi = features.get("RSI", 50.0)
        if rsi < 30:
            votes.append(1)  # 매수
        elif rsi > 70:
            votes.append(-1)  # 매도
        else:
            votes.append(0)  # 보유
        # RSI importance: deviation from neutral (50) normalized to 0-1 range
        rsi_importance = min(abs(rsi - 50) / 50.0, 1.0)
        xai_importance.append({"feature": "RSI", "importance": rsi_importance})
        
        # 에이전트 2: MACD 기반 (추세)
        macd = features.get("MACD", 0.0)
        macd_signal = features.get("MACD_Signal", 0.0)
        if macd > macd_signal:
            votes.append(1)  # 매수
        elif macd < macd_signal:
            votes.append(-1)  # 매도
        else:
            votes.append(0)  # 보유
        # MACD importance: normalized crossover magnitude (0-1 range)
        macd_diff = abs(macd - macd_signal)
        macd_importance = min(macd_diff / (abs(macd_diff) + 1.0), 1.0)
        xai_importance.append({"feature": "MACD", "importance": macd_importance})
        
        # 에이전트 3: VIX 기반 (변동성/공포)
        vix = features.get("VIX", 15.0)
        vix_baseline = 22.5  # VIX 중립점 (15~30의 중간)
        if vix > 30:
            votes.append(-1)  # 매도 (공포 구간)
        elif vix < 15:
            votes.append(1)  # 매수 (안정 구간)
        else:
            votes.append(0)  # 보유
        # VIX importance: deviation from baseline normalized to 0-1 range
        vix_importance = min(abs(vix - vix_baseline) / vix_baseline, 1.0) if vix_baseline != 0 else 0.0
        xai_importance.append({"feature": "VIX", "importance": vix_importance})
        
        vote_sum = sum(votes)  # -3 ~ +3 범위
        
        # 투표 결과를 신호로 변환
        if vote_sum > 0:
            signal = "매수"
        elif vote_sum < 0:
            signal = "매도"
        else:
            signal = "보유"
        
        # XAI 설명 생성
        agent_decisions = ["매수" if v > 0 else ("매도" if v < 0 else "보유") for v in votes]
        xai_explanation = (
            f"3개 에이전트 투표 결과: "
            f"모멘텀 에이전트({agent_decisions[0]}), "
            f"추세 에이전트({agent_decisions[1]}), "
            f"변동성 에이전트({agent_decisions[2]}). "
            f"총 투표 합계: {vote_sum:+d}점"
        )
        
        return signal, float(vote_sum), features, xai_explanation, xai_importance

    def predict_model_2(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """Model 2 예측 (현재 더미 로직)"""
        if self.model_2 is None:
            raise ValueError("Model 2가 로드되지 않았습니다.")

        # TODO: 실제 데이터 전처리 + model_2 예측 로직 구현
        signal = "보유"
        confidence = 0.60
        return signal, confidence, features

    def predict_model_3(self, symbol: Optional[str] = None) -> Tuple[str, float, Dict[str, float]]:
        """
        공격형 A2C 예측.

        - 최신 market 데이터 기반으로 state 생성
        - A2C policy에서 행동 확률 계산
        - 최고 확률 행동을 signal로 선택
        - 최고 확률을 confidence_score로 사용
        """
        if self.model_3 is None:
            raise ValueError("A2C(Model 3)가 로드되지 않았습니다.")

        state, indicators = self._build_latest_state_and_indicators()

        with torch.no_grad():
            state_t = torch.tensor(state, dtype=torch.float32, device=self.model_3.device).unsqueeze(0)
            logits, _ = self.model_3.ac_net(state_t)
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]

        action_idx = int(np.argmax(probs))
        action_map = {0: "매수", 1: "매도", 2: "보유"}
        signal = action_map.get(action_idx, "보유")
        confidence = float(probs[action_idx])

        return signal, confidence, indicators

    def get_model_status(self) -> Dict[str, str]:
        """모델 상태 확인용"""
        return {
            "marl_3agent": "available" if self.marl_model is not None else "unavailable",
            "model_2": "available" if self.model_2 is not None else "unavailable",
            "model_3": "available" if self.model_3 is not None else "unavailable",
        }


# 전역 인스턴스
model_loader = ModelLoader()