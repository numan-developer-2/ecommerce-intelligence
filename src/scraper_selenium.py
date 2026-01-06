# Web Scraping Engine - Selenium Version
"""
Production-Grade E-Commerce Web Scraper
Supports JavaScript-rendered sites using Selenium
Fallback to BeautifulSoup for static sites
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

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available. Install with: pip install selenium webdriver-manager")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EcommerceScraperSelenium:
    """
    Advanced E-commerce scraper with Selenium support
    Handles JavaScript-rendered content
    """

    def __init__(self, site_name: str = "daraz", headless: bool = True):
        self.site_name = site_name
        self.site_config = TARGET_SITES.get(site_name, {})
        self.headless = headless
        self.driver = None
        self.products = []

        if not self.site_config.get("enabled"):
            logger.warning(f"{site_name} is not enabled in config")

        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium webdriver-manager")

    def init_driver(self):
        """Initialize Selenium WebDriver"""
        if self.driver:
            return

        logger.info("Initializing Chrome WebDriver...")

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Disable images for faster loading (optional)
        # chrome_options.add_argument('--blink-settings=imagesEnabled=false')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("WebDriver closed")

    def generate_product_id(self, title: str, url: str) -> str:
        """Generate unique product ID"""
        unique_string = f"{title}{url}".encode('utf-8')
        return hashlib.md5(unique_string).hexdigest()[:12]

    def scrape_daraz_selenium(self, search_query: str, max_pages: int = 3) -> List[Dict]:
        """
        Scrape Daraz.pk using Selenium
        Handles JavaScript-rendered content
        """
        logger.info(f"Starting Daraz Selenium scraping for: {search_query}")
        products = []

        self.init_driver()

        for page in range(1, max_pages + 1):
            url = f"https://www.daraz.pk/catalog/?page={page}&q={search_query}"

            try:
                logger.info(f"Loading page {page}: {url}")
                self.driver.get(url)

                # Wait for products to load
                time.sleep(3)  # Initial wait

                # Scroll to load lazy-loaded content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # Try multiple selectors
                items = []

                # Method 1: Find by data-qa-locator (Verified)
                items = soup.find_all('div', {'data-qa-locator': 'product-item'})

                if not items:
                    # Fallback: Find by class 'Bm3ON'
                    items = soup.find_all('div', class_='Bm3ON')

                logger.info(f"Page {page}: Found {len(items)} product containers")

                # Extract data from items
                for item in items:
                    try:
                        # Extract title
                        # Selector: div.RfADt > a
                        title_elem = item.find('div', class_='RfADt')
                        if title_elem:
                            title_link = title_elem.find('a')
                            title = title_link.get('title') if title_link and title_link.get('title') else title_link.get_text(strip=True)
                        else:
                            # Fallback
                            title_elem = item.find('a', title=True)
                            title = title_elem['title'] if title_elem else item.get_text(strip=True)[:50]

                        if not title or len(title) < 5:
                            continue

                        # Extract price
                        # Selector: span.ooOxS
                        price_elem = item.find('span', class_='ooOxS')
                        if not price_elem:
                            # Fallback: look for currency text
                            price_elem = item.find('span', string=lambda x: x and ('Rs' in x or 'PKR' in x))

                        price = None
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price_text = price_text.replace('Rs.', '').replace('Rs', '').replace(',', '').strip()
                            try:
                                price = float(price_text)
                            except:
                                pass

                        if not price:
                            continue

                        # Extract URL
                        link_elem = item.find('div', class_='RfADt')
                        if link_elem and link_elem.find('a'):
                            link_elem = link_elem.find('a')
                        else:
                            link_elem = item.find('a', href=True)

                        product_url = ""
                        if link_elem:
                            href = link_elem.get('href', '')
                            if href.startswith('//'):
                                product_url = "https:" + href
                            elif href.startswith('/'):
                                product_url = self.site_config["base_url"] + href
                            elif href.startswith('http'):
                                product_url = href

                        # Extract rating (if available)
                        rating = None
                        # Look for rating stars or count
                        rating_container = item.find('div', class_='mdmmT') # Class for rating container often seen
                        if not rating_container:
                             rating_container = item.find('span', class_='rating')

                        if rating_container:
                            try:
                                # Try to find numeric rating
                                rating_text = rating_container.get_text(strip=True)
                                rating = float(rating_text)
                            except:
                                pass

                        # Extract review count
                        review_count = 0
                        review_elem = item.find('span', class_='qzqFw') # Class for review count
                        if review_elem:
                            try:
                                review_text = review_elem.get_text(strip=True)
                                review_count = int(''.join(filter(str.isdigit, review_text)))
                            except:
                                pass

                        # Extract brand
                        brand = self.extract_brand(title)

                        product_data = {
                            'product_id': self.generate_product_id(title, product_url),
                            'url': product_url,
                            'title': title,
                            'brand': brand,
                            'category': search_query,
                            'price': price,
                            'original_price': price,
                            'discount_pct': 0,
                            'rating': rating if rating else 4.0,  # Default rating
                            'review_count': review_count,
                            'availability': 'In Stock',
                            'scraped_at': datetime.now().isoformat()
                        }

                        products.append(product_data)

                    except Exception as e:
                        logger.debug(f"Error parsing item: {str(e)}")
                        continue

                logger.info(f"Page {page}: Successfully scraped {len([p for p in products if p.get('category') == search_query])} products")

                # Random delay between pages
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                logger.error(f"Error scraping page {page}: {str(e)}")
                continue

        logger.info(f"Total products scraped for '{search_query}': {len(products)}")
        return products

    def extract_brand(self, title: str) -> str:
        """
        Extract brand name from title
        """
        if not title:
            return "Unknown"

        # Common brand patterns
        brands = [
            'Apple', 'Samsung', 'Xiaomi', 'Oppo', 'Vivo', 'Realme', 'OnePlus',
            'HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'MSI', 'Sony',
            'JBL', 'Bose', 'Boat', 'Anker', 'Logitech'
        ]

        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand

        # Default to first word
        words = title.split()
        return words[0] if words else "Unknown"

    def scrape(self, search_query: str, max_pages: int = 3) -> pd.DataFrame:
        """
        Main scraping method
        """
        try:
            if self.site_name == "daraz":
                products = self.scrape_daraz_selenium(search_query, max_pages)
            else:
                logger.error(f"No scraper available for {self.site_name}")
                return pd.DataFrame()

            self.products = products
            df = pd.DataFrame(products)

            logger.info(f"Total products scraped: {len(df)}")
            return df

        finally:
            # Always close driver
            self.close_driver()

    def save_raw_data(self, df: pd.DataFrame, filename: Optional[str] = None):
        """Save scraped data to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_data_{self.site_name}_{timestamp}.csv"

        filepath = RAW_DATA_DIR / filename
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"Data saved to {filepath}")
        return filepath


# ============================================
# USAGE EXAMPLE
# ============================================
if __name__ == "__main__":
    # Initialize scraper
    scraper = EcommerceScraperSelenium(site_name="daraz", headless=True)

    # Define search queries
    search_queries = [
        "laptop",
        "smartphone"
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

        print(f"\n✓ Scraping completed!")
        print(f"Total unique products: {len(final_df)}")
        print(f"Data saved to: {RAW_DATA_DIR}")
