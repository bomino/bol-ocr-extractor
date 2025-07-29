"""
Global test configuration and fixtures for BOL OCR Extractor testing
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the parent directory to path to import the app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import BOLOCRApp, PDFProcessor, BOLDataExtractor, FieldPatterns, TableParser, ExcelExporter, BOLData

# Test data for creating synthetic BOL content
SAMPLE_BOL_TEXT = """
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

DESCRIPTION OF GOODS: Electronic Equipment and Components
"""

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    # Create subdirectories
    os.makedirs(f"{temp_dir}/pdfs", exist_ok=True)
    os.makedirs(f"{temp_dir}/results", exist_ok=True)
    yield temp_dir
    # Cleanup is handled by system

@pytest.fixture
def sample_bol_text():
    """Provide sample BOL text for testing"""
    return SAMPLE_BOL_TEXT

@pytest.fixture
def sample_bol_data():
    """Provide sample BOL data object for testing"""
    bol_data = BOLData()
    bol_data.filename = "test_sample.pdf"
    bol_data.bol_number = "BOL123456789"
    bol_data.shipper_name = "ABC Shipping Company"
    bol_data.shipper_address = "123 Export Lane\nLos Angeles, CA 90001"
    bol_data.consignee_name = "XYZ Import Corp"
    bol_data.consignee_address = "456 Harbor Blvd\nNew York, NY 10001"
    bol_data.notify_party_name = "Maritime Logistics Inc"
    bol_data.notify_party_address = "789 Dock Street\nBoston, MA 02101"
    bol_data.vessel_name = "MV Ocean Carrier"
    bol_data.voyage_number = "VOY2024001"
    bol_data.port_of_load = "Los Angeles, CA"
    bol_data.port_of_discharge = "New York, NY"
    bol_data.description_of_goods = "Electronic Equipment and Components"
    bol_data.quantity_packages = "100 CTNS"
    bol_data.gross_weight = "2,500 KG"
    bol_data.net_weight = "2,200 KG"
    bol_data.freight_terms = "PREPAID"
    bol_data.date_of_issue = "15/03/2024"
    bol_data.extraction_method = "text"
    bol_data.extraction_confidence = "high"
    return bol_data

@pytest.fixture
def mock_pdf_file():
    """Create mock PDF file for testing"""
    mock_file = Mock()
    mock_file.name = "test_bol.pdf"
    return mock_file

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for testing"""
    with patch('streamlit.progress') as mock_progress, \
         patch('streamlit.empty') as mock_empty:
        
        yield {
            'progress': mock_progress,
            'empty': mock_empty
        }

@pytest.fixture
def pdf_processor():
    """Provide PDFProcessor instance"""
    return PDFProcessor()

@pytest.fixture
def bol_extractor():
    """Provide BOLDataExtractor instance"""
    return BOLDataExtractor()

@pytest.fixture
def field_patterns():
    """Provide FieldPatterns instance"""
    return FieldPatterns()

@pytest.fixture
def table_parser():
    """Provide TableParser instance"""
    return TableParser()

@pytest.fixture
def excel_exporter():
    """Provide ExcelExporter instance"""
    return ExcelExporter()

@pytest.fixture
def bol_ocr_app():
    """Provide BOLOCRApp instance"""
    return BOLOCRApp()

# Ground truth data for accuracy testing
@pytest.fixture
def ground_truth_data():
    """Provide ground truth data for accuracy calculations"""
    return {
        "test_bol_001.pdf": {
            "bol_number": "BOL123456789",
            "shipper_name": "ABC Shipping Company",
            "consignee_name": "XYZ Import Corp",
            "vessel_name": "MV Ocean Carrier",
            "voyage_number": "VOY2024001",
            "port_of_load": "Los Angeles, CA",
            "port_of_discharge": "New York, NY",
            "freight_terms": "PREPAID",
            "gross_weight": "2,500 KG",
            "quantity_packages": "100 CTNS"
        }
    }

# Configuration for coverage and test execution
def pytest_configure(config):
    """Configure pytest with coverage and reporting settings"""
    # Add custom markers
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)

# Cleanup function
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Any cleanup code here
    pass