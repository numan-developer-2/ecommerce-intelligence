"""
Price Forecasting Model
Using Prophet for time series prediction
Easy to switch to ARIMA if needed
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path
import joblib
import warnings
warnings.filterwarnings('ignore')

# Prophet import (install: pip install prophet)
try:
    from prophet import Prophet
except ImportError:
    print("⚠️ Prophet not installed. Run: pip install prophet")

from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceForecaster:
    """
    Time series forecasting for product prices
    Supports multiple products
    """

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or get_latest_cleaned_file()
        self.df = None
        self.models = {}  # Store models for each product
        self.forecasts = {}

    def load_data(self):
        """Load cleaned data"""
        logger.info(f"Loading data from {self.data_file}")
        self.df = pd.read_csv(self.data_file)

        # Convert date column
        if 'scraped_at' in self.df.columns:
            self.df['scraped_at'] = pd.to_datetime(self.df['scraped_at'])

        logger.info(f"Loaded {len(self.df)} records")
        return self.df

    def prepare_time_series(self, product_id: str) -> pd.DataFrame:
        """
        Prepare data for Prophet model
        Prophet requires: ds (date) and y (value) columns
        """
        # Filter product data
        if self.df is None:
             # Handle case where self.df is not loaded yet
             product_df = pd.DataFrame()
        else:
            product_df = self.df[self.df['product_id'] == product_id].copy()

        if len(product_df) == 0:
            logger.warning(f"Product {product_id} not found in DB. Generating VIRTUAL history for demo.")
            # Virtual Product Mode: Generate completely synthetic data
            # Use a deterministic hash of ID to pick a consistent 'random' price
            import hashlib
            seed = int(hashlib.sha256(product_id.encode('utf-8')).hexdigest(), 16) % 10000
            current_price = 1000 + seed  # Price between 1000 and 11000
            current_date = pd.Timestamp.now()
            
            synthetic_data = []
            import random
            random.seed(seed) # Consistent randomness for same product name
            
            base_price = current_price
            for i in range(1, 15):
                change = random.uniform(-0.03, 0.03) 
                simulated_price = base_price * (1 + change)
                synthetic_data.append({
                    'scraped_at': current_date - pd.Timedelta(days=i),
                    'price': round(simulated_price, 2)
                })
                base_price = simulated_price
                
            product_df = pd.DataFrame(synthetic_data)
            product_df['product_id'] = product_id

        elif len(product_df) < 2:
            logger.warning(f"Not enough data for {product_id}. generating synthetic history for demo purposes.")
            # Create synthetic history for single-point products to allow forecasting
            if len(product_df) == 1:
                current_price = product_df.iloc[0]['price']
                current_date = pd.to_datetime(product_df.iloc[0]['scraped_at'])
                
                # Generate 14 days of realistic synthetic history
                # Add randomness so every graph looks different
                import random
                
                synthetic_data = []
                base_price = current_price
                
                # Determine volatility based on price (higher price = less volatile usually)
                volatility = 0.02 if base_price > 5000 else 0.05
                
                # Add a random trend (-1% to +1%)
                trend_factor = random.uniform(-0.01, 0.01)
                
                for i in range(1, 15):
                    # Create variation
                    change = random.uniform(-volatility, volatility) + trend_factor
                    simulated_price = base_price * (1 + change)
                    
                    # Ensure price doesn't go below 0
                    simulated_price = max(simulated_price, 100)
                    
                    synthetic_data.append({
                        'scraped_at': current_date - pd.Timedelta(days=i),
                        'price': round(simulated_price, 2)
                    })
                    
                    # Update base slightly for next day to create a path
                    base_price = simulated_price
                
                synthetic_df = pd.DataFrame(synthetic_data)
                product_df = pd.concat([synthetic_df, product_df], ignore_index=True)
                
                # Sort ensuring newest is last
                if 'scraped_at' in product_df.columns:
                     product_df['scraped_at'] = pd.to_datetime(product_df['scraped_at'])
                     product_df = product_df.sort_values('scraped_at')
            else:
                 return None

        # Create Prophet format
        ts_df = pd.DataFrame({
            'ds': product_df['scraped_at'],
            'y': product_df['price']
        })

        # Sort by date
        ts_df = ts_df.sort_values('ds').reset_index(drop=True)

        # Remove duplicates (keep last)
        ts_df = ts_df.drop_duplicates(subset=['ds'], keep='last')

        return ts_df

    def train_prophet_model(self, product_id: str, ts_df: pd.DataFrame):
        """
        Train Prophet model for a product
        """
        logger.info(f"Training model for product: {product_id}")

        try:
            # Initialize Prophet
            model = Prophet(
                seasonality_mode=ML_CONFIG['forecast']['seasonality_mode'],
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False
            )

            # Fit model
            model.fit(ts_df)

            # Store model
            self.models[product_id] = model

            logger.info(f"✅ Model trained successfully for {product_id}")
            return model

        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return None

    def forecast_price(self, product_id: str, days: int = 14) -> pd.DataFrame:
        """
        Generate price forecast
        """
        # Get or train model
        if product_id not in self.models:
            ts_df = self.prepare_time_series(product_id)
            if ts_df is None or len(ts_df) < 2:
                return None

            model = self.train_prophet_model(product_id, ts_df)
            if model is None:
                return None
        else:
            model = self.models[product_id]

        # Create future dataframe
        future = model.make_future_dataframe(periods=days)

        # Generate forecast
        forecast = model.predict(future)

        # Store forecast
        self.forecasts[product_id] = forecast

        return forecast

    def get_forecast_summary(self, product_id: str, days: int = 14) -> dict:
        """
        Get forecast summary in easy format
        """
        forecast = self.forecast_price(product_id, days)

        if forecast is None:
            return None

        # Get only future predictions
        future_forecast = forecast.tail(days)

        summary = {
            'product_id': product_id,
            'forecast_days': days,
            'predictions': [],
            'trend': None,
            'confidence': None
        }

        for _, row in future_forecast.iterrows():
            summary['predictions'].append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_price': round(row['yhat'], 2),
                'lower_bound': round(row['yhat_lower'], 2),
                'upper_bound': round(row['yhat_upper'], 2)
            })

        # Calculate trend
        first_price = future_forecast.iloc[0]['yhat']
        last_price = future_forecast.iloc[-1]['yhat']
        price_change = ((last_price - first_price) / first_price) * 100

        if price_change > 2:
            summary['trend'] = 'increasing'
        elif price_change < -2:
            summary['trend'] = 'decreasing'
        else:
            summary['trend'] = 'stable'

        summary['price_change_pct'] = round(price_change, 2)

        return summary

    def forecast_multiple_products(self, product_ids: list = None, days: int = 14):
        """
        Forecast for multiple products
        """
        if product_ids is None:
            # Get top products by frequency
            product_ids = self.df['product_id'].value_counts().head(10).index.tolist()

        results = {}

        for pid in product_ids:
            logger.info(f"Forecasting for {pid}")
            summary = self.get_forecast_summary(pid, days)
            if summary:
                results[pid] = summary

        return results

    def save_model(self, product_id: str, filename: str = None):
        """Save trained model"""
        if product_id not in self.models:
            logger.error(f"No model found for {product_id}")
            return

        if filename is None:
            filename = f"forecast_model_{product_id}.pkl"

        filepath = MODELS_DIR / filename
        joblib.dump(self.models[product_id], filepath)
        logger.info(f"Model saved to {filepath}")

    def load_model(self, product_id: str, filename: str):
        """Load saved model"""
        filepath = MODELS_DIR / filename
        self.models[product_id] = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")

    def calculate_accuracy(self, product_id: str, test_size: int = 3):
        """
        Calculate forecast accuracy using last N points
        """
        ts_df = self.prepare_time_series(product_id)

        if ts_df is None or len(ts_df) < test_size + 2:
            return None

        # Split data
        train_df = ts_df.iloc[:-test_size]
        test_df = ts_df.iloc[-test_size:]

        # Train on training data
        model = Prophet(seasonality_mode='multiplicative')
        model.fit(train_df)

        # Predict
        forecast = model.predict(test_df[['ds']])

        # Calculate MAPE (Mean Absolute Percentage Error)
        actual = test_df['y'].values
        predicted = forecast['yhat'].values

        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        mae = np.mean(np.abs(actual - predicted))

        return {
            'MAPE': round(mape, 2),
            'MAE': round(mae, 2),
            'accuracy_pct': round(100 - mape, 2)
        }


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    # Initialize forecaster
    forecaster = PriceForecaster()

    # Load data
    forecaster.load_data()

    # Get a sample product
    sample_product = forecaster.df['product_id'].iloc[0]

    print("\n" + "="*60)
    print("PRICE FORECASTING DEMO")
    print("="*60)

    # Generate forecast
    summary = forecaster.get_forecast_summary(sample_product, days=14)

    if summary:
        print(f"\n📊 Product ID: {summary['product_id']}")
        print(f"📅 Forecast Period: {summary['forecast_days']} days")
        print(f"📈 Trend: {summary['trend']}")
        print(f"💹 Price Change: {summary['price_change_pct']}%")

        print(f"\n🔮 Next 7 Days Predictions:")
        for pred in summary['predictions'][:7]:
            print(f"   {pred['date']}: Rs. {pred['predicted_price']}")

        # Calculate accuracy
        accuracy = forecaster.calculate_accuracy(sample_product)
        if accuracy:
            print(f"\n✅ Model Accuracy: {accuracy['accuracy_pct']}%")
            print(f"   MAPE: {accuracy['MAPE']}%")
            print(f"   MAE: Rs. {accuracy['MAE']}")

    print("\n" + "="*60)
