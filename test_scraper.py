"""
Test script for the Zara scraper
This script tests the scraper with a smaller subset of functionality
"""

import asyncio
import json
from datetime import datetime
from zara_scraper import ZaraScraper

async def test_scraper():
    """Test the Zara scraper functionality."""
    
    print("🧪 Testing Zara Scraper")
    print("=" * 50)
    
    # Test with provided credentials
    supabase_url = "https://mxlxrloxdzijsqbhuhul.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14bHhybG94ZHppanNxYmh1aHVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjM0MTQyMSwiZXhwIjoyMDcxOTE3NDIxfQ.t1fgsHPIV0KQGMDuKLb0XECdGvy_lyE--hMswKVI2v0"
    zara_url = "https://www.zara.com/tn/fr/homme-tout-l7465.html?v1=2443335"
    
    try:
        # Initialize scraper
        print("🔧 Initializing scraper...")
        scraper = ZaraScraper(supabase_url, supabase_key)
        print("✅ Scraper initialized successfully")
        
        # Test database connection
        print("\n🗄️  Testing database connection...")
        try:
            # Try to query the table (it might not exist yet, that's ok)
            existing_products = scraper.get_existing_products()
            print(f"✅ Database connection successful. Found {len(existing_products)} existing products")
        except Exception as e:
            print(f"⚠️  Database table might not exist yet: {e}")
            print("   This is normal for first run. Please run the SQL schema in Supabase first.")
        
        # Test scraping (just the first few products to avoid overwhelming the site)
        print("\n🕷️  Testing product scraping...")
        products = await scraper.scrape_products(zara_url)
        
        if products:
            print(f"✅ Successfully scraped {len(products)} products")
            print("\n📦 Sample product data:")
            print(json.dumps(products[0], indent=2, default=str))
            
            # Test saving to database (only if we could connect earlier)
            if 'existing_products' in locals():
                print("\n💾 Testing database save...")
                try:
                    saved_count = await scraper.save_products(products[:3])  # Save only first 3 for testing
                    print(f"✅ Successfully saved {saved_count} products to database")
                except Exception as e:
                    print(f"❌ Failed to save products: {e}")
            else:
                print("\n⏭️  Skipping database save test (connection issue)")
        else:
            print("❌ No products found. This might be due to:")
            print("   - Website structure changes")
            print("   - Geographic blocking")
            print("   - Anti-bot measures")
        
        print(f"\n🎉 Test completed at {datetime.now()}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_scraper())