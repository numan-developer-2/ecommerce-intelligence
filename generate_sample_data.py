"""
Generate sample data for testing the pipeline
This will help test the rest of the pipeline while we fix the scraper
"""
import pandas as pd
from datetime import datetime
import random
import hashlib
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Sample product data
brands = ['HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'Samsung', 'Xiaomi', 'Oppo', 'Vivo', 'Realme', 'Apple', 'OnePlus']
laptop_models = ['ProBook', 'Inspiron', 'ThinkPad', 'VivoBook', 'Aspire', 'Pavilion', 'Latitude', 'IdeaPad']
phone_models = ['Galaxy', 'Note', 'Redmi', 'A-Series', 'F-Series', 'iPhone', 'Nord']

products = []

# Generate laptop data
for i in range(30):
    brand = random.choice(brands[:7])  # Laptop brands
    model = random.choice(laptop_models)
    title = f"{brand} {model} {random.choice(['i3', 'i5', 'i7', 'Ryzen 5', 'Ryzen 7'])} {random.choice(['8GB', '16GB'])} RAM {random.choice(['256GB', '512GB', '1TB'])} SSD"

    price = random.randint(40000, 150000)
    original_price = price + random.randint(0, 20000)
    discount_pct = round(((original_price - price) / original_price) * 100, 2) if original_price > price else 0

    product_id = hashlib.md5(f"{title}{i}".encode()).hexdigest()[:12]

    products.append({
        'product_id': product_id,
        'url': f'https://www.daraz.pk/products/laptop-{product_id}.html',
        'title': title,
        'brand': brand,
        'category': 'laptop',
        'price': price,
        'original_price': original_price,
        'discount_pct': discount_pct,
        'rating': round(random.uniform(3.5, 5.0), 1),
        'review_count': random.randint(10, 500),
        'availability': 'In Stock',
        'scraped_at': datetime.now().isoformat()
    })

# Generate smartphone data
for i in range(30):
    brand = random.choice(brands[3:])  # Phone brands
    model = random.choice(phone_models)
    title = f"{brand} {model} {random.choice(['4GB', '6GB', '8GB', '12GB'])} RAM {random.choice(['64GB', '128GB', '256GB'])} Storage"

    price = random.randint(15000, 120000)
    original_price = price + random.randint(0, 15000)
    discount_pct = round(((original_price - price) / original_price) * 100, 2) if original_price > price else 0

    product_id = hashlib.md5(f"{title}{i}".encode()).hexdigest()[:12]

    products.append({
        'product_id': product_id,
        'url': f'https://www.daraz.pk/products/smartphone-{product_id}.html',
        'title': title,
        'brand': brand,
        'category': 'smartphone',
        'price': price,
        'original_price': original_price,
        'discount_pct': discount_pct,
        'rating': round(random.uniform(3.5, 5.0), 1),
        'review_count': random.randint(10, 500),
        'availability': 'In Stock',
        'scraped_at': datetime.now().isoformat()
    })

# Create DataFrame
df = pd.DataFrame(products)

# Save to CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"raw_data_daraz_{timestamp}.csv"
filepath = RAW_DATA_DIR / filename

df.to_csv(filepath, index=False, encoding='utf-8-sig')

print("=" * 70)
print("SAMPLE DATA GENERATED SUCCESSFULLY")
print("=" * 70)
print(f"\nTotal Products: {len(df)}")
print(f"Laptops: {len(df[df['category'] == 'laptop'])}")
print(f"Smartphones: {len(df[df['category'] == 'smartphone'])}")
print(f"\nFile saved to: {filepath}")
print(f"\nPrice Range: Rs. {df['price'].min():,.0f} - Rs. {df['price'].max():,.0f}")
print(f"Average Price: Rs. {df['price'].mean():,.0f}")
print(f"Average Rating: {df['rating'].mean():.2f}")
print(f"Products on Discount: {(df['discount_pct'] > 0).sum()}")
print("\n" + "=" * 70)
print("You can now run the pipeline with this sample data!")
print("Command: python main.py")
print("=" * 70)
