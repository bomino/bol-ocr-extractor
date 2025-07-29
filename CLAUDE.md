# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OCR (Optical Character Recognition) project for automating data extraction from PDF Bills of Lading (BOLs). The repository currently contains only a project specification (`prompt.md`) that describes requirements for building a Python application with the following capabilities:

- PDF parsing and OCR for both text-based and scanned documents
- Batch processing of multiple PDF files
- Data extraction from Bills of Lading with specific field targeting
- Excel export functionality
- Streamlit-based web GUI

## Project Architecture

Based on the specification and execution plan (`EXECUTION_PLAN.md`), the project follows a modular architecture:

### Project Structure
```
ocr_app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Dependencies
├── config/
│   └── field_patterns.py  # Configurable regex patterns
├── modules/
│   ├── pdf_processor.py   # PDF text extraction & OCR
│   ├── data_extractor.py  # Field extraction logic
│   ├── table_parser.py    # Table extraction
│   └── excel_exporter.py  # Excel output handling
├── utils/
│   ├── validators.py      # Data validation
│   └── logger.py         # Logging utilities
└── tests/                 # Unit and integration tests
```

### Core Components
- **PDF Processing Module** (`modules/pdf_processor.py`): Handle text extraction (`pdfplumber`) and OCR fallback (`pytesseract`, `Pillow`)
- **Data Extraction Engine** (`modules/data_extractor.py`): Regex-based field extraction with configurable patterns for:
  - Bill of Lading Number
  - Shipper/Consignee/Notify Party details
  - Vessel and voyage information
  - Cargo descriptions and quantities
  - Dates and freight terms
- **Table Processing** (`modules/table_parser.py`): `tabula-py` for extracting tabular data from PDFs
- **Export Module** (`modules/excel_exporter.py`): `pandas`-based DataFrame creation and Excel output
- **Web Interface** (`app.py`): `streamlit` GUI for file upload, processing, and download
- **Configuration System** (`config/field_patterns.py`): Configurable regex patterns for different BOL templates

### Key Dependencies
```
streamlit>=1.28.0
pdfplumber>=0.9.0
pandas>=2.0.0
pytesseract>=0.3.10
Pillow>=10.0.0
tabula-py>=2.8.0
openpyxl>=3.1.0
regex>=2023.0.0
```

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv ocr_env
source ocr_env/bin/activate  # Windows: ocr_env\Scripts\activate

# Install Tesseract OCR (system dependency)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Install Python dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_pdf_processor.py
python -m pytest tests/test_data_extractor.py

# Run with coverage
python -m pytest tests/ --cov=modules
```

### Development Workflow
```bash
# Process single PDF for testing
python -c "from modules.pdf_processor import PDFProcessor; print(PDFProcessor().process_pdf('sample.pdf'))"

# Test data extraction patterns
python -c "from modules.data_extractor import BOLDataExtractor; extractor = BOLDataExtractor(); print(extractor.test_patterns())"
```

## Development Notes

### Critical Requirements
- Tesseract OCR engine must be installed separately on the system
- Regex patterns in `config/field_patterns.py` should be configurable for different BOL templates
- Error handling is critical for batch processing scenarios (up to 100 PDFs)
- Memory efficiency optimization needed for large batch operations
- OCR fallback should trigger automatically when text extraction yields insufficient results

### Implementation Guidelines
- Follow the 6-phase development plan outlined in `EXECUTION_PLAN.md`
- Implement comprehensive logging throughout all modules
- Use dependency injection for testability
- Maintain >90% test coverage for core functionality
- Follow modular architecture with clear separation of concerns

### Performance Targets
- Single PDF processing: <30 seconds
- 100 PDF batch processing: <30 minutes  
- Memory usage: <2GB for large batches
- UI response time: <3 seconds

### Field Extraction Priorities
BOL fields in order of extraction importance:
1. Bill of Lading Number (critical for identification)
2. Shipper/Consignee details (business critical)
3. Cargo description and quantities (operational)
4. Dates and vessel information (tracking)
5. Ports and freight terms (logistics)

## Implementation Status

- [x] Project specification (`prompt.md`)
- [x] Execution plan (`EXECUTION_PLAN.md`)
- [ ] Phase 0: Project setup and environment
- [ ] Phase 1: PDF processing module
- [ ] Phase 2: Data extraction engine
- [ ] Phase 3: Excel export functionality
- [ ] Phase 4: Streamlit web interface
- [ ] Phase 5: Integration testing
- [ ] Phase 6: Optimization and polish

## References

- **Project Specification**: `prompt.md` - Detailed requirements
- **Implementation Plan**: `EXECUTION_PLAN.md` - Phase-by-phase development approach
- **Architecture**: Modular design with clear component separation