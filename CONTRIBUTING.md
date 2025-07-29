# Contributing to BOL OCR Extractor

Thank you for your interest in contributing to the BOL OCR Extractor! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Security Considerations](#security-considerations)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- **Be Respectful**: Treat all contributors with respect and kindness
- **Be Inclusive**: Welcome contributors from all backgrounds and experience levels
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Professional**: Maintain a professional tone in all communications
- **Be Secure**: Never share sensitive data or credentials

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Docker (for containerized development)
- Tesseract OCR engine
- Java Runtime Environment (for table extraction)

### Fork and Clone
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/bol-ocr-extractor.git
   cd bol-ocr-extractor
   ```

## Development Environment

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Docker Development Setup
```bash
# Build development image
docker-compose -f docker-compose.yml build

# Run development environment
docker-compose -f docker-compose.yml up
```

### Testing Your Setup
```bash
# Run the test suite
python tests/run_tests.py --quick

# Run the application
streamlit run app.py
```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

#### 🐛 **Bug Reports**
- Use the bug report template
- Include detailed reproduction steps
- Provide sample data (anonymized) when possible
- Include system information and logs

#### ✨ **Feature Requests**
- Use the feature request template
- Describe the use case and business value
- Consider implementation complexity and compatibility

#### 🔧 **Code Contributions**
- Bug fixes
- New features
- Performance improvements
- Security enhancements
- Documentation improvements

#### 📚 **Documentation**
- User guide improvements
- API documentation
- Architecture documentation
- Tutorial creation

#### 🧪 **Testing**
- New test cases
- Test data creation
- Performance benchmarks
- Security testing

### Contribution Areas

#### **BOL Pattern Recognition**
Help improve extraction accuracy by contributing:
- New regex patterns for different BOL formats
- Field extraction logic improvements
- Support for additional shipping lines
- International format support

#### **Performance Optimization**
- Memory usage improvements
- Processing speed enhancements
- Scalability improvements
- Caching strategies

#### **Security Enhancements**
- Vulnerability fixes
- Security control implementations
- Compliance improvements
- Audit trail enhancements

#### **User Experience**
- UI/UX improvements
- Error message clarity
- Workflow optimizations
- Accessibility enhancements

## Pull Request Process

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow coding standards
- Add tests for new functionality
- Update documentation as needed
- Ensure security best practices

### 3. Test Your Changes
```bash
# Run full test suite
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --unit-only
python tests/run_tests.py --integration-only
python tests/run_tests.py --performance-only

# Run security checks
python tests/run_tests.py --security-checks
```

### 4. Update Documentation
- Update README.md if needed
- Add/update API documentation
- Update user guide for new features
- Include code comments for complex logic

### 5. Submit Pull Request
- Use the pull request template
- Provide clear description of changes
- Link related issues
- Include test results and screenshots
- Request appropriate reviewers

### 6. Address Review Comments
- Respond to all review comments
- Make requested changes
- Update tests if needed
- Ensure CI/CD pipeline passes

## Coding Standards

### Python Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Maximum line length: 88 characters (Black formatter)
- Use type hints where appropriate

```python
def extract_bol_number(self, text: str) -> str:
    """Extract Bill of Lading number from text.
    
    Args:
        text: Input text to search for BOL number
        
    Returns:
        Extracted BOL number or empty string if not found
    """
    return self.extract_field(text, "bol_number")
```

### Code Organization
- Keep functions focused and small (< 50 lines)
- Use classes for related functionality
- Separate concerns appropriately
- Follow single responsibility principle

### Error Handling
```python
try:
    result = process_pdf(pdf_file)
except PDFProcessingError as e:
    logger.error(f"PDF processing failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle gracefully
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning about potential issues")
logger.error("Error occurred but application continues")
logger.critical("Critical error requiring immediate attention")
```

## Testing Guidelines

### Test Coverage Requirements
- Minimum 80% code coverage for new code
- 100% coverage for critical security functions
- All public methods must have tests
- Integration tests for new features

### Test Types

#### **Unit Tests**
```python
def test_bol_number_extraction():
    """Test BOL number extraction with various formats."""
    extractor = BOLDataExtractor()
    
    test_cases = [
        ("B/L No: ABC123", "ABC123"),
        ("BOL#: XYZ789", "XYZ789"),
        ("Document Number: 123-456", "123-456"),
    ]
    
    for text, expected in test_cases:
        result = extractor.extract_bol_number(text)
        assert result == expected
```

#### **Integration Tests**
```python
def test_end_to_end_processing():
    """Test complete PDF processing workflow."""
    # Test with sample PDF
    result = process_pdf("tests/data/sample_bol.pdf")
    
    # Validate results
    assert result.bol_number is not None
    assert result.extraction_method in ["text", "ocr"]
    assert not result.extraction_failed
```

#### **Performance Tests**
```python
def test_processing_performance():
    """Test processing performance benchmarks."""
    start_time = time.time()
    
    # Process test file
    result = process_pdf("tests/data/large_bol.pdf")
    
    processing_time = time.time() - start_time
    assert processing_time < 30  # Should complete within 30 seconds
```

### Test Data
- Use anonymized BOL documents for testing
- Create synthetic test data when real data isn't available
- Include edge cases and error conditions
- Test with various BOL formats and qualities

## Security Considerations

### Secure Coding Practices
- **Input Validation**: Validate all inputs
- **Output Encoding**: Encode outputs appropriately
- **Error Handling**: Don't expose sensitive information in errors
- **Logging**: Don't log sensitive data

### Security Testing
- Run security scans on all changes
- Test for common vulnerabilities (OWASP Top 10)
- Validate input sanitization
- Test access controls

### Data Handling
- Never commit sensitive data
- Use environment variables for configuration
- Implement data minimization principles
- Follow data retention policies

### Example Secure Code
```python
def validate_pdf_file(file_data: bytes) -> bool:
    """Validate PDF file securely."""
    # Check file signature
    if not file_data.startswith(b'%PDF-'):
        raise ValueError("Invalid PDF file format")
    
    # Check file size
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Additional security checks
    scan_for_malicious_content(file_data)
    
    return True
```

## Documentation

### Code Documentation
- Document all public APIs
- Include docstrings for classes and methods
- Provide examples for complex functionality
- Keep documentation up-to-date with code changes

### README Updates
Update README.md for:
- New features or capabilities
- Changed installation requirements
- Updated usage instructions
- New configuration options

### User Guide Updates
Update user documentation for:
- New user-facing features
- Changed workflows
- New best practices
- Troubleshooting information

## Development Workflow

### Branch Naming Conventions
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `security/description` - Security improvements
- `docs/description` - Documentation updates
- `performance/description` - Performance improvements

### Commit Message Format
```
type(scope): brief description

Longer description if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Release Process
1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag release in Git
5. Deploy to staging
6. Run full test suite
7. Deploy to production

## Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community support
- **Security Issues**: Use private security reporting

### Getting Help
- Check existing documentation
- Search GitHub issues
- Create new issue if needed
- Tag appropriate reviewers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Annual contributor appreciation

## Questions?

If you have questions about contributing, please:
1. Check this document
2. Search existing issues
3. Create a new issue with the question label
4. Contact the maintainers

Thank you for contributing to the BOL OCR Extractor! 🚢