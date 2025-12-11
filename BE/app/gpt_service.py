import os
import time
import json
from typing import List, Dict, Any, Optional
import openai

# 환경변수에서 OPENAI_API_KEY 읽기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def interpret_model_output(
    signal: str,
    xai_features: List[Dict[str, Any]],  # [핵심 수정] 리스트 형태의 xai_features를 받습니다
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    GPT API를 호출하여 모델의 예측 결과(Top-3 지표 포함)를 금융 관점에서 해석합니다.
    
    Args:
        signal (str): "매수", "매도", "관망" 등
        xai_features (List[Dict]): AI가 선정한 중요 지표 리스트 (Top 3)
            Example: [{"base": "MACD", "value": 3.05, "description": "..."}, ...]

    Returns:
        Dict: {
            "feature_explanations": [ "지표1 설명...", "지표2 설명...", "지표3 설명..." ],
            "global_explanation": "종합 투자 의견..."
        }
    """

    # 1. API 키 예외 처리
    if not OPENAI_API_KEY:
        return {
            "feature_explanations": [
                "GPT API 키가 설정되지 않아 분석할 수 없습니다." 
                for _ in xai_features
            ],
            "global_explanation": "OpenAI API Key가 설정되지 않았습니다."
        }

    # 2. 프롬프트에 들어갈 지표 정보 텍스트 생성
    # 예: "1. MACD (추세 지표): 값 3.05"
    features_desc_str = ""
    for idx, feat in enumerate(xai_features):
        name = feat.get("base") or feat.get("name") or "Unknown"
        val = feat.get("value", 0.0)
        desc = feat.get("description", "")
        # 방향성 정보가 있다면 포함 (지지/저항 등)
        direction = feat.get("direction", "")
        
        features_desc_str += f"{idx+1}. {name} ({desc}): 값 {val:.4f} "
        if direction:
            features_desc_str += f"({direction}) "
        features_desc_str += "\n"

    # 3. GPT 프롬프트 작성 (JSON 응답 강제)
    prompt = f"""
당신은 베테랑 주식 투자 애널리스트입니다.
AI 모델이 현재 '{signal}' 포지션을 제안했습니다.
이 판단에 결정적인 영향을 미친 Top 3 지표는 다음과 같습니다:

[Top 3 영향 지표]
{features_desc_str}

[요청 사항]
1. 위 3가지 지표 각각에 대해, **"해당 지표의 값이 왜 '{signal}' 판단을 지지하는지"** 금융 공학적 관점에서 1문장으로 구체적으로 설명해주세요.
   (예시: "RSI가 30 미만으로 과매도 상태여서 반등 가능성이 높습니다.")
2. 이 지표들을 종합하여 투자자에게 전할 2~3문장의 **최종 코멘트(explanation)**를 작성해주세요.

[응답 형식 (JSON)]
반드시 아래 JSON 포맷만 출력하세요. 마크다운이나 다른 텍스트를 포함하지 마세요.
{{
  "feature_explanations": [
    "첫 번째 지표에 대한 상세 해석",
    "두 번째 지표에 대한 상세 해석",
    "세 번째 지표에 대한 상세 해석"
  ],
  "global_explanation": "종합적인 투자 의견 코멘트"
}}
"""

    last_error = None

    for attempt in range(max_retries):
        try:
            # GPT-4o-mini 호출 (JSON 모드 사용)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful financial assistant. Respond only in JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=600,
                temperature=0.7,
                response_format={"type": "json_object"} # 중요: JSON 응답 강제
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            
            # 응답 필드 검증
            if "feature_explanations" in result and "global_explanation" in result:
                # 지표 개수만큼 리스트 길이가 안 맞을 경우 안전장치
                expls = result["feature_explanations"]
                if len(expls) < len(xai_features):
                    expls.extend(["추가 설명이 없습니다."] * (len(xai_features) - len(expls)))
                
                return result

        except Exception as e:
            last_error = e
            time.sleep(1) # 잠시 대기 후 재시도

    # 3번 시도 실패 시 기본 문구 반환
    return {
        "feature_explanations": [
            f"{f.get('base', '지표')}가 예측에 중요한 영향을 미쳤습니다. (분석 실패)" 
            for f in xai_features
        ],
        "global_explanation": f"AI 모델 분석 결과 {signal} 의견을 제시합니다. (GPT 응답 실패: {str(last_error)})"
    }