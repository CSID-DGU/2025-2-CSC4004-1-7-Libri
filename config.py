import torch

# --- 설정 ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GAMMA = 0.99
LR = 5e-5
BATCH_SIZE = 64
BUFFER_SIZE = int(5e4)
WINDOW_SIZE = 10
N_AGENTS = 3
TARGET_UPDATE_FREQ = 200
TAU = 0.003

# --- QMIX 관련 설정 ---
MIXER_EMBED_DIM = 32

# --- 데이터 설정 ---
TICKER = "005930.KS"
VIX_TICKER = "^VIX"
START_DATE = "2020-11-17"  # 5년 데이터로 확장 (더 많은 패턴 학습)
END_DATE = "2025-11-16"

# --- 학습 설정 ---
NUM_EPISODES = 500