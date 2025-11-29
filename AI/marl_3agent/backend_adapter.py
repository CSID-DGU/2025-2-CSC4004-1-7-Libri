# AI/marl_3agent/backend_adapter.py

from typing import Dict, Any
from datetime import datetime

# ⚠️ 같은 폴더 안의 inference.py 를 사용한다고 가정
from inference import predict_today as _raw_predict_today

def stable_marl3_predict() -> Dict[str, Any]:
    """
    BE에서 바로 쓸 수 있는 '안정형(MARL3)' 예측 래퍼.

    - 내부적으로는 inference.predict_today() 로직을 그대로 사용하되,
      최종 결과를 dict 형태로 만들어서 반환한다.
    """
    # -------------------------------------------------------
    # 1) inference.predict_today() 가 "최종 신호, 설명, 지표"를
    #    반환하도록 네가 먼저 살짝 고쳐두어야 한다.
    #
    #    예: inference.py 안 predict_today() 를 이런 식으로 수정
    #
    #    def predict_today(return_result: bool = False):
    #        ...
    #        # joint_action, final_signal, explanation, current_indicators 계산 완료 후
    #        result = {
    #            "final_signal": final_signal,         # 예: "매수", "보유", "매도" 등
    #            "explanation": explanation,           # 긴 한국어 설명 문자열
    #            "current_indicators": current_indicators.to_dict(),  # 마지막 행 지표들
    #            "joint_action": joint_action,         # [a0, a1, a2]
    #        }
    #
    #        if return_result:
    #            return result
    #        else:
    #            print_ui_output(... 기존 print 로직 ...)
    #
    #    if __name__ == "__main__":
    #        predict_today(return_result=False)
    # -------------------------------------------------------

    raw = _raw_predict_today(return_result=True)

    final_signal = raw.get("final_signal", "보유")
    explanation = raw.get("explanation", "")
    indicators = raw.get("current_indicators", {})
    joint_action = raw.get("joint_action", [])

    # BE에서 공통으로 쓰기 좋은 포맷으로 변환
    result: Dict[str, Any] = {
        "model_type": "stable_marl3",
        "signal": final_signal,          # "매수" / "보유" / "매도" / "적극 매수" ...
        "confidence_score": 0.0,         # 원하면 나중에 Q값 기반으로 채워도 됨
        "technical_indicators": indicators,
        "raw_actions": joint_action,     # [agent0_action, agent1_action, agent2_action]
        "explanation": explanation,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    return result