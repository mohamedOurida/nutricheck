"""
Database Manager for Zara Product Data

This module handles all database operations for storing Zara product data in Supabase PostgreSQL.
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import asdict
import json

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not installed. Run: pip install supabase")

from zara_scraper import ZaraProduct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations for Zara product data"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.table_name = "zara_products"
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Supabase connection"""
        if not SUPABASE_AVAILABLE:
            logger.error("Supabase client not available")
            return
        
        try:
            # Get Supabase credentials from environment variables
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_ANON_KEY')
            
            if not url or not key:
                logger.error("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
                return
            
            self.supabase = create_client(url, key)
            logger.info("Successfully connected to Supabase")
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self.supabase = None
    
    def create_table_if_not_exists(self):
        """Create the zara_products table if it doesn't exist"""
        if not self.supabase:
            logger.error("No database connection available")
            return False
        
        # Note: In Supabase, table creation is usually done through the dashboard or SQL editor
        # This is a placeholder for the table structure documentation
        table_schema = """
        CREATE TABLE IF NOT EXISTS zara_products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price TEXT,
            original_price TEXT,
            image_url TEXT,
            product_url TEXT,
            color TEXT,
            sizes JSONB,
            category TEXT,
            description TEXT,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_sale BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_zara_products_scraped_at ON zara_products(scraped_at);
        CREATE INDEX IF NOT EXISTS idx_zara_products_category ON zara_products(category);
        CREATE INDEX IF NOT EXISTS idx_zara_products_is_sale ON zara_products(is_sale);
        """
        
        logger.info("Table schema ready. Please ensure the table exists in Supabase:")
        logger.info(table_schema)
        
        return True
    
    def product_to_dict(self, product: ZaraProduct) -> Dict[str, Any]:
        """Convert ZaraProduct to dictionary for database insertion"""
        product_dict = asdict(product)
        
        # Convert datetime to ISO format string
        if isinstance(product_dict['scraped_at'], datetime):
            product_dict['scraped_at'] = product_dict['scraped_at'].isoformat()
        
        # Convert sizes list to JSON
        product_dict['sizes'] = json.dumps(product_dict['sizes'])
        
        # Add timestamps
        now = datetime.now().isoformat()
        product_dict['updated_at'] = now
        if 'created_at' not in product_dict:
            product_dict['created_at'] = now
        
        return product_dict
    
    def save_products(self, products: List[ZaraProduct]) -> bool:
        """Save products to the database"""
        if not self.supabase:
            logger.error("No database connection available")
            return False
        
        if not products:
            logger.info("No products to save")
            return True
        
        try:
            # Convert products to dictionaries
            product_dicts = [self.product_to_dict(product) for product in products]
            
            # Use upsert to handle duplicates
            result = self.supabase.table(self.table_name).upsert(
                product_dicts,
                on_conflict='id'
            ).execute()
            
            if result.data:
                logger.info(f"Successfully saved {len(result.data)} products to database")
                return True
            else:
                logger.error("No data returned from upsert operation")
                return False
                
        except Exception as e:
            logger.error(f"Failed to save products to database: {e}")
            return False
    
    def get_products(self, limit: int = 100, category: str = None) -> List[Dict[str, Any]]:
        """Retrieve products from the database"""
        if not self.supabase:
            logger.error("No database connection available")
            return []
        
        try:
            query = self.supabase.table(self.table_name).select("*")
            
            if category:
                query = query.eq('category', category)
            
            result = query.order('scraped_at', desc=True).limit(limit).execute()
            
            if result.data:
                logger.info(f"Retrieved {len(result.data)} products from database")
                return result.data
            else:
                logger.info("No products found in database")
                return []
                
        except Exception as e:
            logger.error(f"Failed to retrieve products from database: {e}")
            return []
    
    def get_product_count(self) -> int:
        """Get total number of products in the database"""
        if not self.supabase:
            logger.error("No database connection available")
            return 0
        
        try:
            result = self.supabase.table(self.table_name).select("id", count="exact").execute()
            return result.count if result.count else 0
            
        except Exception as e:
            logger.error(f"Failed to get product count: {e}")
            return 0
    
    def delete_old_products(self, days: int = 30) -> bool:
        """Delete products older than specified days"""
        if not self.supabase:
            logger.error("No database connection available")
            return False
        
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            result = self.supabase.table(self.table_name).delete().lt('scraped_at', cutoff_date).execute()
            
            logger.info(f"Deleted old products (older than {days} days)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete old products: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.supabase:
            logger.error("No database connection available")
            return {}
        
        try:
            stats = {}
            
            # Total count
            total_result = self.supabase.table(self.table_name).select("id", count="exact").execute()
            stats['total_products'] = total_result.count if total_result.count else 0
            
            # Count by category
            category_result = self.supabase.table(self.table_name).select("category", count="exact").execute()
            stats['by_category'] = {}
            
            # Sale products count
            sale_result = self.supabase.table(self.table_name).select("id", count="exact").eq('is_sale', True).execute()
            stats['sale_products'] = sale_result.count if sale_result.count else 0
            
            # Latest scrape time
            latest_result = self.supabase.table(self.table_name).select("scraped_at").order('scraped_at', desc=True).limit(1).execute()
            if latest_result.data:
                stats['latest_scrape'] = latest_result.data[0]['scraped_at']
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

# Mock database for testing when Supabase is not available
class MockDatabaseManager:
    """Mock database manager for testing purposes"""
    
    def __init__(self):
        self.products = []
        logger.info("Using mock database manager")
    
    def create_table_if_not_exists(self):
        logger.info("Mock: Table creation simulated")
        return True
    
    def save_products(self, products: List[ZaraProduct]) -> bool:
        self.products.extend(products)
        logger.info(f"Mock: Saved {len(products)} products")
        return True
    
    def get_products(self, limit: int = 100, category: str = None) -> List[Dict[str, Any]]:
        products = [asdict(p) for p in self.products[-limit:]]
        logger.info(f"Mock: Retrieved {len(products)} products")
        return products
    
    def get_product_count(self) -> int:
        return len(self.products)
    
    def delete_old_products(self, days: int = 30) -> bool:
        logger.info(f"Mock: Deleted old products (older than {days} days)")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            'total_products': len(self.products),
            'by_category': {'Men': len(self.products)},
            'sale_products': sum(1 for p in self.products if p.is_sale),
            'latest_scrape': datetime.now().isoformat()
        }

def get_database_manager() -> DatabaseManager:
    """Factory function to get appropriate database manager"""
    if SUPABASE_AVAILABLE and os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_ANON_KEY'):
        return DatabaseManager()
    else:
        logger.warning("Using mock database manager. Set SUPABASE_URL and SUPABASE_ANON_KEY for real database.")
        return MockDatabaseManager()

def main():
    """Test the database manager"""
    db = get_database_manager()
    
    # Create table
    db.create_table_if_not_exists()
    
    # Get statistics
    stats = db.get_statistics()
    print("Database Statistics:")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()