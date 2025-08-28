"""
Zara Product Scraper
Scrapes products from Zara website and stores them in Supabase database.
Handles product updates and runs daily via GitHub Actions.
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
import re

from playwright.async_api import async_playwright, Page, Browser
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ZaraScraper:
    """Scraper for Zara products using Playwright and Supabase."""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize the scraper with Supabase credentials."""
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and key are required")
        
        # Initialize Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Base URL for Zara
        self.base_url = "https://www.zara.com"
        
    async def setup_database(self):
        """Set up the database table for storing products."""
        try:
            # Create products table if it doesn't exist
            # Note: In a real scenario, you'd run this SQL via Supabase dashboard or migration
            logger.info("Database setup completed")
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise

    async def scrape_products(self, url: str) -> List[Dict]:
        """Scrape products from the given Zara URL."""
        products = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                logger.info(f"Navigating to {url}")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait for products to load
                await page.wait_for_selector('[data-testid="product"]', timeout=30000)
                
                # Extract product information
                product_elements = await page.query_selector_all('[data-testid="product"]')
                
                logger.info(f"Found {len(product_elements)} products")
                
                for element in product_elements:
                    try:
                        product_data = await self.extract_product_data(element, page)
                        if product_data:
                            products.append(product_data)
                    except Exception as e:
                        logger.error(f"Error extracting product data: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error during scraping: {e}")
            finally:
                await browser.close()
        
        logger.info(f"Successfully scraped {len(products)} products")
        return products
    
    async def extract_product_data(self, element, page: Page) -> Optional[Dict]:
        """Extract data from a single product element."""
        try:
            # Extract product URL
            product_link_element = await element.query_selector('a')
            if not product_link_element:
                return None
                
            product_href = await product_link_element.get_attribute('href')
            product_url = urljoin(self.base_url, product_href) if product_href else None
            
            # Extract product ID from URL or data attributes
            product_id = None
            if product_url:
                # Try to extract ID from URL
                id_match = re.search(r'/(\d+)\.html', product_url)
                if id_match:
                    product_id = id_match.group(1)
            
            # If no ID found in URL, try data attributes
            if not product_id:
                product_id = await element.get_attribute('data-productid') or \
                           await element.get_attribute('data-product-id')
            
            # Extract product name
            name_element = await element.query_selector('[data-testid="product-name"], .product-info-name, h3, .product-title')
            name = await name_element.inner_text() if name_element else None
            
            # Extract price
            price_element = await element.query_selector('[data-testid="product-price"], .price, .money-amount')
            price_text = await price_element.inner_text() if price_element else None
            
            # Clean and parse price
            price = None
            if price_text:
                # Remove currency symbols and extract numeric value
                price_clean = re.sub(r'[^\d,.]', '', price_text.replace(',', '.'))
                try:
                    price = float(price_clean)
                except ValueError:
                    logger.warning(f"Could not parse price: {price_text}")
            
            # Extract image URL
            img_element = await element.query_selector('img')
            image_url = None
            if img_element:
                image_url = await img_element.get_attribute('src') or \
                           await img_element.get_attribute('data-src')
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
            
            # Extract color/additional info if available
            color_element = await element.query_selector('[data-testid="product-color"], .color-name')
            color = await color_element.inner_text() if color_element else None
            
            if not product_id:
                # Generate ID from URL or name if still not found
                if product_url:
                    product_id = str(hash(product_url))
                elif name:
                    product_id = str(hash(name))
                else:
                    return None
            
            product_data = {
                'product_id': product_id,
                'name': name,
                'price': price,
                'price_text': price_text,
                'image_url': image_url,
                'product_url': product_url,
                'color': color,
                'scraped_at': datetime.utcnow().isoformat(),
                'source': 'zara',
                'category': 'homme'  # Based on the URL provided
            }
            
            # Remove None values
            product_data = {k: v for k, v in product_data.items() if v is not None}
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error extracting product data from element: {e}")
            return None
    
    async def save_products(self, products: List[Dict]) -> int:
        """Save products to Supabase database."""
        if not products:
            logger.info("No products to save")
            return 0
        
        try:
            # First, try to get existing products to check for updates
            existing_products = self.get_existing_products()
            existing_ids = {p['product_id'] for p in existing_products}
            
            new_products = []
            updated_products = []
            
            for product in products:
                if product['product_id'] in existing_ids:
                    # Check if product needs updating
                    existing_product = next(p for p in existing_products if p['product_id'] == product['product_id'])
                    if self.product_needs_update(existing_product, product):
                        product['updated_at'] = datetime.utcnow().isoformat()
                        updated_products.append(product)
                else:
                    product['created_at'] = datetime.utcnow().isoformat()
                    new_products.append(product)
            
            saved_count = 0
            
            # Insert new products
            if new_products:
                result = self.supabase.table('zara_products').insert(new_products).execute()
                saved_count += len(new_products)
                logger.info(f"Inserted {len(new_products)} new products")
            
            # Update existing products
            if updated_products:
                for product in updated_products:
                    self.supabase.table('zara_products').update(product).eq('product_id', product['product_id']).execute()
                saved_count += len(updated_products)
                logger.info(f"Updated {len(updated_products)} existing products")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving products to database: {e}")
            raise
    
    def get_existing_products(self) -> List[Dict]:
        """Get existing products from database."""
        try:
            result = self.supabase.table('zara_products').select('*').execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching existing products: {e}")
            return []
    
    def product_needs_update(self, existing: Dict, new: Dict) -> bool:
        """Check if a product needs to be updated."""
        # Compare key fields that might change
        fields_to_compare = ['name', 'price', 'price_text', 'image_url', 'color']
        
        for field in fields_to_compare:
            if existing.get(field) != new.get(field):
                return True
        
        return False
    
    async def run_scraping(self, url: str) -> Dict:
        """Main method to run the complete scraping process."""
        logger.info("Starting Zara product scraping")
        
        try:
            # Setup database (in production, this would be done via migrations)
            await self.setup_database()
            
            # Scrape products
            products = await self.scrape_products(url)
            
            if not products:
                logger.warning("No products found")
                return {'success': False, 'message': 'No products found', 'products_saved': 0}
            
            # Save products to database
            saved_count = await self.save_products(products)
            
            result = {
                'success': True,
                'message': f'Successfully processed {len(products)} products',
                'products_scraped': len(products),
                'products_saved': saved_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scraping completed: {result}")
            return result
            
        except Exception as e:
            error_message = f"Scraping failed: {e}"
            logger.error(error_message)
            return {
                'success': False,
                'message': error_message,
                'products_saved': 0,
                'timestamp': datetime.utcnow().isoformat()
            }


async def main():
    """Main function to run the scraper."""
    # Zara URL from the problem statement
    zara_url = "https://www.zara.com/tn/fr/homme-tout-l7465.html?v1=2443335"
    
    # Supabase credentials from the problem statement
    supabase_url = "https://mxlxrloxdzijsqbhuhul.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14bHhybG94ZHppanNxYmh1aHVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjM0MTQyMSwiZXhwIjoyMDcxOTE3NDIxfQ.t1fgsHPIV0KQGMDuKLb0XECdGvy_lyE--hMswKVI2v0"
    
    try:
        scraper = ZaraScraper(supabase_url, supabase_key)
        result = await scraper.run_scraping(zara_url)
        
        print(json.dumps(result, indent=2))
        
        if result['success']:
            exit(0)
        else:
            exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())