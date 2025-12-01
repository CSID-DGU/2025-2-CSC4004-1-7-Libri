# data_utils.py

import numpy as np
import pandas as pd
from typing import Tuple, List

import yfinance as yf
import pandas_ta as ta


# ============================================================
# 1. 사용할 피처(기술 지표) 정의
# ============================================================

FEATURES: List[str] = [
    "EMA12",
    "EMA26",
    "MACD",
    "Volume",
    "KOSPI",
    "SMA20",
    "RSI",
    "STOCH_%K",
    "VIX",
    "BB_%B",
    "BB_BW",
    "ATR",
]


# ============================================================
# 2. 데이터 다운로드 (★ 수정됨)
# ============================================================

def download_data(
    ticker: str,
    kospi_ticker: str,
    vix_ticker: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    삼성전자, KOSPI, VIX를 yfinance로 받아서
    하나의 DataFrame으로 합친 후 반환.
    
    반환 컬럼:
    - ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'KOSPI', 'VIX']
    """
    # 개별 다운로드
    stock = yf.download(ticker, start=start_date, end=end_date, progress=False)
    kospi = yf.download(kospi_ticker, start=start_date, end=end_date, progress=False)
    vix = yf.download(vix_ticker, start=start_date, end=end_date, progress=False)

    if stock.empty:
        raise ValueError(f"{ticker} 데이터가 비어 있습니다. yfinance 또는 티커 설정을 확인하세요.")
    if kospi.empty:
        raise ValueError(f"{kospi_ticker} (KOSPI) 데이터가 비어 있습니다.")
    if vix.empty:
        raise ValueError(f"{vix_ticker} (VIX) 데이터가 비어 있습니다.")

    # 혹시라도 MultiIndex 컬럼이면 평탄화
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = [c[0] for c in stock.columns]
    if isinstance(kospi.columns, pd.MultiIndex):
        kospi.columns = [c[0] for c in kospi.columns]
    if isinstance(vix.columns, pd.MultiIndex):
        vix.columns = [c[0] for c in vix.columns]

    # 인덱스 공통 구간만 사용
    common_index = stock.index.intersection(kospi.index).intersection(vix.index)
    stock = stock.loc[common_index]
    kospi = kospi.loc[common_index]
    vix   = vix.loc[common_index]

    # 기본 price 데이터
    df = stock.copy()

    # 디버그용(원하면 잠깐 켜서 확인 가능)
    # print("stock.columns:", stock.columns)
    # print("kospi.columns:", kospi.columns)
    # print("vix.columns:", vix.columns)

    # KOSPI, VIX Close 붙이기 (컬럼이 없으면 에러 대신 NaN 채우기)
    if "Close" in kospi.columns:
        df["KOSPI"] = kospi["Close"]
    else:
        df["KOSPI"] = np.nan

    if "Close" in vix.columns:
        df["VIX"] = vix["Close"]
    else:
        df["VIX"] = np.nan

    # --- 여기서가 핵심: 실제 존재하는 컬럼만 subset으로 사용 ---
    required_cols = ["Close", "Volume", "KOSPI", "VIX"]
    existing_cols = [c for c in required_cols if c in df.columns]

    if not existing_cols:
        raise ValueError(
            f"다운로드한 DataFrame에 Close/Volume/KOSPI/VIX 중 아무 컬럼도 없습니다. "
            f"df.columns={list(df.columns)}"
        )

    df = df.dropna(subset=existing_cols)

    return df


# ============================================================
# 3. 기술 지표 생성
# ============================================================

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    원본 price DataFrame에 기술지표를 계산해서 추가한 뒤,
    NaN이 제거된 clean DataFrame을 반환.
    """
    df = df.copy()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # --- 이동 평균 계열 ---
    df["EMA12"] = ta.ema(close, length=12)
    df["EMA26"] = ta.ema(close, length=26)

    macd = ta.macd(close, fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        df["MACD"] = macd.iloc[:, 0]
    else:
        df["MACD"] = np.nan

    df["SMA20"] = ta.sma(close, length=20)

    # --- 모멘텀 계열 ---
    df["RSI"] = ta.rsi(close, length=14)

    stoch = ta.stoch(high=high, low=low, close=close, k=14, d=3)
    if stoch is not None and not stoch.empty:
        df["STOCH_%K"] = stoch.iloc[:, 0]
    else:
        df["STOCH_%K"] = np.nan

    # --- 변동성/심리 계열 ---
    bbands = ta.bbands(close, length=20, std=2)
    if bbands is not None and not bbands.empty:
        bw_col = [c for c in bbands.columns if "BBB_" in c or "BW" in c]
        bp_col = [c for c in bbands.columns if "BBP_" in c or "%B" in c]

        if bw_col:
            df["BB_BW"] = bbands[bw_col[0]]
        else:
            try:
                lower = bbands.iloc[:, 0]
                middle = bbands.iloc[:, 1]
                upper = bbands.iloc[:, 2]
                df["BB_BW"] = (upper - lower) / middle.replace(0, np.nan)
            except Exception:
                df["BB_BW"] = np.nan

        if bp_col:
            df["BB_%B"] = bbands[bp_col[0]]
        else:
            try:
                lower = bbands.iloc[:, 0]
                upper = bbands.iloc[:, 2]
                df["BB_%B"] = (close - lower) / (upper - lower).replace(0, np.nan)
            except Exception:
                df["BB_%B"] = np.nan
    else:
        df["BB_BW"] = np.nan
        df["BB_%B"] = np.nan

    # --- 리스크 계열 ---
    df["ATR"] = ta.atr(high=high, low=low, close=close, length=14)

    # 최종적으로 FEATURE들에 NaN 있는 행 제거
    df = df.dropna(subset=FEATURES)

    return df


# ============================================================
# 4. Train / Test 분할  (기존 + 새로 추가)
# ============================================================

def train_test_split_by_ratio(
    df: pd.DataFrame, train_ratio: float
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    (기존) 비율 기반 분할.
    """
    n = len(df)
    n_train = int(n * train_ratio)
    train_df = df.iloc[:n_train].copy()
    test_df = df.iloc[n_train:].copy()
    return train_df, test_df


def train_test_split_last_10y_and_1y(
    df: pd.DataFrame,
    train_years: int = 10,
    backtest_days: int = 365,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    마지막 날짜를 기준으로:
      - 직전 `backtest_days`일을 test(백테스트) 구간으로,
      - 그 바로 앞 `train_years`년을 train 구간으로 사용.

    예:
      df.index.max() = 2025-01-31 이라면,
        test:   2024-02-01 ~ 2025-01-31 (365일 전 ~ 마지막)
        train:  2014-02-01 ~ 2024-01-31 (그 직전 10년)
    """
    df = df.sort_index()
    last_date = df.index.max()

    # 백테스트 시작일 = 마지막 날짜 - (backtest_days - 1)일
    test_start = last_date - pd.Timedelta(days=backtest_days - 1)

    # 학습 시작일 = test_start - train_years 년
    train_start = test_start - pd.DateOffset(years=train_years)

    # 해당 구간만 잘라서 사용
    df_range = df[df.index >= train_start].copy()

    train_df = df_range[(df_range.index >= train_start) & (df_range.index < test_start)].copy()
    test_df = df_range[df_range.index >= test_start].copy()

    return train_df, test_df


# ============================================================
# 5. 상태 벡터 생성
# ============================================================

def build_state(window_df: pd.DataFrame, position_flag: int) -> np.ndarray:
    feat_mat = window_df[FEATURES].values
    flat_feats = feat_mat.reshape(-1)
    state = np.concatenate([flat_feats, np.array([position_flag], dtype=float)], axis=0)
    return state.astype(np.float32)


# ============================================================
# 6. SHAP용 피처 이름 생성
# ============================================================

def get_feature_names_with_position(window_size: int) -> List[str]:
    names: List[str] = []
    for i in range(window_size):
        lag = window_size - 1 - i
        for feat in FEATURES:
            names.append(f"{feat}_t-{lag}")
    names.append("Position")
    return names