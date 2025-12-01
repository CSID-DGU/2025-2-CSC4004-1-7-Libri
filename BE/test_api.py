"""
간단한 API 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"  # .env 파일의 API_KEY와 동일하게 설정

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

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
    """MARL 모델 예측 테스트"""
    print("\n=== MARL Prediction ===")
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
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_model2_prediction():
    """Model 2 예측 테스트"""
    print("\n=== Model 2 Prediction ===")
    data = {
        "symbol": "005930",
        "features": {
            "SMA20": 70000.0,
            "MACD": 500.0,
            "RSI": 65.0
        }
    }
    response = requests.post(f"{BASE_URL}/predict/model2", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_model3_prediction():
    """Model 3 예측 테스트"""
    print("\n=== Model 3 Prediction ===")
    data = {
        "symbol": "005930",
        "features": {
            "SMA20": 70000.0,
            "MACD": 500.0,
            "RSI": 65.0
        }
    }
    response = requests.post(f"{BASE_URL}/predict/model3", headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

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
        "model_type": "marl_4agent",
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
    print("AI Trading Backend API 테스트")
    print("=" * 50)
    
    try:
        test_health()
        test_model_status()
        test_model_list()
        test_portfolio_creation()
        test_portfolio_get()
        
        # 각 모델 테스트
        test_marl_prediction()
        test_model2_prediction()
        test_model3_prediction()
        
        test_investment_record()
        test_investment_history()
        test_performance_metrics()
        
        print("\n" + "=" * 50)
        print("모든 테스트 완료!")
        
    except requests.exceptions.ConnectionError:
        print("\n오류: 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: python main.py")
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
