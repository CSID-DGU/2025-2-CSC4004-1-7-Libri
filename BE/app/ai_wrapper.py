import sys
import os
import pandas as pd
import numpy as np
import torch
import joblib
from datetime import datetime, timedelta
import yaml
import warnings
from typing import Dict, Any, List, Optional

from .gpt_service import interpret_model_output

# Suppress warnings
warnings.filterwarnings("ignore")

# Define base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
AI_DIR = os.path.join(PROJECT_ROOT, "AI")

# Model directories
A2C_DIR = os.path.join(AI_DIR, "a2c_11.29")
MARL_DIR = os.path.join(AI_DIR, "marl_3agent")


class A2CWrapper:
    """
    A2C 강화학습 모델을 래핑하는 클래스.

    - load_model(): 모델/스케일러/config 로딩
    - get_historical_signals(start_date_str): 특정 날짜부터의 히스토리컬 시그널 + 수익률 계산
    - predict_today(): 오늘(또는 가장 최근 데이터 기준) 액션 및 확률 반환
    """

    def __init__(self):
        self.model_loaded = False
        self.agent = None
        self.cfg = None
        self.scaler = None
        self.explainer = None
        self.feature_names = None
        self._setup_path()

    def _setup_path(self):
        if A2C_DIR not in sys.path:
            sys.path.append(A2C_DIR)

    def load_model(self):
        if self.model_loaded:
            return

        try:
            original_cwd = os.getcwd()
            os.chdir(A2C_DIR)

            import ac_model
            import data_utils
            import explain_a2c

            # Load Config
            with open("config.yaml", "r", encoding="utf-8") as f:
                self.cfg = yaml.safe_load(f)

            # Load Scaler
            scaler_path = os.path.join(self.cfg["report_dir"], "scaler.joblib")
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            else:
                print(f"Warning: Scaler not found at {scaler_path}")

            # Initialize Agent
            model_cfg = self.cfg["model_cfg"]
            window_size = self.cfg["window_size"]
            dummy_state_dim = len(data_utils.FEATURES) * window_size + 1

            self.agent = ac_model.A2CAgent(
                state_dim=dummy_state_dim,
                action_dim=3,
                hidden_dims=model_cfg.get("hidden_dims", [128, 128]),
                gamma=self.cfg["gamma"],
                lr=self.cfg["lr"],
                value_loss_coeff=self.cfg["value_loss_coeff"],
                entropy_coeff=self.cfg["entropy_coeff"],
                seed=self.cfg["seed"],
                device=self.cfg.get("device", "cpu"),
            )

            model_path = self.cfg["model_path"]
            if os.path.exists(model_path):
                self.agent.load(model_path)
            else:
                print(f"Warning: Model not found at {model_path}")

            self.model_loaded = True

            # --- SHAP Setup ---
            import shap

            # Load data for background distribution (recent 2 years)
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=365 * 2)

            raw_df = data_utils.download_data(
                self.cfg["ticker"],
                self.cfg["kospi_ticker"],
                self.cfg["vix_ticker"],
                start_dt.strftime("%Y-%m-%d"),
                end_dt.strftime("%Y-%m-%d"),
            )
            df = data_utils.add_indicators(raw_df)
            if self.scaler:
                df[data_utils.FEATURES] = self.scaler.transform(df[data_utils.FEATURES])

            # Create background states
            bg_states = []
            bg_len = min(200 + window_size, len(df) - 1)
            for i in range(window_size - 1, bg_len):
                current_window = df.iloc[i - (window_size - 1): i + 1]
                s = data_utils.build_state(current_window, position_flag=0)
                bg_states.append(s)
            bg_states = np.array(bg_states, dtype=np.float32)

            # Sample background
            if len(bg_states) > 100:
                bg_summary = shap.sample(bg_states, 100)
            else:
                bg_summary = bg_states

            # Define model function for SHAP
            def model_f(x):
                x_t = torch.tensor(x, dtype=torch.float32, device=self.cfg.get("device", "cpu"))
                policy_logits, _ = self.agent.ac_net(x_t)
                policy_probs = torch.nn.functional.softmax(policy_logits, dim=-1)
                return policy_probs.detach().cpu().numpy()

            self.explainer = shap.KernelExplainer(model_f, bg_summary)
            self.feature_names = explain_a2c.get_feature_names_with_position(window_size)

        except Exception as e:
            print(f"Error loading A2C model: {e}")
        finally:
            os.chdir(original_cwd)

    def get_historical_signals(self, start_date_str: str):
        """
        start_date_str (YYYY-MM-DD)부터 어제까지,
        날짜별 시그널 및 전략 수익률(strategy_return)을 리스트로 반환.
        """
        self.load_model()
        if not self.model_loaded:
            return []

        original_cwd = os.getcwd()
        os.chdir(A2C_DIR)

        try:
            from data_utils import download_data, add_indicators, FEATURES, build_state

            window_size = self.cfg["window_size"]

            # Parse start date
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")

            # 인디케이터 계산과 윈도우 확보를 위한 버퍼 기간 (6개월)
            data_start = (start_dt - timedelta(days=180)).strftime("%Y-%m-%d")
            end_dt = datetime.now()
            data_end = end_dt.strftime("%Y-%m-%d")

            raw_df = download_data(
                self.cfg["ticker"],
                self.cfg["kospi_ticker"],
                self.cfg["vix_ticker"],
                data_start,
                data_end,
            )
            df = add_indicators(raw_df)

            # Scale data
            if self.scaler is not None:
                df[FEATURES] = self.scaler.transform(df[FEATURES])

            results: List[Dict[str, Any]] = []

            target_date = start_dt
            yesterday = end_dt - timedelta(days=1)

            while target_date <= yesterday:
                date_str = target_date.strftime("%Y-%m-%d")

                if target_date not in df.index:
                    target_date += timedelta(days=1)
                    continue

                idx = df.index.get_loc(target_date)
                if idx < window_size - 1:
                    target_date += timedelta(days=1)
                    continue

                # prev_date = target_date - 1 에 대한 윈도우로 시그널 생성
                prev_date_loc = df.index.get_loc(df.index[df.index < target_date][-1])
                if prev_date_loc < window_size - 1:
                    target_date += timedelta(days=1)
                    continue

                prev_window = df.iloc[
                    prev_date_loc - (window_size - 1): prev_date_loc + 1
                ]
                state = build_state(prev_window, position_flag=0)

                with torch.no_grad():
                    s_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                    logits, _ = self.agent.ac_net(s_t)
                    probs = (
                        torch.nn.functional.softmax(logits, dim=-1)
                        .detach()
                        .cpu()
                        .numpy()[0]
                    )
                    action = int(np.argmax(probs))  # 0: Long, 1: Short, 2: Hold

                # 원시 가격으로 일간 수익률 계산
                curr_price = raw_df.loc[target_date]["Close"]
                prev_price = raw_df.iloc[raw_df.index.get_loc(target_date) - 1]["Close"]
                daily_pct_change = (curr_price - prev_price) / prev_price

                strategy_return = 0.0
                if action == 0:  # Long
                    strategy_return = daily_pct_change
                elif action == 1:  # Short
                    strategy_return = -daily_pct_change
                elif action == 2:  # Hold
                    strategy_return = 0.0

                results.append(
                    {
                        "date": date_str,
                        "signal": int(action),
                        "daily_return": float(daily_pct_change),
                        "strategy_return": float(strategy_return),
                    }
                )

                target_date += timedelta(days=1)

            return results

        except Exception as e:
            print(f"Error in A2C historical signals: {e}")
            import traceback

            traceback.print_exc()
            return []
        finally:
            os.chdir(original_cwd)

    def predict_today(self):
        """
        가장 최근 데이터(마지막 윈도우)를 사용해
        오늘(또는 다음 스텝)에 대한 액션 및 확률을 반환.
        """
        self.load_model()
        if not self.model_loaded:
            return None

        original_cwd = os.getcwd()
        os.chdir(A2C_DIR)

        try:
            from data_utils import download_data, add_indicators, FEATURES, build_state
            import explain_a2c

            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=100)

            raw_df = download_data(
                self.cfg["ticker"],
                self.cfg["kospi_ticker"],
                self.cfg["vix_ticker"],
                start_dt.strftime("%Y-%m-%d"),
                end_dt.strftime("%Y-%m-%d"),
            )
            df = add_indicators(raw_df)

            if self.scaler is not None:
                df[FEATURES] = self.scaler.transform(df[FEATURES])

            window_size = self.cfg["window_size"]
            if len(df) < window_size:
                return None

            last_window = df.iloc[-window_size:]
            last_date = df.index[-1]

            state = build_state(last_window, position_flag=0)

            with torch.no_grad():
                s_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                logits, _ = self.agent.ac_net(s_t)
                probs = (
                    torch.nn.functional.softmax(logits, dim=-1)
                    .detach()
                    .cpu()
                    .numpy()[0]
                )
                action = int(np.argmax(probs))

            # Get XAI features (Top-3)
            _, _, _, top_features = explain_a2c.get_top_features(
                state, self.agent, self.explainer, self.feature_names, top_k=3
            )

            # 🔹 Top-3 지표에 현재 값(value) 주입
            try:
                last_row = last_window.iloc[-1]  # 이 함수 안에서 이미 만든 마지막 윈도우 DataFrame
                for feat in top_features:
                    if not isinstance(feat, dict):
                        continue

                    base_name = (
                        feat.get("base")
                        or feat.get("name")
                        or feat.get("indicator")
                    )

                    if base_name and base_name in last_row.index:
                        try:
                            feat["value"] = float(last_row[base_name])
                        except Exception:
                            # 개별 지표 값 변환 실패해도 전체 로직엔 영향 없게 무시
                            pass
            except Exception:
                # value 주입과정 전체가 실패해도 모델 추론은 그대로 가도록
                pass

            return {
                "date": last_date.strftime("%Y-%m-%d"),
                "action": int(action),  # 0: Long, 1: Short, 2: Hold
                "probs": probs.tolist(),
                "xai_features": top_features,  # 이제 각 feat 안에 value가 들어 있음
            }

        except Exception as e:
            print(f"Error in A2C predict_today: {e}")
            return None
        finally:
            os.chdir(original_cwd)


class MarlWrapper:
    """
    MARL(QMIX) 3-agent 트레이딩 모델을 래핑하는 클래스.

    - load_model(): 모델/스케일러/DataProcessor 초기화
    - get_historical_signals(start_date_str): 날짜별 시그널 및 전략 수익률 계산
    - predict_today(): 가장 최근 윈도우 기준 액션/공동액션 반환
    """

    def __init__(self):
        self.model_loaded = False
        self.learner = None
        self.processor = None
        self.a0_cols = None
        self.a1_cols = None
        self.a2_cols = None
        self._setup_path()

    def _setup_path(self):
        if MARL_DIR not in sys.path:
            sys.path.append(MARL_DIR)

    def load_model(self):
        if self.model_loaded:
            return

        original_cwd = os.getcwd()
        os.chdir(MARL_DIR)

        try:
            import marl_config as config
            from qmix_model import QMIX_Learner
            from environment import MARLStockEnv
            import pickle
            from data_processor import DataProcessor

            today_str = datetime.now().strftime("%Y-%m-%d")
            self.processor = DataProcessor(end=today_str)

            (features_df, prices_df, _, self.a0_cols, self.a1_cols, self.a2_cols) = (
                self.processor.process()
            )

            if os.path.exists("scaler.pkl"):
                with open("scaler.pkl", "rb") as f:
                    self.processor.scalers = pickle.load(f)

            norm_features, _ = self.processor.normalize_data(
                features_df, features_df
            )

            dummy_env = MARLStockEnv(
                norm_features.iloc[-50:],
                prices_df.iloc[-50:],
                self.a0_cols,
                self.a1_cols,
                self.a2_cols,
            )

            self.learner = QMIX_Learner(
                [
                    dummy_env.observation_dim_0,
                    dummy_env.observation_dim_1,
                    dummy_env.observation_dim_2,
                ],
                dummy_env.action_dim,
                dummy_env.state_dim,
                config.DEVICE,
            )

            if os.path.exists("best_model.pth"):
                self.learner.load_state_dict(
                    torch.load("best_model.pth", map_location=config.DEVICE)
                )
                self.learner.eval()
                self.model_loaded = True
            else:
                print("Warning: MARL best_model.pth not found")

        except Exception as e:
            print(f"Error loading MARL model: {e}")
        finally:
            os.chdir(original_cwd)

    def get_historical_signals(self, start_date_str: str):
        """
        start_date_str부터 어제까지,
        MARL joint action → 최종 시그널 → 전략 수익률을 계산.
        """
        original_cwd = os.getcwd()
        os.chdir(MARL_DIR)

        try:
            self.load_model()
            if not self.model_loaded:
                return []

            from marl_config import WINDOW_SIZE
            from environment import MARLStockEnv
            from data_processor import DataProcessor
            from utils import convert_joint_action_to_signal
            import pickle

            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            data_start = (start_dt - timedelta(days=180)).strftime("%Y-%m-%d")
            end_dt = datetime.now()
            data_end = end_dt.strftime("%Y-%m-%d")

            processor = DataProcessor(start=data_start, end=data_end)
            (features_df, original_prices, _, a0, a1, a2) = processor.process()

            if os.path.exists("scaler.pkl"):
                with open("scaler.pkl", "rb") as f:
                    processor.scalers = pickle.load(f)

            norm_features, _ = processor.normalize_data(
                features_df, features_df
            )

            results: List[Dict[str, Any]] = []
            target_date = start_dt
            yesterday = end_dt - timedelta(days=1)

            dummy_env = MARLStockEnv(norm_features, original_prices, a0, a1, a2)

            while target_date <= yesterday:
                date_str = target_date.strftime("%Y-%m-%d")

                if target_date not in norm_features.index:
                    target_date += timedelta(days=1)
                    continue

                idx = norm_features.index.get_loc(target_date)
                prev_idx = idx - 1
                if prev_idx < WINDOW_SIZE - 1:
                    target_date += timedelta(days=1)
                    continue

                dummy_env.current_step = prev_idx - WINDOW_SIZE + 1
                obs_dict, _ = dummy_env._get_obs_and_state()

                with torch.no_grad():
                    actions = self.learner.select_actions(obs_dict, epsilon=0.0)

                joint_action = [actions[f"agent_{i}"] for i in range(3)]
                final_signal_str = convert_joint_action_to_signal(
                    joint_action, {0: "Long", 1: "Hold", 2: "Short"}
                )

                signal_int = 2  # Hold
                if final_signal_str == "Long":
                    signal_int = 0
                elif final_signal_str == "Short":
                    signal_int = 1

                curr_price = original_prices.loc[target_date]
                prev_price = original_prices.iloc[
                    original_prices.index.get_loc(target_date) - 1
                ]

                daily_pct_change = (curr_price - prev_price) / prev_price

                strategy_return = 0.0
                if signal_int == 0:  # Long
                    strategy_return = daily_pct_change
                elif signal_int == 1:  # Short
                    strategy_return = -daily_pct_change

                results.append(
                    {
                        "date": date_str,
                        "signal": signal_int,
                        "daily_return": float(daily_pct_change),
                        "strategy_return": float(strategy_return),
                    }
                )

                target_date += timedelta(days=1)

            return results

        except Exception as e:
            print(f"Error in MARL historical signals: {e}")
            import traceback

            traceback.print_exc()
            return []
        finally:
            os.chdir(original_cwd)

    def predict_today(self):
        """
        가장 최근 윈도우 기준으로 joint action → 최종 시그널을 계산.
        """
        original_cwd = os.getcwd()
        os.chdir(MARL_DIR)

        try:
            self.load_model()
            if not self.model_loaded:
                return None

            from marl_config import WINDOW_SIZE
            from environment import MARLStockEnv
            from utils import convert_joint_action_to_signal, get_top_features_marl

            (features_df, prices_df, _, a0, a1, a2) = self.processor.process()
            norm_features, _ = self.processor.normalize_data(
                features_df, features_df
            )

            dummy_env = MARLStockEnv(norm_features, prices_df, a0, a1, a2)

            if len(norm_features) < WINDOW_SIZE:
                print(
                    f"Not enough data for MARL prediction. Need {WINDOW_SIZE}, got {len(norm_features)}"
                )
                return None

            last_idx = len(norm_features) - WINDOW_SIZE
            dummy_env.current_step = last_idx
            obs_dict, _ = dummy_env._get_obs_and_state()

            with torch.no_grad():
                actions = self.learner.select_actions(obs_dict, epsilon=0.0)

            joint_action = [actions[f"agent_{i}"] for i in range(3)]
            final_signal_str = convert_joint_action_to_signal(
                joint_action, {0: "Long", 1: "Hold", 2: "Short"}
            )

            # --- XAI for MARL ---
            agent_analyses = []
            feature_names_list = [self.a0_cols, self.a1_cols, self.a2_cols]
            n_features_list = [len(c) for c in feature_names_list]

            for i, agent in enumerate(self.learner.agents):
                obs = obs_dict[f"agent_{i}"]
                _, q_vals, importance = agent.get_prediction_with_reason(
                    obs, feature_names_list[i], WINDOW_SIZE, n_features_list[i]
                )
                agent_analyses.append((actions[f"agent_{i}"], q_vals, importance))

            top_features = get_top_features_marl(agent_analyses)

            # 🔹 Top-3 지표에 현재 값(value) 주입
            try:
                # 위에서 self.processor.process(raw_df)는 이미 호출되어 있고,
                # 그 결과로 features_df / norm_features 같은 DataFrame이 있음
                last_row = features_df.iloc[-1]
                for feat in top_features:
                    if not isinstance(feat, dict):
                        continue

                    name = (
                        feat.get("name")
                        or feat.get("base")
                        or feat.get("indicator")
                    )

                    if name and name in last_row.index:
                        try:
                            feat["value"] = float(last_row[name])
                        except Exception:
                            pass
            except Exception:
                pass

            signal_int = 2
            if final_signal_str in ["매수", "적극 매수"]:
                signal_int = 0
            elif final_signal_str in ["매도", "적극 매도"]:
                signal_int = 1

            return {
                "date": norm_features.index[-1].strftime("%Y-%m-%d"),
                "action": signal_int,
                "action_str": final_signal_str,
                "joint_action": joint_action,
                "xai_features": top_features,  # 여기에도 value 붙음
            }

        except Exception as e:
            print(f"Error in MARL predict_today: {e}")
            return None
        finally:
            os.chdir(original_cwd)


# === 기존 래퍼 싱글톤 ===
a2c_wrapper = A2CWrapper()
marl_wrapper = MarlWrapper()


# === 공통 서비스 레이어 (B 파트 핵심) ===

# A2C / MARL 공통 액션 → BUY/SELL/HOLD 매핑
ACTION_ID_TO_EN = {
    0: "BUY",   # Long
    1: "SELL",  # Short
    2: "HOLD",  # Hold
}

ACTION_ID_TO_KO = {
    0: "매수",
    1: "매도",
    2: "관망",
}


class AIService:
    """
    FastAPI 라우터에서 직접 사용하는 상위 서비스 레이어.

    - A2CWrapper / MarlWrapper를 내부에서 사용
    - 주가 데이터 다운로드, 모델 inference, 히스토리 기반 승률 계산
    - "오늘의 추천 행동", "승률", "설명"을 포함한 JSON 응답 생성
    """

    def __init__(self):
        self.a2c = a2c_wrapper
        self.marl = marl_wrapper



    def _build_explanation(
        self,
        model_name: str,
        action_id: int,
        investment_style: str,
    ) -> str:
        """
        간단한 자연어 설명 생성.
        (추후 GPT 연동 시 이 부분만 교체하면 됨)
        """
        action_ko = ACTION_ID_TO_KO.get(action_id, "관망")
        model_label = "A2C 강화학습" if model_name == "a2c" else "MARL 3-에이전트"

        style_label = (
            "공격적인"
            if investment_style == "aggressive"
            else "안정적인"
        )

        # 규칙 기반 설명에는 [RULE] 태그
        return (
            f"[RULE] {model_label} 모델이 최근 학습된 패턴을 바탕으로 "
            f"{style_label} 투자 성향에 맞춰 오늘은 '{action_ko}' 전략이 유리하다고 판단했습니다."
        )

    def predict_today(
        self,
        symbol: Optional[str] = None,
        mode: str = "a2c",
        investment_style: str = "aggressive",
    ) -> Dict[str, Any]:
        """
        B 파트에서 실제로 사용할 진입점 함수.
        """
        if mode not in ("a2c", "marl"):
            raise ValueError(f"Unsupported mode: {mode}")

        # 일단 삼성전자 전용 모델이므로, symbol이 없으면 기본값 사용
        if symbol is None:
            symbol = "005930.KS"

        # 최근 6개월을 기준으로 승률 계산
        start_dt = datetime.now() - timedelta(days=180)
        start_str = start_dt.strftime("%Y-%m-%d")

        try:
            if mode == "a2c":
                today_pred = self.a2c.predict_today()
                if today_pred is None:
                    raise RuntimeError("A2C 오늘 예측에 실패했습니다.")

                hist_signals = self.a2c.get_historical_signals(start_str)

                action_id = int(today_pred["action"])
                probs = today_pred.get("probs", [])
                date_str = today_pred.get("date")

            else:  # mode == "marl"
                today_pred = self.marl.predict_today()
                if today_pred is None:
                    raise RuntimeError("MARL 오늘 예측에 실패했습니다.")

                hist_signals = self.marl.get_historical_signals(start_str)

                action_id = int(today_pred["action"])
                date_str = today_pred.get("date")

            action_en = ACTION_ID_TO_EN.get(action_id, "HOLD")
            action_ko = ACTION_ID_TO_KO.get(action_id, "관망")
            explanation = self._build_explanation(
                model_name=mode,
                action_id=action_id,
                investment_style=investment_style,
            )

            xai_features = today_pred.get("xai_features", [])

            # -----------------------------
            # OpenAI GPT 기반 상세 설명 시도
            # -----------------------------
            try:
                # XAI에서 넘어온 top features를 feature_importance / technical_indicators 형태로 변환
                feature_importance: Dict[str, float] = {}
                technical_indicators: Dict[str, float] = {}

                # Top-3만 사용 (xai_features 자체가 이미 top-k지만 방어적으로 [:3])
                for i, feat in enumerate(xai_features[:3]):
                    if not isinstance(feat, dict):
                        continue

                    # 🔹 지표 이름 통합: A2C(base), MARL(name) 모두 커버
                    fname = (
                        feat.get("name")
                        or feat.get("base")
                        or feat.get("feature")
                        or feat.get("indicator")
                        or f"feature_{i}"
                    )

                    # 🔹 중요도 추출: MARL(importance), A2C(shap) 모두 커버
                    importance_val: float = 0.0
                    for key in ("importance", "shap", "value", "score"):
                        if feat.get(key) is not None:
                            try:
                                importance_val = float(feat.get(key))  # type: ignore[arg-type]
                            except Exception:
                                importance_val = 0.0
                            break

                    feature_importance[fname] = importance_val

                    # 🔹 실제 지표 값(value)을 technical_indicators에 반영
                    if feat.get("value") is not None:
                        try:
                            technical_indicators[fname] = float(feat.get("value"))  # type: ignore[arg-type]
                        except Exception:
                            # value 파싱 실패 시에는 해당 지표만 생략
                            pass

                # GPT 서비스 호출
                gpt_explanation = interpret_model_output(
                    signal=action_en,
                    technical_indicators=technical_indicators,
                    feature_importance=feature_importance,
                )

                if isinstance(gpt_explanation, str) and gpt_explanation.strip():
                    # GPT가 성공하면 [GPT] 태그로 덮어쓰기
                    explanation = "[GPT] " + gpt_explanation.strip()

            except Exception as gpt_err:
                # GPT 호출 실패 시에는 기존 규칙 기반 설명 사용
                print(f"[AIService] GPT explanation failed, fallback to rule-based: {gpt_err}")

                if isinstance(gpt_explanation, str) and gpt_explanation.strip():
                    # GPT가 성공하면 [GPT] 태그로 덮어쓰기
                    explanation = "[GPT] " + gpt_explanation.strip()

            except Exception as gpt_err:
                # GPT 호출 실패 시에는 기존 규칙 기반 설명 사용
                print(f"[AIService] GPT explanation failed, fallback to rule-based: {gpt_err}")

            return {
                "symbol": symbol,
                "model": mode,
                "date": date_str,
                "action": action_en,          # "BUY" / "SELL" / "HOLD"
                "action_ko": action_ko,       # "매수" / "매도" / "관망"
                "investment_style": investment_style,
                "xai_features": xai_features, # Top-k XAI 지표
                "explanation": explanation,   # ★ GPT 결과(or fallback)
            }

        except Exception as e:
            print(f"[AIService] Error in predict_today: {e}")
            return {
                "symbol": symbol,
                "model": mode,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "action": "HOLD",
                "action_ko": "관망",
                "investment_style": investment_style,
                "explanation": (
                    "AI 예측 중 오류가 발생하여 기본적으로 '관망' 전략을 추천합니다. "
                    "상세 로그는 서버 콘솔을 확인해주세요."
                ),
            }


# 라우터에서 import 해서 사용할 싱글톤 인스턴스
ai_service = AIService()