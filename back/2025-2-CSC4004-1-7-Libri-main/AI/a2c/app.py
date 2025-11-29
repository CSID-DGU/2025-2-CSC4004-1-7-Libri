# app.py (A2C 수정본)
import os
import yaml
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import torch
import torch.nn.functional as F
import shap
from flask import Flask, jsonify, request

from data_utils import (
    download_data, add_indicators, train_test_split_by_ratio, 
    build_state, get_feature_names_with_position, FEATURES
)
# (수정) A2CAgent, ActorCriticNet 임포트
from ac_model import A2CAgent, ActorCriticNet 
from sklearn.preprocessing import StandardScaler

# --- 1. 설명 사전 (기존과 동일) ---
FEATURE_DESCRIPTIONS = {
    "EMA12": "최근 12일간의 주가 흐름을 반영하는 '단기 추세' 지표입니다.",
    # ... (중략) ...
    "VIX": "시장의 '변동성(공포 지수)'을 나타내며, 이 값이 높으면 시장 위험이 크다는 의미입니다.",
    "Position": "현재 AI가 주식을 '보유'하고 있는지(1) '미보유' 중인지(0) 여부도 결정에 영향을 줍니다."
}

# --- 2. Flask 앱 초기화 ---
app = Flask(__name__)
cfg = None
scaler = None
agent = None
explainer = None
feature_names = None
action_map = {0: "Long(매수)", 1: "Short(매도)", 2: "Hold(관망)"}

# --- 3. (수정) A2C 모델 및 SHAP Explainer 로드 ---
def load_models_and_explainer():
    global cfg, scaler, agent, explainer, feature_names
    
    print("--- 1. 설정 및 스케일러 로드 중... ---")
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    window_size = cfg["window_size"]
    model_cfg = cfg["model_cfg"]
    
    scaler_path = os.path.join(cfg["report_dir"], "scaler.joblib")
    scaler = joblib.load(scaler_path)

    print("--- 2. A2C 모델 로드 중... ---")
    dummy_state_dim = len(FEATURES) * window_size + 1
    
    agent = A2CAgent(
        state_dim=dummy_state_dim,
        action_dim=3,
        hidden_dims=model_cfg.get("hidden_dims", [128, 128]),
        device=cfg.get("device", "cpu")
    )
    agent.load(cfg["model_path"])
    feature_names = get_feature_names_with_position(window_size)

    print("--- 3. SHAP Explainer 준비 중 (A2C Actor 대상) ---")
    # ... (배경 데이터 준비는 기존과 동일) ...
    raw = download_data(cfg["ticker"], cfg["kospi_ticker"], cfg["vix_ticker"],
                        cfg["start_date"], cfg["end_date"])
    df  = add_indicators(raw)
    train_df, _ = train_test_split_by_ratio(df, cfg["train_ratio"])
    train_df[FEATURES] = scaler.transform(train_df[FEATURES])

    bg_states = []
    bg_len = min(200 + window_size, len(train_df) - 1)
    for i in range(window_size - 1, bg_len):
        current_position_flag = 0
        current_window = train_df.iloc[i - (window_size - 1) : i + 1]
        s = build_state(current_window, current_position_flag)
        bg_states.append(s)
    bg_states = np.array(bg_states, dtype=np.float32)
    bg_summary = shap.sample(bg_states, 100) # 100개로 요약

    # --- (핵심 수정) SHAP이 "정책 확률"을 설명하도록 model_f 변경 ---
    def model_f(x):
        """
        SHAP을 위한 모델 함수.
        입력(state)을 받아 액터의 출력(정책 확률)을 반환.
        """
        x_t = torch.tensor(x, dtype=torch.float32, device=cfg.get("device", "cpu"))
        # ac_net(x) -> (policy_logits, value)
        policy_logits, _ = agent.ac_net(x_t)
        policy_probs = F.softmax(policy_logits, dim=-1)
        return policy_probs.detach().cpu().numpy()
    # -----------------------------------------------------------
    
    explainer = shap.KernelExplainer(model_f, bg_summary)
    
    print("--- 4. 예측 서비스 준비 완료 ---")


# --- 4. API 엔드포인트 (A2C 수정) ---
@app.route('/recommend', methods=['GET'])
def get_recommendation():
    try:
        current_position = int(request.args.get('position', 0))
        if current_position not in [0, 1]: current_position = 0
        window_size = cfg["window_size"]
            
        print("\n[API] 최신 데이터 수집 중...")
        end_str = datetime.today().strftime("%Y-%m-%d")
        start_str = (datetime.today() - timedelta(days=100 + window_size)).strftime("%Y-%m-%d")
        raw_latest = download_data(cfg["ticker"], cfg["kospi_ticker"], cfg["vix_ticker"], start_str, end_str)
        
        df_latest = add_indicators(raw_latest)
        if len(df_latest) < window_size:
            return jsonify({"status": "error", "message": "데이터가 윈도우 크기보다 부족합니다."}), 500
            
        latest_window_df = df_latest.iloc[-window_size:]
        latest_window_df_scaled = latest_window_df.copy()
        latest_window_df_scaled[FEATURES] = scaler.transform(latest_window_df[FEATURES])
        
        state = build_state(latest_window_df_scaled, current_position)

        # 4. (수정) 행동 추천 (A2C deterministic act)
        print(f"[API] A2C 행동 추천 생성 중 (Position={current_position})...")
        # (수정) A2C 모델은 (logits, value)를 반환함
        state_t = torch.tensor(state, dtype=torch.float32, device=cfg.get("device", "cpu"))
        policy_logits, _ = agent.ac_net(state_t)
        policy_probs = F.softmax(policy_logits, dim=-1).detach().cpu().numpy()[0]
        
        action_idx = int(np.argmax(policy_probs))
        recommendation = action_map[action_idx]

        # 5. SHAP 분석 (정책 확률 대상)
        print("[API] SHAP 분석 수행 중 (Actor Policy 대상)...")
        # explainer.shap_values는 (N, state_dim, action_dim) 텐서를 반환
        shap_values_tensor = explainer.shap_values(state.reshape(1, -1))
        # (수정) 선택된 행동(action_idx)에 대한 SHAP 값 추출
        shap_for_action = shap_values_tensor[0, :, action_idx]
        
        explanation = dict(zip(feature_names, shap_for_action))
        sorted_explanation = sorted(explanation.items(), key=lambda item: item[1], reverse=True)
        
        top_3_reasons = []
        for feature, value in sorted_explanation[:3]:
            base_feature_name = feature.split('_t-')[0] 
            top_3_reasons.append({
                "feature": feature,
                "impact_value": f"{value:+.4f}",
                "description": FEATURE_DESCRIPTIONS.get(base_feature_name, "설명 없음")
            })

        # 6. JSON 응답 반환 (수정: q_values -> policy_probabilities)
        return jsonify({
            "status": "success",
            "predict_for_date": datetime.today().strftime("%Y-%m-%d"),
            "based_on_data_date": raw_latest.index[-1].strftime("%Y-%m-%d"),
            "current_position_input": "Holding" if current_position == 1 else "Not Holding",
            "recommendation": recommendation,
            # (수정) Q-value 대신 정책 확률 반환
            "policy_probabilities": {
                action_map[0]: f"{policy_probs[0]:.4f}",
                action_map[1]: f"{policy_probs[1]:.4f}",
                action_map[2]: f"{policy_probs[2]:.4f}",
            },
            "top_3_reasons": top_3_reasons
        })

    except Exception as e:
        print(f"[API] 오류 발생: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 5. 웹 서버 실행 (기존과 동일) ---
if __name__ == '__main__':
    try: import flask
    except ImportError:
        print("pip install -r requirements.txt 를 실행해주세요.")
        exit()

    load_models_and_explainer()
    print("\n--- 5. A2C 웹 서버를 시작합니다 ---")
    app.run(debug=False, host='0.0.0.0', port=5000)