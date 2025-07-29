# BOL OCR Extractor - Comprehensive QA Testing Strategy

## Executive Summary

This document outlines a comprehensive testing strategy for the BOL OCR Extractor application, designed to ensure production-level quality, reliability, and performance. The strategy covers unit testing, integration testing, performance testing, and quality assurance protocols for the OCR-based data extraction system.

## Table of Contents

1. [Test Strategy Overview](#test-strategy-overview)
2. [Test Framework Architecture](#test-framework-architecture)
3. [Unit Testing Plan](#unit-testing-plan)
4. [Integration Testing Plan](#integration-testing-plan)
5. [Performance Testing Plan](#performance-testing-plan)
6. [Synthetic Test Data Creation](#synthetic-test-data-creation)
7. [Quality Metrics and Success Criteria](#quality-metrics-and-success-criteria)
8. [Test Coverage Analysis](#test-coverage-analysis)
9. [Implementation Roadmap](#implementation-roadmap)

## Test Strategy Overview

### Testing Objectives

1. **Functional Validation**: Ensure all core functionality works as specified
2. **Accuracy Verification**: Validate extraction accuracy across different BOL formats
3. **Performance Assurance**: Confirm application meets performance benchmarks
4. **Error Handling**: Verify robust error handling and recovery mechanisms
5. **Scalability Testing**: Ensure system can handle production workloads
6. **Cross-Platform Compatibility**: Validate operation across different environments

### Testing Pyramid

```
        /\        End-to-End Tests (10%)
       /  \       - Full workflow testing
      /    \      - User acceptance scenarios
     /      \     
    /--------\    Integration Tests (20%)
   /          \   - Component interactions
  /            \  - API integration testing
 /              \ 
/--------------\ Unit Tests (70%)
                 - Individual class testing
                 - Method-level validation
                 - Mock-based testing
```

### Risk Assessment

**High Risk Areas:**
- OCR accuracy and text extraction quality
- PDF parsing with various formats and quality levels
- Memory management during batch processing
- Regex pattern matching across different BOL layouts

**Medium Risk Areas:**
- Table extraction reliability
- File upload and handling
- Export functionality (Excel/CSV)
- Configuration management

**Low Risk Areas:**
- User interface components
- Basic data structure operations
- Static content rendering

## Test Framework Architecture

### Technology Stack

```python
# Core Testing Framework
pytest>=7.4.0           # Test runner and framework
pytest-cov>=4.1.0       # Coverage reporting
pytest-xdist>=3.3.0     # Parallel test execution
pytest-mock>=3.11.0     # Mocking utilities

# Performance Testing
pytest-benchmark>=4.0.0  # Performance benchmarking
memory-profiler>=0.61.0  # Memory usage analysis
psutil>=5.9.0            # System resource monitoring

# Test Data Generation
fpdf2>=2.7.0            # PDF generation for test data
reportlab>=4.0.0        # Advanced PDF creation
Pillow>=10.0.0          # Image manipulation for OCR tests

# Fixtures and Utilities
factory-boy>=3.2.0      # Test data factories
freezegun>=1.2.0        # Time mocking
responses>=0.23.0       # HTTP request mocking
```

### Project Structure

```
tests/
├── conftest.py                 # Global fixtures and configuration
├── unit/                       # Unit tests
│   ├── test_pdf_processor.py   # PDFProcessor class tests
│   ├── test_bol_extractor.py   # BOLDataExtractor tests
│   ├── test_field_patterns.py  # FieldPatterns tests
│   ├── test_table_parser.py    # TableParser tests
│   └── test_excel_exporter.py  # ExcelExporter tests
├── integration/                # Integration tests
│   ├── test_end_to_end.py      # Full workflow tests
│   ├── test_batch_processing.py # Batch processing tests
│   └── test_file_handling.py   # File I/O tests
├── performance/                # Performance tests
│   ├── test_extraction_speed.py # Processing speed tests
│   ├── test_memory_usage.py    # Memory consumption tests
│   └── test_batch_scalability.py # Scalability tests
├── fixtures/                   # Test data and fixtures
│   ├── sample_pdfs/           # Sample BOL PDFs
│   ├── synthetic_bols/        # Generated test BOLs
│   └── expected_results/      # Ground truth data
└── utils/                     # Testing utilities
    ├── pdf_generator.py       # Synthetic PDF creation
    ├── test_helpers.py        # Common test utilities
    └── mock_factories.py      # Mock object factories
```

## Unit Testing Plan

### Core Classes to Test

#### 1. PDFProcessor Tests

```python
# tests/unit/test_pdf_processor.py

import pytest
from unittest.mock import Mock, patch, MagicMock
from app import PDFProcessor, BOLData
import io
import tempfile

class TestPDFProcessor:
    
    @pytest.fixture
    def pdf_processor(self):
        return PDFProcessor()
    
    @pytest.fixture
    def mock_pdf_file(self):
        """Create mock PDF file for testing"""
        mock_file = Mock()
        mock_file.name = "test_bol.pdf"
        return mock_file
    
    def test_extract_text_pdfplumber_success(self, pdf_processor, mock_pdf_file):
        """Test successful text extraction from PDF"""
        with patch('pdfplumber.open') as mock_open:
            # Mock PDF with extractable text
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = "Sample BOL text content " * 20  # >100 chars
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            text, success = pdf_processor.extract_text_pdfplumber(mock_pdf_file)
            
            assert success is True
            assert len(text) >= pdf_processor.min_text_threshold
            assert "Sample BOL text content" in text
    
    def test_extract_text_pdfplumber_insufficient_text(self, pdf_processor, mock_pdf_file):
        """Test handling of PDFs with insufficient text"""
        with patch('pdfplumber.open') as mock_open:
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = "Short"  # <100 chars
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            text, success = pdf_processor.extract_text_pdfplumber(mock_pdf_file)
            
            assert success is False
            assert len(text) < pdf_processor.min_text_threshold
    
    def test_extract_text_ocr_success(self, pdf_processor, mock_pdf_file):
        """Test OCR text extraction"""
        with patch('pdfplumber.open') as mock_open, \
             patch('pytesseract.image_to_string') as mock_ocr:
            # Mock PDF to image conversion
            mock_pdf = Mock()
            mock_page = Mock()
            mock_image = Mock()
            mock_image.original = Mock()  # PIL Image mock
            mock_page.to_image.return_value = mock_image
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            # Mock OCR result
            mock_ocr.return_value = "OCR extracted BOL content " * 10  # >100 chars
            
            text, success = pdf_processor.extract_text_ocr(mock_pdf_file)
            
            assert success is True
            assert "OCR extracted BOL content" in text
            mock_ocr.assert_called_once()
    
    def test_assess_text_quality_high(self, pdf_processor):
        """Test text quality assessment - high quality"""
        text = """
        SHIPPER: Test Company
        123 Main Street
        CONSIGNEE: Destination Corp
        456 Oak Avenue
        VESSEL: Test Ship
        B/L NUMBER: TST123456
        """
        quality = pdf_processor.assess_text_quality(text)
        assert quality == "high"
    
    def test_assess_text_quality_medium(self, pdf_processor):
        """Test text quality assessment - medium quality"""
        text = "SHIPPER: Some company with basic structure"
        quality = pdf_processor.assess_text_quality(text)
        assert quality == "medium"
    
    def test_assess_text_quality_low(self, pdf_processor):
        """Test text quality assessment - low quality"""
        text = "Short text"
        quality = pdf_processor.assess_text_quality(text)
        assert quality == "low"
    
    def test_process_pdf_text_fallback_to_ocr(self, pdf_processor, mock_pdf_file):
        """Test automatic fallback from text to OCR"""
        with patch.object(pdf_processor, 'extract_text_pdfplumber') as mock_text, \
             patch.object(pdf_processor, 'extract_text_ocr') as mock_ocr, \
             patch.object(pdf_processor, 'assess_text_quality') as mock_quality:
            
            # Text extraction returns insufficient content
            mock_text.return_value = ("Short", False)
            mock_ocr.return_value = ("Long OCR content " * 20, True)
            mock_quality.side_effect = ["low", "high"]  # First call low, second call high
            
            text, method, confidence = pdf_processor.process_pdf(mock_pdf_file, "test.pdf")
            
            assert method == "ocr"
            assert confidence == "high"
            assert "Long OCR content" in text
            mock_text.assert_called_once()
            mock_ocr.assert_called_once()
```

#### 2. BOLDataExtractor Tests

```python
# tests/unit/test_bol_extractor.py

import pytest
from app import BOLDataExtractor, FieldPatterns, BOLData

class TestBOLDataExtractor:
    
    @pytest.fixture
    def extractor(self):
        return BOLDataExtractor()
    
    @pytest.fixture
    def sample_bol_text(self):
        return """
        B/L NUMBER: BOL123456789
        
        SHIPPER:
        ABC Shipping Company
        123 Export Lane
        Los Angeles, CA 90001
        
        CONSIGNEE:
        XYZ Import Corp
        456 Harbor Blvd
        New York, NY 10001
        
        NOTIFY PARTY:
        Maritime Logistics Inc
        789 Dock Street
        Boston, MA 02101
        
        VESSEL: MV Ocean Carrier
        VOYAGE: VOY2024001
        
        PORT OF LOADING: Los Angeles, CA
        PORT OF DISCHARGE: New York, NY
        
        FREIGHT: PREPAID
        
        GROSS WEIGHT: 2,500 KG
        NET WEIGHT: 2,200 KG
        PACKAGES: 100 CTNS
        
        DATE: 15/03/2024
        """
    
    def test_extract_bol_number(self, extractor, sample_bol_text):
        """Test BOL number extraction"""
        result = extractor.extract_bol_number(sample_bol_text)
        assert result == "BOL123456789"
    
    def test_extract_parties(self, extractor, sample_bol_text):
        """Test extraction of shipper, consignee, and notify party"""
        shipper_name, shipper_address, consignee_name, consignee_address, notify_name, notify_address = extractor.extract_parties(sample_bol_text)
        
        assert shipper_name == "ABC Shipping Company"
        assert "123 Export Lane" in shipper_address
        assert consignee_name == "XYZ Import Corp"
        assert "456 Harbor Blvd" in consignee_address
        assert notify_name == "Maritime Logistics Inc"
        assert "789 Dock Street" in notify_address
    
    def test_extract_vessel_info(self, extractor, sample_bol_text):
        """Test vessel and voyage extraction"""
        vessel, voyage = extractor.extract_vessel_info(sample_bol_text)
        assert vessel == "MV Ocean Carrier"
        assert voyage == "VOY2024001"
    
    def test_extract_ports(self, extractor, sample_bol_text):
        """Test port extraction"""
        port_load, port_discharge = extractor.extract_ports(sample_bol_text)
        assert port_load == "Los Angeles, CA"
        assert port_discharge == "New York, NY"
    
    def test_extract_weights_quantities(self, extractor, sample_bol_text):
        """Test weight and quantity extraction"""
        gross_weight, net_weight, quantity = extractor.extract_weights_quantities(sample_bol_text)
        assert gross_weight == "2,500 KG"
        assert net_weight == "2,200 KG"
        assert quantity == "100 CTNS"
    
    def test_extract_freight_terms(self, extractor, sample_bol_text):
        """Test freight terms extraction"""
        result = extractor.extract_freight_terms(sample_bol_text)
        assert result == "PREPAID"
    
    def test_extract_dates(self, extractor, sample_bol_text):
        """Test date extraction"""
        result = extractor.extract_dates(sample_bol_text)
        assert result == "15/03/2024"
    
    def test_extract_all_fields_complete(self, extractor, sample_bol_text):
        """Test complete field extraction"""
        bol_data = extractor.extract_all_fields(sample_bol_text, [], "test.pdf")
        
        assert bol_data.filename == "test.pdf"
        assert bol_data.bol_number == "BOL123456789"
        assert bol_data.shipper_name == "ABC Shipping Company"
        assert bol_data.consignee_name == "XYZ Import Corp"
        assert bol_data.vessel_name == "MV Ocean Carrier"
        assert bol_data.freight_terms == "PREPAID"
        assert not bol_data.extraction_failed
    
    def test_clean_field_data(self, extractor):
        """Test field data cleaning"""
        dirty_data = "  : - Test Data - :  "
        cleaned = extractor.clean_field_data(dirty_data)
        assert cleaned == "Test Data"
    
    def test_extract_field_no_match(self, extractor):
        """Test extraction when no patterns match"""
        text = "This text has no BOL patterns"
        result = extractor.extract_field(text, "bol_number")
        assert result == ""
    
    # Edge case tests
    def test_extract_multiple_bol_numbers(self, extractor):
        """Test handling of multiple BOL numbers (should return first)"""
        text = "B/L NO: BOL001 and also BOL NO: BOL002"
        result = extractor.extract_bol_number(text)
        assert result == "BOL001"
    
    def test_extract_case_insensitive(self, extractor):
        """Test case-insensitive pattern matching"""
        text = "b/l number: bol123456"
        result = extractor.extract_bol_number(text)
        assert result == "bol123456"
```

#### 3. FieldPatterns Tests

```python
# tests/unit/test_field_patterns.py

import pytest
import re
from app import FieldPatterns

class TestFieldPatterns:
    
    @pytest.fixture
    def patterns(self):
        return FieldPatterns()
    
    def test_get_bol_number_patterns(self, patterns):
        """Test BOL number pattern retrieval"""
        bol_patterns = patterns.get_patterns("bol_number")
        assert len(bol_patterns) > 0
        assert any("B/L" in pattern for pattern in bol_patterns)
        assert any("BOL" in pattern for pattern in bol_patterns)
    
    def test_get_nonexistent_pattern(self, patterns):
        """Test retrieval of non-existent pattern type"""
        result = patterns.get_patterns("nonexistent_field")
        assert result == []
    
    def test_bol_number_pattern_matching(self, patterns):
        """Test actual BOL number pattern matching"""
        bol_patterns = patterns.get_patterns("bol_number")
        test_cases = [
            ("B/L No: BOL123456", "BOL123456"),
            ("BOL NUMBER: TEST-001", "TEST-001"),
            ("Bill of Lading #: ABC123", "ABC123"),
            ("Document No: DOC789", "DOC789")
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in bol_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    assert match.group(1) == expected
                    matched = True
                    break
            assert matched, f"No pattern matched for text: {text}"
    
    def test_shipper_pattern_matching(self, patterns):
        """Test shipper pattern matching"""
        shipper_patterns = patterns.get_patterns("shipper")
        text = """
        SHIPPER:
        Test Company Inc
        123 Main Street
        CONSIGNEE:
        Other Company
        """
        
        matched = False
        for pattern in shipper_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                result = match.group(1).strip()
                assert "Test Company Inc" in result  
                assert "123 Main Street" in result
                matched = True
                break
        assert matched
    
    def test_date_pattern_matching(self, patterns):
        """Test date pattern matching"""
        date_patterns = patterns.get_patterns("date_patterns")
        test_cases = [
            "Date: 15/03/2024",
            "Issue Date: Mar 15, 2024", 
            "15 March 2024",
            "March 15, 2024"
        ]
        
        for text in test_cases:
            matched = False
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    matched = True
                    break
            assert matched, f"No date pattern matched for: {text}"
```

#### 4. TableParser Tests

```python
# tests/unit/test_table_parser.py

import pytest
from unittest.mock import Mock, patch
import pandas as pd
from app import TableParser

class TestTableParser:
    
    @pytest.fixture
    def table_parser(self):
        return TableParser()
    
    @pytest.fixture
    def mock_cargo_table(self):
        """Create mock table with cargo description"""
        return pd.DataFrame({
            'Description of Goods': ['Steel Pipes', 'Construction Materials'],
            'Quantity': ['100 PCS', '50 TONS'],
            'Weight': ['5000 KG', '2000 KG']
        })
    
    @pytest.fixture
    def mock_pdf_file(self):
        return Mock()
    
    def test_extract_tables_success(self, table_parser, mock_pdf_file, mock_cargo_table):
        """Test successful table extraction"""
        with patch('tabula.read_pdf') as mock_read_pdf:
            mock_read_pdf.return_value = [mock_cargo_table]
            
            tables = table_parser.extract_tables(mock_pdf_file)
            
            assert len(tables) == 1
            assert isinstance(tables[0], pd.DataFrame)
            mock_read_pdf.assert_called_once_with(mock_pdf_file, pages='all', multiple_tables=True)
    
    def test_extract_tables_no_tables(self, table_parser, mock_pdf_file):
        """Test handling when no tables found"""
        with patch('tabula.read_pdf') as mock_read_pdf:
            mock_read_pdf.return_value = []
            
            tables = table_parser.extract_tables(mock_pdf_file)
            
            assert tables == []
    
    def test_extract_tables_error(self, table_parser, mock_pdf_file):
        """Test error handling in table extraction"""
        with patch('tabula.read_pdf') as mock_read_pdf:
            mock_read_pdf.side_effect = Exception("Table extraction failed")
            
            tables = table_parser.extract_tables(mock_pdf_file)
            
            assert tables == []
    
    def test_parse_cargo_description_table(self, table_parser, mock_cargo_table):
        """Test cargo description parsing from table"""
        result = table_parser.parse_cargo_description_table([mock_cargo_table])
        
        assert "Steel Pipes" in result
        assert "Construction Materials" in result
        assert ";" in result  # Multiple descriptions joined
    
    def test_parse_cargo_description_multiple_tables(self, table_parser):
        """Test parsing cargo descriptions from multiple tables"""
        table1 = pd.DataFrame({
            'DESCRIPTION': ['Item A', 'Item B']
        })
        table2 = pd.DataFrame({
            'GOODS': ['Item C', 'Item D']
        })
        
        result = table_parser.parse_cargo_description_table([table1, table2])
        
        assert "Item A" in result
        assert "Item B" in result  
        assert "Item C" in result
        assert "Item D" in result
    
    def test_parse_cargo_description_no_description_columns(self, table_parser):
        """Test handling when no description columns found"""
        table = pd.DataFrame({
            'Weight': ['100 KG', '200 KG'],
            'Quantity': ['10', '20']
        })
        
        result = table_parser.parse_cargo_description_table([table])
        
        assert result == ""
```

#### 5. ExcelExporter Tests

```python
# tests/unit/test_excel_exporter.py

import pytest
import pandas as pd
import io
from app import ExcelExporter, BOLData

class TestExcelExporter:
    
    @pytest.fixture
    def exporter(self):
        return ExcelExporter()
    
    @pytest.fixture
    def sample_bol_data(self):
        """Create sample BOL data for testing"""
        bol1 = BOLData()
        bol1.filename = "test1.pdf"
        bol1.bol_number = "BOL001"
        bol1.shipper_name = "Shipper A"
        bol1.consignee_name = "Consignee A"
        bol1.extraction_method = "text"
        bol1.extraction_confidence = "high"
        
        bol2 = BOLData()
        bol2.filename = "test2.pdf"
        bol2.bol_number = "BOL002"
        bol2.shipper_name = "Shipper B"
        bol2.consignee_name = "Consignee B"
        bol2.extraction_method = "ocr"
        bol2.extraction_confidence = "medium"
        bol2.extraction_failed = True
        
        return [bol1, bol2]
    
    def test_create_dataframe(self, exporter, sample_bol_data):
        """Test DataFrame creation from BOL data"""
        df = exporter.create_dataframe(sample_bol_data)
        
        assert len(df) == 2
        assert list(df.columns) == exporter.column_order
        assert df.iloc[0]['bol_number'] == "BOL001"
        assert df.iloc[1]['bol_number'] == "BOL002"
        assert df.iloc[0]['extraction_failed'] is False
        assert df.iloc[1]['extraction_failed'] is True
    
    def test_export_to_excel(self, exporter, sample_bol_data):
        """Test Excel export functionality"""
        excel_buffer = exporter.export_to_excel(sample_bol_data)
        
        assert isinstance(excel_buffer, io.BytesIO)
        assert excel_buffer.tell() > 0  # Buffer has content
        
        # Test that we can read the Excel file
        excel_buffer.seek(0)
        df_main = pd.read_excel(excel_buffer, sheet_name='BOL_Data')
        df_summary = pd.read_excel(excel_buffer, sheet_name='Processing_Summary')
        
        assert len(df_main) == 2
        assert 'Metric' in df_summary.columns
        assert 'Count' in df_summary.columns
    
    def test_export_to_csv(self, exporter, sample_bol_data):
        """Test CSV export functionality"""
        csv_buffer = exporter.export_to_csv(sample_bol_data)
        
        assert isinstance(csv_buffer, io.StringIO)
        csv_content = csv_buffer.getvalue()
        assert len(csv_content) > 0
        assert "BOL001" in csv_content
        assert "BOL002" in csv_content
    
    def test_column_order_consistency(self, exporter):
        """Test that column order is consistent"""
        expected_columns = [
            'filename', 'bol_number', 'shipper_name', 'shipper_address',
            'consignee_name', 'consignee_address', 'notify_party_name', 'notify_party_address',
            'vessel_name', 'voyage_number', 'port_of_load', 'port_of_discharge',
            'description_of_goods', 'quantity_packages', 'gross_weight', 'net_weight',
            'freight_terms', 'date_of_issue', 'extraction_method', 'extraction_confidence',
            'processing_notes', 'extraction_failed'
        ]
        
        assert exporter.column_order == expected_columns
    
    def test_summary_statistics(self, exporter, sample_bol_data):
        """Test summary statistics calculation"""
        excel_buffer = exporter.export_to_excel(sample_bol_data)
        excel_buffer.seek(0)
        df_summary = pd.read_excel(excel_buffer, sheet_name='Processing_Summary')
        
        # Find specific metrics
        metrics = dict(zip(df_summary['Metric'], df_summary['Count']))
        
        assert metrics['Total PDFs Processed'] == 2
        assert metrics['Successful Extractions'] == 1  # Only one succeeded
        assert metrics['Failed Extractions'] == 1
        assert metrics['Text-based Extractions'] == 1
        assert metrics['OCR-based Extractions'] == 1
        assert metrics['High Confidence'] == 1
        assert metrics['Medium Confidence'] == 1
```

## Integration Testing Plan

### End-to-End Workflow Tests

```python
# tests/integration/test_end_to_end.py

import pytest
import tempfile
import os
from unittest.mock import patch
from app import BOLOCRApp, PDFProcessor, BOLDataExtractor, ExcelExporter
import pandas as pd

class TestEndToEndWorkflow:
    
    @pytest.fixture
    def app(self):
        return BOLOCRApp()
    
    @pytest.fixture
    def sample_pdf_bytes(self):
        """Create sample PDF bytes for testing"""
        # This would be actual PDF bytes in real implementation
        return b"Sample PDF content for testing"
    
    def test_complete_text_extraction_workflow(self, app, sample_pdf_bytes):
        """Test complete workflow for text-based PDF"""
        with patch.object(app.pdf_processor, 'process_pdf') as mock_process, \
             patch.object(app.table_parser, 'extract_tables') as mock_tables, \
             patch.object(app.data_extractor, 'extract_all_fields') as mock_extract:
            
            # Mock successful text extraction
            mock_process.return_value = ("Sample BOL text", "text", "high")
            mock_tables.return_value = []
            
            # Mock BOL data extraction
            from app import BOLData
            mock_bol_data = BOLData()
            mock_bol_data.filename = "test.pdf"
            mock_bol_data.bol_number = "BOL123"
            mock_bol_data.extraction_method = "text"
            mock_bol_data.extraction_confidence = "high"
            mock_extract.return_value = mock_bol_data
            
            # Process single PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(sample_pdf_bytes)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as pdf_file:
                    result = app.process_single_pdf(pdf_file, "test.pdf")
                
                os.unlink(tmp_file.name)
            
            assert result.bol_number == "BOL123"
            assert result.extraction_method == "text"
            assert result.extraction_confidence == "high"
            assert not result.extraction_failed
    
    def test_complete_ocr_fallback_workflow(self, app, sample_pdf_bytes):
        """Test complete workflow with OCR fallback"""
        with patch.object(app.pdf_processor, 'process_pdf') as mock_process, \
             patch.object(app.table_parser, 'extract_tables') as mock_tables, \
             patch.object(app.data_extractor, 'extract_all_fields') as mock_extract:
            
            # Mock OCR extraction (text extraction failed)
            mock_process.return_value = ("OCR extracted text", "ocr", "medium")
            mock_tables.return_value = []
            
            from app import BOLData
            mock_bol_data = BOLData()
            mock_bol_data.filename = "test_scanned.pdf"
            mock_bol_data.bol_number = "SCN456"
            mock_bol_data.extraction_method = "ocr"
            mock_bol_data.extraction_confidence = "medium"
            mock_extract.return_value = mock_bol_data
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(sample_pdf_bytes)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as pdf_file:
                    result = app.process_single_pdf(pdf_file, "test_scanned.pdf")
                
                os.unlink(tmp_file.name)
            
            assert result.bol_number == "SCN456"
            assert result.extraction_method == "ocr"
            assert result.extraction_confidence == "medium"
    
    def test_batch_processing_workflow(self, app):
        """Test batch processing of multiple PDFs"""
        from app import BOLData
        
        # Mock batch processing
        with patch.object(app, 'process_single_pdf') as mock_process:
            mock_results = []
            for i in range(3):
                bol_data = BOLData()
                bol_data.filename = f"test_{i}.pdf"
                bol_data.bol_number = f"BOL{i:03d}"
                mock_results.append(bol_data)
            
            mock_process.side_effect = mock_results
            
            # Simulate file list
            files = [(f"mock_file_{i}", f"test_{i}.pdf") for i in range(3)]
            
            with patch('streamlit.progress') as mock_progress, \
                 patch('streamlit.empty') as mock_empty:
                results = app.process_batch_pdfs(files)
            
            assert len(results) == 3
            assert all(result.bol_number.startswith("BOL") for result in results)
            assert mock_process.call_count == 3
    
    def test_export_integration(self, app):
        """Test integration between extraction and export"""
        from app import BOLData
        
        # Create test data
        bol_data = BOLData()
        bol_data.filename = "integration_test.pdf"
        bol_data.bol_number = "INT001"
        bol_data.shipper_name = "Test Shipper"
        bol_data.consignee_name = "Test Consignee"
        bol_data.extraction_method = "text"
        bol_data.extraction_confidence = "high"
        
        # Test Excel export
        excel_buffer = app.excel_exporter.export_to_excel([bol_data])
        assert excel_buffer.tell() > 0
        
        # Verify exported data
        excel_buffer.seek(0)
        df = pd.read_excel(excel_buffer, sheet_name='BOL_Data')
        assert len(df) == 1
        assert df.iloc[0]['bol_number'] == "INT001"
        assert df.iloc[0]['shipper_name'] == "Test Shipper"
```

### Component Integration Tests

```python
# tests/integration/test_component_integration.py

import pytest
from app import PDFProcessor, BOLDataExtractor, TableParser
from unittest.mock import Mock, patch

class TestComponentIntegration:
    
    def test_pdf_processor_extractor_integration(self):
        """Test integration between PDF processor and data extractor"""
        pdf_processor = PDFProcessor()
        extractor = BOLDataExtractor()
        
        sample_text = """
        B/L NUMBER: TEST123
        SHIPPER: Test Company
        VESSEL: Test Ship
        """
        
        # Mock the PDF processing to return our sample text
        with patch.object(pdf_processor, 'process_pdf') as mock_process:
            mock_process.return_value = (sample_text, "text", "high")
            
            # Process and extract
            text, method, confidence = pdf_processor.process_pdf(Mock(), "test.pdf")
            bol_data = extractor.extract_all_fields(text, [], "test.pdf")
            
            assert bol_data.bol_number == "TEST123"
            assert bol_data.shipper_name == "Test Company"
            assert bol_data.vessel_name == "Test Ship"
            assert bol_data.extraction_method == "text"
            assert bol_data.extraction_confidence == "high"
    
    def test_table_parser_extractor_integration(self):
        """Test integration between table parser and data extractor"""
        import pandas as pd
        
        table_parser = TableParser()
        extractor = BOLDataExtractor()
        
        # Mock table with cargo description
        mock_table = pd.DataFrame({
            'Description of Goods': ['Steel Products', 'Machinery Parts']
        })
        
        with patch.object(table_parser, 'extract_tables') as mock_extract:
            mock_extract.return_value = [mock_table]
            
            tables = table_parser.extract_tables(Mock())
            bol_data = extractor.extract_all_fields("", tables, "test.pdf")
            
            assert "Steel Products" in bol_data.description_of_goods
            assert "Machinery Parts" in bol_data.description_of_goods
```

## Performance Testing Plan

### Speed and Memory Tests

```python
# tests/performance/test_extraction_speed.py

import pytest
import time
import psutil
import os
from app import BOLOCRApp, PDFProcessor, BOLDataExtractor
from unittest.mock import Mock, patch

class TestExtractionPerformance:
    
    @pytest.fixture
    def performance_app(self):
        return BOLOCRApp()
    
    def test_text_extraction_speed(self, performance_app):
        """Test text extraction performance benchmark"""
        # Mock PDF with substantial text content
        large_text = "Sample BOL content " * 1000  # Large text
        
        with patch.object(performance_app.pdf_processor, 'extract_text_pdfplumber') as mock_extract:
            mock_extract.return_value = (large_text, True)
            
            start_time = time.time()
            
            # Process 10 iterations
            for _ in range(10):
                text, success = performance_app.pdf_processor.extract_text_pdfplumber(Mock())
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 10
            
            # Should process text extraction in under 1 second per file
            assert avg_time < 1.0, f"Text extraction too slow: {avg_time:.2f}s"
    
    def test_data_extraction_speed(self, performance_app):
        """Test data extraction performance"""
        sample_text = """
        B/L NUMBER: PERF123456
        SHIPPER: Performance Test Company
        123 Speed Lane
        CONSIGNEE: Quick Processing Corp
        456 Fast Street
        VESSEL: Speed Ship
        VOYAGE: FAST001
        """ * 50  # Multiply to create larger text
        
        start_time = time.time()
        
        # Extract data 100 times
        for i in range(100):
            bol_data = performance_app.data_extractor.extract_all_fields(
                sample_text, [], f"perf_test_{i}.pdf"
            )
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Should extract data in under 0.1 second per file
        assert avg_time < 0.1, f"Data extraction too slow: {avg_time:.3f}s"
    
    @pytest.mark.benchmark
    def test_memory_usage_single_file(self, performance_app):
        """Test memory usage for single file processing"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large text content
        large_text = "Large BOL content with many fields " * 10000
        
        with patch.object(performance_app.pdf_processor, 'process_pdf') as mock_process:
            mock_process.return_value = (large_text, "text", "high")
            
            # Process single large file
            result = performance_app.process_single_pdf(Mock(), "large_test.pdf")
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (< 100MB for single file)
            assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"
    
    def test_batch_processing_performance(self, performance_app):
        """Test batch processing performance and scalability"""
        from app import BOLData
        
        batch_sizes = [10, 50, 100]
        results = {}
        
        for batch_size in batch_sizes:
            # Mock processing for batch
            mock_results = []
            for i in range(batch_size):
                bol_data = BOLData()
                bol_data.filename = f"batch_test_{i}.pdf"
                bol_data.bol_number = f"BATCH{i:03d}"
                mock_results.append(bol_data)
            
            with patch.object(performance_app, 'process_single_pdf') as mock_process, \
                 patch('streamlit.progress') as mock_progress, \
                 patch('streamlit.empty') as mock_empty:
                
                mock_process.side_effect = mock_results
                
                # Create mock file list
                files = [(Mock(), f"batch_test_{i}.pdf") for i in range(batch_size)]
                
                start_time = time.time()
                batch_results = performance_app.process_batch_pdfs(files)
                end_time = time.time()
                
                results[batch_size] = {
                    'total_time': end_time - start_time,
                    'avg_time_per_file': (end_time - start_time) / batch_size,
                    'files_processed': len(batch_results)
                }
        
        # Performance should scale reasonably
        assert results[10]['avg_time_per_file'] <= results[100]['avg_time_per_file'] * 1.5
        print(f"Performance results: {results}")
```

### Stress Testing

```python
# tests/performance/test_batch_scalability.py

import pytest
import threading
import time
from unittest.mock import Mock, patch
from app import BOLOCRApp, BOLData

class TestBatchScalability:
    
    @pytest.fixture
    def stress_app(self):
        return BOLOCRApp()
    
    def test_concurrent_processing_stability(self, stress_app):
        """Test application stability under concurrent load"""
        results = []
        errors = []
        
        def process_batch():
            try:
                # Simulate processing
                with patch.object(stress_app, 'process_single_pdf') as mock_process:
                    bol_data = BOLData()
                    bol_data.filename = "concurrent_test.pdf"
                    bol_data.bol_number = "CONC001"
                    mock_process.return_value = bol_data
                    
                    files = [(Mock(), "concurrent_test.pdf")]
                    with patch('streamlit.progress'), patch('streamlit.empty'):
                        batch_results = stress_app.process_batch_pdfs(files)
                        results.extend(batch_results)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=process_batch)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify results and no errors
        assert len(errors) == 0, f"Concurrent processing errors: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
    
    def test_large_batch_memory_management(self, stress_app):
        """Test memory management with large batches"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate processing 200 files
        large_batch_size = 200
        
        with patch.object(stress_app, 'process_single_pdf') as mock_process:
            # Create mock results
            mock_results = []
            for i in range(large_batch_size):
                bol_data = BOLData()
                bol_data.filename = f"large_batch_{i}.pdf"
                bol_data.bol_number = f"LB{i:04d}"
                # Add some substantial data
                bol_data.shipper_name = f"Large Batch Shipper {i}"
                bol_data.description_of_goods = "Large cargo description " * 100
                mock_results.append(bol_data)
            
            mock_process.side_effect = mock_results
            
            # Create large file list
            files = [(Mock(), f"large_batch_{i}.pdf") for i in range(large_batch_size)]
            
            with patch('streamlit.progress'), patch('streamlit.empty'):
                batch_results = stress_app.process_batch_pdfs(files)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable even for large batches
            assert memory_increase < 500, f"Memory usage too high for large batch: {memory_increase:.1f}MB"
            assert len(batch_results) == large_batch_size
    
    def test_export_performance_large_dataset(self, stress_app):
        """Test export performance with large datasets"""
        from app import BOLData
        
        # Create large dataset
        large_dataset = []
        for i in range(1000):
            bol_data = BOLData()
            bol_data.filename = f"export_test_{i}.pdf"
            bol_data.bol_number = f"EXP{i:04d}"
            bol_data.shipper_name = f"Export Test Shipper {i}"
            bol_data.consignee_name = f"Export Test Consignee {i}"
            bol_data.description_of_goods = "Export test cargo " * 50
            large_dataset.append(bol_data)
        
        # Test Excel export performance
        start_time = time.time()
        excel_buffer = stress_app.excel_exporter.export_to_excel(large_dataset)
        excel_time = time.time() - start_time
        
        # Test CSV export performance
        start_time = time.time()
        csv_buffer = stress_app.excel_exporter.export_to_csv(large_dataset)
        csv_time = time.time() - start_time
        
        # Export should complete within reasonable time
        assert excel_time < 30, f"Excel export too slow: {excel_time:.1f}s"
        assert csv_time < 10, f"CSV export too slow: {csv_time:.1f}s"
        
        # Verify export content
        assert excel_buffer.tell() > 0
        assert len(csv_buffer.getvalue()) > 0
```

## Synthetic Test Data Creation

### PDF Generation Utilities

```python
# tests/utils/pdf_generator.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont
import io
import random
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import os

@dataclass
class SyntheticBOLData:
    """Ground truth data for synthetic BOL"""
    filename: str
    bol_number: str
    shipper_name: str
    shipper_address: str
    consignee_name: str
    consignee_address: str
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
    pdf_type: str = "text"  # "text" or "scanned"
    quality: str = "high"   # "high", "medium", "low"

class SyntheticBOLGenerator:
    """Generates synthetic BOL PDFs with known ground truth data"""
    
    def __init__(self):
        self.sample_data = self._load_sample_data()
        self.layouts = self._define_layouts()
    
    def _load_sample_data(self) -> Dict:
        """Load sample data for generating realistic BOLs"""
        return {
            "shipping_companies": [
                "ABC Shipping Lines", "Global Maritime Corp", "Ocean Express Ltd",
                "Pacific Cargo Co", "Atlantic Shipping Inc", "Maritime Logistics LLC"
            ],
            "consignees": [
                "Import Solutions Inc", "Trade Partners Ltd", "Global Imports Corp",
                "Destination Logistics", "Harbor Receivers Co", "Port Authority Inc"
            ],
            "vessels": [
                "MV Ocean Pioneer", "SS Cargo Master", "MV Pacific Express",
                "Atlantic Carrier", "Global Voyager", "Maritime Explorer"
            ],
            "ports": [
                "Los Angeles, CA", "New York, NY", "Long Beach, CA", "Savannah, GA",
                "Seattle, WA", "Houston, TX", "Norfolk, VA", "Charleston, SC"
            ],
            "cargo_types": [
                "Electronic Equipment", "Automotive Parts", "Textiles and Apparel",
                "Machinery Components", "Consumer Goods", "Industrial Materials",
                "Food Products", "Chemical Products", "Steel Products"
            ],
            "addresses": [
                "123 Industrial Blvd, Suite 100",
                "456 Harbor Drive, Building A",
                "789 Trade Center Way, Floor 5",
                "321 Shipping Lane, Unit 200",
                "654 Commerce Street, Suite 50",
                "987 Export Avenue, Building B"
            ]
        }
    
    def _define_layouts(self) -> List[Dict]:
        """Define different BOL layout templates"""
        return [
            {
                "name": "standard_layout",
                "title_pos": (72, 750),
                "bol_number_pos": (400, 720),
                "shipper_pos": (72, 650),
                "consignee_pos": (300, 650),
                "vessel_pos": (72, 500),
                "ports_pos": (300, 500),
                "cargo_pos": (72, 350),
                "weights_pos": (400, 350)
            },
            {
                "name": "alternate_layout",
                "title_pos": (100, 720),
                "bol_number_pos": (72, 680),
                "shipper_pos": (72, 600),
                "consignee_pos": (72, 480),
                "vessel_pos": (300, 600),
                "ports_pos": (300, 520),
                "cargo_pos": (72, 300),
                "weights_pos": (300, 300)
            }
        ]
    
    def generate_random_bol_data(self, bol_id: str = None) -> SyntheticBOLData:
        """Generate random but realistic BOL data"""
        if not bol_id:
            bol_id = f"BOL{random.randint(100000, 999999)}"
        
        data = SyntheticBOLData(
            filename=f"synthetic_bol_{bol_id}.pdf",
            bol_number=bol_id,
            shipper_name=random.choice(self.sample_data["shipping_companies"]),
            shipper_address=f"{random.choice(self.sample_data['addresses'])}\n{random.choice(['CA', 'NY', 'TX', 'FL'])} {random.randint(10000, 99999)}",
            consignee_name=random.choice(self.sample_data["consignees"]),
            consignee_address=f"{random.choice(self.sample_data['addresses'])}\n{random.choice(['CA', 'NY', 'TX', 'FL'])} {random.randint(10000, 99999)}",
            notify_party_name=random.choice(self.sample_data["consignees"]),
            notify_party_address=f"{random.choice(self.sample_data['addresses'])}\n{random.choice(['CA', 'NY', 'TX', 'FL'])} {random.randint(10000, 99999)}",
            vessel_name=random.choice(self.sample_data["vessels"]),
            voyage_number=f"VOY{random.randint(2024, 2025)}{random.randint(100, 999)}",
            port_of_load=random.choice(self.sample_data["ports"]),
            port_of_discharge=random.choice(self.sample_data["ports"]),
            description_of_goods=random.choice(self.sample_data["cargo_types"]),
            quantity_packages=f"{random.randint(10, 500)} CTNS",
            gross_weight=f"{random.randint(1000, 25000)} KG",
            net_weight=f"{random.randint(800, 20000)} KG",
            freight_terms=random.choice(["PREPAID", "COLLECT"]),
            date_of_issue=f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/2024"
        )
        
        return data
    
    def generate_text_based_pdf(self, bol_data: SyntheticBOLData, layout_name: str = "standard_layout") -> bytes:
        """Generate text-based PDF with extractable text"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        layout = next((l for l in self.layouts if l["name"] == layout_name), self.layouts[0])
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(layout["title_pos"][0], layout["title_pos"][1], "BILL OF LADING")
        
        # BOL Number
        c.setFont("Helvetica-Bold", 12)
        c.drawString(layout["bol_number_pos"][0], layout["bol_number_pos"][1], f"B/L NO: {bol_data.bol_number}")
        
        # Shipper section
        c.setFont("Helvetica-Bold", 10)
        c.drawString(layout["shipper_pos"][0], layout["shipper_pos"][1], "SHIPPER:")
        c.setFont("Helvetica", 9)
        y_pos = layout["shipper_pos"][1] - 15
        c.drawString(layout["shipper_pos"][0], y_pos, bol_data.shipper_name)
        for line in bol_data.shipper_address.split('\n'):
            y_pos -= 12
            c.drawString(layout["shipper_pos"][0], y_pos, line)
        
        # Consignee section
        c.setFont("Helvetica-Bold", 10)
        c.drawString(layout["consignee_pos"][0], layout["consignee_pos"][1], "CONSIGNEE:")
        c.setFont("Helvetica", 9)
        y_pos = layout["consignee_pos"][1] - 15
        c.drawString(layout["consignee_pos"][0], y_pos, bol_data.consignee_name)
        for line in bol_data.consignee_address.split('\n'):
            y_pos -= 12
            c.drawString(layout["consignee_pos"][0], y_pos, line)
        
        # Vessel information
        c.setFont("Helvetica-Bold", 10)
        c.drawString(layout["vessel_pos"][0], layout["vessel_pos"][1], f"VESSEL: {bol_data.vessel_name}")
        c.drawString(layout["vessel_pos"][0], layout["vessel_pos"][1] - 15, f"VOYAGE: {bol_data.voyage_number}")
        
        # Port information
        c.drawString(layout["ports_pos"][0], layout["ports_pos"][1], f"PORT OF LOADING: {bol_data.port_of_load}")
        c.drawString(layout["ports_pos"][0], layout["ports_pos"][1] - 15, f"PORT OF DISCHARGE: {bol_data.port_of_discharge}")
        
        # Cargo information
        c.drawString(layout["cargo_pos"][0], layout["cargo_pos"][1], f"DESCRIPTION OF GOODS: {bol_data.description_of_goods}")
        c.drawString(layout["cargo_pos"][0], layout["cargo_pos"][1] - 15, f"QUANTITY: {bol_data.quantity_packages}")
        
        # Weight information
        c.drawString(layout["weights_pos"][0], layout["weights_pos"][1], f"GROSS WEIGHT: {bol_data.gross_weight}")
        c.drawString(layout["weights_pos"][0], layout["weights_pos"][1] - 15, f"NET WEIGHT: {bol_data.net_weight}")
        
        # Additional information
        c.drawString(72, 200, f"FREIGHT TERMS: {bol_data.freight_terms}")
        c.drawString(72, 180, f"DATE OF ISSUE: {bol_data.date_of_issue}")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_scanned_pdf(self, bol_data: SyntheticBOLData, quality: str = "high") -> bytes:
        """Generate scanned-style PDF (image-based) for OCR testing"""
        # First create a high-resolution image
        img_width, img_height = 2550, 3300  # 300 DPI letter size
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 60)
            font_medium = ImageFont.truetype("arial.ttf", 45)
            font_small = ImageFont.truetype("arial.ttf", 35)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add content to image
        y_pos = 100
        
        # Title
        draw.text((200, y_pos), "BILL OF LADING", fill='black', font=font_large)
        y_pos += 100
        
        # BOL Number
        draw.text((1500, y_pos), f"B/L NO: {bol_data.bol_number}", fill='black', font=font_medium)
        y_pos += 150
        
        # Shipper
        draw.text((200, y_pos), "SHIPPER:", fill='black', font=font_medium)
        y_pos += 60
        draw.text((200, y_pos), bol_data.shipper_name, fill='black', font=font_small)
        y_pos += 50
        for line in bol_data.shipper_address.split('\n'):
            draw.text((200, y_pos), line, fill='black', font=font_small)
            y_pos += 45
        
        y_pos += 50
        
        # Consignee
        draw.text((200, y_pos), "CONSIGNEE:", fill='black', font=font_medium)
        y_pos += 60
        draw.text((200, y_pos), bol_data.consignee_name, fill='black', font=font_small)
        y_pos += 50
        for line in bol_data.consignee_address.split('\n'):
            draw.text((200, y_pos), line, fill='black', font=font_small)
            y_pos += 45
        
        # Continue with other fields...
        y_pos += 100
        draw.text((200, y_pos), f"VESSEL: {bol_data.vessel_name}", fill='black', font=font_medium)
        y_pos += 60
        draw.text((200, y_pos), f"VOYAGE: {bol_data.voyage_number}", fill='black', font=font_medium)
        
        # Apply quality degradation based on quality parameter
        if quality == "medium":
            # Add slight blur and noise
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        elif quality == "low":
            # Add more blur and reduce resolution
            img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
            img = img.resize((1275, 1650))  # Reduce to 150 DPI
            img = img.resize((2550, 3300))  # Scale back up (pixelated)
        
        # Convert image to PDF
        pdf_buffer = io.BytesIO()
        img.save(pdf_buffer, format='PDF', quality=95)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def generate_test_dataset(self, count: int, output_dir: str) -> List[SyntheticBOLData]:
        """Generate a complete test dataset with ground truth"""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/pdfs", exist_ok=True)
        
        dataset = []
        
        for i in range(count):
            # Generate random BOL data
            bol_data = self.generate_random_bol_data(f"TEST{i:04d}")
            
            # Randomly choose PDF type and quality
            pdf_type = random.choice(["text", "scanned"])
            quality = random.choice(["high", "medium", "low"])
            
            bol_data.pdf_type = pdf_type
            bol_data.quality = quality
            
            # Generate PDF
            if pdf_type == "text":
                pdf_bytes = self.generate_text_based_pdf(bol_data)
            else:
                pdf_bytes = self.generate_scanned_pdf(bol_data, quality)
            
            # Save PDF
            pdf_path = f"{output_dir}/pdfs/{bol_data.filename}"
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            dataset.append(bol_data)
        
        # Save ground truth data
        ground_truth = [asdict(bol) for bol in dataset]
        with open(f"{output_dir}/ground_truth.json", 'w') as f:
            json.dump(ground_truth, f, indent=2)
        
        return dataset

# Usage example and test data generation script
if __name__ == "__main__":
    generator = SyntheticBOLGenerator()
    
    # Generate small test dataset
    small_dataset = generator.generate_test_dataset(10, "tests/fixtures/small_dataset")
    print(f"Generated {len(small_dataset)} BOL PDFs for small dataset")
    
    # Generate performance test dataset
    perf_dataset = generator.generate_test_dataset(100, "tests/fixtures/performance_dataset")
    print(f"Generated {len(perf_dataset)} BOL PDFs for performance testing")
    
    # Generate edge case dataset
    edge_cases = []
    
    # Corrupted/incomplete BOLs
    for i in range(5):
        bol_data = generator.generate_random_bol_data(f"EDGE{i:02d}")
        # Randomly remove some fields to test error handling
        if i % 2 == 0:
            bol_data.bol_number = ""  # Missing BOL number
        if i % 3 == 0:
            bol_data.shipper_name = ""  # Missing shipper
        edge_cases.append(bol_data)
    
    # Save edge cases separately
    edge_cases_dir = "tests/fixtures/edge_cases"
    os.makedirs(edge_cases_dir, exist_ok=True)
    os.makedirs(f"{edge_cases_dir}/pdfs", exist_ok=True)
    
    for bol_data in edge_cases:
        pdf_bytes = generator.generate_text_based_pdf(bol_data)
        with open(f"{edge_cases_dir}/pdfs/{bol_data.filename}", 'wb') as f:
            f.write(pdf_bytes)
    
    with open(f"{edge_cases_dir}/ground_truth.json", 'w') as f:
        json.dump([asdict(bol) for bol in edge_cases], f, indent=2)
    
    print(f"Generated {len(edge_cases)} edge case BOL PDFs")
```

## Quality Metrics and Success Criteria

### Accuracy Benchmarks

```python
# tests/utils/accuracy_calculator.py

from typing import List, Dict, Tuple
import json
from dataclasses import asdict
from app import BOLData, SyntheticBOLData

class AccuracyCalculator:
    """Calculate extraction accuracy metrics"""
    
    def __init__(self):
        self.field_weights = {
            'bol_number': 1.0,          # Critical field
            'shipper_name': 0.9,        # Very important
            'consignee_name': 0.9,      # Very important  
            'vessel_name': 0.8,         # Important
            'port_of_load': 0.8,        # Important
            'port_of_discharge': 0.8,   # Important
            'gross_weight': 0.7,        # Moderately important
            'quantity_packages': 0.7,   # Moderately important
            'freight_terms': 0.6,       # Useful
            'date_of_issue': 0.6,       # Useful
            'voyage_number': 0.5        # Nice to have
        }
    
    def calculate_field_accuracy(self, extracted: str, expected: str, threshold: float = 0.8) -> float:
        """Calculate accuracy for a single field using fuzzy matching"""
        if not expected.strip():
            return 1.0 if not extracted.strip() else 0.5  # Partial credit for empty expected
        
        if not extracted.strip():
            return 0.0  # No extraction when expected
        
        # Exact match
        if extracted.strip().lower() == expected.strip().lower():
            return 1.0
        
        # Fuzzy matching using simple character overlap
        extracted_clean = set(extracted.lower().replace(' ', '').replace(',', ''))
        expected_clean = set(expected.lower().replace(' ', '').replace(',', ''))
        
        if not expected_clean:
            return 0.0
        
        overlap = len(extracted_clean.intersection(expected_clean))
        similarity = overlap / len(expected_clean)
        
        return 1.0 if similarity >= threshold else similarity
    
    def calculate_bol_accuracy(self, extracted: BOLData, expected: SyntheticBOLData) -> Dict[str, float]:
        """Calculate accuracy metrics for a single BOL"""
        results = {}
        
        # Compare each field
        field_mapping = {
            'bol_number': (extracted.bol_number, expected.bol_number),
            'shipper_name': (extracted.shipper_name, expected.shipper_name),
            'consignee_name': (extracted.consignee_name, expected.consignee_name),
            'vessel_name': (extracted.vessel_name, expected.vessel_name),
            'voyage_number': (extracted.voyage_number, expected.voyage_number),
            'port_of_load': (extracted.port_of_load, expected.port_of_load),
            'port_of_discharge': (extracted.port_of_discharge, expected.port_of_discharge),
            'gross_weight': (extracted.gross_weight, expected.gross_weight),
            'quantity_packages': (extracted.quantity_packages, expected.quantity_packages),
            'freight_terms': (extracted.freight_terms, expected.freight_terms),
            'date_of_issue': (extracted.date_of_issue, expected.date_of_issue)
        }
        
        for field, (ext_val, exp_val) in field_mapping.items():
            results[field] = self.calculate_field_accuracy(ext_val, exp_val)
        
        # Calculate weighted overall accuracy
        weighted_sum = sum(results[field] * self.field_weights.get(field, 0.5) 
                          for field in results)
        total_weight = sum(self.field_weights.get(field, 0.5) for field in results)
        results['overall_accuracy'] = weighted_sum / total_weight
        
        return results
    
    def calculate_dataset_accuracy(self, extracted_results: List[BOLData], 
                                 ground_truth: List[SyntheticBOLData]) -> Dict[str, any]:
        """Calculate accuracy metrics for entire dataset"""
        if len(extracted_results) != len(ground_truth):
            raise ValueError("Mismatched dataset sizes")
        
        field_accuracies = {field: [] for field in self.field_weights.keys()}
        field_accuracies['overall_accuracy'] = []
        
        individual_results = []
        
        for extracted, expected in zip(extracted_results, ground_truth):
            bol_accuracy = self.calculate_bol_accuracy(extracted, expected)
            individual_results.append(bol_accuracy)
            
            for field, accuracy in bol_accuracy.items():
                if field in field_accuracies:
                    field_accuracies[field].append(accuracy)
        
        # Calculate summary statistics
        summary = {}
        for field, accuracies in field_accuracies.items():
            summary[field] = {
                'mean': sum(accuracies) / len(accuracies),
                'min': min(accuracies),
                'max': max(accuracies),
                'above_80_percent': sum(1 for a in accuracies if a >= 0.8) / len(accuracies),
                'above_90_percent': sum(1 for a in accuracies if a >= 0.9) / len(accuracies)
            }
        
        return {
            'summary': summary,
            'individual_results': individual_results,
            'dataset_size': len(extracted_results)
        }

# Success criteria definitions
SUCCESS_CRITERIA = {
    'field_accuracy_targets': {
        'bol_number': 0.95,      # 95% accuracy target
        'shipper_name': 0.85,    # 85% accuracy target
        'consignee_name': 0.85,  # 85% accuracy target
        'vessel_name': 0.80,     # 80% accuracy target
        'port_of_load': 0.80,    # 80% accuracy target
        'port_of_discharge': 0.80, # 80% accuracy target
        'overall_accuracy': 0.80   # 80% overall accuracy target
    },
    'performance_targets': {
        'text_based_processing_time': 5.0,     # seconds per file
        'ocr_processing_time': 45.0,           # seconds per file
        'batch_memory_usage': 100,             # MB per 50 files
        'export_time_1000_records': 30.0       # seconds
    },
    'reliability_targets': {
        'crash_rate': 0.01,                    # <1% crash rate
        'successful_extraction_rate': 0.95,   # >95% successful extractions
        'ocr_fallback_success_rate': 0.70     # >70% OCR success when needed
    }
}
```

## Test Coverage Analysis

### Coverage Configuration

```python
# tests/conftest.py

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch
from app import BOLOCRApp, PDFProcessor, BOLDataExtractor, FieldPatterns, TableParser, ExcelExporter
from tests.utils.pdf_generator import SyntheticBOLGenerator, SyntheticBOLData

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup handled by system

@pytest.fixture(scope="session") 
def synthetic_bol_generator():
    """Provide synthetic BOL generator"""
    return SyntheticBOLGenerator()

@pytest.fixture
def sample_bol_data():
    """Provide sample BOL data for testing"""
    return SyntheticBOLData(
        filename="test_sample.pdf",
        bol_number="TEST123456",
        shipper_name="Test Shipper Inc",
        shipper_address="123 Test Street\nTest City, TC 12345",
        consignee_name="Test Consignee Corp", 
        consignee_address="456 Dest Avenue\nDest City, DC 67890",
        vessel_name="MV Test Ship",
        voyage_number="VOY2024001",
        port_of_load="Test Port A",
        port_of_discharge="Test Port B",
        description_of_goods="Test Cargo",
        quantity_packages="100 CTNS",
        gross_weight="5000 KG",
        freight_terms="PREPAID",
        date_of_issue="01/01/2024"
    )

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing"""
    with patch('streamlit.progress') as mock_progress, \
         patch('streamlit.empty') as mock_empty, \
         patch('streamlit.session_state') as mock_session:
        
        mock_session.processed_data = []
        mock_session.processing_complete = False
        
        yield {
            'progress': mock_progress,
            'empty': mock_empty,
            'session_state': mock_session
        }

# Coverage configuration for pytest-cov
pytest_plugins = ["pytest_cov"]

def pytest_configure(config):
    """Configure pytest with coverage settings"""
    config.option.cov_source = ["app"]
    config.option.cov_report = ["term-missing", "html"]
    config.option.cov_fail_under = 80  # Require 80% coverage
```

### Coverage Test Runner

```python
# tests/run_coverage.py

import subprocess
import sys
import os
from pathlib import Path

def run_tests_with_coverage():
    """Run complete test suite with coverage analysis"""
    
    # Define test categories
    test_categories = {
        'unit': 'tests/unit/',
        'integration': 'tests/integration/', 
        'performance': 'tests/performance/'
    }
    
    # Run tests by category
    for category, path in test_categories.items():
        print(f"\n{'='*50}")
        print(f"Running {category.upper()} Tests")
        print(f"{'='*50}")
        
        cmd = [
            'python', '-m', 'pytest',
            path,
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-append',
            '-v',
            '--tb=short'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FAILED: {category} tests")
            print(result.stdout)
            print(result.stderr)
            return False
        else:
            print(f"PASSED: {category} tests")
    
    # Generate final coverage report
    print(f"\n{'='*50}")
    print("Generating Final Coverage Report")
    print(f"{'='*50}")
    
    coverage_cmd = [
        'python', '-m', 'pytest',
        '--cov=app',
        '--cov-report=html:htmlcov',
        '--cov-report=term',
        '--cov-fail-under=80',
        'tests/'
    ]
    
    result = subprocess.run(coverage_cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed with sufficient coverage!")
        print("📊 HTML coverage report generated in htmlcov/")
        return True
    else:
        print("\n❌ Coverage requirements not met")
        return False

if __name__ == "__main__":
    success = run_tests_with_coverage()
    sys.exit(0 if success else 1)
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
1. Set up test framework and structure
2. Create synthetic test data generator
3. Implement core unit tests for all classes
4. Establish CI/CD pipeline with automated testing

### Phase 2: Integration & Performance (Week 3-4)
1. Develop integration tests for component interactions
2. Build performance testing framework
3. Create stress tests for batch processing
4. Implement memory usage monitoring

### Phase 3: Quality Assurance (Week 5-6)
1. Develop accuracy calculation and reporting
2. Create comprehensive test datasets
3. Implement automated quality metrics
4. Build test result dashboard

### Phase 4: Advanced Testing (Week 7-8)
1. Cross-platform compatibility tests
2. Security and error handling validation
3. User acceptance test scenarios
4. Documentation and training materials

This comprehensive testing strategy provides a robust framework for ensuring the BOL OCR Extractor meets production quality standards with measurable accuracy targets, performance benchmarks, and comprehensive coverage analysis.