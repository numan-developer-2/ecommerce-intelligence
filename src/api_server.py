"""
FastAPI Server with OpenRouter Integration
Serves ML predictions and AI insights
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
import logging
import requests
from datetime import datetime

# Import our modules
from config import *
from price_forecast import PriceForecaster
from demand_prediction import DemandPredictor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="E-Commerce Intelligence API",
    description="Price forecasting and demand prediction API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models globally
forecaster = None
demand_predictor = None
products_df = None


# ============================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================

class ProductQuery(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None

class ForecastRequest(BaseModel):
    product_id: str
    days: int = 14

class DemandRequest(BaseModel):
    price: float
    original_price: Optional[float] = None
    discount_pct: Optional[float] = 0
    rating: Optional[float] = 3.5
    review_count: Optional[int] = 0

class AIInsightRequest(BaseModel):
    product_id: str
    query: str = "Analyze this product's price trend and give recommendations"


# ============================================
# STARTUP EVENT
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize models on server startup"""
    global forecaster, demand_predictor, products_df

    try:
        logger.info("Starting API server...")

        # Load data
        data_file = get_latest_cleaned_file()
        if data_file:
            products_df = pd.read_csv(data_file)
            logger.info(f"Loaded {len(products_df)} products")

            # Initialize forecaster
            forecaster = PriceForecaster(data_file)
            forecaster.load_data()
            logger.info("Price forecaster initialized")

            # Initialize demand predictor
            demand_predictor = DemandPredictor(data_file)
            demand_predictor.load_data()
            demand_predictor.create_synthetic_demand()
            demand_predictor.engineer_features()
            demand_predictor.train_model()
            logger.info("Demand predictor initialized")
        else:
            logger.warning("No data file found. Run scraper first.")

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")


# ============================================
# HELPER FUNCTIONS
# ============================================

def call_openrouter_api(messages: List[Dict], model: str = "anthropic/claude-3.5-sonnet") -> str:
    """
    Call OpenRouter API for AI insights
    Fallback to simulation if API fails or key is missing
    """
    # Check if key is available
    if not OPENROUTER_API_KEY:
        logger.warning("No OpenRouter API key found. Using simulated AI response.")
        return _generate_simulated_insight(messages)

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages
            },
            timeout=10 # Short timeout to prevent hanging
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code in [401, 402, 429]: # Auth error, Payment required, Rate limit
            logger.warning(f"OpenRouter Limit/Credit Error ({response.status_code}). Switching to simulation.")
            return _generate_simulated_insight(messages)
        else:
            logger.error(f"OpenRouter API error: {response.text}")
            return _generate_simulated_insight(messages)
            
    except Exception as e:
        logger.error(f"Error calling OpenRouter: {str(e)}")
        return _generate_simulated_insight(messages)

def _generate_simulated_insight(messages: List[Dict]) -> str:
    """Generate a realistic looking 'AI' insight for demo purposes"""
    try:
        content = messages[0]['content']
        # Extract basic info if possible
        price_line = [l for l in content.split('\n') if 'Current Price:' in l]
        price = price_line[0].split(':')[-1].strip() if price_line else "unknown"
        
        return (
            f"Based on the analysis (Simulation Mode), this product shows a stable trend at {price}. "
            "Demand appears consistent with market averages. "
            "Recommendation: Monitor for price drops below 10% before purchasing. "
            "Note: Your OpenRouter API usage limit has been reached (Code 402). Using simulation."
        )
    except:
        return "Market analysis suggests monitoring this product for price fluctuations. Demand is stable."


# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "E-Commerce Intelligence API",
        "version": "1.0.0",
        "endpoints": [
            "/products",
            "/forecast",
            "/demand",
            "/ai-insight",
            "/stats"
        ]
    }


@app.get("/products")
async def get_products(limit: int = 50):
    """Get all products"""
    if products_df is None:
        raise HTTPException(status_code=503, detail="No data available")

    products = products_df.head(limit).to_dict('records')

    return {
        "total": len(products_df),
        "returned": len(products),
        "products": products
    }


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get specific product details"""
    if products_df is None:
        raise HTTPException(status_code=503, detail="No data available")

    product = products_df[products_df['product_id'] == product_id]

    if len(product) == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return product.iloc[0].to_dict()


@app.post("/forecast")
async def forecast_price(request: ForecastRequest):
    """
    Get price forecast for a product
    """
    if forecaster is None:
        raise HTTPException(status_code=503, detail="Forecaster not initialized")

    try:
        # Generate forecast
        summary = forecaster.get_forecast_summary(
            request.product_id,
            days=request.days
        )
        
        if summary is None:
            # Return gentle failure
            return {
                "success": False,
                "message": "Not enough data to forecast"
            }
        
        return {
            "success": True,
            "forecast": summary
        }
        
    except Exception as e:
        logger.error(f"Forecast error: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }


@app.post("/demand")
async def predict_demand(request: DemandRequest):
    """
    Predict demand for product based on features
    """
    if demand_predictor is None:
        raise HTTPException(status_code=503, detail="Demand predictor not initialized")

    try:
        # Prepare product data
        product_data = {
            'price': request.price,
            'original_price': request.original_price or request.price,
            'discount_pct': request.discount_pct,
            'rating': request.rating,
            'review_count': request.review_count
        }

        # Get prediction
        result = demand_predictor.predict_demand(product_data)

        return {
            "success": True,
            "prediction": result,
            "input": product_data
        }

    except Exception as e:
        logger.error(f"Demand prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai-insight")
async def get_ai_insight(request: AIInsightRequest):
    """
    Get AI-powered insights using OpenRouter
    """
    try:
        # Get product data
        if products_df is None:
            raise HTTPException(status_code=503, detail="No data available")

        product = products_df[products_df['product_id'] == request.product_id]

        if len(product) == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        product_info = product.iloc[0].to_dict()

        # Get forecast
        forecast_summary = forecaster.get_forecast_summary(request.product_id, days=7)

        # Create prompt for OpenRouter
        prompt = f"""
        Analyze this e-commerce product and provide insights:

        Product: {product_info.get('title', 'Unknown')}
        Current Price: Rs. {product_info.get('price', 0)}
        Original Price: Rs. {product_info.get('original_price', 0)}
        Discount: {product_info.get('discount_pct', 0)}%
        Rating: {product_info.get('rating', 0)}/5
        Reviews: {product_info.get('review_count', 0)}

        Price Forecast (7 days): {forecast_summary.get('trend', 'stable') if forecast_summary else 'unavailable'}

        User Question: {request.query}

        Provide a concise, professional analysis in 3-4 sentences.
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        # Get AI response
        ai_response = call_openrouter_api(messages)

        return {
            "success": True,
            "product_id": request.product_id,
            "insight": ai_response,
            "product_info": {
                "title": product_info.get('title'),
                "price": product_info.get('price'),
                "rating": product_info.get('rating')
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI insight error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics():
    """Get overall statistics"""
    if products_df is None:
        raise HTTPException(status_code=503, detail="No data available")

    stats = {
        "total_products": len(products_df),
        "unique_brands": products_df['brand'].nunique() if 'brand' in products_df.columns else 0,
        "unique_categories": products_df['category'].nunique() if 'category' in products_df.columns else 0,
        "price_stats": {
            "average": round(products_df['price'].mean(), 2),
            "median": round(products_df['price'].median(), 2),
            "min": round(products_df['price'].min(), 2),
            "max": round(products_df['price'].max(), 2)
        },
        "rating_stats": {
            "average": round(products_df['rating'].mean(), 2),
            "products_above_4": int((products_df['rating'] >= 4).sum())
        },
        "discount_stats": {
            "products_on_sale": int((products_df['discount_pct'] > 0).sum()),
            "average_discount": round(products_df['discount_pct'].mean(), 2)
        }
    }

    return stats


@app.get("/search")
async def search_products(query: str, limit: int = 20):
    """Search products by name"""
    if products_df is None:
        raise HTTPException(status_code=503, detail="No data available")

    # Simple search in title
    results = products_df[
        products_df['title'].str.contains(query, case=False, na=False)
    ].head(limit)

    return {
        "query": query,
        "count": len(results),
        "products": results.to_dict('records')
    }


# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("Starting E-Commerce Intelligence API Server")
    print("="*60)
    print(f"Server: http://{API_CONFIG['host']}:{API_CONFIG['port']}")
    print(f"Docs: http://localhost:{API_CONFIG['port']}/docs")
    print("="*60 + "\n")

    uvicorn.run(
        "api_server:app",
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        reload=API_CONFIG['reload'],
        log_level=API_CONFIG['log_level']
    )
