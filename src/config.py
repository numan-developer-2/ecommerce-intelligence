"""
Central Configuration File
All settings in one place - easy to modify
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# PROJECT PATHS
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent  # Project root (not src)
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, CLEANED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================
# API KEYS & SECRETS
# ============================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Warn if API key is not set
if not OPENROUTER_API_KEY:
    import logging
    logging.warning("⚠️  OPENROUTER_API_KEY not set! AI insights will not work. Set it in .env file.")

# ============================================
# SCRAPING CONFIGURATION
# ============================================
SCRAPING_CONFIG = {
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ],
    "delay_range": (2, 5),  # Random delay between requests (seconds)
    "max_retries": 3,
    "timeout": 15,
    "verify_ssl": True
}

# Target websites (easy to add more)
TARGET_SITES = {
    "daraz": {
        "base_url": "https://www.daraz.pk",
        "search_url": "https://www.daraz.pk/catalog/?q={query}",
        "enabled": True
    },
    "amazon": {
        "base_url": "https://www.amazon.com",
        "search_url": "https://www.amazon.com/s?k={query}",
        "enabled": False  # Enable when needed
    }
}

# ============================================
# DATA SCHEMA
# ============================================
DATA_COLUMNS = [
    "product_id",
    "url",
    "title",
    "brand",
    "category",
    "price",
    "original_price",
    "discount_pct",
    "rating",
    "review_count",
    "availability",
    "scraped_at"
]

# ============================================
# ML MODEL CONFIGURATION
# ============================================
ML_CONFIG = {
    "forecast": {
        "model_type": "prophet",  # or "arima"
        "forecast_days": 14,
        "seasonality_mode": "multiplicative"
    },
    "demand": {
        "model_type": "xgboost",  # or "lightgbm"
        "test_size": 0.2,
        "random_state": 42,
        "n_estimators": 100
    }
}

# Feature columns for demand prediction
FEATURE_COLUMNS = [
    "price",
    "discount_pct",
    "rating",
    "review_count",
    "price_change_7d",
    "weekday",
    "month"
]

# ============================================
# API SERVER CONFIGURATION
# ============================================
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,  # Auto-reload on code changes
    "log_level": "info"
}

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://*.netlify.app",  # Your Netlify domain
    "*"  # Allow all (for development only)
]

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "app.log"),
            "formatter": "default"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file", "console"]
    }
}

# ============================================
# DASHBOARD CONFIGURATION
# ============================================
EXCEL_CONFIG = {
    "file_name": "price_intelligence_dashboard.xlsx",
    "sheets": {
        "raw_data": "Raw Data",
        "cleaned_data": "Cleaned Data",
        "pivot_tables": "Analysis",
        "dashboard": "Dashboard"
    }
}

# ============================================
# EMAIL ALERTS (Optional)
# ============================================
EMAIL_CONFIG = {
    "enabled": False,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "recipients": ["recipient@example.com"]
}

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_latest_raw_file():
    """Get the most recent raw data file"""
    files = list(RAW_DATA_DIR.glob("*.csv"))
    return max(files, key=os.path.getctime) if files else None

def get_latest_cleaned_file():
    """Get the most recent cleaned data file"""
    files = list(CLEANED_DATA_DIR.glob("*.csv"))
    return max(files, key=os.path.getctime) if files else None

# Print configuration on import (optional)
if __name__ == "__main__":
    print("=" * 50)
    print("Configuration Loaded Successfully")
    print("=" * 50)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"OpenRouter API: {'✓ Configured' if OPENROUTER_API_KEY else '✗ Not Set'}")
    print("=" * 50)
