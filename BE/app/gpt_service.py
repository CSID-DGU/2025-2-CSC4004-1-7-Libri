# app/gpt_service.py

import os
import time
from typing import Dict, Optional

import openai

# 환경변수에서 OPENAI_API_KEY 읽기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def interpret_model_output(
    signal: str,
    technical_indicators: Dict[str, float],
    feature_importance: Optional[Dict[str, float]] = None,
    max_retries: int = 3,
) -> str:
    """
    GPT API를 호출하여 모델 출력을 자연어로 해석하는 동기 함수.

    - signal: "buy" / "sell" / "hold" 등 모델 액션
    - technical_indicators: 기술적 지표들 {이름: 값}
    - feature_importance: (선택) XAI 중요도 {이름: 중요도}
    """

    if not OPENAI_API_KEY:
        # 키가 없어도 서버 전체가 터지지 않도록 안전하게 처리
        return "OPENAI_API_KEY가 설정되어 있지 않아 GPT 해석을 생성할 수 없습니다."

    indicators_text = "\n".join(
        [f"- {k}: {v:.2f}" for k, v in technical_indicators.items()]
    )

    importance_text = ""
    if feature_importance:
        importance_text = "\n주요 영향 지표:\n" + "\n".join(
            [
                f"- {k}: {v:.4f}"
                for k, v in sorted(
                    feature_importance.items(), key=lambda x: x[1], reverse=True
                )[:5]
            ]
        )

    prompt = f"""
당신은 주식 투자 AI 분석가입니다. 다음 AI 모델의 예측 결과를 일반 투자자가 이해하기 쉽게 설명해주세요.

AI 예측 신호: {signal}

현재 기술적 지표:
{indicators_text}
{importance_text}

위 정보를 바탕으로 AI가 왜 이런 결정을 내렸는지 3~4문장으로 설명해주세요. 
투자자가 이해하기 쉽게, 과도한 투자 권유 없이 중립적인 어투로 작성해주세요.
"""

    last_error = None

    for attempt in range(max_retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # 팀에서 쓰는 모델명으로 맞추면 됨
                messages=[
                    {"role": "system", "content": "당신은 주식 투자 분석 전문가입니다."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            last_error = e
            # 지수 백오프
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                break

    return f"AI 해석을 생성할 수 없습니다. (오류: {last_error})"