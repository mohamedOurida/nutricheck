# Zara Product Scraper

This module scrapes product information from Zara's website and stores it in Supabase PostgreSQL database. It's designed to run daily to keep the product dataset up-to-date.

## Features

- 🕷️ **Web Scraping**: Robust scraper for Zara product pages with multiple fallback strategies
- 🗄️ **Database Integration**: Seamless integration with Supabase PostgreSQL
- ⏰ **Daily Scheduling**: Automated daily runs via GitHub Actions
- 🔄 **Data Management**: Automatic cleanup of old product data
- 📊 **Monitoring**: Comprehensive logging and statistics
- 🛡️ **Error Handling**: Robust error handling with retry logic
- 🎯 **Mock Mode**: Testing mode when database is not available

## Files

- `zara_scraper.py` - Core scraping functionality
- `database_manager.py` - Database operations and Supabase integration
- `run_scraper.py` - Main orchestrator script
- `test_scraper.py` - Test suite for validation
- `.github/workflows/daily-scraper.yml` - GitHub Actions workflow for daily runs
- `requirements_scraper.txt` - Additional dependencies for scraping

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements_scraper.txt
```

### 2. Set up Supabase

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Get your project URL and anonymous key
3. Create the database table (see Database Schema below)
4. Set environment variables:

```bash
export SUPABASE_URL="your_supabase_url"
export SUPABASE_ANON_KEY="your_supabase_anon_key"
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Database Schema

Execute this SQL in your Supabase SQL editor:

```sql
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
```

### 4. Run the Scraper

```bash
# Test with dry run
python run_scraper.py --dry-run

# Run full scraping
python run_scraper.py

# Check database statistics
python run_scraper.py --stats-only

# Run tests
python test_scraper.py
```

## Usage

### Command Line Interface

```bash
# Basic usage
python run_scraper.py

# Custom URL
python run_scraper.py --url "https://www.zara.com/tn/fr/homme-tout-l7465.html?v1=2443335"

# Skip cleanup of old products
python run_scraper.py --no-cleanup

# Custom cleanup period
python run_scraper.py --cleanup-days 60

# Dry run (scrape but don't save)
python run_scraper.py --dry-run

# Show statistics only
python run_scraper.py --stats-only
```

### Programmatic Usage

```python
from zara_scraper import ZaraScraper
from database_manager import get_database_manager

# Create scraper
scraper = ZaraScraper()

# Scrape products
products = scraper.scrape_products()

# Save to database
db_manager = get_database_manager()
db_manager.save_products(products)
```

## Daily Scheduling

The scraper runs automatically every day at 2 AM UTC using GitHub Actions. To set this up:

1. **Add Secrets**: In your GitHub repository, go to Settings > Secrets and add:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_ANON_KEY`: Your Supabase anonymous key

2. **Enable Actions**: The workflow file `.github/workflows/daily-scraper.yml` is already configured

3. **Manual Trigger**: You can also trigger the workflow manually from the Actions tab

## Data Structure

Each scraped product contains:

```python
@dataclass
class ZaraProduct:
    id: str                    # Unique product identifier
    name: str                  # Product name
    price: str                 # Current price
    original_price: str        # Original price (if on sale)
    image_url: str            # Product image URL
    product_url: str          # Link to product page
    color: str                # Color variant
    sizes: List[str]          # Available sizes
    category: str             # Product category
    description: str          # Product description
    scraped_at: datetime      # When it was scraped
    is_sale: bool             # Whether it's on sale
```

## Configuration

Environment variables:

- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `ZARA_BASE_URL`: Default URL to scrape (optional)
- `REQUEST_DELAY`: Delay between requests in seconds (default: 1)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `CLEANUP_DAYS`: Days to keep old products (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)

## Error Handling

The scraper includes comprehensive error handling:

- **Network Issues**: Automatic retries with exponential backoff
- **Rate Limiting**: Built-in delays between requests
- **Parse Errors**: Graceful fallback to alternative parsing methods
- **Database Errors**: Detailed logging and mock mode fallback
- **Blocking Detection**: Detection and handling of bot blocking

## Monitoring

### Logs

The scraper generates detailed logs:
- Console output for real-time monitoring
- Daily log files (`zara_scraper_YYYYMMDD.log`)
- GitHub Actions workflow logs

### Statistics

Get insights into your data:

```bash
python run_scraper.py --stats-only
```

Returns:
- Total products count
- Products by category
- Sale products count
- Latest scrape timestamp

## Testing

Run the test suite:

```bash
python test_scraper.py
```

Tests include:
- ✅ Scraper creation
- ✅ Mock product data validation
- ✅ Database manager functionality
- ✅ HTML parsing with fallback data

## Troubleshooting

### Common Issues

1. **Network Access**: The scraper requires internet access to reach Zara's website
2. **Rate Limiting**: If blocked, increase the `REQUEST_DELAY` setting
3. **Database Connection**: Ensure Supabase credentials are correct
4. **Parsing Issues**: The scraper includes multiple fallback strategies

### Mock Mode

If Supabase isn't available, the scraper automatically uses a mock database for testing.

### GitHub Actions Issues

- Check that secrets are properly configured
- Review workflow logs in the Actions tab
- Ensure the repository has Actions enabled

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project follows the same license as the parent repository.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for error details
3. Open an issue with detailed error information