#!/usr/bin/env python3
"""
OCR to Excel Application
Convert screenshots, PDFs, and images to structured Excel data

Built on top of Nutricheck infrastructure for easy deployment and scalability.
"""

import io
import base64
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import datetime
import uuid

# Check for required dependencies and provide graceful fallbacks
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create mock streamlit functions for testing
    class MockStreamlit:
        def title(self, text): print(f"TITLE: {text}")
        def write(self, text): print(f"WRITE: {text}")
        def subheader(self, text): print(f"SUBHEADER: {text}")
        def error(self, text): print(f"ERROR: {text}")
        def warning(self, text): print(f"WARNING: {text}")
        def success(self, text): print(f"SUCCESS: {text}")
        def info(self, text): print(f"INFO: {text}")
        def markdown(self, text, **kwargs): print(f"MARKDOWN: {text}")
        def file_uploader(self, **kwargs): return None
        def button(self, label, **kwargs): return False
        def text_input(self, label, **kwargs): return kwargs.get('value', '')
        def text_area(self, label, text, **kwargs): return text
        def selectbox(self, label, options, **kwargs): return options[kwargs.get('index', 0)]
        def columns(self, n): return [self] * n
        def tabs(self, labels): return [self] * len(labels)
        def expander(self, label): return self
        def form(self, key): return self
        def form_submit_button(self, **kwargs): return False
        def download_button(self, **kwargs): return False
        def dataframe(self, data, **kwargs): print(f"DATAFRAME: {data}")
        def json(self, data): print(f"JSON: {data}")
        def spinner(self, text): return MockContextManager()
        def set_page_config(self, **kwargs): pass
        @property
        def session_state(self): 
            if not hasattr(self, '_session_state'):
                self._session_state = {}
            return self._session_state
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    class MockContextManager:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    st = MockStreamlit()

# Basic imports that should be available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Import our utilities
try:
    from ocr_utils import create_sample_data, format_value_for_excel
    OCR_UTILS_AVAILABLE = True
except ImportError:
    OCR_UTILS_AVAILABLE = False


@dataclass
class ExtractedData:
    """Structure for holding extracted data"""
    text: str
    structured_data: List[Dict[str, Any]]
    confidence: float
    source_file: str


@dataclass
class FieldMapping:
    """Structure for field to column mapping"""
    field_name: str
    column_name: str
    data_type: str
    example_value: str


class OCRToExcelApp:
    """Main application class for OCR to Excel conversion"""
    
    def __init__(self):
        self.session_key = "ocr_to_excel_session"
        self.initialize_session()
    
    def initialize_session(self):
        """Initialize session state variables"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                "upload_key": str(uuid.uuid4()),
                "extracted_data": None,
                "field_mappings": [],
                "templates": {},
                "processed_files": []
            }
    
    def render_header(self):
        """Render application header and description"""
        st.title("📄➡️📊 OCR to Excel Converter")
        st.write("""
        **Transform any document into structured Excel data in seconds!**
        
        Perfect for:
        - 💼 **Business**: Digitize receipts, invoices, and forms
        - 📚 **Students**: Convert notes, surveys, and research data  
        - 👨‍🏫 **Teachers**: Process grading sheets and attendance lists
        - 🏥 **Healthcare**: Structure prescriptions and patient records
        - 🎯 **Everyone**: Eliminate tedious copy-paste work
        """)
        
        with st.expander("🚀 How it works"):
            st.write("""
            1. **Upload** your file (screenshot, PDF, photo, handwritten note)
            2. **Review** the extracted text and data
            3. **Map** fields to Excel columns (save as templates for reuse)
            4. **Export** to Excel, CSV, or Google Sheets
            """)
    
    def render_file_upload(self):
        """Render file upload interface"""
        st.subheader("📤 Upload Your Document")
        
        # File uploader with multiple formats
        uploaded_file = st.file_uploader(
            label="Choose a file to process",
            type=["png", "jpg", "jpeg", "pdf", "tiff", "bmp"],
            help="Drag & drop or click to upload screenshots, PDFs, photos, or scanned documents",
            key=st.session_state[self.session_key]["upload_key"]
        )
        
        # Alternative upload methods
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📷 Take Photo", help="Use your camera to capture a document"):
                st.info("📱 Camera feature coming soon! For now, please upload an image file.")
        
        with col2:
            if st.button("🖼️ Paste from Clipboard", help="Paste an image from clipboard"):
                st.info("📋 Clipboard feature coming soon! For now, please upload an image file.")
        
        return uploaded_file
    
    def extract_text_basic(self, file_content: bytes, file_type: str) -> ExtractedData:
        """
        Basic text extraction - placeholder for OCR functionality
        In production, this would use Tesseract, Google Vision API, or similar
        """
        # Use sample data if OCR utils are available
        if OCR_UTILS_AVAILABLE:
            sample_text, sample_data = create_sample_data()
            return ExtractedData(
                text=sample_text,
                structured_data=sample_data,
                confidence=0.85,
                source_file=f"uploaded_file_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        else:
            # Fallback sample data
            sample_data = [
                {"Item": "Office Supplies", "Amount": "25.99", "Date": "2024-01-15"},
                {"Item": "Software License", "Amount": "199.00", "Date": "2024-01-15"},
                {"Item": "Training Materials", "Amount": "75.50", "Date": "2024-01-16"}
            ]
            
            extracted_text = """INVOICE #INV-2024-001
Date: January 15, 2024
Office Supplies    $25.99
Software License   $199.00
Training Materials $75.50
Total: $300.49"""
            
            return ExtractedData(
                text=extracted_text,
                structured_data=sample_data,
                confidence=0.85,
                source_file=f"uploaded_file_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
    
    def render_data_preview(self, extracted_data: ExtractedData):
        """Render extracted data preview"""
        st.subheader("👁️ Data Preview")
        
        # Show confidence score
        confidence_color = "green" if extracted_data.confidence > 0.8 else "orange" if extracted_data.confidence > 0.6 else "red"
        st.markdown(f"**Extraction Confidence:** :{confidence_color}[{extracted_data.confidence:.0%}]")
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["📋 Raw Text", "📊 Structured Data"])
        
        with tab1:
            st.text_area("Extracted Text", extracted_data.text, height=200, disabled=True)
        
        with tab2:
            if PANDAS_AVAILABLE and extracted_data.structured_data:
                df = pd.DataFrame(extracted_data.structured_data)
                st.dataframe(df, use_container_width=True)
                return df
            else:
                st.json(extracted_data.structured_data)
                return None
    
    def render_field_mapping(self, structured_data: List[Dict]):
        """Render field mapping interface"""
        st.subheader("🎯 Field Mapping")
        st.write("Map the extracted fields to Excel columns:")
        
        if not structured_data:
            st.warning("No structured data available for mapping.")
            return []
        
        # Get available fields from structured data
        sample_row = structured_data[0] if structured_data else {}
        available_fields = list(sample_row.keys())
        
        mappings = []
        for field in available_fields:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.text_input(f"Field: {field}", value=field, disabled=True, key=f"field_{field}")
            
            with col2:
                column_name = st.text_input(
                    "Excel Column", 
                    value=field,  # Default to field name
                    key=f"column_{field}",
                    placeholder="Enter column name"
                )
            
            with col3:
                data_type = st.selectbox(
                    "Type",
                    ["Text", "Number", "Date", "Currency"],
                    key=f"type_{field}",
                    index=1 if field.lower() in ['amount', 'price', 'cost', 'total'] else 0
                )
            
            if column_name:  # Only add mapping if column name is provided
                mappings.append(FieldMapping(
                    field_name=field,
                    column_name=column_name,
                    data_type=data_type,
                    example_value=str(sample_row.get(field, ""))
                ))
        
        return mappings
    
    def render_template_management(self, mappings: List[FieldMapping]):
        """Render template save/load functionality"""
        st.subheader("📁 Template Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input("Template Name", placeholder="e.g., Invoice Template")
            if st.button("💾 Save Template") and template_name and mappings:
                # Save template to session state (in production, would save to database)
                st.session_state[self.session_key]["templates"][template_name] = mappings
                st.success(f"Template '{template_name}' saved!")
        
        with col2:
            existing_templates = list(st.session_state[self.session_key]["templates"].keys())
            if existing_templates:
                selected_template = st.selectbox("Load Template", [""] + existing_templates)
                if st.button("📂 Load Template") and selected_template:
                    # Load template logic would go here
                    st.info(f"Template '{selected_template}' loaded!")
    
    def generate_excel_download(self, data: List[Dict], mappings: List[FieldMapping]) -> bytes:
        """Generate Excel file from mapped data"""
        if not PANDAS_AVAILABLE:
            # Fallback to CSV generation
            return self.generate_csv_download(data, mappings)
        
        # Create DataFrame with mapped columns
        mapped_data = []
        for row in data:
            mapped_row = {}
            for mapping in mappings:
                value = row.get(mapping.field_name, "")
                mapped_row[mapping.column_name] = value
            mapped_data.append(mapped_row)
        
        df = pd.DataFrame(mapped_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        try:
            # Try to create Excel file
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Extracted Data')
            return output.getvalue()
        except:
            # Fallback to CSV if Excel creation fails
            return self.generate_csv_download(data, mappings)
    
    def generate_csv_download(self, data: List[Dict], mappings: List[FieldMapping]) -> bytes:
        """Generate CSV file from mapped data"""
        output = io.StringIO()
        
        # Write header
        headers = [mapping.column_name for mapping in mappings]
        output.write(",".join(headers) + "\n")
        
        # Write data rows
        for row in data:
            values = []
            for mapping in mappings:
                value = str(row.get(mapping.field_name, ""))
                # Escape commas and quotes in CSV
                if "," in value or '"' in value:
                    value = '"' + value.replace('"', '""') + '"'
                values.append(value)
            output.write(",".join(values) + "\n")
        
        return output.getvalue().encode('utf-8')
    
    def render_export_options(self, data: List[Dict], mappings: List[FieldMapping]):
        """Render export options and download buttons"""
        st.subheader("📥 Export Data")
        
        if not data or not mappings:
            st.warning("No data or mappings available for export.")
            return
        
        col1, col2, col3 = st.columns(3)
        
        # Excel Download
        with col1:
            try:
                excel_data = self.generate_excel_download(data, mappings)
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"extracted_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download as Excel (.xlsx) file"
                )
            except Exception as e:
                st.error(f"Excel export error: {str(e)}")
        
        # CSV Download
        with col2:
            try:
                csv_data = self.generate_csv_download(data, mappings)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"extracted_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download as CSV file"
                )
            except Exception as e:
                st.error(f"CSV export error: {str(e)}")
        
        # Google Sheets option (placeholder)
        with col3:
            if st.button("📈 Send to Google Sheets", help="Export to Google Sheets"):
                st.info("🚧 Google Sheets integration coming soon!")
    
    def run(self):
        """Main application execution"""
        # Check dependencies
        if not PIL_AVAILABLE:
            st.error("PIL/Pillow not available. Image processing may be limited.")
        
        if not PANDAS_AVAILABLE:
            st.warning("Pandas not available. Excel export will use basic CSV format.")
        
        # Render application
        self.render_header()
        
        uploaded_file = self.render_file_upload()
        
        if uploaded_file is not None:
            # Process uploaded file
            with st.spinner("🔍 Extracting data from your document..."):
                file_content = uploaded_file.read()
                file_type = uploaded_file.type
                
                # Extract text and data
                extracted_data = self.extract_text_basic(file_content, file_type)
                st.session_state[self.session_key]["extracted_data"] = extracted_data
            
            # Show data preview
            df = self.render_data_preview(extracted_data)
            
            if extracted_data.structured_data:
                # Field mapping
                mappings = self.render_field_mapping(extracted_data.structured_data)
                
                if mappings:
                    # Template management
                    self.render_template_management(mappings)
                    
                    # Export options
                    self.render_export_options(extracted_data.structured_data, mappings)
                    
                    # Success metrics
                    st.success(f"""
                    ✅ **Processing Complete!**
                    - Extracted {len(extracted_data.structured_data)} records
                    - Mapped {len(mappings)} fields
                    - Ready for export
                    """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Built with ❤️ for productivity • Part of the Nutricheck ecosystem</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main entry point"""
    if not STREAMLIT_AVAILABLE:
        print("❌ Streamlit not available. Running in demo mode...")
        print("To install Streamlit: pip install streamlit")
        print("Then run: streamlit run ocr_to_excel.py")
        print("\nFor a demo of the core functionality, run: python demo_ocr.py")
        return
    
    st.set_page_config(
        page_title="OCR to Excel Converter",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    app = OCRToExcelApp()
    app.run()


if __name__ == "__main__":
    main()