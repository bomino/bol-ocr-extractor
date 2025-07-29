#!/usr/bin/env python3
"""
Bill of Lading OCR Application
A complete Python application for extracting data from PDF Bills of Lading (BOLs) 
and exporting to Excel format. Supports both text-based and scanned PDFs with 
automatic OCR fallback.

Dependencies:
    streamlit>=1.28.0
    pdfplumber>=0.9.0  
    pandas>=2.0.0
    pytesseract>=0.3.10
    Pillow>=10.0.0
    tabula-py>=2.8.0
    openpyxl>=3.1.0
    regex>=2023.0.0

System Requirements:
    - Tesseract OCR engine must be installed separately
    - Java runtime required for tabula-py

Usage:
    streamlit run app.py

Author: Claude Code Assistant
"""

import streamlit as st
import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import tabula
import io
import re
import logging
import json
import zipfile
import tempfile
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BOLData:
    """Data structure for storing extracted BOL information."""
    filename: str = ""
    bol_number: str = ""
    shipper_name: str = ""
    shipper_address: str = ""
    consignee_name: str = ""
    consignee_address: str = ""
    notify_party_name: str = ""
    notify_party_address: str = ""
    vessel_name: str = ""
    voyage_number: str = ""
    port_of_load: str = ""
    port_of_discharge: str = ""
    description_of_goods: str = ""
    quantity_packages: str = ""
    gross_weight: str = ""
    net_weight: str = ""
    freight_terms: str = ""
    date_of_issue: str = ""
    extraction_method: str = ""  # "text" or "ocr"
    extraction_confidence: str = "medium"  # "high", "medium", "low"
    processing_notes: str = ""
    extraction_failed: bool = False

class FieldPatterns:
    """Configurable regex patterns for BOL field extraction."""
    
    def __init__(self):
        self.patterns = {
            "bol_number": [
                r"(?:B/L\s*(?:No|Number|#)\.?\s*:?\s*)([A-Z0-9\-]+)",
                r"(?:BOL\s*(?:No|Number|#)\.?\s*:?\s*)([A-Z0-9\-]+)",
                r"(?:Bill\s*of\s*Lading\s*(?:No|Number|#)\.?\s*:?\s*)([A-Z0-9\-]+)",
                r"(?:Document\s*(?:No|Number)\.?\s*:?\s*)([A-Z0-9\-]+)"
            ],
            "shipper": [
                r"(?:SHIPPER\.?\s*:?\s*)(.*?)(?=\n\s*(?:CONSIGNEE|Consignee|\n\n))",
                r"(?:Shipper\.?\s*:?\s*)(.*?)(?=\n\s*(?:CONSIGNEE|Consignee|\n\n))",
                r"(?:FROM\.?\s*:?\s*)(.*?)(?=\n\s*(?:TO|CONSIGNEE|\n\n))"
            ],
            "consignee": [
                r"(?:CONSIGNEE\.?\s*:?\s*)(.*?)(?=\n\s*(?:NOTIFY|Notify|VESSEL|\n\n))",
                r"(?:Consignee\.?\s*:?\s*)(.*?)(?=\n\s*(?:NOTIFY|Notify|VESSEL|\n\n))",
                r"(?:TO\.?\s*:?\s*)(.*?)(?=\n\s*(?:NOTIFY|Notify|VESSEL|\n\n))"
            ],
            "notify_party": [
                r"(?:NOTIFY\s*PARTY\.?\s*:?\s*)(.*?)(?=\n\s*(?:VESSEL|PORT|GOODS|\n\n))",
                r"(?:Notify\s*Party\.?\s*:?\s*)(.*?)(?=\n\s*(?:VESSEL|PORT|GOODS|\n\n))",
                r"(?:ALSO\s*NOTIFY\.?\s*:?\s*)(.*?)(?=\n\s*(?:VESSEL|PORT|GOODS|\n\n))"
            ],
            "vessel": [
                r"(?:VESSEL\.?\s*:?\s*)([^\n]+)",
                r"(?:Vessel\.?\s*:?\s*)([^\n]+)",
                r"(?:SHIP\s*NAME\.?\s*:?\s*)([^\n]+)"
            ],
            "voyage": [
                r"(?:VOYAGE\.?\s*:?\s*)([A-Z0-9\-]+)",
                r"(?:Voyage\.?\s*:?\s*)([A-Z0-9\-]+)",
                r"(?:VOY\.?\s*:?\s*)([A-Z0-9\-]+)"
            ],
            "port_of_load": [
                r"(?:PORT\s*OF\s*(?:LOADING|LOAD)\.?\s*:?\s*)([^\n]+)",
                r"(?:Port\s*of\s*(?:Loading|Load)\.?\s*:?\s*)([^\n]+)",
                r"(?:LOAD\s*PORT\.?\s*:?\s*)([^\n]+)"
            ],
            "port_of_discharge": [
                r"(?:PORT\s*OF\s*(?:DISCHARGE|DEST)\.?\s*:?\s*)([^\n]+)",
                r"(?:Port\s*of\s*(?:Discharge|Dest)\.?\s*:?\s*)([^\n]+)",
                r"(?:DISCHARGE\s*PORT\.?\s*:?\s*)([^\n]+)"
            ],
            "freight_terms": [
                r"(?:FREIGHT\.?\s*:?\s*)(PREPAID|COLLECT|PAYABLE)",
                r"(?:Freight\.?\s*:?\s*)(PREPAID|COLLECT|PAYABLE)",
                r"(?:TERMS\.?\s*:?\s*)(PREPAID|COLLECT|PAYABLE)"
            ],
            "date_patterns": [
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})",
                r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4})"
            ],
            "weight_patterns": [
                r"(?:GROSS\s*WEIGHT\.?\s*:?\s*)([0-9,.\s]+(?:KG|LBS|MT|TON))",
                r"(?:NET\s*WEIGHT\.?\s*:?\s*)([0-9,.\s]+(?:KG|LBS|MT|TON))",
                r"(?:WEIGHT\.?\s*:?\s*)([0-9,.\s]+(?:KG|LBS|MT|TON))"
            ],
            "quantity_patterns": [
                r"(?:PACKAGES\.?\s*:?\s*)([0-9,.\s]+)",
                r"(?:QUANTITY\.?\s*:?\s*)([0-9,.\s]+)",
                r"(?:QTY\.?\s*:?\s*)([0-9,.\s]+)"
            ]
        }

    def get_patterns(self, field_type: str) -> List[str]:
        """Get regex patterns for a specific field type."""
        return self.patterns.get(field_type, [])

class PDFProcessor:
    """Handles PDF text extraction and OCR processing."""
    
    def __init__(self):
        self.min_text_threshold = 100  # Minimum characters to consider text extraction successful
        
    def extract_text_pdfplumber(self, pdf_file) -> Tuple[str, bool]:
        """Extract text from PDF using pdfplumber."""
        try:
            text_content = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            success = len(text_content.strip()) >= self.min_text_threshold
            logger.info(f"Text extraction: {len(text_content)} characters, success: {success}")
            return text_content, success
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            return "", False

    def extract_text_ocr(self, pdf_file) -> Tuple[str, bool]:
        """Extract text from PDF using OCR."""
        try:
            import fitz  # PyMuPDF - fallback if available
            text_content = ""
            
            # Convert PDF to images and apply OCR
            with pdfplumber.open(pdf_file) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Convert page to image
                    img = page.to_image(resolution=300)
                    
                    # Apply OCR
                    ocr_text = pytesseract.image_to_string(
                        img.original, 
                        config='--psm 6 --oem 3'  # Optimized settings for documents
                    )
                    text_content += ocr_text + "\n"
                    
                    logger.info(f"OCR page {i+1}: {len(ocr_text)} characters")
            
            success = len(text_content.strip()) >= self.min_text_threshold
            logger.info(f"OCR extraction: {len(text_content)} characters, success: {success}")
            return text_content, success
            
        except Exception as e:
            logger.error(f"Error in OCR extraction: {str(e)}")
            return "", False

    def assess_text_quality(self, text: str) -> str:
        """Assess the quality of extracted text."""
        if len(text.strip()) < 50:
            return "low"
        
        # Check for common indicators of good text extraction
        has_structured_fields = any(keyword in text.upper() for keyword in 
                                  ["SHIPPER", "CONSIGNEE", "VESSEL", "B/L", "BOL"])
        has_addresses = text.count('\n') > 5  # Multiple lines suggest structured data
        
        if has_structured_fields and has_addresses:
            return "high"
        elif has_structured_fields or has_addresses:
            return "medium"
        else:
            return "low"

    def process_pdf(self, pdf_file, filename: str) -> Tuple[str, str, str]:
        """Main method to process PDF with hybrid approach."""
        logger.info(f"Processing PDF: {filename}")
        
        # Try text extraction first
        text_content, text_success = self.extract_text_pdfplumber(pdf_file)
        extraction_method = "text"
        confidence = self.assess_text_quality(text_content)
        
        # Fall back to OCR if text extraction is insufficient
        if not text_success or confidence == "low":
            logger.info("Falling back to OCR extraction")
            ocr_text, ocr_success = self.extract_text_ocr(pdf_file)
            
            if ocr_success:
                text_content = ocr_text
                extraction_method = "ocr"
                confidence = self.assess_text_quality(text_content)
            elif text_content:  # Use original text if OCR fails
                extraction_method = "text_fallback"
        
        return text_content, extraction_method, confidence

class TableParser:
    """Handles table extraction from PDFs."""
    
    def extract_tables(self, pdf_file) -> List[pd.DataFrame]:
        """Extract tables from PDF using tabula-py."""
        try:
            # Extract all tables from the PDF
            tables = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
            
            if tables:
                logger.info(f"Extracted {len(tables)} tables from PDF")
                return tables
            else:
                logger.info("No tables found in PDF")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting tables: {str(e)}")
            return []

    def parse_cargo_description_table(self, tables: List[pd.DataFrame]) -> str:
        """Parse cargo description from extracted tables."""
        cargo_descriptions = []
        
        for table in tables:
            # Look for columns that might contain cargo descriptions
            description_columns = []
            for col in table.columns:
                if any(keyword in str(col).upper() for keyword in 
                      ['DESCRIPTION', 'GOODS', 'CARGO', 'COMMODITY']):
                    description_columns.append(col)
            
            if description_columns:
                for col in description_columns:
                    descriptions = table[col].dropna().astype(str).tolist()
                    cargo_descriptions.extend(descriptions)
        
        return "; ".join(cargo_descriptions) if cargo_descriptions else ""

class BOLDataExtractor:
    """Extracts specific BOL fields from text using regex patterns."""
    
    def __init__(self):
        self.patterns = FieldPatterns()
        
    def extract_field(self, text: str, field_type: str) -> str:
        """Extract a specific field using regex patterns."""
        patterns = self.patterns.get_patterns(field_type)
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                result = match.group(1).strip()
                if result:  # Only return non-empty results
                    return self.clean_field_data(result)
        
        return ""

    def clean_field_data(self, data: str) -> str:
        """Clean and normalize extracted field data."""
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', data.strip())
        
        # Remove common artifacts
        cleaned = re.sub(r'^[:\-\s]+', '', cleaned)
        cleaned = re.sub(r'[:\-\s]+$', '', cleaned)
        
        return cleaned

    def extract_bol_number(self, text: str) -> str:
        """Extract Bill of Lading number."""
        return self.extract_field(text, "bol_number")

    def extract_parties(self, text: str) -> Tuple[str, str, str, str, str, str]:
        """Extract shipper, consignee, and notify party information."""
        shipper_text = self.extract_field(text, "shipper") 
        consignee_text = self.extract_field(text, "consignee")
        notify_text = self.extract_field(text, "notify_party")
        
        # Split name and address (first line vs rest)
        def split_name_address(text):
            if not text:
                return "", ""
            lines = text.split('\n')
            name = lines[0].strip()
            address = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
            return name, address
        
        shipper_name, shipper_address = split_name_address(shipper_text)
        consignee_name, consignee_address = split_name_address(consignee_text)
        notify_name, notify_address = split_name_address(notify_text)
        
        return (shipper_name, shipper_address, consignee_name, 
                consignee_address, notify_name, notify_address)

    def extract_vessel_info(self, text: str) -> Tuple[str, str]:
        """Extract vessel name and voyage number."""
        vessel_name = self.extract_field(text, "vessel")
        voyage_number = self.extract_field(text, "voyage")
        return vessel_name, voyage_number

    def extract_ports(self, text: str) -> Tuple[str, str]:
        """Extract port of loading and discharge."""
        port_load = self.extract_field(text, "port_of_load")
        port_discharge = self.extract_field(text, "port_of_discharge")
        return port_load, port_discharge

    def extract_dates(self, text: str) -> str:
        """Extract date of issue."""
        patterns = self.patterns.get_patterns("date_patterns")
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Return the first date found
                return matches[0]
        
        return ""

    def extract_weights_quantities(self, text: str) -> Tuple[str, str, str]:
        """Extract gross weight, net weight, and quantity."""
        weight_patterns = self.patterns.get_patterns("weight_patterns")
        quantity_patterns = self.patterns.get_patterns("quantity_patterns")
        
        gross_weight = ""
        net_weight = ""
        quantity = ""
        
        # Extract weights
        for pattern in weight_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if "GROSS" in pattern.upper():
                    gross_weight = matches[0]
                elif "NET" in pattern.upper():
                    net_weight = matches[0]
                elif not gross_weight:  # Use generic weight as gross if no specific gross found
                    gross_weight = matches[0]
        
        # Extract quantity
        for pattern in quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                quantity = match.group(1).strip()
                break
        
        return gross_weight, net_weight, quantity

    def extract_freight_terms(self, text: str) -> str:
        """Extract freight terms."""
        return self.extract_field(text, "freight_terms")

    def extract_all_fields(self, text: str, tables: List[pd.DataFrame], filename: str) -> BOLData:
        """Extract all BOL fields from text and tables."""
        bol_data = BOLData()
        bol_data.filename = filename
        
        try:
            # Extract basic fields
            bol_data.bol_number = self.extract_bol_number(text)
            
            # Extract party information
            (bol_data.shipper_name, bol_data.shipper_address,
             bol_data.consignee_name, bol_data.consignee_address,
             bol_data.notify_party_name, bol_data.notify_party_address) = self.extract_parties(text)
            
            # Extract vessel and voyage
            bol_data.vessel_name, bol_data.voyage_number = self.extract_vessel_info(text)
            
            # Extract ports
            bol_data.port_of_load, bol_data.port_of_discharge = self.extract_ports(text)
            
            # Extract dates
            bol_data.date_of_issue = self.extract_dates(text)
            
            # Extract weights and quantities
            (bol_data.gross_weight, bol_data.net_weight, 
             bol_data.quantity_packages) = self.extract_weights_quantities(text)
            
            # Extract freight terms
            bol_data.freight_terms = self.extract_freight_terms(text)
            
            # Extract cargo description from tables if available
            if tables:
                table_parser = TableParser()
                bol_data.description_of_goods = table_parser.parse_cargo_description_table(tables)
            
            # If no table description, try to extract from text
            if not bol_data.description_of_goods:
                # Simple heuristic to find goods description
                goods_patterns = [
                    r"(?:DESCRIPTION\s*OF\s*GOODS\.?\s*:?\s*)(.*?)(?=\n\s*(?:[A-Z]+:|$))",
                    r"(?:GOODS\.?\s*:?\s*)(.*?)(?=\n\s*(?:[A-Z]+:|$))",
                    r"(?:CARGO\.?\s*:?\s*)(.*?)(?=\n\s*(?:[A-Z]+:|$))"
                ]
                
                for pattern in goods_patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    if match:
                        bol_data.description_of_goods = self.clean_field_data(match.group(1))
                        break
            
            logger.info(f"Extracted data for {filename}: BOL# {bol_data.bol_number}")
            
        except Exception as e:
            logger.error(f"Error extracting fields from {filename}: {str(e)}")
            bol_data.extraction_failed = True
            bol_data.processing_notes = f"Extraction error: {str(e)}"
        
        return bol_data

class ExcelExporter:
    """Handles Excel export functionality."""
    
    def __init__(self):
        self.column_order = [
            'filename', 'bol_number', 'shipper_name', 'shipper_address',
            'consignee_name', 'consignee_address', 'notify_party_name', 'notify_party_address',
            'vessel_name', 'voyage_number', 'port_of_load', 'port_of_discharge',
            'description_of_goods', 'quantity_packages', 'gross_weight', 'net_weight',
            'freight_terms', 'date_of_issue', 'extraction_method', 'extraction_confidence',
            'processing_notes', 'extraction_failed'
        ]

    def create_dataframe(self, bol_data_list: List[BOLData]) -> pd.DataFrame:
        """Create pandas DataFrame from BOL data list."""
        data_dicts = []
        
        for bol_data in bol_data_list:
            data_dict = {
                'filename': bol_data.filename,
                'bol_number': bol_data.bol_number,
                'shipper_name': bol_data.shipper_name,
                'shipper_address': bol_data.shipper_address,
                'consignee_name': bol_data.consignee_name,
                'consignee_address': bol_data.consignee_address,
                'notify_party_name': bol_data.notify_party_name,
                'notify_party_address': bol_data.notify_party_address,
                'vessel_name': bol_data.vessel_name,
                'voyage_number': bol_data.voyage_number,
                'port_of_load': bol_data.port_of_load,
                'port_of_discharge': bol_data.port_of_discharge,
                'description_of_goods': bol_data.description_of_goods,
                'quantity_packages': bol_data.quantity_packages,
                'gross_weight': bol_data.gross_weight,
                'net_weight': bol_data.net_weight,
                'freight_terms': bol_data.freight_terms,
                'date_of_issue': bol_data.date_of_issue,
                'extraction_method': bol_data.extraction_method,
                'extraction_confidence': bol_data.extraction_confidence,
                'processing_notes': bol_data.processing_notes,
                'extraction_failed': bol_data.extraction_failed
            }
            data_dicts.append(data_dict)
        
        df = pd.DataFrame(data_dicts)
        return df[self.column_order]  # Ensure consistent column order

    def export_to_excel(self, bol_data_list: List[BOLData], output_filename: str = None) -> io.BytesIO:
        """Export BOL data to Excel format."""
        df = self.create_dataframe(bol_data_list)
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='BOL_Data', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total PDFs Processed',
                    'Successful Extractions', 
                    'Failed Extractions',
                    'Text-based Extractions',
                    'OCR-based Extractions',
                    'High Confidence',
                    'Medium Confidence', 
                    'Low Confidence'
                ],
                'Count': [
                    len(bol_data_list),
                    len([x for x in bol_data_list if not x.extraction_failed]),
                    len([x for x in bol_data_list if x.extraction_failed]),
                    len([x for x in bol_data_list if x.extraction_method == 'text']),
                    len([x for x in bol_data_list if 'ocr' in x.extraction_method]),
                    len([x for x in bol_data_list if x.extraction_confidence == 'high']),
                    len([x for x in bol_data_list if x.extraction_confidence == 'medium']),
                    len([x for x in bol_data_list if x.extraction_confidence == 'low'])
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Processing_Summary', index=False)
        
        excel_buffer.seek(0)
        return excel_buffer

    def export_to_csv(self, bol_data_list: List[BOLData]) -> io.StringIO:
        """Export BOL data to CSV format."""
        df = self.create_dataframe(bol_data_list)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        return csv_buffer

class BOLOCRApp:
    """Main application class for the Streamlit interface."""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.table_parser = TableParser()
        self.data_extractor = BOLDataExtractor()
        self.excel_exporter = ExcelExporter()
        
        # Initialize session state
        if 'processed_data' not in st.session_state:
            st.session_state.processed_data = []
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False

    def process_single_pdf(self, pdf_file, filename: str) -> BOLData:
        """Process a single PDF file."""
        try:
            # Extract text from PDF
            text_content, extraction_method, confidence = self.pdf_processor.process_pdf(pdf_file, filename)
            
            # Extract tables
            tables = self.table_parser.extract_tables(pdf_file)
            
            # Extract BOL data
            bol_data = self.data_extractor.extract_all_fields(text_content, tables, filename)
            bol_data.extraction_method = extraction_method
            bol_data.extraction_confidence = confidence
            
            return bol_data
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            bol_data = BOLData()
            bol_data.filename = filename
            bol_data.extraction_failed = True
            bol_data.processing_notes = f"Processing error: {str(e)}"
            return bol_data

    def process_batch_pdfs(self, files: List[Tuple[Any, str]]) -> List[BOLData]:
        """Process multiple PDF files."""
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (pdf_file, filename) in enumerate(files):
            status_text.text(f"Processing {filename}... ({i+1}/{len(files)})")
            
            bol_data = self.process_single_pdf(pdf_file, filename)
            results.append(bol_data)
            
            progress_bar.progress((i + 1) / len(files))
        
        status_text.text("Processing complete!")
        return results

    def render_sidebar(self):
        """Render the sidebar with configuration options."""
        st.sidebar.header("Configuration")
        
        # Export format selection
        export_format = st.sidebar.selectbox(
            "Export Format",
            ["Excel (.xlsx)", "CSV (.csv)"],
            index=0
        )
        
        # Processing options
        st.sidebar.subheader("Processing Options")
        
        ocr_enabled = st.sidebar.checkbox("Enable OCR Fallback", value=True)
        
        min_text_threshold = st.sidebar.slider(
            "Minimum Text Threshold",
            min_value=50,
            max_value=500,
            value=100,
            help="Minimum characters required for successful text extraction"
        )
        
        # Update processor settings
        self.pdf_processor.min_text_threshold = min_text_threshold
        
        return export_format, ocr_enabled

    def render_main_interface(self, export_format: str, ocr_enabled: bool):
        """Render the main application interface."""
        st.title("🚢 Bill of Lading OCR Extractor")
        st.markdown("""
        Upload PDF Bills of Lading to automatically extract key information and export to Excel/CSV.
        Supports both text-based and scanned PDFs with automatic OCR fallback.
        """)
        
        # File upload section
        st.header("📁 Upload Files")
        
        upload_option = st.radio(
            "Choose upload method:",
            ["Single PDF File", "Multiple PDF Files", "ZIP Archive"]
        )
        
        uploaded_files = []
        
        if upload_option == "Single PDF File":
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                accept_multiple_files=False
            )
            if uploaded_file:
                uploaded_files = [(uploaded_file, uploaded_file.name)]
                
        elif upload_option == "Multiple PDF Files":
            uploaded_file_list = st.file_uploader(
                "Choose PDF files",
                type=['pdf'],
                accept_multiple_files=True
            )
            if uploaded_file_list:
                uploaded_files = [(f, f.name) for f in uploaded_file_list]
                
        elif upload_option == "ZIP Archive":
            uploaded_zip = st.file_uploader(
                "Choose a ZIP file containing PDFs",
                type=['zip'],
                accept_multiple_files=False
            )
            
            if uploaded_zip:
                try:
                    with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
                        pdf_files = [name for name in zip_ref.namelist() if name.lower().endswith('.pdf')]
                        
                        if pdf_files:
                            for pdf_name in pdf_files:
                                pdf_data = zip_ref.read(pdf_name)
                                pdf_file = io.BytesIO(pdf_data)
                                uploaded_files.append((pdf_file, pdf_name))
                            
                            st.success(f"Found {len(pdf_files)} PDF files in the ZIP archive")
                        else:
                            st.warning("No PDF files found in the ZIP archive")
                            
                except Exception as e:
                    st.error(f"Error reading ZIP file: {str(e)}")
        
        # Processing section
        if uploaded_files:
            st.header("⚙️ Processing")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Files to Process", len(uploaded_files))
            
            with col2:
                st.metric("OCR Enabled", "Yes" if ocr_enabled else "No")
            
            if st.button("🚀 Start Processing", type="primary"):
                with st.spinner("Processing PDFs..."):
                    st.session_state.processed_data = self.process_batch_pdfs(uploaded_files)
                    st.session_state.processing_complete = True
                
                st.success("Processing completed!")
        
        # Results section
        if st.session_state.processing_complete and st.session_state.processed_data:
            self.render_results(export_format)

    def render_results(self, export_format: str):
        """Render the results section with data preview and download."""
        st.header("📊 Results")
        
        processed_data = st.session_state.processed_data
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", len(processed_data))
        
        with col2:
            successful = len([x for x in processed_data if not x.extraction_failed])
            st.metric("Successful", successful)
        
        with col3:
            failed = len([x for x in processed_data if x.extraction_failed])
            st.metric("Failed", failed)
        
        with col4:
            ocr_used = len([x for x in processed_data if 'ocr' in x.extraction_method])
            st.metric("OCR Used", ocr_used)
        
        # Data preview
        st.subheader("📋 Data Preview")
        
        df = self.excel_exporter.create_dataframe(processed_data)
        
        # Display key columns only for preview
        preview_columns = ['filename', 'bol_number', 'shipper_name', 'consignee_name', 
                          'vessel_name', 'extraction_method', 'extraction_confidence']
        
        available_columns = [col for col in preview_columns if col in df.columns]
        st.dataframe(df[available_columns], use_container_width=True)
        
        # Download section
        st.subheader("💾 Download Results")
        
        if export_format == "Excel (.xlsx)":
            excel_buffer = self.excel_exporter.export_to_excel(processed_data)
            
            st.download_button(
                label="📥 Download Excel File",
                data=excel_buffer.getvalue(),
                file_name=f"bol_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        else:  # CSV format
            csv_buffer = self.excel_exporter.export_to_csv(processed_data)
            
            st.download_button(
                label="📥 Download CSV File",
                data=csv_buffer.getvalue(),
                file_name=f"bol_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Detailed results (expandable)
        with st.expander("🔍 View Detailed Results"):
            st.dataframe(df, use_container_width=True)
        
        # Error details (if any)
        failed_extractions = [x for x in processed_data if x.extraction_failed]
        if failed_extractions:
            with st.expander("❌ Failed Extractions Details"):
                for bol_data in failed_extractions:
                    st.error(f"**{bol_data.filename}**: {bol_data.processing_notes}")

    def render_help_section(self):
        """Render help and instructions."""
        with st.expander("📖 Help & Instructions"):
            st.markdown("""
            ### How to Use This Application
            
            1. **Upload Files**: Choose to upload a single PDF, multiple PDFs, or a ZIP archive containing PDFs
            2. **Configure Settings**: Use the sidebar to adjust processing options
            3. **Process**: Click "Start Processing" to extract data from your PDFs
            4. **Download**: Export results as Excel or CSV format
            
            ### Supported Data Fields
            
            The application extracts the following information from Bills of Lading:
            
            - **Bill of Lading Number**
            - **Shipper Information** (Name & Address)
            - **Consignee Information** (Name & Address) 
            - **Notify Party Information** (Name & Address)
            - **Vessel Name & Voyage Number**
            - **Port of Loading & Discharge**
            - **Description of Goods**
            - **Quantity/Packages**
            - **Weight Information** (Gross/Net)
            - **Freight Terms**
            - **Date of Issue**
            
            ### Processing Methods
            
            - **Text Extraction**: Fast processing for text-based PDFs
            - **OCR Processing**: Slower but handles scanned/image-based PDFs
            - **Hybrid Approach**: Automatically switches to OCR if text extraction yields insufficient results
            
            ### Tips for Best Results
            
            - Ensure PDFs are high quality and clearly readable
            - For scanned documents, higher resolution improves OCR accuracy
            - The application works best with standard BOL formats
            - Review results before final use, especially for critical business applications
            
            ### System Requirements
            
            - Tesseract OCR engine must be installed on the system
            - Java runtime required for table extraction features
            """)

    def run(self):
        """Main application entry point."""
        st.set_page_config(
            page_title="BOL OCR Extractor",
            page_icon="🚢",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Render sidebar configuration
        export_format, ocr_enabled = self.render_sidebar()
        
        # Render main interface
        self.render_main_interface(export_format, ocr_enabled)
        
        # Render help section
        self.render_help_section()

def main():
    """Application entry point."""
    app = BOLOCRApp()
    app.run()

if __name__ == "__main__":
    main()