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

# [중요] 같은 패키지 내 모듈이므로 상대 경로 import 사용
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


# ==================================================================================
# 1. 공통 유틸리티 (Action Selection Logic)
# ==================================================================================
def _select_action_from_logits(
    logits,
    temperature: float = 2.5,   
    min_conf: float = 0.70,     
    min_margin: float = 0.20,   
    sample: bool = True,
):
    """
    Logits -> Softmax(Temperature) -> Action 선택
    """
    probs = torch.nn.functional.softmax(logits / temperature, dim=-1).detach().cpu().numpy()[0]
    sorted_probs = np.sort(probs)[::-1]
    top_idx = int(np.argmax(probs))
    max_p = float(sorted_probs[0])
    second_p = float(sorted_probs[1]) if len(sorted_probs) > 1 else 0.0

    if (max_p < min_conf) or (max_p - second_p < min_margin):
        return 2, probs 

    if sample:
        sampled = int(np.random.choice(len(probs), p=probs))
        return sampled, probs

    return top_idx, probs


# ==================================================================================
# 2. A2C Wrapper
# ==================================================================================
class A2CWrapper:
    def __init__(self):
        self.model_loaded = False
        self.agent = None
        self.cfg = None
        self.scaler = None
        self.explainer = None
        self.feature_names = None

        # Caching
        self.cached_prediction = None
        self.cached_date = None

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

            bg_states = []
            bg_len = min(200 + window_size, len(df) - 1)
            for i in range(window_size - 1, bg_len):
                current_window = df.iloc[i - (window_size - 1): i + 1]
                s = data_utils.build_state(current_window, position_flag=0)
                bg_states.append(s)
            bg_states = np.array(bg_states, dtype=np.float32)

            if len(bg_states) > 100:
                bg_summary = shap.sample(bg_states, 100)
            else:
                bg_summary = bg_states

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
            return []

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
        # 1. Check Cache
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.cached_prediction is not None and self.cached_date == today_str:
            print(f"[A2C] Using cached prediction for {today_str}")
            return self.cached_prediction

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

            # Get XAI features (Top-3)
            _, _, _, top_features = explain_a2c.get_top_features(
                state, self.agent, self.explainer, self.feature_names, top_k=3
            )

            # Top-3 지표에 현재 값(value) 주입
            try:
                last_row = last_window.iloc[-1]
                for feat in top_features:
                    if not isinstance(feat, dict): continue
                    
                    base_name = (
                        feat.get("base") or feat.get("name") or feat.get("indicator")
                    )
                    if base_name and base_name in last_row.index:
                        try:
                            if base_name in raw_df.columns:
                                feat["value"] = float(raw_df.iloc[-1][base_name])
                            else:
                                feat["value"] = float(last_row[base_name])
                        except: pass
            except: pass

            print(f"[A2C] predict_today probs={probs.tolist()} action={action}")

            result = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "action": int(action),
                "probs": probs.tolist(),
                "xai_features": top_features,
            }
            
            # Update Cache
            self.cached_prediction = result
            self.cached_date = today_str
            
            return result

        except Exception as e:
            print(f"Error in A2C predict_today: {e}")
            return None
        finally:
            os.chdir(original_cwd)


# ==================================================================================
# 3. MARL Wrapper (Temperature Sampling + Value Injection 통합)
# ==================================================================================
class MarlWrapper:
    TEMP_HISTORY = 2.0 
    TEMP_TODAY = 1.5   

    def __init__(self):
        self.model_loaded = False
        self.learner = None
        self.processor = None
        self.a0_cols = None
        self.a1_cols = None
        self.a2_cols = None

        # Caching
        self.cached_prediction = None
        self.cached_date = None

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

            if os.path.exists("scalers.pkl"):
                with open("scalers.pkl", "rb") as f:
                    self.processor.scalers = pickle.load(f)
            
            norm_features, _ = self.processor.normalize_data(features_df, features_df)
            
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
                self.learner.agents[0].q_net.eval()
                self.model_loaded = True
                print("[MARL] Model loaded successfully.")
            else:
                print("[MARL] Warning: best_model.pth not found.")

        except Exception as e:
            print(f"[MARL] Model load failed: {e}")
        finally:
            os.chdir(original_cwd)

    def get_historical_signals(self, start_date_str: str):
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
                
                joint_action = []
                with torch.no_grad():
                    for i, agent in enumerate(self.learner.agents):
                        agent_id = f'agent_{i}'
                        obs = torch.FloatTensor(obs_dict[agent_id]).unsqueeze(0).to(self.learner.dvc)
                        q_values = agent.q_net(obs)
                        
                        probs = F.softmax(q_values / self.TEMP_HISTORY, dim=-1).cpu().numpy()[0]
                        action = np.random.choice(len(probs), p=probs)
                        joint_action.append(action)

                final_signal_str = convert_joint_action_to_signal(
                    joint_action, {0: "Long", 1: "Hold", 2: "Short"}
                )
                
                signal_int = 2
                if final_signal_str in ["매수", "적극 매수"]: signal_int = 0
                elif final_signal_str in ["매도", "적극 매도"]: signal_int = 1
                
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
        # 1. 이전에 예측한 데이터가 있는지 확인
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.cached_prediction is not None and self.cached_date == today_str:
            print(f"[MARL] Using cached prediction for {today_str}")
            return self.cached_prediction

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
            
            # [핵심 수정] XAI 역전파(Backprop)를 위해 torch.no_grad() 제거
            for i, agent in enumerate(self.learner.agents):
                obs = obs_dict[f"agent_{i}"]
                feature_names = [self.a0_cols, self.a1_cols, self.a2_cols][i]
                
                # 내부에서 gradients를 계산하므로 no_grad 바깥에서 실행해야 함
                _, q_vals, importance = agent.get_prediction_with_reason(
                    obs, feature_names, WINDOW_SIZE, len(feature_names)
                )
                
                # [적용] Sampling
                q_vals_tensor = q_vals.unsqueeze(0)
                probs = F.softmax(q_vals_tensor / self.TEMP_TODAY, dim=-1).detach().cpu().numpy()[0]
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

            # Top-3 지표에 현재 값(value) 주입
            try:
                last_row = features_df.iloc[-1]
                for feat in top_features:
                    if not isinstance(feat, dict): continue
                    name = (feat.get("name") or feat.get("base") or feat.get("indicator"))
                    if name and name in last_row.index:
                        try:
                            feat["value"] = float(last_row[name])
                        except: pass
            except: pass
            
            result = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "action": signal_int,
                "action_str": final_signal_str,
                "joint_action": joint_action,
                "xai_features": top_features
            }

            # 예측 기록 업데이트
            self.cached_prediction = result
            self.cached_date = today_str

            return result
            
        except Exception as e:
            print(f"[MARL] Predict Error: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            os.chdir(original_cwd)


# === Global Instances ===
a2c_wrapper = A2CWrapper()
marl_wrapper = MarlWrapper()


# === Service Layer (통합된 예측 및 GPT 설명 서비스) ===
ACTION_ID_TO_EN = {0: "BUY", 1: "SELL", 2: "HOLD"}
ACTION_ID_TO_KO = {0: "매수", 1: "매도", 2: "관망"}

class AIService:
    def __init__(self):
        self.a2c = a2c_wrapper
        self.marl = marl_wrapper
        # 캐싱을 위한 딕셔너리
        self.prediction_cache = {}

    def predict_today(self, symbol: Optional[str] = None, mode: str = "a2c", investment_style: str = "aggressive") -> Dict[str, Any]:
        if mode not in ("a2c", "marl"):
            raise ValueError(f"Unsupported mode: {mode}")

        if symbol is None:
            symbol = "005930.KS"

        # 1. 캐시 확인 (오늘 날짜 + 조건이 같으면 캐시 리턴)
        today_str = datetime.now().strftime("%Y-%m-%d")
        cache_key = (today_str, symbol, mode, investment_style)

        if cache_key in self.prediction_cache:
            print(f"[AIService] Using cached result for {cache_key}")
            return self.prediction_cache[cache_key]

        try:
            # 2. 모델 예측 실행
            if mode == "a2c":
                today_pred = self.a2c.predict_today()
            else:
                today_pred = self.marl.predict_today()

            if today_pred is None:
                raise RuntimeError(f"{mode.upper()} 오늘 예측 실패")

            action_id = int(today_pred["action"])
            date_str = today_pred.get("date")
            # XAI Feature 리스트 (Top 3)
            xai_features = today_pred.get("xai_features", [])

            action_en = ACTION_ID_TO_EN.get(action_id, "HOLD")
            action_ko = ACTION_ID_TO_KO.get(action_id, "관망")
            
            # 기본값 설정 (GPT 실패 대비)
            explanation = f"AI 모델이 {action_ko} 포지션을 추천합니다."
            
            # 3. GPT 서비스를 호출하여 '구체적 이유' 생성
            try:
                gpt_result = interpret_model_output(
                    signal=action_ko,       # "매수" / "매도"
                    xai_features=xai_features # 지표 리스트 통째로 전달
                )
                
                # 3-1. 종합 설명 적용
                if gpt_result.get("global_explanation"):
                    explanation = gpt_result["global_explanation"]
                
                # 3-2. 각 지표별 설명(explain) 매핑
                explanations_list = gpt_result.get("feature_explanations", [])
                
                for i, feat in enumerate(xai_features):
                    # GPT가 준 리스트 순서대로 매핑
                    if i < len(explanations_list):
                        feat["explain"] = explanations_list[i]
                    else:
                        feat["explain"] = f"{feat.get('base')} 지표가 예측에 기여했습니다."

            except Exception as e:
                print(f"[AIService] GPT Generation Failed: {e}")
                # 실패 시에도 기본 explain 필드는 있어야 함
                for feat in xai_features:
                    feat["explain"] = "상세 분석 정보를 불러오지 못했습니다."

            # 4. 최종 결과 조립
            result = {
                "symbol": symbol,
                "model": mode,
                "date": date_str,
                "action": action_en,
                "action_ko": action_ko,
                "investment_style": investment_style,
                "xai_features": xai_features,  # 여기에 'explain'이 채워져 있음
                "explanation": explanation,
            }

            # 캐시에 저장
            self.prediction_cache[cache_key] = result
            return result

        except Exception as e:
            print(f"[AIService] Critical Error: {e}")
            return None

ai_service = AIService()