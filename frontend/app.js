// ============================================
// E-COMMERCE INTELLIGENCE - FRONTEND LOGIC
// Modern JavaScript with Error Handling
// ============================================

const CONFIG = {
    // Dynamically select API URL based on environment
    // 1. If running locally, use localhost:8000
    // 2. If running on Netlify/Production, use your Render Backend URL
    API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://replace-me-with-your-render-url.onrender.com', // <--- REPLACE THIS AFTER DEPLOYING BACKEND
        
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
    TOAST_DURATION: 5000
};

// Global State
const state = {
    currentProductId: null,
    forecastChart: null,
    theme: localStorage.getItem('theme') || 'light',
    isLoading: false
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    initializeEventListeners();
    initializeDashboard();
});

function initializeTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
}

function initializeEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
    
    // Search input - Enter key
    document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeProduct();
    });
}

async function initializeDashboard() {
    showLoading();
    try {
        await Promise.all([
            checkAPIConnection(),
            loadStats(),
            loadProducts()
        ]);
        showToast('Dashboard loaded successfully', 'success');
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showToast('Failed to load dashboard. Please check if API server is running.', 'error');
    } finally {
        hideLoading();
    }
}

// ============================================
// THEME MANAGEMENT
// ============================================

function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    
    // Update chart if exists
    if (state.forecastChart) {
        updateChartTheme();
    }
}

function updateChartTheme() {
    const isDark = state.theme === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#6b7280';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    if (state.forecastChart) {
        state.forecastChart.options.scales.x.ticks.color = textColor;
        state.forecastChart.options.scales.y.ticks.color = textColor;
        state.forecastChart.options.scales.x.grid.color = gridColor;
        state.forecastChart.options.scales.y.grid.color = gridColor;
        state.forecastChart.update();
    }
}

// ============================================
// API FUNCTIONS
// ============================================

async function fetchWithRetry(url, options = {}, retries = CONFIG.RETRY_ATTEMPTS) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        if (retries > 0) {
            await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY));
            return fetchWithRetry(url, options, retries - 1);
        }
        throw error;
    }
}

async function checkAPIConnection() {
    try {
        await fetchWithRetry(`${CONFIG.API_URL}/`);
        updateAPIStatus('connected', 'API Connected');
    } catch (error) {
        updateAPIStatus('error', 'API Offline');
        throw error;
    }
}

function updateAPIStatus(status, text) {
    const statusElement = document.getElementById('apiStatus');
    if (!statusElement) return;
    
    const indicator = statusElement.querySelector('.status-indicator');
    const statusText = statusElement.querySelector('.status-text');
    
    indicator.className = `status-indicator ${status}`;
    statusText.textContent = text;
}

// ============================================
// STATS LOADING
// ============================================

async function loadStats() {
    try {
        const data = await fetchWithRetry(`${CONFIG.API_URL}/stats`);
        displayStats(data);
    } catch (error) {
        console.error('Stats loading error:', error);
        displayStatsError();
    }
}

function displayStats(data) {
    const statsHTML = `
        <div class="stat-card">
            <div class="stat-header">
                <div>
                    <div class="stat-label">Total Products</div>
                    <div class="stat-value">${data.total_products.toLocaleString()}</div>
                </div>
                <div class="stat-icon primary">📦</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-header">
                <div>
                    <div class="stat-label">Avg Price</div>
                    <div class="stat-value">Rs. ${Math.round(data.price_stats.average).toLocaleString()}</div>
                </div>
                <div class="stat-icon success">💰</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-header">
                <div>
                    <div class="stat-label">Avg Rating</div>
                    <div class="stat-value">${data.rating_stats.average.toFixed(1)} ⭐</div>
                </div>
                <div class="stat-icon warning">⭐</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-header">
                <div>
                    <div class="stat-label">On Sale</div>
                    <div class="stat-value">${data.discount_stats.products_on_sale}</div>
                </div>
                <div class="stat-icon error">🏷️</div>
            </div>
        </div>
    `;
    
    document.getElementById('statsGrid').innerHTML = statsHTML;
}

function displayStatsError() {
    document.getElementById('statsGrid').innerHTML = `
        <div class="stat-card" style="grid-column: 1 / -1;">
            <div class="empty-state">
                <p>Failed to load statistics. Please check API connection.</p>
            </div>
        </div>
    `;
}

// ============================================
// PRODUCTS LOADING
// ============================================

async function loadProducts() {
    try {
        const data = await fetchWithRetry(`${CONFIG.API_URL}/products?limit=10`);
        displayProducts(data.products || []);
    } catch (error) {
        console.error('Products loading error:', error);
        displayProductsError();
    }
}

function displayProducts(products) {
    const tbody = document.getElementById('productTableBody');
    
    if (!products || products.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="loading-row">
                    No products found. Run the scraper first: <code>python main.py</code>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = products.map(product => `
        <tr>
            <td>
                <div class="product-title">${truncate(product.title, 60)}</div>
                <div class="product-id">${product.product_id}</div>
            </td>
            <td><strong>Rs. ${product.price.toLocaleString()}</strong></td>
            <td>${product.rating} ⭐</td>
            <td><span style="color: var(--color-error);">${product.discount_pct}%</span></td>
            <td>
                <button class="btn btn-secondary" onclick="selectProduct('${product.product_id}')" style="padding: 0.5rem 1rem;">
                    Analyze
                </button>
            </td>
        </tr>
    `).join('');
}

function displayProductsError() {
    document.getElementById('productTableBody').innerHTML = `
        <tr>
            <td colspan="5" class="loading-row">
                Failed to load products. Please check API connection.
            </td>
        </tr>
    `;
}

// ============================================
// PRODUCT ANALYSIS
// ============================================

async function analyzeProduct() {
    let productId = document.getElementById('searchInput').value.trim();
    
    if (!productId) {
        showToast('Please enter a Product Name or ID', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        // SMART SEARCH LOGIC
        // 1. Try to see if this is a valid ID directly
        let product = null; 
        try {
            product = await fetchWithRetry(`${CONFIG.API_URL}/products/${productId}`);
        } catch (e) {
            // Not a valid ID, assume it is a search query
            console.log(`'${productId}' is not an ID, searching by name...`);
        }

        // 2. If direct lookup failed, search by name
        if (!product) {
            const searchResults = await fetchWithRetry(`${CONFIG.API_URL}/search?query=${encodeURIComponent(productId)}&limit=1`);
            
            if (searchResults && searchResults.products && searchResults.products.length > 0) {
                // Found a real product match
                product = searchResults.products[0];
                productId = product.product_id; 
                showToast(`Found: ${truncate(product.title, 30)}`, 'success');
                document.getElementById('searchInput').value = productId;
            } else {
                // Not found in DB -> Virtual Product Mode
                console.log("Product not found. Converting to Virtual Product.");
                showToast(`Analyzing new product: "${truncate(productId, 20)}"`, 'info');
                
                // Create a virtual product object
                // Use hash of string to get consistent pseudo-random numbers
                const seed = productId.length * 7; 
                const smartPrice = estimatePrice(productId);
                
                product = {
                    product_id: productId, // Use name as ID
                    title: productId,
                    price: smartPrice, 
                    original_price: Math.round(smartPrice * 1.2), // 20% markup
                    rating: 4.0 + (seed % 10) / 10, // 4.0 - 4.9
                    review_count: 50 + (seed * 5),
                    discount_pct: 15
                };
            }
        }

        // 3. Set global state and analyze
        state.currentProductId = productId;
        
        // Ensure demand API receives all fields
        const productForDemand = {
            price: product.price,
            original_price: product.original_price || product.price,
            discount_pct: product.discount_pct || 0,
            rating: product.rating || 0,
            review_count: product.review_count || 0,
            product_id: product.product_id
        };
        
        await Promise.all([
            loadForecast(productId), 
            loadDemand(productId, productForDemand) 
        ]);
        
        showToast('Analysis complete!', 'success');
        
    } catch (error) {

// ... inside existing code ...

// Helper to guess price based on keywords
function estimatePrice(name) {
    const lower = name.toLowerCase();
    
    // High end
    if (lower.match(/laptop|macbook|iphone|samsung|mobile|tv|camera|fridge|ac|console|ps5/)) return 75000;
    if (lower.match(/watch|monitor|tablet|speaker|headphone|sofa|bed|cycle/)) return 15000;
    
    // Mid range
    if (lower.match(/shoe|sneaker|jacket|jeans|bag|mixer|blender|keyboard|mouse/)) return 4000;
    if (lower.match(/shirt|t-shirt|pant|trouser|dress|perfume|toy|book/)) return 1500;
    
    // Low end
    if (lower.match(/sock|pen|pencil|case|cover|cable|charger|glass|soap|shampoo/)) return 500;
    
    // Default randomish
    return 2500 + (name.length * 100);
}
        console.error('Analysis error:', error);
        showToast(`Could not find product: "${productId}"`, 'error');
        // Reset UI if failed
        updateBadge('forecastBadge', 'Not Found', 'error');
        updateBadge('demandBadge', 'Not Found', 'error');
        displayForecastError('Product not found');
        displayDemandError('Product not found');
    } finally {
        hideLoading();
    }
}

function selectProduct(productId) {
    document.getElementById('searchInput').value = productId;
    analyzeProduct();
}

// ============================================
// PRICE FORECAST
// ============================================

async function loadForecast(productId) {
    const days = parseInt(document.getElementById('forecastDays').value);
    
    try {
        const data = await fetchWithRetry(`${CONFIG.API_URL}/forecast`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, days })
        });
        
        if (data.success && data.forecast) {
            displayForecast(data.forecast);
            updateBadge('forecastBadge', 'Forecast Ready', 'success');
        } else {
            displayForecastError('No forecast data available');
            updateBadge('forecastBadge', 'No Data', 'warning');
        }
    } catch (error) {
        console.error('Forecast error:', error);
        displayForecastError('Failed to load forecast');
        updateBadge('forecastBadge', 'Error', 'error');
    }
}

function displayForecast(forecast) {
    const ctx = document.getElementById('forecastChart');
    
    // Destroy existing chart
    if (state.forecastChart) {
        state.forecastChart.destroy();
    }
    
    const labels = forecast.predictions.map(p => formatDate(p.date));
    const prices = forecast.predictions.map(p => p.predicted_price);
    
    const isDark = state.theme === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#6b7280';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    state.forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Predicted Price (Rs)',
                data: prices,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: { color: textColor, font: { size: 12, weight: '600' } }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    borderColor: '#6366f1',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: { color: textColor },
                    grid: { color: gridColor }
                },
                y: {
                    ticks: { color: textColor },
                    grid: { color: gridColor }
                }
            }
        }
    });
    
    // Display forecast details
    const trendClass = forecast.trend === 'increasing' ? 'positive' : 
                       forecast.trend === 'decreasing' ? 'negative' : 'neutral';
    const changeClass = forecast.price_change_pct > 0 ? 'positive' : 'negative';
    
    document.getElementById('forecastDetails').innerHTML = `
        <div class="detail-item">
            <div class="detail-label">Trend</div>
            <div class="detail-value ${trendClass}">${forecast.trend.toUpperCase()}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Price Change</div>
            <div class="detail-value ${changeClass}">
                ${forecast.price_change_pct > 0 ? '+' : ''}${forecast.price_change_pct}%
            </div>
        </div>
    `;
}

function displayForecastError(message) {
    document.getElementById('forecastDetails').innerHTML = `
        <div class="empty-state">
            <p>${message}</p>
        </div>
    `;
}

// ============================================
// DEMAND PREDICTION
// ============================================

async function loadDemand(productId, productObj = null) {
    try {
        // Use passed object or fetch from API
        let product = productObj;
        
        if (!product) {
            product = await fetchWithRetry(`${CONFIG.API_URL}/products/${productId}`);
        }
        
        // Then get demand prediction
        const demandData = await fetchWithRetry(`${CONFIG.API_URL}/demand`, {
            method: 'POST',
            body: JSON.stringify({
                price: product.price,
                original_price: product.original_price || product.price,
                discount_pct: product.discount_pct || 0,
                rating: product.rating || 0,
                review_count: product.review_count || 0
            })
        });
        
        if (demandData.success && demandData.prediction) {
            displayDemand(demandData.prediction);
            updateBadge('demandBadge', 'Prediction Ready', 'success');
        } else {
            displayDemandError('No demand data available');
            updateBadge('demandBadge', 'No Data', 'warning');
        }
    } catch (error) {
        console.error('Demand error:', error);
        displayDemandError('Failed to load demand prediction');
        updateBadge('demandBadge', 'Error', 'error');
    }
}

function displayDemand(prediction) {
    const levelClass = prediction.demand_level.toLowerCase().replace(' ', '-');
    
    document.getElementById('demandResult').innerHTML = `
        <div class="demand-score">${prediction.demand_score}</div>
        <div class="demand-level ${levelClass}">${prediction.demand_level}</div>
        <div style="max-width: 400px; margin: 0 auto;">
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${(prediction.confidence * 100).toFixed(0)}%"></div>
            </div>
            <div class="confidence-text">
                Model Confidence: ${(prediction.confidence * 100).toFixed(0)}%
            </div>
        </div>
    `;
}

function displayDemandError(message) {
    document.getElementById('demandResult').innerHTML = `
        <div class="empty-state">
            <p>${message}</p>
        </div>
    `;
}

// ============================================
// AI INSIGHTS
// ============================================

async function getAIInsight() {
    if (!state.currentProductId) {
        showToast('Please analyze a product first', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const data = await fetchWithRetry(`${CONFIG.API_URL}/ai-insight`, {
            method: 'POST',
            body: JSON.stringify({
                product_id: state.currentProductId,
                query: 'Analyze price trends and provide buying recommendations'
            })
        });
        
        if (data.success && data.insight) {
            displayAIInsight(data.insight);
            showToast('AI insight generated!', 'success');
        } else {
            displayAIInsightError('Failed to generate insight');
        }
    } catch (error) {
        console.error('AI insight error:', error);
        showToast('Failed to generate AI insight. Check API key configuration.', 'error');
        displayAIInsightError('AI service unavailable');
    } finally {
        hideLoading();
    }
}

function displayAIInsight(insight) {
    document.getElementById('aiInsights').innerHTML = `
        <div class="ai-content">
            <p>${insight}</p>
        </div>
    `;
}

function displayAIInsightError(message) {
    document.getElementById('aiInsights').innerHTML = `
        <div class="empty-state">
            <p>${message}</p>
        </div>
    `;
}

// ============================================
// UI UTILITIES
// ============================================

function showLoading() {
    state.isLoading = true;
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('active');
}

function hideLoading() {
    state.isLoading = false;
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('active');
}

function updateBadge(elementId, text, type) {
    const badge = document.getElementById(elementId);
    if (!badge) return;
    
    badge.textContent = text;
    badge.className = 'card-badge';
    if (type) badge.classList.add(type);
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${getToastIcon(type)}</div>
        <div class="toast-message">${message}</div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, CONFIG.TOAST_DURATION);
}

function getToastIcon(type) {
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    return icons[type] || icons.info;
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function truncate(str, length) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// ERROR HANDLING
// ============================================

window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    showToast('An unexpected error occurred', 'error');
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred', 'error');
});

// ============================================
// EXPORT FOR TESTING
// ============================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        state,
        analyzeProduct,
        loadStats,
        loadProducts,
        getAIInsight
    };
}
