"""
AI Trading Backend API 테스트 스크립트

실행 방법:
    1. 서버 실행: python main.py (다른 터미널에서)
    2. 테스트 실행: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = ""  # .env 파일의 API_KEY와 동일하게 설정 (비어있으면 인증 비활성화)

headers = {
    "Content-Type": "application/json",
}
if API_KEY:
    headers["X-API-Key"] = API_KEY

def test_health():
    """헬스 체크 테스트"""
    print("\n=== Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_model_status():
    """모델 상태 확인 테스트"""
    print("\n=== Model Status ===")
    response = requests.get(f"{BASE_URL}/models/status", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_model_list():
    """모델 목록 조회 테스트 (FE 선택 UI용)"""
    print("\n=== Model List (for FE selection) ===")
    response = requests.get(f"{BASE_URL}/models/list", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_marl_prediction():
    """MARL (안정형) 모델 예측 테스트"""
    print("\n=== MARL 3-Agent (안정형) Prediction ===")
    data = {
        "symbol": "005930",
        "features": {
            "SMA20": 70000.0,
            "MACD": 500.0,
            "MACD_Signal": 450.0,
            "RSI": 65.0,
            "Stoch_K": 70.0,
            "Stoch_D": 68.0,
            "ATR": 1500.0,
            "Bollinger_B": 0.8,
            "VIX": 15.0,
            "ROA": 0.05,
            "DebtRatio": 0.3,
            "AnalystRating": 4.2
        }
    }
    response = requests.post(f"{BASE_URL}/predict/marl", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Signal: {result.get('signal')}")
        print(f"Confidence: {result.get('confidence_score'):.2%}")
        print(f"XAI Explanation: {result.get('xai_explanation')}")
    else:
        print(f"Error: {response.text}")

def test_a2c_prediction():
    """A2C (공격형) 모델 예측 테스트"""
    print("\n=== A2C (공격형) Prediction ===")
    data = {
        "symbol": "005930",
        "features": {
            "RSI": 25.0,
            "MACD": 150.0,
            "MACD_Signal": 50.0,
            "Stoch_K": 18.0,
            "VIX": 22.0
        }
    }
    response = requests.post(f"{BASE_URL}/predict/a2c", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Signal: {result.get('signal')}")
        print(f"Confidence: {result.get('confidence_score'):.2%}")
    else:
        print(f"Error: {response.text}")

def test_portfolio_creation():
    """포트폴리오 생성 테스트"""
    print("\n=== Portfolio Creation ===")
    data = {
        "portfolio_id": "test_user_001",
        "initial_capital": 10000000.0
    }
    response = requests.post(f"{BASE_URL}/portfolio/capital", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_portfolio_get():
    """포트폴리오 조회 테스트"""
    print("\n=== Portfolio Get ===")
    portfolio_id = "test_user_001"
    response = requests.get(f"{BASE_URL}/portfolio/{portfolio_id}", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_investment_record():
    """투자 내역 기록 테스트"""
    print("\n=== Investment Record ===")
    params = {
        "portfolio_id": "test_user_001",
        "model_type": "marl_3agent",
        "signal": "매수",
        "entry_price": 70000.0,
        "shares": 100,
        "portfolio_value": 10500000.0,
        "pnl": 500000.0,
        "confidence_score": 0.85,
        "gpt_explanation": "RSI와 MACD 지표가 상승 추세를 보이고 있어 매수 신호를 생성했습니다."
    }
    response = requests.post(f"{BASE_URL}/investment/record", headers=headers, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_investment_history():
    """투자 내역 조회 테스트"""
    print("\n=== Investment History ===")
    params = {
        "portfolio_id": "test_user_001",
        "page": 1,
        "page_size": 10
    }
    response = requests.get(f"{BASE_URL}/investment/history", headers=headers, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_performance_metrics():
    """성과 지표 조회 테스트"""
    print("\n=== Performance Metrics ===")
    params = {
        "portfolio_id": "test_user_001"
    }
    response = requests.get(f"{BASE_URL}/investment/metrics", headers=headers, params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    print("=" * 60)
    print("AI Trading Backend API 테스트")
    print("=" * 60)
    print("\n사용 가능한 모델:")
    print("  - MARL 3-Agent (안정형): /predict/marl")
    print("  - A2C (공격형): /predict/a2c")
    
    try:
        # 기본 테스트
        test_health()
        test_model_status()
        test_model_list()
        
        # 모델 예측 테스트
        test_marl_prediction()
        test_a2c_prediction()
        
        # 포트폴리오 테스트
        test_portfolio_creation()
        test_portfolio_get()
        
        # 투자 내역 테스트
        test_investment_record()
        test_investment_history()
        test_performance_metrics()
        
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 오류: 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: python main.py")
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
