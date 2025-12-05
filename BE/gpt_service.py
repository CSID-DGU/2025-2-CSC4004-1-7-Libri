from typing import Dict, Optional
import os

def interpret_model_output(
    signal: str,
    technical_indicators: Dict[str, float],
    feature_importance: Optional[Dict[str, float]] = None,
) -> str:
    """
    모델 출력을 자연어로 해석 (GPT 없이 규칙 기반)
    
    OpenAI API 키가 설정되어 있으면 GPT를 사용하고,
    없으면 규칙 기반 설명을 반환합니다.
    """
    # OpenAI API 키 확인
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    if openai_key:
        try:
            # OpenAI 사용 시도
            import openai
            openai.api_key = openai_key
            
            indicators_text = "\n".join([f"- {k}: {v:.2f}" for k, v in technical_indicators.items()])
            
            importance_text = ""
            if feature_importance:
                importance_text = "\n주요 영향 지표:\n" + "\n".join(
                    [f"- {k}: {v:.4f}" for k, v in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]]
                )
            
            prompt = f"""당신은 주식 투자 AI 분석가입니다. 다음 AI 모델의 예측 결과를 일반 투자자가 이해하기 쉽게 설명해주세요.

AI 예측 신호: {signal}

현재 기술적 지표:
{indicators_text}
{importance_text}

위 정보를 바탕으로 AI가 왜 이런 결정을 내렸는지 3-4문장으로 설명해주세요. 투자자가 이해하기 쉽게 작성해주세요."""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 주식 투자 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"GPT API 호출 실패, 규칙 기반 설명 사용: {str(e)}")
    
    # 규칙 기반 설명 (GPT 없을 때)
    signal_upper = signal.upper()
    
    if signal_upper == "BUY":
        return (
            "AI 모델이 현재 시장 상황을 분석한 결과, 매수 시점으로 판단했습니다. "
            "기술적 지표들이 상승 추세를 나타내고 있으며, 단기적으로 긍정적인 수익을 기대할 수 있습니다. "
            "다만 시장 변동성을 고려하여 신중한 접근이 필요합니다."
        )
    elif signal_upper == "SELL":
        return (
            "AI 모델이 현재 시장 상황을 분석한 결과, 매도 시점으로 판단했습니다. "
            "기술적 지표들이 하락 추세를 나타내고 있으며, 리스크 관리 차원에서 포지션 정리를 권장합니다. "
            "시장 상황에 대한 신중한 접근과 경계를 유지하여 변동성에 대비하는 것이 중요합니다."
        )
    else:  # HOLD
        return (
            "AI 모델이 현재 시장 상황을 분석한 결과, 관망 전략이 적절하다고 판단했습니다. "
            "현재 기술적 지표들이 명확한 방향성을 보이지 않고 있어, "
            "추가적인 시장 신호를 기다리는 것이 안전한 선택입니다."
        )
