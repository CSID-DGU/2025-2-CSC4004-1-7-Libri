# api_server.py

import os
import yaml
import numpy as np
import shap
import torch
import torch.nn.functional as F
import joblib

from fastapi import FastAPI
from pydantic import BaseModel

from data_utils import (
    download_data,
    add_indicators,
    train_test_split_by_ratio,
    FEATURES,
    build_state,
)
from ac_model import A2CAgent
from explain_a2c import (
    get_feature_names_with_position,
    INDICATOR_DESC_KO,
)

# ===================== 전역 초기화 =====================

with open("config.yaml", "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

REPORT_DIR = CFG["report_dir"]
SCALER_PATH = os.path.join(REPORT_DIR, "scaler.joblib")
MODEL_PATH = CFG["model_path"]
WINDOW_SIZE = CFG["window_size"]
MODEL_CFG = CFG["model_cfg"]

# 1) 데이터 로드 + 전처리
RAW = download_data(
    CFG["ticker"],
    CFG["kospi_ticker"],
    CFG["vix_ticker"],
    CFG["start_date"],
    CFG["end_date"],
)
DF = add_indicators(RAW)
TRAIN_DF, TEST_DF = train_test_split_by_ratio(DF, CFG["train_ratio"])

# 2) 스케일러 & 모델
SCALER = joblib.load(SCALER_PATH)
TRAIN_DF[FEATURES] = SCALER.transform(TRAIN_DF[FEATURES])
TEST_DF[FEATURES] = SCALER.transform(TEST_DF[FEATURES])

dummy_state_dim = len(FEATURES) * WINDOW_SIZE + 1
AGENT = A2CAgent(
    state_dim=dummy_state_dim,
    action_dim=3,
    hidden_dims=MODEL_CFG.get("hidden_dims", [128, 128]),
    gamma=CFG["gamma"],
    lr=CFG["lr"],
    value_loss_coeff=CFG["value_loss_coeff"],
    entropy_coeff=CFG["entropy_coeff"],
    seed=CFG["seed"],
    device=CFG.get("device", "cpu"),
)
AGENT.load(MODEL_PATH)

# 3) SHAP 준비 (배경 데이터)
bg_states = []
bg_len = min(200 + WINDOW_SIZE, len(TRAIN_DF) - 1)
for i in range(WINDOW_SIZE - 1, bg_len):
    win = TRAIN_DF.iloc[i - (WINDOW_SIZE - 1) : i + 1]
    s = build_state(win, position_flag=0)
    bg_states.append(s)
bg_states = np.array(bg_states, dtype=np.float32)
bg_summary = shap.sample(bg_states, 100)

def model_f(x):
    x_t = torch.tensor(x, dtype=torch.float32, device=CFG.get("device", "cpu"))
    policy_logits, _ = AGENT.ac_net(x_t)
    policy_probs = F.softmax(policy_logits, dim=-1)
    return policy_probs.detach().cpu().numpy()

EXPLAINER = shap.KernelExplainer(model_f, bg_summary)
FEATURE_NAMES = get_feature_names_with_position(WINDOW_SIZE)

ACTION_MAP = {0: "Long(매수)", 1: "Short(매도)", 2: "Hold(관망)"}


# ===================== FastAPI 스키마 =====================

class TopReason(BaseModel):
    indicator: str
    direction: str
    description: str
    shap: float

class RecommendationResponse(BaseModel):
    date: str
    action: str
    probs: dict
    top_reasons: list[TopReason]


# ===================== FastAPI 앱 =====================

app = FastAPI(title="A2C Samsung XAI API")

@app.get("/recommendation", response_model=RecommendationResponse)
def get_recommendation(position: int = 0):
    """
    오늘(or 테스트 마지막 날) 기준 추천과 TOP3 근거를 반환.
    position: 0(미보유), 1(보유) 같은 식으로 나중에 확장 가능.
    """

    # 1. 현재 기준 시점 선택 (여기서는 테스트 마지막 날 기준)
    target_idx = len(TEST_DF) - 2
    target_window = TEST_DF.iloc[target_idx - (WINDOW_SIZE - 1) : target_idx + 1]
    target_date = TEST_DF.index[target_idx]

    state = build_state(target_window, position_flag=position)

    # 2. 정책 확률 & SHAP
    with torch.no_grad():
        s_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        logits, _ = AGENT.ac_net(s_t)
        probs_t = F.softmax(logits, dim=-1).detach().cpu().numpy()[0]

    action_idx = int(np.argmax(probs_t))
    shap_values_tensor = EXPLAINER.shap_values(state.reshape(1, -1))
    shap_for_action = shap_values_tensor[0, :, action_idx]

    # feature별 shap dict
    feature_shap = dict(zip(FEATURE_NAMES, shap_for_action))

    # base feature 단위로 묶기
    aggregate = {}
    for name, val in feature_shap.items():
        if "_t-" in name:
            base = name.split("_t-")[0]
        else:
            base = name
        if base not in aggregate:
            aggregate[base] = {"sum_abs": 0.0, "best_val": val}
        aggregate[base]["sum_abs"] += abs(val)
        if abs(val) > abs(aggregate[base]["best_val"]):
            aggregate[base]["best_val"] = val

    sorted_base = sorted(
        aggregate.items(), key=lambda x: x[1]["sum_abs"], reverse=True
    )

    top_reasons = []
    for base, info in sorted_base[:3]:
        shap_val = float(info["best_val"])
        direction = "지지" if shap_val > 0 else "방해"
        desc = INDICATOR_DESC_KO.get(base, base)
        top_reasons.append(
            TopReason(
                indicator=base,
                direction=direction,
                description=desc,
                shap=shap_val,
            )
        )

    probs_dict = {
        "long": float(probs_t[0]),
        "short": float(probs_t[1]),
        "hold": float(probs_t[2]),
    }

    return RecommendationResponse(
        date=target_date.strftime("%Y-%m-%d"),
        action=ACTION_MAP[action_idx],
        probs=probs_dict,
        top_reasons=top_reasons,
    )