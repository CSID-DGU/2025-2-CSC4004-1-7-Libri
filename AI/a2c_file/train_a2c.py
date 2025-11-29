# train_a2c.py

import os
import yaml
import joblib
import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler

from data_utils import download_data, add_indicators, FEATURES
from trading_env import TradingEnv
from ac_model import A2CAgent


# --- A2C용 검증(Validation) 함수 ---
def validate_agent(agent: A2CAgent, env_config: dict, scaler: StandardScaler = None):
    """
    훈련 중인 에이전트를 테스트(백테스트) 데이터셋으로 검증합니다.
    env_config: TradingEnv 생성에 사용할 설정 딕셔너리
    scaler: 여기서는 이미 스케일된 데이터를 env에 넣는 구조라면 사용하지 않음
    """
    val_env = TradingEnv(**env_config)
    s = val_env.reset()
    done = False
    episode_reward = 0.0

    while not done:
        # 검증 시에는 deterministic=True로 greedy 정책 사용
        a, _ = agent.act(s, deterministic=True)
        ns, r, done, _ = val_env.step(a)
        episode_reward += r
        s = ns if not done else s

    return episode_reward


def calendar_split(df: pd.DataFrame, train_years: int, backtest_days: int):
    """
    df 전체에서
      - 마지막 날짜 기준으로 직전 backtest_days일을 test(백테스트)로,
      - 그 이전 train_years년을 train으로 사용.
    """
    last_date = df.index[-1]
    backtest_end = last_date
    backtest_start = backtest_end - pd.Timedelta(days=backtest_days)

    train_start = backtest_end - pd.DateOffset(years=train_years)

    train_df = df.loc[(df.index >= train_start) & (df.index < backtest_start)].copy()
    test_df = df.loc[(df.index >= backtest_start) & (df.index <= backtest_end)].copy()

    print("\n[데이터 분할(캘린더 기준)]")
    print(
        f"  - Train 기간: {train_df.index[0].date()} ~ {train_df.index[-1].date()} "
        f"({len(train_df)}일)"
    )
    print(
        f"  - Test  기간: {test_df.index[0].date()} ~ {test_df.index[-1].date()} "
        f"({len(test_df)}일)"
    )

    return train_df, test_df


def run_training():
    print("A2C 모델 학습을 시작합니다...")

    # 1. 설정 로드
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    report_dir = cfg["report_dir"]
    os.makedirs(report_dir, exist_ok=True)

    # A2C 관련 설정값 로드
    window_size = cfg["window_size"]
    model_cfg = cfg["model_cfg"]
    reward_cfg = cfg.get("reward", {})
    validate_every = cfg.get("validate_every_n_episodes", 10)
    model_path = cfg["model_path"]

    train_years = cfg.get("train_years", 10)
    backtest_days = cfg.get("backtest_days", 365)

    # 2. 데이터 로드 및 전처리
    print("데이터 로딩 및 전처리 중...")
    raw = download_data(
        cfg["ticker"],
        cfg["kospi_ticker"],
        cfg["vix_ticker"],
        cfg["start_date"],
        cfg["end_date"],
    )
    df = add_indicators(raw)

    # === 10년 학습 + 1년 백테스트(최근) ===
    train_df, test_df = calendar_split(df, train_years, backtest_days)

    # 3. 데이터 정규화 (StandardScaler)
    print("\n데이터 정규화(Scaling) 수행 중...")
    scaler = StandardScaler()
    train_df[FEATURES] = scaler.fit_transform(train_df[FEATURES])
    test_df[FEATURES] = scaler.transform(test_df[FEATURES])  # test는 transform만

    # 4. 스케일러 저장
    scaler_path = os.path.join(report_dir, "scaler.joblib")
    joblib.dump(scaler, scaler_path)
    print(f"Scaler 저장 완료: {scaler_path}")

    # 5. 환경 및 에이전트 생성 (A2C)
    print("\n환경 및 A2C 에이전트 생성 중...")
    train_env_config = {
        "data": train_df,
        "window_size": window_size,
        "trade_penalty": cfg["trade_penalty"],
        "use_daily_unrealized": cfg["use_daily_unrealized"],
        "reward_cfg": reward_cfg,
    }
    val_env_config = {
        "data": test_df,
        "window_size": window_size,
        "trade_penalty": cfg["trade_penalty"],
        "use_daily_unrealized": cfg["use_daily_unrealized"],
        "reward_cfg": reward_cfg,
    }

    env = TradingEnv(**train_env_config)

    # A2CAgent 생성
    agent = A2CAgent(
        state_dim=env.current_state_dim(),  # env에서 현재 상태 차원을 알려주는 메서드
        action_dim=3,
        hidden_dims=model_cfg.get("hidden_dims", [128, 128]),
        gamma=cfg["gamma"],
        lr=cfg["lr"],
        value_loss_coeff=cfg["value_loss_coeff"],
        entropy_coeff=cfg["entropy_coeff"],
        seed=cfg["seed"],
        device=cfg.get("device", "cpu"),
    )

    # 6. A2C 학습 루프 (On-Policy)
    episodes = cfg["episodes"]
    best_val_reward = -np.inf
    print(f"\nA2C 학습 시작 (총 {episodes} 에피소드)...")

    # --- 학습 곡선 분석용 로그 ---
    episode_rewards = []
    val_rewards = []

    for ep in range(episodes):
        s = env.reset()
        done = False
        episode_reward = 0.0

        # --- 디버깅 누적용 (보상 구성 요소 평균 보기) ---
        dbg_acc = {
            "base": 0.0,
            "r_t": 0.0,
            "rb_t": 0.0,
            "comp_beta": 0.0,
            "comp_R": 0.0,
            "comp_Ddown": 0.0,
            "comp_Dret": 0.0,
            "comp_Try": 0.0,
        }
        steps = 0

        desc = f"Episode {ep + 1}/{episodes}"
        pbar = tqdm(total=len(train_df) - window_size, desc=desc, leave=True)

        while not done:
            # 1. 행동 결정 (샘플링)
            a, log_prob = agent.act(s, deterministic=False)

            # 2. 크리틱의 현재 상태 가치(V(s)) 추정
            value = agent.get_value(s)

            # 3. 환경 스텝
            ns, r, done, info = env.step(a)

            # 4. 롤아웃 버퍼에 저장
            agent.remember(s, a, r, ns, done, log_prob, value)

            episode_reward += r
            s = ns if not done else s
            pbar.update(1)

            # --- info 누적 (디버그용) ---
            for k in dbg_acc.keys():
                if k in info:
                    dbg_acc[k] += info[k]
            steps += 1

        pbar.close()

        # 5. (핵심) 에피소드가 끝나면, 수집된 롤아웃으로 학습
        loss_tuple = agent.train_step()

        # 에피소드 보상 로그 저장
        episode_rewards.append(episode_reward)

        # --- 에피소드별 디버그 출력 ---
        if steps > 0:
            avg_dbg = {k: v / steps for k, v in dbg_acc.items()}
            print(
                f"[DBG Ep {ep+1}] "
                f"base:{avg_dbg['base']:.5f} "
                f"r:{avg_dbg['r_t']:.5f} rb:{avg_dbg['rb_t']:.5f} "
                f"beta:{avg_dbg['comp_beta']:.3f} "
                f"R:{avg_dbg['comp_R']:.3f} D:{avg_dbg['comp_Ddown']:.3f} "
                f"Dret:{avg_dbg['comp_Dret']:.3f} Try:{avg_dbg['comp_Try']:.3f}"
            )

        if loss_tuple:
            actor_loss, critic_loss, entropy_loss = loss_tuple

            # NaN / Inf 감지
            if not np.isfinite(actor_loss):
                print(f"[WARN] Ep {ep+1}: actor_loss is {actor_loss}")
            if not np.isfinite(critic_loss):
                print(f"[WARN] Ep {ep+1}: critic_loss is {critic_loss}")

            print(
                f"Ep {ep+1:4d} | "
                f"Reward: {episode_reward:12.2f} | "
                f"A_Loss: {actor_loss:10.4f} | "
                f"C_Loss: {critic_loss:14.4f} | "
                f"E_Loss: {entropy_loss:10.4f}"
            )
        else:
            print(
                f"Ep {ep+1:4d} | "
                f"Reward: {episode_reward:12.2f} | "
                "(버퍼가 비어 학습 스킵)"
            )

        # 7. 검증
        if (ep + 1) % validate_every == 0:
            val_reward = validate_agent(agent, val_env_config, scaler)
            val_rewards.append(val_reward)

            print(f"--- Validation Ep {ep+1} | Reward: {val_reward:.2f} ---")

            if val_reward > best_val_reward:
                best_val_reward = val_reward
                print(f"*** New Best Model! Saving to {model_path} ***")
                agent.save(model_path)

    # --- 학습 요약 출력 + 로그 저장 ---
    if len(episode_rewards) > 0:
        ep_rewards_arr = np.array(episode_rewards, dtype=float)

        first_100_mean = ep_rewards_arr[:100].mean() if len(ep_rewards_arr) >= 100 else ep_rewards_arr.mean()
        last_100_mean = ep_rewards_arr[-100:].mean() if len(ep_rewards_arr) >= 100 else ep_rewards_arr.mean()
        best_ep_reward = ep_rewards_arr.max()

        best_val = best_val_reward if np.isfinite(best_val_reward) else (np.max(val_rewards) if val_rewards else np.nan)

        print("\n--- 학습 곡선 분석 ---")
        print(f"    - 초기 100 에피소드 평균: {first_100_mean:.2f}")
        print(f"    - 최종 100 에피소드 평균: {last_100_mean:.2f}")
        print(f"    - 최고 에피소드 보상: {best_ep_reward:.2f}")
        print(f"    - 최고 검증 보상: {best_val:.2f}")

        hist_path = os.path.join(report_dir, "a2c_train_history.npz")
        np.savez(
            hist_path,
            episode_rewards=ep_rewards_arr,
            val_rewards=np.array(val_rewards, dtype=float),
        )
        print(f"[INFO] 학습 로그 저장 완료: {hist_path}")

    print(
        f"\n[OK] A2C Training finished. "
        f"Best validation reward: {best_val_reward:.2f} (saved to {model_path})"
    )


if __name__ == "__main__":
    run_training()