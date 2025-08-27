"""
Main orchestrator for Zara product scraping and database operations

This script runs the complete pipeline: scraping products and storing them in the database.
Designed to be run daily via scheduled job.
"""

import logging
import sys
from datetime import datetime
from typing import List
import argparse

from zara_scraper import ZaraScraper, ZaraProduct
from database_manager import get_database_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'zara_scraper_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)

class ZaraScrapingPipeline:
    """Main pipeline for scraping and storing Zara products"""
    
    def __init__(self, target_url: str = None):
        self.scraper = ZaraScraper(target_url) if target_url else ZaraScraper()
        self.db_manager = get_database_manager()
        self.stats = {
            'start_time': None,
            'end_time': None,
            'products_scraped': 0,
            'products_saved': 0,
            'errors': []
        }
    
    def run(self, cleanup_old: bool = True, cleanup_days: int = 30) -> bool:
        """Run the complete scraping and storage pipeline"""
        logger.info("Starting Zara scraping pipeline...")
        self.stats['start_time'] = datetime.now()
        
        try:
            # Ensure database table exists
            if not self.db_manager.create_table_if_not_exists():
                raise Exception("Failed to create database table")
            
            # Scrape products
            logger.info("Scraping products from Zara...")
            products = self.scraper.scrape_products()
            self.stats['products_scraped'] = len(products)
            
            if not products:
                logger.warning("No products scraped")
                return False
            
            # Save to database
            logger.info(f"Saving {len(products)} products to database...")
            success = self.db_manager.save_products(products)
            
            if success:
                self.stats['products_saved'] = len(products)
                logger.info(f"Successfully saved {len(products)} products")
            else:
                raise Exception("Failed to save products to database")
            
            # Cleanup old records
            if cleanup_old:
                logger.info(f"Cleaning up products older than {cleanup_days} days...")
                self.db_manager.delete_old_products(cleanup_days)
            
            # Get final statistics
            db_stats = self.db_manager.get_statistics()
            logger.info(f"Database now contains {db_stats.get('total_products', 0)} total products")
            
            self.stats['end_time'] = datetime.now()
            self._log_final_stats()
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.stats['errors'].append(str(e))
            self.stats['end_time'] = datetime.now()
            self._log_final_stats()
            return False
    
    def _log_final_stats(self):
        """Log final pipeline statistics"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        logger.info("=== PIPELINE SUMMARY ===")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Products scraped: {self.stats['products_scraped']}")
        logger.info(f"Products saved: {self.stats['products_saved']}")
        
        if self.stats['errors']:
            logger.error(f"Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.error(f"  - {error}")
        else:
            logger.info("Pipeline completed successfully with no errors")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Zara Product Scraper')
    parser.add_argument(
        '--url', 
        type=str, 
        help='Zara URL to scrape (default: men\'s section)'
    )
    parser.add_argument(
        '--no-cleanup', 
        action='store_true', 
        help='Skip cleanup of old products'
    )
    parser.add_argument(
        '--cleanup-days', 
        type=int, 
        default=30, 
        help='Days to keep products (default: 30)'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help='Run scraping but don\'t save to database'
    )
    parser.add_argument(
        '--stats-only', 
        action='store_true', 
        help='Only show database statistics'
    )
    
    args = parser.parse_args()
    
    # Just show statistics
    if args.stats_only:
        db_manager = get_database_manager()
        stats = db_manager.get_statistics()
        print("\n=== DATABASE STATISTICS ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
        return
    
    # Run dry run
    if args.dry_run:
        logger.info("Running in DRY RUN mode - no database writes")
        scraper = ZaraScraper(args.url) if args.url else ZaraScraper()
        products = scraper.scrape_products()
        print(f"\nDry run complete: {len(products)} products would be saved")
        
        if products:
            print("\nSample products:")
            for i, product in enumerate(products[:3], 1):
                print(f"{i}. {product.name} - {product.price}")
        return
    
    # Run full pipeline
    pipeline = ZaraScrapingPipeline(args.url)
    success = pipeline.run(
        cleanup_old=not args.no_cleanup,
        cleanup_days=args.cleanup_days
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()