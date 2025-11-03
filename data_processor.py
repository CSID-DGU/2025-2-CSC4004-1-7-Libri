import yfinance as yf
import pandas as pd
import numpy as np

# --- Config ---
from config import TICKER, VIX_TICKER, START_DATE, END_DATE

# ---- pandas-ta 호환 래퍼 ---------------------------------------
try:
    import pandas_ta as ta
    _USING_PANDAS_TA = True
except Exception:
    _USING_PANDAS_TA = False
    try:
        import ta as _ta
    except Exception as e:
        raise RuntimeError(
            "pandas-ta도, ta도 설치되어 있지 않습니다. 다음 중 하나를 설치하세요:\n"
            "  pip install pandas-ta  (Python 3.12+)\n"
            "  pip install ta          (대체 라이브러리)"
        ) from e

    class _PTAWrapper:
        @staticmethod
        def sma(close, length=20):
            return _ta.trend.SMAIndicator(close=close, window=length).sma_indicator()

        @staticmethod
        def macd(close, fast=12, slow=26, signal=9):
            ind = _ta.trend.MACD(close=close, window_slow=slow, window_fast=fast, window_sign=signal)
            return pd.DataFrame({
                f"MACD_{fast}_{slow}_{signal}": ind.macd(),
                f"MACDs_{fast}_{slow}_{signal}": ind.macd_signal(),
                f"MACDh_{fast}_{slow}_{signal}": ind.macd_diff()
            })

        @staticmethod
        def rsi(close, length=14):
            return _ta.momentum.RSIIndicator(close=close, window=length).rsi()

        @staticmethod
        def stoch(high, low, close, k=14, d=3, smooth_k=3):
            ind = _ta.momentum.StochasticOscillator(
                high=high, low=low, close=close, window=k, smooth_window=smooth_k
            )
            return pd.DataFrame({
                f"STOCHk_{k}_{d}_{smooth_k}": ind.stoch(),
                f"STOCHd_{k}_{d}_{smooth_k}": ind.stoch_signal()
            })

        @staticmethod
        def atr(high, low, close, length=14):
            return _ta.volatility.AverageTrueRange(
                high=high, low=low, close=close, window=length
            ).average_true_range()

        @staticmethod
        def bbands(close, length=20, std=2.0):
            bb = _ta.volatility.BollingerBands(close=close, window=length, window_dev=std)
            return pd.DataFrame({
                f"BBL_{length}_{std}": bb.bollinger_lband(),
                f"BBM_{length}_{std}": bb.bollinger_mavg(),
                f"BBU_{length}_{std}": bb.bollinger_hband()
            })

    ta = _PTAWrapper()
# ------------------------------------------------------------------------------

class DataProcessor:
    def __init__(self, ticker=TICKER, vix_ticker=VIX_TICKER, start=START_DATE, end=END_DATE):
        self.ticker_str = ticker
        self.ticker_obj = yf.Ticker(self.ticker_str)
        self.vix_ticker = vix_ticker
        self.start = start
        self.end = end
        self.features = []
        self.original_prices = None

    def _flatten_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join([str(x) for x in col if str(x) != '']) for col in df.columns]
        return df

    def _strip_suffix(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        suffix = f"_{ticker}"
        if any(str(c).endswith(suffix) for c in df.columns):
            for base in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                col = base + suffix
                if col in df.columns:
                    df[base] = df[col]
        return df

    def fetch_data(self):
        print(f"데이터 다운로드 중 ({self.ticker_str}, {self.vix_ticker})...")
        df = yf.download(self.ticker_str, start=self.start, end=self.end, group_by="column", auto_adjust=False, progress=False, threads=False)
        df = self._flatten_cols(df)
        df = self._strip_suffix(df, self.ticker_str)

        if 'Close' not in df.columns:
            if 'Adj Close' in df.columns:
                df['Close'] = df['Adj Close']
            else:
                raise RuntimeError(f"'{self.ticker_str}' 데이터에 Close/Adj Close 컬럼이 없습니다. 실제 컬럼: {list(df.columns)}")

        needed_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        keep_cols = [c for c in needed_cols if c in df.columns]
        if len(keep_cols) == 0:
            raise RuntimeError(f"'{self.ticker_str}' 데이터가 비었거나 필수 컬럼이 없습니다. 실제 컬럼: {list(df.columns)}")
        df = df[keep_cols].copy()
        if df.empty:
            raise RuntimeError(f"'{self.ticker_str}' 가격 데이터가 비어 있습니다. 날짜 범위/티커를 확인하세요.")

        vix_df = yf.download(self.vix_ticker, start=self.start, end=self.end, group_by="column", auto_adjust=False, progress=False, threads=False)
        vix_df = self._flatten_cols(vix_df)
        vix_df = self._strip_suffix(vix_df, self.vix_ticker)

        if 'Close' not in vix_df.columns:
            if 'Adj Close' in vix_df.columns:
                vix_df['Close'] = vix_df['Adj Close']
            else:
                vix_df['Close'] = np.nan

        vix_df = vix_df[['Close']].rename(columns={'Close': 'VIX'})
        df = df.join(vix_df, how='left')
        if 'VIX' in df.columns:
            df['VIX'] = df['VIX'].ffill()

        missing_cols = [c for c in ['Close', 'VIX'] if c not in df.columns]
        if missing_cols:
            raise RuntimeError(f"필수 컬럼이 없습니다: {missing_cols}. 현재 컬럼: {list(df.columns)}")

        if df['VIX'].isna().all():
            print("경고: VIX 데이터를 가져오지 못했습니다. 0으로 채웁니다.")
            df['VIX'] = 0.0

        df = df.dropna(subset=['Close']).copy()
        if df.empty:
            raise RuntimeError("병합/정리 후 데이터가 비어 있습니다. 기간/네트워크 상태/티커를 확인하세요.")

        try:
            df.index = pd.to_datetime(df.index).tz_localize(None)
        except Exception:
            pass

        return df

    def calculate_features(self, df):
        print("기술적 지표 및 재무 지표 계산 중...")

        def pick(df_like, candidates):
            if not isinstance(df_like, pd.DataFrame):
                raise KeyError("pick expects a DataFrame-like object.")
            for k in candidates:
                if k in df_like.columns:
                    return df_like[k]
            cols = list(df_like.columns)
            for cand in candidates:
                for c in cols:
                    if cand.lower() in str(c).lower():
                        return df_like[c]
            for c in cols:
                head = str(c).split('_')[0]
                for cand in candidates:
                    if cand.lower() == head.lower():
                        return df_like[c]
            raise KeyError(f"원하는 컬럼을 찾지 못했습니다. 사용 가능한 컬럼: {cols}")

        df['SMA20'] = ta.sma(df['Close'], length=20)

        macd = ta.macd(df['Close'])
        df['MACD'] = pick(macd, ['MACD_12_26_9', 'MACD', 'macd'])
        df['MACD_Signal'] = pick(macd, ['MACDs_12_26_9', 'MACD_Signal', 'Signal', 'macd_signal'])

        df['RSI'] = ta.rsi(df['Close'])

        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = pick(stoch, ['STOCHk_14_3_3', 'STOCHk', 'stoch_k', 'K', 'k'])
        df['Stoch_D'] = pick(stoch, ['STOCHd_14_3_3', 'STOCHd', 'stoch_d', 'D', 'd'])

        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'])

        bbands = ta.bbands(df['Close'], length=20)
        lower = pick(bbands, ['BBL_20_2.0', 'BBL_20_2', 'BBL', 'lower', 'lband', 'bollinger_lband', 'bb_lower'])
        upper = pick(bbands, ['BBU_20_2.0', 'BBU_20_2', 'BBU', 'upper', 'hband', 'bollinger_hband', 'bb_upper'])
        denom = (upper - lower).replace(0, np.nan)
        df['Bollinger_B'] = ((df['Close'] - lower) / (denom + 1e-9)).clip(-1, 2)

        print("분기별 재무제표 가져오는 중...")
        qf = self.ticker_obj.quarterly_financials
        qbs = self.ticker_obj.quarterly_balance_sheet

        try:
            if (qf is not None) and (qbs is not None) and ('Net Income' in qf.index) and ('Total Assets' in qbs.index):
                net_income = qf.loc['Net Income'].T
                total_assets = qbs.loc['Total Assets'].T
                total_liab = qbs.loc['Total Liabilities Net Minority Interest'].T

                df_fund = pd.DataFrame(index=total_assets.index)
                df_fund['ROA'] = net_income / total_assets
                df_fund['DebtRatio'] = total_liab / total_assets

                df_fund.index = pd.to_datetime(df_fund.index)
                try:
                    df_fund = df_fund.tz_localize(None)
                except Exception:
                    pass
                
                df_fund_daily = df_fund.resample('D').ffill()
                df_fund_daily = df_fund_daily.reindex(df.index).ffill().fillna(0.0) 
                df = df.join(df_fund_daily)
                
            else:
                print("경고: 재무제표(ROA, DebtRatio)를 가져올 수 없습니다. 0으로 채웁니다.")
                df['ROA'] = 0.0
                df['DebtRatio'] = 0.0
        except Exception as e:
            print(f"경고: 재무제표 처리 중 오류({e}). 0으로 채웁니다.")
            df['ROA'] = 0.0
            df['DebtRatio'] = 0.0

        print("애널리스트 추천 정보 가져오는 중...")
        try:
            rec = self.ticker_obj.recommendations

            if rec is None or rec.empty:
                raise Exception("추천 정보 데이터가 비어있음")

            required_cols = ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']
            if not all(col in rec.columns for col in required_cols):
                raise Exception(f"필요한 컬럼({required_cols})이 없음. 현재 컬럼: {list(rec.columns)}")

            latest_rec = rec.iloc[0]

            score_buy = (latest_rec['strongBuy'] * 1.5) + (latest_rec['buy'] * 1.0)
            score_sell = (latest_rec['sell'] * 1.0) + (latest_rec['strongSell'] * 1.5)
            total_count = latest_rec[required_cols].sum()

            if total_count == 0:
                weighted_score = 0.0
            else:
                weighted_score = (score_buy - score_sell) / total_count
            
            df['AnalystRating'] = weighted_score

        except Exception as e:
            print(f"경고: 애널리스트 추천 정보({e})를 가져올 수 없습니다. 0으로 채웁니다.")
            df['AnalystRating'] = 0.0

        self.features = [
            'Close', 'High', 'Low', 'Volume', 'VIX',
            'SMA20', 'MACD', 'MACD_Signal', 'RSI', 'Stoch_K', 'Stoch_D', 'ATR', 'Bollinger_B',
            'ROA', 'DebtRatio', 'AnalystRating'
        ]

        df = df.dropna()
        return df

    def normalize_data(self, df):
        print("데이터 정규화 중...")
        self.original_prices = df['Close'].copy()
        
        for col in ['Close', 'High', 'Low', 'SMA20']:
            if col in df.columns:
                df[col] = (df[col] / (df[col].iloc[0] + 1e-9)) - 1.0

        for col in ['Volume', 'ATR', 'VIX']:
            if col in df.columns:
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min() + 1e-9)

        for col in ['MACD', 'MACD_Signal', 'ROA', 'DebtRatio']:
            if col in df.columns:
                df[col] = (df[col] - df[col].mean()) / (df[col].std() + 1e-9)

        for col in ['RSI', 'Stoch_K', 'Stoch_D']:
            if col in df.columns:
                df[col] = df[col] / 100.0

        if 'AnalystRating' in df.columns:
            # 0으로만 채워진 경우 std()가 0이 되어 NaN이 될 수 있으므로 분모에 1e-9 추가
            df['AnalystRating'] = (df['AnalystRating'] - df['AnalystRating'].mean()) / (df['AnalystRating'].std() + 1e-9)

        if 'Bollinger_B' in df.columns:
            df['Bollinger_B'] = np.clip(df['Bollinger_B'], -1, 2)

        df = df.fillna(0)
        return df

    def process(self):
        if not _USING_PANDAS_TA:
            print("[알림] pandas-ta를 찾지 못하여 'ta' 라이브러리로 대체했습니다.")
             
        df = self.fetch_data()
        df_features = self.calculate_features(df)
        
        df_features_unnormalized = df_features.copy()
        
        df_normalized = self.normalize_data(df_features_unnormalized.copy()) 

        self.original_prices = self.original_prices.reindex(df_normalized.index).dropna()
        df_normalized = df_normalized.reindex(self.original_prices.index).dropna()
        df_features = df_features.reindex(self.original_prices.index).dropna()

        print(f"--- 데이터 처리 완료 ---")
        print(f"총 {len(df_normalized)}일의 데이터")
        print(f"사용된 지표 (총 {len(self.features)}개): {', '.join(self.features)}")

        return df_normalized[self.features], df_features[self.features], self.original_prices, self.features