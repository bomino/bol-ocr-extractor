"""
Unit tests for FieldPatterns class
"""

import pytest
import re
from app import FieldPatterns

class TestFieldPatterns:
    """Test suite for FieldPatterns class"""
    
    def test_init(self, field_patterns):
        """Test FieldPatterns initialization"""
        assert isinstance(field_patterns.patterns, dict)
        assert len(field_patterns.patterns) > 0
        
        # Check that key pattern types exist
        expected_keys = [
            "bol_number", "shipper", "consignee", "notify_party",
            "vessel", "voyage", "port_of_load", "port_of_discharge",
            "freight_terms", "date_patterns", "weight_patterns", "quantity_patterns"
        ]
        
        for key in expected_keys:
            assert key in field_patterns.patterns
    
    def test_get_bol_number_patterns(self, field_patterns):
        """Test BOL number pattern retrieval"""
        bol_patterns = field_patterns.get_patterns("bol_number")
        assert len(bol_patterns) > 0
        assert isinstance(bol_patterns, list)
        assert any("B/L" in pattern for pattern in bol_patterns)
        assert any("BOL" in pattern for pattern in bol_patterns)
        assert any("Bill" in pattern for pattern in bol_patterns)
    
    def test_get_shipper_patterns(self, field_patterns):
        """Test shipper pattern retrieval"""
        shipper_patterns = field_patterns.get_patterns("shipper")
        assert len(shipper_patterns) > 0
        assert any("SHIPPER" in pattern for pattern in shipper_patterns)
        assert any("FROM" in pattern for pattern in shipper_patterns)
    
    def test_get_nonexistent_pattern(self, field_patterns):
        """Test retrieval of non-existent pattern type"""
        result = field_patterns.get_patterns("nonexistent_field")
        assert result == []
    
    def test_bol_number_pattern_matching(self, field_patterns):
        """Test actual BOL number pattern matching"""
        bol_patterns = field_patterns.get_patterns("bol_number")
        test_cases = [
            ("B/L No: BOL123456", "BOL123456"),
            ("B/L NUMBER: TEST-001", "TEST-001"),
            ("BOL No: ABC123", "ABC123"),
            ("BOL NUMBER: XYZ789", "XYZ789"),
            ("Bill of Lading No: DOC456", "DOC456"),
            ("Bill of Lading Number: SAMPLE123", "SAMPLE123"),
            ("Document No: DOC789", "DOC789"),
            ("Document Number: REF001", "REF001"),
            # Case variations
            ("b/l no: bol123456", "bol123456"),
            ("B/L No.: BOL-TEST-001", "BOL-TEST-001"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in bol_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    assert match.group(1) == expected, f"Pattern {pattern} matched {match.group(1)} instead of {expected} for text: {text}"
                    matched = True
                    break
            assert matched, f"No pattern matched for text: {text}"
    
    def test_shipper_pattern_matching(self, field_patterns):
        """Test shipper pattern matching"""
        shipper_patterns = field_patterns.get_patterns("shipper")
        test_cases = [
            ("""SHIPPER:
Test Company Inc
123 Main Street
CONSIGNEE:
Other Company""", "Test Company Inc\n123 Main Street"),
            ("""Shipper:
ABC Shipping Ltd
456 Export Blvd
City, State 12345
CONSIGNEE:
Destination Corp""", "ABC Shipping Ltd\n456 Export Blvd\nCity, State 12345"),
            ("""FROM:
Origin Company
789 Source Ave
CONSIGNEE:
Target Inc""", "Origin Company\n789 Source Ave"),
        ]
        
        for text, expected_content in test_cases:
            matched = False
            for pattern in shipper_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    result = match.group(1).strip()
                    # Check that expected content is in the result
                    for line in expected_content.split('\n'):
                        assert line.strip() in result, f"Expected '{line.strip()}' in result '{result}'"
                    matched = True
                    break
            assert matched, f"No shipper pattern matched for text: {text}"
    
    def test_consignee_pattern_matching(self, field_patterns):
        """Test consignee pattern matching"""
        consignee_patterns = field_patterns.get_patterns("consignee")
        test_cases = [
            ("""CONSIGNEE:
Destination Corp
456 Harbor Blvd
NOTIFY PARTY:
Notify Company""", "Destination Corp\n456 Harbor Blvd"),
            ("""Consignee:
Import Solutions Inc
789 Trade Center
VESSEL:
Ship Name""", "Import Solutions Inc\n789 Trade Center"),
            ("""TO:
Final Destination LLC
321 End Street
NOTIFY:
Someone""", "Final Destination LLC\n321 End Street"),
        ]
        
        for text, expected_content in test_cases:
            matched = False
            for pattern in consignee_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    result = match.group(1).strip()
                    for line in expected_content.split('\n'):
                        assert line.strip() in result
                    matched = True
                    break
            assert matched, f"No consignee pattern matched for text: {text}"
    
    def test_notify_party_pattern_matching(self, field_patterns):
        """Test notify party pattern matching"""
        notify_patterns = field_patterns.get_patterns("notify_party")
        test_cases = [
            ("""NOTIFY PARTY:
Notification Company
123 Notify Street
VESSEL:
Ship Name""", "Notification Company\n123 Notify Street"),
            ("""Notify Party:
Alert Services LLC
456 Alert Ave
PORT:
Port Name""", "Alert Services LLC\n456 Alert Ave"),
            ("""ALSO NOTIFY:
Additional Notify Corp
789 Extra Blvd
GOODS:
Cargo Description""", "Additional Notify Corp\n789 Extra Blvd"),
        ]
        
        for text, expected_content in test_cases:
            matched = False
            for pattern in notify_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if match:
                    result = match.group(1).strip()
                    for line in expected_content.split('\n'):
                        assert line.strip() in result
                    matched = True
                    break
            assert matched, f"No notify party pattern matched for text: {text}"
    
    def test_vessel_pattern_matching(self, field_patterns):
        """Test vessel pattern matching"""
        vessel_patterns = field_patterns.get_patterns("vessel")
        test_cases = [
            ("VESSEL: MV Ocean Carrier", "MV Ocean Carrier"),
            ("Vessel: SS Maritime Express", "SS Maritime Express"),
            ("SHIP NAME: Atlantic Voyager", "Atlantic Voyager"),
            ("vessel: pacific trader", "pacific trader"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in vessel_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    assert match.group(1).strip() == expected
                    matched = True
                    break
            assert matched, f"No vessel pattern matched for text: {text}"
    
    def test_voyage_pattern_matching(self, field_patterns):
        """Test voyage pattern matching"""
        voyage_patterns = field_patterns.get_patterns("voyage")
        test_cases = [
            ("VOYAGE: VOY2024001", "VOY2024001"),
            ("Voyage: V123-2024", "V123-2024"),
            ("VOY: TEST001", "TEST001"),
            ("voyage: abc123", "abc123"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in voyage_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    assert match.group(1).strip() == expected
                    matched = True
                    break
            assert matched, f"No voyage pattern matched for text: {text}"
    
    def test_port_of_load_pattern_matching(self, field_patterns):
        """Test port of loading pattern matching"""
        port_patterns = field_patterns.get_patterns("port_of_load")
        test_cases = [
            ("PORT OF LOADING: Los Angeles, CA", "Los Angeles, CA"),
            ("Port of Loading: Long Beach, CA", "Long Beach, CA"),
            ("PORT OF LOAD: New York, NY", "New York, NY"),
            ("Port of Load: Seattle, WA", "Seattle, WA"),
            ("LOAD PORT: Houston, TX", "Houston, TX"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in port_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    assert match.group(1).strip() == expected
                    matched = True
                    break
            assert matched, f"No port of load pattern matched for text: {text}"
    
    def test_port_of_discharge_pattern_matching(self, field_patterns):
        """Test port of discharge pattern matching"""
        port_patterns = field_patterns.get_patterns("port_of_discharge")
        test_cases = [
            ("PORT OF DISCHARGE: New York, NY", "New York, NY"),
            ("Port of Discharge: Savannah, GA", "Savannah, GA"),
            ("PORT OF DEST: Miami, FL", "Miami, FL"),
            ("Port of Dest: Norfolk, VA", "Norfolk, VA"),
            ("DISCHARGE PORT: Charleston, SC", "Charleston, SC"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in port_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    assert match.group(1).strip() == expected
                    matched = True
                    break
            assert matched, f"No port of discharge pattern matched for text: {text}"
    
    def test_freight_terms_pattern_matching(self, field_patterns):
        """Test freight terms pattern matching"""
        freight_patterns = field_patterns.get_patterns("freight_terms")
        test_cases = [
            ("FREIGHT: PREPAID", "PREPAID"),
            ("Freight: COLLECT", "COLLECT"),
            ("TERMS: PAYABLE", "PAYABLE"),
            ("freight: prepaid", "prepaid"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in freight_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    assert match.group(1).strip() == expected
                    matched = True
                    break
            assert matched, f"No freight terms pattern matched for text: {text}"
    
    def test_date_pattern_matching(self, field_patterns):
        """Test date pattern matching"""
        date_patterns = field_patterns.get_patterns("date_patterns")
        test_cases = [
            ("Date: 15/03/2024", "15/03/2024"),
            ("Issue Date: 03-15-2024", "03-15-2024"),
            ("Date: 15 Mar 2024", "15 Mar 2024"),
            ("March 15, 2024", "March 15, 2024"),
            ("15 March 2024", "15 March 2024"),
            ("Dec 25, 2023", "Dec 25, 2023"),
            ("25 December 2023", "25 December 2023"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    assert expected in matches, f"Expected '{expected}' in matches {matches} for pattern {pattern}"
                    matched = True
                    break
            assert matched, f"No date pattern matched for text: {text}"
    
    def test_weight_pattern_matching(self, field_patterns):
        """Test weight pattern matching"""
        weight_patterns = field_patterns.get_patterns("weight_patterns")
        test_cases = [
            ("GROSS WEIGHT: 2,500 KG", "2,500 KG"),
            ("NET WEIGHT: 2,200 LBS", "2,200 LBS"),
            ("WEIGHT: 1,000 MT", "1,000 MT"),
            ("Gross Weight: 5000 TON", "5000 TON"),
            ("Net Weight: 3,456.78 KG", "3,456.78 KG"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in weight_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    assert expected in matches, f"Expected '{expected}' in matches {matches}"
                    matched = True
                    break
            assert matched, f"No weight pattern matched for text: {text}"
    
    def test_quantity_pattern_matching(self, field_patterns):
        """Test quantity pattern matching"""
        quantity_patterns = field_patterns.get_patterns("quantity_patterns")
        test_cases = [
            ("PACKAGES: 100", "100"),
            ("QUANTITY: 50", "50"),
            ("QTY: 25", "25"),
            ("Packages: 1,000", "1,000"),
            ("Quantity: 500", "500"),
        ]
        
        for text, expected in test_cases:
            matched = False
            for pattern in quantity_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    assert match.group(1).strip() == expected
                    matched = True
                    break
            assert matched, f"No quantity pattern matched for text: {text}"
    
    def test_pattern_completeness(self, field_patterns):
        """Test that all expected pattern categories are present and non-empty"""
        required_patterns = [
            "bol_number", "shipper", "consignee", "notify_party",
            "vessel", "voyage", "port_of_load", "port_of_discharge",
            "freight_terms", "date_patterns", "weight_patterns", "quantity_patterns"
        ]
        
        for pattern_type in required_patterns:
            patterns = field_patterns.get_patterns(pattern_type)
            assert len(patterns) > 0, f"Pattern type '{pattern_type}' should have at least one pattern"
            assert all(isinstance(p, str) for p in patterns), f"All patterns for '{pattern_type}' should be strings"
            assert all(len(p.strip()) > 0 for p in patterns), f"All patterns for '{pattern_type}' should be non-empty"
    
    def test_regex_pattern_validity(self, field_patterns):
        """Test that all regex patterns are valid and compilable"""
        for pattern_type, patterns in field_patterns.patterns.items():
            for i, pattern in enumerate(patterns):
                try:
                    re.compile(pattern)
                except re.error as e:
                    pytest.fail(f"Invalid regex pattern in {pattern_type}[{i}]: {pattern} - Error: {e}")
    
    def test_pattern_case_insensitivity(self, field_patterns):
        """Test that patterns work with case variations"""
        # Test BOL number with various cases
        bol_patterns = field_patterns.get_patterns("bol_number")
        test_texts = [
            "B/L NO: BOL123",
            "b/l no: bol123", 
            "B/l No: Bol123",
            "b/L number: BOL123"
        ]
        
        for text in test_texts:
            matched = False
            for pattern in bol_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    matched = True
                    break
            assert matched, f"No pattern matched case variation: {text}"