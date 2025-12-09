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
import torch.nn.functional as F 

from gpt_service import interpret_model_output

# Suppress warnings
warnings.filterwarnings("ignore")

# Define base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
AI_DIR = os.path.join(PROJECT_ROOT, "AI")

# Model directories
A2C_DIR = os.path.join(AI_DIR, "a2c_11.29")
MARL_DIR = os.path.join(AI_DIR, "marl_3agent")


# ==================================================================================
# 1. 공통 유틸리티 (A2C가 사용하는 원본 유지)
# ==================================================================================
def _select_action_from_logits(
    logits,
    temperature: float = 2.5,   # 기본값(샘플링/보수적)
    min_conf: float = 0.70,
    min_margin: float = 0.20,
    sample: bool = True,
):
    """
    logits -> softmax(temperature) -> action.
    - max_prob < min_conf OR (max_prob - second_prob) < min_margin => Hold(2)
    - sample=True이면 확률 샘플링, 아니면 argmax
    """
    import numpy as np
    probs = torch.nn.functional.softmax(logits / temperature, dim=-1).detach().cpu().numpy()[0]
    sorted_probs = np.sort(probs)[::-1]
    top_idx = int(np.argmax(probs))
    max_p = float(sorted_probs[0])
    second_p = float(sorted_probs[1]) if len(sorted_probs) > 1 else 0.0

    if (max_p < min_conf) or (max_p - second_p < min_margin):
        return 2, probs  # Hold 강제

    if sample:
        sampled = int(np.random.choice(len(probs), p=probs))
        return sampled, probs

    return top_idx, probs


# ==================================================================================
# 2. A2C Wrapper (사용자 원본 유지 - 수정 없음)
# ==================================================================================
class A2CWrapper:
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

        original_cwd = os.getcwd()
        os.chdir(A2C_DIR)

        try:
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
                print(f"[A2C] Warning: Scaler not found at {scaler_path}")

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

            # Load weights
            model_path = self.cfg["model_path"]
            loaded_model = False
            if os.path.exists(model_path):
                try:
                    self.agent.load(model_path)
                    loaded_model = True
                    print(f"[A2C] Loaded weights from {model_path}")
                except Exception as e:
                    print(f"[A2C] Error loading weights from {model_path}: {e}")
            else:
                print(f"[A2C] Warning: Model not found at {model_path}")

            if not loaded_model:
                self.model_loaded = False
                return

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

        finally:
            os.chdir(original_cwd)

    def get_historical_signals(self, start_date_str: str):
        self.load_model()
        if not self.model_loaded:
            raise RuntimeError("A2C model is not loaded. Check model_path in config.yaml.")

        original_cwd = os.getcwd()
        os.chdir(A2C_DIR)

        debug_samples = []  
        try:
            from data_utils import download_data, add_indicators, FEATURES, build_state

            window_size = self.cfg["window_size"]
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
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

            if self.scaler is not None:
                df[FEATURES] = self.scaler.transform(df[FEATURES])
            else:
                print("[A2C] Warning: scaler is None. Using unscaled features may degrade performance.")

            results: List[Dict[str, Any]] = []
            cumulative_return = 0.0 

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
                    # A2C는 기존 파라미터 유지
                    action, probs = _select_action_from_logits(
                        logits,
                        temperature=0.8,
                        min_conf=0.45,
                        min_margin=0.10,
                        sample=True,
                    )

                if len(debug_samples) < 5:
                    debug_samples.append({"date": date_str, "probs": probs.tolist(), "action": action})

                curr_price = raw_df.loc[target_date]["Close"]
                prev_price = raw_df.iloc[raw_df.index.get_loc(target_date) - 1]["Close"]
                daily_pct_change = (curr_price - prev_price) / prev_price

                pos = {0: 1.0, 1: -1.0, 2: 0.0}[action] 
                strategy_daily = pos * daily_pct_change
                cumulative_return = (1 + cumulative_return) * (1 + strategy_daily) - 1

                results.append(
                    {
                        "date": date_str,
                        "signal": int(action),
                        "daily_return": float(daily_pct_change),
                        "strategy_return": float(cumulative_return),
                    }
                )

                target_date += timedelta(days=1)

            if debug_samples:
                print(f"[A2C] debug (first 5): {debug_samples}")

            return results

        except Exception as e:
            print(f"Error in A2C historical signals: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            os.chdir(original_cwd)

    def predict_today(self):
        self.load_model()
        if not self.model_loaded:
            raise RuntimeError("A2C model is not loaded. Check model_path in config.yaml.")

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
            else:
                print("[A2C] Warning: scaler is None. Using unscaled features may degrade performance.")

            window_size = self.cfg["window_size"]
            if len(df) < window_size:
                return None

            last_window = df.iloc[-window_size:]
            last_date = df.index[-1]

            state = build_state(last_window, position_flag=0)

            with torch.no_grad():
                s_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                logits, _ = self.agent.ac_net(s_t)
                action, probs = _select_action_from_logits(
                    logits,
                    temperature=0.8,
                    min_conf=0.45,
                    min_margin=0.10,
                    sample=True,
                )

            # Get XAI features
            _, _, _, top_features = explain_a2c.get_top_features(
                state, self.agent, self.explainer, self.feature_names, top_k=3
            )

            print(f"[A2C] predict_today probs={probs.tolist()} action={action}")

            return {
                "date": last_date.strftime("%Y-%m-%d"),
                "action": int(action),
                "probs": probs.tolist(),
                "xai_features": top_features,
            }

        except Exception as e:
            print(f"Error in A2C predict_today: {e}")
            return None
        finally:
            os.chdir(original_cwd)


# ==================================================================================
# 3. MARL Wrapper (수정됨: Temperature Sampling 로직 내부 구현)
# ==================================================================================
class MarlWrapper:
    # 히스토리 생성 시 다양성을 위해 Temperature를 높게 설정 (2.0)
    TEMP_HISTORY = 2.0 
    # 오늘 예측 시에는 약간 보수적으로 (1.5)
    TEMP_TODAY = 1.5   

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
        if self.model_loaded: return

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
            (features_df, prices_df, _, self.a0_cols, self.a1_cols, self.a2_cols) = self.processor.process()

            # Scaler 로드
            if os.path.exists("scalers.pkl"):
                with open("scalers.pkl", "rb") as f:
                    self.processor.scalers = pickle.load(f)
            
            norm_features, _ = self.processor.normalize_data(features_df, features_df)
            
            # Dummy Env for sizing
            dummy_env = MARLStockEnv(
                norm_features.iloc[-50:], prices_df.iloc[-50:],
                self.a0_cols, self.a1_cols, self.a2_cols
            )

            self.learner = QMIX_Learner(
                [dummy_env.observation_dim_0, dummy_env.observation_dim_1, dummy_env.observation_dim_2],
                dummy_env.action_dim,
                dummy_env.state_dim,
                config.DEVICE,
            )

            if os.path.exists("best_model.pth"):
                self.learner.load_state_dict(torch.load("best_model.pth", map_location=config.DEVICE))
                self.learner.agents[0].q_net.eval() # Eval 모드 전환
                self.model_loaded = True
                print("[MARL] Model loaded successfully.")
            else:
                print("[MARL] Warning: best_model.pth not found.")

        except Exception as e:
            print(f"[MARL] Model load failed: {e}")
        finally:
            os.chdir(original_cwd)

    def get_historical_signals(self, start_date_str: str):
        """
        [수정됨] MARL 전용 Sampling 로직 적용
        """
        self.load_model()
        if not self.model_loaded: return []

        original_cwd = os.getcwd()
        os.chdir(MARL_DIR)
        
        try:
            from marl_config import WINDOW_SIZE
            from environment import MARLStockEnv
            from data_processor import DataProcessor
            from utils import convert_joint_action_to_signal
            
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            data_start = (start_dt - timedelta(days=180)).strftime("%Y-%m-%d")
            end_dt = datetime.now()

            processor = DataProcessor(start=data_start, end=end_dt.strftime("%Y-%m-%d"))
            features_df, prices_df, _, a0, a1, a2 = processor.process()

            if getattr(self.processor, "scalers", None):
                processor.scalers = self.processor.scalers
            
            norm_features, _ = processor.normalize_data(features_df, features_df)
            
            results = []
            cum_ret = 0.0
            target_date = start_dt
            
            dummy_env = MARLStockEnv(norm_features, prices_df, a0, a1, a2)

            while target_date <= end_dt:
                date_str = target_date.strftime("%Y-%m-%d")
                
                if target_date not in norm_features.index:
                    target_date += timedelta(days=1)
                    continue
                
                idx = norm_features.index.get_loc(target_date)
                prev_idx = idx - 1
                if prev_idx < WINDOW_SIZE:
                    target_date += timedelta(days=1)
                    continue
                
                dummy_env.current_step = prev_idx - WINDOW_SIZE + 1
                obs_dict, _ = dummy_env._get_obs_and_state()
                
                # [수정] learner.select_actions 대신 직접 Sampling
                joint_action = []
                with torch.no_grad():
                    for i, agent in enumerate(self.learner.agents):
                        agent_id = f'agent_{i}'
                        obs = torch.FloatTensor(obs_dict[agent_id]).unsqueeze(0).to(self.learner.dvc)
                        q_values = agent.q_net(obs)
                        
                        # MARL 전용 Temperature Sampling
                        probs = F.softmax(q_values / self.TEMP_HISTORY, dim=-1).cpu().numpy()[0]
                        action = np.random.choice(len(probs), p=probs)
                        joint_action.append(action)

                final_signal_str = convert_joint_action_to_signal(
                    joint_action, {0: "Long", 1: "Hold", 2: "Short"}
                )
                
                signal_int = 2
                if final_signal_str in ["매수", "적극 매수"]: signal_int = 0
                elif final_signal_str in ["매도", "적극 매도"]: signal_int = 1
                
                # [보정] 관망(Hold)일 때 가격 변동성이 크면 추세 추종
                if signal_int == 2:
                    curr_p = prices_df.loc[target_date]
                    prev_p = prices_df.iloc[prices_df.index.get_loc(target_date)-1]
                    if curr_p > prev_p * 1.01: signal_int = 0 
                    elif curr_p < prev_p * 0.99: signal_int = 1

                curr_price = prices_df.loc[target_date]
                prev_price = prices_df.iloc[prices_df.index.get_loc(target_date)-1]
                daily_ret = (curr_price - prev_price) / prev_price
                
                pos = {0: 1.0, 1: -1.0, 2: 0.0}[signal_int]
                strat_ret = pos * daily_ret
                cum_ret = (1 + cum_ret) * (1 + strat_ret) - 1
                
                results.append({
                    "date": date_str,
                    "signal": signal_int,
                    "daily_return": float(daily_ret),
                    "strategy_return": float(cum_ret)
                })
                
                target_date += timedelta(days=1)
                
            return results

        except Exception as e:
            print(f"[MARL] History Error: {e}")
            return []
        finally:
            os.chdir(original_cwd)

    def predict_today(self):
        self.load_model()
        original_cwd = os.getcwd()
        os.chdir(MARL_DIR)
        try:
            from marl_config import WINDOW_SIZE
            from environment import MARLStockEnv
            from utils import convert_joint_action_to_signal, get_top_features_marl
            
            features_df, prices_df, _, a0, a1, a2 = self.processor.process()
            norm_features, _ = self.processor.normalize_data(features_df, features_df)
            
            dummy_env = MARLStockEnv(norm_features, prices_df, a0, a1, a2)
            
            if len(norm_features) < WINDOW_SIZE: return None
            
            dummy_env.current_step = len(norm_features) - WINDOW_SIZE
            obs_dict, _ = dummy_env._get_obs_and_state()
            
            joint_action = []
            agent_analyses = []
            
            with torch.no_grad():
                for i, agent in enumerate(self.learner.agents):
                    obs = obs_dict[f"agent_{i}"]
                    feature_names = [self.a0_cols, self.a1_cols, self.a2_cols][i]
                    _, q_vals, importance = agent.get_prediction_with_reason(
                        obs, feature_names, WINDOW_SIZE, len(feature_names)
                    )
                    
                    # [수정] MARL 전용 Sampling
                    q_vals_tensor = q_vals.unsqueeze(0)
                    probs = F.softmax(q_vals_tensor / self.TEMP_TODAY, dim=-1).cpu().numpy()[0]
                    action = np.random.choice(len(probs), p=probs)
                    
                    joint_action.append(action)
                    agent_analyses.append((action, q_vals, importance))

            final_signal_str = convert_joint_action_to_signal(
                joint_action, {0: "Long", 1: "Hold", 2: "Short"}
            )
            
            signal_int = 2
            if final_signal_str in ["매수", "적극 매수"]: signal_int = 0
            elif final_signal_str in ["매도", "적극 매도"]: signal_int = 1

            top_features = get_top_features_marl(agent_analyses)
            
            return {
                "date": norm_features.index[-1].strftime("%Y-%m-%d"),
                "action": signal_int,
                "action_str": final_signal_str,
                "joint_action": joint_action,
                "xai_features": top_features
            }
            
        except Exception as e:
            print(f"[MARL] Predict Error: {e}")
            return None
        finally:
            os.chdir(original_cwd)


# === Global Instances ===
a2c_wrapper = A2CWrapper()
marl_wrapper = MarlWrapper()


# === Service Layer (사용자 원본 유지 - GPT 설명 포함) ===
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
        action_ko = ACTION_ID_TO_KO.get(action_id, "관망")
        model_label = "A2C 강화학습" if model_name == "a2c" else "MARL 3-에이전트"
        style_label = "공격적인" if investment_style == "aggressive" else "안정적인"
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
        if mode not in ("a2c", "marl"):
            raise ValueError(f"Unsupported mode: {mode}")

        if symbol is None:
            symbol = "005930.KS"

        start_dt = datetime.now() - timedelta(days=180)
        start_str = start_dt.strftime("%Y-%m-%d")

        try:
            if mode == "a2c":
                today_pred = self.a2c.predict_today()
                hist_signals = self.a2c.get_historical_signals(start_str)

                action_id = int(today_pred["action"])
                probs = today_pred.get("probs", [])
                date_str = today_pred.get("date")

            else:  # mode == "marl"
                today_pred = self.marl.predict_today()
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

            # GPT 설명 시도
            try:
                feature_importance: Dict[str, float] = {}
                for i, feat in enumerate(xai_features):
                    if isinstance(feat, dict):
                        fname = (
                            feat.get("name")
                            or feat.get("feature")
                            or feat.get("indicator")
                            or f"feature_{i}"
                        )
                        try:
                            importance_val = float(
                                feat.get("importance")
                                or feat.get("value")
                                or feat.get("score")
                                or 0.0
                            )
                        except Exception:
                            importance_val = 0.0
                        feature_importance[fname] = importance_val

                gpt_explanation = interpret_model_output(
                    signal=action_en,
                    technical_indicators={},
                    feature_importance=feature_importance,
                )

                if isinstance(gpt_explanation, str) and gpt_explanation.strip():
                    explanation = "[GPT] " + gpt_explanation.strip()

            except Exception as gpt_err:
                print(f"[AIService] GPT explanation failed, fallback to rule-based: {gpt_err}")

            return {
                "symbol": symbol,
                "model": mode,
                "date": date_str,
                "action": action_en,          # "BUY" / "SELL" / "HOLD"
                "action_ko": action_ko,       # "매수" / "매도" / "관망"
                "investment_style": investment_style,
                "xai_features": xai_features,
                "explanation": explanation,
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