"""
Utility functions for managing the Zara scraper
Provides CLI commands for managing the scraper and database
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime, timedelta

from zara_scraper import ZaraScraper

async def clear_old_products(scraper: ZaraScraper, days_old: int = 30):
    """Remove products older than specified days."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # This would need to be implemented in the scraper class
        # For now, just log what would happen
        existing_products = scraper.get_existing_products()
        
        old_count = 0
        for product in existing_products:
            created_at = datetime.fromisoformat(product.get('created_at', '').replace('Z', '+00:00'))
            if created_at < cutoff_date:
                old_count += 1
        
        print(f"Found {old_count} products older than {days_old} days")
        print("Note: Actual deletion not implemented in this demo")
        
        return old_count
        
    except Exception as e:
        print(f"Error clearing old products: {e}")
        return 0

async def get_stats(scraper: ZaraScraper):
    """Get statistics about scraped products."""
    try:
        existing_products = scraper.get_existing_products()
        
        total = len(existing_products)
        
        if total == 0:
            print("No products found in database")
            return
        
        # Count by category
        categories = {}
        price_ranges = {'0-50': 0, '50-100': 0, '100-200': 0, '200+': 0}
        
        for product in existing_products:
            # Category stats
            category = product.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
            
            # Price stats
            price = product.get('price', 0)
            if price < 50:
                price_ranges['0-50'] += 1
            elif price < 100:
                price_ranges['50-100'] += 1
            elif price < 200:
                price_ranges['100-200'] += 1
            else:
                price_ranges['200+'] += 1
        
        print(f"📊 Database Statistics")
        print(f"Total products: {total}")
        print(f"\nBy category:")
        for category, count in categories.items():
            print(f"  {category}: {count}")
        
        print(f"\nBy price range:")
        for range_name, count in price_ranges.items():
            print(f"  {range_name}€: {count}")
        
        # Get latest scraping date
        latest_scraped = max(
            (datetime.fromisoformat(p.get('scraped_at', '').replace('Z', '+00:00')) 
             for p in existing_products if p.get('scraped_at')), 
            default=None
        )
        
        if latest_scraped:
            print(f"\nLast scraped: {latest_scraped.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
    except Exception as e:
        print(f"Error getting stats: {e}")

async def export_products(scraper: ZaraScraper, filename: str = None):
    """Export products to JSON file."""
    try:
        existing_products = scraper.get_existing_products()
        
        if not filename:
            filename = f"zara_products_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_products, f, indent=2, default=str)
        
        print(f"Exported {len(existing_products)} products to {filename}")
        
    except Exception as e:
        print(f"Error exporting products: {e}")

async def test_connection(scraper: ZaraScraper):
    """Test database connection and basic functionality."""
    try:
        print("Testing Supabase connection...")
        
        # Test reading
        existing_products = scraper.get_existing_products()
        print(f"✅ Successfully connected. Found {len(existing_products)} products")
        
        # Test the scraper setup
        await scraper.setup_database()
        print("✅ Database setup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def main():
    """CLI interface for scraper utilities."""
    parser = argparse.ArgumentParser(description="Zara Scraper Utilities")
    parser.add_argument('--supabase-url', default=None, help='Supabase URL')
    parser.add_argument('--supabase-key', default=None, help='Supabase Key')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export products to JSON')
    export_parser.add_argument('--filename', help='Output filename')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear-old', help='Clear old products')
    clear_parser.add_argument('--days', type=int, default=30, help='Age threshold in days')
    
    # Test command
    subparsers.add_parser('test', help='Test database connection')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Run scraping now')
    scrape_parser.add_argument('--url', default="https://www.zara.com/tn/fr/homme-tout-l7465.html?v1=2443335", help='Zara URL to scrape')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Use provided credentials or defaults
    supabase_url = args.supabase_url or "https://mxlxrloxdzijsqbhuhul.supabase.co"
    supabase_key = args.supabase_key or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14bHhybG94ZHppanNxYmh1aHVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjM0MTQyMSwiZXhwIjoyMDcxOTE3NDIxfQ.t1fgsHPIV0KQGMDuKLb0XECdGvy_lyE--hMswKVI2v0"
    
    try:
        scraper = ZaraScraper(supabase_url, supabase_key)
        
        if args.command == 'stats':
            await get_stats(scraper)
        elif args.command == 'export':
            await export_products(scraper, args.filename)
        elif args.command == 'clear-old':
            await clear_old_products(scraper, args.days)
        elif args.command == 'test':
            success = await test_connection(scraper)
            sys.exit(0 if success else 1)
        elif args.command == 'scrape':
            result = await scraper.run_scraping(args.url)
            print(json.dumps(result, indent=2))
            sys.exit(0 if result['success'] else 1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())