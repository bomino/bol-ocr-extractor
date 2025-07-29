# BOL OCR Extractor - API Reference & Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [Core Class APIs](#core-class-apis)
3. [Configuration Reference](#configuration-reference)
4. [Integration Patterns](#integration-patterns)
5. [Error Handling](#error-handling)
6. [Performance Considerations](#performance-considerations)
7. [Examples](#examples)

## Overview

The BOL OCR Extractor provides a comprehensive API for integrating document processing capabilities into your applications. The system offers both programmatic APIs for custom integration and REST endpoints for web service integration.

### API Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  BOLOCRApp    │  PDFProcessor  │  BOLDataExtractor          │
├─────────────────────────────────────────────────────────────┤
│  TableParser  │  FieldPatterns │  ExcelExporter             │
├─────────────────────────────────────────────────────────────┤
│                    Integration Layer                        │
├─────────────────────────────────────────────────────────────┤
│  REST API     │  CLI Interface │  Direct Class Usage        │
└─────────────────────────────────────────────────────────────┘
```

## Core Class APIs

### BOLOCRApp Class

The primary application controller that orchestrates the entire processing workflow.

#### Class Definition

```python
class BOLOCRApp:
    """
    Main application class for BOL OCR processing.
    
    Provides high-level interfaces for document processing with
    session management, progress tracking, and error handling.
    """
    
    def __init__(self):
        """Initialize application with all processing components."""
        
    def process_single_pdf(self, pdf_file, filename: str) -> BOLData:
        """Process a single PDF file and extract BOL data."""
        
    def process_batch_pdfs(self, files: List[Tuple[Any, str]]) -> List[BOLData]:
        """Process multiple PDF files in batch mode."""
```

#### Methods

##### `process_single_pdf(pdf_file, filename: str) -> BOLData`

Process a single PDF document and extract structured BOL data.

**Parameters:**
- `pdf_file`: File-like object containing PDF data
- `filename` (str): Original filename for tracking and reporting

**Returns:**
- `BOLData`: Structured data object containing extracted information

**Example:**
```python
app = BOLOCRApp()

with open('sample_bol.pdf', 'rb') as pdf_file:
    result = app.process_single_pdf(pdf_file, 'sample_bol.pdf')
    print(f"BOL Number: {result.bol_number}")
    print(f"Extraction Method: {result.extraction_method}")
    print(f"Confidence: {result.extraction_confidence}")
```

##### `process_batch_pdfs(files: List[Tuple[Any, str]]) -> List[BOLData]`

Process multiple PDF files with progress tracking and error resilience.

**Parameters:**
- `files`: List of tuples containing (file_object, filename) pairs

**Returns:**
- `List[BOLData]`: List of extraction results with metadata

**Example:**
```python
files = [
    (open('bol1.pdf', 'rb'), 'bol1.pdf'),
    (open('bol2.pdf', 'rb'), 'bol2.pdf'),
    (open('bol3.pdf', 'rb'), 'bol3.pdf')
]

results = app.process_batch_pdfs(files)
successful = [r for r in results if not r.extraction_failed]
print(f"Successfully processed {len(successful)} out of {len(results)} files")
```

### PDFProcessor Class

Handles PDF text extraction and OCR processing with intelligent fallback mechanisms.

#### Class Definition

```python
class PDFProcessor:
    """
    PDF processing engine with hybrid text extraction and OCR capabilities.
    
    Automatically determines the best extraction method based on content
    quality and provides confidence scoring for results.
    """
    
    def __init__(self):
        """Initialize processor with default configuration."""
        
    def extract_text_pdfplumber(self, pdf_file) -> Tuple[str, bool]:
        """Extract text using pdfplumber library."""
        
    def extract_text_ocr(self, pdf_file) -> Tuple[str, bool]:
        """Extract text using OCR (pytesseract)."""
        
    def assess_text_quality(self, text: str) -> str:
        """Assess the quality of extracted text."""
        
    def process_pdf(self, pdf_file, filename: str) -> Tuple[str, str, str]:
        """Main processing method with intelligent fallback."""
```

#### Configuration Properties

```python
class PDFProcessor:
    # Configurable thresholds
    min_text_threshold: int = 100  # Minimum characters for successful extraction
    ocr_confidence_threshold: float = 0.6  # Minimum OCR confidence score
    max_page_limit: int = 50  # Maximum pages to process
```

#### Methods

##### `process_pdf(pdf_file, filename: str) -> Tuple[str, str, str]`

Main processing method that automatically chooses the best extraction approach.

**Parameters:**
- `pdf_file`: File-like object containing PDF data
- `filename` (str): Filename for logging and tracking

**Returns:**
- `Tuple[str, str, str]`: (extracted_text, extraction_method, confidence_level)

**Extraction Methods:**
- `"text"`: Direct text extraction from PDF
- `"ocr"`: OCR-based extraction from image conversion
- `"text_fallback"`: Text extraction with OCR enhancement

**Confidence Levels:**
- `"high"`: High-quality extraction with structured fields
- `"medium"`: Moderate quality with some recognizable patterns
- `"low"`: Poor quality, may require manual review

**Example:**
```python
processor = PDFProcessor()
processor.min_text_threshold = 150  # Custom threshold

with open('document.pdf', 'rb') as pdf_file:
    text, method, confidence = processor.process_pdf(pdf_file, 'document.pdf')
    
    if confidence == 'high':
        print("High-quality extraction achieved")
    elif method == 'ocr':
        print("OCR processing was required")
```

### BOLDataExtractor Class

Pattern-based data extraction engine with configurable field patterns.

#### Class Definition

```python
class BOLDataExtractor:
    """
    Configurable data extraction engine using regex patterns.
    
    Extracts structured BOL data from text using predefined patterns
    with support for multiple BOL formats and layouts.
    """
    
    def __init__(self):
        """Initialize extractor with pattern configurations."""
        
    def extract_field(self, text: str, field_type: str) -> str:
        """Extract a specific field using configured patterns."""
        
    def extract_all_fields(self, text: str, tables: List[pd.DataFrame], 
                          filename: str) -> BOLData:
        """Extract all BOL fields from text and table data."""
        
    def clean_field_data(self, data: str) -> str:
        """Clean and normalize extracted field data."""
```

#### Field Extraction Methods

##### Individual Field Extractors

```python
def extract_bol_number(self, text: str) -> str:
    """Extract Bill of Lading number."""
    
def extract_parties(self, text: str) -> Tuple[str, str, str, str, str, str]:
    """Extract shipper, consignee, and notify party information."""
    
def extract_vessel_info(self, text: str) -> Tuple[str, str]:
    """Extract vessel name and voyage number."""
    
def extract_ports(self, text: str) -> Tuple[str, str]:
    """Extract port of loading and discharge."""
    
def extract_dates(self, text: str) -> str:
    """Extract date of issue."""
    
def extract_weights_quantities(self, text: str) -> Tuple[str, str, str]:
    """Extract gross weight, net weight, and quantity."""
    
def extract_freight_terms(self, text: str) -> str:
    """Extract freight terms (PREPAID/COLLECT/PAYABLE)."""
```

##### `extract_all_fields(text: str, tables: List[pd.DataFrame], filename: str) -> BOLData`

Comprehensive field extraction with error handling and confidence assessment.

**Parameters:**
- `text` (str): Extracted text from PDF
- `tables` (List[pd.DataFrame]): Extracted table data
- `filename` (str): Source filename for tracking

**Returns:**
- `BOLData`: Complete structured data object

**Example:**
```python
extractor = BOLDataExtractor()
tables = []  # Assume no table data

# Extract all fields
bol_data = extractor.extract_all_fields(text_content, tables, "sample.pdf")

# Check extraction results
if bol_data.bol_number:
    print(f"BOL Number found: {bol_data.bol_number}")
if bol_data.extraction_failed:
    print(f"Extraction failed: {bol_data.processing_notes}")
```

### FieldPatterns Class

Configurable pattern management system for flexible field extraction.

#### Class Definition

```python
class FieldPatterns:
    """
    Centralized pattern management for BOL field extraction.
    
    Provides configurable regex patterns for different BOL formats
    and supports runtime pattern modification.
    """
    
    def __init__(self):
        """Initialize with default pattern configurations."""
        
    def get_patterns(self, field_type: str) -> List[str]:
        """Get regex patterns for a specific field type."""
        
    def add_pattern(self, field_type: str, pattern: str):
        """Add a new pattern for a field type."""
        
    def remove_pattern(self, field_type: str, pattern: str):
        """Remove a pattern from a field type."""
```

#### Pattern Categories

##### BOL Number Patterns
```python
"bol_number": [
    r"(?:B/L\s*(?:No|Number|#)\.?\s*:?\s*)([A-Z0-9\-]+)",
    r"(?:BOL\s*(?:No|Number|#)\.?\s*:?\s*)([A-Z0-9\-]+)",
    r"(?:Bill\s*of\s*Lading\s*(?:No|Number|#)\.?\s*:?\s*)([A-Z0-9\-]+)",
    r"(?:Document\s*(?:No|Number)\.?\s*:?\s*)([A-Z0-9\-]+)"
]
```

##### Party Information Patterns
```python
"shipper": [
    r"(?:SHIPPER\.?\s*:?\s*)(.*?)(?=\n\s*(?:CONSIGNEE|Consignee|\n\n))",
    r"(?:Shipper\.?\s*:?\s*)(.*?)(?=\n\s*(?:CONSIGNEE|Consignee|\n\n))",
    r"(?:FROM\.?\s*:?\s*)(.*?)(?=\n\s*(?:TO|CONSIGNEE|\n\n))"
]
```

##### Weight and Quantity Patterns
```python
"weight_patterns": [
    r"(?:GROSS\s*WEIGHT\.?\s*:?\s*)([0-9,.\s]+(?:KG|LBS|MT|TON))",
    r"(?:NET\s*WEIGHT\.?\s*:?\s*)([0-9,.\s]+(?:KG|LBS|MT|TON))",
    r"(?:WEIGHT\.?\s*:?\s*)([0-9,.\s]+(?:KG|LBS|MT|TON))"
]
```

#### Pattern Management

```python
# Example: Adding custom patterns
patterns = FieldPatterns()

# Add new BOL number pattern
patterns.add_pattern("bol_number", r"(?:REF\s*NO\.?\s*:?\s*)([A-Z0-9\-]+)")

# Add custom vessel pattern
patterns.add_pattern("vessel", r"(?:SHIP\s*:?\s*)([^\n]+)")

# Get all patterns for a field
bol_patterns = patterns.get_patterns("bol_number")
```

### TableParser Class

Tabular data extraction using tabula-py integration.

#### Class Definition

```python
class TableParser:
    """
    Table extraction and parsing for structured BOL data.
    
    Extracts tabular information such as cargo manifests,
    container details, and line item information.
    """
    
    def extract_tables(self, pdf_file) -> List[pd.DataFrame]:
        """Extract all tables from PDF using tabula-py."""
        
    def parse_cargo_description_table(self, tables: List[pd.DataFrame]) -> str:
        """Parse cargo description from extracted tables."""
```

#### Methods

##### `extract_tables(pdf_file) -> List[pd.DataFrame]`

Extract all tabular data from PDF document.

**Parameters:**
- `pdf_file`: File-like object containing PDF data

**Returns:**
- `List[pd.DataFrame]`: List of extracted tables as pandas DataFrames

**Example:**
```python
table_parser = TableParser()

with open('bol_with_tables.pdf', 'rb') as pdf_file:
    tables = table_parser.extract_tables(pdf_file)
    
    print(f"Found {len(tables)} tables")
    for i, table in enumerate(tables):
        print(f"Table {i}: {table.shape[0]} rows, {table.shape[1]} columns")
        print(table.head())
```

### ExcelExporter Class

Professional export system with multiple format support.

#### Class Definition

```python
class ExcelExporter:
    """
    Professional-grade export system for BOL data.
    
    Generates Excel workbooks with multiple sheets, summary statistics,
    and formatted output for business use.
    """
    
    def __init__(self):
        """Initialize exporter with column configurations."""
        
    def create_dataframe(self, bol_data_list: List[BOLData]) -> pd.DataFrame:
        """Create pandas DataFrame from BOL data list."""
        
    def export_to_excel(self, bol_data_list: List[BOLData], 
                       output_filename: str = None) -> io.BytesIO:
        """Export BOL data to Excel format."""
        
    def export_to_csv(self, bol_data_list: List[BOLData]) -> io.StringIO:
        """Export BOL data to CSV format."""
```

#### Export Methods

##### `export_to_excel(bol_data_list: List[BOLData], output_filename: str = None) -> io.BytesIO`

Generate Excel workbook with multiple sheets and summary statistics.

**Parameters:**
- `bol_data_list` (List[BOLData]): List of extracted BOL data
- `output_filename` (str, optional): Custom filename for the export

**Returns:**
- `io.BytesIO`: Excel file as binary stream

**Excel Structure:**
- `BOL_Data` sheet: Complete extraction results
- `Processing_Summary` sheet: Statistics and metrics

**Example:**
```python
exporter = ExcelExporter()

# Export to Excel
excel_buffer = exporter.export_to_excel(bol_data_list)

# Save to file
with open('bol_results.xlsx', 'wb') as f:
    f.write(excel_buffer.getvalue())

# Or serve via web response
return send_file(
    excel_buffer,
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    as_attachment=True,
    attachment_filename='bol_extraction_results.xlsx'
)
```

## Configuration Reference

### Application Configuration

#### Environment Variables

```bash
# Processing Configuration
BOL_OCR_MIN_TEXT_THRESHOLD=100
BOL_OCR_MAX_BATCH_SIZE=100
BOL_OCR_PROCESSING_TIMEOUT=300
BOL_OCR_OCR_ENABLED=true

# Performance Configuration  
BOL_OCR_MAX_WORKERS=4
BOL_OCR_MEMORY_LIMIT=2048
BOL_OCR_CACHE_TTL=3600

# Security Configuration
BOL_OCR_MAX_FILE_SIZE=50MB
BOL_OCR_ALLOWED_EXTENSIONS=pdf
BOL_OCR_SECURE_MODE=true

# Logging Configuration
BOL_OCR_LOG_LEVEL=INFO
BOL_OCR_LOG_FORMAT=json
BOL_OCR_AUDIT_ENABLED=true
```

#### Configuration File Format

```yaml
# config.yaml
processing:
  min_text_threshold: 100
  max_batch_size: 100
  ocr_enabled: true
  processing_timeout: 300
  
patterns:
  custom_bol_patterns:
    - "(?:Reference\s*:?\s*)([A-Z0-9\-]+)"
    - "(?:Doc\s*ID\s*:?\s*)([A-Z0-9\-]+)"
  
export:
  default_format: "excel"
  include_metadata: true
  column_order: ["filename", "bol_number", "shipper_name"]
  
security:
  max_file_size: "50MB"
  scan_uploads: true
  encryption_at_rest: true
```

### Runtime Configuration

```python
# Runtime configuration example
from app import BOLOCRApp, PDFProcessor, FieldPatterns

# Configure processing thresholds
app = BOLOCRApp()
app.pdf_processor.min_text_threshold = 150
app.pdf_processor.max_page_limit = 100

# Add custom field patterns
custom_patterns = FieldPatterns()
custom_patterns.add_pattern("bol_number", r"(?:REF\s*:?\s*)([A-Z0-9\-]+)")
app.data_extractor.patterns = custom_patterns

# Configure export format
app.excel_exporter.column_order = [
    'filename', 'bol_number', 'shipper_name', 
    'consignee_name', 'extraction_confidence'
]
```

## Integration Patterns

### Direct Class Integration

```python
from app import PDFProcessor, BOLDataExtractor, ExcelExporter

class CustomBOLProcessor:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.data_extractor = BOLDataExtractor()
        self.exporter = ExcelExporter()
    
    def process_document(self, pdf_path: str) -> dict:
        """Custom processing workflow"""
        with open(pdf_path, 'rb') as pdf_file:
            # Extract text
            text, method, confidence = self.pdf_processor.process_pdf(
                pdf_file, pdf_path
            )
            
            # Extract data
            bol_data = self.data_extractor.extract_all_fields(
                text, [], pdf_path
            )
            
            # Return structured result
            return {
                'success': not bol_data.extraction_failed,
                'data': bol_data,
                'metadata': {
                    'extraction_method': method,
                    'confidence': confidence
                }
            }
```

### REST API Integration

```python
from flask import Flask, request, send_file
from app import BOLOCRApp

app = Flask(__name__)
bol_processor = BOLOCRApp()

@app.route('/api/v1/extract', methods=['POST'])
def extract_bol():
    """Extract BOL data from uploaded PDF"""
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    try:
        # Process the file
        result = bol_processor.process_single_pdf(file, file.filename)
        
        # Return structured response
        return {
            'success': not result.extraction_failed,
            'data': {
                'bol_number': result.bol_number,
                'shipper_name': result.shipper_name,
                'consignee_name': result.consignee_name,
                'vessel_name': result.vessel_name,
                'extraction_method': result.extraction_method,
                'confidence': result.extraction_confidence
            },
            'metadata': {
                'filename': result.filename,
                'processing_notes': result.processing_notes
            }
        }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/v1/batch', methods=['POST'])
def batch_extract():
    """Batch process multiple BOL files"""
    files = request.files.getlist('files')
    if not files:
        return {'error': 'No files provided'}, 400
    
    try:
        # Prepare file list
        file_list = [(f, f.filename) for f in files]
        
        # Process batch
        results = bol_processor.process_batch_pdfs(file_list)
        
        # Generate Excel export
        excel_buffer = bol_processor.excel_exporter.export_to_excel(results)
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            attachment_filename='batch_results.xlsx'
        )
    except Exception as e:
        return {'error': str(e)}, 500
```

### Webhook Integration

```python
import requests
from app import BOLOCRApp

class WebhookBOLProcessor(BOLOCRApp):
    def __init__(self, webhook_url: str):
        super().__init__()
        self.webhook_url = webhook_url
    
    def process_single_pdf(self, pdf_file, filename: str):
        """Process with webhook notifications"""
        # Send processing started notification
        self._send_webhook({
            'event': 'processing.started',
            'filename': filename,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            # Process the file
            result = super().process_single_pdf(pdf_file, filename)
            
            # Send completion notification
            self._send_webhook({
                'event': 'processing.completed',
                'filename': filename,
                'success': not result.extraction_failed,
                'bol_number': result.bol_number,
                'confidence': result.extraction_confidence,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            # Send error notification
            self._send_webhook({
                'event': 'processing.failed',
                'filename': filename,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            raise
    
    def _send_webhook(self, payload: dict):
        """Send webhook notification"""
        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            # Log webhook failure but don't interrupt processing
            print(f"Webhook notification failed: {e}")
```

## Error Handling

### Exception Hierarchy

```python
class BOLOCRException(Exception):
    """Base exception for BOL OCR processing"""
    pass

class PDFProcessingError(BOLOCRException):
    """PDF processing related errors"""
    pass

class ExtractionError(BOLOCRException):
    """Data extraction related errors"""
    pass

class ValidationError(BOLOCRException):
    """Data validation related errors"""
    pass

class ExportError(BOLOCRException):
    """Export generation related errors"""
    pass
```

### Error Response Format

```python
{
    "success": false,
    "error": {
        "type": "PDFProcessingError",
        "message": "Unable to extract text from PDF",
        "details": {
            "filename": "problematic_file.pdf",
            "stage": "text_extraction",
            "suggestion": "File may be corrupted or password protected"
        },
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_123456789"
    }
}
```

### Error Handling Patterns

```python
def safe_process_pdf(pdf_file, filename: str) -> dict:
    """Process PDF with comprehensive error handling"""
    try:
        app = BOLOCRApp()
        result = app.process_single_pdf(pdf_file, filename)
        
        return {
            'success': True,
            'data': result,
            'warnings': _get_processing_warnings(result)
        }
        
    except PDFProcessingError as e:
        return {
            'success': False,
            'error': {
                'type': 'PDFProcessingError',
                'message': str(e),
                'recoverable': True,
                'suggestion': 'Try converting to a different PDF format'
            }
        }
        
    except ExtractionError as e:
        return {
            'success': False,
            'error': {
                'type': 'ExtractionError',
                'message': str(e),
                'recoverable': True,
                'suggestion': 'Manual review may be required for this document'
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': {
                'type': 'UnexpectedError',
                'message': 'An unexpected error occurred',
                'recoverable': False,
                'details': str(e) if DEBUG else None
            }
        }
```

## Performance Considerations

### Memory Management

```python
import psutil
import gc
from contextlib import contextmanager

@contextmanager
def memory_monitor(threshold_mb: int = 1000):
    """Monitor memory usage during processing"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024
    
    try:
        yield
    finally:
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        if memory_increase > threshold_mb:
            print(f"Warning: Memory increase of {memory_increase:.1f}MB detected")
            gc.collect()  # Force garbage collection

# Usage
with memory_monitor(500):
    results = app.process_batch_pdfs(large_file_list)
```

### Batch Processing Optimization

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

class OptimizedBOLProcessor(BOLOCRApp):
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.max_workers = max_workers
    
    def process_batch_parallel(self, files: List[Tuple[Any, str]]) -> List[BOLData]:
        """Process files in parallel with controlled concurrency"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_file = {
                executor.submit(self._safe_process_single, pdf_file, filename): filename
                for pdf_file, filename in files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = BOLData()
                    error_result.filename = filename
                    error_result.extraction_failed = True
                    error_result.processing_notes = f"Processing error: {str(e)}"
                    results.append(error_result)
        
        return results
    
    def _safe_process_single(self, pdf_file, filename: str) -> BOLData:
        """Thread-safe single file processing"""
        try:
            return self.process_single_pdf(pdf_file, filename)
        except Exception as e:
            error_result = BOLData()
            error_result.filename = filename
            error_result.extraction_failed = True
            error_result.processing_notes = str(e)
            return error_result
```

### Caching Implementation

```python
import redis
import pickle
import hashlib
from functools import wraps

class CachedBOLProcessor(BOLOCRApp):
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        super().__init__()
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.cache_ttl = 3600  # 1 hour
    
    def _get_file_hash(self, pdf_file) -> str:
        """Generate hash for PDF file content"""
        pdf_file.seek(0)
        content = pdf_file.read()
        pdf_file.seek(0)
        return hashlib.md5(content).hexdigest()
    
    def process_single_pdf_cached(self, pdf_file, filename: str) -> BOLData:
        """Process with result caching"""
        # Generate cache key
        file_hash = self._get_file_hash(pdf_file)
        cache_key = f"bol_ocr:{file_hash}"
        
        # Check cache
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return pickle.loads(cached_result)
        
        # Process file
        result = self.process_single_pdf(pdf_file, filename)
        
        # Cache result if successful
        if not result.extraction_failed:
            self.redis_client.setex(
                cache_key, 
                self.cache_ttl, 
                pickle.dumps(result)
            )
        
        return result
```

## Examples

### Complete Integration Example

```python
#!/usr/bin/env python3
"""
Complete BOL OCR integration example demonstrating:
- Custom configuration
- Error handling
- Performance monitoring
- Result validation
"""

import os
import time
import logging
from typing import List, Dict, Any
from app import BOLOCRApp, BOLData, FieldPatterns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnterpriseVOLProcessor:
    """Enterprise-grade BOL processor with full integration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with custom configuration"""
        self.config = config or {}
        self.app = BOLOCRApp()
        self._configure_app()
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'total_processing_time': 0
        }
    
    def _configure_app(self):
        """Apply custom configuration"""
        # Configure PDF processor
        if 'min_text_threshold' in self.config:
            self.app.pdf_processor.min_text_threshold = self.config['min_text_threshold']
        
        # Configure custom patterns
        if 'custom_patterns' in self.config:
            patterns = FieldPatterns()
            for field, pattern_list in self.config['custom_patterns'].items():
                for pattern in pattern_list:
                    patterns.add_pattern(field, pattern)
            self.app.data_extractor.patterns = patterns
        
        # Configure export settings
        if 'export_columns' in self.config:
            self.app.excel_exporter.column_order = self.config['export_columns']
    
    def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Process all PDF files in a directory"""
        pdf_files = []
        
        # Collect PDF files
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                pdf_files.append((file_path, filename))
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Process files
        results = []
        start_time = time.time()
        
        for file_path, filename in pdf_files:
            try:
                with open(file_path, 'rb') as pdf_file:
                    result = self._process_with_validation(pdf_file, filename)
                    results.append(result)
                    
                    # Update statistics
                    self.stats['processed'] += 1
                    if not result.extraction_failed:
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1
                        
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}")
                # Create error result
                error_result = BOLData()
                error_result.filename = filename
                error_result.extraction_failed = True
                error_result.processing_notes = f"File processing error: {str(e)}"
                results.append(error_result)
                self.stats['failed'] += 1
        
        self.stats['total_processing_time'] = time.time() - start_time
        
        # Generate report
        return self._generate_processing_report(results)
    
    def _process_with_validation(self, pdf_file, filename: str) -> BOLData:
        """Process file with additional validation"""
        result = self.app.process_single_pdf(pdf_file, filename)
        
        # Additional validation rules
        validation_errors = []
        
        if not result.bol_number:
            validation_errors.append("Missing BOL number")
        
        if not result.shipper_name:
            validation_errors.append("Missing shipper information")
        
        if not result.consignee_name:
            validation_errors.append("Missing consignee information")
        
        # Update processing notes with validation results
        if validation_errors:
            additional_notes = "Validation warnings: " + "; ".join(validation_errors)
            if result.processing_notes:
                result.processing_notes += f" | {additional_notes}"
            else:
                result.processing_notes = additional_notes
        
        return result
    
    def _generate_processing_report(self, results: List[BOLData]) -> Dict[str, Any]:
        """Generate comprehensive processing report"""
        # Calculate success rate
        success_rate = (self.stats['successful'] / self.stats['processed']) * 100 if self.stats['processed'] > 0 else 0
        
        # Group by extraction method
        method_stats = {}
        confidence_stats = {}
        
        for result in results:
            if not result.extraction_failed:
                method = result.extraction_method
                confidence = result.extraction_confidence
                
                method_stats[method] = method_stats.get(method, 0) + 1
                confidence_stats[confidence] = confidence_stats.get(confidence, 0) + 1
        
        # Generate Excel export
        excel_buffer = self.app.excel_exporter.export_to_excel(results)
        
        return {
            'summary': {
                'total_files': self.stats['processed'],
                'successful_extractions': self.stats['successful'],
                'failed_extractions': self.stats['failed'],
                'success_rate_percent': round(success_rate, 2),
                'total_processing_time_seconds': round(self.stats['total_processing_time'], 2),
                'average_time_per_file': round(self.stats['total_processing_time'] / self.stats['processed'], 2) if self.stats['processed'] > 0 else 0
            },
            'extraction_methods': method_stats,
            'confidence_distribution': confidence_stats,
            'failed_files': [r.filename for r in results if r.extraction_failed],
            'results': results,
            'excel_export': excel_buffer
        }

# Usage example
if __name__ == "__main__":
    # Custom configuration
    config = {
        'min_text_threshold': 150,
        'custom_patterns': {
            'bol_number': [
                r"(?:Reference\s*No\.?\s*:?\s*)([A-Z0-9\-]+)",
                r"(?:Document\s*ID\s*:?\s*)([A-Z0-9\-]+)"
            ]
        },
        'export_columns': [
            'filename', 'bol_number', 'shipper_name', 'consignee_name',
            'vessel_name', 'extraction_method', 'extraction_confidence'
        ]
    }
    
    # Initialize processor
    processor = EnterpriseBOLProcessor(config)
    
    # Process directory
    report = processor.process_directory('/path/to/bol/files')
    
    # Print summary
    print("Processing Summary:")
    print(f"Total files: {report['summary']['total_files']}")
    print(f"Success rate: {report['summary']['success_rate_percent']}%")
    print(f"Processing time: {report['summary']['total_processing_time_seconds']}s")
    
    # Save results
    with open('processing_results.xlsx', 'wb') as f:
        f.write(report['excel_export'].getvalue())
    
    print("Results exported to processing_results.xlsx")
```

This comprehensive API reference provides developers with all the information needed to integrate the BOL OCR Extractor into their applications, whether using direct class integration, REST APIs, or custom processing workflows.