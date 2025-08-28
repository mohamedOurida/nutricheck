#!/usr/bin/env python3
"""
Quick start script for Zara scraping
Simple one-command interface for running the scraper
"""

import asyncio
import sys
from datetime import datetime

def main():
    """Quick start the scraper."""
    print("🚀 Starting Zara Product Scraper...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        from zara_scraper import ZaraScraper
        
        # Use the provided credentials
        supabase_url = "https://mxlxrloxdzijsqbhuhul.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14bHhybG94ZHppanNxYmh1aHVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjM0MTQyMSwiZXhwIjoyMDcxOTE3NDIxfQ.t1fgsHPIV0KQGMDuKLb0XECdGvy_lyE--hMswKVI2v0"
        zara_url = "https://www.zara.com/tn/fr/homme-tout-l7465.html?v1=2443335"
        
        async def run():
            scraper = ZaraScraper(supabase_url, supabase_key)
            result = await scraper.run_scraping(zara_url)
            
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"📦 Products scraped: {result['products_scraped']}")
                print(f"💾 Products saved: {result['products_saved']}")
            else:
                print(f"❌ {result['message']}")
                sys.exit(1)
        
        asyncio.run(run())
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install playwright supabase python-dotenv")
        print("Then: playwright install chromium")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()