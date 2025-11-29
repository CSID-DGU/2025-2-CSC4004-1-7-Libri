import sys
import os
import torch
import numpy as np
from typing import Dict, Tuple, Optional, List

class ModelLoader:
    def __init__(self):
        self.marl_predictor = None
        self.model_2 = None
        self.model_3 = None
        
    def load_marl_model(self):
        """MARL 4-agent 모델 로드"""
        try:
            # AI/marl_4agent 경로 추가
            marl_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../AI/marl_4agent"))
            if marl_path not in sys.path:
                sys.path.insert(0, marl_path)
            
            from predictor import get_predictor
            
            # 모델 및 scaler 경로
            model_path = os.path.join(marl_path, "qmix_model.pth")
            scaler_path = os.path.join(marl_path, "scaler.pkl")
            
            # Predictor 로드
            self.marl_predictor = get_predictor(model_path, scaler_path)
            
            print(f"MARL 모델 로드 성공: {model_path}")
            return True
            
        except Exception as e:
            print(f"MARL 모델 로드 실패: {str(e)}")
            print(f"경고: 더미 모드로 동작합니다.")
            return False
    
    def load_model_2(self):
        """MARL 3-agent 모델 로드"""
        try:
            # AI/marl_3agent 경로 추가
            marl3_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../AI/marl_3agent"))
            if marl3_path not in sys.path:
                sys.path.insert(0, marl3_path)
            
            from predictor import get_predictor
            
            # 모델 및 scaler 경로
            model_path = os.path.join(marl3_path, "best_model.pth")
            scaler_path = os.path.join(marl3_path, "scaler.pkl")
            
            # Predictor 로드
            self.model_2 = get_predictor(model_path, scaler_path)
            
            print(f"MARL 3-agent 모델 로드 성공: {model_path}")
            return True
            
        except Exception as e:
            print(f"MARL 3-agent 모델 로드 실패: {str(e)}")
            print(f"경고: 더미 모드로 동작합니다.")
            return False
    
    def load_model_3(self):
        """A2C 모델 로드 (구현 필요)"""
        try:
            # TODO: A2C 모델 구현 후 로드
            # a2c_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../AI/a2c"))
            # ...
            
            self.model_3 = "A2C Model Placeholder"
            print("경고: A2C 모델이 아직 구현되지 않았습니다.")
            return True
        except Exception as e:
            print(f"A2C 모델 로드 실패: {str(e)}")
            return False
    
    def predict_marl(self, features: Dict[str, float]) -> Tuple[str, int, Dict[str, float], str, List[Dict[str, float]]]:
        """MARL 4-agent 모델 예측 (XAI 포함)"""
        if self.marl_predictor is None:
            # 모델이 로드되지 않은 경우 더미 응답
            print("경고: MARL 모델이 로드되지 않아 더미 응답을 반환합니다.")
            signal = "보유"
            vote_sum = 0
            xai_explanation = "모델이 로드되지 않았습니다."
            xai_importance = []
            return signal, vote_sum, features, xai_explanation, xai_importance
        
        try:
            # 실제 모델 예측 (XAI 포함)
            signal, vote_sum, features, xai_explanation, xai_importance = self.marl_predictor.predict(features)
            return signal, vote_sum, features, xai_explanation, xai_importance
            
        except Exception as e:
            print(f"MARL 예측 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시 더미 응답
            signal = "보유"
            vote_sum = 0
            xai_explanation = f"예측 중 오류 발생: {str(e)}"
            xai_importance = []
            return signal, vote_sum, features, xai_explanation, xai_importance
    
    def predict_model_2(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """MARL 3-agent 모델 예측"""
        if self.model_2 is None or isinstance(self.model_2, str):
            # 더미 응답
            print("경고: MARL 3-agent 모델이 로드되지 않아 더미 응답을 반환합니다.")
            signal = "보유"
            confidence = 0.65
            return signal, confidence, features
        
        try:
            # 실제 모델 예측 (XAI 포함)
            signal, vote_sum, features, xai_explanation, xai_importance = self.model_2.predict(features)
            
            # vote_sum을 confidence_score로 변환 (-3~3 -> 0.0~1.0)
            confidence = (abs(vote_sum) / 3.0) * 0.5 + 0.5
            
            return signal, confidence, features
            
        except Exception as e:
            print(f"MARL 3-agent 예측 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시 더미 응답
            signal = "보유"
            confidence = 0.65
            return signal, confidence, features
    
    def predict_model_3(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """A2C 모델 예측"""
        if self.model_3 is None or isinstance(self.model_3, str):
            # 더미 응답
            print("경고: A2C 모델이 로드되지 않아 더미 응답을 반환합니다.")
            signal = "매도"
            confidence = 0.70
            return signal, confidence, features
        
        # TODO: A2C 모델 구현 후 실제 예측 로직 추가
        signal = "매도"
        confidence = 0.70
        
        return signal, confidence, features
    
    def get_model_status(self) -> Dict[str, str]:
        """모델 상태 확인"""
        return {
            "marl_4agent": "available" if self.marl_predictor is not None else "unavailable",
            "model_2": "available" if self.model_2 is not None else "unavailable",
            "model_3": "available" if self.model_3 is not None else "unavailable"
        }

# 전역 모델 로더 인스턴스
model_loader = ModelLoader()
