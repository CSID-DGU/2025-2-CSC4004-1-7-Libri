import torch

# --- 설정 ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# [개선 1] Gamma 증가 - 장기 보상 중시
GAMMA = 0.995  # 0.99 -> 0.995

# [개선 2] Learning Rate 증가 - 더 빠른 학습
LR = 3e-4  # 1e-5 -> 3e-4

# [개선 3] Batch Size 증가 - 안정적 학습
BATCH_SIZE = 128  # 64 -> 128

# [개선 4] Buffer Size 증가 - 더 다양한 경험
BUFFER_SIZE = int(1e5)  # 5e4 -> 1e5

WINDOW_SIZE = 10
N_AGENTS = 3

# [개선 5] Target Update 빈도 감소 - 안정성 향상
TARGET_UPDATE_FREQ = 500  # 1000 -> 500

# [개선 6] TAU 증가 - 더 빠른 Target Network 업데이트
TAU = 0.01  # 0.005 -> 0.01

# --- QMIX 관련 설정 ---
# [개선 7] Mixer Embed Dim 증가 - 더 강력한 표현력
MIXER_EMBED_DIM = 64  # 32 -> 64

# --- 데이터 설정 ---
TICKER = "005930.KS"
VIX_TICKER = "^VIX"
START_DATE = "2020-11-12"
END_DATE = "2025-11-11"

# --- 학습 설정 ---
# [개선 8] 에피소드 수 증가 - 충분한 학습
NUM_EPISODES = 200  # 100 -> 200 (더 충분한 학습)

# [개선 9] 탐험 설정 추가
EPSILON_START = 1.0
EPSILON_END = 0.05  # 0.01 -> 0.05 (최소 탐험 유지)
EPSILON_DECAY_STEPS = 150000  # 100000 -> 150000 (더 긴 탐험 기간)

# [개선 11] Warmup 설정 - 초기 경험 수집
WARMUP_STEPS = 5000  # 학습 전 랜덤 행동으로 경험 수집

# [개선 10] 보상 스케일링 - Q-value collapse 방지를 위해 크게 증가
REWARD_SCALE = 100.0  # 보상을 주가 대비 비율로 변환