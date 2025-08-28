#!/usr/bin/env python3
"""
Setup script for the Zara Product Scraper
This script helps users set up the scraper for the first time
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(step_num, text):
    """Print a formatted step."""
    print(f"\n🔧 Step {step_num}: {text}")

def check_python_version():
    """Check if Python version is adequate."""
    print_step(1, "Checking Python version")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print_step(2, "Installing dependencies")
    
    required_packages = [
        "playwright>=1.40.0",
        "supabase>=2.0.0", 
        "python-dotenv>=1.0.0"
    ]
    
    try:
        for package in required_packages:
            print(f"   Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ All dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def install_playwright_browser():
    """Install Playwright browser."""
    print_step(3, "Installing Playwright browser")
    
    try:
        print("   This may take a few minutes...")
        result = subprocess.run([
            "playwright", "install", "chromium"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Playwright browser installed successfully")
            return True
        else:
            print(f"❌ Failed to install browser: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Browser installation timed out. You may need to run 'playwright install chromium' manually")
        return False
    except FileNotFoundError:
        print("⚠️  Playwright command not found. Dependencies may not be installed correctly")
        return False
    except Exception as e:
        print(f"❌ Error installing browser: {e}")
        return False

def setup_environment():
    """Set up environment variables."""
    print_step(4, "Setting up environment variables")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            # Copy example to .env
            with open(env_example, 'r') as src:
                content = src.read()
            
            with open(env_file, 'w') as dst:
                dst.write(content)
            
            print("✅ Created .env file from template")
            print("   Please edit .env with your actual Supabase credentials")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  No .env.example file found")
        return False

def test_setup():
    """Test the setup."""
    print_step(5, "Testing setup")
    
    try:
        # Try to import required modules
        print("   Testing imports...")
        from zara_scraper import ZaraScraper
        print("   ✅ ZaraScraper imported successfully")
        
        # Test validation
        print("   Running validation tests...")
        result = subprocess.run([
            sys.executable, "validate_scraper.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ All validation tests passed")
            return True
        else:
            print("   ❌ Some validation tests failed:")
            print(f"   {result.stdout}")
            return False
            
    except Exception as e:
        print(f"   ❌ Setup test failed: {e}")
        return False

def show_next_steps():
    """Show next steps to the user."""
    print_header("Setup Complete! 🎉")
    
    print("\n📋 Next Steps:")
    print("1. Edit the .env file with your actual Supabase credentials")
    print("2. Run the database schema in your Supabase dashboard:")
    print("   - Open https://supabase.com/dashboard")
    print("   - Go to SQL Editor")
    print("   - Copy and paste the contents of database_schema.sql")
    print("   - Run the SQL")
    
    print("\n3. Test the scraper:")
    print("   python scraper_utils.py test")
    
    print("\n4. Run a test scrape:")
    print("   python scraper_utils.py scrape")
    
    print("\n5. Set up GitHub Secrets for automation:")
    print("   - Go to your repository Settings > Secrets and variables > Actions")
    print("   - Add SUPABASE_URL and SUPABASE_KEY secrets")
    
    print("\n📚 Documentation:")
    print("   - Main scraper: zara_scraper.py")
    print("   - Utilities: scraper_utils.py --help")
    print("   - Full docs: ZARA_SCRAPER_README.md")

def main():
    """Main setup function."""
    print_header("Zara Product Scraper Setup")
    print("This script will help you set up the Zara product scraper")
    
    steps = [
        ("Check Python version", check_python_version),
        ("Install dependencies", install_dependencies),
        ("Install Playwright browser", install_playwright_browser),
        ("Setup environment", setup_environment),
        ("Test setup", test_setup)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n❌ Setup failed at the following steps:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease fix the issues and run the setup again.")
        sys.exit(1)
    else:
        show_next_steps()
        sys.exit(0)

if __name__ == "__main__":
    main()