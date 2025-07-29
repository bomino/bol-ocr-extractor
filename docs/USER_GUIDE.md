# BOL OCR Extractor - User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Interface Overview](#user-interface-overview)
3. [Processing Workflows](#processing-workflows)
4. [File Management](#file-management)
5. [Data Export Options](#data-export-options)
6. [Quality Assessment](#quality-assessment)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### What is the BOL OCR Extractor?

The BOL OCR Extractor is an intelligent document processing application that automatically extracts structured data from Bills of Lading (BOL) documents. Whether your documents are text-based PDFs or scanned images, the system can intelligently process them and extract key shipping and logistics information.

### Key Features

- **Hybrid Processing**: Automatically switches between text extraction and OCR based on document quality
- **Batch Processing**: Handle single files, multiple files, or ZIP archives containing PDFs
- **Intelligent Recognition**: Extracts 15+ key BOL fields with high accuracy
- **Professional Export**: Generate Excel spreadsheets or CSV files with summary statistics
- **Progress Tracking**: Real-time processing updates with detailed status information
- **Quality Assessment**: Confidence scoring and processing method reporting

### System Requirements

**Supported File Formats:**
- PDF documents (text-based or scanned)
- ZIP archives containing PDF files
- Maximum file size: 50MB per file
- Maximum batch size: 100 files

**Browser Requirements:**
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Stable internet connection

## User Interface Overview

### Main Application Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    🚢 Bill of Lading OCR Extractor          │
├─────────────────────────────────────────────────────────────┤
│  Configuration Sidebar    │         Main Content Area       │
│  ┌─────────────────────┐  │  ┌─────────────────────────────┐  │
│  │ Export Format       │  │  │ 📁 Upload Files             │  │
│  │ Processing Options  │  │  │ ⚙️ Processing               │  │
│  │ Settings           │  │  │ 📊 Results                  │  │
│  └─────────────────────┘  │  │ 💾 Download                 │  │
│                           │  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Sidebar Configuration

#### Export Format Options
- **Excel (.xlsx)**: Professional spreadsheet with multiple sheets and formatting
- **CSV (.csv)**: Simple comma-separated values for database import

#### Processing Options
- **Enable OCR Fallback**: Automatically use OCR for scanned documents (recommended)
- **Minimum Text Threshold**: Character count required for successful text extraction (default: 100)

### Main Content Areas

#### 1. File Upload Section
Choose from three upload methods:
- **Single PDF File**: Upload one document at a time
- **Multiple PDF Files**: Select multiple PDFs simultaneously
- **ZIP Archive**: Upload a ZIP file containing multiple PDFs

#### 2. Processing Section
- Real-time progress bar
- File count and processing status
- Current file being processed
- Processing method indicator (text/OCR)

#### 3. Results Section
- Summary statistics dashboard
- Data preview table
- Detailed results view
- Error reporting for failed extractions

#### 4. Download Section
- Export format selection
- Download buttons for results
- File naming with timestamps

## Processing Workflows

### Single File Processing

#### Step 1: Configure Settings
1. In the sidebar, select your preferred export format
2. Adjust processing options if needed (defaults work well for most cases)
3. Ensure "Enable OCR Fallback" is checked for maximum compatibility

#### Step 2: Upload Document
1. Select "Single PDF File" in the upload section
2. Click "Choose a PDF file" or drag and drop your document
3. Verify the file appears with correct name and size

#### Step 3: Start Processing
1. Click the "🚀 Start Processing" button
2. Watch the progress indicator for real-time updates
3. Processing typically takes 2-30 seconds depending on document complexity

#### Step 4: Review Results
1. Check the summary metrics (successful/failed extractions)
2. Preview the extracted data in the results table
3. Review any processing notes or warnings

#### Step 5: Download Results
1. Click the download button for your preferred format
2. File will be saved with timestamp (e.g., `bol_extraction_results_20240115_143022.xlsx`)

### Batch Processing

#### Step 1: Prepare Files
**Option A: Multiple Files**
- Organize all PDF files in a folder
- Select "Multiple PDF Files" in the upload section
- Use Ctrl+Click (Windows) or Cmd+Click (Mac) to select multiple files

**Option B: ZIP Archive**
- Create a ZIP archive containing all PDF files
- Ensure all files in the ZIP are PDFs
- Select "ZIP Archive" in the upload section

#### Step 2: Upload and Process
1. Upload your files using your chosen method
2. Review the file count confirmation
3. Click "🚀 Start Processing" to begin batch processing
4. Monitor progress - batch processing shows individual file progress

#### Step 3: Review Batch Results
1. **Summary Statistics**: Total files, success/failure counts, processing methods used
2. **Success Rate**: Percentage of successfully processed files
3. **Processing Time**: Total time and average per file
4. **Method Distribution**: How many files used text vs. OCR processing

#### Step 4: Handle Failed Extractions
1. Check "Failed Extractions Details" section for error information
2. Note which files failed and why
3. Consider reprocessing failed files individually with adjusted settings

### Quality Assessment Workflow

#### Understanding Confidence Levels

**High Confidence (Green)**
- Text extraction successful with clear field structure
- All major fields detected and extracted
- Minimal processing notes or warnings
- Recommended action: Use results as-is

**Medium Confidence (Yellow)**
- OCR processing used or partial field detection
- Most important fields extracted successfully
- Some fields may be incomplete or require verification
- Recommended action: Spot-check critical fields

**Low Confidence (Red)**
- Poor document quality or unusual format
- Limited field extraction success
- Significant processing warnings
- Recommended action: Manual review required

#### Quality Indicators

**Processing Method Indicators:**
- **Text**: Direct text extraction (fastest, most accurate)
- **OCR**: Optical character recognition (slower, may have errors)
- **Text Fallback**: Combined approach for challenging documents

**Field Completion Rates:**
- **Critical Fields**: BOL Number, Shipper, Consignee (should be >90% complete)
- **Important Fields**: Vessel, Ports, Dates (target >80% complete)
- **Optional Fields**: Weights, Quantities, Terms (variable completion expected)

## File Management

### Supported File Types and Formats

#### PDF Document Requirements
- **Text-based PDFs**: Created from digital documents (preferred)
- **Scanned PDFs**: Image-based documents from scanners or photos
- **Mixed PDFs**: Documents with both text and image elements
- **Multi-page Documents**: Up to 50 pages per document

#### ZIP Archive Requirements
- **File Format**: Standard ZIP compression
- **Contents**: Only PDF files (other file types ignored)
- **Structure**: Flat structure preferred (nested folders supported)
- **Size Limits**: Individual PDFs must be under 50MB

### File Quality Guidelines

#### Optimal Document Characteristics
- **Resolution**: 300 DPI or higher for scanned documents
- **Orientation**: Portrait orientation, properly aligned
- **Quality**: Clear, high-contrast text with minimal blur
- **Completeness**: Full document pages without cropping
- **Format**: Standard BOL layout with labeled fields

#### Common Quality Issues
- **Low Resolution**: Scanned at less than 200 DPI
- **Poor Contrast**: Light text on light backgrounds
- **Skewed Pages**: Rotated or tilted document orientation
- **Partial Pages**: Cropped or cut-off content
- **Handwritten Text**: Difficult for OCR to process accurately

### File Naming Best Practices

#### Recommended Naming Conventions
```
BOL_[BOL_NUMBER]_[DATE]_[DESCRIPTION].pdf
Examples:
- BOL_12345_20240115_Containerload.pdf
- BOL_ABC789_20240115_Automotive_Parts.pdf
- BOL_XYZ001_20240115_Electronics_Shipment.pdf
```

#### Avoid These Naming Patterns
- Special characters: `<>:"/\|?*`
- Very long filenames (>255 characters)
- Leading or trailing spaces
- Duplicate names in batch processing

## Data Export Options

### Excel Export Format

#### Workbook Structure
The Excel export includes two worksheets:

**BOL_Data Sheet:**
- Complete extraction results with all fields
- One row per processed document
- Color-coded confidence indicators
- Processing metadata columns

**Processing_Summary Sheet:**
- Statistical overview of batch processing
- Success/failure metrics
- Processing method distribution
- Quality confidence breakdown

#### Column Reference

| Column | Description | Example Values |
|--------|-------------|----------------|
| filename | Original file name | "shipment_001.pdf" |
| bol_number | Bill of Lading number | "BOL123456789" |
| shipper_name | Shipping company name | "ABC Logistics Inc" |
| shipper_address | Complete shipper address | "123 Port St, LA, CA 90001" |
| consignee_name | Receiving company name | "XYZ Imports Corp" |
| consignee_address | Complete consignee address | "456 Harbor Blvd, NY, NY 10001" |
| notify_party_name | Notification party name | "Maritime Services LLC" |
| notify_party_address | Notification party address | "789 Dock Ave, Boston, MA" |
| vessel_name | Ship/vessel name | "MV Ocean Carrier" |
| voyage_number | Voyage identifier | "VOY2024001" |
| port_of_load | Loading port | "Los Angeles, CA" |
| port_of_discharge | Destination port | "New York, NY" |
| description_of_goods | Cargo description | "Electronic Equipment" |
| quantity_packages | Package count and type | "100 CTNS" |
| gross_weight | Total weight | "2,500 KG" |
| net_weight | Net cargo weight | "2,200 KG" |
| freight_terms | Payment terms | "PREPAID" |
| date_of_issue | BOL issue date | "15/03/2024" |
| extraction_method | Processing method used | "text", "ocr" |
| extraction_confidence | Quality assessment | "high", "medium", "low" |
| processing_notes | Additional information | Warnings or extraction notes |
| extraction_failed | Processing status | TRUE/FALSE |

### CSV Export Format

#### Structure
- Comma-separated values with header row
- Same column structure as Excel BOL_Data sheet
- UTF-8 encoding for international characters
- Suitable for database import or spreadsheet applications

#### Usage Scenarios
- **Database Import**: Direct import into SQL databases
- **Data Analysis**: Use with R, Python, or statistical software
- **Legacy Systems**: Compatible with older systems that don't support Excel
- **Automation**: Easier to parse programmatically

### Export Customization

#### Filename Convention
All exports use timestamp-based naming:
- Excel: `bol_extraction_results_YYYYMMDD_HHMMSS.xlsx`
- CSV: `bol_extraction_results_YYYYMMDD_HHMMSS.csv`

#### Content Filtering
The system exports all processed files, including failed extractions:
- **Successful extractions**: Complete data with confidence indicators
- **Failed extractions**: Filename and error information preserved
- **Partial extractions**: Available data included with processing notes

## Quality Assessment

### Understanding Extraction Quality

#### Confidence Scoring System

**High Confidence (85-100% accuracy expected)**
- Clear, structured document with standard BOL format
- Text-based PDF with good quality text extraction
- All major fields detected with clear delimiters
- Minimal ambiguity in field identification

**Medium Confidence (70-85% accuracy expected)**
- OCR processing required or non-standard format
- Most fields detected but some may need verification
- Acceptable text quality with minor recognition issues
- Some manual validation recommended for critical fields

**Low Confidence (50-70% accuracy expected)**
- Poor document quality or highly non-standard format
- Significant OCR challenges or text recognition issues
- Limited field detection success
- Manual review strongly recommended

#### Field-Level Quality Indicators

**Critical Field Validation:**
- BOL Number: Must be present and alphanumeric
- Shipper Name: Should be a company or organization name
- Consignee Name: Should be a company or organization name

**Format Validation:**
- Dates: Various formats supported (MM/DD/YYYY, DD/MM/YYYY, etc.)
- Weights: Numbers with units (KG, LBS, MT, TON)
- Quantities: Numbers with package types (CTNS, BOXES, PALLETS)

### Accuracy Expectations by Document Type

#### Text-Based PDFs
- **Expected Accuracy**: 85-95%
- **Processing Speed**: 2-5 seconds per document
- **Common Issues**: Non-standard layouts, merged text fields
- **Best Results**: Standard maritime industry BOL templates

#### High-Quality Scanned Documents (300+ DPI)
- **Expected Accuracy**: 75-85%
- **Processing Speed**: 15-30 seconds per document
- **Common Issues**: OCR misreading similar characters (0/O, 1/I)
- **Best Results**: Clean, high-contrast scans with standard fonts

#### Lower Quality Scanned Documents (<300 DPI)
- **Expected Accuracy**: 60-75%
- **Processing Speed**: 20-45 seconds per document
- **Common Issues**: Character recognition errors, field boundary detection
- **Recommendations**: Rescan at higher quality if possible

### Quality Improvement Tips

#### For Scanned Documents
1. **Scan at 300 DPI or higher**: Higher resolution improves OCR accuracy
2. **Ensure proper alignment**: Straight, centered documents work best
3. **Use high contrast settings**: Black text on white background is optimal
4. **Avoid compression artifacts**: Use lossless formats when possible
5. **Clean document surfaces**: Remove staples, folds, or markings before scanning

#### For Digital PDFs
1. **Use searchable PDFs**: Text-based PDFs are always more accurate
2. **Avoid image-only PDFs**: Convert image PDFs to searchable format if possible
3. **Check text selectable**: Ensure text can be selected/copied in PDF viewer
4. **Standard formatting**: Use consistent fonts and layouts

## Troubleshooting

### Common Processing Issues

#### Issue: "No text extracted from PDF"
**Symptoms:**
- Processing completes but no fields are extracted
- All fields show as empty in results
- Low confidence rating

**Possible Causes:**
- PDF is image-only with no text layer
- Document is heavily encrypted or protected
- Scan quality is too poor for OCR recognition

**Solutions:**
1. Enable OCR fallback in processing options
2. Increase OCR processing time limit
3. Rescan document at higher resolution
4. Try converting PDF to different format first

#### Issue: "Processing timeout"
**Symptoms:**
- Processing stops with timeout error
- Large files or complex documents fail
- Batch processing stops mid-way

**Possible Causes:**
- Document too large or complex
- OCR processing taking too long
- System resource limitations

**Solutions:**
1. Process files individually instead of batch
2. Reduce image resolution if possible
3. Split large multi-page documents
4. Try processing during off-peak hours

#### Issue: "Incorrect field extraction"
**Symptoms:**
- Fields contain wrong information
- Data appears in wrong columns
- Mixed up shipper/consignee information

**Possible Causes:**
- Non-standard BOL format
- Poor text recognition quality
- Ambiguous field labels

**Solutions:**
1. Review document format compatibility
2. Manual verification of critical fields
3. Check if document uses standard BOL terminology
4. Consider custom pattern configuration

### File Format Issues

#### Issue: "File not recognized as PDF"
**Symptoms:**
- Upload fails with format error
- File appears but won't process

**Solutions:**
1. Verify file has .pdf extension
2. Try opening file in PDF viewer to confirm validity
3. Convert from other formats (Word, image) to PDF
4. Ensure file isn't corrupted during transfer

#### Issue: "ZIP archive problems"
**Symptoms:**
- ZIP upload successful but no PDFs found
- Some files missing from batch processing

**Solutions:**
1. Extract ZIP manually to verify contents  
2. Ensure all files in ZIP are PDF format
3. Check for nested folders in ZIP structure
4. Verify ZIP file isn't corrupted

### Performance Issues

#### Issue: "Slow processing speed"
**Symptoms:**
- Processing takes much longer than expected
- Browser becomes unresponsive
- Batch processing very slow

**Solutions:**
1. Process smaller batches (25-50 files max)
2. Close other browser tabs/applications
3. Ensure stable internet connection
4. Process during off-peak system usage times

#### Issue: "Memory errors"
**Symptoms:**
- Browser crashes during processing
- "Out of memory" error messages
- Processing stops unexpectedly

**Solutions:**
1. Restart browser and try again
2. Process files in smaller batches
3. Close other browser tabs and applications
4. Try using a different browser

### Getting Help

#### Before Contacting Support
1. **Document the Issue**: Note exact error messages and steps to reproduce
2. **Try Basic Solutions**: Clear browser cache, restart browser, try different files
3. **Check File Quality**: Verify your documents meet quality guidelines
4. **Test with Sample Files**: Try processing with known good documents

#### Information to Provide
- Exact error message or description of issue
- File types and sizes being processed
- Browser type and version
- Steps taken before the issue occurred
- Screenshots of error conditions (if applicable)

## Best Practices

### Document Preparation

#### Before Upload
1. **Review Document Quality**: Ensure PDFs are clear and readable
2. **Check File Names**: Use descriptive, consistent naming conventions  
3. **Organize Files**: Group related documents for batch processing
4. **Verify Content**: Confirm all pages are present and properly oriented

#### Quality Checklist
- [ ] Document is properly oriented (not rotated)
- [ ] All text is clearly visible and readable
- [ ] No pages are missing or duplicated
- [ ] File size is under 50MB
- [ ] Filename uses standard characters only

### Processing Strategy

#### For Single Documents
1. **Use Default Settings**: Start with standard configuration
2. **Enable OCR Fallback**: Ensures processing of all document types
3. **Review Results**: Always check confidence levels and processing notes
4. **Verify Critical Fields**: Double-check BOL numbers and party information

#### For Batch Processing
1. **Start Small**: Test with 5-10 documents first
2. **Group Similar Documents**: Process documents from same source together
3. **Monitor Progress**: Watch for patterns in failed extractions
4. **Process in Segments**: Handle large batches in groups of 25-50 files

### Data Validation

#### Critical Field Verification
Always manually verify these fields for business-critical applications:
- **BOL Number**: Unique identifier for shipping documents
- **Shipper Information**: Company name and contact details
- **Consignee Information**: Destination company and address
- **Vessel and Voyage**: Transportation details
- **Cargo Description**: Goods being shipped

#### Quality Control Process
1. **Spot Check**: Review 10-20% of extractions manually
2. **Focus on Low Confidence**: Prioritize manual review of medium/low confidence results
3. **Pattern Recognition**: Look for consistent extraction issues across similar documents
4. **Field Completion**: Ensure critical fields have high completion rates

### Workflow Optimization

#### Efficient Processing Workflow
1. **Preparation Phase**: Organize files, check quality, name consistently
2. **Processing Phase**: Use appropriate batch sizes, monitor progress
3. **Review Phase**: Check results, identify issues, note patterns
4. **Validation Phase**: Verify critical information, spot-check accuracy
5. **Export Phase**: Choose appropriate format, save with descriptive names

#### Time Management
- **Small Batches (1-10 files)**: Allow 5-15 minutes total
- **Medium Batches (10-50 files)**: Allow 15-45 minutes total  
- **Large Batches (50-100 files)**: Allow 45-90 minutes total
- **Quality Review**: Allow 2-5 minutes per document for manual verification

### Security and Privacy

#### Data Handling
- **Temporary Processing**: Uploaded files are processed temporarily and not permanently stored
- **Secure Transmission**: All data transmitted over encrypted connections
- **No Data Retention**: Processing data is cleared after session completion
- **Privacy Protection**: Personal information in documents is not accessed beyond extraction needs

#### Recommended Practices
1. **Remove Sensitive Information**: Redact unnecessary personal data before processing
2. **Use Secure Networks**: Avoid public WiFi for processing confidential documents
3. **Clear Browser Data**: Clear downloads and cache after processing sensitive documents
4. **Verify Export Contents**: Review exported data before sharing or storing

This comprehensive user guide provides all the information needed to effectively use the BOL OCR Extractor for both individual and batch document processing, ensuring optimal results and efficient workflows.