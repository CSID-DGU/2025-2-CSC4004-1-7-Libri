import openai
import asyncio
from typing import Dict
import config

openai.api_key = config.OPENAI_API_KEY

async def interpret_model_output(
    signal: str,
    technical_indicators: Dict[str, float],
    feature_importance: Dict[str, float] = None,
    max_retries: int = 3
) -> str:
    """
    GPT API를 호출하여 모델 출력을 자연어로 해석
    """
    if not config.OPENAI_API_KEY:
        return "GPT API 키가 설정되지 않았습니다."
    
    # 프롬프트 구성
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

    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                openai.chat.completions.create,
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
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
            else:
                print(f"GPT API 호출 실패: {str(e)}")
                return f"AI 해석을 생성할 수 없습니다. (오류: {str(e)})"
    
    return "AI 해석을 생성할 수 없습니다."
