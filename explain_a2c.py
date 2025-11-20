# explain_a2c.py

import os
import yaml
import numpy as np
import shap
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import joblib
import pandas as pd

from data_utils import (
    download_data,
    add_indicators,
    FEATURES,
    build_state,
)
from ac_model import A2CAgent


# --- feature 이름 생성 (window_size 반영) ---
def get_feature_names_with_position(window_size: int):
    names = []
    for t in range(window_size):
        for f in FEATURES:
            names.append(f"{f}_t-{window_size-1-t}")
    names.append("Position")
    return names


# --- 지표별 한글 설명 매핑 ---
INDICATOR_DESC_KO = {
    "EMA12": "단기 추세(12일 지수이동평균)",
    "EMA26": "중기 추세(26일 지수이동평균)",
    "MACD": "추세 모멘텀(MACD 지표)",
    "Volume": "거래량 변화",
    "KOSPI": "시장 전체(KOSPI 지수) 흐름",
    "SMA20": "중기 이동평균선(20일 단순이동평균)",
    "RSI": "과매수·과매도 수준(RSI)",
    "STOCH_%K": "단기 모멘텀(Stochastic %K)",
    "VIX": "시장 변동성(VIX 지수)",
    "BB_%B": "볼린저 밴드 내 위치(%B)",
    "BB_BW": "볼린저 밴드 폭(변동성)",
    "ATR": "평균 진폭(ATR, 변동성)",
    "Position": "현재 포지션(보유 여부)",
}


def calendar_split(df: pd.DataFrame, train_years: int, backtest_days: int):
    """
    train.py와 동일한 방식으로 10년 학습 + 1년 백테스트 구간을 분할.
    (여기서는 test_df만 실제로 사용)
    """
    last_date = df.index[-1]
    backtest_end = last_date
    backtest_start = backtest_end - pd.Timedelta(days=backtest_days)
    train_start = backtest_end - pd.DateOffset(years=train_years)

    train_df = df.loc[(df.index >= train_start) & (df.index < backtest_start)].copy()
    test_df = df.loc[(df.index >= backtest_start) & (df.index <= backtest_end)].copy()

    print("\n[데이터 분할(캘린더 기준, explain용)]")
    print(
        f"  - Train 기간: {train_df.index[0].date()} ~ {train_df.index[-1].date()} "
        f"({len(train_df)}일)"
    )
    print(
        f"  - Test  기간: {test_df.index[0].date()} ~ {test_df.index[-1].date()} "
        f"({len(test_df)}일)"
    )
    return train_df, test_df


# --- 추천 + SHAP 계산 ---
def get_recommendation_and_explanation(
    state: np.ndarray,
    agent: A2CAgent,
    explainer: shap.Explainer,
    feature_names: list,
    save_path: str,
    top_k: int = 3,
):
    # 1. 정책 확률 계산
    with torch.no_grad():
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        policy_logits, _ = agent.ac_net(state_tensor)
        policy_probs = F.softmax(policy_logits, dim=-1).detach().cpu().numpy()[0]

    action_idx = int(np.argmax(policy_probs))
    action_map = {0: "매수", 1: "매도", 2: "보유"}
    action_label = action_map[action_idx]
    recommendation = action_label  # 자연어용

    # 2. SHAP 값 계산
    print("SHAP 값 계산 중 (A2C Actor 기준)...")
    shap_values_tensor = explainer.shap_values(state.reshape(1, -1))
    shap_for_action = shap_values_tensor[0, :, action_idx]

    # 3. feature별 SHAP dict
    feature_shap = dict(zip(feature_names, shap_for_action))

    # 3-1. base feature 단위로 묶기(EMA12, VIX 등)
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

    # 3-2. 중요도 순으로 정렬
    sorted_base = sorted(
        aggregate.items(), key=lambda x: x[1]["sum_abs"], reverse=True
    )

    top_features = []
    for base, info in sorted_base[:top_k]:
        shap_val = info["best_val"]
        direction = "지지" if shap_val > 0 else "방해"
        desc = INDICATOR_DESC_KO.get(base, base)
        top_features.append(
            {
                "base": base,
                "shap": shap_val,
                "direction": direction,
                "description": desc,
            }
        )

    # 4. 전체 feature 단위 barh 그래프 저장
    plt.figure(figsize=(10, 6))
    order = np.argsort(shap_for_action)
    plt.barh([feature_names[i] for i in order], shap_for_action[order])
    plt.title(f"'{recommendation}' 추천에 대한 SHAP 기여도 (A2C Actor)")
    plt.xlabel("SHAP Value (정책 확률 기여도: +는 지지, -는 방해)")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    plt.close()

    return recommendation, policy_probs, feature_shap, top_features


def run_prediction():
    print("A2C 예측 및 SHAP 분석을 시작합니다...")

    # 1. 설정 로드
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    report_dir = cfg["report_dir"]
    scaler_path = os.path.join(report_dir, "scaler.joblib")
    model_path = cfg["model_path"]
    window_size = cfg["window_size"]
    model_cfg = cfg["model_cfg"]
    train_years = cfg.get("train_years", 10)
    backtest_days = cfg.get("backtest_days", 365)

    # 2. 데이터 로드
    raw = download_data(
        cfg["ticker"],
        cfg["kospi_ticker"],
        cfg["vix_ticker"],
        cfg["start_date"],
        cfg["end_date"],
    )
    df = add_indicators(raw)

    # train/test 분할 (train은 배경 데이터용, test는 대상 window 선택용)
    train_df, test_df = calendar_split(df, train_years, backtest_days)

    # 3. 스케일러 & 모델 로드
    try:
        scaler = joblib.load(scaler_path)
        print(f"[OK] Scaler 로드: {scaler_path}")
    except FileNotFoundError:
        print(f"[에러] {scaler_path} 를 찾을 수 없음. 먼저 train.py를 실행해서 학습하세요.")
        return

    train_df[FEATURES] = scaler.transform(train_df[FEATURES])
    test_df[FEATURES] = scaler.transform(test_df[FEATURES])

    print(f"[OK] A2C 모델 로드: {model_path}")
    dummy_state_dim = len(FEATURES) * window_size + 1

    agent = A2CAgent(
        state_dim=dummy_state_dim,
        action_dim=3,
        hidden_dims=model_cfg.get("hidden_dims", [128, 128]),
        gamma=cfg["gamma"],
        lr=cfg["lr"],
        value_loss_coeff=cfg["value_loss_coeff"],
        entropy_coeff=cfg["entropy_coeff"],
        seed=cfg["seed"],
        device=cfg.get("device", "cpu"),
    )
    agent.load(model_path)

    # 4. SHAP용 배경 데이터
    print("SHAP 배경 데이터(훈련 샘플 일부) 생성 중...")
    bg_states = []
    bg_len = min(200 + window_size, len(train_df) - 1)
    for i in range(window_size - 1, bg_len):
        current_window = train_df.iloc[i - (window_size - 1) : i + 1]
        s = build_state(current_window, position_flag=0)
        bg_states.append(s)
    bg_states = np.array(bg_states, dtype=np.float32)
    bg_summary = shap.sample(bg_states, 100)

    def model_f(x):
        x_t = torch.tensor(x, dtype=torch.float32, device=cfg.get("device", "cpu"))
        policy_logits, _ = agent.ac_net(x_t)
        policy_probs = F.softmax(policy_logits, dim=-1)
        return policy_probs.detach().cpu().numpy()

    print("SHAP KernelExplainer 생성 중...")
    explainer = shap.KernelExplainer(model_f, bg_summary)
    feature_names = get_feature_names_with_position(window_size)
    print("[OK] SHAP 준비 완료")

    # 5. 예측 대상: 테스트 마지막 날 기준 (window_size만큼 과거 포함)
    target_idx = len(test_df) - 2  # 마지막 바로 전날을 기준으로
    target_window = test_df.iloc[target_idx - (window_size - 1) : target_idx + 1]
    target_date = test_df.index[target_idx]

    current_position = 0  # 웹 서비스 기준: 기본값은 미보유
    state_to_explain = build_state(target_window, current_position)

    # 6. 추천 + 설명
    save_path = os.path.join(report_dir, "prediction_explanation_a2c.png")
    print(f"\n기준 날짜: {target_date.strftime('%Y-%m-%d')}")
    print(f"SHAP 그래프 저장 위치: {save_path}")

    rec, probs, shap_all, top_feats = get_recommendation_and_explanation(
        state_to_explain, agent, explainer, feature_names, save_path
    )

    # critic value (DQN의 Q-value 대신, 상태 가치 V(s) 사용)
    with torch.no_grad():
        v_pred = agent.get_value(state_to_explain).item()

    # 7. 팀원 스타일의 출력
    print("\n=============================================")
    print(f"      [ 📱 리브리 AI 분석 결과 ({cfg['ticker']}) ]")
    print("=============================================\n")

    print("--- 1. AI 최종 신호 ---")
    print(f"    {rec}")
    print(f"    (예상 팀 Score(V값): {v_pred:.4f})")

    print("\n--- 2. AI 설명 ---")
    print(f"AI가 '{rec}'을(를) 결정한 주된 이유는 다음과 같습니다.\n")

    # TOP3 설명 문장
    for i, feat in enumerate(top_feats, start=1):
        base = feat["base"]
        desc = feat["description"]
        if i == 1:
            tail = "가장 중요하게 고려했습니다."
        elif i == 2:
            tail = "2순위로 결정에 영향을 미쳤습니다."
        else:
            tail = "마지막으로 참고했습니다."
        print(f"  {i}. '{base}' 지표({desc})의 최근 움직임을 {tail}")

    # (선택) 정책 확률도 같이 보고 싶으면 아래 유지
    print("\n--- 정책 확률 (Policy Probabilities) ---")
    action_labels = ["매수", "매도", "보유"]
    for i, p in enumerate(probs):
        print(f"  {action_labels[i]:<4}: {p:.4f}")


if __name__ == "__main__":
    run_prediction()