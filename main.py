"""
Main Execution Script
Orchestrates the complete pipeline
Easy to run entire project with one command
"""

import sys
import time
from pathlib import Path
import logging
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from config import *
from scraper_selenium import EcommerceScraperSelenium
from etl_pipeline import DataCleaner
from price_forecast import PriceForecaster
from demand_prediction import DemandPredictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Orchestrates the complete data pipeline
    From scraping to model training
    """

    def __init__(self):
        self.start_time = None
        self.results = {}

    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70 + "\n")

    def step_1_scraping(self, queries=['laptop', 'smartphone'], pages=2):
        """Step 1: Web Scraping"""
        self.print_header("STEP 1: WEB SCRAPING")

        try:
            scraper = EcommerceScraperSelenium(site_name="daraz", headless=True)
            all_data = []

            for query in queries:
                logger.info(f"Scraping: {query}")
                df = scraper.scrape(search_query=query, max_pages=pages)
                all_data.append(df)
                time.sleep(3)  # Delay between queries

            if all_data:
                import pandas as pd
                final_df = pd.concat(all_data, ignore_index=True)
                final_df.drop_duplicates(subset=['product_id'], inplace=True)

                filepath = scraper.save_raw_data(final_df)

                self.results['scraping'] = {
                    'status': 'success',
                    'products': len(final_df),
                    'file': filepath
                }

                logger.info(f"Scraped {len(final_df)} products")
                return True

        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            self.results['scraping'] = {'status': 'failed', 'error': str(e)}
            return False

    def step_2_cleaning(self):
        """Step 2: Data Cleaning"""
        self.print_header("STEP 2: DATA CLEANING & ETL")

        try:
            cleaner = DataCleaner()
            cleaned_data = cleaner.run_pipeline()
            filepath = cleaner.save_cleaned_data()
            cleaner.generate_summary_report()

            self.results['cleaning'] = {
                'status': 'success',
                'records': len(cleaned_data),
                'file': filepath
            }

            logger.info(f"Cleaned {len(cleaned_data)} records")
            return True

        except Exception as e:
            logger.error(f"Cleaning failed: {str(e)}")
            self.results['cleaning'] = {'status': 'failed', 'error': str(e)}
            return False

    def step_3_forecasting(self, n_products=5):
        """Step 3: Price Forecasting"""
        self.print_header("STEP 3: PRICE FORECASTING")

        try:
            forecaster = PriceForecaster()
            forecaster.load_data()

            # Get top products
            product_ids = forecaster.df['product_id'].value_counts().head(n_products).index.tolist()

            forecasts = {}
            for pid in product_ids:
                summary = forecaster.get_forecast_summary(pid, days=14)
                if summary:
                    forecasts[pid] = summary
                    logger.info(f"Forecasted: {pid} - Trend: {summary['trend']}")

            # Save a model
            if product_ids:
                forecaster.save_model(product_ids[0], "sample_forecast_model.pkl")

            self.results['forecasting'] = {
                'status': 'success',
                'products_forecasted': len(forecasts)
            }

            logger.info(f"Generated forecasts for {len(forecasts)} products")
            return True

        except Exception as e:
            logger.error(f"Forecasting failed: {str(e)}")
            self.results['forecasting'] = {'status': 'failed', 'error': str(e)}
            return False

    def step_4_demand_prediction(self):
        """Step 4: Demand Prediction"""
        self.print_header("STEP 4: DEMAND PREDICTION")

        try:
            predictor = DemandPredictor()
            predictor.load_data()
            predictor.create_synthetic_demand()
            predictor.engineer_features()

            metrics = predictor.train_model()
            predictor.save_model()

            self.results['demand'] = {
                'status': 'success',
                'accuracy': metrics['accuracy_pct'],
                'rmse': metrics['RMSE']
            }

            logger.info(f"Model trained - Accuracy: {metrics['accuracy_pct']}%")
            return True

        except Exception as e:
            logger.error(f"Demand prediction failed: {str(e)}")
            self.results['demand'] = {'status': 'failed', 'error': str(e)}
            return False

    def step_5_excel_dashboard(self):
        """Step 5: Generate Excel Dashboard"""
        self.print_header("STEP 5: EXCEL DASHBOARD")

        try:
            import pandas as pd
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            from openpyxl.chart import BarChart, LineChart, Reference

            # Load cleaned data
            data_file = get_latest_cleaned_file()
            df = pd.read_csv(data_file)

            # Create Excel file
            excel_file = BASE_DIR / "dashboard" / "price_intelligence_dashboard.xlsx"
            excel_file.parent.mkdir(exist_ok=True)

            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Raw data sheet
                df.to_excel(writer, sheet_name='Raw Data', index=False)

                # Summary statistics
                summary = pd.DataFrame({
                    'Metric': ['Total Products', 'Avg Price', 'Avg Rating', 'Products on Sale'],
                    'Value': [
                        len(df),
                        df['price'].mean(),
                        df['rating'].mean(),
                        (df['discount_pct'] > 0).sum()
                    ]
                })
                summary.to_excel(writer, sheet_name='Summary', index=False)

                # Category analysis
                category_stats = df.groupby('category').agg({
                    'price': 'mean',
                    'rating': 'mean',
                    'product_id': 'count'
                }).round(2)
                category_stats.to_excel(writer, sheet_name='Category Analysis')

            self.results['dashboard'] = {
                'status': 'success',
                'file': excel_file
            }

            logger.info(f"Excel dashboard created: {excel_file}")
            return True

        except Exception as e:
            logger.error(f"Dashboard creation failed: {str(e)}")
            self.results['dashboard'] = {'status': 'failed', 'error': str(e)}
            return False

    def run_complete_pipeline(self):
        """Execute complete pipeline"""
        self.start_time = time.time()

        print("\n" + "="*70)
        print("  E-COMMERCE INTELLIGENCE SYSTEM - COMPLETE PIPELINE")
        print("="*70 + "\n")

        # Run all steps
        steps = [
            ("Scraping", lambda: self.step_1_scraping()),
            ("Cleaning", self.step_2_cleaning),
            ("Forecasting", self.step_3_forecasting),
            ("Demand Prediction", self.step_4_demand_prediction),
            ("Excel Dashboard", self.step_5_excel_dashboard)
        ]

        for step_name, step_func in steps:
            success = step_func()
            if not success:
                logger.warning(f"{step_name} encountered issues, continuing...")

        # Print final report
        self.print_final_report()

    def print_final_report(self):
        """Print execution summary"""
        elapsed = time.time() - self.start_time

        self.print_header("EXECUTION SUMMARY")

        print(f"Total Execution Time: {elapsed:.2f} seconds\n")

        print("Pipeline Results:\n")
        for step, result in self.results.items():
            status_icon = "[OK]" if result['status'] == 'success' else "[FAIL]"
            print(f"  {status_icon} {step.upper()}: {result['status']}")

            # Print additional info
            if result['status'] == 'success':
                for key, value in result.items():
                    if key != 'status':
                        print(f"      - {key}: {value}")

        print("\n" + "="*70)
        print("  PIPELINE EXECUTION COMPLETED")
        print("="*70 + "\n")

        print("Next Steps:")
        print("  1. Review Excel dashboard in /dashboard folder")
        print("  2. Start API server: python src/api_server.py")
        print("  3. Open frontend/index.html for web dashboard")
        print("  4. Check logs in /logs folder")
        print()


# ============================================
# COMMAND LINE INTERFACE
# ============================================

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='E-Commerce Intelligence Pipeline')
    parser.add_argument('--step', type=str, help='Run specific step: scrape, clean, forecast, demand, dashboard, all')
    parser.add_argument('--queries', nargs='+', default=['laptop', 'smartphone'], help='Search queries for scraping')
    parser.add_argument('--pages', type=int, default=2, help='Pages to scrape per query')

    args = parser.parse_args()

    orchestrator = PipelineOrchestrator()

    if args.step == 'scrape':
        orchestrator.step_1_scraping(queries=args.queries, pages=args.pages)
    elif args.step == 'clean':
        orchestrator.step_2_cleaning()
    elif args.step == 'forecast':
        orchestrator.step_3_forecasting()
    elif args.step == 'demand':
        orchestrator.step_4_demand_prediction()
    elif args.step == 'dashboard':
        orchestrator.step_5_excel_dashboard()
    else:
        # Run complete pipeline
        orchestrator.run_complete_pipeline()


if __name__ == "__main__":
    main()
