"""
Zara Product Scraper

This module scrapes product information from Zara's website and stores it in Supabase PostgreSQL.
Designed to run daily to keep the product dataset up-to-date.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os
from dataclasses import dataclass
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ZaraProduct:
    """Data class for Zara product information"""
    id: str
    name: str
    price: str
    original_price: Optional[str]
    image_url: str
    product_url: str
    color: Optional[str]
    sizes: List[str]
    category: str
    description: Optional[str]
    scraped_at: datetime
    is_sale: bool

class ZaraScraper:
    """Scraper for Zara products"""
    
    def __init__(self, base_url: str = "https://www.zara.com/tn/fr/homme-tout-l7465.html?v1=2443335"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Rate limiting
        self.request_delay = 1  # seconds between requests
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page with retry logic"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching page: {url} (attempt {attempt + 1})")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we got blocked (common pattern for e-commerce sites)
                if "blocked" in response.text.lower() or response.status_code == 403:
                    logger.warning(f"Possible blocking detected for {url}")
                    time.sleep(self.request_delay * 2)  # Longer delay
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info(f"Successfully fetched page: {url}")
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(self.request_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"All attempts failed for {url}")
                    return None
                    
        return None
    
    def extract_product_data(self, soup: BeautifulSoup, base_url: str) -> List[ZaraProduct]:
        """Extract product information from the page"""
        products = []
        
        try:
            # Look for JSON-LD structured data (common on e-commerce sites)
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    
                    if data.get('@type') == 'Product' or 'Product' in str(data.get('@type', '')):
                        product = self.parse_json_ld_product(data, base_url)
                        if product:
                            products.append(product)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse JSON-LD: {e}")
            
            # Fallback: Look for product cards in HTML
            if not products:
                products = self.extract_from_html(soup, base_url)
                
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            
        return products
    
    def parse_json_ld_product(self, data: Dict, base_url: str) -> Optional[ZaraProduct]:
        """Parse product from JSON-LD structured data"""
        try:
            offers = data.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            
            # Extract price information
            price = offers.get('price', '')
            original_price = offers.get('highPrice')
            is_sale = original_price is not None and original_price != price
            
            # Extract image URL
            image_data = data.get('image', [])
            image_url = ''
            if isinstance(image_data, list) and image_data:
                image_url = image_data[0] if isinstance(image_data[0], str) else image_data[0].get('url', '')
            elif isinstance(image_data, str):
                image_url = image_data
            elif isinstance(image_data, dict):
                image_url = image_data.get('url', '')
            
            product = ZaraProduct(
                id=data.get('productID', data.get('sku', str(hash(data.get('name', ''))))),
                name=data.get('name', ''),
                price=str(price),
                original_price=str(original_price) if original_price else None,
                image_url=image_url,
                product_url=data.get('url', base_url),
                color=data.get('color'),
                sizes=self.extract_sizes_from_offers(offers),
                category=data.get('category', 'Men'),
                description=data.get('description'),
                scraped_at=datetime.now(),
                is_sale=is_sale
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Error parsing JSON-LD product: {e}")
            return None
    
    def extract_sizes_from_offers(self, offers: Dict) -> List[str]:
        """Extract available sizes from offers data"""
        sizes = []
        
        # Common patterns for size information
        size_keys = ['size', 'sizes', 'availableSizes', 'variants']
        
        for key in size_keys:
            if key in offers:
                size_data = offers[key]
                if isinstance(size_data, list):
                    sizes.extend([str(s) for s in size_data])
                elif isinstance(size_data, str):
                    sizes.append(size_data)
        
        return list(set(sizes))  # Remove duplicates
    
    def extract_from_html(self, soup: BeautifulSoup, base_url: str) -> List[ZaraProduct]:
        """Fallback method to extract products from HTML structure"""
        products = []
        
        # Common CSS selectors for product cards on e-commerce sites
        selectors = [
            '.product-item',
            '.product-card',
            '.product',
            '[data-product]',
            '.item',
            '.grid-item'
        ]
        
        for selector in selectors:
            product_elements = soup.select(selector)
            if product_elements:
                logger.info(f"Found {len(product_elements)} products using selector: {selector}")
                break
        
        for i, element in enumerate(product_elements[:50]):  # Limit to 50 products
            try:
                product = self.parse_html_product(element, base_url, i)
                if product:
                    products.append(product)
            except Exception as e:
                logger.warning(f"Failed to parse product element {i}: {e}")
        
        return products
    
    def parse_html_product(self, element, base_url: str, index: int) -> Optional[ZaraProduct]:
        """Parse product from HTML element"""
        try:
            # Extract name
            name_selectors = ['h3', '.product-name', '.title', '[data-product-name]', 'a']
            name = ''
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    break
            
            # Extract price
            price_selectors = ['.price', '.current-price', '[data-price]', '.amount']
            price = ''
            for selector in price_selectors:
                price_element = element.select_one(selector)
                if price_element:
                    price = price_element.get_text(strip=True)
                    break
            
            # Extract image URL
            image_element = element.select_one('img')
            image_url = ''
            if image_element:
                image_url = image_element.get('src', '') or image_element.get('data-src', '')
                if image_url and not image_url.startswith('http'):
                    image_url = f"https://www.zara.com{image_url}"
            
            # Extract product URL
            link_element = element.select_one('a')
            product_url = base_url
            if link_element:
                href = link_element.get('href', '')
                if href:
                    product_url = href if href.startswith('http') else f"https://www.zara.com{href}"
            
            if not name and not price:
                return None
            
            product = ZaraProduct(
                id=f"zara_{index}_{hash(name)}",
                name=name or f"Product {index}",
                price=price or "0",
                original_price=None,
                image_url=image_url,
                product_url=product_url,
                color=None,
                sizes=[],
                category="Men",
                description=None,
                scraped_at=datetime.now(),
                is_sale=False
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Error parsing HTML product: {e}")
            return None
    
    def scrape_products(self) -> List[ZaraProduct]:
        """Main method to scrape products"""
        logger.info("Starting Zara product scraping...")
        
        soup = self.get_page(self.base_url)
        if not soup:
            logger.error("Failed to fetch the main page")
            return []
        
        products = self.extract_product_data(soup, self.base_url)
        
        logger.info(f"Successfully scraped {len(products)} products")
        return products

def main():
    """Main function to run the scraper"""
    try:
        scraper = ZaraScraper()
        products = scraper.scrape_products()
        
        if products:
            logger.info(f"Scraped {len(products)} products successfully")
            # Products will be saved to database by the database module
            return products
        else:
            logger.warning("No products were scraped")
            return []
            
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return []

if __name__ == "__main__":
    main()