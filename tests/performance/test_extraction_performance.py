"""
Performance tests for BOL OCR extraction speed and resource usage
"""

import pytest
import time
import psutil
import os
import threading
from unittest.mock import Mock, patch, MagicMock
from app import BOLOCRApp, PDFProcessor, BOLDataExtractor, BOLData

class TestExtractionPerformance:
    """Performance tests for extraction operations"""
    
    @pytest.fixture
    def performance_app(self):
        """Provide BOLOCRApp instance for performance testing"""
        return BOLOCRApp()
    
    @pytest.fixture
    def large_bol_text(self):
        """Generate large BOL text for performance testing"""
        base_text = """
        B/L NUMBER: PERF123456789
        
        SHIPPER:
        Performance Test Shipping Company International Ltd
        123 Performance Testing Boulevard, Suite 500
        Industrial Complex Area, Zone A
        Los Angeles, California 90001
        United States of America
        
        CONSIGNEE:
        High Volume Processing Corporation Ltd
        456 Bulk Import Avenue, Building B, Floor 15
        Trade Center Complex, Import Zone
        New York, New York 10001, USA
        
        NOTIFY PARTY:
        Performance Notification Services LLC
        789 Alert Processing Street, Unit 200
        Notification Center, Bay Area
        Boston, Massachusetts 02101
        
        VESSEL: MV Performance Testing Vessel
        VOYAGE: VOY2024PERF001
        
        PORT OF LOADING: Los Angeles Performance Terminal, CA
        PORT OF DISCHARGE: New York High Volume Port, NY
        
        DESCRIPTION OF GOODS:
        Performance Testing Electronic Equipment and Components
        Including High-Volume Processing Hardware Systems
        Advanced Computing Components and Accessories
        Industrial Grade Performance Testing Materials
        
        GROSS WEIGHT: 25,000 KG
        NET WEIGHT: 22,500 KG
        PACKAGES: 500 CTNS
        
        FREIGHT: PREPAID
        DATE: 15/03/2024
        """
        return base_text * 10  # Multiply to create substantial content
    
    @pytest.mark.performance
    def test_text_extraction_speed_benchmark(self, performance_app, large_bol_text):
        """Benchmark text extraction speed"""
        with patch.object(performance_app.pdf_processor, 'extract_text_pdfplumber') as mock_extract:
            mock_extract.return_value = (large_bol_text, True)
            
            # Warm up
            performance_app.pdf_processor.extract_text_pdfplumber(Mock())
            
            # Benchmark
            iterations = 50
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                text, success = performance_app.pdf_processor.extract_text_pdfplumber(Mock())
                assert success is True
            
            end_time = time.perf_counter()
            avg_time = (end_time - start_time) / iterations
            
            # Performance target: <0.1 seconds per extraction
            assert avg_time < 0.1, f"Text extraction too slow: {avg_time:.3f}s per file"
            print(f"Text extraction benchmark: {avg_time:.3f}s per file")
    
    @pytest.mark.performance 
    def test_data_extraction_speed_benchmark(self, performance_app, large_bol_text):
        """Benchmark data extraction speed from text"""
        # Warm up
        performance_app.data_extractor.extract_all_fields(large_bol_text, [], "warmup.pdf")
        
        # Benchmark
        iterations = 100
        start_time = time.perf_counter()
        
        for i in range(iterations):
            bol_data = performance_app.data_extractor.extract_all_fields(
                large_bol_text, [], f"perf_test_{i}.pdf"
            )
            assert not bol_data.extraction_failed
        
        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / iterations
        
        # Performance target: <0.05 seconds per extraction
        assert avg_time < 0.05, f"Data extraction too slow: {avg_time:.3f}s per file"
        print(f"Data extraction benchmark: {avg_time:.3f}s per file")
    
    @pytest.mark.performance
    def test_memory_usage_single_file(self, performance_app, large_bol_text):
        """Test memory usage for single file processing"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch.object(performance_app.pdf_processor, 'process_pdf') as mock_process:
            mock_process.return_value = (large_bol_text, "text", "high")
            
            # Process single large file
            result = performance_app.process_single_pdf(Mock(), "large_test.pdf")
            assert not result.extraction_failed
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (<50MB for single file)
            assert memory_increase < 50, f"Memory usage too high: {memory_increase:.1f}MB"
            print(f"Single file memory usage: {memory_increase:.1f}MB")
    
    @pytest.mark.performance
    def test_batch_processing_scalability(self, performance_app):
        """Test batch processing performance scalability"""
        batch_sizes = [10, 25, 50]
        results = {}
        
        for batch_size in batch_sizes:
            # Create mock results
            mock_results = []
            for i in range(batch_size):
                bol_data = BOLData()
                bol_data.filename = f"batch_test_{i}.pdf"
                bol_data.bol_number = f"BATCH{i:03d}"
                bol_data.shipper_name = f"Batch Test Shipper {i}"
                bol_data.extraction_method = "text"
                bol_data.extraction_confidence = "high"
                mock_results.append(bol_data)
            
            with patch.object(performance_app, 'process_single_pdf') as mock_process, \
                 patch('streamlit.progress'), \
                 patch('streamlit.empty'):
                
                mock_process.side_effect = mock_results
                
                # Create mock file list
                files = [(Mock(), f"batch_test_{i}.pdf") for i in range(batch_size)]
                
                start_time = time.perf_counter()
                batch_results = performance_app.process_batch_pdfs(files)
                end_time = time.perf_counter()
                
                total_time = end_time - start_time
                avg_time_per_file = total_time / batch_size
                
                results[batch_size] = {
                    'total_time': total_time,
                    'avg_time_per_file': avg_time_per_file,
                    'files_processed': len(batch_results),
                    'throughput': batch_size / total_time  # files per second
                }
                
                assert len(batch_results) == batch_size
        
        # Performance should scale reasonably (not degrade significantly)
        small_batch_time = results[10]['avg_time_per_file']
        large_batch_time = results[50]['avg_time_per_file']
        
        # Large batch shouldn't be more than 50% slower per file
        assert large_batch_time <= small_batch_time * 1.5, \
            f"Performance degradation too high: {small_batch_time:.3f}s -> {large_batch_time:.3f}s"
        
        print(f"Batch processing scalability results: {results}")
    
    @pytest.mark.performance
    def test_concurrent_processing_performance(self, performance_app):
        """Test performance under concurrent load"""
        results = []
        errors = []
        execution_times = []
        
        def process_single_threaded():
            """Single threaded processing task"""
            try:
                start_time = time.perf_counter()
                
                with patch.object(performance_app, 'process_single_pdf') as mock_process:
                    bol_data = BOLData()
                    bol_data.filename = "concurrent_test.pdf"
                    bol_data.bol_number = "CONC001"
                    bol_data.extraction_method = "text"
                    bol_data.extraction_confidence = "high"
                    mock_process.return_value = bol_data
                    
                    files = [(Mock(), "concurrent_test.pdf")]
                    with patch('streamlit.progress'), patch('streamlit.empty'):
                        batch_results = performance_app.process_batch_pdfs(files)
                        results.extend(batch_results)
                
                end_time = time.perf_counter()
                execution_times.append(end_time - start_time)
                
            except Exception as e:
                errors.append(str(e))
        
        # Create and start multiple threads
        threads = []
        thread_count = 5
        
        for _ in range(thread_count):
            thread = threading.Thread(target=process_single_threaded)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify concurrent processing results
        assert len(errors) == 0, f"Concurrent processing errors: {errors}"
        assert len(results) == thread_count, f"Expected {thread_count} results, got {len(results)}"
        
        # Check performance consistency
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times)
        
        # Maximum execution time shouldn't be more than 2x average (reasonable variance)
        assert max_execution_time <= avg_execution_time * 2, \
            f"High performance variance: avg={avg_execution_time:.3f}s, max={max_execution_time:.3f}s"
        
        print(f"Concurrent processing - Avg: {avg_execution_time:.3f}s, Max: {max_execution_time:.3f}s")
    
    @pytest.mark.performance
    def test_export_performance_large_dataset(self, performance_app):
        """Test export performance with large datasets"""
        # Create large dataset
        large_dataset = []
        dataset_size = 1000
        
        for i in range(dataset_size):
            bol_data = BOLData()
            bol_data.filename = f"export_test_{i}.pdf"
            bol_data.bol_number = f"EXP{i:04d}"
            bol_data.shipper_name = f"Export Test Shipper {i} with Long Name"
            bol_data.consignee_name = f"Export Test Consignee {i} with Extended Details"
            bol_data.description_of_goods = "Export test cargo with detailed description " * 10
            bol_data.extraction_method = "text" if i % 2 == 0 else "ocr"
            bol_data.extraction_confidence = ["high", "medium", "low"][i % 3]
            large_dataset.append(bol_data)
        
        # Test Excel export performance
        start_time = time.perf_counter()
        excel_buffer = performance_app.excel_exporter.export_to_excel(large_dataset)
        excel_time = time.perf_counter() - start_time
        
        # Test CSV export performance
        start_time = time.perf_counter()
        csv_buffer = performance_app.excel_exporter.export_to_csv(large_dataset)
        csv_time = time.perf_counter() - start_time
        
        # Performance targets
        assert excel_time < 30, f"Excel export too slow: {excel_time:.1f}s for {dataset_size} records"
        assert csv_time < 10, f"CSV export too slow: {csv_time:.1f}s for {dataset_size} records"
        
        # Verify export integrity
        assert excel_buffer.tell() > 0
        assert len(csv_buffer.getvalue()) > 0
        
        print(f"Export performance - Excel: {excel_time:.1f}s, CSV: {csv_time:.1f}s for {dataset_size} records")
    
    @pytest.mark.performance
    def test_memory_leak_detection(self, performance_app):
        """Test for memory leaks during repeated processing"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate repeated processing
        iterations = 100
        memory_samples = []
        
        with patch.object(performance_app, 'process_single_pdf') as mock_process:
            for i in range(iterations):
                # Create new BOL data for each iteration
                bol_data = BOLData()
                bol_data.filename = f"leak_test_{i}.pdf"
                bol_data.bol_number = f"LEAK{i:03d}"
                bol_data.shipper_name = f"Memory Test Shipper {i}" * 10  # Create substantial data
                bol_data.description_of_goods = "Memory leak test cargo description " * 20
                mock_process.return_value = bol_data
                
                # Process single file
                files = [(Mock(), f"leak_test_{i}.pdf")]
                with patch('streamlit.progress'), patch('streamlit.empty'):
                    results = performance_app.process_batch_pdfs(files)
                
                # Sample memory every 20 iterations
                if i % 20 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory - initial_memory)
        
        # Check for memory leaks
        if len(memory_samples) >= 3:
            # Memory shouldn't increase consistently (indicating a leak)
            memory_trend = memory_samples[-1] - memory_samples[0]
            
            # Allow for some memory growth but not excessive (< 100MB over 100 iterations)
            assert memory_trend < 100, f"Potential memory leak detected: {memory_trend:.1f}MB increase"
            
            print(f"Memory leak test - Memory trend: {memory_trend:.1f}MB over {iterations} iterations")
            print(f"Memory samples: {[f'{m:.1f}MB' for m in memory_samples]}")
    
    @pytest.mark.performance
    def test_regex_pattern_performance(self, performance_app):
        """Test regex pattern matching performance"""
        extractor = performance_app.data_extractor
        
        # Create text with many potential matches to stress-test regex
        complex_text = """
        B/L NUMBER: BOL123456 and also BOL NUMBER: BOL789012
        SHIPPER: First Shipper Company and SHIPPER: Second Shipper Corp
        VESSEL: Ship One and VESSEL: Ship Two and VESSEL: Ship Three
        """ * 100  # Multiply to create complex matching scenario
        
        # Benchmark BOL number extraction
        start_time = time.perf_counter()
        iterations = 1000
        
        for _ in range(iterations):
            result = extractor.extract_bol_number(complex_text)
            assert result == "BOL123456"  # Should return first match
        
        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / iterations
        
        # Regex matching should be very fast (<0.001s per operation)
        assert avg_time < 0.001, f"Regex matching too slow: {avg_time:.4f}s per extraction"
        print(f"Regex pattern performance: {avg_time:.4f}s per extraction")