"""
Utility functions for OCR and data processing
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid


def create_unique_filename(prefix: str = "ocr", extension: str = "txt") -> str:
    """Generate a unique filename for processed files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"


def detect_data_patterns(text: str) -> Dict[str, Any]:
    """
    Detect common data patterns in text (dates, currencies, numbers, etc.)
    This is a basic implementation that can be extended with ML models
    """
    patterns = {
        'dates': [],
        'currencies': [],
        'numbers': [],
        'emails': [],
        'phone_numbers': []
    }
    
    # Date patterns (various formats)
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY or M/D/YYYY
        r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY or M-D-YYYY
        r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        patterns['dates'].extend(matches)
    
    # Currency patterns
    currency_patterns = [
        r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # $123.45, $1,234.56
        r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|CAD)\b',  # 123.45 USD
    ]
    
    for pattern in currency_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        patterns['currencies'].extend(matches)
    
    # General numbers
    number_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?\b'
    patterns['numbers'] = re.findall(number_pattern, text)
    
    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    patterns['emails'] = re.findall(email_pattern, text)
    
    # Phone numbers (basic patterns)
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{10}\b'  # 1234567890
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        patterns['phone_numbers'].extend(matches)
    
    return patterns


def extract_table_data(text: str) -> List[Dict[str, str]]:
    """
    Extract tabular data from text
    This is a basic implementation that looks for common table patterns
    """
    lines = text.strip().split('\n')
    table_data = []
    
    # Look for lines that might represent table rows
    potential_rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line contains multiple "columns" separated by whitespace/tabs
        # or common separators
        if re.search(r'\s{2,}|\t|,', line):
            # Split on multiple spaces, tabs, or commas
            columns = re.split(r'\s{2,}|\t|,', line)
            columns = [col.strip() for col in columns if col.strip()]
            if len(columns) >= 2:  # At least 2 columns
                potential_rows.append(columns)
    
    if not potential_rows:
        return []
    
    # Assume first row might be headers if it doesn't contain numbers/currency
    headers = None
    data_rows = potential_rows
    
    if potential_rows:
        first_row = potential_rows[0]
        # Check if first row looks like headers (mostly text, no currency/numbers)
        has_numbers = any(re.search(r'[\d$]', col) for col in first_row)
        if not has_numbers and len(potential_rows) > 1:
            headers = first_row
            data_rows = potential_rows[1:]
    
    # Create dictionaries from the rows
    if headers:
        for row in data_rows:
            if len(row) >= len(headers):
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        row_dict[header] = row[i]
                table_data.append(row_dict)
    else:
        # Create generic column names
        max_cols = max(len(row) for row in data_rows) if data_rows else 0
        generic_headers = [f"Column_{i+1}" for i in range(max_cols)]
        
        for row in data_rows:
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(generic_headers):
                    row_dict[generic_headers[i]] = value
            table_data.append(row_dict)
    
    return table_data


def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common OCR artifacts
    text = re.sub(r'[|]{2,}', '', text)  # Multiple pipes
    text = re.sub(r'[-_]{3,}', '', text)  # Multiple dashes/underscores
    
    # Normalize line breaks
    text = re.sub(r'\r\n?', '\n', text)
    
    return text.strip()


def validate_data_quality(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate the quality of extracted data
    Returns metrics about data completeness and consistency
    """
    if not data:
        return {
            'total_rows': 0,
            'total_fields': 0,
            'completeness': 0.0,
            'issues': ['No data available']
        }
    
    total_rows = len(data)
    all_fields = set()
    for row in data:
        all_fields.update(row.keys())
    
    total_fields = len(all_fields)
    total_cells = total_rows * total_fields
    filled_cells = 0
    issues = []
    
    # Count filled cells and identify issues
    for row_idx, row in enumerate(data):
        for field in all_fields:
            value = row.get(field, '')
            if value and str(value).strip():
                filled_cells += 1
            else:
                if len(issues) < 10:  # Limit issue reporting
                    issues.append(f"Empty value in row {row_idx + 1}, field '{field}'")
    
    completeness = filled_cells / total_cells if total_cells > 0 else 0.0
    
    # Check for consistency
    if total_rows > 1:
        field_counts = {}
        for row in data:
            for field in row.keys():
                field_counts[field] = field_counts.get(field, 0) + 1
        
        # Identify fields that are missing in some rows
        inconsistent_fields = [
            field for field, count in field_counts.items() 
            if count < total_rows
        ]
        
        if inconsistent_fields and len(issues) < 10:
            issues.append(f"Inconsistent fields: {', '.join(inconsistent_fields[:3])}")
    
    return {
        'total_rows': total_rows,
        'total_fields': total_fields,
        'completeness': completeness,
        'filled_cells': filled_cells,
        'total_cells': total_cells,
        'issues': issues
    }


def suggest_field_types(data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Analyze data and suggest appropriate field types
    """
    if not data:
        return {}
    
    field_types = {}
    all_fields = set()
    for row in data:
        all_fields.update(row.keys())
    
    for field in all_fields:
        values = [str(row.get(field, '')) for row in data if row.get(field)]
        values = [v for v in values if v.strip()]
        
        if not values:
            field_types[field] = 'Text'
            continue
        
        # Check if all values look like numbers
        numeric_count = 0
        currency_count = 0
        date_count = 0
        
        for value in values:
            value = value.strip()
            
            # Check for currency
            if re.match(r'^\$?\d+(?:,\d{3})*(?:\.\d{2})?$', value):
                currency_count += 1
            
            # Check for pure numbers
            elif re.match(r'^\d+(?:\.\d+)?$', value.replace(',', '')):
                numeric_count += 1
            
            # Check for dates
            elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', value) or \
                 re.match(r'\d{4}-\d{1,2}-\d{1,2}', value) or \
                 re.match(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', value, re.IGNORECASE):
                date_count += 1
        
        total_values = len(values)
        
        # Determine type based on majority
        if currency_count / total_values > 0.7:
            field_types[field] = 'Currency'
        elif numeric_count / total_values > 0.7:
            field_types[field] = 'Number'
        elif date_count / total_values > 0.7:
            field_types[field] = 'Date'
        else:
            field_types[field] = 'Text'
    
    return field_types


def format_value_for_excel(value: Any, data_type: str) -> Any:
    """
    Format a value appropriately for Excel export based on its data type
    """
    if not value or str(value).strip() == '':
        return ''
    
    value_str = str(value).strip()
    
    if data_type == 'Currency':
        # Remove currency symbols and convert to float
        clean_value = re.sub(r'[,$]', '', value_str)
        try:
            return float(clean_value)
        except ValueError:
            return value_str
    
    elif data_type == 'Number':
        # Convert to number if possible
        clean_value = value_str.replace(',', '')
        try:
            if '.' in clean_value:
                return float(clean_value)
            else:
                return int(clean_value)
        except ValueError:
            return value_str
    
    elif data_type == 'Date':
        # Keep as string for now (Excel will auto-detect dates)
        return value_str
    
    else:  # Text
        return value_str


def create_sample_data() -> Tuple[str, List[Dict[str, Any]]]:
    """
    Create sample data for demonstration purposes
    """
    sample_text = """INVOICE #INV-2024-001
    
Date: January 15, 2024
Bill To: ABC Company
123 Main Street

ITEM DESCRIPTION          QTY    UNIT PRICE    TOTAL
Office Supplies            2        $12.99     $25.98
Software License           1       $199.00    $199.00
Training Materials         3        $25.17     $75.51

                                   SUBTOTAL:   $300.49
                                        TAX:    $24.04
                                      TOTAL:   $324.53

Payment Terms: Net 30
Due Date: February 14, 2024
"""
    
    sample_structured_data = [
        {
            "Item": "Office Supplies",
            "Quantity": "2",
            "Unit_Price": "$12.99",
            "Total": "$25.98"
        },
        {
            "Item": "Software License", 
            "Quantity": "1",
            "Unit_Price": "$199.00",
            "Total": "$199.00"
        },
        {
            "Item": "Training Materials",
            "Quantity": "3", 
            "Unit_Price": "$25.17",
            "Total": "$75.51"
        }
    ]
    
    return sample_text, sample_structured_data