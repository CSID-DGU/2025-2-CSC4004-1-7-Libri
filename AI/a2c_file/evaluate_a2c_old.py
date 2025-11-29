# evaluate_a2c.py

import os
import yaml
import joblib
import numpy as np
import pandas as pd
import shap
import torch
import torch.nn.functional as F

from sklearn.preprocessing import StandardScaler

from data_utils import (
    download_data,
    add_indicators,
    FEATURES,
    build_state,
)
from trading_env import TradingEnv
from ac_model import A2CAgent


def pretty_feature_name(feat_name: str) -> str:
    """SHAP feature 이름을 사람이 보기 좋게 변환."""
    base = feat_name.split("_t-")[0]
    mapping = {
        "EMA12": "단기 추세(EMA12)",
        "EMA26": "중기 추세(EMA26)",
        "MACD": "MACD(추세 모멘텀)",
        "Volume": "거래량",
        "KOSPI": "코스피 지수",
        "SMA20": "20일 이동평균선",
        "RSI": "RSI(과매수/과매도)",
        "STOCH_%K": "스토캐스틱 %K",
        "VIX": "변동성 지수(VIX)",
        "BB_%B": "볼린저 %b",
        "BB_BW": "볼린저 밴드 폭",
        "ATR": "ATR(변동성)",
        "Position": "현재 포지션",
    }
    return mapping.get(base, base)


def get_feature_names_with_position(window_size: int):
    names = []
    for t in range(window_size):
        for f in FEATURES:
            names.append(f"{f}_t-{window_size-1-t}")
    names.append("Position")
    return names


def compute_backtest_metrics(daily_returns: np.ndarray):
    """일별 수익률 배열로부터 성능 지표 계산."""
    n = len(daily_returns)
    if n == 0:
        return None

    # 누적 수익 (1 -> equity 마지막 - 1)
    equity = np.cumprod(1.0 + daily_returns)
    cum_return = equity[-1] - 1.0

    mean_ret = daily_returns.mean()
    vol = daily_returns.std(ddof=1) if n > 1 else 0.0
    sharpe = (mean_ret / vol * np.sqrt(252)) if vol > 0 else np.nan

    win_mask = daily_returns > 0
    wins = int(win_mask.sum())
    win_rate = wins / n if n > 0 else 0.0

    # 최대 낙폭(MDD)
    running_max = np.maximum.accumulate(equity)
    drawdown = equity / running_max - 1.0
    mdd = drawdown.min() if len(drawdown) > 0 else 0.0

    return {
        "days": n,
        "cum_return": cum_return,
        "mean_ret": mean_ret,
        "vol": vol,
        "sharpe": sharpe,
        "wins": wins,
        "win_rate": win_rate,
        "mdd": mdd,
    }


def run_evaluation_and_explain():
    print("A2C 백테스트 및 최종일 설명을 시작합니다...")

    # 1. 설정 로드
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    report_dir = cfg["report_dir"]
    scaler_path = os.path.join(report_dir, "scaler.joblib")
    model_path = cfg["model_path"]
    window_size = cfg["window_size"]
    model_cfg = cfg["model_cfg"]

    # --- (선택) 학습 곡선 분석: train_history npz 읽기 ---
    hist_path = os.path.join(report_dir, "a2c_train_history.npz")
    print("\n--- 학습 곡선 분석 ---")
    if os.path.exists(hist_path):
        hist = np.load(hist_path)
        ep_rewards = hist["episode_rewards"]
        val_rewards = hist["val_rewards"] if "val_rewards" in hist.files else np.array([])

        first_100_mean = ep_rewards[:100].mean() if len(ep_rewards) >= 100 else ep_rewards.mean()
        last_100_mean = ep_rewards[-100:].mean() if len(ep_rewards) >= 100 else ep_rewards.mean()
        best_ep_reward = ep_rewards.max()
        best_val = val_rewards.max() if len(val_rewards) > 0 else np.nan

        print(f"    - 초기 100 에피소드 평균: {first_100_mean:.2f}")
        print(f"    - 최종 100 에피소드 평균: {last_100_mean:.2f}")
        print(f"    - 최고 에피소드 보상: {best_ep_reward:.2f}")
        print(f"    - 최고 검증 보상: {best_val:.2f}")
    else:
        print("    (경고) a2c_train_history.npz 파일을 찾지 못했습니다.")
        print("    -> 새 train.py로 다시 학습하면 자동으로 생성됩니다.")

    # 2. 데이터 로드 (config 범위 전체)
    raw = download_data(
        cfg["ticker"],
        cfg["kospi_ticker"],
        cfg["vix_ticker"],
        cfg["start_date"],
        cfg["end_date"],
    )
    df = add_indicators(raw)

    # 마지막 365 거래일을 백테스트로 사용
    backtest_days = 365
    if len(df) <= backtest_days + window_size:
        raise ValueError("데이터가 너무 짧아서 365일 백테스트를 만들 수 없습니다. 기간을 늘려주세요.")

    test_df = df.iloc[-backtest_days:].copy()
    train_df = df.iloc[:-backtest_days].copy()

    backtest_start = test_df.index[0].date()
    backtest_end = test_df.index[-1].date()

    # 3. 스케일러 및 모델 로드
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"{scaler_path} 를 찾을 수 없습니다. train.py를 먼저 실행하세요.")

    scaler: StandardScaler = joblib.load(scaler_path)

    train_df[FEATURES] = scaler.transform(train_df[FEATURES])
    test_df[FEATURES] = scaler.transform(test_df[FEATURES])

    print(f"\nScaler 로드 완료: {scaler_path}")
    print(f"학습된 A2C 모델 로드 중: {model_path}")

    state_dim = len(FEATURES) * window_size + 1
    agent = A2CAgent(
        state_dim=state_dim,
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

    # 4. 백테스트 환경 구성
    env_cfg = {
        "data": test_df,
        "window_size": window_size,
        "trade_penalty": cfg["trade_penalty"],
        "use_daily_unrealized": cfg["use_daily_unrealized"],
        "reward_cfg": cfg.get("reward", {}),
    }
    env = TradingEnv(**env_cfg)

    # 5. 백테스트 실행 (greedy 정책)
    s = env.reset()
    done = False
    rets = []
    actions = []

    print("\n--- [1] 전체 테스트 기간 백테스트 ---")
    while not done:
        a, _ = agent.act(s, deterministic=True)
        ns, r, done, info = env.step(a)
        rets.append(r)      # 여기서는 r을 '일별 수익률'로 간주
        actions.append(a)
        s = ns if not done else s

    rets = np.array(rets, dtype=float)
    actions = np.array(actions, dtype=int)

    # 6. 성능 지표 계산
    metrics = compute_backtest_metrics(rets)

    print("\n--- [2] 백테스트 성능 지표 ---")
    if metrics is None:
        print("    (오류) 수익률 데이터가 없습니다.")
        return

    print(f"    - 백테스트 기간: {metrics['days']} 일 ({backtest_start} ~ {backtest_end})")
    print(f"    - 누적 수익: {metrics['cum_return']:.2f}")
    print(f"    - 일 평균 수익: {metrics['mean_ret']:.4f}")
    print(f"    - 일 수익 변동성: {metrics['vol']:.4f}")
    print(f"    - 샤프 비율 (연환산): {metrics['sharpe']:.3f}")
    print(f"    - 승률: {metrics['win_rate']*100:.2f}% ({metrics['wins']}/{metrics['days']} 일)")
    print(f"    - 최대 낙폭(MDD): {metrics['mdd']:.2f}")

    # 행동 분포 (단일 에이전트용)
    buy_pct = (actions == 0).mean() * 100.0  # Long
    sell_pct = (actions == 1).mean() * 100.0 # Short
    hold_pct = (actions == 2).mean() * 100.0 # Hold

    print("\n    - 행동 분포:")
    print(f"      Agent: Buy={buy_pct:.1f}% Hold={hold_pct:.1f}% Sell={sell_pct:.1f}%")

    # 7. 최종일 SHAP 분석
    #    - train_df에서 background sample 생성
    print("\n--- [3] 최종일 예측 상세 분석 ---")

    bg_states = []
    bg_len = min(200 + window_size, len(train_df) - 1)
    for i in range(window_size - 1, bg_len):
        window = train_df.iloc[i - (window_size - 1) : i + 1]
        state_bg = build_state(window, position_flag=0)
        bg_states.append(state_bg)
    bg_states = np.array(bg_states, dtype=np.float32)
    bg_summary = shap.sample(bg_states, 100)

    device = cfg.get("device", "cpu")

    def model_f(x):
        x_t = torch.tensor(x, dtype=torch.float32, device=device)
        logits, _ = agent.ac_net(x_t)
        probs = F.softmax(logits, dim=-1)
        return probs.detach().cpu().numpy()

    explainer = shap.KernelExplainer(model_f, bg_summary)

    # 최종일 기준 window 상태 생성
    target_window = test_df.iloc[-window_size:]
    target_date = target_window.index[-1].date()
    state_last = build_state(target_window, position_flag=0)

    shap_values = explainer.shap_values(state_last.reshape(1, -1))
    # KernelExplainer 반환이 (N, state_dim, action_dim) 형태라고 가정
    # shap_values[0] -> (state_dim, action_dim)
    shap_tensor = shap_values[0]
    # 최종 행동: greedy 정책
    with torch.no_grad():
        st = torch.tensor(state_last, dtype=torch.float32).unsqueeze(0)
        logits, _ = agent.ac_net(st)
        probs = F.softmax(logits, dim=-1).detach().cpu().numpy()[0]

    action_idx = int(np.argmax(probs))
    action_map = {0: "매수", 1: "매도", 2: "보유"}
    action_name = action_map[action_idx]

    shap_for_action = shap_tensor[:, action_idx]
    feature_names = get_feature_names_with_position(window_size)
    explanation = dict(zip(feature_names, shap_for_action))

    # 중요도 상위 3개 (절댓값 기준)
    top3 = sorted(explanation.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]

    print("\n=============================================")
    print("      [ 📱 리브리 AI 분석 결과 (삼성전자) ]")
    print("=============================================\n")

    print("--- 1. AI 최종 신호 ---")
    print(f"    {action_name}")
    print(f"    (정책 확률: Long={probs[0]:.4f}, Short={probs[1]:.4f}, Hold={probs[2]:.4f})")

    print("\n--- 2. AI 설명 ---")
    print(f"AI가 '{action_name}'을(를) 결정한 주된 이유는 다음과 같습니다.\n")
    for rank, (fname, val) in enumerate(top3, start=1):
        pretty = pretty_feature_name(fname)
        direction = "긍정적(+)" if val > 0 else "부정적(-)"
        print(f"  {rank}. '{pretty}' 지표의 영향이 {val:+.4f} ({direction}) 로 크게 작용했습니다.")

    print(f"\n(기준 날짜: {target_date})")


if __name__ == "__main__":
    run_evaluation_and_explain()