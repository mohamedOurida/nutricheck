"""
Example usage of the Zara scraper
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def example_basic_usage():
    """Basic scraper usage example"""
    print("=== BASIC SCRAPER USAGE ===\n")
    
    from zara_scraper import ZaraScraper
    from database_manager import get_database_manager
    
    # Create scraper
    scraper = ZaraScraper()
    
    # Scrape products (will fail due to network restrictions in this environment)
    products = scraper.scrape_products()
    
    if products:
        print(f"Scraped {len(products)} products")
        
        # Display first few products
        for i, product in enumerate(products[:3], 1):
            print(f"{i}. {product.name}")
            print(f"   Price: {product.price}")
            print(f"   URL: {product.product_url}")
            print(f"   Sale: {'Yes' if product.is_sale else 'No'}")
            print()
        
        # Save to database
        db_manager = get_database_manager()
        success = db_manager.save_products(products)
        
        if success:
            print("✅ Products saved to database")
        else:
            print("❌ Failed to save products")
    else:
        print("No products scraped (likely due to network restrictions)")

def example_with_mock_data():
    """Example using mock data for demonstration"""
    print("=== MOCK DATA EXAMPLE ===\n")
    
    from zara_scraper import ZaraProduct
    from database_manager import get_database_manager
    from datetime import datetime
    
    # Create mock products
    mock_products = [
        ZaraProduct(
            id="zara_001",
            name="Cotton Blend Shirt",
            price="29.95",
            original_price="39.95",
            image_url="https://static.zara.net/photos/shirt.jpg",
            product_url="https://www.zara.com/product/001",
            color="White",
            sizes=["S", "M", "L", "XL"],
            category="Men",
            description="Comfortable cotton blend shirt",
            scraped_at=datetime.now(),
            is_sale=True
        ),
        ZaraProduct(
            id="zara_002",
            name="Denim Jeans",
            price="49.95",
            original_price=None,
            image_url="https://static.zara.net/photos/jeans.jpg",
            product_url="https://www.zara.com/product/002",
            color="Blue",
            sizes=["30", "32", "34", "36"],
            category="Men",
            description="Classic fit denim jeans",
            scraped_at=datetime.now(),
            is_sale=False
        )
    ]
    
    print(f"Created {len(mock_products)} mock products:")
    for product in mock_products:
        print(f"- {product.name}: {product.price}")
    
    # Save to database (will use mock database)
    db_manager = get_database_manager()
    success = db_manager.save_products(mock_products)
    
    if success:
        print("✅ Mock products saved to database")
        
        # Get statistics
        stats = db_manager.get_statistics()
        print(f"📊 Database stats: {stats}")
    else:
        print("❌ Failed to save mock products")

def example_configuration():
    """Show configuration options"""
    print("=== CONFIGURATION EXAMPLE ===\n")
    
    print("Environment Variables:")
    print(f"SUPABASE_URL: {'Set' if os.getenv('SUPABASE_URL') else 'Not set'}")
    print(f"SUPABASE_ANON_KEY: {'Set' if os.getenv('SUPABASE_ANON_KEY') else 'Not set'}")
    
    print("\nTo use real database:")
    print("1. Create Supabase project")
    print("2. Set environment variables:")
    print("   export SUPABASE_URL='your_url'")
    print("   export SUPABASE_ANON_KEY='your_key'")
    print("3. Create database table (see SCRAPER_README.md)")
    
    print("\nCommand Line Options:")
    print("python run_scraper.py --dry-run          # Test without saving")
    print("python run_scraper.py --stats-only       # Show database stats")
    print("python run_scraper.py --no-cleanup       # Skip old data cleanup")
    print("python run_scraper.py --cleanup-days 60  # Keep data for 60 days")

def main():
    """Run all examples"""
    example_basic_usage()
    print("\n" + "="*50 + "\n")
    example_with_mock_data()
    print("\n" + "="*50 + "\n")
    example_configuration()

if __name__ == "__main__":
    main()