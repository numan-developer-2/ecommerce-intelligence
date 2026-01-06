# Demand Prediction Model
"""
Demand Prediction Model
Using XGBoost for sales/demand forecasting
Features: price, rating, discount, reviews
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
import joblib
import warnings
warnings.filterwarnings('ignore')

# XGBoost import (install: pip install xgboost)
try:
    import xgboost as xgb
except ImportError:
    print("XGBoost not installed. Run: pip install xgboost")

from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemandPredictor:
    """
    ML model to predict product demand/sales
    Uses product features to estimate demand
    """

    def __init__(self, data_file: Path = None):
        self.data_file = data_file or get_latest_cleaned_file()
        self.df = None
        self.model = None
        self.feature_importance = None

    def load_data(self):
        """Load cleaned data"""
        logger.info(f"Loading data from {self.data_file}")
        self.df = pd.read_csv(self.data_file)
        logger.info(f"Loaded {len(self.df)} records")
        return self.df

    def create_synthetic_demand(self):
        """
        Create synthetic demand target variable
        In production, use actual sales data
        """
        logger.info("Creating synthetic demand variable...")

        # Demand influenced by: rating, reviews, discount, price
        self.df['demand_score'] = (
            (self.df['rating'] * 20) +  # Rating contribution
            (np.log1p(self.df['review_count']) * 10) +  # Review contribution
            (self.df['discount_pct'] * 0.5) -  # Discount bonus
            (np.log1p(self.df['price']) * 2)  # Price penalty
        )

        # Normalize to 0-100 scale
        min_score = self.df['demand_score'].min()
        max_score = self.df['demand_score'].max()
        self.df['demand_score'] = ((self.df['demand_score'] - min_score) /
                                    (max_score - min_score)) * 100

        # Add some noise for realism
        noise = np.random.normal(0, 5, len(self.df))
        self.df['demand_score'] = self.df['demand_score'] + noise
        self.df['demand_score'] = self.df['demand_score'].clip(0, 100)

    def engineer_features(self):
        """
        Create features for ML model
        """
        logger.info("Engineering features...")

        # Fill missing values first
        self.df['price'] = self.df['price'].fillna(0)
        self.df['rating'] = self.df['rating'].fillna(0)
        self.df['review_count'] = self.df['review_count'].fillna(0)
        self.df['discount_pct'] = self.df['discount_pct'].fillna(0)

        # Price-based features
        self.df['price_log'] = np.log1p(self.df['price'])
        self.df['price_per_rating'] = self.df['price'] / (self.df['rating'] + 0.1)

        # Review features
        self.df['review_count_log'] = np.log1p(self.df['review_count'])
        self.df['has_reviews'] = (self.df['review_count'] > 0).astype(int)

        # Discount features
        self.df['is_discounted'] = (self.df['discount_pct'] > 0).astype(int)

        # Handle discount category safely
        self.df['discount_category'] = pd.cut(
            self.df['discount_pct'],
            bins=[-1, 0, 10, 25, 50, 1000], # Adjusted bins to include 0
            labels=[0, 1, 2, 3, 4]
        )
        # Fill NaN categories with 0 (no discount) and convert to int
        self.df['discount_category'] = self.df['discount_category'].cat.add_categories([-1]).fillna(0).astype(int)

        # Rating features
        self.df['is_highly_rated'] = (self.df['rating'] >= 4.0).astype(int)
        self.df['rating_squared'] = self.df['rating'] ** 2

        # Category encoding (if exists)
        if 'category' in self.df.columns:
            self.df['category_encoded'] = pd.Categorical(self.df['category']).codes

        # Brand encoding
        if 'brand' in self.df.columns:
            self.df['brand_encoded'] = pd.Categorical(self.df['brand']).codes

    def prepare_features(self):
        """
        Select and prepare features for modeling
        """
        feature_cols = [
            'price',
            'price_log',
            'original_price',
            'discount_pct',
            'rating',
            'rating_squared',
            'review_count_log',
            'is_discounted',
            'discount_category',
            'is_highly_rated',
            'has_reviews'
        ]

        # Add encoded columns if they exist
        if 'category_encoded' in self.df.columns:
            feature_cols.append('category_encoded')
        if 'brand_encoded' in self.df.columns:
            feature_cols.append('brand_encoded')

        # Filter only existing columns
        feature_cols = [col for col in feature_cols if col in self.df.columns]

        X = self.df[feature_cols]
        y = self.df['demand_score']

        # Handle missing values in features
        X = X.fillna(0)

        return X, y, feature_cols

    def train_model(self, test_size: float = 0.2):
        """
        Train XGBoost model
        """
        logger.info("Training XGBoost model...")

        # Prepare data
        X, y, feature_cols = self.prepare_features()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=ML_CONFIG['demand']['random_state']
        )

        # Initialize model
        self.model = xgb.XGBRegressor(
            n_estimators=ML_CONFIG['demand']['n_estimators'],
            learning_rate=0.1,
            max_depth=6,
            random_state=42,
            objective='reg:squarederror'
        )

        # Train model
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        # Predictions
        y_pred = self.model.predict(X_test)

        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mse)

        metrics = {
            'RMSE': round(rmse, 2),
            'MAE': round(mae, 2),
            'R2': round(r2, 4),
            'accuracy_pct': round(r2 * 100, 2)
        }

        logger.info(f"[OK] Model trained successfully!")
        logger.info(f"   R2 Score: {metrics['R2']}")
        logger.info(f"   RMSE: {metrics['RMSE']}")

        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return metrics

    def predict_demand(self, product_data: dict) -> dict:
        """
        Predict demand for a single product
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")

        # Create feature vector with ALL features used during training
        features = {
            'price': product_data.get('price', 0),
            'price_log': np.log1p(product_data.get('price', 0)),
            'original_price': product_data.get('original_price', 0),
            'discount_pct': product_data.get('discount_pct', 0),
            'rating': product_data.get('rating', 3.0),
            'rating_squared': product_data.get('rating', 3.0) ** 2,
            'review_count_log': np.log1p(product_data.get('review_count', 0)),
            'is_discounted': 1 if product_data.get('discount_pct', 0) > 0 else 0,
            'discount_category': min(int(product_data.get('discount_pct', 0) / 25), 3),
            'is_highly_rated': 1 if product_data.get('rating', 0) >= 4.0 else 0,
            'has_reviews': 1 if product_data.get('review_count', 0) > 0 else 0,
            # Add encoded features with default values (0 = unknown/default category)
            'category_encoded': product_data.get('category_encoded', 0),
            'brand_encoded': product_data.get('brand_encoded', 0)
        }

        try:
            # Create DataFrame
            X = pd.DataFrame([features])
            
            # Ensure column order matches training data
            try:
                if hasattr(self.model, 'get_booster'):
                    booster = self.model.get_booster()
                    model_feature_names = booster.feature_names
                    for col in model_feature_names:
                        if col not in X.columns:
                            X[col] = 0
                    X = X[model_feature_names]
            except:
                pass # Continue if reordering fails

            # Predict using ML Model
            demand_score = float(self.model.predict(X)[0])

        except Exception as e:
            logger.warning(f"ML Prediction failed ({e}). Switching to Heuristic Model (Rule-Based).")
            # --- ENTERPRISE FALLBACK LOGIC ---
            # If ML fails, we calculate score based on business rules
            
            # Base score starts at 50
            score = 50
            
            # Rating Impact (+/- 20)
            rating = features['rating']
            if rating >= 4.5: score += 20
            elif rating >= 4.0: score += 10
            elif rating < 3.0: score -= 20
            
            # Discount Impact (+/- 15)
            if features['discount_pct'] > 20: score += 15
            elif features['discount_pct'] > 5: score += 5
            
            # Price Penalty (Higher price = slightly lower volume demand usually)
            if features['price'] > 10000: score -= 10
            
            # Review Validity
            if features['review_count_log'] > 4: score += 10 # Had many reviews
            
            # Clamp between 0 and 100
            demand_score = max(min(score, 99), 1)

        # Interpret demand
        if demand_score >= 80:
            demand_level = 'Very High'
        elif demand_score >= 60:
            demand_level = 'High'
        elif demand_score >= 40:
            demand_level = 'Medium'
        elif demand_score >= 20:
            demand_level = 'Low'
        else:
            demand_level = 'Very Low'

        return {
            'demand_score': round(demand_score, 1),
            'demand_level': demand_level,
            'confidence': round(demand_score / 100, 2)
        }

    def get_top_features(self, n: int = 10):
        """Get most important features"""
        if self.feature_importance is None:
            return None
        return self.feature_importance.head(n)

    def save_model(self, filename: str = 'demand_model.pkl'):
        """Save trained model"""
        filepath = MODELS_DIR / filename
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")

    def load_model(self, filename: str = 'demand_model.pkl'):
        """Load saved model"""
        filepath = MODELS_DIR / filename
        self.model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    # Initialize predictor
    predictor = DemandPredictor()

    # Load and prepare data
    predictor.load_data()
    predictor.create_synthetic_demand()
    predictor.engineer_features()

    print("\n" + "="*60)
    print("DEMAND PREDICTION MODEL")
    print("="*60)

    # Train model
    metrics = predictor.train_model()

    print(f"\nModel Performance:")
    print(f"   Accuracy: {metrics['accuracy_pct']}%")
    print(f"   RMSE: {metrics['RMSE']}")
    print(f"   MAE: {metrics['MAE']}")
    print(f"   R2 Score: {metrics['R2']}")

    # Show feature importance
    print(f"\nTop 5 Important Features:")
    top_features = predictor.get_top_features(5)
    if top_features is not None:
        for _, row in top_features.iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")

    # Test prediction
    print(f"\nSample Prediction:")
    sample_product = {
        'price': 25000,
        'original_price': 30000,
        'discount_pct': 16.67,
        'rating': 4.5,
        'review_count': 150
    }

    result = predictor.predict_demand(sample_product)
    print(f"   Demand Score: {result['demand_score']}/100")
    print(f"   Demand Level: {result['demand_level']}")
    print(f"   Confidence: {result['confidence']}")

    # Save model
    predictor.save_model()

    print("\n" + "="*60)
