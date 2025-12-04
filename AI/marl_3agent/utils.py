import numpy as np

def convert_joint_action_to_signal(joint_action, action_map):
    """3개 에이전트의 행동을 종합하여 최종 매매 신호 생성"""
    action_to_score = {"Long": 1, "Hold": 0, "Short": -1}
    score = sum(action_to_score[action_map[a]] for a in joint_action)
    
    if score >= 3: return "적극 매수"
    elif score > 0: return "매수"
    elif score == 0: return "보유"
    elif score < 0 and score > -3: return "매도"
    elif score <= -3: return "적극 매도"
    return "보유"

def get_top_features_marl(agent_analyses, top_k=3):
    """MARL 에이전트들의 분석 결과를 종합하여 Top K 중요 지표 추출"""
    all_importances = {}
    for _, _, importance_list in agent_analyses:
        for feature, imp in importance_list:
            all_importances[feature] = all_importances.get(feature, 0.0) + imp
            
    sorted_features = sorted(all_importances.items(), key=lambda item: item[1], reverse=True)
    
    top_features = []
    for feature, imp in sorted_features[:top_k]:
        top_features.append({
            "name": feature,
            "importance": float(imp),
            "description": f"{feature} 지표" # 필요시 상세 설명 매핑 추가 가능
        })
        
    return top_features

def generate_ai_explanation(final_signal, agent_analyses):
    """AI 판단 근거(XAI) 텍스트 생성"""
    top_features = get_top_features_marl(agent_analyses)
    
    explanation = f"AI가 '{final_signal}'을 결정한 주된 이유는 다음과 같습니다.\n\n"
    if not top_features:
        return explanation + "데이터 분석 중입니다."
        
    if len(top_features) > 0:
        explanation += f"  1. '{top_features[0]['name']}' 지표의 최근 움직임을 가장 중요하게 고려했습니다.\n"
    
    if len(top_features) > 1:
        explanation += f"  2. '{top_features[1]['name']}' 지표가 2순위로 결정에 영향을 미쳤습니다.\n"
        
    if len(top_features) > 2:
        explanation += f"  3. 마지막으로 '{top_features[2]['name']}' 지표를 참고했습니다.\n"
        
    return explanation

def print_ui_output(final_signal, ai_explanation, current_indicators, q_total_grid, best_q_total_value, action_names):
    """콘솔에 최종 결과 출력"""
    print("\n\n=============================================")
    print("      [ 📱 리브리 AI 분석 결과 ]")
    print("=============================================")
    print("\n--- 1. AI 최종 신호 ---")
    print(f"    {final_signal}")
    print(f"    (예상 팀 Q-Value: {best_q_total_value:.4f})")
    print("\n--- 2. AI 설명 ---")
    print(ai_explanation)
    print("\n--- 3. 주요 지표 현황 ---")
    for k, v in current_indicators.items():
        if k in ['SMA20', 'RSI', 'MACD', 'VIX']: # 주요 지표만 간략 출력
            print(f"    - {k:<10}: {v:.2f}")
    print("=============================================")