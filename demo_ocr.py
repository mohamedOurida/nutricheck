#!/usr/bin/env python3
"""
OCR to Excel Demo - Command Line Version
Demonstrates the core functionality without Streamlit
"""

import json
import csv
import sys
from pathlib import Path

# Import our utilities
from ocr_utils import (
    create_sample_data,
    detect_data_patterns,
    extract_table_data,
    validate_data_quality,
    suggest_field_types,
    format_value_for_excel
)


def demo_ocr_processing():
    """Demonstrate OCR processing capabilities"""
    print("🔍 OCR to Excel Demo")
    print("=" * 50)
    
    # Get sample data
    print("\n1. Loading sample document...")
    sample_text, sample_data = create_sample_data()
    
    print("✅ Sample invoice loaded")
    print(f"   Text length: {len(sample_text)} characters")
    print(f"   Structured data: {len(sample_data)} records")
    
    # Demonstrate pattern detection
    print("\n2. Detecting data patterns...")
    patterns = detect_data_patterns(sample_text)
    
    for pattern_type, matches in patterns.items():
        if matches:
            print(f"   {pattern_type.replace('_', ' ').title()}: {len(matches)} found")
            if len(matches) <= 3:
                print(f"      {matches}")
            else:
                print(f"      {matches[:3]}... (and {len(matches) - 3} more)")
    
    # Demonstrate table extraction
    print("\n3. Extracting table data...")
    extracted_tables = extract_table_data(sample_text)
    print(f"   Extracted {len(extracted_tables)} table rows")
    
    # Use the pre-structured sample data for better demo
    demo_data = sample_data
    
    # Demonstrate data quality validation
    print("\n4. Validating data quality...")
    quality_metrics = validate_data_quality(demo_data)
    print(f"   Total rows: {quality_metrics['total_rows']}")
    print(f"   Total fields: {quality_metrics['total_fields']}")
    print(f"   Completeness: {quality_metrics['completeness']:.1%}")
    
    if quality_metrics['issues']:
        print(f"   Issues found: {len(quality_metrics['issues'])}")
        for issue in quality_metrics['issues'][:3]:
            print(f"      • {issue}")
    
    # Demonstrate field type suggestions
    print("\n5. Analyzing field types...")
    suggested_types = suggest_field_types(demo_data)
    for field, field_type in suggested_types.items():
        print(f"   {field}: {field_type}")
    
    # Demonstrate Excel formatting
    print("\n6. Formatting for Excel export...")
    formatted_data = []
    for row in demo_data:
        formatted_row = {}
        for field, value in row.items():
            suggested_type = suggested_types.get(field, 'Text')
            formatted_value = format_value_for_excel(value, suggested_type)
            formatted_row[field] = formatted_value
        formatted_data.append(formatted_row)
    
    print("   ✅ Data formatted for Excel")
    
    # Export to CSV as demonstration
    print("\n7. Exporting to CSV...")
    output_file = "demo_output.csv"
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            if formatted_data:
                fieldnames = list(formatted_data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(formatted_data)
        
        print(f"   ✅ Data exported to {output_file}")
        
        # Show file contents
        print("\n8. Generated CSV content:")
        print("-" * 30)
        with open(output_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
    
    return demo_data, formatted_data


def demo_field_mapping():
    """Demonstrate field mapping functionality"""
    print("\n" + "=" * 50)
    print("🎯 Field Mapping Demo")
    print("=" * 50)
    
    # Sample extracted data
    extracted_data = [
        {"ITEM DESCRIPTION": "Office Supplies", "QTY": "2", "UNIT PRICE": "$12.99", "TOTAL": "$25.98"},
        {"ITEM DESCRIPTION": "Software License", "QTY": "1", "UNIT PRICE": "$199.00", "TOTAL": "$199.00"},
    ]
    
    print("Original fields:")
    for field in extracted_data[0].keys():
        print(f"  • {field}")
    
    # Define field mappings (what a user might configure)
    field_mappings = {
        "ITEM DESCRIPTION": {"excel_column": "Product", "type": "Text"},
        "QTY": {"excel_column": "Quantity", "type": "Number"},
        "UNIT PRICE": {"excel_column": "Unit_Price", "type": "Currency"},
        "TOTAL": {"excel_column": "Total_Amount", "type": "Currency"}
    }
    
    print("\nField mappings:")
    for original, mapping in field_mappings.items():
        print(f"  '{original}' → '{mapping['excel_column']}' ({mapping['type']})")
    
    # Apply mappings
    mapped_data = []
    for row in extracted_data:
        mapped_row = {}
        for original_field, value in row.items():
            mapping = field_mappings.get(original_field)
            if mapping:
                excel_column = mapping["excel_column"]
                data_type = mapping["type"]
                formatted_value = format_value_for_excel(value, data_type)
                mapped_row[excel_column] = formatted_value
        mapped_data.append(mapped_row)
    
    print("\nMapped data:")
    for i, row in enumerate(mapped_data, 1):
        print(f"  Row {i}:")
        for field, value in row.items():
            print(f"    {field}: {value} ({type(value).__name__})")
    
    return mapped_data


def main():
    """Run the complete demo"""
    print("🚀 Starting OCR to Excel Complete Demo\n")
    
    try:
        # Core processing demo
        original_data, formatted_data = demo_ocr_processing()
        
        # Field mapping demo
        mapped_data = demo_field_mapping()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Demo Summary")
        print("=" * 50)
        print("✅ OCR text extraction (simulated)")
        print("✅ Data pattern detection") 
        print("✅ Table structure extraction")
        print("✅ Data quality validation")
        print("✅ Field type analysis")
        print("✅ Excel formatting")
        print("✅ Field mapping")
        print("✅ CSV export")
        
        print(f"\nProcessed {len(original_data)} records successfully!")
        print("Demo files created:")
        print("  • demo_output.csv")
        
        # Show what the real app would offer
        print("\n🎯 Full Application Features:")
        print("• Upload images, PDFs, screenshots")
        print("• Real OCR with Tesseract/Cloud Vision")
        print("• Interactive field mapping interface") 
        print("• Template save/load functionality")
        print("• Excel/CSV/Google Sheets export")
        print("• Batch processing capabilities")
        print("• Data validation and preview")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())