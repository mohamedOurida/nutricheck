# Nutricheck Extended - Food Recognition + OCR to Excel 🍔📄➡️📊

**Note:** Nutricheck is a work in progress. Expect plenty of errors and bugs.

## 🚀 New: OCR to Excel Converter Added!

**Original goal:** take a photo of food and learn about it (nutrition information, where it's from, recipes, etc).

**Extended goal:** Transform ANY document into structured Excel data + comprehensive food analysis platform.

**Status:** 
- ✅ Food image collection system operational
- ✅ OCR to Excel converter fully functional  
- ⏳ Integration and cross-platform synergies in development

## 🎯 Dual Value Proposition

### 🍔 Food Intelligence Platform
- Upload food photos to build nutrition database
- Computer vision models for food recognition
- Nutrition information lookup and analysis

### 📄 Document Processing Platform  
- Convert screenshots, PDFs, receipts to Excel
- Smart OCR with field mapping
- Perfect for receipts, invoices, forms, notes

### 🔄 Combined Power
- **Restaurant receipts** → Expense tracking + nutrition analysis
- **Grocery receipts** → Budget analysis + meal planning
- **Menu scanning** → Structured food databases
- **Universal document processing** for any business need

## What's in this repo?

### 🍔 Original Food System
* `images/` - folder with misc images for the project
* `data_exploration/` - notebooks & data exploring the USDA FoodData Central data (this has info about the nutrition content of foods)
* `food_image_collector.py` - Streamlit-powered app that collects photos and uploads them to a Google Storage bucket and stores metadata in Google Sheets (these are private), see the workflow below.
* `foodvision/` - Computer vision models and training pipeline for food recognition

### 📄 New OCR to Excel System
* `ocr_to_excel.py` - Main Streamlit app for document-to-Excel conversion
* `ocr_utils.py` - Core processing utilities for OCR, data extraction, and formatting
* `demo_ocr.py` - Command-line demo showing all OCR capabilities
* `launcher.py` - User-friendly launcher with menu system
* `README_OCR.md` - Comprehensive documentation for OCR features

### 🔄 Integration & Utilities  
* `nutricheck_extended.py` - Combined launcher for both food and OCR apps
* `requirements.txt` - A text file with the dependency requirements for this project.

## 🚀 Quick Start

### Option 1: Try the OCR Demo (No Dependencies)
```bash
python demo_ocr.py
```

### Option 2: Full Interactive Experience
```bash
python nutricheck_extended.py
# or
python launcher.py
```

### Option 3: Launch Specific Apps
```bash
streamlit run food_image_collector.py    # Food image collection
streamlit run ocr_to_excel.py           # OCR to Excel converter
```



## 📈 Development Roadmap

### Stage 1 (done)
Build food image collection app, need a way to store images at large scale, images: object storage (Google Storage), info about images: relational database (PostgreSQL).

### Stage 2 (done)  
Build small prototype computer vision app to take a photo of ~100 different types of foods and return back their nutrition information (this'll be done via a public nutrition API, if you know of one, please let me know).

### Stage 3 (up to here)
Merge inputs to stage 1 and stage 2 into a database (start linking together the data flywheel, more images get taken, models get improved, more images, better models, more images, better models, etc).

### Stage 4 (NEW - OCR Integration)
**✅ COMPLETED:** Built OCR to Excel converter that extends the platform with document processing capabilities:
- Multi-format input support (images, PDFs, screenshots)
- Smart data extraction with pattern recognition
- Flexible field mapping with template system
- Excel/CSV export functionality
- Integration with existing infrastructure

### Stage 5 (Food System Expansion)
Upgrade stage 1, 2, 3 to work with world's 100 most commonly eaten foods (start with top of the Pareto curve and then start working backwards towards the tail).

### Stage 6 (Combined Platform)
Merge food recognition and OCR capabilities into unified productivity platform:
- Restaurant receipt processing (expense + nutrition)
- Grocery receipt analysis (budget + meal planning) 
- Menu digitization (food database + OCR)
- Universal document processing

### Stage 7 (Scale)
Repeat the above until almost every food you can eat is covered + comprehensive document processing for any business need.

## 💰 Business Model Evolution

The addition of OCR to Excel capabilities dramatically expands the market opportunity:

**Original TAM (Food only):** ~$2B (nutrition apps market)
**Extended TAM (Food + OCR):** ~$50B+ (includes document processing, productivity tools, small business software)

**Revenue Streams:**
- Freemium model (free basic, premium advanced features)
- API access for developers  
- Enterprise licensing for bulk processing
- Template marketplace
- Integration partnerships (accounting software, CRMs)

This positions Nutricheck as a comprehensive productivity platform rather than just a food app.
