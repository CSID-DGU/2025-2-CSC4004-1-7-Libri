import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler # [추가]

# --- Config ---
from config import TICKER, VIX_TICKER, START_DATE, END_DATE

# ---- pandas-ta 호환 래퍼 (이하 동일) -----------------------------
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
        
        # [수정] 피처 목록 세분화
        self.features = []
        self.agent_0_features = [] # 단기 트레이더 피처
        self.agent_1_features = [] # 추세 추종자 피처
        
        self.original_prices = None
        self.scalers = {}

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
            
        df = df.sort_index() # [추가] merge_asof를 위해 인덱스 정렬
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
                
                # [수정] 재무제표 데이터 누수 해결 (2개월 공시 지연 적용)
                print("... 재무제표에 2개월 공시 지연(lag) 적용 ...")
                df_fund.index = df_fund.index + pd.DateOffset(months=2)
                
                try:
                    df_fund = df_fund.tz_localize(None)
                except Exception:
                    pass
                
                df_fund_daily = df_fund.resample('D').ffill()
                # [수정] reindex 대신 merge_asof 사용 (더 안전함)
                df = pd.merge_asof(df, df_fund_daily, left_index=True, right_index=True, direction='backward')
                df[['ROA', 'DebtRatio']] = df[['ROA', 'DebtRatio']].ffill().fillna(0.0)
                
            else:
                print("경고: 재무제표(ROA, DebtRatio)를 가져올 수 없습니다. 0으로 채웁니다.")
                df['ROA'] = 0.0
                df['DebtRatio'] = 0.0
        except Exception as e:
            print(f"경고: 재무제표 처리 중 오류({e}). 0으로 채웁니다.")
            df['ROA'] = 0.0
            df['DebtRatio'] = 0.0

        # [수정] 애널리스트 평가 데이터 누수 해결
        print("애널리스트 추천 정보 (시계열) 가져오는 중...")
        try:
            rec = self.ticker_obj.recommendations
            if rec is None or rec.empty:
                raise Exception("추천 정보 데이터가 비어있음")

            required_cols = ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']
            if not all(col in rec.columns for col in required_cols):
                raise Exception(f"필요한 컬럼({required_cols})이 없음. 현재 컬럼: {list(rec.columns)}")

            # 날짜 인덱스 정리
            try:
                rec.index = pd.to_datetime(rec.index).tz_localize(None)
            except Exception:
                pass # 이미 naive일 수 있음
            rec = rec.sort_index()

            # 각 날짜(행)별로 점수 계산
            score_buy = (rec['strongBuy'] * 1.5) + (rec['buy'] * 1.0)
            score_sell = (rec['sell'] * 1.0) + (rec['strongSell'] * 1.5)
            total_count = rec[required_cols].sum(axis=1)
            
            rec_scores = pd.DataFrame(index=rec.index)
            # 0으로 나누는 것 방지
            rec_scores['AnalystRating'] = (score_buy - score_sell) / (total_count + 1e-9)
            rec_scores = rec_scores.fillna(0.0)

            # merge_asof: df의 날짜를 기준으로, 그 날짜와 가장 가깝거나 이전인 rec_scores의 점수를 할당
            df = pd.merge_asof(df, rec_scores, left_index=True, right_index=True, direction='backward')
            df['AnalystRating'] = df['AnalystRating'].ffill().fillna(0.0) # 혹시 모를 초기 결측치 채우기

        except Exception as e:
            print(f"경고: 애널리스트 추천 정보({e})를 가져올 수 없습니다. 0으로 채웁니다.")
            df['AnalystRating'] = 0.0


        # [수정] 피처 목록을 역할별로 명확히 분리
        # (Close, High, Low, Volume, VIX 등 핵심 가격 정보는 둘 다에게 공통으로 제공)
        
        self.agent_0_features = [ # 단기/변동성
            'Close', 'High', 'Low', 'Volume', 'VIX',
            'RSI', 'Stoch_K', 'Stoch_D', 'ATR', 'Bollinger_B'
        ]
        
        self.agent_1_features = [ # 장기/추세/펀더멘탈
            'Close', 'High', 'Low', 'Volume', 'VIX',
            'SMA20', 'MACD', 'MACD_Signal',
            'ROA', 'DebtRatio', 'AnalystRating'
        ]
        
        # [수정] self.features는 두 리스트의 합집합 (중복 제거)
        self.features = sorted(list(set(self.agent_0_features + self.agent_1_features)))

        df = df.dropna()
        return df

    # [수정] normalize_data 함수 변경
    # (self, df) -> (self, df_train, df_test)
    def normalize_data(self, df_train, df_test):
        print("데이터 정규화 중 (Train-Test 분리 적용)...")
        
        df_train_norm = df_train.copy()
        df_test_norm = df_test.copy()
        
        # 1. 가격 기반 정규화 (x / x_train[0]) - 1.0
        #    Test 데이터도 Train의 첫 번째 값으로 정규화
        price_cols = ['Close', 'High', 'Low', 'SMA20']
        for col in price_cols:
            if col in df_train_norm.columns:
                first_val = df_train[col].iloc[0] + 1e-9
                df_train_norm[col] = (df_train_norm[col] / first_val) - 1.0
                df_test_norm[col] = (df_test_norm[col] / first_val) - 1.0
                self.scalers[col] = {'type': 'price', 'first_val': first_val}

        # 2. MinMaxScaler (Volume, ATR, VIX)
        #    Train 데이터로 fit, Train/Test 데이터에 transform
        minmax_cols = ['Volume', 'ATR', 'VIX']
        for col in minmax_cols:
            if col in df_train_norm.columns:
                scaler = MinMaxScaler()
                df_train_norm[col] = scaler.fit_transform(df_train_norm[[col]])
                df_test_norm[col] = scaler.transform(df_test_norm[[col]])
                self.scalers[col] = scaler

        # 3. StandardScaler (MACD, ... AnalystRating)
        #    Train 데이터로 fit, Train/Test 데이터에 transform
        std_cols = ['MACD', 'MACD_Signal', 'ROA', 'DebtRatio', 'AnalystRating']
        for col in std_cols:
            if col in df_train_norm.columns:
                scaler = StandardScaler()
                df_train_norm[col] = scaler.fit_transform(df_train_norm[[col]])
                df_test_norm[col] = scaler.transform(df_test_norm[[col]])
                self.scalers[col] = scaler

        # 4. 100으로 나누기 (고정 스케일)
        ratio_cols = ['RSI', 'Stoch_K', 'Stoch_D']
        for col in ratio_cols:
            if col in df_train_norm.columns:
                df_train_norm[col] = df_train_norm[col] / 100.0
                df_test_norm[col] = df_test_norm[col] / 100.0
                self.scalers[col] = {'type': 'ratio_100'}

        # 5. Clipping (고정 스케일)
        if 'Bollinger_B' in df_train_norm.columns:
            df_train_norm['Bollinger_B'] = np.clip(df_train_norm['Bollinger_B'], -1, 2)
            df_test_norm['Bollinger_B'] = np.clip(df_test_norm['Bollinger_B'], -1, 2)
            self.scalers['Bollinger_B'] = {'type': 'clip_m1_2'}

        df_train_norm = df_train_norm.fillna(0)
        df_test_norm = df_test_norm.fillna(0)
        
        return df_train_norm, df_test_norm

    # [수정] process 함수에서 정규화 로직 제거
    def process(self):
        if not _USING_PANDAS_TA:
            print("[알림] pandas-ta를 찾지 못하여 'ta' 라이브러리로 대체했습니다.")
             
        df = self.fetch_data()
        df_features = self.calculate_features(df) # 데이터 누수 해결된 피처
        
        # 원본 가격 데이터 저장 (정규화 전에)
        self.original_prices = df_features['Close'].copy()
        
        # original_prices와 df_features의 인덱스를 맞춤
        self.original_prices = self.original_prices.reindex(df_features.index).dropna()
        df_features = df_features.reindex(self.original_prices.index).dropna()

        print(f"--- 데이터 처리 완료 (정규화 전) ---")
        print(f"총 {len(df_features)}일의 데이터")
        print(f"사용된 지표 (총 {len(self.features)}개): {', '.join(self.features)}")
        print(f"  - Agent 0 (단기): {len(self.agent_0_features)}개")
        print(f"  - Agent 1 (장기): {len(self.agent_1_features)}개")

        # [수정] 정규화되지 않은 df, 원본 가격, 피처 목록 *3개* 반환
        return (
            df_features[self.features], 
            self.original_prices, 
            self.features,
            self.agent_0_features, # <--- 추가
            self.agent_1_features  # <--- 추가
        )