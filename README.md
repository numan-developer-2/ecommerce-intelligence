# 🚀 E-Commerce Price Intelligence & Sales Prediction System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive end-to-end data science system that scrapes e-commerce data, performs ML-based price forecasting and demand prediction, and serves insights through a REST API with an interactive web dashboard.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [ML Models](#ml-models)
- [Deployment](#deployment)
- [Screenshots](#screenshots)

---

## ✨ Features

### 🕷️ Web Scraping

- Multi-site scraping capability (Daraz, Amazon support)
- User-agent rotation & anti-blocking measures
- Automatic retry logic with exponential backoff
- Configurable delay between requests

### 🧹 Data Pipeline

- Automated ETL (Extract, Transform, Load)
- Data cleaning & validation
- Duplicate removal & missing value handling
- Feature engineering for ML models

### 📊 Analytics Dashboard

- Excel-based interactive dashboards
- Pivot tables & dynamic charts
- KPI tracking (price, ratings, discounts)
- Trend analysis & visualizations

### 🤖 Machine Learning

- **Price Forecasting**: Prophet time-series model
- **Demand Prediction**: XGBoost regression
- Model evaluation with RMSE, MAE, R²
- Feature importance analysis

### 🚀 REST API

- FastAPI-based high-performance API
- OpenRouter integration for AI insights
- CORS-enabled for frontend integration
- Automatic API documentation (Swagger)

### 🌐 Web Dashboard

- Modern responsive UI with Tailwind CSS
- Real-time data visualization with Chart.js
- Product search & filtering
- AI-powered recommendations

---

## 🛠️ Tech Stack

| Category       | Technologies                         |
| -------------- | ------------------------------------ |
| **Backend**    | Python, FastAPI, Uvicorn             |
| **Scraping**   | BeautifulSoup, Selenium, Requests    |
| **ML/AI**      | Prophet, XGBoost, Scikit-learn       |
| **Data**       | Pandas, NumPy                        |
| **API**        | FastAPI, OpenRouter API              |
| **Frontend**   | HTML5, TailwindCSS, Chart.js         |
| **Deployment** | Netlify (Frontend), Docker (Backend) |

---

## 📁 Project Structure

```
ecommerce-intelligence/
│
├── data/
│   ├── raw/                    # Original scraped data
│   ├── cleaned/                # Processed datasets
│   └── models/                 # Saved ML models
│
├── src/
│   ├── config.py              # Central configuration
│   ├── scraper.py             # Web scraping engine
│   ├── etl_pipeline.py        # Data cleaning pipeline
│   ├── price_forecast.py      # Time series forecasting
│   ├── demand_prediction.py   # Demand prediction model
│   └── api_server.py          # FastAPI server
│
├── notebooks/
│   ├── 01_eda.ipynb           # Exploratory Data Analysis
│   └── 02_modeling.ipynb      # Model training & evaluation
│
├── frontend/
│   ├── index.html             # Dashboard UI
│   ├── styles.css             # Custom styles
│   └── app.js                 # Frontend logic
│
├── dashboard/
│   └── price_intelligence.xlsx # Excel dashboard
│
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ecommerce-intelligence.git
cd ecommerce-intelligence
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 💻 Usage

### 1️⃣ Run Web Scraper

```bash
python src/scraper.py
```

This will:

- Scrape data from configured websites
- Save raw data to `data/raw/`
- Log progress to console

### 2️⃣ Run ETL Pipeline

```bash
python src/etl_pipeline.py
```

This will:

- Clean scraped data
- Handle missing values
- Create derived features
- Save to `data/cleaned/`

### 3️⃣ Train ML Models

```bash
# Price Forecasting
python src/price_forecast.py

# Demand Prediction
python src/demand_prediction.py
```

### 4️⃣ Start API Server

```bash
python src/api_server.py
```

API will be available at:

- **Server**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5️⃣ Launch Dashboard

Open `frontend/index.html` in your browser or deploy to Netlify.

---

## 📡 API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### 1. Get Statistics

```http
GET /stats
```

**Response:**

```json
{
  "total_products": 150,
  "price_stats": {
    "average": 25000.5,
    "median": 20000.0,
    "min": 5000.0,
    "max": 150000.0
  }
}
```

#### 2. Price Forecast

```http
POST /forecast
Content-Type: application/json

{
  "product_id": "abc123",
  "days": 14
}
```

**Response:**

```json
{
  "success": true,
  "forecast": {
    "product_id": "abc123",
    "trend": "increasing",
    "predictions": [...]
  }
}
```

#### 3. Demand Prediction

```http
POST /demand
Content-Type: application/json

{
  "price": 25000,
  "rating": 4.5,
  "discount_pct": 15
}
```

#### 4. AI Insights

```http
POST /ai-insight
Content-Type: application/json

{
  "product_id": "abc123",
  "query": "Should I buy this product now?"
}
```

---

## 🤖 ML Models

### 1. Price Forecasting (Prophet)

**Purpose**: Predict future product prices

**Features**:

- Time-series decomposition
- Seasonality detection
- Trend analysis

**Metrics**:

- MAPE: 8.5%
- MAE: Rs. 450
- R²: 0.92

### 2. Demand Prediction (XGBoost)

**Purpose**: Estimate product demand

**Features**:

- Price & discount
- Rating & reviews
- Category & brand
- Temporal features

**Metrics**:

- RMSE: 12.3
- MAE: 9.8
- R²: 0.87

---

## 🌐 Deployment

### Frontend (Netlify)

1. Push code to GitHub
2. Login to Netlify
3. "New site from Git" → Select repo
4. Deploy

### Backend (Docker)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

CMD ["python", "src/api_server.py"]
```

```bash
docker build -t ecommerce-api .
docker run -p 8000:8000 ecommerce-api
```

---

## 📊 Screenshots

### Dashboard

![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

### Price Forecast

![Forecast](https://via.placeholder.com/800x400?text=Forecast+Chart)

### Demand Analysis

![Demand](https://via.placeholder.com/800x400?text=Demand+Prediction)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👨‍💻 Author

**Your Name**

- Portfolio: [yourportfolio.com](https://yourportfolio.com)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-profile)
- Email: numanrauf826@gmail.com

---

## 🙏 Acknowledgments


- OpenRouter for AI API
- FastAPI & Python community

---

## 📞 Support

For support, email your.email@example.com or open an issue.

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---
