# BE/model_loader.py

import os
import sys
import logging
from typing import Dict, Tuple, Any, Optional

import numpy as np
import yaml
import joblib

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    백엔드에서 사용할 투자 모델 로더.

    - 안정형(stable): marl_3agent 기반 (AI/marl_3agent/inference.py::predict_today)
    - 공격형(aggressive): A2C 기반 (AI/a2c_11.29/ 내부 코드)

    각 모델은 아래 공통 인터페이스를 따른다.
      → (signal: str, confidence: float, indicators: Dict[str, float], feature_importance: Dict[str, float])
    """

    def __init__(self) -> None:
        # 안정형 모델 (marl_3agent)
        self.marl3_predict_fn: Optional[Any] = None
        self.marl3_base_dir: Optional[str] = None

        # 공격형 모델 (A2C)
        self.a2c_agent: Optional[Any] = None
        self.a2c_cfg: Optional[dict] = None
        self.a2c_scaler: Optional[Any] = None
        self.a2c_window_size: int = 0
        self.a2c_base_dir: Optional[str] = None

        # 상태 관리
        self.status = {
            "stable": "unavailable",     # marl_3agent
            "aggressive": "unavailable", # A2C
        }

    # ------------------------------------------------------------------
    # 공용 진입점
    # ------------------------------------------------------------------
    def load_models(self) -> None:
        """
        FastAPI startup 시 한 번 호출해서 두 모델을 미리 로딩한다.
        """
        logger.info("[ModelLoader] 모델 로딩 시작")
        self._load_marl3_model()
        self._load_a2c_model()
        logger.info("[ModelLoader] 모델 로딩 완료: %s", self.status)

    def get_model_status(self) -> Dict[str, str]:
        return self.status

    # ------------------------------------------------------------------
    # 1) 안정형 모델: marl_3agent
    # ------------------------------------------------------------------
    def _load_marl3_model(self) -> None:
        """
        AI/marl_3agent/inference.py 안에 있는 `predict_today()`를 불러온다.

        현재 inference.predict_today() 시그니처:
            -> Tuple[str, str, Dict[str, float]]
               (final_signal, explanation, indicators_dict)
        """
        try:
            base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../AI/marl_3agent")
            )
            if base_dir not in sys.path:
                sys.path.append(base_dir)

            from inference import predict_today  # type: ignore

            self.marl3_predict_fn = predict_today
            self.marl3_base_dir = base_dir
            self.status["stable"] = "available"
            logger.info("[MARL3] inference.predict_today 연결 완료")

        except Exception as e:
            logger.exception("[MARL3] 모델 로드 실패: %s", e)
            self.status["stable"] = "unavailable"

    def predict_stable(
        self, symbol: str = "005930"
    ) -> Tuple[str, float, Dict[str, float], Dict[str, float]]:
        """
        안정형 모델(marl_3agent) 예측.

        반환:
            - signal: "BUY" / "SELL" / "HOLD"
            - confidence: 0~1 사이 신뢰도 (간단히 0.7 고정 등으로 처리 가능)
            - indicators: 현재 시점 기술지표 dict
            - feature_importance: 지표 중요도 (GPT 설명용, 현재는 빈 dict)
        """
        if self.status.get("stable") != "available" or self.marl3_predict_fn is None:
            raise RuntimeError("안정형(marl_3agent) 모델이 로드되지 않았습니다.")

        # 실제 inference 함수에 symbol을 넘길지 여부는 네 구현에 맞춰 수정 가능
        result = self.marl3_predict_fn()

        # inference.predict_today() -> (final_signal, explanation, indicators_dict)
        if isinstance(result, tuple) and len(result) == 3:
            signal_raw, explanation, indicators = result
        else:
            logger.warning(
                "[MARL3] 예측 결과 포맷이 예상과 다릅니다: %s", type(result)
            )
            signal_raw, explanation, indicators = "Hold", "", {}

        # "Long"/"Short"/"Hold"/"매수"/"매도"/"보유" → "BUY"/"SELL"/"HOLD"
        mapping = {
            "Long": "BUY",
            "Short": "SELL",
            "Hold": "HOLD",
            "매수": "BUY",
            "매도": "SELL",
            "보유": "HOLD",
        }
        signal = mapping.get(str(signal_raw), "HOLD")

        # 신뢰도는 간단히 0.7 고정 (나중에 Q값 기반으로 바꿀 수 있음)
        confidence = 0.7

        # 타입 정리
        clean_indicators: Dict[str, float] = {}
        for k, v in (indicators or {}).items():
            try:
                clean_indicators[str(k)] = float(v)
            except (TypeError, ValueError):
                continue

        # 현재 inference에서는 중요도를 따로 리턴하지 않으므로 빈 dict
        clean_importance: Dict[str, float] = {}

        return signal, confidence, clean_indicators, clean_importance

    # ------------------------------------------------------------------
    # 2) 공격형 모델: A2C
    # ------------------------------------------------------------------
    def _load_a2c_model(self) -> None:
        try:
            base_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../AI/a2c_11.29")
            )
            if base_dir not in sys.path:
                sys.path.append(base_dir)

            # 1) config.yaml 로드
            cfg_path = os.path.join(base_dir, "config.yaml")
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)

            self.a2c_cfg = cfg
            self.a2c_base_dir = base_dir

            # 2) scaler 로드
            scaler_path = os.path.join(
                base_dir,
                cfg.get("report_dir", "reports") + "/scaler.joblib",
            )
            if os.path.exists(scaler_path):
                self.a2c_scaler = joblib.load(scaler_path)
                logger.info("[A2C] scaler 로드 완료: %s", scaler_path)
            else:
                logger.warning("[A2C] scaler.joblib 이 존재하지 않습니다: %s", scaler_path)

            # 3) A2CAgent 로드
            from ac_model import A2CAgent   # AI/a2c_11.29/ac_model.py
            from data_utils import FEATURES  # AI/a2c_11.29/data_utils.py

            window_size = int(cfg.get("window_size", 5))
            self.a2c_window_size = window_size

            state_dim = len(FEATURES) * window_size + 1
            device = cfg.get("device", "cpu")
            model_path = os.path.join(base_dir, cfg.get("model_path", "a2c_samsung.pt"))

            agent = A2CAgent(
                state_dim=state_dim,
                action_dim=3,
                device=device,
            )
            agent.load(model_path)

            self.a2c_agent = agent
            self.status["aggressive"] = "available"
            logger.info("[A2C] 모델 로드 완료: %s", model_path)

        except Exception as e:
            logger.exception("[A2C] 모델 로드 실패: %s", e)
            self.status["aggressive"] = "unavailable"

    def _run_a2c_prediction(
        self, symbol: str = "005930"
    ) -> Tuple[str, float, Dict[str, float], Dict[str, float]]:
        """
        공격형(A2C) 모델 실제 예측 로직.
        """
        if self.a2c_agent is None or self.a2c_cfg is None:
            raise RuntimeError("공격형(A2C) 모델이 로드되지 않았습니다.")

        try:
            from data_utils import (
                download_data,
                add_indicators,
                build_state,
                FEATURES,
            )

            cfg = self.a2c_cfg
            ticker = cfg.get("ticker", "005930.KS")
            kospi_ticker = cfg.get("kospi_ticker", "^KS11")
            vix_ticker = cfg.get("vix_ticker", "^VIX")
            start_date = cfg.get("start_date", "2010-01-01")
            end_date = cfg.get("end_date", None)

            # 1) 데이터 다운로드 + 지표 추가
            df = download_data(
                ticker=ticker,
                kospi_ticker=kospi_ticker,
                vix_ticker=vix_ticker,
                start_date=start_date,
                end_date=end_date,
            )
            df = add_indicators(df)

            if len(df) < self.a2c_window_size:
                raise RuntimeError("A2C 예측을 위한 데이터가 충분하지 않습니다.")

            window_df = df.iloc[-self.a2c_window_size :]
            indicators = window_df.iloc[-1].to_dict()

            # (선택) scaler 적용
            if self.a2c_scaler is not None:
                window_df[FEATURES] = self.a2c_scaler.transform(window_df[FEATURES])

            # 2) state 구성 (np.ndarray)
            state = build_state(window_df, position_flag=0)

            # 3) 행동 선택 (deterministic=True로 greedy 사용)
            action_idx, _ = self.a2c_agent.act(state, deterministic=True)

            mapping = {0: "BUY", 1: "SELL", 2: "HOLD"}
            signal = mapping.get(int(action_idx), "HOLD")

            confidence = 0.8  # 일단 고정값 (나중에 policy 확률로 바꿀 수 있음)
            feature_importance: Dict[str, float] = {}  # SHAP 붙일 때 채우기

            clean_indicators: Dict[str, float] = {}
            for k, v in indicators.items():
                try:
                    clean_indicators[str(k)] = float(v)
                except (TypeError, ValueError):
                    continue

            return signal, confidence, clean_indicators, feature_importance

        except Exception:
            logger.exception("[A2C] 예측 중 오류 발생")
            raise

    def predict_aggressive(
        self, symbol: str = "005930"
    ) -> Tuple[str, float, Dict[str, float], Dict[str, float]]:
        """
        공격형(A2C) 모델 예측 공용 인터페이스.
        """
        if self.status.get("aggressive") != "available":
            raise RuntimeError("공격형(A2C) 모델이 로드되지 않았습니다.")
        return self._run_a2c_prediction(symbol=symbol)


# 전역 인스턴스 (main.py 에서 import 해서 사용)
model_loader = ModelLoader()