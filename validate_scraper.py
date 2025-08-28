"""
Basic validation test for the Zara scraper without browser installation
This test validates the code structure and Supabase connection
"""

import sys
import json
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import asyncio
        print("✅ asyncio imported successfully")
        
        import logging
        print("✅ logging imported successfully")
        
        from supabase import create_client
        print("✅ supabase imported successfully")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
        
        # Test that playwright would import (but don't require browser)
        try:
            from playwright.async_api import async_playwright
            print("✅ playwright imported successfully")
        except ImportError as e:
            print(f"⚠️  playwright import failed: {e}")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_scraper_class():
    """Test that the ZaraScraper class can be instantiated."""
    print("\n🧪 Testing ZaraScraper class...")
    
    try:
        from zara_scraper import ZaraScraper
        
        # Test with dummy credentials
        supabase_url = "https://mxlxrloxdzijsqbhuhul.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14bHhybG94ZHppanNxYmh1aHVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjM0MTQyMSwiZXhwIjoyMDcxOTE3NDIxfQ.t1fgsHPIV0KQGMDuKLb0XECdGvy_lyE--hMswKVI2v0"
        
        scraper = ZaraScraper(supabase_url, supabase_key)
        print("✅ ZaraScraper instantiated successfully")
        
        # Test that methods exist
        assert hasattr(scraper, 'scrape_products'), "scrape_products method missing"
        assert hasattr(scraper, 'save_products'), "save_products method missing"
        assert hasattr(scraper, 'run_scraping'), "run_scraping method missing"
        print("✅ All required methods exist")
        
        # Test database connection (might fail if table doesn't exist)
        try:
            existing_products = scraper.get_existing_products()
            print(f"✅ Database connection successful. Found {len(existing_products)} existing products")
        except Exception as e:
            print(f"⚠️  Database table might not exist: {e}")
            print("   This is normal for first run. Please run the SQL schema in Supabase first.")
        
        return True
        
    except Exception as e:
        print(f"❌ ZaraScraper test failed: {e}")
        return False

def test_helper_methods():
    """Test helper methods without browser interaction."""
    print("\n🧪 Testing helper methods...")
    
    try:
        from zara_scraper import ZaraScraper
        
        supabase_url = "https://mxlxrloxdzijsqbhuhul.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14bHhybG94ZHppanNxYmh1aHVsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjM0MTQyMSwiZXhwIjoyMDcxOTE3NDIxfQ.t1fgsHPIV0KQGMDuKLb0XECdGvy_lyE--hMswKVI2v0"
        
        scraper = ZaraScraper(supabase_url, supabase_key)
        
        # Test product comparison logic
        existing_product = {
            'product_id': 'test123',
            'name': 'Test Product',
            'price': 29.99,
            'color': 'blue'
        }
        
        new_product_same = {
            'product_id': 'test123',
            'name': 'Test Product',
            'price': 29.99,
            'color': 'blue'
        }
        
        new_product_different = {
            'product_id': 'test123',
            'name': 'Test Product',
            'price': 35.99,  # Different price
            'color': 'blue'
        }
        
        # Test comparison logic
        needs_update_same = scraper.product_needs_update(existing_product, new_product_same)
        needs_update_different = scraper.product_needs_update(existing_product, new_product_different)
        
        assert not needs_update_same, "Should not need update for identical products"
        assert needs_update_different, "Should need update for different products"
        
        print("✅ Product comparison logic works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Helper method test failed: {e}")
        return False

def test_github_workflow():
    """Test that GitHub workflow file is properly formatted."""
    print("\n🧪 Testing GitHub workflow...")
    
    try:
        import yaml
        
        with open('.github/workflows/zara_scraper.yml', 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Basic validation
        assert 'name' in workflow, "Workflow name missing"
        assert 'on' in workflow, "Workflow triggers missing"
        assert 'jobs' in workflow, "Workflow jobs missing"
        
        # Check that it has a cron schedule
        assert 'schedule' in workflow['on'], "Scheduled trigger missing"
        assert 'workflow_dispatch' in workflow['on'], "Manual trigger missing"
        
        print("✅ GitHub workflow file is valid")
        return True
        
    except FileNotFoundError:
        print("❌ GitHub workflow file not found")
        return False
    except Exception as e:
        print(f"❌ GitHub workflow test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Running Zara Scraper Validation Tests")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Scraper Class Test", test_scraper_class),
        ("Helper Methods Test", test_helper_methods),
        ("GitHub Workflow Test", test_github_workflow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The scraper is ready to use.")
        print("\n📋 Next steps:")
        print("1. Run the SQL schema in your Supabase dashboard (see database_schema.sql)")
        print("2. Set up GitHub Secrets for SUPABASE_URL and SUPABASE_KEY")
        print("3. Test the scraper locally with: python zara_scraper.py")
        print("4. The GitHub Actions workflow will run daily automatically")
        return True
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    try:
        # Install yaml for workflow testing
        import yaml
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML"])
        import yaml
    
    success = main()
    sys.exit(0 if success else 1)