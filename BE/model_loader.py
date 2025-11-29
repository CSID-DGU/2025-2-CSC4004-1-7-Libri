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
        """두 번째 모델 로드 (구현 필요)"""
        try:
            # TODO: 실제 모델 2 로드 로직 구현
            self.model_2 = "Model 2 Placeholder"
            return True
        except Exception as e:
            print(f"Model 2 로드 실패: {str(e)}")
            return False
    
    def load_model_3(self):
        """세 번째 모델 로드 (구현 필요)"""
        try:
            # TODO: 실제 모델 3 로드 로직 구현
            self.model_3 = "Model 3 Placeholder"
            return True
        except Exception as e:
            print(f"Model 3 로드 실패: {str(e)}")
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
        """Model 2 예측"""
        if self.model_2 is None:
            raise ValueError("Model 2가 로드되지 않았습니다.")
        
        # TODO: 실제 예측 로직 구현
        signal = "보유"
        confidence = 0.65
        
        return signal, confidence, features
    
    def predict_model_3(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """Model 3 예측"""
        if self.model_3 is None:
            raise ValueError("Model 3가 로드되지 않았습니다.")
        
        # TODO: 실제 예측 로직 구현
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
