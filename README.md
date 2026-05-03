# Fair Trial Readiness Tool

## Overview

**Fair Trial Readiness Tool** is an AI‑assisted validation system for **European Court of Human Rights (ECHR) application forms**.  
It helps assess whether a filled form is **formally correct**, **likely admissible**, and **properly framed under Article 6 (Right to a Fair Trial)**.

The tool analyzes **uploaded scanned or printed ECHR application PDFs**, provides **field‑by‑field feedback**, and suggests **corrections and improvements** before submission.

---

## What It Does

- 📄 Accepts **printed or scanned ECHR application forms (PDF)**
- 🔍 Extracts data using **OCR (Tesseract)**
- 🧩 Reconstructs a **canonical ECHR form structure (Sections A–J)**
- 🧠 Uses an LLM to:
  - Validate each field
  - Detect missing, unclear, or incorrect entries
  - Check admissibility‑relevant information
  - Evaluate clarity and framing of **Article 6 claims**
- ✅ Returns **structured feedback and correction suggestions** per field and section

---

## How It Works (Process)

1. **Upload Form**  
   User uploads a scanned / printed ECHR application PDF.

2. **OCR & Normalisation**  
   Pages are converted to images, OCR is applied, and layout noise is cleaned.

3. **Canonical Form Mapping**  
   Extracted text is mapped into a fixed ECHR template (all sections always present).

4. **Prompt Attachment**  
   Each field is paired with a legal/semantic instruction explaining what it should contain.

5. **Section‑wise LLM Analysis**  
   Each section (A–J) is sent separately to the LLM for validation and correction.

6. **Fault‑Tolerant Execution**  
   If one section fails, others continue; errors are captured per section.

7. **Output**  
   The tool returns:
   - Corrected / validated field values
   - Feedback on errors or omissions
   - Suggestions to improve admissibility and Article 6 compliance

---

## Focus Areas

- ✅ Formal completeness of the ECHR form
- ✅ Admissibility‑related requirements
- ✅ Clear and coherent **Article 6 (Fair Trial)** allegations
- ✅ Identification of weaknesses that may lead to rejection

---

## What It Is Not

- ❌ Not legal advice  
- ❌ Not an automated filing system  
- ❌ Not a guarantee of admissibility  

It is a **pre‑submission readiness and quality‑control tool**.

---

## Typical Use Cases

- Lawyers reviewing draft ECHR applications
- NGOs and legal clinics assisting applicants
- Early screening of admissibility risks
- Improving clarity and structure of Article 6 complaints

---

## Configuration

### Environment Variable

```env
GWDG_API_KEY=your_api_key_here