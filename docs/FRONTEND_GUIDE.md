# Frontend Dashboard Guide

## Kese Kam Karta Hai (How It Works)

### 1. **Architecture**

Yeh ek **Single Page Application (SPA)** hai jo:

- **HTML** - Structure ke liye
- **Tailwind CSS** - Styling ke liye (CDN se load hota hai)
- **JavaScript** - Logic aur API calls ke liye
- **Chart.js** - Graphs banane ke liye

### 2. **Backend Connection**

Frontend Python backend (`src/api_server.py`) se baat karta hai:

```javascript
const API_URL = "http://localhost:8000";
```

### 3. **Main Features**

#### A. **Stats Dashboard**

- `/stats` endpoint se data fetch karta hai
- Total products, average price, ratings display karta hai

#### B. **Product Search & List**

- `/products?limit=10` se products load hota hai
- Table mein products display hote hain
- "Analyze" button se product select kar sakte hain

#### C. **Price Forecast**

- `/forecast` endpoint (POST) use karta hai
- Chart.js se graph banata hai
- Trend (increasing/decreasing) dikhata hai

#### D. **Demand Prediction**

- `/demand` endpoint (POST) use karta hai
- XGBoost model se demand predict karta hai
- Confidence level dikhata hai

#### E. **AI Insights**

- `/ai-insight` endpoint use karta hai
- OpenRouter API se AI analysis milta hai

### 4. **Kese Chalaye (How to Run)**

#### Step 1: API Server Start Karein

```bash
cd "d:\Python Project\Data Scietist Projects\E-commerce Intelligence"
python src/api_server.py
```

Server `http://localhost:8000` pe start hoga.

#### Step 2: Frontend Open Karein

Browser mein yeh file open karein:

```
d:\Python Project\Data Scietist Projects\E-commerce Intelligence\frontend\index.html
```

Ya double-click karein `index.html` pe.

### 5. **User Flow**

1. **Page Load** → Stats aur products automatically load hote hain
2. **Product Select** → Table se kisi product pe "Analyze" click karein
3. **Analysis** → Price forecast aur demand prediction dikhai dega
4. **AI Insight** → "Generate AI Insight" button se detailed analysis milega

### 6. **Important Functions**

```javascript
// Dashboard initialize karta hai
initDashboard();

// Stats load karta hai
loadStats();

// Products load karta hai
loadProducts();

// Product analyze karta hai
analyzeProduct();

// Forecast display karta hai
displayForecast(forecast);

// Demand display karta hai
displayDemand(prediction);

// AI insight generate karta hai
getAIInsight();
```

### 7. **API Endpoints Used**

| Endpoint         | Method | Purpose                |
| ---------------- | ------ | ---------------------- |
| `/stats`         | GET    | Overall statistics     |
| `/products`      | GET    | Product list           |
| `/products/{id}` | GET    | Single product details |
| `/forecast`      | POST   | Price forecasting      |
| `/demand`        | POST   | Demand prediction      |
| `/ai-insight`    | POST   | AI analysis            |

### 8. **Error Handling**

Agar API server nahi chal raha:

```
Failed to load dashboard data
```

**Solution:** `python src/api_server.py` run karein.

### 9. **Design Features**

- **Glassmorphism** - Modern glass effect
- **Animations** - Smooth fade-in, slide-in effects
- **Responsive** - Mobile aur desktop dono pe kaam karta hai
- **Dark Theme** - Purple gradient background
- **Interactive Charts** - Hover pe details dikhate hain

### 10. **Customization**

API URL change karne ke liye:

```javascript
const API_URL = "http://your-server:port";
```

Forecast days change karne ke liye:

```html
<select id="forecastDays">
  <option value="7">7 Days</option>
  <option value="14">14 Days</option>
  <option value="30">30 Days</option>
</select>
```

---

## Quick Commands

```bash
# API Server Start
python src/api_server.py

# Complete Pipeline Run (data generate karne ke liye)
python main.py

# Browser mein open karein
start frontend/index.html
```

---

## Troubleshooting

### Issue 1: "API Connected" red dikhai de raha hai

**Fix:** API server start karein

### Issue 2: Products load nahi ho rahe

**Fix:** Pehle `python main.py` run karke data generate karein

### Issue 3: Forecast/Demand kaam nahi kar raha

**Fix:** Product ID sahi enter karein (table se copy karein)

---

## Next Steps

1. ✅ API server start karein
2. ✅ Frontend open karein
3. ✅ Product analyze karein
4. ✅ AI insights generate karein

**Enjoy your E-Commerce Intelligence Dashboard!** 🚀
