# A2C 백테스트 + 승률/수익률 시각화 셀
# (오늘 기준 최근 10년 학습 + 최근 1년 테스트 / 교수님 피드백 반영 버전)

import os
import yaml
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # 날짜 축용

from ac_model import A2CAgent
from trading_env import TradingEnv
from data_utils import FEATURES, download_data, add_indicators

# -------------------------------------------
# 1. 백테스트 지표 계산 함수 (승률 정의 포함)
# -------------------------------------------
def compute_backtest_metrics(daily_returns: np.ndarray, risk_free_rate: float = 0.0) -> dict:
    """
    daily_returns: 포트폴리오 일별 수익률 r_t (예: 0.01 = 1%)

    승률 정의:
      - win_rate = (r_t > 0 인 날 수) / 전체 거래일 수
    """
    if len(daily_returns) == 0:
        return {
            "cum_return": 0.0,
            "mean_ret": 0.0,
            "vol": 0.0,
            "sharpe": 0.0,
            "win_rate": 0.0,
            "wins": 0,
            "days": 0,
            "mdd": 0.0,
        }

    equity = (1.0 + daily_returns).cumprod()
    cum_return = float(equity[-1] - 1.0)

    mean_ret = float(np.mean(daily_returns))
    vol = float(np.std(daily_returns))

    if vol > 0:
        sharpe = float((mean_ret - risk_free_rate) / vol * np.sqrt(252))
    else:
        sharpe = 0.0

    wins_mask = daily_returns > 0
    wins = int(wins_mask.sum())
    days = int(len(daily_returns))
    win_rate = wins / days if days > 0 else 0.0

    high_water_mark = np.maximum.accumulate(equity)
    drawdown = equity / high_water_mark - 1.0
    mdd = float(drawdown.min())

    return {
        "cum_return": cum_return,
        "mean_ret": mean_ret,
        "vol": vol,
        "sharpe": sharpe,
        "win_rate": win_rate,
        "wins": wins,
        "days": days,
        "mdd": mdd,
    }

# -------------------------------------------
# 2. 오늘 기준 최근 10년 / 최근 1년 분할
# -------------------------------------------
def split_last_10y_train_1y_test(df: pd.DataFrame):
    df = df.sort_index()

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]

    today = df.index.max()
    test_start = today - pd.DateOffset(years=1)
    train_start = today - pd.DateOffset(years=10)

    train_df = df[(df.index >= train_start) & (df.index < test_start)]
    test_df = df[(df.index >= test_start) & (df.index <= today)]

    return train_df, test_df, today

# -------------------------------------------
# 3. 설정(config) 로드
# -------------------------------------------
with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

ticker = cfg.get("ticker", "005930.KS")
kospi_ticker = cfg.get("kospi_ticker", "^KS11")
vix_ticker = cfg.get("vix_ticker", "^VIX")

start_date = cfg.get("start_date", "2010-01-01")
end_date = cfg.get("end_date", None)

window_size = int(cfg.get("window_size", 30))

trade_penalty = float(cfg.get("trade_penalty", 0.001))
use_daily_unrealized = bool(cfg.get("use_daily_unrealized", True))
reward_cfg = cfg.get("reward", {})

model_path = cfg.get("model_path", "reports/a2c_samsung.pt")
report_dir = cfg.get("report_dir", "reports")
device = cfg.get("device", "cpu")

os.makedirs(report_dir, exist_ok=True)

print("========== [A2C Evaluation in Notebook] ==========")
print(f"- Ticker             : {ticker}")
print(f"- KOSPI ticker       : {kospi_ticker}")
print(f"- VIX ticker         : {vix_ticker}")
print(f"- 다운로드 구간      : {start_date} ~ {end_date}")
print(f"- window_size        : {window_size}")
print(f"- trade_penalty      : {trade_penalty}")
print(f"- use_daily_unrealized: {use_daily_unrealized}")
print(f"- device             : {device}\n")

# -------------------------------------------
# 4. 데이터 다운로드 & 지표 계산
# -------------------------------------------
print("[1] 데이터 다운로드 및 지표 계산중 ...")

df = download_data(
    ticker=ticker,
    kospi_ticker=kospi_ticker,
    vix_ticker=vix_ticker,
    start_date=start_date,
    end_date=end_date,
)
df = add_indicators(df)
df = df.dropna(subset=FEATURES + ["Close", "KOSPI"])

print(f"    · 전체 데이터 기간: {df.index.min().date()} ~ {df.index.max().date()} (총 {len(df)}일)")

# -------------------------------------------
# 5. 오늘 기준 최근 10년 / 최근 1년 분할
# -------------------------------------------
print("[2] 오늘 기준 최근 10년 학습 + 최근 1년 테스트 구간 분할 ...")
train_df, test_df, today = split_last_10y_train_1y_test(df)

if train_df.empty or test_df.empty:
    raise RuntimeError(
        f"[evaluation] train/test 데이터가 비어 있습니다. "
        f"len(train_df)={len(train_df)}, len(test_df)={len(test_df)}"
    )

print(f"    · today(데이터 마지막 날짜): {today.date()}")
print(f"    · Train 기간: {train_df.index.min().date()} ~ {train_df.index.max().date()} (총 {len(train_df)}일)")
print(f"    · Test  기간: {test_df.index.min().date()} ~ {test_df.index.max().date()} (총 {len(test_df)}일)")

# -------------------------------------------
# 6. 스케일러 & 테스트 구간 스케일링
# -------------------------------------------
print("[3] 스케일러 로드 및 테스트 구간 스케일링 ...")

scaler_path = os.path.join(report_dir, "scaler.joblib")
if not os.path.exists(scaler_path):
    raise FileNotFoundError(
        f"[evaluation] scaler.joblib이 없습니다. ({scaler_path})\n"
        f"train_a2c.py에서 학습 및 저장이 먼저 되어야 합니다."
    )

scaler = joblib.load(scaler_path)

test_indicators = test_df[FEATURES].values.astype(float)
test_scaled = scaler.transform(test_indicators)

test_df_scaled = test_df.copy()
test_df_scaled[FEATURES] = test_scaled

# -------------------------------------------
# 7. TradingEnv & A2CAgent 로드
# -------------------------------------------
print("[4] TradingEnv 및 A2CAgent 로드 ...")

env = TradingEnv(
    data=test_df_scaled,
    window_size=window_size,
    trade_penalty=trade_penalty,
    use_daily_unrealized=use_daily_unrealized,
    reward_cfg=reward_cfg,
)

state_dim = env.current_state_dim()
action_dim = 3  # 0=Long, 1=Short, 2=Hold

agent = A2CAgent(
    state_dim=state_dim,
    action_dim=action_dim,
    device=device,
)

if not os.path.exists(model_path):
    raise FileNotFoundError(
        f"[evaluation] 학습된 모델 파일이 없습니다. ({model_path})\n"
        f"train_a2c.py에서 학습 및 모델 저장이 먼저 되어야 합니다."
    )

agent.load(model_path)
agent.epsilon = 0.0

print(f"    · 모델 로드 완료: {model_path}")

# -------------------------------------------
# 8. 백테스트 실행 (일별 r_t 기준, 초반 포지션 강제)
# -------------------------------------------
print("\n[5] 테스트 구간 백테스트 진행 ...")

s = env.reset()
done = False

daily_returns = []
rewards = []
actions = []

has_position = False   # ✅ 아직 포지션이 없으면 True가 될 때까지 Hold 금지

while not done:
    a_raw, _ = agent.act(s, deterministic=True)

    # ✅ 초반부터 포지션 잡도록 강제: 포지션 없는데 Hold(2) 나오면 Long(0)으로 바꿈
    if (not has_position) and (a_raw == 2):
        a = 0  # Long 강제
    else:
        a = a_raw

    ns, r, done, info = env.step(a)

    if a in (0, 1):    # Long 또는 Short 한 번이라도 하면 이후에는 자유
        has_position = True

    r_t = float(info.get("r_t", 0.0))

    daily_returns.append(r_t)
    rewards.append(r)
    actions.append(a)

    s = ns if not done else s

daily_returns = np.array(daily_returns, dtype=float)
rewards = np.array(rewards, dtype=float)
actions = np.array(actions, dtype=int)

print(f"    · 총 스텝 수: {len(daily_returns)} (거래일 기준)")

# -------------------------------------------
# 9. 성능 지표 (승률 포함) 출력
# -------------------------------------------
print("\n[6] 백테스트 성능 지표 (r_t 기준) ...")
metrics = compute_backtest_metrics(daily_returns)

print(f"    - 누적 수익률      : {metrics['cum_return']*100:.2f}%")
print(f"    - 일 평균 수익률    : {metrics['mean_ret']*100:.4f}%")
print(f"    - 일 수익률 변동성  : {metrics['vol']*100:.4f}%")
print(f"    - 샤프 비율 (연환산): {metrics['sharpe']:.3f}")
print(
    f"    - 승률 (r_t > 0)    : "
    f"{metrics['win_rate']*100:.2f}% "
    f"({metrics['wins']}/{metrics['days']} 일)"
)
print(f"    - 최대 낙폭(MDD)    : {metrics['mdd']*100:.2f}%")

# -------------------------------------------
# 10. 수익률/승률 시각화 (전체 구간 + 최근 30일 확대)
# -------------------------------------------
print("\n[7] 일별 수익률 및 승률 시각화 ...")

port_rets = np.array(env.port_ret_hist, dtype=float)
mkt_rets_env = np.array(env.mkt_ret_hist, dtype=float)  # 필요하면 참고용
equity_curve = np.array(env.equity_curve, dtype=float)
buyhold_curve = np.array(env.buyhold_curve, dtype=float)

# 첫 트레이드 가능한 날부터의 날짜 (window_size일 이후)
dates = test_df.index[window_size:]
min_len = min(len(dates), len(port_rets))

dates = dates[-min_len:]
port_rets = port_rets[-min_len:]
equity_agent = equity_curve[-min_len:]
equity_bh = buyhold_curve[-min_len:]

# ✅ KOSPI는 원본 test_df 사용해서 "몇 배"로 정규화
kospi_price = test_df["KOSPI"].values.astype(float)
equity_kospi_full = kospi_price / kospi_price[0]
equity_kospi = equity_kospi_full[window_size:][-min_len:]

win_ret = port_rets > 0
cum_win_ret = np.cumsum(win_ret) / np.arange(1, len(win_ret) + 1)

# ---------- (1) 전체 테스트 구간 그래프 ----------
fig, axes = plt.subplots(3, 1, figsize=(16, 10), sharex=True)

axes[0].plot(dates, equity_agent, label="A2C 포트폴리오")
axes[0].plot(dates, equity_bh, label="삼성전자 Buy&Hold", linestyle="--")
axes[0].plot(dates, equity_kospi, label="KOSPI 지수 (정규화)", linestyle=":")
axes[0].set_ylabel("누적 가치 (배)")
axes[0].legend()
axes[0].grid(True)

colors = ["tab:red" if r < 0 else "tab:blue" for r in port_rets]
axes[1].bar(dates, port_rets, label="A2C 일별 수익률", color=colors)
axes[1].axhline(0.0, linestyle="--", linewidth=1)
axes[1].set_ylabel("일별 수익률")
axes[1].legend()
axes[1].grid(True)

axes[2].plot(dates, cum_win_ret * 100.0, label="승률 (r_t > 0)")
axes[2].set_ylabel("누적 승률 (%)")
axes[2].set_xlabel("날짜")
axes[2].legend()
axes[2].grid(True)

# x축 날짜 tick – 5일 간격
day_locator = mdates.DayLocator(interval=5)
day_formatter = mdates.DateFormatter("%Y-%m-%d")
for ax in axes:
    ax.xaxis.set_major_locator(day_locator)
    ax.xaxis.set_major_formatter(day_formatter)
plt.setp(axes[-1].get_xticklabels(), rotation=90, fontsize=6)

plt.tight_layout()
plt.show()

# ---------- (2) 최근 30거래일 확대 그래프 ----------
zoom_n = 30
if len(dates) >= zoom_n:
    z_dates = dates[-zoom_n:]
    z_port = port_rets[-zoom_n:]
    z_eq_agent = equity_agent[-zoom_n:]
    z_eq_bh = equity_bh[-zoom_n:]
    z_eq_kospi = equity_kospi[-zoom_n:]
    z_cum_win = cum_win_ret[-zoom_n:]

    fig2, axes2 = plt.subplots(3, 1, figsize=(16, 10), sharex=True)

    axes2[0].plot(z_dates, z_eq_agent, label="A2C 포트폴리오")
    axes2[0].plot(z_dates, z_eq_bh, label="삼성전자 Buy&Hold", linestyle="--")
    axes2[0].plot(z_dates, z_eq_kospi, label="KOSPI 지수 (정규화)", linestyle=":")
    axes2[0].set_ylabel("누적 가치 (배)")
    axes2[0].legend()
    axes2[0].grid(True)

    colors_z = ["tab:red" if r < 0 else "tab:blue" for r in z_port]
    axes2[1].bar(z_dates, z_port, label="A2C 일별 수익률", color=colors_z)
    axes2[1].axhline(0.0, linestyle="--", linewidth=1)
    axes2[1].set_ylabel("일별 수익률")
    axes2[1].legend()
    axes2[1].grid(True)

    axes2[2].plot(z_dates, z_cum_win * 100.0, label="승률 (r_t > 0)")
    axes2[2].set_ylabel("누적 승률 (%)")
    axes2[2].set_xlabel("날짜")
    axes2[2].legend()
    axes2[2].grid(True)

    day_locator2 = mdates.DayLocator(interval=1)
    day_formatter2 = mdates.DateFormatter("%Y-%m-%d")
    for ax in axes2:
        ax.xaxis.set_major_locator(day_locator2)
        ax.xaxis.set_major_formatter(day_formatter2)
    plt.setp(axes2[-1].get_xticklabels(), rotation=90, fontsize=8)

    plt.tight_layout()
    plt.show()
else:
    print("    · 데이터가 30거래일보다 짧아서 확대 그래프는 생략합니다.")