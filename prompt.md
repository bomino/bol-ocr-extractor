                                                                                                                                                                                           You are an expert Python developer specializing in automation tools for document processing. Your task is to create a complete, functional Python application that automates the extraction of data from PDF files containing Bills of Lading (BOLs) and exports the extracted data to an Excel file. The app should handle multiple PDFs in batch mode, support both text-based and scanned (image-based) PDFs, and be user-friendly with a simple graphical user interface (GUI).

### Requirements:
1. **Input Handling**:
   - Allow the user to select a single PDF file or a folder containing multiple PDF files.
   - Support batch processing: If a folder is selected, process all PDFs inside it and compile the data into a single Excel file (one row per BOL/PDF).

2. **PDF Parsing**:
   - Use libraries like `pdfplumber` for extracting text from text-based PDFs.
   - For scanned PDFs (where text extraction fails or is incomplete), integrate OCR using `pytesseract` and `Pillow` to convert images to text.
   - Automatically detect if OCR is needed: If initial text extraction yields little or no text, fall back to OCR.

3. **Data Extraction**:
   - Extract the following key fields from each BOL using regex patterns, keyword searching, or layout-based parsing (customize patterns based on common BOL structures):
     - Bill of Lading Number (e.g., search for "B/L No:", "BOL#", etc.)
     - Shipper Name and Address
     - Consignee Name and Address
     - Notify Party Name and Address
     - Vessel Name and Voyage Number
     - Port of Load
     - Port of Discharge
     - Description of Goods (may be multi-line or in a table)
     - Quantity/Packages
     - Weight (Gross/Net)
     - Freight Terms (e.g., Prepaid, Collect)
     - Date of Issue
   - Handle variations in layouts: Use flexible regex to account for different formats (e.g., fields might be labeled as "SHIPPER:", "Consignee:", etc.).
   - If tables are present (common in BOLs for goods description), use `tabula-py` to extract tabular data.
   - Store extracted data in a dictionary or structured format for each PDF.

4. **Output**:
   - Use `pandas` to create a DataFrame from the extracted data.
   - Export the DataFrame to an Excel file (.xlsx) with columns matching the extracted fields.
   - Include a column for the PDF filename or a unique identifier for traceability.
   - If extraction fails for a PDF (e.g., poor quality scan), log an error and add a row with "Extraction Failed" notes.

5. **GUI**:
   - Build a web-based GUI using `streamlit` for ease of use (preferred over tkinter for modern feel).
   - Interface elements:
     - Upload button for single PDF or folder selection (Streamlit supports file uploads; for folders, guide user to upload a zip or process individually if needed—alternatively, allow command-line for batches).
     - Button to start extraction.
     - Display progress (e.g., via spinner or status messages).
     - Download button for the generated Excel file.
     - Show a preview of extracted data in a table before downloading.

6. **Error Handling and Robustness**:
   - Handle exceptions gracefully (e.g., invalid PDF, missing fields).
   - Provide logging: Print or display warnings for missing data or OCR usage.
   - Ensure the app is efficient for up to 100 PDFs (optimize memory and processing).
   - Include comments in the code explaining each section.

7. **Dependencies**:
   - List all required libraries at the top (e.g., pdfplumber, pandas, re, tabula-py, pytesseract, Pillow, streamlit).
   - Assume the user will install them via pip (provide installation instructions in comments).
   - For OCR, note that Tesseract engine must be installed separately on the system.

8. **Additional Features**:
   - Make the regex patterns configurable (e.g., via a dictionary) so users can tweak them for specific BOL templates.
   - Option to export to CSV as an alternative.
   - Basic validation: Flag if key fields like BOL Number are missing.

### Output Format:
- Write the complete Python script in a single file (e.g., app.py).
- Include detailed comments throughout the code.
- At the end, provide usage instructions: How to run the app (e.g., `streamlit run app.py`), how to install dependencies, and example workflows.
- Explain any assumptions or limitations (e.g., OCR accuracy depends on PDF quality).
- If needed, suggest improvements like integrating AI APIs for better parsing (but keep the core app library-based).

Generate the code now, ensuring it's tested in your mind for functionality.                                                              
