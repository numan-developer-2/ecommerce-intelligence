# Data Cleaning Pipeline
"""
ETL Pipeline - Extract, Transform, Load
Clean and prepare data for analysis and ML
"""

import pandas as pd
import numpy as np
import re
import logging
from datetime import datetime
from pathlib import Path
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaning and transformation pipeline
    Modular and easy to extend
    """

    def __init__(self, input_file: Path = None):
        self.input_file = input_file or get_latest_raw_file()
        self.df = None
        self.cleaned_df = None

        if self.input_file is None:
            raise FileNotFoundError("No raw data file found!")

    def load_data(self) -> pd.DataFrame:
        """Load raw data"""
        logger.info(f"Loading data from {self.input_file}")
        self.df = pd.read_csv(self.input_file)
        logger.info(f"Loaded {len(self.df)} records")
        return self.df

    def clean_price_column(self):
        """Clean and standardize price data"""
        logger.info("Cleaning price columns...")

        def clean_price(price):
            if pd.isna(price):
                return None

            # Remove currency symbols and commas
            price_str = str(price).replace('Rs.', '').replace(',', '').strip()

            try:
                return float(price_str)
            except:
                return None

        self.df['price'] = self.df['price'].apply(clean_price)
        self.df['original_price'] = self.df['original_price'].apply(clean_price)

        # Fill missing original_price with current price
        self.df['original_price'].fillna(self.df['price'], inplace=True)

    def calculate_discount(self):
        """Calculate discount percentage"""
        logger.info("Calculating discounts...")

        self.df['discount_pct'] = np.where(
            (self.df['original_price'] > 0) & (self.df['price'] > 0),
            ((self.df['original_price'] - self.df['price']) / self.df['original_price']) * 100,
            0
        )

        # Round to 2 decimal places
        self.df['discount_pct'] = self.df['discount_pct'].round(2)

    def clean_rating(self):
        """Clean rating column"""
        logger.info("Cleaning ratings...")

        self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce')

        # Rating should be between 0-5
        self.df['rating'] = self.df['rating'].clip(0, 5)

        # Fill missing ratings with median
        median_rating = self.df['rating'].median()
        self.df['rating'].fillna(median_rating, inplace=True)

    def clean_text_fields(self):
        """Clean title and brand columns"""
        logger.info("Cleaning text fields...")

        # Clean title
        self.df['title'] = self.df['title'].str.strip()
        self.df['title'] = self.df['title'].str.replace(r'\s+', ' ', regex=True)

        # Extract brand if not present
        if 'brand' not in self.df.columns or self.df['brand'].isna().sum() > 0:
            self.df['brand'] = self.df['title'].apply(self.extract_brand)

        # Clean category
        if 'category' in self.df.columns:
            self.df['category'] = self.df['category'].str.title()

    def extract_brand(self, title: str) -> str:
        """
        Extract brand from title using patterns
        Customize based on your data
        """
        if pd.isna(title):
            return "Unknown"

        # Common brand patterns
        brands = [
            'Apple', 'Samsung', 'Xiaomi', 'Oppo', 'Vivo', 'Realme',
            'HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'Sony',
            'JBL', 'Bose', 'Boat', 'OnePlus'
        ]

        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand

        # Default to first word
        return title.split()[0] if title else "Unknown"

    def handle_missing_values(self):
        """Handle missing values strategically"""
        logger.info("Handling missing values...")

        # Fill missing review counts with 0
        if 'review_count' in self.df.columns:
            self.df['review_count'].fillna(0, inplace=True)

        # Fill missing availability
        if 'availability' in self.df.columns:
            self.df['availability'].fillna('Unknown', inplace=True)

        # Drop rows with missing critical fields
        critical_cols = ['product_id', 'title', 'price']
        self.df.dropna(subset=critical_cols, inplace=True)

    def remove_duplicates(self):
        """Remove duplicate products"""
        logger.info("Removing duplicates...")

        initial_count = len(self.df)
        self.df.drop_duplicates(subset=['product_id'], keep='first', inplace=True)

        duplicates_removed = initial_count - len(self.df)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate records")

    def add_derived_features(self):
        """Add useful features for analysis"""
        logger.info("Adding derived features...")

        # Price range categories
        self.df['price_range'] = pd.cut(
            self.df['price'],
            bins=[0, 5000, 20000, 50000, float('inf')],
            labels=['Budget', 'Mid-Range', 'Premium', 'Luxury']
        )

        # Rating category
        self.df['rating_category'] = pd.cut(
            self.df['rating'],
            bins=[0, 2, 3.5, 4.5, 5],
            labels=['Poor', 'Average', 'Good', 'Excellent']
        )

        # Is discounted
        self.df['is_discounted'] = self.df['discount_pct'] > 0

        # Extract date components
        if 'scraped_at' in self.df.columns:
            self.df['scraped_at'] = pd.to_datetime(self.df['scraped_at'])
            self.df['scrape_date'] = self.df['scraped_at'].dt.date
            self.df['scrape_hour'] = self.df['scraped_at'].dt.hour

    def validate_data(self):
        """Validate cleaned data"""
        logger.info("Validating data...")

        issues = []

        # Check for negative prices
        if (self.df['price'] < 0).any():
            issues.append("Negative prices found")

        # Check for invalid ratings
        if ((self.df['rating'] < 0) | (self.df['rating'] > 5)).any():
            issues.append("Invalid ratings found")

# Data Cleaning Pipeline
"""
ETL Pipeline - Extract, Transform, Load
Clean and prepare data for analysis and ML
"""

import pandas as pd
import numpy as np
import re
import logging
from datetime import datetime
from pathlib import Path
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaning and transformation pipeline
    Modular and easy to extend
    """

    def __init__(self, input_file: Path = None):
        self.input_file = input_file or get_latest_raw_file()
        self.df = None
        self.cleaned_df = None

        if self.input_file is None:
            raise FileNotFoundError("No raw data file found!")

    def load_data(self) -> pd.DataFrame:
        """Load raw data"""
        logger.info(f"Loading data from {self.input_file}")
        self.df = pd.read_csv(self.input_file)
        logger.info(f"Loaded {len(self.df)} records")
        return self.df

    def clean_price_column(self):
        """Clean and standardize price data"""
        logger.info("Cleaning price columns...")

        def clean_price(price):
            if pd.isna(price):
                return None

            # Remove currency symbols and commas
            price_str = str(price).replace('Rs.', '').replace(',', '').strip()

            try:
                return float(price_str)
            except:
                return None

        self.df['price'] = self.df['price'].apply(clean_price)
        self.df['original_price'] = self.df['original_price'].apply(clean_price)

        # Fill missing original_price with current price
        self.df['original_price'].fillna(self.df['price'], inplace=True)

    def calculate_discount(self):
        """Calculate discount percentage"""
        logger.info("Calculating discounts...")

        self.df['discount_pct'] = np.where(
            (self.df['original_price'] > 0) & (self.df['price'] > 0),
            ((self.df['original_price'] - self.df['price']) / self.df['original_price']) * 100,
            0
        )

        # Round to 2 decimal places
        self.df['discount_pct'] = self.df['discount_pct'].round(2)

    def clean_rating(self):
        """Clean rating column"""
        logger.info("Cleaning ratings...")

        self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce')

        # Rating should be between 0-5
        self.df['rating'] = self.df['rating'].clip(0, 5)

        # Fill missing ratings with median
        median_rating = self.df['rating'].median()
        self.df['rating'].fillna(median_rating, inplace=True)

    def clean_text_fields(self):
        """Clean title and brand columns"""
        logger.info("Cleaning text fields...")

        # Clean title
        self.df['title'] = self.df['title'].str.strip()
        self.df['title'] = self.df['title'].str.replace(r'\s+', ' ', regex=True)

        # Extract brand if not present
        if 'brand' not in self.df.columns or self.df['brand'].isna().sum() > 0:
            self.df['brand'] = self.df['title'].apply(self.extract_brand)

        # Clean category
        if 'category' in self.df.columns:
            self.df['category'] = self.df['category'].str.title()

    def extract_brand(self, title: str) -> str:
        """
        Extract brand from title using patterns
        Customize based on your data
        """
        if pd.isna(title):
            return "Unknown"

        # Common brand patterns
        brands = [
            'Apple', 'Samsung', 'Xiaomi', 'Oppo', 'Vivo', 'Realme',
            'HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'Sony',
            'JBL', 'Bose', 'Boat', 'OnePlus'
        ]

        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand

        # Default to first word
        return title.split()[0] if title else "Unknown"

    def handle_missing_values(self):
        """Handle missing values strategically"""
        logger.info("Handling missing values...")

        # Fill missing review counts with 0
        if 'review_count' in self.df.columns:
            self.df['review_count'].fillna(0, inplace=True)

        # Fill missing availability
        if 'availability' in self.df.columns:
            self.df['availability'].fillna('Unknown', inplace=True)

        # Drop rows with missing critical fields
        critical_cols = ['product_id', 'title', 'price']
        self.df.dropna(subset=critical_cols, inplace=True)

    def remove_duplicates(self):
        """Remove duplicate products"""
        logger.info("Removing duplicates...")

        initial_count = len(self.df)
        self.df.drop_duplicates(subset=['product_id'], keep='first', inplace=True)

        duplicates_removed = initial_count - len(self.df)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate records")

    def add_derived_features(self):
        """Add useful features for analysis"""
        logger.info("Adding derived features...")

        # Price range categories
        self.df['price_range'] = pd.cut(
            self.df['price'],
            bins=[0, 5000, 20000, 50000, float('inf')],
            labels=['Budget', 'Mid-Range', 'Premium', 'Luxury']
        )

        # Rating category
        self.df['rating_category'] = pd.cut(
            self.df['rating'],
            bins=[0, 2, 3.5, 4.5, 5],
            labels=['Poor', 'Average', 'Good', 'Excellent']
        )

        # Is discounted
        self.df['is_discounted'] = self.df['discount_pct'] > 0

        # Extract date components
        if 'scraped_at' in self.df.columns:
            self.df['scraped_at'] = pd.to_datetime(self.df['scraped_at'])
            self.df['scrape_date'] = self.df['scraped_at'].dt.date
            self.df['scrape_hour'] = self.df['scraped_at'].dt.hour

    def validate_data(self):
        """Validate cleaned data"""
        logger.info("Validating data...")

        issues = []

        # Check for negative prices
        if (self.df['price'] < 0).any():
            issues.append("Negative prices found")

        # Check for invalid ratings
        if ((self.df['rating'] < 0) | (self.df['rating'] > 5)).any():
            issues.append("Invalid ratings found")

        # Check for missing product IDs
        if self.df['product_id'].isna().any():
            issues.append("Missing product IDs found")

        if issues:
            logger.warning(f"Validation issues: {', '.join(issues)}")
        else:
            logger.info("[OK] Data validation passed")

    def run_pipeline(self) -> pd.DataFrame:
        """Execute complete ETL pipeline"""
        logger.info("\n" + "="*50)
        logger.info("Starting ETL Pipeline")
        logger.info("="*50 + "\n")

        # Load data
        self.load_data()

        # Cleaning steps
        self.clean_price_column()
        self.calculate_discount()
        self.clean_rating()
        self.clean_text_fields()
        self.handle_missing_values()
        self.remove_duplicates()
        self.add_derived_features()
        self.validate_data()

        self.cleaned_df = self.df.copy()

        logger.info(f"\n[OK] Pipeline completed!")
        logger.info(f"Final records: {len(self.cleaned_df)}")

        return self.cleaned_df

    def save_cleaned_data(self, filename: str = None):
        """Save cleaned data"""
        if self.cleaned_df is None:
            raise ValueError("No cleaned data available. Run pipeline first.")

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cleaned_data_{timestamp}.csv"

        filepath = CLEANED_DATA_DIR / filename
        self.cleaned_df.to_csv(filepath, index=False)
        logger.info(f"Cleaned data saved to {filepath}")
        return filepath

    def generate_summary_report(self):
        """Generate data quality report"""
        if self.cleaned_df is None:
            return

        print("\n" + "="*50)
        print("DATA SUMMARY REPORT")
        print("="*50)

        print(f"\nDataset Shape: {self.cleaned_df.shape}")
        print(f"Total Products: {len(self.cleaned_df)}")
        print(f"Unique Brands: {self.cleaned_df['brand'].nunique()}")
        print(f"Categories: {self.cleaned_df['category'].nunique()}")

        print(f"\nPrice Statistics:")
        print(f"   Average: Rs. {self.cleaned_df['price'].mean():.2f}")
        print(f"   Median: Rs. {self.cleaned_df['price'].median():.2f}")
        print(f"   Min: Rs. {self.cleaned_df['price'].min():.2f}")
        print(f"   Max: Rs. {self.cleaned_df['price'].max():.2f}")

        print(f"\nRating Statistics:")
        print(f"   Average: {self.cleaned_df['rating'].mean():.2f}")
        print(f"   Products with 4+ rating: {(self.cleaned_df['rating'] >= 4).sum()}")

        print(f"\nDiscount Statistics:")
        discounted = (self.cleaned_df['discount_pct'] > 0).sum()
        print(f"   Products on discount: {discounted} ({discounted/len(self.cleaned_df)*100:.1f}%)")
        print(f"   Average discount: {self.cleaned_df['discount_pct'].mean():.2f}%")

        print("\n" + "="*50)


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    # Initialize cleaner
    cleaner = DataCleaner()

    # Run pipeline
    cleaned_data = cleaner.run_pipeline()

    # Save cleaned data
    cleaner.save_cleaned_data()

    # Generate report
    cleaner.generate_summary_report()

    print("\n[OK] ETL Pipeline executed successfully!")
