# Fair Trial Readiness Tool

AI-assisted validation and readiness analysis system for **European Court of Human Rights (ECHR)** application forms.

The tool extracts information from scanned or printed ECHR application PDFs, reconstructs the official ECHR form structure, and performs section-wise legal and admissibility-oriented validation using Large Language Models (LLMs).

It is designed as a **pre-submission quality assurance and admissibility screening tool** for lawyers, legal clinics, NGOs, and researchers working with ECHR applications.

---

# Features

- 📄 Parse scanned or printed ECHR application PDFs
- 🔍 OCR-based extraction using Tesseract
- 🧩 Reconstruct canonical ECHR Sections A–J
- 🧠 AI-powered field validation and correction
- ⚖️ Admissibility-oriented review
- 📝 Article 6 (Fair Trial) complaint assessment
- 🚨 Missing/incomplete field detection
- 🔄 Fault-tolerant section-wise LLM execution
- 📦 Modular importable Python API
- 📊 Structured JSON outputs
- 🧾 Detailed processing logs and execution tracking

---

# Project Goal

The purpose of this project is to improve the quality, clarity, and admissibility readiness of ECHR application forms before submission.

The system focuses on:

- formal completeness,
- admissibility-related weaknesses,
- clarity of legal framing,
- and coherence of Article 6 allegations.

This project does **not** provide legal advice or replace professional legal review.

---

# How the System Works

## 1. PDF Upload

The user provides a scanned or printed ECHR application form PDF.

---

## 2. OCR Extraction

Each page is rendered as an image and processed using:

- Tesseract OCR
- PDFPlumber
- PIL

The pipeline extracts all readable text lines from the document.

---

## 3. Text Normalization

OCR artifacts and layout noise are cleaned.

Examples:
- checkbox symbols
- OCR separators
- broken formatting
- page artifacts

---

## 4. Canonical Form Reconstruction

The extracted content is mapped into a fixed nested ECHR structure.

The parser reconstructs sections such as:

- A. Applicant
- B. States
- C. Representatives
- D. Organisation Representatives
- E. Statement of Facts
- F. Alleged Violations
- G. Admissibility
- H. Other Proceedings
- I. Supporting Documents
- J. Final Declaration

All fields are always present in the final structure.

---

## 5. Prompt Attachment

Each field is paired with structured legal and semantic guidance from `prompts.json`.

These prompts include:

- admissibility guidance
- application notes
- common mistakes
- relevant case-law hints

---

## 6. Section-wise LLM Validation

Each top-level ECHR section is sent independently to the LLM.

The LLM performs:

- validation,
- normalization,
- correction,
- completeness checks,
- admissibility-oriented review,
- and clarity analysis.

---

## 7. Fault-Tolerant Processing

If one section fails:

- remaining sections continue processing,
- errors are captured separately,
- successful sections are preserved.

---

## 8. Structured Output

The system returns:

```json
{
  "success_response_json": {...},
  "failed_response_json": {...}
}
```

Each validated field includes:

- given value
- corrected value
- detected issues
- verification summary
- confidence level

---

# Example Output Structure

```json
{
  "given_value": "Mr Jon Do",
  "corrected_value": "Mr John Doe",
  "problem_in_given_value": "OCR spelling error detected",
  "verification_summary": "Corrected probable OCR mistake in surname",
  "confidence": "high"
}
```

---

# Technology Stack

## OCR & PDF Processing

- Python
- Tesseract OCR
- PDFPlumber
- Pillow (PIL)

---

## AI / LLM

- OpenAI-compatible APIs
- Section-wise prompt engineering
- Structured JSON generation

---

## Data Handling

- JSON-based canonical schema
- Prompt attachment pipeline
- Fault-tolerant response parsing

---

# Project Structure

```text
project/
│
├── Backend/
│   ├── echr_application_parser.py
│   ├── prompts.json
│   ├── sample data/
│   ├── app data/
│   └── notebooks/
│
├── README.md
├── requirements.txt
└── .env
```

---

# Installation

## 1. Clone Repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

---

## 2. Create Virtual Environment

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

# Tesseract Installation

Install Tesseract OCR:

## Windows

Download:
- https://github.com/UB-Mannheim/tesseract/wiki

Default path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## Linux

```bash
sudo apt install tesseract-ocr
```

---

## macOS

```bash
brew install tesseract
```

---

# Environment Variables

Create a `.env` file:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_base_url
LLM_MODEL_NAME=llama-3.3-70b-instruct
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

# Usage

## As a Python Module

```python
from echr_application_parser import process_echr_application_form

result = process_echr_application_form(
    form_file_path="sample data/form.pdf",
    prompts_json_path="app data/prompts.json",
)

print(result["success_response_json"])
print(result["failed_response_json"])
```

---

# Logging & Execution Visibility

The pipeline includes detailed execution logs:

- OCR progress
- page-by-page tracking
- extracted fields
- prompt generation
- LLM processing progress
- retry handling
- parsing success/failure summaries

Example:

```text
🚀 STEP 1 — OCR EXTRACTION
📌 OCR Processing Page 1/14
✅ Page completed successfully
```

Logs can be disabled:

```python
process_echr_application_form(
    ...,
    enable_logs=False,
)
```

---

# Typical Use Cases

- Lawyers reviewing ECHR applications
- NGOs assisting applicants
- Legal aid clinics
- Admissibility risk screening
- Article 6 complaint structuring
- Pre-submission quality control

---

# Focus Areas

The system is particularly focused on:

- admissibility readiness,
- procedural completeness,
- legal clarity,
- and Article 6 fair trial allegations.

---

# What This Tool Is NOT

- ❌ Not legal advice
- ❌ Not an automated filing system
- ❌ Not an official ECHR service
- ❌ Not a guarantee of admissibility
- ❌ Not a replacement for legal counsel

This is a legal-tech assistance and readiness tool.

---

# Error Handling

The system is designed to be resilient.

If:
- one section fails,
- OCR partially fails,
- or JSON parsing fails,

the remaining pipeline continues processing.

Failures are captured inside:

```python
failed_response_json
```

---

# Current Limitations

- Optimized for printed/scanned ECHR forms
- Assumes relatively stable ECHR form layout
- OCR quality depends on scan quality
- Some handwritten content may reduce accuracy
- Current parser contains rule-based extraction for several sections

---

# Future Improvements

- Handwriting support
- Better layout detection
- Multi-language OCR
- Retrieval-augmented legal references
- GUI/Web interface
- Full admissibility scoring
- Fine-tuned legal models
- Vector-search case-law integration

---

# License

This project is intended for research, educational, and legal-tech assistance purposes.

Please ensure compliance with:
- local legal regulations,
- privacy obligations,
- and ECHR procedural requirements.

---

# Disclaimer

This project does not constitute legal advice.

Users should always consult qualified legal professionals before filing applications before the European Court of Human Rights.

---

# Author

Developed as an AI-assisted legal-tech project for improving ECHR application readiness and admissibility screening.