# Web Scraping Engine
"""
Production-Grade E-Commerce Web Scraper
Supports multiple sites with easy configuration
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional
import hashlib
from config import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EcommerceScraper:
    """
    Universal E-commerce scraper
    Easily extensible for new websites
    """

    def __init__(self, site_name: str = "daraz"):
        self.site_name = site_name
        self.site_config = TARGET_SITES.get(site_name, {})
        self.session = requests.Session()
        self.products = []

        if not self.site_config.get("enabled"):
            logger.warning(f"{site_name} is not enabled in config")

    def get_random_user_agent(self) -> str:
        """Return random user agent to avoid blocking"""
        return random.choice(SCRAPING_CONFIG["user_agents"])

    def make_request(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Make HTTP request with retry logic
        """
        headers = {"User-Agent": self.get_random_user_agent()}

        for attempt in range(retries):
            try:
                time.sleep(random.uniform(*SCRAPING_CONFIG["delay_range"]))

                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=SCRAPING_CONFIG["timeout"],
                    verify=SCRAPING_CONFIG["verify_ssl"]
                )

                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
                else:
                    logger.warning(f"Status {response.status_code} for {url}")

            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff

        return None

    def generate_product_id(self, title: str, url: str) -> str:
        """Generate unique product ID"""
        unique_string = f"{title}{url}".encode('utf-8')
        return hashlib.md5(unique_string).hexdigest()[:12]

    def scrape_daraz(self, search_query: str, max_pages: int = 3) -> List[Dict]:
        """
        Scrape Daraz.pk
        Modify selectors if website structure changes
        """
        logger.info(f"Starting Daraz scraping for: {search_query}")
        products = []

        for page in range(1, max_pages + 1):
            url = f"https://www.daraz.pk/catalog/?page={page}&q={search_query}"
            soup = self.make_request(url)

            if not soup:
                continue

            # Find product containers (update selector if needed)
            items = soup.find_all('div', {'data-qa-locator': 'product-item'})

            for item in items:
                try:
                    # Extract data (modify selectors as needed)
                    title_elem = item.find('div', class_='title')
                    price_elem = item.find('span', class_='currency')
                    rating_elem = item.find('span', class_='rating')

                    if not title_elem or not price_elem:
                        continue

                    title = title_elem.text.strip()
                    price_text = price_elem.text.strip().replace('Rs. ', '').replace(',', '')

                    try:
                        price = float(price_text)
                    except:
                        price = None

                    # Get product URL
                    link_elem = item.find('a')
                    product_url = self.site_config["base_url"] + link_elem['href'] if link_elem else ""

                    # Extract rating
                    rating = None
                    if rating_elem:
                        try:
                            rating = float(rating_elem.text.strip())
                        except:
                            pass

                    product_data = {
                        'product_id': self.generate_product_id(title, product_url),
                        'url': product_url,
                        'title': title,
                        'brand': self.extract_brand(title),
                        'category': search_query,
                        'price': price,
                        'original_price': price,  # Will be updated if discount found
                        'discount_pct': 0,
                        'rating': rating,
                        'review_count': 0,
                        'availability': 'In Stock',
                        'scraped_at': datetime.now().isoformat()
                    }

                    products.append(product_data)

                except Exception as e:
                    logger.error(f"Error parsing item: {str(e)}")
                    continue

            logger.info(f"Page {page}: Scraped {len(items)} items")

        return products

    def scrape_amazon(self, search_query: str, max_pages: int = 3) -> List[Dict]:
        """
        Scrape Amazon (template - needs customization)
        Add your Amazon scraping logic here
        """
        logger.info("Amazon scraping not yet implemented")
        return []

    def extract_brand(self, title: str) -> str:
        """
        Extract brand name from title
        Customize based on common patterns
        """
        # Simple extraction - first word often is brand
        words = title.split()
        return words[0] if words else "Unknown"

    def scrape(self, search_query: str, max_pages: int = 3) -> pd.DataFrame:
        """
        Main scraping method
        Routes to appropriate scraper
        """
        if self.site_name == "daraz":
            products = self.scrape_daraz(search_query, max_pages)
        elif self.site_name == "amazon":
            products = self.scrape_amazon(search_query, max_pages)
        else:
            logger.error(f"No scraper available for {self.site_name}")
            return pd.DataFrame()

        self.products = products
        df = pd.DataFrame(products)

        logger.info(f"Total products scraped: {len(df)}")
        return df

    def save_raw_data(self, df: pd.DataFrame, filename: Optional[str] = None):
        """Save scraped data to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_data_{self.site_name}_{timestamp}.csv"

        filepath = RAW_DATA_DIR / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Data saved to {filepath}")
        return filepath


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    # Initialize scraper
    scraper = EcommerceScraper(site_name="daraz")

    # Define search queries
    search_queries = [
        "laptop",
        "smartphone",
        "headphones"
    ]

    all_data = []

    for query in search_queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"Scraping: {query}")
        logger.info(f"{'='*50}\n")

        # Scrape data
        df = scraper.scrape(search_query=query, max_pages=2)
        all_data.append(df)

        # Small delay between queries
        time.sleep(random.uniform(3, 6))

    # Combine all data
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)

        # Remove duplicates
        final_df.drop_duplicates(subset=['product_id'], inplace=True)

        # Save
        scraper.save_raw_data(final_df)

        print(f"\n✅ Scraping completed!")
        print(f"📊 Total unique products: {len(final_df)}")
        print(f"💾 Data saved to: {RAW_DATA_DIR}")
