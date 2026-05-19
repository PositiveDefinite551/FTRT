# Fair Trial Readiness Tool

AI-assisted validation and readiness analysis tool for **European Court of Human Rights (ECHR)** application forms.

This project allows users to upload an ECHR application PDF through a Streamlit frontend. The backend extracts and analyses the application data, validates the form section by section, detects missing or incorrect values, and returns structured JSON results.

---

# Project Structure

```text
FTRT/
├── Backend/
│   ├── process_echr_application_file.py
│   └── prompts.json
├── frontend.py
├── README.md
├── requirements.txt
└── .env
```

---

# Features

- Upload ECHR application PDF from browser
- Streamlit-based frontend interface
- Backend processing of application form
- Section-wise ECHR validation
- Structured JSON output
- Display of:
  - given values
  - corrected/suggested values
  - detected issues
  - verification summaries
  - confidence levels
- Raw JSON result viewer
- Optional processing logs
- Temporary PDF handling
- Error-safe frontend rendering for nested JSON data

---

# System Specifications

## Minimum Requirements

| Requirement | Minimum |
|---|---|
| Operating System | Windows 10, Ubuntu 20.04+, macOS 11+ |
| Python | Python 3.9 or higher |
| RAM | 4 GB minimum |
| Storage | 1 GB free space |
| CPU | Dual-core processor |
| Browser | Chrome, Edge, Firefox, or Safari |
| Internet | Required if using online LLM APIs |

---

## Recommended Requirements

| Requirement | Recommended |
|---|---|
| Python | Python 3.10 or 3.11 |
| RAM | 8 GB or more |
| CPU | Quad-core processor |
| Storage | 2 GB free space |
| Internet | Stable internet connection |

---

# Installation

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd FTRT
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_base_url
LLM_MODEL_NAME=your_model_name
TESSERACT_CMD=your_tesseract_path
```

Example for Windows:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

# Tesseract OCR Installation

This project may require Tesseract OCR if scanned PDFs are processed.

---

## Windows

Download and install:

```text
https://github.com/UB-Mannheim/tesseract/wiki
```

Default installation path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## Ubuntu / Debian

```bash
sudo apt update
sudo apt install tesseract-ocr
```

---

## macOS

```bash
brew install tesseract
```

---

# Frontend Details

The frontend is implemented in:

```text
frontend.py
```

The frontend uses **Streamlit** to provide a browser-based user interface.

---

## Frontend Responsibilities

The frontend performs the following operations:

1. Displays application title and description.
2. Accepts ECHR application PDF uploads.
3. Provides sidebar controls for processing logs.
4. Temporarily stores uploaded PDF files.
5. Sends uploaded files to backend processing.
6. Displays:
   - section-wise validation results
   - corrected values
   - detected problems
   - raw JSON output
7. Safely renders nested JSON structures recursively.
8. Deletes temporary files after processing.

---

## Backend Function Call

```python
process_echr_application_form(
    tmp_file_path,
    "Backend/prompts.json",
    enable_logs=enable_logs
)
```

---

# Backend Details

The backend processing logic is located in:

```text
Backend/process_echr_application_file.py
```

---

## Backend Function

```python
process_echr_application_form()
```

### Parameters

| Parameter | Description |
|---|---|
| `pdf_path` | Path to uploaded PDF |
| `prompts_path` | Path to prompts.json |
| `enable_logs` | Enables/disables logs |

---

## Expected Output

```json
{
  "success_response_json": {},
  "failed_response_json": {}
}
```

---

# Running the Application

Activate the virtual environment first.

Then run:

```bash
python -m streamlit run frontend.py
```

Streamlit will display a local URL such as:

```text
http://localhost:8501
```

Open this URL in your browser.

---

# Run Without Keeping Terminal Busy

## Linux / macOS

Run in background:

```bash
nohup python -m streamlit run frontend.py > streamlit.log 2>&1 &
```

View logs:

```bash
tail -f streamlit.log
```

Stop application:

```bash
pkill -f streamlit
```

---

## Windows PowerShell

```powershell
Start-Process python -ArgumentList "-m streamlit run frontend.py"
```

---

# Run on Custom Port

```bash
python -m streamlit run frontend.py --server.port 8501
```

---

# Run for External Access

```bash
python -m streamlit run frontend.py --server.address 0.0.0.0 --server.port 8501
```

Access using:

```text
http://SERVER_IP_ADDRESS:8501
```

---

# Example Workflow

1. Start the application:

```bash
python -m streamlit run frontend.py
```

2. Open the Streamlit URL.

3. Upload an ECHR application PDF.

4. Enable or disable logs.

5. Click:

```text
Analyse Application
```

6. View:
   - processed validation results
   - corrected values
   - raw JSON data

---

# Output Field Format

Each field may contain:

```json
{
  "given_value": "Original extracted value",
  "corrected_value": "Suggested corrected value",
  "problem_in_given_value": "Detected issue",
  "verification_summary": "Explanation of validation",
  "confidence": "high"
}
```

---

# Error Handling

The frontend handles:

- missing uploads
- invalid JSON
- nested JSON rendering
- backend failures
- temporary file cleanup
- field type mismatches

Example error display:

```text
Something went wrong: <error message>
```

---

# Common Issues

## Streamlit Not Found

Install Streamlit:

```bash
pip install streamlit
```

---

## ModuleNotFoundError

Run commands from project root:

```bash
cd FTRT
python -m streamlit run frontend.py
```

---

## Tesseract Not Found

Install Tesseract and configure `.env`:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## API Key Errors

Verify `.env` values:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_base_url
LLM_MODEL_NAME=your_model_name
```

---

# Logging

Processing logs can be enabled from the sidebar.

Logs may include:

- OCR progress
- page processing
- parsing status
- validation steps
- backend execution details
- JSON parsing
- section completion status

---

# Current Limitations

- OCR quality depends on scan quality
- Handwritten text may reduce accuracy
- Large PDFs may increase processing time
- Requires internet for LLM APIs
- Not connected to official ECHR systems
- Does not submit applications automatically

---

# What This Tool Is Not

- Not legal advice
- Not an official ECHR platform
- Not an automated filing system
- Not a guarantee of admissibility
- Not a replacement for legal professionals

---

# Disclaimer

This project is intended for:

- educational use
- research purposes
- legal-tech experimentation
- pre-submission readiness analysis

Users should always consult qualified legal professionals before filing applications before the European Court of Human Rights.

---

# License

This project is intended for research and legal-tech assistance purposes.

Please ensure compliance with:

- local laws
- privacy regulations
- ECHR procedural requirements
- data protection obligations

---

# Author

Developed as an AI-assisted legal-tech project focused on improving ECHR application readiness and admissibility screening.