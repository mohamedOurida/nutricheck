# Zara Product Scraper

This module adds Zara product scraping functionality to the Nutricheck project. It uses Playwright to scrape product data from Zara's website and stores it in a Supabase PostgreSQL database with automated daily updates via GitHub Actions.

## Features

- 🕷️ **Web Scraping**: Uses Playwright to handle JavaScript-heavy Zara website
- 🗄️ **Database Integration**: Stores product data in Supabase PostgreSQL
- 🔄 **Update Detection**: Compares existing products and updates only when needed
- ⏰ **Automated Runs**: Daily GitHub Actions workflow
- 🚀 **Error Handling**: Comprehensive logging and error management

## Setup

### 1. Dependencies

Install the required Python packages:

```bash
pip install playwright supabase python-dotenv
playwright install chromium
```

### 2. Database Setup

Run the SQL schema in your Supabase dashboard:

```sql
-- See database_schema.sql for the complete schema
```

### 3. Environment Variables

Create a `.env` file (or use GitHub Secrets for Actions):

```env
SUPABASE_URL=https://mxlxrloxdzijsqbhuhul.supabase.co
SUPABASE_KEY=your_service_role_key_here
```

## Usage

### Run Locally

```bash
python zara_scraper.py
```

### Test the Scraper

```bash
python test_scraper.py
```

### GitHub Actions

The scraper runs automatically daily at 9:00 AM UTC via GitHub Actions. You can also trigger it manually from the Actions tab.

## Database Schema

The scraper creates a `zara_products` table with the following structure:

- `id`: Primary key
- `product_id`: Unique product identifier from Zara
- `name`: Product name
- `price`: Product price (decimal)
- `price_text`: Original price text
- `image_url`: Product image URL
- `product_url`: Link to product page
- `color`: Product color/variant
- `source`: Always 'zara'
- `category`: Product category
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp
- `scraped_at`: Scraping timestamp

## How It Works

1. **Scraping**: The scraper navigates to the Zara men's section and extracts:
   - Product names
   - Prices
   - Images
   - URLs
   - Colors/variants

2. **Update Detection**: For each scraped product:
   - Checks if it exists in the database
   - Compares key fields (name, price, image, etc.)
   - Updates only if changes are detected

3. **Data Storage**: Products are stored in Supabase with:
   - Automatic timestamps
   - Unique constraints on product IDs
   - Indexing for performance

## Error Handling

- Network timeouts and retries
- Missing elements gracefully handled
- Database connection errors logged
- Comprehensive logging for debugging

## Customization

### Different Zara Sections

To scrape different sections, modify the URL in `zara_scraper.py`:

```python
# Women's section
zara_url = "https://www.zara.com/tn/fr/femme-tout-l1055.html"

# Kids section  
zara_url = "https://www.zara.com/tn/fr/enfants-tout-l1176.html"
```

### Custom Fields

Add custom fields by:
1. Updating the database schema
2. Modifying `extract_product_data()` method
3. Adding fields to the comparison logic

## Monitoring

- GitHub Actions provides execution logs
- Artifacts are saved for 30 days
- Error notifications via GitHub Actions

## Legal Considerations

This scraper:
- Respects robots.txt
- Uses reasonable delays
- Doesn't overload the server
- Is for educational/personal use

Always check the website's terms of service before scraping.