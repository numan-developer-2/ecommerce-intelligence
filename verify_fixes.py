
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.demand_prediction import DemandPredictor
from src.price_forecast import PriceForecaster
from src.config import get_latest_cleaned_file

def verify_fixes():
    print("="*60)
    print("[*] VERIFYING FIXES")
    print("="*60)
    
    # 1. Verify Price Forecast Fix
    print("\n[1] Testing Price Forecast (Single Record fix)...")
    try:
        forecaster = PriceForecaster()
        
        # Create dummy data with just 1 record to test the fix
        dummy_df = pd.DataFrame({
            'product_id': ['test_product_123'],
            'price': [1000],
            'scraped_at': [pd.Timestamp.now()],
            'title': ['Test Product'],
            'original_price': [1200],
            'discount_pct': [20],
            'rating': [4.5],
            'review_count': [100]
        })
        
        # Override internal df for testing
        forecaster.df = dummy_df
        
        # Try to forecast
        summary = forecaster.get_forecast_summary('test_product_123', days=7)
        
        if summary and summary['predictions']:
            print("   [OK] Price Forecast working for single record!")
            print(f"      Trend: {summary['trend']}")
            print(f"      Predictions generated: {len(summary['predictions'])}")
        else:
            print("   [FAIL] Price Forecast returned None / Failed")
            
    except Exception as e:
        print(f"   [FAIL] Price Forecast Crashed: {e}")
        import traceback
        traceback.print_exc()

    # 2. Verify Demand Prediction Fix
    print("\n[2] Testing Demand Prediction (Feature mismatch fix)...")
    try:
        # We need actual trained model for this, so we'll try to load data
        predictor = DemandPredictor()
        
        data_file = get_latest_cleaned_file()
        if not data_file:
            print("   [WARN] No cleaned data file found to train model. Skipping deep test.")
        else:
            predictor.load_data()
            predictor.create_synthetic_demand()
            predictor.engineer_features()
            predictor.train_model()
            
            # Create a sample product input
            sample_product = {
                'price': 5000,
                'rating': 4.5,
                'review_count': 50,
                'discount_pct': 10,
                # Intentionally missing some features to test robustness
            }
            
            result = predictor.predict_demand(sample_product)
            
            if result and 'demand_score' in result:
                print("   [OK] Demand Prediction working!")
                print(f"      Score: {result['demand_score']}")
            else:
                print("   [FAIL] Demand Prediction returned invalid result")

    except Exception as e:
        print(f"   [FAIL] Demand Prediction Crashed: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)

if __name__ == "__main__":
    verify_fixes()
