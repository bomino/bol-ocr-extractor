"""
Unit tests for PDFProcessor class
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import io
from app import PDFProcessor, BOLData

class TestPDFProcessor:
    """Test suite for PDFProcessor class"""
    
    def test_init(self, pdf_processor):
        """Test PDFProcessor initialization"""
        assert pdf_processor.min_text_threshold == 100
        assert isinstance(pdf_processor.min_text_threshold, int)
    
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
            mock_open.assert_called_once_with(mock_pdf_file)
    
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
            assert text.strip() == "Short"
    
    def test_extract_text_pdfplumber_empty_pages(self, pdf_processor, mock_pdf_file):
        """Test handling of PDFs with empty pages"""
        with patch('pdfplumber.open') as mock_open:
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = None
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            text, success = pdf_processor.extract_text_pdfplumber(mock_pdf_file)
            
            assert success is False
            assert text == ""
    
    def test_extract_text_pdfplumber_multiple_pages(self, pdf_processor, mock_pdf_file):
        """Test text extraction from multiple pages"""
        with patch('pdfplumber.open') as mock_open:
            mock_pdf = Mock()
            mock_page1 = Mock()
            mock_page1.extract_text.return_value = "Page 1 content " * 10
            mock_page2 = Mock()
            mock_page2.extract_text.return_value = "Page 2 content " * 10
            mock_pdf.pages = [mock_page1, mock_page2]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            text, success = pdf_processor.extract_text_pdfplumber(mock_pdf_file)
            
            assert success is True
            assert "Page 1 content" in text
            assert "Page 2 content" in text
            assert text.count('\n') >= 1  # Pages separated by newlines
    
    def test_extract_text_pdfplumber_exception(self, pdf_processor, mock_pdf_file):
        """Test error handling in text extraction"""
        with patch('pdfplumber.open') as mock_open:
            mock_open.side_effect = Exception("PDF parsing error")
            
            text, success = pdf_processor.extract_text_pdfplumber(mock_pdf_file)
            
            assert success is False
            assert text == ""
    
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
    
    def test_extract_text_ocr_insufficient_content(self, pdf_processor, mock_pdf_file):
        """Test OCR with insufficient extracted content"""
        with patch('pdfplumber.open') as mock_open, \
             patch('pytesseract.image_to_string') as mock_ocr:
            mock_pdf = Mock()
            mock_page = Mock()
            mock_image = Mock()
            mock_image.original = Mock()
            mock_page.to_image.return_value = mock_image
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            mock_ocr.return_value = "Short"  # <100 chars
            
            text, success = pdf_processor.extract_text_ocr(mock_pdf_file)
            
            assert success is False
            assert text.strip() == "Short"
    
    def test_extract_text_ocr_exception(self, pdf_processor, mock_pdf_file):
        """Test error handling in OCR extraction"""
        with patch('pdfplumber.open') as mock_open:
            mock_open.side_effect = Exception("OCR processing error")
            
            text, success = pdf_processor.extract_text_ocr(mock_pdf_file)
            
            assert success is False
            assert text == ""
    
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
    
    def test_assess_text_quality_medium_structured(self, pdf_processor):
        """Test text quality assessment - medium quality with structure"""
        text = "SHIPPER: Some company with basic structure\n" * 10
        quality = pdf_processor.assess_text_quality(text)
        assert quality == "medium"
    
    def test_assess_text_quality_medium_keywords(self, pdf_processor):
        """Test text quality assessment - medium quality with keywords only"""
        text = "This document contains VESSEL information and BOL details"
        quality = pdf_processor.assess_text_quality(text)
        assert quality == "medium"
    
    def test_assess_text_quality_low(self, pdf_processor):
        """Test text quality assessment - low quality"""
        text = "Short text without structure"
        quality = pdf_processor.assess_text_quality(text)
        assert quality == "low"
    
    def test_assess_text_quality_very_short(self, pdf_processor):
        """Test text quality assessment - very short text"""
        text = "Short"
        quality = pdf_processor.assess_text_quality(text)
        assert quality == "low"
    
    def test_process_pdf_text_success(self, pdf_processor, mock_pdf_file):
        """Test successful text-based PDF processing"""
        with patch.object(pdf_processor, 'extract_text_pdfplumber') as mock_text, \
             patch.object(pdf_processor, 'assess_text_quality') as mock_quality:
            
            mock_text.return_value = ("Good quality BOL text " * 20, True)
            mock_quality.return_value = "high"
            
            text, method, confidence = pdf_processor.process_pdf(mock_pdf_file, "test.pdf")
            
            assert method == "text"
            assert confidence == "high"
            assert "Good quality BOL text" in text
            mock_text.assert_called_once()
    
    def test_process_pdf_fallback_to_ocr(self, pdf_processor, mock_pdf_file):
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
    
    def test_process_pdf_fallback_low_quality(self, pdf_processor, mock_pdf_file):
        """Test fallback to OCR due to low quality text"""
        with patch.object(pdf_processor, 'extract_text_pdfplumber') as mock_text, \
             patch.object(pdf_processor, 'extract_text_ocr') as mock_ocr, \
             patch.object(pdf_processor, 'assess_text_quality') as mock_quality:
            
            # Text extraction returns sufficient content but low quality
            mock_text.return_value = ("Low quality text " * 20, True)
            mock_ocr.return_value = ("Better OCR content " * 20, True)
            mock_quality.side_effect = ["low", "medium"]
            
            text, method, confidence = pdf_processor.process_pdf(mock_pdf_file, "test.pdf")
            
            assert method == "ocr"
            assert confidence == "medium"
            assert "Better OCR content" in text
    
    def test_process_pdf_ocr_fails_use_original(self, pdf_processor, mock_pdf_file):
        """Test using original text when OCR fails"""
        with patch.object(pdf_processor, 'extract_text_pdfplumber') as mock_text, \
             patch.object(pdf_processor, 'extract_text_ocr') as mock_ocr, \
             patch.object(pdf_processor, 'assess_text_quality') as mock_quality:
            
            # Text extraction low quality, OCR fails
            mock_text.return_value = ("Some text " * 20, True)
            mock_ocr.return_value = ("", False)
            mock_quality.side_effect = ["low", "low"]
            
            text, method, confidence = pdf_processor.process_pdf(mock_pdf_file, "test.pdf")
            
            assert method == "text_fallback"
            assert confidence == "low"
            assert "Some text" in text
    
    def test_process_pdf_both_fail(self, pdf_processor, mock_pdf_file):
        """Test when both text extraction and OCR fail"""
        with patch.object(pdf_processor, 'extract_text_pdfplumber') as mock_text, \
             patch.object(pdf_processor, 'extract_text_ocr') as mock_ocr, \
             patch.object(pdf_processor, 'assess_text_quality') as mock_quality:
            
            # Both methods fail
            mock_text.return_value = ("", False)
            mock_ocr.return_value = ("", False)
            mock_quality.return_value = "low"
            
            text, method, confidence = pdf_processor.process_pdf(mock_pdf_file, "test.pdf")
            
            assert method == "ocr"  # Still reports OCR as method tried
            assert confidence == "low"
            assert text == ""
    
    def test_min_text_threshold_adjustment(self, pdf_processor, mock_pdf_file):
        """Test that min_text_threshold can be adjusted"""
        # Change threshold
        pdf_processor.min_text_threshold = 50
        
        with patch('pdfplumber.open') as mock_open:
            mock_pdf = Mock()
            mock_page = Mock()
            mock_page.extract_text.return_value = "Medium text content"  # ~50 chars
            mock_pdf.pages = [mock_page]
            mock_open.return_value.__enter__.return_value = mock_pdf
            
            text, success = pdf_processor.extract_text_pdfplumber(mock_pdf_file)
            
            assert success is True  # Should pass with lower threshold
            assert len(text.strip()) >= 50