import sys
import os

# Add BE directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'BE')))

from app.ai_wrapper import a2c_wrapper, marl_wrapper

def test_a2c():
    print("Testing A2C...")
    try:
        # Test History
        print("  Fetching history...")
        history = a2c_wrapper.get_historical_signals("2025-10-01")
        print(f"  History length: {len(history)}")
        if history:
            print(f"  First item: {history[0]}")
            
        # Test Prediction
        print("  Predicting today...")
        prediction = a2c_wrapper.predict_today()
        print(f"  Prediction: {prediction}")
        
    except Exception as e:
        print(f"  A2C Error: {e}")
        import traceback
        traceback.print_exc()

def test_marl():
    print("\nTesting MARL...")
    try:
        # Test History
        print("  Fetching history...")
        history = marl_wrapper.get_historical_signals("2025-10-01")
        print(f"  History length: {len(history)}")
        if history:
            print(f"  First item: {history[0]}")
            
        # Test Prediction
        print("  Predicting today...")
        prediction = marl_wrapper.predict_today()
        print(f"  Prediction: {prediction}")
        
    except Exception as e:
        print(f"  MARL Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_a2c()
    test_marl()
