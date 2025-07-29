# BOL OCR Extractor - Testing Suite

This directory contains a comprehensive testing framework for the BOL OCR Extractor application, designed to ensure production-level quality, reliability, and performance.

## 🧪 Test Suite Overview

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Individual class and method testing
   - Mock-based isolation testing
   - Edge case validation
   - Coverage: All core classes (PDFProcessor, BOLDataExtractor, etc.)

2. **Integration Tests** (`tests/integration/`)
   - End-to-end workflow testing
   - Component interaction validation
   - File processing pipelines
   - Export functionality integration

3. **Performance Tests** (`tests/performance/`)
   - Speed benchmarking
   - Memory usage monitoring
   - Scalability testing
   - Concurrent processing validation

4. **Accuracy Validation**
   - Synthetic test data with ground truth
   - Extraction accuracy calculation
   - Quality metrics analysis
   - Success criteria evaluation

## 🚀 Quick Start

### Prerequisites

Install testing dependencies:
```bash
pip install -r test_requirements.txt
```

### Running Tests

#### Complete Test Suite
```bash
# Run all tests with coverage analysis
python tests/run_tests.py

# Quick test run (skip slow tests)
python tests/run_tests.py --quick

# Verbose output
python tests/run_tests.py --verbose
```

#### Individual Test Categories
```bash
# Unit tests only
python tests/run_tests.py --unit-only

# Integration tests only
python tests/run_tests.py --integration-only

# Performance tests only
python tests/run_tests.py --performance-only

# Coverage analysis only
python tests/run_tests.py --coverage-only

# Accuracy validation only
python tests/run_tests.py --accuracy-only
```

#### Using pytest directly
```bash
# Run specific test file
pytest tests/unit/test_pdf_processor.py -v

# Run with coverage
pytest tests/unit/ --cov=app --cov-report=html

# Run performance tests
pytest tests/performance/ -m performance
```

## 📊 Test Coverage & Quality Metrics

### Coverage Targets
- **Overall Coverage**: ≥80%
- **Unit Test Coverage**: ≥90% for core classes
- **Integration Coverage**: ≥70% for workflows

### Accuracy Targets
- **BOL Number Extraction**: ≥95%
- **Shipper/Consignee Names**: ≥85%
- **Vessel Information**: ≥80%
- **Overall Field Accuracy**: ≥80%

### Performance Targets
- **Text-based Processing**: <5 seconds per file
- **OCR Processing**: <45 seconds per file
- **Batch Processing**: <1 second per file overhead
- **Memory Usage**: <100MB per 50 files

## 🏗️ Test Framework Architecture

### Directory Structure
```
tests/
├── conftest.py                 # Global fixtures and configuration
├── run_tests.py               # Comprehensive test runner
├── README.md                  # This documentation
├── unit/                      # Unit tests
│   ├── test_pdf_processor.py
│   ├── test_bol_extractor.py
│   ├── test_field_patterns.py
│   ├── test_table_parser.py
│   └── test_excel_exporter.py
├── integration/               # Integration tests
│   ├── test_end_to_end.py
│   └── test_component_integration.py
├── performance/               # Performance tests
│   ├── test_extraction_performance.py
│   └── test_memory_usage.py
├── utils/                     # Testing utilities
│   ├── synthetic_data_generator.py
│   ├── accuracy_calculator.py
│   └── test_helpers.py
└── fixtures/                  # Test data and fixtures
    ├── synthetic_dataset/
    ├── edge_cases/
    └── sample_pdfs/
```

### Key Components

#### 1. Synthetic Data Generator
- Creates realistic BOL PDFs with known ground truth
- Generates various formats and quality levels
- Supports edge cases and error scenarios
- Configurable layouts and content

#### 2. Accuracy Calculator
- Fuzzy string matching for field comparison
- Weighted accuracy scoring by field importance
- Category-based performance analysis
- Success criteria evaluation

#### 3. Performance Monitor
- Memory usage tracking
- Execution time benchmarking
- Concurrent processing testing
- Resource leak detection

## 📋 Test Data Management

### Synthetic Test Data

The testing framework includes a sophisticated synthetic data generator that creates realistic BOL PDFs:

```python
from tests.utils.synthetic_data_generator import SyntheticBOLGenerator

# Generate test dataset
generator = SyntheticBOLGenerator()
dataset = generator.generate_test_dataset(count=50, output_dir="test_data")
```

### Data Categories

1. **Standard BOLs**: Regular format, high quality
2. **Edge Cases**: Missing fields, special characters
3. **Performance Data**: Large batches for scalability testing
4. **Quality Variations**: Different scan qualities and formats

### Ground Truth Data

All synthetic PDFs come with corresponding ground truth JSON files:

```json
{
  "filename": "synthetic_bol_TEST0001.pdf",
  "bol_number": "TEST0001",
  "shipper_name": "ABC Shipping Lines Ltd",
  "consignee_name": "Import Solutions International",
  "vessel_name": "MV Ocean Pioneer",
  ...
}
```

## 🔍 Accuracy Testing

### Validation Process

1. **Generate Synthetic Data**: Create BOLs with known ground truth
2. **Process with OCR**: Extract data using the application
3. **Calculate Accuracy**: Compare extracted vs. expected data
4. **Evaluate Criteria**: Check against success thresholds
5. **Generate Report**: Detailed accuracy analysis

### Accuracy Metrics

- **Exact Match**: Character-for-character accuracy
- **Normalized Match**: Case and whitespace insensitive
- **Fuzzy Match**: Similarity-based scoring (60-100%)
- **Numeric Accuracy**: Percentage-based for weights/quantities

### Success Criteria

```python
SUCCESS_CRITERIA = {
    'field_accuracy_targets': {
        'bol_number': 0.95,      # 95% accuracy
        'shipper_name': 0.85,    # 85% accuracy
        'consignee_name': 0.85,  # 85% accuracy
        'overall_accuracy': 0.80  # 80% overall
    },
    'success_rate_targets': {
        'acceptable_rate': 0.90,  # 90% of docs ≥70% accurate
        'good_rate': 0.70,        # 70% of docs ≥85% accurate
        'failure_rate': 0.05      # <5% extraction failures
    }
}
```

## 🚄 Performance Testing

### Benchmarking Categories

1. **Speed Tests**
   - Text extraction time
   - Data parsing performance
   - Export generation speed

2. **Memory Tests**
   - Single file processing
   - Batch processing memory usage
   - Memory leak detection

3. **Scalability Tests**
   - Batch size performance
   - Concurrent processing
   - Resource utilization

### Performance Markers

Tests are marked for different execution contexts:

```python
@pytest.mark.performance  # Performance tests
@pytest.mark.slow         # Long-running tests
@pytest.mark.unit         # Unit tests
@pytest.mark.integration  # Integration tests
```

## 📈 Continuous Integration

### Test Automation

The test suite is designed for CI/CD integration:

```bash
# CI-friendly test execution
python tests/run_tests.py --quick --skip-accuracy

# Generate coverage reports for CI
pytest --cov=app --cov-report=xml --cov-report=term
```

### Quality Gates

Automated quality checks include:
- Minimum test coverage (80%)
- Performance regression detection
- Accuracy threshold validation
- Code quality metrics

## 🛠️ Development Workflow

### Adding New Tests

1. **Unit Tests**: Test individual methods/classes
```python
def test_new_feature(self, extractor):
    result = extractor.new_method("test input")
    assert result == "expected output"
```

2. **Integration Tests**: Test component interactions
```python
def test_workflow_integration(self, app):
    result = app.process_complete_workflow(test_data)
    assert result.extraction_success
```

3. **Performance Tests**: Benchmark new features
```python
@pytest.mark.performance
def test_new_feature_performance(self):
    start_time = time.time()
    # ... test code ...
    assert (time.time() - start_time) < threshold
```

### Test Data Management

- Store sample PDFs in `tests/fixtures/sample_pdfs/`
- Update ground truth data for accuracy tests
- Version control test data configurations
- Document expected behaviors

## 🐛 Debugging Tests

### Common Issues

1. **Import Errors**: Ensure proper Python path configuration
2. **Missing Dependencies**: Install all test requirements
3. **Data Path Issues**: Use absolute paths in fixtures
4. **Mock Failures**: Verify mock configurations match actual APIs

### Debug Tools

```bash
# Run single test with detailed output
pytest tests/unit/test_pdf_processor.py::TestPDFProcessor::test_specific_method -v -s

# Debug with coverage
pytest --cov=app --cov-report=html tests/unit/test_pdf_processor.py

# Profile performance
pytest --benchmark-only tests/performance/
```

## 📚 Additional Resources

### Documentation
- [Testing Strategy Document](../QA_TESTING_STRATEGY.md)
- [Application README](../README.md)
- [Development Guide](../CLAUDE.md)

### External Tools
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [ReportLab PDF Generation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

## 🤝 Contributing to Tests

### Guidelines

1. **Test Naming**: Use descriptive test names that explain the scenario
2. **Test Structure**: Follow Arrange-Act-Assert pattern
3. **Mock Usage**: Mock external dependencies, test internal logic
4. **Documentation**: Document complex test scenarios
5. **Performance**: Mark performance-sensitive tests appropriately

### Review Checklist

- [ ] Tests cover both success and failure cases
- [ ] Mocks are properly configured and verified
- [ ] Test data is realistic and comprehensive
- [ ] Performance tests have reasonable thresholds
- [ ] Documentation is updated for new test categories

---

**Ready to ensure your BOL OCR Extractor is production-ready? Run the comprehensive test suite and validate your implementation!**

```bash
python tests/run_tests.py --verbose
```