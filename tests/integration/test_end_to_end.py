"""
Integration tests for end-to-end BOL OCR workflows
"""

import pytest
import tempfile
import os
import io
from unittest.mock import patch, Mock, MagicMock
import pandas as pd
from app import BOLOCRApp, PDFProcessor, BOLDataExtractor, ExcelExporter, BOLData

class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    @pytest.fixture
    def app(self):
        """Provide BOLOCRApp instance for testing"""
        return BOLOCRApp()
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF content for testing"""
        return b"Sample PDF content for testing purposes"
    
    def test_complete_text_extraction_workflow(self, app, sample_pdf_content, sample_bol_text):
        """Test complete workflow for text-based PDF processing"""
        with patch.object(app.pdf_processor, 'process_pdf') as mock_process, \
             patch.object(app.table_parser, 'extract_tables') as mock_tables, \
             patch.object(app.data_extractor, 'extract_all_fields') as mock_extract:
            
            # Mock successful text extraction
            mock_process.return_value = (sample_bol_text, "text", "high")
            mock_tables.return_value = []
            
            # Mock BOL data extraction
            expected_bol_data = BOLData()
            expected_bol_data.filename = "test.pdf"
            expected_bol_data.bol_number = "BOL123456789"
            expected_bol_data.shipper_name = "ABC Shipping Company"
            expected_bol_data.consignee_name = "XYZ Import Corp"
            expected_bol_data.vessel_name = "MV Ocean Carrier"
            expected_bol_data.extraction_method = "text"
            expected_bol_data.extraction_confidence = "high"
            mock_extract.return_value = expected_bol_data
            
            # Process single PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(sample_pdf_content)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as pdf_file:
                    result = app.process_single_pdf(pdf_file, "test.pdf")
                
                os.unlink(tmp_file.name)
            
            # Verify results
            assert result.filename == "test.pdf"
            assert result.bol_number == "BOL123456789"
            assert result.shipper_name == "ABC Shipping Company"
            assert result.consignee_name == "XYZ Import Corp"
            assert result.vessel_name == "MV Ocean Carrier"
            assert result.extraction_method == "text"
            assert result.extraction_confidence == "high"
            assert not result.extraction_failed
            
            # Verify all components were called correctly
            mock_process.assert_called_once()
            mock_tables.assert_called_once()
            mock_extract.assert_called_once()
    
    def test_complete_ocr_fallback_workflow(self, app, sample_pdf_content):
        """Test complete workflow with OCR fallback"""
        ocr_text = """
        B/L NUMBER: SCN456789
        SHIPPER: OCR Extracted Shipper
        CONSIGNEE: OCR Extracted Consignee
        VESSEL: OCR Ship Name
        """
        
        with patch.object(app.pdf_processor, 'process_pdf') as mock_process, \
             patch.object(app.table_parser, 'extract_tables') as mock_tables, \
             patch.object(app.data_extractor, 'extract_all_fields') as mock_extract:
            
            # Mock OCR extraction (text extraction failed)
            mock_process.return_value = (ocr_text, "ocr", "medium")
            mock_tables.return_value = []
            
            expected_bol_data = BOLData()
            expected_bol_data.filename = "test_scanned.pdf"
            expected_bol_data.bol_number = "SCN456789"
            expected_bol_data.shipper_name = "OCR Extracted Shipper"
            expected_bol_data.consignee_name = "OCR Extracted Consignee"
            expected_bol_data.vessel_name = "OCR Ship Name"
            expected_bol_data.extraction_method = "ocr"
            expected_bol_data.extraction_confidence = "medium"
            mock_extract.return_value = expected_bol_data
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(sample_pdf_content)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as pdf_file:
                    result = app.process_single_pdf(pdf_file, "test_scanned.pdf")
                
                os.unlink(tmp_file.name)
            
            # Verify OCR workflow results
            assert result.filename == "test_scanned.pdf"
            assert result.bol_number == "SCN456789"
            assert result.extraction_method == "ocr"
            assert result.extraction_confidence == "medium"
            assert not result.extraction_failed
    
    def test_batch_processing_workflow(self, app, mock_streamlit):
        """Test batch processing of multiple PDFs"""
        # Create mock results for batch processing
        mock_results = []
        for i in range(3):
            bol_data = BOLData()
            bol_data.filename = f"test_{i}.pdf"
            bol_data.bol_number = f"BOL{i:03d}"
            bol_data.shipper_name = f"Test Shipper {i}"
            bol_data.consignee_name = f"Test Consignee {i}"
            bol_data.extraction_method = "text"
            bol_data.extraction_confidence = "high"
            mock_results.append(bol_data)
        
        with patch.object(app, 'process_single_pdf') as mock_process:
            mock_process.side_effect = mock_results
            
            # Simulate file list
            files = [(f"mock_file_{i}", f"test_{i}.pdf") for i in range(3)]
            
            results = app.process_batch_pdfs(files)
            
            # Verify batch processing results
            assert len(results) == 3
            assert all(result.bol_number.startswith("BOL") for result in results)
            assert all(result.extraction_method == "text" for result in results)
            assert all(result.extraction_confidence == "high" for result in results)
            assert mock_process.call_count == 3
    
    def test_export_integration_excel(self, app, sample_bol_data):
        """Test integration between extraction and Excel export"""
        # Create test data list
        test_data = [sample_bol_data]
        
        # Test Excel export
        excel_buffer = app.excel_exporter.export_to_excel(test_data)
        assert excel_buffer.tell() > 0
        
        # Verify exported data structure
        excel_buffer.seek(0)
        df_main = pd.read_excel(excel_buffer, sheet_name='BOL_Data')
        df_summary = pd.read_excel(excel_buffer, sheet_name='Processing_Summary')
        
        # Verify main data
        assert len(df_main) == 1
        assert df_main.iloc[0]['bol_number'] == "BOL123456789"
        assert df_main.iloc[0]['shipper_name'] == "ABC Shipping Company"
        assert df_main.iloc[0]['consignee_name'] == "XYZ Import Corp"
        assert df_main.iloc[0]['extraction_method'] == "text"
        
        # Verify summary data
        assert 'Metric' in df_summary.columns
        assert 'Count' in df_summary.columns
        assert len(df_summary) > 0
    
    def test_export_integration_csv(self, app, sample_bol_data):
        """Test integration between extraction and CSV export"""
        test_data = [sample_bol_data]
        
        # Test CSV export
        csv_buffer = app.excel_exporter.export_to_csv(test_data)
        csv_content = csv_buffer.getvalue()
        
        # Verify CSV content
        assert len(csv_content) > 0
        assert "BOL123456789" in csv_content
        assert "ABC Shipping Company" in csv_content
        assert "XYZ Import Corp" in csv_content
        assert "text" in csv_content  # extraction_method
    
    def test_error_handling_workflow(self, app, sample_pdf_content):
        """Test error handling in complete workflow"""
        with patch.object(app.pdf_processor, 'process_pdf') as mock_process:
            # Mock processing error
            mock_process.side_effect = Exception("PDF processing failed")
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(sample_pdf_content)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as pdf_file:
                    result = app.process_single_pdf(pdf_file, "error_test.pdf")
                
                os.unlink(tmp_file.name)
            
            # Verify error handling
            assert result.filename == "error_test.pdf"
            assert result.extraction_failed is True
            assert "PDF processing failed" in result.processing_notes
    
    def test_table_extraction_integration(self, app, sample_pdf_content):
        """Test integration with table extraction"""
        # Mock table data
        mock_table = pd.DataFrame({
            'Description of Goods': ['Steel Products', 'Electronic Components'],
            'Quantity': ['100 MT', '50 BOXES'],
            'Weight': ['10000 KG', '500 KG']
        })
        
        with patch.object(app.pdf_processor, 'process_pdf') as mock_process, \
             patch.object(app.table_parser, 'extract_tables') as mock_tables, \
             patch.object(app.data_extractor, 'extract_all_fields') as mock_extract:
            
            mock_process.return_value = ("Basic BOL text", "text", "medium")
            mock_tables.return_value = [mock_table]
            
            # Mock extraction with table data
            bol_data = BOLData()
            bol_data.filename = "table_test.pdf"
            bol_data.bol_number = "TBL001"
            bol_data.description_of_goods = "Steel Products; Electronic Components"
            mock_extract.return_value = bol_data
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(sample_pdf_content)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as pdf_file:
                    result = app.process_single_pdf(pdf_file, "table_test.pdf")
                
                os.unlink(tmp_file.name)
            
            # Verify table integration
            assert result.filename == "table_test.pdf"
            assert result.bol_number == "TBL001"
            assert "Steel Products" in result.description_of_goods
            mock_tables.assert_called_once()
            mock_extract.assert_called_once()
    
    def test_mixed_quality_batch_processing(self, app):
        """Test batch processing with mixed quality results"""
        # Create mixed quality results
        mock_results = []
        
        # High quality text extraction
        bol1 = BOLData()
        bol1.filename = "high_quality.pdf"
        bol1.bol_number = "HQ001"
        bol1.extraction_method = "text"
        bol1.extraction_confidence = "high"
        mock_results.append(bol1)
        
        # Medium quality OCR
        bol2 = BOLData()
        bol2.filename = "medium_quality.pdf"
        bol2.bol_number = "MQ002"
        bol2.extraction_method = "ocr"
        bol2.extraction_confidence = "medium"
        mock_results.append(bol2)
        
        # Failed extraction
        bol3 = BOLData()
        bol3.filename = "failed.pdf"
        bol3.extraction_failed = True
        bol3.processing_notes = "Extraction failed"
        mock_results.append(bol3)
        
        with patch.object(app, 'process_single_pdf') as mock_process, \
             patch('streamlit.progress'), \
             patch('streamlit.empty'):
            
            mock_process.side_effect = mock_results
            
            files = [
                ("mock_high", "high_quality.pdf"),
                ("mock_medium", "medium_quality.pdf"),
                ("mock_failed", "failed.pdf")
            ]
            
            results = app.process_batch_pdfs(files)
            
            # Verify mixed results
            assert len(results) == 3
            
            # Check high quality result
            high_result = next(r for r in results if r.filename == "high_quality.pdf")
            assert high_result.bol_number == "HQ001"
            assert high_result.extraction_method == "text"
            assert high_result.extraction_confidence == "high"
            assert not high_result.extraction_failed
            
            # Check medium quality result
            medium_result = next(r for r in results if r.filename == "medium_quality.pdf")
            assert medium_result.bol_number == "MQ002"
            assert medium_result.extraction_method == "ocr"
            assert medium_result.extraction_confidence == "medium"
            assert not medium_result.extraction_failed
            
            # Check failed result
            failed_result = next(r for r in results if r.filename == "failed.pdf")
            assert failed_result.extraction_failed is True
            assert "Extraction failed" in failed_result.processing_notes
    
    def test_complete_workflow_with_export(self, app):
        """Test complete workflow from processing to export"""
        # Create realistic test data
        test_results = []
        for i in range(5):
            bol_data = BOLData()
            bol_data.filename = f"complete_test_{i}.pdf"
            bol_data.bol_number = f"CMP{i:03d}"
            bol_data.shipper_name = f"Complete Shipper {i}"
            bol_data.consignee_name = f"Complete Consignee {i}"
            bol_data.vessel_name = f"Complete Vessel {i}"
            bol_data.port_of_load = f"Port A{i}"
            bol_data.port_of_discharge = f"Port B{i}"
            bol_data.extraction_method = "text" if i % 2 == 0 else "ocr"
            bol_data.extraction_confidence = ["high", "medium", "low"][i % 3]
            test_results.append(bol_data)
        
        # Test export with complete data
        excel_buffer = app.excel_exporter.export_to_excel(test_results)
        csv_buffer = app.excel_exporter.export_to_csv(test_results)
        
        # Verify Excel export
        assert excel_buffer.tell() > 0
        excel_buffer.seek(0)
        df_main = pd.read_excel(excel_buffer, sheet_name='BOL_Data')
        df_summary = pd.read_excel(excel_buffer, sheet_name='Processing_Summary')
        
        assert len(df_main) == 5
        assert all(f"CMP{i:03d}" in df_main['bol_number'].values for i in range(5))
        
        # Verify CSV export
        csv_content = csv_buffer.getvalue()
        assert len(csv_content) > 0
        assert all(f"CMP{i:03d}" in csv_content for i in range(5))
        
        # Verify summary statistics
        summary_dict = dict(zip(df_summary['Metric'], df_summary['Count']))
        assert summary_dict['Total PDFs Processed'] == 5
        assert summary_dict['Text-based Extractions'] == 3  # Even indices
        assert summary_dict['OCR-based Extractions'] == 2   # Odd indices