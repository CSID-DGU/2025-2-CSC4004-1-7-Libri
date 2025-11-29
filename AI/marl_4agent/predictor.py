"""
MARL 4-Agent 모델 예측 모듈
BE에서 호출할 수 있는 간단한 예측 인터페이스 제공
"""

import torch
import numpy as np
import pandas as pd
import pickle
from typing import Dict, Tuple, List
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from config import DEVICE, N_AGENTS, WINDOW_SIZE
from qmix_model import QMIX_Learner
from environment import MARLStockEnv


class MARLPredictor:
    """MARL 모델 예측기"""
    
    def __init__(self, model_path='qmix_model.pth', scaler_path='scaler.pkl'):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.learner = None
        self.scaler_data = None
        self.obs_dims_list = None
        
    def load(self):
        """모델과 scaler 로드"""
        # Scaler 로드
        try:
            with open(self.scaler_path, 'rb') as f:
                self.scaler_data = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Scaler 파일을 찾을 수 없습니다: {self.scaler_path}")
        
        # 모델 차원 설정
        agent_0_cols = self.scaler_data['agent_0_cols']
        agent_1_cols = self.scaler_data['agent_1_cols']
        agent_2_cols = self.scaler_data['agent_2_cols']
        agent_3_cols = self.scaler_data['agent_3_cols']
        
        # 각 에이전트의 observation 차원 계산
        obs_dim_0 = len(agent_0_cols) * WINDOW_SIZE
        obs_dim_1 = len(agent_1_cols) * WINDOW_SIZE
        obs_dim_2 = len(agent_2_cols) * WINDOW_SIZE
        obs_dim_3 = len(agent_3_cols) * WINDOW_SIZE
        
        self.obs_dims_list = [obs_dim_0, obs_dim_1, obs_dim_2, obs_dim_3]
        
        # 상태 차원 계산
        feature_names = self.scaler_data['feature_names']
        state_dim = len(feature_names) * WINDOW_SIZE
        action_dim = 3  # Buy, Hold, Sell
        
        # 모델 로드
        self.learner = QMIX_Learner(self.obs_dims_list, action_dim, state_dim, DEVICE)
        
        try:
            self.learner.load_model(self.model_path)
            return True
        except Exception as e:
            print(f"모델 로드 실패: {e}")
            return False
    
    def predict(self, features: Dict[str, float]) -> Tuple[str, int, Dict[str, float], str, List[Dict[str, float]]]:
        """
        단일 시점 예측 (XAI 포함)
        
        Args:
            features: 기술 지표 딕셔너리
            
        Returns:
            (signal, vote_sum, features, xai_explanation, xai_importance)
            - signal: "매수", "매도", "보유"
            - vote_sum: 투표 합계 (-4 ~ 4)
            - features: 입력 features 그대로 반환
            - xai_explanation: XAI 설명 텍스트
            - xai_importance: 특징 중요도 리스트
        """
        if self.learner is None:
            raise ValueError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        
        # 특징 벡터를 numpy 배열로 변환
        feature_names = self.scaler_data['feature_names']
        feature_vector = np.array([features.get(name, 0.0) for name in feature_names])
        
        # 정규화 (간단 버전 - 실제로는 scaler 사용)
        # 여기서는 이미 정규화된 값이 들어온다고 가정
        
        # WINDOW_SIZE만큼 복제 (단일 시점이므로)
        obs_window = np.tile(feature_vector, (WINDOW_SIZE, 1))
        
        # 각 에이전트별 observation 생성
        agent_0_cols = self.scaler_data['agent_0_cols']
        agent_1_cols = self.scaler_data['agent_1_cols']
        agent_2_cols = self.scaler_data['agent_2_cols']
        agent_3_cols = self.scaler_data['agent_3_cols']
        
        # 컬럼 인덱스 찾기
        agent_0_indices = [feature_names.index(col) for col in agent_0_cols if col in feature_names]
        agent_1_indices = [feature_names.index(col) for col in agent_1_cols if col in feature_names]
        agent_2_indices = [feature_names.index(col) for col in agent_2_cols if col in feature_names]
        agent_3_indices = [feature_names.index(col) for col in agent_3_cols if col in feature_names]
        
        # Observation 딕셔너리 생성
        obs_dict = {
            'agent_0': torch.FloatTensor(obs_window[:, agent_0_indices].flatten()).unsqueeze(0).to(DEVICE),
            'agent_1': torch.FloatTensor(obs_window[:, agent_1_indices].flatten()).unsqueeze(0).to(DEVICE),
            'agent_2': torch.FloatTensor(obs_window[:, agent_2_indices].flatten()).unsqueeze(0).to(DEVICE),
            'agent_3': torch.FloatTensor(obs_window[:, agent_3_indices].flatten()).unsqueeze(0).to(DEVICE)
        }
        
        # 예측 (epsilon=0.0으로 greedy 선택)
        actions_dict = self.learner.select_actions(obs_dict, epsilon=0.0)
        
        # XAI 분석 수행
        agent_analyses = []
        agent_cols_list = [agent_0_cols, agent_1_cols, agent_2_cols, agent_3_cols]
        
        for i in range(N_AGENTS):
            obs_np = obs_dict[f'agent_{i}'].cpu().numpy().flatten()
            agent_feature_names = agent_cols_list[i]
            n_features_agent = len(agent_feature_names)
            
            # get_prediction_with_reason 호출
            action_idx, q_values, importance = self.learner.agents[i].get_prediction_with_reason(
                obs_np,
                agent_feature_names,
                WINDOW_SIZE,
                n_features_agent
            )
            agent_analyses.append((action_idx, q_values, importance))
        
        # 투표 집계
        votes = []
        action_map = {0: "Long", 1: "Hold", 2: "Short"}
        agent_actions = []
        
        for i in range(N_AGENTS):
            action = actions_dict[f'agent_{i}']
            agent_actions.append(action_map[action])
            
            if action == 0:  # Buy
                votes.append(1)
            elif action == 2:  # Sell
                votes.append(-1)
            else:  # Hold
                votes.append(0)
        
        vote_sum = sum(votes)
        
        # 신호 결정 (marl_3agent와 동일한 로직)
        if vote_sum >= 3:
            signal = "적극 매수"
        elif vote_sum > 0:
            signal = "매수"
        elif vote_sum == 0:
            signal = "보유"
        elif vote_sum < 0 and vote_sum > -3:
            signal = "매도"
        elif vote_sum <= -3:
            signal = "적극 매도"
        else:
            signal = "보유"
        
        # XAI 설명 생성
        xai_explanation, xai_importance = self._generate_xai_explanation(signal, agent_analyses)
        
        # 디버그 정보 추가
        features['_agent_actions'] = ', '.join(agent_actions)
        features['_vote_sum'] = vote_sum
        
        return signal, vote_sum, features, xai_explanation, xai_importance
    
    def _generate_xai_explanation(self, signal: str, agent_analyses: List) -> Tuple[str, List[Dict[str, float]]]:
        """XAI 설명 생성"""
        # 모든 에이전트의 중요도 합산
        all_importances = {}
        for _, _, importance_list in agent_analyses:
            for feature, imp in importance_list:
                all_importances[feature] = all_importances.get(feature, 0.0) + imp
        
        # 중요도 순으로 정렬
        sorted_features = sorted(all_importances.items(), key=lambda item: item[1], reverse=True)
        
        # 설명 텍스트 생성
        explanation = f"AI가 '{signal}'을 결정한 주된 이유는 다음과 같습니다.\n\n"
        
        if not sorted_features:
            explanation += "데이터 분석 중입니다."
        else:
            top_feature_1 = sorted_features[0][0]
            explanation += f"  1. '{top_feature_1}' 지표의 최근 움직임을 가장 중요하게 고려했습니다.\n"
            
            if len(sorted_features) > 1:
                top_feature_2 = sorted_features[1][0]
                explanation += f"  2. '{top_feature_2}' 지표가 2순위로 결정에 영향을 미쳤습니다.\n"
            
            if len(sorted_features) > 2:
                top_feature_3 = sorted_features[2][0]
                explanation += f"  3. 마지막으로 '{top_feature_3}' 지표를 참고했습니다.\n"
        
        # 중요도 리스트 (상위 10개)
        importance_list = [
            {"feature": feature, "importance": float(importance)}
            for feature, importance in sorted_features[:10]
        ]
        
        return explanation, importance_list


# 전역 인스턴스 
_predictor_instance = None


def get_predictor(model_path='qmix_model.pth', scaler_path='scaler.pkl') -> MARLPredictor:
    """전역 predictor 인스턴스 반환"""
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = MARLPredictor(model_path, scaler_path)
        _predictor_instance.load()
    
    return _predictor_instance
