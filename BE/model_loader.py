import sys
import os
import torch
import numpy as np
import pickle
from typing import Dict, Tuple, Optional, List

class ModelLoader:
    def __init__(self):
        self.marl_3_model = None  # marl_3agent
        self.a2c_model = None  # a2c
        
        # 각 모델의 스케일러를 미리 로드
        self.marl_3_scaler = None
        self.a2c_scaler = None
    
    def load_marl_3_model(self):
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
            
            # Scaler 미리 로드
            with open(scaler_path, 'rb') as f:
                self.marl_3_scaler = pickle.load(f)
            
            # Predictor 로드
            self.marl_3_model = get_predictor(model_path, scaler_path)
            
            print(f"MARL 3-agent 모델 및 스케일러 로드 성공: {model_path}")
            return True
            
        except Exception as e:
            print(f"MARL 3-agent 모델 로드 실패: {str(e)}")
            print(f"경고: 더미 모드로 동작합니다.")
            return False
    
    def load_a2c_model(self):
        """A2C 모델 로드"""
        try:
            import joblib
            
            # AI/a2c_file 경로
            a2c_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../AI/a2c_file"))
            
            # Scaler 로드 (a2c는 joblib 사용)
            scaler_path = os.path.join(a2c_path, "report", "scaler.joblib")
            self.a2c_scaler = joblib.load(scaler_path)
            
            # TODO: A2C predictor 구현 필요
            self.a2c_model = "A2C Model Loaded"
            print(f"A2C 스케일러 로드 성공: {scaler_path}")
            print("경고: A2C predictor는 아직 구현되지 않았습니다.")
            return True
            
        except Exception as e:
            print(f"A2C 모델 로드 실패: {str(e)}")
            print(f"경고: 더미 모드로 동작합니다.")
            return False
    
    def predict_marl_3(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """MARL 3-agent 모델 예측"""
        if self.marl_3_model is None or isinstance(self.marl_3_model, str):
            # 더미 응답
            print("경고: MARL 3-agent 모델이 로드되지 않아 더미 응답을 반환합니다.")
            signal = "보유"
            confidence = 0.65
            return signal, confidence, features
        
        try:
            # BE에서 미리 정규화 수행
            normalized_features = self.normalize_features(features, "marl_3")
            
            # 실제 모델 예측 (이미 정규화된 데이터 전달)
            signal, vote_sum, _, xai_explanation, xai_importance = self.marl_3_model.predict(normalized_features)
            
            # vote_sum을 confidence_score로 변환 (-3~3 -> 0.0~1.0)
            confidence = (abs(vote_sum) / 3.0) * 0.5 + 0.5
            
            # 원본 features 반환
            return signal, confidence, features
            
        except Exception as e:
            print(f"MARL 3-agent 예측 중 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            # 오류 발생 시 더미 응답
            signal = "보유"
            confidence = 0.65
            return signal, confidence, features
    
    def predict_a2c(self, features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
        """A2C 모델 예측"""
        if self.a2c_model is None or isinstance(self.a2c_model, str):
            # 더미 응답
            print("경고: A2C 모델이 로드되지 않아 더미 응답을 반환합니다.")
            signal = "매도"
            confidence = 0.70
            return signal, confidence, features
        
        try:
            # BE에서 미리 정규화 수행
            normalized_features = self.normalize_features(features, "a2c")
            
            # TODO: A2C predictor 구현 후 실제 예측 로직 추가
            # signal, confidence = self.a2c_model.predict(normalized_features)
            
            signal = "매도"
            confidence = 0.70
            
            # 원본 features 반환
            return signal, confidence, features
            
        except Exception as e:
            print(f"A2C 예측 중 오류: {str(e)}")
            signal = "매도"
            confidence = 0.70
            return signal, confidence, features
    
    def normalize_features(self, features: Dict[str, float], model_type: str) -> Dict[str, float]:
        """
        모델별 스케일러를 사용해 features를 정규화
        
        Args:
            features: 원본 features
            model_type: "marl_3", "a2c"
            
        Returns:
            정규화된 features
        """
        # 스케일러 선택
        if model_type == "marl_3":
            scaler_data = self.marl_3_scaler
        elif model_type == "a2c":
            scaler_data = self.a2c_scaler
        else:
            return features  # 스케일러 없으면 그대로 반환
        
        if scaler_data is None:
            return features
        
        try:
            # MARL 3-agent는 pickle로 저장된 scaler_data 딕셔너리 구조
            if model_type == "marl_3":
                feature_names = scaler_data.get('feature_names', list(features.keys()))
                scaler = scaler_data.get('scaler')
                
                if scaler is None:
                    return features
                
                # feature_names 순서대로 벡터 생성
                feature_vector = np.array([features.get(name, 0.0) for name in feature_names])
                
                # 정규화
                normalized_vector = scaler.transform(feature_vector.reshape(1, -1)).flatten()
                
                # 다시 딕셔너리로 변환
                normalized_features = {name: float(val) for name, val in zip(feature_names, normalized_vector)}
                
            # A2C는 joblib로 저장된 scaler 객체
            elif model_type == "a2c":
                feature_names = list(features.keys())
                feature_vector = np.array([features.get(name, 0.0) for name in feature_names])
                
                # 정규화
                normalized_vector = scaler_data.transform(feature_vector.reshape(1, -1)).flatten()
                
                # 다시 딕셔너리로 변환
                normalized_features = {name: float(val) for name, val in zip(feature_names, normalized_vector)}
            
            return normalized_features
            
        except Exception as e:
            print(f"정규화 중 오류 ({model_type}): {str(e)}")
            return features  # 오류 시 원본 반환
    
    def get_model_status(self) -> Dict[str, str]:
        """모델 상태 확인"""
        return {
            "marl_3agent": "available" if self.marl_3_model is not None else "unavailable",
            "a2c": "available" if self.a2c_model is not None else "unavailable"
        }

# 전역 모델 로더 인스턴스
model_loader = ModelLoader()
