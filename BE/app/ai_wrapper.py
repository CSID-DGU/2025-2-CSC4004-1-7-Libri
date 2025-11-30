import sys
import os
import pandas as pd
import numpy as np
import torch
import joblib
from datetime import datetime, timedelta
import yaml
import warnings

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
            # Import modules from A2C directory
            # We need to be in the directory for relative imports/config loading to work usually, 
            # but let's try to handle it gracefully.
            # Ideally, we temporarily change cwd or ensure paths are absolute in the AI code.
            # For now, we will rely on sys.path and potentially changing CWD if needed.
            
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
            
        except Exception as e:
            print(f"Error loading A2C model: {e}")
        finally:
            os.chdir(original_cwd)

    def get_historical_signals(self, start_date_str: str):
        self.load_model()
        if not self.model_loaded:
            return []

        original_cwd = os.getcwd()
        os.chdir(A2C_DIR)
        
        try:
            from data_utils import download_data, add_indicators, FEATURES, build_state
            
            # Download data from start_date to yesterday (or today to ensure we have enough)
            # We need extra data for windowing
            window_size = self.cfg["window_size"]
            
            # Parse start date
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            # We need data from before start_date to calculate indicators and window
            # A safe buffer is 6 months
            data_start = (start_dt - timedelta(days=180)).strftime("%Y-%m-%d")
            end_dt = datetime.now()
            data_end = end_dt.strftime("%Y-%m-%d")

            raw_df = download_data(
                self.cfg["ticker"],
                self.cfg["kospi_ticker"],
                self.cfg["vix_ticker"],
                data_start,
                data_end
            )
            df = add_indicators(raw_df)
            
            # Scale data
            if self.scaler:
                df[FEATURES] = self.scaler.transform(df[FEATURES])

            results = []
            
            # Iterate from start_date to yesterday
            target_date = start_dt
            yesterday = end_dt - timedelta(days=1)
            
            while target_date <= yesterday:
                date_str = target_date.strftime("%Y-%m-%d")
                
                if target_date not in df.index:
                    target_date += timedelta(days=1)
                    continue

                # Get window
                idx = df.index.get_loc(target_date)
                if idx < window_size - 1:
                    target_date += timedelta(days=1)
                    continue
                    
                window = df.iloc[idx - (window_size - 1) : idx + 1]
                
                # Build state (assume position 0 for simplicity or track it)
                # For historical simulation, we might assume 0 or last action. 
                # Let's assume 0 (Neutral) for independent signal generation.
                state = build_state(window, position_flag=0)
                
                # Predict
                with torch.no_grad():
                    s_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                    logits, _ = self.agent.ac_net(s_t)
                    probs = torch.nn.functional.softmax(logits, dim=-1).detach().cpu().numpy()[0]
                    action = int(np.argmax(probs))

                # Calculate Return
                # Return is (Close_today - Close_yesterday) / Close_yesterday
                # But we need to know the return of the action taken YESTERDAY for TODAY's price movement?
                # Or is the signal for TODAY based on data until YESTERDAY?
                # Usually: Data until T-1 -> Signal for T -> Return at T (Close_T - Close_T-1)
                
                # Let's assume signal is for the current 'target_date' based on window ending at 'target_date' (Close is available?)
                # Wait, if we use Close of target_date, we are peeking.
                # Real-time: We have data until T-1 (Close). We predict for T.
                # In backtest: We are at T. We use data until T-1?
                # The 'build_state' uses the window ending at 'idx'. If 'idx' is 'target_date', it includes 'target_date' data.
                # So if we want to predict for 'target_date', we should use data until 'target_date - 1'.
                
                # Let's adjust: Signal for T is generated using data up to T-1.
                # So for a given date T, we look at window ending at T-1.
                
                prev_idx = idx - 1
                if prev_idx < window_size - 1:
                     target_date += timedelta(days=1)
                     continue
                     
                # Window ending yesterday
                # But wait, the A2C implementation in api_server.py uses:
                # target_idx = len(TEST_DF) - 2 (second to last?)
                # target_window = TEST_DF.iloc[target_idx - (WINDOW_SIZE - 1) : target_idx + 1]
                # target_date = TEST_DF.index[target_idx]
                # It seems it predicts for the date of the last data point in window?
                # Let's stick to standard logic: Signal for T uses info available at T-1 (or T Open).
                # If the model was trained on (State_t, Action_t) -> Reward_t+1, then State_t includes info up to t.
                
                # Let's assume the model takes data up to Day X and predicts action for Day X+1.
                # So to get signal for 'target_date', we use window ending at 'target_date - 1'.
                
                # However, to calculate return for 'target_date', we need (Close_target - Close_prev) / Close_prev.
                
                # Let's refine:
                # 1. Get Close price of target_date and prev_date.
                # 2. Calculate daily_return = (Close_target - Close_prev) / Close_prev.
                # 3. Generate Signal for target_date using data up to prev_date.
                
                # Re-check A2C logic.
                # It seems 'build_state' takes a window.
                # If we want to simulate "What would AI say on morning of 2025-10-01?", we pass data up to 2025-09-30.
                
                prev_date_loc = df.index.get_loc(df.index[df.index < target_date][-1])
                if prev_date_loc < window_size - 1:
                    target_date += timedelta(days=1)
                    continue
                    
                prev_window = df.iloc[prev_date_loc - (window_size - 1) : prev_date_loc + 1]
                state = build_state(prev_window, position_flag=0)
                
                with torch.no_grad():
                    s_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                    logits, _ = self.agent.ac_net(s_t)
                    probs = torch.nn.functional.softmax(logits, dim=-1).detach().cpu().numpy()[0]
                    action = int(np.argmax(probs)) # 0: Long, 1: Short, 2: Hold (Check mapping)
                
                # A2C Map: 0: Long, 1: Short, 2: Hold
                
                # Calculate Return
                # We need raw prices for return, not scaled.
                # raw_df has the original prices.
                # Ensure we get the correct row from raw_df
                
                curr_price = raw_df.loc[target_date]["Close"]
                prev_price = raw_df.iloc[raw_df.index.get_loc(target_date) - 1]["Close"]
                
                daily_pct_change = (curr_price - prev_price) / prev_price
                
                strategy_return = 0.0
                if action == 0: # Long
                    strategy_return = daily_pct_change
                elif action == 1: # Short
                    strategy_return = -daily_pct_change
                elif action == 2: # Hold
                    strategy_return = 0.0
                    
                results.append({
                    "date": date_str,
                    "signal": int(action), # 0, 1, 2
                    "daily_return": float(daily_pct_change),
                    "strategy_return": float(strategy_return)
                })
                
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
        self.load_model()
        if not self.model_loaded:
            return None

        original_cwd = os.getcwd()
        os.chdir(A2C_DIR)
        
        try:
            from data_utils import download_data, add_indicators, FEATURES, build_state
            
            # Download recent data
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=100) # Enough for window
            
            raw_df = download_data(
                self.cfg["ticker"],
                self.cfg["kospi_ticker"],
                self.cfg["vix_ticker"],
                start_dt.strftime("%Y-%m-%d"),
                end_dt.strftime("%Y-%m-%d")
            )
            df = add_indicators(raw_df)
            
            if self.scaler:
                df[FEATURES] = self.scaler.transform(df[FEATURES])
                
            # Use last available window (assuming it ends yesterday/today depending on market close)
            # If today is trading day and market is open, we might have today's partial data?
            # Usually we predict for "Tomorrow" using "Today's Close", or "Today" using "Yesterday's Close".
            # Let's assume we predict for the NEXT step based on LAST available data.
            
            window_size = self.cfg["window_size"]
            if len(df) < window_size:
                return None
                
            last_window = df.iloc[-window_size:]
            last_date = df.index[-1]
            
            state = build_state(last_window, position_flag=0)
            
            with torch.no_grad():
                s_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
                logits, _ = self.agent.ac_net(s_t)
                probs = torch.nn.functional.softmax(logits, dim=-1).detach().cpu().numpy()[0]
                action = int(np.argmax(probs))
                
            return {
                "date": last_date.strftime("%Y-%m-%d"),
                "action": int(action),
                "probs": probs.tolist()
            }
            
        except Exception as e:
            print(f"Error in A2C predict_today: {e}")
            return None
        finally:
            os.chdir(original_cwd)


class MarlWrapper:
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
            import config
            from qmix_model import QMIX_Learner
            from environment import MARLStockEnv
            import pickle
            
            # We need to know input dimensions to init QMIX_Learner
            # These are usually determined by data columns.
            # Let's try to load them or infer them.
            # In inference.py, it processes data first to get cols.
            # We might need to do the same.
            
            from data_processor import DataProcessor
            # Override end date to today for inference
            today_str = datetime.now().strftime("%Y-%m-%d")
            self.processor = DataProcessor(end=today_str)
            # We don't want to fetch all data just to load model if possible, 
            # but the model architecture depends on feature counts.
            # Let's do a minimal process or hardcode if we knew.
            # inference.py does: (features_df, _, _, a0_cols, a1_cols, a2_cols) = processor.process()
            
            # To avoid heavy download on init, maybe we only do it when needed?
            # But we need 'learner' for prediction.
            # Let's defer learner creation to the first prediction call if needed, 
            # or just do it here.
            
            # For now, let's assume we need to run processor.process() to get dimensions.
            # It downloads data.
            (features_df, prices_df, _, self.a0_cols, self.a1_cols, self.a2_cols) = self.processor.process()
            
            # Load Scaler
            if os.path.exists('scaler.pkl'):
                with open('scaler.pkl', 'rb') as f:
                    self.processor.scalers = pickle.load(f)
            
            # Normalize to get dummy env for dims
            norm_features, _ = self.processor.normalize_data(features_df, features_df)
            
            dummy_env = MARLStockEnv(norm_features.iloc[-50:], prices_df.iloc[-50:], self.a0_cols, self.a1_cols, self.a2_cols)
            
            self.learner = QMIX_Learner(
                [dummy_env.observation_dim_0, dummy_env.observation_dim_1, dummy_env.observation_dim_2],
                dummy_env.action_dim, dummy_env.state_dim, config.DEVICE
            )
            
            if os.path.exists('best_model.pth'):
                self.learner.load_state_dict(torch.load('best_model.pth', map_location=config.DEVICE))
                self.learner.eval()
                self.model_loaded = True
            else:
                print("Warning: MARL best_model.pth not found")
                
        except Exception as e:
            print(f"Error loading MARL model: {e}")
        finally:
            os.chdir(original_cwd)

    def get_historical_signals(self, start_date_str: str):
        # Similar logic to A2C but for MARL
        # MARL inference is a bit more complex with agents.
        # We need to iterate and construct observations.
        
        original_cwd = os.getcwd()
        os.chdir(MARL_DIR)
        
        try:
            self.load_model()
            if not self.model_loaded:
                return []
                
            from config import WINDOW_SIZE, DEVICE
            from environment import MARLStockEnv
            
            # We already have data in self.processor from load_model (if we cache it?)
            # But we need to ensure we have data covering the historical period.
            # The DataProcessor by default downloads START_DATE to END_DATE from config.
            # We might need to override dates in DataProcessor or config?
            # DataProcessor takes start/end in __init__.
            
            # Re-init processor with wider range if needed
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            data_start = (start_dt - timedelta(days=180)).strftime("%Y-%m-%d")
            end_dt = datetime.now()
            data_end = end_dt.strftime("%Y-%m-%d")
            
            # We can create a new processor instance
            from data_processor import DataProcessor
            processor = DataProcessor(start=data_start, end=data_end)
            (features_df, original_prices, _, a0, a1, a2) = processor.process()
            
            # Load scalers if not already
            import pickle
            if os.path.exists('scaler.pkl'):
                with open('scaler.pkl', 'rb') as f:
                    processor.scalers = pickle.load(f)
            
            norm_features, _ = processor.normalize_data(features_df, features_df)
            
            # We need to simulate step by step?
            # Or just construct state for each day.
            # MARLStockEnv can help construct state.
            
            # We need to iterate dates.
            results = []
            target_date = start_dt
            yesterday = end_dt - timedelta(days=1)
            
            # Create a dummy env to use its methods
            dummy_env = MARLStockEnv(norm_features, original_prices, a0, a1, a2)
            
            while target_date <= yesterday:
                date_str = target_date.strftime("%Y-%m-%d")
                
                if target_date not in norm_features.index:
                    target_date += timedelta(days=1)
                    continue
                    
                # Index in norm_features
                idx = norm_features.index.get_loc(target_date)
                
                # We need window ending at T-1 to predict for T
                prev_idx = idx - 1
                if prev_idx < WINDOW_SIZE - 1:
                    target_date += timedelta(days=1)
                    continue
                
                # Set env to this step
                # MARLStockEnv uses current_step as the START of the window.
                # We want the window to END at prev_idx (target_date - 1).
                # Window: [start, start + window_size - 1]
                # Last index = start + window_size - 1 = prev_idx
                # start = prev_idx - window_size + 1
                
                dummy_env.current_step = prev_idx - WINDOW_SIZE + 1
                obs_dict, _ = dummy_env._get_obs_and_state()
                
                with torch.no_grad():
                    actions = self.learner.select_actions(obs_dict, epsilon=0.0)
                    
                # Joint action to signal
                # 0: Long, 1: Hold, 2: Short (Check utils.py or inference.py)
                # inference.py: action_map = {0: "Long", 1: "Hold", 2: "Short"}
                # utils.convert_joint_action_to_signal logic?
                # Let's import it
                from utils import convert_joint_action_to_signal
                
                joint_action = [actions[f'agent_{i}'] for i in range(3)]
                # This returns string "Long", "Hold", "Short"
                final_signal_str = convert_joint_action_to_signal(joint_action, {0: "Long", 1: "Hold", 2: "Short"})
                
                # Map back to int for consistency? 
                # A2C: 0=Long, 1=Short, 2=Hold
                # MARL String: Long, Short, Hold
                
                signal_int = 2 # Hold
                if final_signal_str == "Long": signal_int = 0
                elif final_signal_str == "Short": signal_int = 1
                
                # Calculate Return
                curr_price = original_prices.loc[target_date]
                prev_price = original_prices.iloc[original_prices.index.get_loc(target_date) - 1]
                
                daily_pct_change = (curr_price - prev_price) / prev_price
                
                strategy_return = 0.0
                if signal_int == 0: # Long
                    strategy_return = daily_pct_change
                elif signal_int == 1: # Short
                    strategy_return = -daily_pct_change
                
                results.append({
                    "date": date_str,
                    "signal": signal_int,
                    "daily_return": float(daily_pct_change),
                    "strategy_return": float(strategy_return)
                })
                
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
        original_cwd = os.getcwd()
        os.chdir(MARL_DIR)
        
        try:
            self.load_model()
            if not self.model_loaded:
                return None
                
            from inference import predict_today as marl_predict
            # marl_predict prints output, we might want to capture it or reimplement logic.
            # Reimplementing logic is safer to return structured data.
            
            from config import WINDOW_SIZE, DEVICE
            from environment import MARLStockEnv
            from utils import convert_joint_action_to_signal
            
            # Use existing processor which should have latest data if we just loaded
            # Or re-process if needed. 
            # For efficiency, let's assume processor has data. 
            # But if day changed, we might need new data.
            # Let's re-run process() to be safe.
            (features_df, prices_df, _, a0, a1, a2) = self.processor.process()
            norm_features, _ = self.processor.normalize_data(features_df, features_df)
            
            dummy_env = MARLStockEnv(norm_features, prices_df, a0, a1, a2)
            
            # Last available window
            if len(norm_features) < WINDOW_SIZE:
                print(f"Not enough data for MARL prediction. Need {WINDOW_SIZE}, got {len(norm_features)}")
                return None
                
            last_idx = len(norm_features) - WINDOW_SIZE
            dummy_env.current_step = last_idx
            obs_dict, _ = dummy_env._get_obs_and_state()
            
            with torch.no_grad():
                actions = self.learner.select_actions(obs_dict, epsilon=0.0)
                
            joint_action = [actions[f'agent_{i}'] for i in range(3)]
            final_signal_str = convert_joint_action_to_signal(joint_action, {0: "Long", 1: "Hold", 2: "Short"})
            
            signal_int = 2
            if final_signal_str == "Long": signal_int = 0
            elif final_signal_str == "Short": signal_int = 1
            
            return {
                "date": norm_features.index[-1].strftime("%Y-%m-%d"),
                "action": signal_int,
                "action_str": final_signal_str,
                "joint_action": joint_action
            }

        except Exception as e:
            print(f"Error in MARL predict_today: {e}")
            return None
        finally:
            os.chdir(original_cwd)

# Singleton instances
a2c_wrapper = A2CWrapper()
marl_wrapper = MarlWrapper()
