# BOL OCR Extractor - Developer Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Code Architecture](#code-architecture)
4. [Development Workflow](#development-workflow)
5. [Testing Framework](#testing-framework)
6. [Performance Optimization](#performance-optimization)
7. [Contributing Guidelines](#contributing-guidelines)
8. [Deployment Process](#deployment-process)

## Development Environment Setup

### Prerequisites

#### System Requirements
- **Python**: 3.8 or higher (3.11 recommended)
- **Node.js**: 16+ (for build tools and CI/CD)
- **Git**: Latest version
- **Docker**: 20.10+ (for containerized development)
- **Kubernetes**: kubectl configured (for deployment testing)

#### External Dependencies
- **Tesseract OCR**: System-level OCR engine installation
- **Java Runtime**: Required for tabula-py table extraction
- **Redis**: Optional, for caching and session management

### Local Development Setup

#### 1. Clone and Initialize Repository

```bash
# Clone the repository
git clone https://github.com/your-org/bol-ocr-extractor.git
cd bol-ocr-extractor

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt
```

#### 2. System Dependencies Installation

**Windows:**
```bash
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Install Java
# Download from: https://www.java.com/download/

# Verify installations
tesseract --version
java -version
```

**macOS:**
```bash
# Install via Homebrew
brew install tesseract
brew install openjdk@11

# Verify installations
tesseract --version
java -version
```

**Linux (Ubuntu/Debian):**
```bash
# Install system packages
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng
sudo apt-get install default-jre

# Verify installations
tesseract --version
java -version
```

#### 3. Development Configuration

Create development configuration file:

```yaml
# config/development.yaml
debug: true
environment: development

processing:
  min_text_threshold: 50  # Lower threshold for testing
  max_batch_size: 10      # Smaller batches for development
  ocr_enabled: true
  processing_timeout: 120

logging:
  level: DEBUG
  format: detailed
  file: logs/development.log

testing:
  synthetic_data_generation: true
  mock_external_services: true
  test_data_directory: tests/fixtures
```

#### 4. IDE Configuration

**VS Code Setup (.vscode/settings.json):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/.pytest_cache": true
    }
}
```

**PyCharm Configuration:**
- Set Python interpreter to `./venv/bin/python`
- Configure pytest as default test runner
- Enable Black formatter
- Set up run configurations for `streamlit run app.py`

### Docker Development Environment

#### Development Docker Setup

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    default-jre \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt test_requirements.txt ./
RUN pip install -r requirements.txt -r test_requirements.txt

# Copy source code
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Development command
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  bol-ocr-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8501:8501"
    volumes:
      - .:/app
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    depends_on:
      - redis-dev
  
  redis-dev:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

#### Running Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f bol-ocr-dev

# Access application
open http://localhost:8501

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

## Project Structure

### Directory Organization

```
bol-ocr-extractor/
├── app.py                          # Main application entry point
├── requirements.txt                # Production dependencies
├── test_requirements.txt           # Testing dependencies
├── Dockerfile                      # Production container
├── Dockerfile.dev                  # Development container
├── docker-compose.yml             # Production compose
├── docker-compose.dev.yml         # Development compose
│
├── config/                         # Configuration files
│   ├── __init__.py
│   ├── development.yaml
│   ├── production.yaml
│   └── patterns.py                # Field extraction patterns
│
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── pdf_processor.py       # PDF processing engine
│   │   ├── data_extractor.py      # Data extraction engine
│   │   ├── table_parser.py        # Table processing
│   │   └── excel_exporter.py      # Export functionality
│   │
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── bol_data.py           # BOL data structures
│   │   └── processing_result.py   # Processing results
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── logging.py            # Logging configuration
│   │   ├── validation.py         # Data validation
│   │   └── helpers.py            # General utilities
│   │
│   └── web/                      # Web interface components
│       ├── __init__.py
│       ├── streamlit_app.py      # Main Streamlit interface
│       └── components/           # UI components
│           ├── __init__.py
│           ├── upload.py         # File upload handling
│           ├── processing.py     # Processing interface
│           └── results.py        # Results display
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Test configuration
│   ├── unit/                    # Unit tests
│   │   ├── test_pdf_processor.py
│   │   ├── test_data_extractor.py
│   │   ├── test_table_parser.py
│   │   └── test_excel_exporter.py
│   │
│   ├── integration/             # Integration tests
│   │   ├── test_end_to_end.py
│   │   ├── test_file_handling.py
│   │   └── test_batch_processing.py
│   │
│   ├── performance/             # Performance tests
│   │   ├── test_processing_speed.py
│   │   ├── test_memory_usage.py
│   │   └── test_scalability.py
│   │
│   ├── fixtures/                # Test data
│   │   ├── sample_pdfs/
│   │   ├── synthetic_bols/
│   │   └── expected_results/
│   │
│   └── utils/                   # Testing utilities
│       ├── synthetic_data_generator.py
│       ├── accuracy_calculator.py
│       └── test_helpers.py
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md      # This file
│   └── COMPLIANCE.md
│
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── hpa.yaml
│
├── monitoring/                 # Monitoring configuration
│   ├── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── rules/
│       └── alerts.yml
│
├── scripts/                   # Utility scripts
│   ├── deploy.sh
│   ├── test.sh
│   ├── setup-dev.sh
│   └── generate-test-data.py
│
└── .github/                  # GitHub Actions
    └── workflows/
        ├── ci.yml
        ├── security-scan.yml
        └── deploy.yml
```

### Code Organization Principles

#### 1. Separation of Concerns
- **Business Logic**: Core processing in `src/core/`
- **Data Models**: Structured data definitions in `src/models/`
- **User Interface**: Web components in `src/web/`
- **Utilities**: Helper functions in `src/utils/`

#### 2. Dependency Injection
```python
# Example: Configurable dependencies
class BOLOCRApp:
    def __init__(self, 
                 pdf_processor: PDFProcessor = None,
                 data_extractor: BOLDataExtractor = None,
                 excel_exporter: ExcelExporter = None):
        self.pdf_processor = pdf_processor or PDFProcessor()
        self.data_extractor = data_extractor or BOLDataExtractor()
        self.excel_exporter = excel_exporter or ExcelExporter()
```

#### 3. Configuration Management
```python
# config/settings.py
import os
import yaml
from dataclasses import dataclass

@dataclass
class ProcessingConfig:
    min_text_threshold: int = 100
    max_batch_size: int = 100
    ocr_enabled: bool = True
    processing_timeout: int = 300

@dataclass
class AppConfig:
    processing: ProcessingConfig
    debug: bool = False
    environment: str = "production"

def load_config(config_file: str = None) -> AppConfig:
    """Load configuration from file or environment"""
    if not config_file:
        config_file = os.getenv('CONFIG_FILE', 'config/production.yaml')
    
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return AppConfig(
        processing=ProcessingConfig(**config_data.get('processing', {})),
        debug=config_data.get('debug', False),
        environment=config_data.get('environment', 'production')
    )
```

## Code Architecture

### Core Components Architecture

#### 1. PDFProcessor Design

```python
from abc import ABC, abstractmethod
from typing import Tuple, Protocol

class TextExtractor(Protocol):
    def extract(self, pdf_file) -> Tuple[str, bool]:
        """Extract text from PDF"""
        ...

class PDFPlumberExtractor:
    def extract(self, pdf_file) -> Tuple[str, bool]:
        """Text extraction using pdfplumber"""
        # Implementation here
        pass

class TesseractExtractor:
    def extract(self, pdf_file) -> Tuple[str, bool]:
        """OCR extraction using pytesseract"""
        # Implementation here
        pass

class PDFProcessor:
    def __init__(self, 
                 text_extractor: TextExtractor = None,
                 ocr_extractor: TextExtractor = None):
        self.text_extractor = text_extractor or PDFPlumberExtractor()
        self.ocr_extractor = ocr_extractor or TesseractExtractor()
        self.min_text_threshold = 100
    
    def process_pdf(self, pdf_file, filename: str) -> Tuple[str, str, str]:
        """Process PDF with intelligent fallback strategy"""
        # Try text extraction first
        text, success = self.text_extractor.extract(pdf_file)
        method = "text"
        confidence = self._assess_quality(text)
        
        # Fallback to OCR if needed
        if not success or confidence == "low":
            ocr_text, ocr_success = self.ocr_extractor.extract(pdf_file)
            if ocr_success:
                text = ocr_text
                method = "ocr"
                confidence = self._assess_quality(text)
        
        return text, method, confidence
    
    def _assess_quality(self, text: str) -> str:
        """Assess text extraction quality"""
        if len(text.strip()) < 50:
            return "low"
        
        has_structure = any(keyword in text.upper() 
                          for keyword in ["SHIPPER", "CONSIGNEE", "B/L"])
        has_addresses = text.count('\n') > 5
        
        if has_structure and has_addresses:
            return "high"
        elif has_structure or has_addresses:
            return "medium"
        else:
            return "low"
```

#### 2. Data Extraction Architecture

```python
from typing import Dict, List, Callable
import re

class FieldExtractor:
    """Base class for field extraction strategies"""
    
    def __init__(self, patterns: Dict[str, List[str]]):
        self.patterns = patterns
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Pre-compile regex patterns for performance"""
        compiled = {}
        for field, pattern_list in self.patterns.items():
            compiled[field] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                for pattern in pattern_list
            ]
        return compiled
    
    def extract_field(self, text: str, field_type: str) -> str:
        """Extract a specific field using compiled patterns"""
        if field_type not in self._compiled_patterns:
            return ""
        
        for pattern in self._compiled_patterns[field_type]:
            match = pattern.search(text)
            if match:
                result = match.group(1).strip()
                if result:
                    return self._clean_field_data(result)
        
        return ""
    
    def _clean_field_data(self, data: str) -> str:
        """Clean and normalize extracted field data"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', data.strip())
        # Remove common artifacts
        cleaned = re.sub(r'^[:\-\s]+', '', cleaned)
        cleaned = re.sub(r'[:\-\s]+$', '', cleaned)
        return cleaned

class BOLDataExtractor:
    """Main data extraction engine"""
    
    def __init__(self, field_extractor: FieldExtractor = None):
        self.field_extractor = field_extractor or FieldExtractor(DEFAULT_PATTERNS)
        self.extractors = self._build_extractor_map()
    
    def _build_extractor_map(self) -> Dict[str, Callable]:
        """Build mapping of field names to extraction methods"""
        return {
            'bol_number': self._extract_bol_number,
            'shipper_name': self._extract_shipper_name,
            'shipper_address': self._extract_shipper_address,
            'consignee_name': self._extract_consignee_name,
            'consignee_address': self._extract_consignee_address,
            # ... more extractors
        }
    
    def extract_all_fields(self, text: str, tables: List, filename: str) -> BOLData:
        """Extract all fields using registered extractors"""
        bol_data = BOLData(filename=filename)
        
        try:
            for field_name, extractor_func in self.extractors.items():
                value = extractor_func(text, tables)
                setattr(bol_data, field_name, value)
            
            # Set processing metadata
            bol_data.extraction_failed = False
            
        except Exception as e:
            bol_data.extraction_failed = True
            bol_data.processing_notes = f"Extraction error: {str(e)}"
        
        return bol_data
```

#### 3. Error Handling Strategy

```python
import logging
from typing import Optional, Union
from enum import Enum
from dataclasses import dataclass

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ProcessingError:
    code: str
    message: str
    severity: ErrorSeverity
    details: Optional[Dict] = None
    recoverable: bool = True

class ErrorHandler:
    """Centralized error handling with classification"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_counts = {}
    
    def handle_error(self, error: Exception, context: Dict) -> ProcessingError:
        """Classify and handle processing errors"""
        error_info = self._classify_error(error, context)
        
        # Log error with appropriate level
        log_method = getattr(self.logger, error_info.severity.value)
        log_method(f"{error_info.code}: {error_info.message}", 
                  extra={"context": context, "details": error_info.details})
        
        # Track error frequency
        self.error_counts[error_info.code] = self.error_counts.get(error_info.code, 0) + 1
        
        return error_info
    
    def _classify_error(self, error: Exception, context: Dict) -> ProcessingError:
        """Classify error type and severity"""
        error_type = type(error).__name__
        
        # PDF processing errors
        if error_type in ['PDFSyntaxError', 'PDFEncryptionError']:
            return ProcessingError(
                code="PDF_PROCESSING_ERROR",
                message=f"PDF processing failed: {str(error)}",
                severity=ErrorSeverity.MEDIUM,
                details={"error_type": error_type, "filename": context.get("filename")},
                recoverable=True
            )
        
        # OCR processing errors
        elif error_type in ['TesseractError', 'TesseractNotFoundError']:
            return ProcessingError(
                code="OCR_PROCESSING_ERROR", 
                message=f"OCR processing failed: {str(error)}",
                severity=ErrorSeverity.HIGH,
                details={"error_type": error_type},
                recoverable=False
            )
        
        # Memory errors
        elif error_type == 'MemoryError':
            return ProcessingError(
                code="MEMORY_ERROR",
                message="Insufficient memory for processing",
                severity=ErrorSeverity.CRITICAL,
                details={"memory_usage": context.get("memory_usage")},
                recoverable=False
            )
        
        # Default classification
        else:
            return ProcessingError(
                code="UNKNOWN_ERROR",
                message=f"Unexpected error: {str(error)}",
                severity=ErrorSeverity.HIGH,
                details={"error_type": error_type},
                recoverable=False
            )
```

### Performance Architecture

#### 1. Caching Strategy

```python
import hashlib
import pickle
import redis
from functools import wraps
from typing import Any, Callable

class CacheManager:
    """Redis-based caching for processing results"""
    
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def cached_processing(self, ttl: int = None):
        """Decorator for caching processing results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"bol_ocr:{func.__name__}:{self.cache_key(*args, **kwargs)}"
                
                # Try to get from cache
                try:
                    cached_result = self.redis.get(cache_key)
                    if cached_result:
                        return pickle.loads(cached_result)
                except Exception as e:
                    # Cache miss or error, continue with processing
                    pass
                
                # Process and cache result
                result = func(*args, **kwargs)
                
                try:
                    self.redis.setex(
                        cache_key,
                        ttl or self.default_ttl,
                        pickle.dumps(result)
                    )
                except Exception as e:
                    # Cache write failed, but processing succeeded
                    pass
                
                return result
            
            return wrapper
        return decorator

# Usage example
cache_manager = CacheManager(redis.Redis())

class CachedPDFProcessor(PDFProcessor):
    @cache_manager.cached_processing(ttl=7200)  # 2 hours
    def process_pdf(self, pdf_file, filename: str):
        return super().process_pdf(pdf_file, filename)
```

#### 2. Parallel Processing

```python
import asyncio
import concurrent.futures
from typing import List, Tuple, Any
import threading

class ParallelProcessor:
    """Parallel processing manager for batch operations"""
    
    def __init__(self, max_workers: int = 4, memory_limit_mb: int = 1000):
        self.max_workers = max_workers
        self.memory_limit_mb = memory_limit_mb
        self.semaphore = threading.Semaphore(max_workers)
    
    async def process_batch_parallel(self, 
                                   files: List[Tuple[Any, str]], 
                                   processor_func: Callable) -> List[Any]:
        """Process files in parallel with memory management"""
        # Create event loop for async processing
        loop = asyncio.get_event_loop()
        
        # Use ThreadPoolExecutor for I/O bound operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            tasks = []
            for pdf_file, filename in files:
                task = loop.run_in_executor(
                    executor, 
                    self._safe_process_single, 
                    processor_func, 
                    pdf_file, 
                    filename
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result
                    error_result = self._create_error_result(files[i][1], result)
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            return processed_results
    
    def _safe_process_single(self, processor_func: Callable, pdf_file, filename: str):
        """Thread-safe single file processing with memory monitoring"""
        with self.semaphore:  # Limit concurrent processing
            try:
                # Monitor memory usage
                initial_memory = self._get_memory_usage()
                
                # Process the file
                result = processor_func(pdf_file, filename)
                
                # Check memory usage
                final_memory = self._get_memory_usage()
                memory_increase = final_memory - initial_memory
                
                if memory_increase > self.memory_limit_mb:
                    # Force garbage collection
                    import gc
                    gc.collect()
                
                return result
                
            except Exception as e:
                return self._create_error_result(filename, e)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def _create_error_result(self, filename: str, error: Exception):
        """Create error result object"""
        from src.models.bol_data import BOLData
        error_result = BOLData()
        error_result.filename = filename
        error_result.extraction_failed = True
        error_result.processing_notes = f"Processing error: {str(error)}"
        return error_result
```

## Development Workflow

### Git Workflow

#### Branch Strategy
```
main/master (production)
├── develop (integration branch)
│   ├── feature/BOL-123-improve-ocr-accuracy
│   ├── feature/BOL-124-add-custom-patterns
│   ├── bugfix/BOL-125-memory-leak-fix
│   └── hotfix/BOL-126-critical-security-patch
```

#### Commit Convention
```
type(scope): brief description

[optional body]

[optional footer(s)]

Types:
- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting, missing semi-colons, etc.
- refactor: code restructuring
- test: adding tests
- chore: maintenance tasks

Examples:
feat(extraction): add support for multi-language BOLs
fix(pdf): resolve memory leak in batch processing
docs(api): update extraction method documentation
```

#### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/BOL-123-improve-ocr-accuracy
   ```

2. **Development and Testing**
   ```bash
   # Make changes and commit
   git add .
   git commit -m "feat(ocr): improve text recognition accuracy"
   
   # Run tests
   python -m pytest tests/
   
   # Run linting
   flake8 src/ tests/
   black src/ tests/
   ```

3. **Create Pull Request**
   - Open PR from feature branch to develop
   - Fill out PR template with description, testing notes
   - Request review from team members
   - Ensure all CI checks pass

4. **Code Review Checklist**
   - [ ] Code follows project style guidelines
   - [ ] All tests pass and new tests added for new functionality
   - [ ] Documentation updated for API changes
   - [ ] Performance impact assessed for critical paths
   - [ ] Security implications reviewed
   - [ ] Error handling and logging appropriate

### Development Scripts

#### Setup Script
```bash
#!/bin/bash
# scripts/setup-dev.sh

set -e

echo "Setting up BOL OCR Extractor development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r test_requirements.txt

# Install pre-commit hooks
pre-commit install

# Create development configuration
cp config/development.yaml.example config/development.yaml

# Generate test data
python scripts/generate-test-data.py

# Run initial tests
python -m pytest tests/unit/ -v

echo "Development environment setup complete!"
echo "Activate environment with: source venv/bin/activate"
echo "Run application with: streamlit run app.py"
```

#### Test Script
```bash
#!/bin/bash
# scripts/test.sh

set -e

echo "Running BOL OCR Extractor test suite..."

# Unit tests
echo "Running unit tests..."
python -m pytest tests/unit/ -v --cov=src --cov-report=html

# Integration tests
echo "Running integration tests..."
python -m pytest tests/integration/ -v

# Performance tests (optional)
if [ "$1" = "--performance" ]; then
    echo "Running performance tests..."
    python -m pytest tests/performance/ -v
fi

# Code quality checks
echo "Running code quality checks..."
flake8 src/ tests/
black --check src/ tests/
mypy src/

echo "All tests completed successfully!"
```

### Code Quality Tools

#### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

#### Linting Configuration
```ini
# setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    build,
    dist

[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
ignore_missing_imports = True

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
```

## Testing Framework

### Test Architecture

#### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing  
3. **Performance Tests**: Speed and memory benchmarking
4. **End-to-End Tests**: Complete workflow validation

#### Test Data Management

```python
# tests/utils/test_data_manager.py
import os
import json
from pathlib import Path
from typing import Dict, List, Any

class TestDataManager:
    """Manage test data and fixtures"""
    
    def __init__(self, base_path: str = "tests/fixtures"):
        self.base_path = Path(base_path)
        self.synthetic_pdfs_path = self.base_path / "synthetic_pdfs"
        self.sample_pdfs_path = self.base_path / "sample_pdfs"
        self.expected_results_path = self.base_path / "expected_results"
    
    def get_test_pdfs(self, category: str = "all") -> List[Path]:
        """Get test PDF files by category"""
        if category == "synthetic":
            return list(self.synthetic_pdfs_path.glob("*.pdf"))
        elif category == "sample":
            return list(self.sample_pdfs_path.glob("*.pdf"))
        else:
            pdfs = []
            pdfs.extend(self.get_test_pdfs("synthetic"))
            pdfs.extend(self.get_test_pdfs("sample"))
            return pdfs
    
    def get_expected_result(self, pdf_filename: str) -> Dict[str, Any]:
        """Get expected extraction result for a PDF"""
        result_file = self.expected_results_path / f"{pdf_filename}.json"
        if result_file.exists():
            with open(result_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_expected_result(self, pdf_filename: str, result: Dict[str, Any]):
        """Save expected result for future testing"""
        result_file = self.expected_results_path / f"{pdf_filename}.json"
        result_file.parent.mkdir(parents=True, exist_ok=True)
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
```

#### Performance Testing Framework

```python
# tests/performance/test_performance_framework.py
import time
import psutil
import pytest
from typing import Dict, Any, Callable
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    execution_time: float
    memory_peak: float
    memory_average: float
    cpu_usage: float

class PerformanceTester:
    """Framework for performance testing"""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def measure_performance(self, test_func: Callable, *args, **kwargs) -> PerformanceMetrics:
        """Measure performance metrics for a function"""
        # Record initial state
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_samples = [initial_memory]
        
        # Start timing
        start_time = time.time()
        start_cpu = self.process.cpu_percent()
        
        # Execute function with memory monitoring
        def memory_monitor():
            while not hasattr(memory_monitor, 'stop'):
                memory_samples.append(self.process.memory_info().rss / 1024 / 1024)
                time.sleep(0.1)
        
        # Start memory monitoring in background
        import threading
        monitor_thread = threading.Thread(target=memory_monitor)
        monitor_thread.start()
        
        try:
            # Execute the test function
            result = test_func(*args, **kwargs)
        finally:
            # Stop monitoring
            memory_monitor.stop = True
            monitor_thread.join()
            
            # Record final state
            end_time = time.time()
            end_cpu = self.process.cpu_percent()
        
        return PerformanceMetrics(
            execution_time=end_time - start_time,
            memory_peak=max(memory_samples),
            memory_average=sum(memory_samples) / len(memory_samples),
            cpu_usage=end_cpu - start_cpu
        )

# Performance test example
@pytest.mark.performance
def test_batch_processing_performance():
    """Test batch processing performance with various batch sizes"""
    tester = PerformanceTester()
    test_data = TestDataManager()
    
    # Test different batch sizes
    batch_sizes = [1, 10, 25, 50]
    results = {}
    
    for batch_size in batch_sizes:
        pdfs = test_data.get_test_pdfs()[:batch_size]
        
        def batch_process():
            app = BOLOCRApp()
            files = [(open(pdf, 'rb'), pdf.name) for pdf in pdfs]
            return app.process_batch_pdfs(files)
        
        metrics = tester.measure_performance(batch_process)
        results[batch_size] = metrics
        
        # Performance assertions
        assert metrics.execution_time < batch_size * 30  # Max 30s per file
        assert metrics.memory_peak < 500 + (batch_size * 10)  # Max 500MB + 10MB per file
    
    # Analyze scalability
    time_per_file_1 = results[1].execution_time
    time_per_file_50 = results[50].execution_time / 50
    
    # Should not degrade more than 50% with batch processing
    assert time_per_file_50 < time_per_file_1 * 1.5
```

### Continuous Integration

#### GitHub Actions Configuration

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng default-jre
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r test_requirements.txt
    
    - name: Run linting
      run: |
        flake8 src/ tests/
        black --check src/ tests/
        mypy src/
    
    - name: Run unit tests
      run: |
        python -m pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: |
        python -m pytest tests/integration/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: 'security-scan-results.sarif'
    
    - name: Run dependency check
      run: |
        pip install safety
        safety check --json --output safety-report.json

  build-and-push:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t bol-ocr-extractor:${{ github.sha }} .
        docker tag bol-ocr-extractor:${{ github.sha }} bol-ocr-extractor:latest
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push bol-ocr-extractor:${{ github.sha }}
        docker push bol-ocr-extractor:latest
```

## Performance Optimization

### Profiling and Monitoring

#### Performance Profiling

```python
# scripts/profile_performance.py
import cProfile
import pstats
import io
from pstats import SortKey
from app import BOLOCRApp

def profile_processing():
    """Profile BOL processing performance"""
    pr = cProfile.Profile()
    
    # Start profiling
    pr.enable()
    
    # Run processing
    app = BOLOCRApp()
    with open('test_bol.pdf', 'rb') as pdf_file:
        result = app.process_single_pdf(pdf_file, 'test_bol.pdf')
    
    # Stop profiling
    pr.disable()
    
    # Print results
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    
    print(s.getvalue())

if __name__ == "__main__":
    profile_processing()
```

#### Memory Profiling

```python
# scripts/memory_profile.py
from memory_profiler import profile
from app import BOLOCRApp

@profile
def memory_test_batch_processing():
    """Memory profile for batch processing"""
    app = BOLOCRApp()
    
    # Load test files
    files = []
    for i in range(50):
        with open(f'test_files/test_{i}.pdf', 'rb') as f:
            files.append((f, f'test_{i}.pdf'))
    
    # Process batch
    results = app.process_batch_pdfs(files)
    
    return results

if __name__ == "__main__":
    memory_test_batch_processing()
```

### Optimization Strategies

#### 1. Pattern Compilation Optimization

```python
import re
from typing import Dict, List
from functools import lru_cache

class OptimizedFieldPatterns:
    """Optimized pattern management with caching"""
    
    def __init__(self):
        self._pattern_cache = {}
        self._compiled_patterns = {}
    
    @lru_cache(maxsize=128)
    def get_compiled_patterns(self, field_type: str) -> List[re.Pattern]:
        """Get compiled patterns with LRU caching"""
        if field_type not in self._compiled_patterns:
            patterns = self.get_patterns(field_type)
            self._compiled_patterns[field_type] = [
                re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                for pattern in patterns
            ]
        
        return self._compiled_patterns[field_type]
    
    def warm_pattern_cache(self):
        """Pre-compile all patterns for better performance"""
        field_types = ['bol_number', 'shipper', 'consignee', 'vessel', 'ports']
        for field_type in field_types:
            self.get_compiled_patterns(field_type)
```

#### 2. Memory-Efficient Batch Processing

```python
import gc
from typing import Iterator, List, Tuple, Any

class MemoryEfficientProcessor:
    """Memory-efficient batch processing with streaming"""
    
    def __init__(self, chunk_size: int = 10, memory_threshold_mb: int = 500):
        self.chunk_size = chunk_size
        self.memory_threshold_mb = memory_threshold_mb
    
    def process_batch_streaming(self, files: List[Tuple[Any, str]]) -> Iterator[BOLData]:
        """Process files in chunks to manage memory usage"""
        for i in range(0, len(files), self.chunk_size):
            chunk = files[i:i + self.chunk_size]
            
            # Process chunk
            for pdf_file, filename in chunk:
                try:
                    result = self._process_single_with_cleanup(pdf_file, filename)
                    yield result
                except Exception as e:
                    error_result = self._create_error_result(filename, e)
                    yield error_result
            
            # Memory cleanup after each chunk
            gc.collect()
            
            # Check memory usage
            current_memory = self._get_memory_usage()
            if current_memory > self.memory_threshold_mb:
                # Force more aggressive cleanup
                import ctypes
                ctypes.CDLL("libc.so.6").malloc_trim(0)
    
    def _process_single_with_cleanup(self, pdf_file, filename: str) -> BOLData:
        """Process single file with automatic cleanup"""
        app = BOLOCRApp()
        try:
            result = app.process_single_pdf(pdf_file, filename)
            return result
        finally:
            # Explicit cleanup
            del app
            gc.collect()
```

## Contributing Guidelines

### Code Standards

#### Style Guidelines
- **PEP 8**: Follow Python PEP 8 style guide
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Naming**: Use descriptive names, snake_case for functions/variables
- **Type Hints**: Use type hints for all public functions
- **Docstrings**: Google-style docstrings for all public classes/methods

#### Documentation Requirements
- **API Changes**: Update API documentation for any interface changes
- **New Features**: Add user guide documentation for new functionality
- **Configuration**: Document any new configuration options
- **Examples**: Provide usage examples for complex features

#### Testing Requirements
- **Unit Tests**: 80%+ code coverage for new code
- **Integration Tests**: Add tests for new integration points
- **Performance Tests**: Add benchmarks for performance-critical changes
- **Documentation Tests**: Ensure documentation examples work

### Contribution Process

#### 1. Issue Creation
Before starting work, create or reference an issue:
- Bug reports: Include reproduction steps, expected vs actual behavior
- Feature requests: Include use case, proposed solution, alternatives considered
- Performance issues: Include profiling data and benchmarks

#### 2. Development Process
```bash
# 1. Fork and clone repository
git clone https://github.com/your-username/bol-ocr-extractor.git
cd bol-ocr-extractor

# 2. Create feature branch
git checkout -b feature/issue-123-add-new-feature

# 3. Set up development environment
./scripts/setup-dev.sh

# 4. Make changes following code standards
# ... development work ...

# 5. Run tests and checks
./scripts/test.sh
pre-commit run --all-files

# 6. Commit changes
git add .
git commit -m "feat(extraction): add support for custom patterns"

# 7. Push and create pull request
git push origin feature/issue-123-add-new-feature
```

#### 3. Pull Request Guidelines
- **Title**: Clear, descriptive title following commit convention
- **Description**: Explain what changes were made and why
- **Testing**: Describe testing performed and results
- **Breaking Changes**: Clearly document any breaking changes
- **Screenshots**: Include UI changes screenshots if applicable

#### 4. Review Process
- **Automated Checks**: All CI checks must pass
- **Code Review**: At least one approval from maintainer required
- **Testing**: Manual testing of new features by reviewer
- **Documentation**: Verify documentation updates are complete

### Release Process

#### Version Management
- **Semantic Versioning**: Follow semver (MAJOR.MINOR.PATCH)
- **Release Branches**: Create release branches for major/minor versions
- **Hotfix Process**: Direct patches to main branch for critical fixes
- **Changelog**: Maintain CHANGELOG.md with all notable changes

#### Deployment Pipeline
```yaml
# Release workflow
1. Create release branch: release/v1.2.0
2. Update version numbers and changelog
3. Run full test suite including performance tests
4. Create release PR to main branch
5. After merge, tag release: git tag v1.2.0
6. Build and push Docker images
7. Deploy to staging environment
8. Run acceptance tests
9. Deploy to production
10. Monitor for issues
```

This developer guide provides comprehensive information for setting up, developing, testing, and contributing to the BOL OCR Extractor project. It ensures consistent development practices and maintains high code quality standards.