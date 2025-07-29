"""
Unit tests for BOLDataExtractor class
"""

import pytest
from unittest.mock import Mock, patch
from app import BOLDataExtractor, FieldPatterns, BOLData, TableParser
import pandas as pd

class TestBOLDataExtractor:
    """Test suite for BOLDataExtractor class"""
    
    def test_init(self, bol_extractor):
        """Test BOLDataExtractor initialization"""
        assert isinstance(bol_extractor.patterns, FieldPatterns)
    
    def test_extract_bol_number(self, bol_extractor, sample_bol_text):
        """Test BOL number extraction"""
        result = bol_extractor.extract_bol_number(sample_bol_text)
        assert result == "BOL123456789"
    
    def test_extract_bol_number_variations(self, bol_extractor):
        """Test BOL number extraction with different formats"""
        test_cases = [
            ("B/L No: BOL123456", "BOL123456"),
            ("BOL NUMBER: TEST-001", "TEST-001"),
            ("Bill of Lading #: ABC123", "ABC123"),
            ("Document No: DOC789", "DOC789"),
            ("b/l number: bol123456", "bol123456"),  # Case insensitive
        ]
        
        for text, expected in test_cases:
            result = bol_extractor.extract_bol_number(text)
            assert result == expected
    
    def test_extract_bol_number_no_match(self, bol_extractor):
        """Test BOL number extraction when no match found"""
        text = "This text has no BOL number patterns"
        result = bol_extractor.extract_bol_number(text)
        assert result == ""
    
    def test_extract_parties(self, bol_extractor, sample_bol_text):
        """Test extraction of shipper, consignee, and notify party"""
        shipper_name, shipper_address, consignee_name, consignee_address, notify_name, notify_address = bol_extractor.extract_parties(sample_bol_text)
        
        assert shipper_name == "ABC Shipping Company"
        assert "123 Export Lane" in shipper_address
        assert "Los Angeles, CA 90001" in shipper_address
        assert consignee_name == "XYZ Import Corp"
        assert "456 Harbor Blvd" in consignee_address
        assert "New York, NY 10001" in consignee_address
        assert notify_name == "Maritime Logistics Inc"
        assert "789 Dock Street" in notify_address
        assert "Boston, MA 02101" in notify_address
    
    def test_extract_parties_single_line_addresses(self, bol_extractor):
        """Test party extraction with single line addresses"""
        text = """
        SHIPPER: Single Line Shipper, CA 90001
        CONSIGNEE: Single Line Consignee, NY 10001
        NOTIFY PARTY: Single Line Notify, MA 02101
        """
        
        shipper_name, shipper_address, consignee_name, consignee_address, notify_name, notify_address = bol_extractor.extract_parties(text)
        
        assert shipper_name == "Single Line Shipper, CA 90001"
        assert shipper_address == ""  # No additional address lines
        assert consignee_name == "Single Line Consignee, NY 10001"
        assert consignee_address == ""
        assert notify_name == "Single Line Notify, MA 02101"  
        assert notify_address == ""
    
    def test_extract_parties_missing_fields(self, bol_extractor):
        """Test party extraction when some fields are missing"""
        text = """
        SHIPPER: Only Shipper Company
        123 Shipper Street
        """
        
        shipper_name, shipper_address, consignee_name, consignee_address, notify_name, notify_address = bol_extractor.extract_parties(text)
        
        assert shipper_name == "Only Shipper Company"
        assert "123 Shipper Street" in shipper_address
        assert consignee_name == ""
        assert consignee_address == ""
        assert notify_name == ""
        assert notify_address == ""
    
    def test_extract_vessel_info(self, bol_extractor, sample_bol_text):
        """Test vessel and voyage extraction"""
        vessel, voyage = bol_extractor.extract_vessel_info(sample_bol_text)
        assert vessel == "MV Ocean Carrier"
        assert voyage == "VOY2024001"
    
    def test_extract_vessel_info_variations(self, bol_extractor):
        """Test vessel extraction with different formats"""
        test_cases = [
            ("VESSEL: MV Test Ship", "MV Test Ship"),
            ("Vessel: SS Cargo Master", "SS Cargo Master"),
            ("SHIP NAME: Atlantic Express", "Atlantic Express"),
        ]
        
        for text, expected in test_cases:
            vessel, _ = bol_extractor.extract_vessel_info(text)
            assert vessel == expected
    
    def test_extract_voyage_variations(self, bol_extractor):
        """Test voyage extraction with different formats"""
        test_cases = [
            ("VOYAGE: VOY2024001", "VOY2024001"),
            ("Voyage: V001-2024", "V001-2024"),
            ("VOY: TEST123", "TEST123"),
        ]
        
        for text, expected in test_cases:
            _, voyage = bol_extractor.extract_vessel_info(text)
            assert voyage == expected
    
    def test_extract_ports(self, bol_extractor, sample_bol_text):
        """Test port extraction"""
        port_load, port_discharge = bol_extractor.extract_ports(sample_bol_text)
        assert port_load == "Los Angeles, CA"
        assert port_discharge == "New York, NY"
    
    def test_extract_ports_variations(self, bol_extractor):
        """Test port extraction with different formats"""
        text = """
        PORT OF LOADING: Long Beach, CA
        PORT OF DISCHARGE: Savannah, GA
        """
        
        port_load, port_discharge = bol_extractor.extract_ports(text)
        assert port_load == "Long Beach, CA"
        assert port_discharge == "Savannah, GA"
    
    def test_extract_dates(self, bol_extractor, sample_bol_text):
        """Test date extraction"""
        result = bol_extractor.extract_dates(sample_bol_text)
        assert result == "15/03/2024"
    
    def test_extract_dates_variations(self, bol_extractor):
        """Test date extraction with different formats"""
        test_cases = [
            ("Date: 15/03/2024", "15/03/2024"),
            ("Issue Date: Mar 15, 2024", "Mar 15, 2024"),
            ("15 March 2024", "15 March 2024"),
            ("March 15, 2024", "March 15, 2024"),
            ("12-25-2023", "12-25-2023"),
        ]
        
        for text, expected in test_cases:
            result = bol_extractor.extract_dates(text)
            assert result == expected
    
    def test_extract_weights_quantities(self, bol_extractor, sample_bol_text):
        """Test weight and quantity extraction"""
        gross_weight, net_weight, quantity = bol_extractor.extract_weights_quantities(sample_bol_text)
        assert gross_weight == "2,500 KG"
        assert net_weight == "2,200 KG"
        assert quantity == "100 CTNS"
    
    def test_extract_weights_quantities_variations(self, bol_extractor):
        """Test weight and quantity extraction with different formats"""
        text = """
        GROSS WEIGHT: 5,000 LBS
        NET WEIGHT: 4,500 LBS
        PACKAGES: 50 BOXES
        QUANTITY: 25 PALLETS
        """
        
        gross_weight, net_weight, quantity = bol_extractor.extract_weights_quantities(text)
        assert gross_weight == "5,000 LBS"
        assert net_weight == "4,500 LBS"
        # Should get first quantity pattern match
        assert quantity in ["50 BOXES", "25 PALLETS"]
    
    def test_extract_weights_only_gross(self, bol_extractor):
        """Test weight extraction when only gross weight is available"""
        text = "WEIGHT: 3,000 KG"
        
        gross_weight, net_weight, quantity = bol_extractor.extract_weights_quantities(text)
        assert gross_weight == "3,000 KG"
        assert net_weight == ""
        assert quantity == ""
    
    def test_extract_freight_terms(self, bol_extractor, sample_bol_text):
        """Test freight terms extraction"""
        result = bol_extractor.extract_freight_terms(sample_bol_text)
        assert result == "PREPAID"
    
    def test_extract_freight_terms_variations(self, bol_extractor):
        """Test freight terms extraction with different formats"""
        test_cases = [
            ("FREIGHT: PREPAID", "PREPAID"),
            ("Freight: COLLECT", "COLLECT"),
            ("TERMS: PAYABLE", "PAYABLE"),
            ("freight: prepaid", "PREPAID"),  # Case insensitive match
        ]
        
        for text, expected in test_cases:
            result = bol_extractor.extract_freight_terms(text)
            assert result == expected
    
    def test_clean_field_data(self, bol_extractor):
        """Test field data cleaning"""
        test_cases = [
            ("  : - Test Data - :  ", "Test Data"),
            ("   Extra   Spaces   ", "Extra Spaces"),
            (": Leading colon", "Leading colon"),
            ("Trailing colon :", "Trailing colon"),
            ("Multiple\n\nLines\n", "Multiple Lines"),
        ]
        
        for dirty, expected in test_cases:
            cleaned = bol_extractor.clean_field_data(dirty)
            assert cleaned == expected
    
    def test_extract_field_no_match(self, bol_extractor):
        """Test extraction when no patterns match"""
        text = "This text has no BOL patterns"
        result = bol_extractor.extract_field(text, "bol_number")
        assert result == ""
    
    def test_extract_field_empty_result(self, bol_extractor):
        """Test extraction when pattern matches but result is empty"""
        text = "B/L NO: "  # Pattern matches but no content
        result = bol_extractor.extract_field(text, "bol_number")
        assert result == ""
    
    def test_extract_all_fields_complete(self, bol_extractor, sample_bol_text):
        """Test complete field extraction"""
        bol_data = bol_extractor.extract_all_fields(sample_bol_text, [], "test.pdf")
        
        assert bol_data.filename == "test.pdf"
        assert bol_data.bol_number == "BOL123456789"
        assert bol_data.shipper_name == "ABC Shipping Company"
        assert bol_data.consignee_name == "XYZ Import Corp"
        assert bol_data.notify_party_name == "Maritime Logistics Inc"
        assert bol_data.vessel_name == "MV Ocean Carrier"
        assert bol_data.voyage_number == "VOY2024001"
        assert bol_data.port_of_load == "Los Angeles, CA"
        assert bol_data.port_of_discharge == "New York, NY"
        assert bol_data.freight_terms == "PREPAID"
        assert bol_data.gross_weight == "2,500 KG"
        assert bol_data.net_weight == "2,200 KG"
        assert bol_data.quantity_packages == "100 CTNS"
        assert bol_data.date_of_issue == "15/03/2024"
        assert not bol_data.extraction_failed
    
    def test_extract_all_fields_with_tables(self, bol_extractor):
        """Test field extraction including table-based cargo description"""
        text = "B/L NUMBER: TABLE001"
        
        # Mock table with cargo description
        mock_table = pd.DataFrame({
            'Description of Goods': ['Steel Products', 'Machinery Parts']
        })
        
        with patch.object(TableParser, 'parse_cargo_description_table') as mock_parse:
            mock_parse.return_value = "Steel Products; Machinery Parts"
            
            bol_data = bol_extractor.extract_all_fields(text, [mock_table], "table_test.pdf")
            
            assert bol_data.filename == "table_test.pdf"
            assert bol_data.bol_number == "TABLE001"
            assert bol_data.description_of_goods == "Steel Products; Machinery Parts"
            mock_parse.assert_called_once_with([mock_table])
    
    def test_extract_all_fields_text_cargo_fallback(self, bol_extractor):
        """Test cargo description extraction from text when no tables"""
        text = """
        B/L NUMBER: CARGO001
        DESCRIPTION OF GOODS: Electronic Components and Accessories
        Additional cargo info here
        """
        
        bol_data = bol_extractor.extract_all_fields(text, [], "cargo_test.pdf")
        
        assert bol_data.filename == "cargo_test.pdf"
        assert bol_data.bol_number == "CARGO001"
        assert "Electronic Components and Accessories" in bol_data.description_of_goods
    
    def test_extract_all_fields_extraction_error(self, bol_extractor):
        """Test error handling during field extraction"""
        # Create malformed text that might cause extraction errors
        malformed_text = "Malformed BOL content"
        
        with patch.object(bol_extractor, 'extract_bol_number') as mock_extract:
            mock_extract.side_effect = Exception("Extraction error")
            
            bol_data = bol_extractor.extract_all_fields(malformed_text, [], "error_test.pdf")
            
            assert bol_data.filename == "error_test.pdf"
            assert bol_data.extraction_failed is True
            assert "Extraction error" in bol_data.processing_notes
    
    def test_extract_multiple_bol_numbers_returns_first(self, bol_extractor):
        """Test handling of multiple BOL numbers (should return first)"""
        text = "B/L NO: BOL001 and also BOL NO: BOL002 and Bill of Lading #: BOL003"
        result = bol_extractor.extract_bol_number(text)
        assert result == "BOL001"
    
    def test_extract_case_insensitive_patterns(self, bol_extractor):
        """Test case-insensitive pattern matching"""
        text = """
        b/l number: bol123456
        shipper: lowercase shipper
        vessel: mv lowercase ship
        """
        
        bol_number = bol_extractor.extract_bol_number(text)
        vessel, _ = bol_extractor.extract_vessel_info(text)
        
        assert bol_number == "bol123456"
        assert vessel == "mv lowercase ship"
    
    def test_extract_with_special_characters(self, bol_extractor):
        """Test extraction with special characters in data"""
        text = """
        B/L NUMBER: BOL-123/456_789
        VESSEL: M.V. Special-Ship (2024)
        GROSS WEIGHT: 1,234.56 KG
        """
        
        bol_number = bol_extractor.extract_bol_number(text)
        vessel, _ = bol_extractor.extract_vessel_info(text)
        gross_weight, _, _ = bol_extractor.extract_weights_quantities(text)
        
        assert bol_number == "BOL-123/456_789"
        assert vessel == "M.V. Special-Ship (2024)"
        assert gross_weight == "1,234.56 KG"