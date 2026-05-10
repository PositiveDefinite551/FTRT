"""
ECHR Application Form Parser
============================

Parses scanned/printed ECHR application forms, attaches prompts,
runs section-wise LLM verification, and returns:

{
    "success_response_json": {...},
    "failed_response_json": {...}
}
"""

from __future__ import annotations

import json
import os
import re
import traceback
from datetime import datetime, time
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

import pdfplumber
import pytesseract
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


# =============================================================================
# Configuration
# =============================================================================

load_dotenv()

DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

DEFAULT_SYSTEM_PROMPT = (
    "You are a legal assistant helping to complete a European Court of Human "
    "Rights application form. You must return strictly valid JSON only."
)

GUIDELINE_KEYS = [
    "admissibility_guide",
    "application_notes",
    "common_mistakes",
    "case_law",
]

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")

TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# =============================================================================
# Console Logging Helpers
# =============================================================================

ENABLE_LOGS = False


def log_header(title: str) -> None:
    if not ENABLE_LOGS:
        return

    line = "=" * 80
    print(f"\n{line}")
    print(f"{title}")
    print(line)


def log_section(title: str) -> None:
    if not ENABLE_LOGS:
        return

    print(f"\n {title}")
    print("-" * 60)


def log_step(message: str) -> None:
    if not ENABLE_LOGS:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] * {message}")


def log_success(message: str) -> None:
    if not ENABLE_LOGS:
        return

    print(f" {message}")


def log_warning(message: str) -> None:
    if not ENABLE_LOGS:
        return

    print(f"  {message}")


def log_error(message: str) -> None:
    if not ENABLE_LOGS:
        return

    print(f" {message}")


# =============================================================================
# Type Definitions
# =============================================================================

JsonDict = Dict[str, Any]


class SectionLLMResults(TypedDict):
    responses: Dict[str, str]
    errors: Dict[str, JsonDict]


class FinalProcessingResult(TypedDict):
    success_response_json: JsonDict
    failed_response_json: JsonDict


# =============================================================================
# OCR and Text Normalization
# =============================================================================

def clean_line(line: str) -> str:
    return (
        line.replace("©)", "")
        .replace("@)", "")
        .replace("|", "")
        .strip()
    )


def extract_lines_from_pdf(
    pdf_path: str | Path,
    resolution: int = 300,
) -> List[str]:

    lines: List[str] = []
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    log_header("STEP 1 — OCR EXTRACTION")
    log_step(f"Opening PDF file: {pdf_path}")

    with pdfplumber.open(str(pdf_path)) as pdf:
        total_pages = len(pdf.pages)

        log_success("PDF loaded successfully")
        log_step(f"Total pages detected: {total_pages}")
        log_step(f"OCR resolution: {resolution} DPI")

        for page_index, page in enumerate(pdf.pages, start=1):
            log_section(f"OCR Processing Page {page_index}/{total_pages}")

            image: Image.Image = page.to_image(
                resolution=resolution
            ).original

            log_step("Running Tesseract OCR...")

            text = pytesseract.image_to_string(image, lang="eng")
            page_lines = 0

            for raw_line in text.splitlines():
                line = raw_line.strip()
                if line:
                    lines.append(line)
                    page_lines += 1

            remaining_pages = total_pages - page_index

            log_success(
                f"Page {page_index}/{total_pages} completed "
                f"({page_lines} lines extracted)"
            )
            log_step(f"Pages remaining: {remaining_pages}")

    log_success(
        f"OCR completed successfully. Total extracted lines: {len(lines)}"
    )

    return lines


# =============================================================================
# Generic Parsing Helpers
# =============================================================================

def value_after(
    lines: List[str],
    label: str,
    stop_regex: str = r"^\d+\.|^[A-Z]\.",
    max_following_lines: int = 8,
) -> Optional[str]:

    for index, line in enumerate(lines):
        if label in line:
            collected: List[str] = []

            for next_line in lines[index + 1: index + 1 + max_following_lines]:
                if re.search(stop_regex, next_line):
                    break

                collected.append(clean_line(next_line))

            value = " ".join(collected).strip()
            return value or None

    return None


def extract_section_block(
    lines: List[str],
    start_marker: str,
    end_marker: str,
) -> Optional[str]:

    captured: List[str] = []
    is_capturing = False

    for line in lines:
        if line.startswith(start_marker):
            is_capturing = True
            continue

        if is_capturing and line.startswith(end_marker):
            break

        if is_capturing:
            captured.append(clean_line(line))

    value = " ".join(captured).strip()
    return value or None


# =============================================================================
# ECHR Form Template
# =============================================================================

def echr_form_template() -> JsonDict:
    return {
        "A. Applicant": {
            "A.1 Individual": {
                "Surname": None,
                "First name(s)": None,
                "Date of birth": None,
                "Place of birth": None,
                "Nationality": None,
                "Address": None,
                "Telephone": None,
                "Email": None,
                "Sex": None,
            },
            "A.2 Organisation": {
                "Name": None,
                "Identification number": None,
                "Date of registration": None,
                "Activity": None,
                "Registered address": None,
                "Telephone": None,
                "Email": None,
            },
        },
        "B. States": {
            "Selected": [],
            "Available": [
                "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan",
                "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia",
                "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland",
                "France", "Georgia", "Germany", "Greece", "Hungary",
                "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein",
                "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco",
                "Montenegro", "Netherlands", "North Macedonia", "Norway",
                "Poland", "Portugal", "Romania", "San Marino", "Serbia",
                "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",
                "Türkiye", "Ukraine", "United Kingdom",
            ],
        },
        "C. Representative (Individual applicant)": {
            "C.1 Non-lawyer": {
                "Capacity / relationship": None,
                "Surname": None,
                "First name(s)": None,
                "Nationality": None,
                "Address": None,
                "Telephone": None,
                "Fax": None,
                "Email": None,
            },
            "C.2 Lawyer": {
                "Surname": None,
                "First name(s)": None,
                "Nationality": None,
                "Address": None,
                "Telephone": None,
                "Fax": None,
                "Email": None,
                "eComms email": None,
            },
        },
        "D. Representative (Organisation)": {
            "D.1 Organisation official": {
                "Capacity / function": None,
                "Surname": None,
                "First name(s)": None,
                "Nationality": None,
                "Address": None,
                "Telephone": None,
                "Fax": None,
                "Email": None,
            },
            "D.2 Lawyer": {
                "Surname": None,
                "First name(s)": None,
                "Nationality": None,
                "Address": None,
                "Telephone": None,
                "Fax": None,
                "Email": None,
            },
        },
        "E. Statement of facts": None,
        "F. Alleged violations": {
            "Article 61": None,
            "Article 62": None,
        },
        "G. Admissibility": {
            "Complaints summary": None,
            "Unused remedies": None,
            "Why unused": None,
        },
        "H. Other international proceedings": {
            "Any proceedings": None,
            "Details": None,
            "Other ECHR applications": None,
            "Application numbers": None,
        },
        "I. List of accompanying documents": [],
        "J. Final declaration": {
            "Additional comments": None,
            "Date": None,
            "Signed by": None,
            "Correspondence contact": None,
        },
    }


# =============================================================================
# Template Population
# =============================================================================

def fill_template(template: JsonDict, lines: List[str]) -> JsonDict:

    log_header("STEP 2 — FORM FIELD EXTRACTION")
    log_step(f"Total OCR lines available for parsing: {len(lines)}")

    log_section("Extracting A.1 Individual Applicant")

    individual = template["A. Applicant"]["A.1 Individual"]

    individual["Surname"] = value_after(lines, "1. Surname")
    individual["First name(s)"] = value_after(lines, "2. First name")
    individual["Date of birth"] = value_after(lines, "3. Date of birth")
    individual["Place of birth"] = value_after(lines, "4. Place of birth")
    individual["Nationality"] = value_after(lines, "5. Nationality")
    individual["Address"] = value_after(lines, "6. Address")
    individual["Telephone"] = value_after(lines, "7. Telephone")
    individual["Email"] = value_after(lines, "8. Email")

    for line in lines:
        lower_line = line.lower()
        if "female" in lower_line:
            individual["Sex"] = "female"
        elif "male" in lower_line:
            individual["Sex"] = "male"

    log_step(f"Surname: {individual['Surname']}")
    log_step(f"First name(s): {individual['First name(s)']}")
    log_step(f"Date of birth: {individual['Date of birth']}")
    log_step(f"Nationality: {individual['Nationality']}")
    log_step(f"Email: {individual['Email']}")
    log_success("A.1 Individual Applicant extracted")

    log_section("Extracting B. States")

    if any("GEO - Georgia" in line for line in lines):
        template["B. States"]["Selected"].append("Georgia")
        log_success("Detected selected state: Georgia")
    else:
        log_warning("No selected state detected using current rules")

    log_section("Extracting C.2 Lawyer")

    lawyer = template["C. Representative (Individual applicant)"]["C.2 Lawyer"]

    lawyer["Surname"] = value_after(lines, "26. Surname")
    lawyer["First name(s)"] = value_after(lines, "27. First name")
    lawyer["Nationality"] = value_after(lines, "28. Nationality")
    lawyer["Telephone"] = value_after(lines, "30. Telephone")
    lawyer["Email"] = value_after(lines, "32. Email")
    lawyer["eComms email"] = value_after(lines, "37. Email")

    log_step(f"Lawyer surname: {lawyer['Surname']}")
    log_step(f"Lawyer first name(s): {lawyer['First name(s)']}")
    log_step(f"Lawyer email: {lawyer['Email']}")
    log_success("C.2 Lawyer section extracted")

    log_section("Extracting E. Statement of Facts")

    template["E. Statement of facts"] = extract_section_block(
        lines,
        start_marker="E. Statement of the facts",
        end_marker="European Court of Human Rights - Application form 6",
    )

    if template["E. Statement of facts"]:
        log_success("Statement of facts extracted")
        log_step(
            f"Statement length: "
            f"{len(template['E. Statement of facts'])} characters"
        )
    else:
        log_warning("Statement of facts not detected")

    log_section("Extracting F. Alleged Violations")

    template["F. Alleged violations"]["Article 61"] = value_after(
        lines,
        "material aspect of Article 2",
        stop_regex=r"procedural|62\.",
    )

    template["F. Alleged violations"]["Article 62"] = value_after(
        lines,
        "procedural aspect of Article 2",
        stop_regex=r"G\.",
    )

    log_step(
        f"Article 61 detected: "
        f"{bool(template['F. Alleged violations']['Article 61'])}"
    )
    log_step(
        f"Article 62 detected: "
        f"{bool(template['F. Alleged violations']['Article 62'])}"
    )
    log_success("F. Alleged Violations extracted")

    log_section("Extracting G. Admissibility")

    template["G. Admissibility"]["Unused remedies"] = (
        "Yes" if any("©) Yes" in line for line in lines) else "No"
    )

    log_step(
        f"Unused remedies answer: "
        f"{template['G. Admissibility']['Unused remedies']}"
    )
    log_success("G. Admissibility extracted")

    log_success("Form field extraction completed")

    return template


def parse_echr_application(pdf_path: str | Path) -> JsonDict:
    lines = extract_lines_from_pdf(pdf_path)

    log_step("Creating canonical ECHR form template")
    template = echr_form_template()

    return fill_template(template, lines)


# =============================================================================
# Prompt Attachment and Rendering
# =============================================================================

def is_prompt_object(node: Any) -> bool:
    return isinstance(node, dict) and set(GUIDELINE_KEYS).issubset(node.keys())


def attach_prompts_to_output(
    output_dict: JsonDict,
    prompts_dict: JsonDict,
) -> JsonDict:

    log_header("STEP 3 — ATTACHING PROMPTS TO FORM DATA")

    attached_count = 0
    total_leaf_fields = 0

    def recurse(output_node: Any, prompt_node: Any) -> Any:
        nonlocal attached_count, total_leaf_fields

        if isinstance(output_node, dict):
            merged: JsonDict = {}

            for key, value in output_node.items():
                child_prompt = (
                    prompt_node.get(key)
                    if isinstance(prompt_node, dict)
                    else None
                )
                merged[key] = recurse(value, child_prompt)

            if is_prompt_object(prompt_node):
                merged["prompts"] = prompt_node
                attached_count += 1

            return merged

        total_leaf_fields += 1

        if is_prompt_object(prompt_node):
            attached_count += 1

        return {
            "value": output_node,
            "prompts": prompt_node if is_prompt_object(prompt_node) else None,
        }

    result = recurse(output_dict, prompts_dict)

    log_success("Prompt attachment completed")
    log_step(f"Total leaf fields processed: {total_leaf_fields}")
    log_step(f"Prompt objects attached: {attached_count}")

    return result


def render_prompt_content(node: Any, indent: int = 0) -> str:
    pad = "  " * indent
    output: List[str] = []

    if isinstance(node, dict) and "value" in node:
        output.append(
            f"{pad}given_value: "
            f"{json.dumps(node.get('value'), ensure_ascii=False)}"
        )

        prompts = node.get("prompts", {})

        if isinstance(prompts, dict):
            output.append(f"{pad}verification_guidelines:")
            for key in GUIDELINE_KEYS:
                output.append(
                    f"{pad}  {key}: "
                    f"{json.dumps(prompts.get(key), ensure_ascii=False)}"
                )

        return "\n".join(output)

    if isinstance(node, dict):
        for key, value in node.items():
            if key == "prompts":
                continue

            output.append(f"{pad}{key}:")
            output.append(render_prompt_content(value, indent + 1))

        return "\n".join(output)

    return f"{pad}given_value: {json.dumps(node, ensure_ascii=False)}"


def extract_output_structure(node: Any) -> Any:
    if isinstance(node, dict) and "value" in node:
        return {
            "given_value": node.get("value"),
            "corrected_value": None,
            "problem_in_given_value": None,
            "verification_summary": None,
            "confidence": None,
        }

    if isinstance(node, dict):
        return {
            key: extract_output_structure(value)
            for key, value in node.items()
            if key != "prompts"
        }

    return {
        "given_value": node,
        "corrected_value": None,
        "problem_in_given_value": None,
        "verification_summary": None,
        "confidence": None,
    }


def build_single_section_prompt(
    section_name: str,
    section_body: Any,
) -> str:

    section_structure = extract_output_structure(section_body)

    return f"""
You are completing the European Court of Human Rights application form.

Section: {section_name}
{"-" * 40}

Task:
For each field below:
1. Read the user's given value.
2. Check it against the verification guidelines.
3. Correct the value if it is incomplete, noisy, wrongly formatted, or obviously incorrect.
4. If the value is missing and cannot be inferred, use null.
5. Explain briefly what was wrong, if anything.

Input values and verification guidelines:
{render_prompt_content(section_body, indent=0)}

Return ONLY valid JSON.

The JSON must keep the same section structure as below.

For every field, return this object format:
{{
  "given_value": "...",
  "corrected_value": "...",
  "problem_in_given_value": "...",
  "verification_summary": "...",
  "confidence": "high | medium | low"
}}

Required output structure:
{json.dumps(section_structure, ensure_ascii=False, indent=2)}
""".strip()


def build_section_prompts(prompted_output: JsonDict) -> Dict[str, str]:

    log_header("STEP 4 — BUILDING SECTION PROMPTS")

    section_prompts: Dict[str, str] = {}
    total_sections = len(prompted_output)

    for index, (section_name, section_body) in enumerate(
        prompted_output.items(),
        start=1,
    ):
        log_section(f"Building Prompt {index}/{total_sections}")
        log_step(f"Section name: {section_name}")

        section_prompts[section_name] = build_single_section_prompt(
            section_name=section_name,
            section_body=section_body,
        )

        prompt_length = len(section_prompts[section_name])

        log_success(f"Prompt built for section: {section_name}")
        log_step(f"Prompt size: {prompt_length} characters")
        log_step(f"Remaining prompts: {total_sections - index}")

    log_success(f"All section prompts generated: {total_sections}")

    return section_prompts


# =============================================================================
# LLM Handling
# =============================================================================

def get_openai_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OpenAI:

    resolved_api_key = api_key or LLM_API_KEY
    resolved_base_url = base_url or LLM_BASE_URL

    if not resolved_api_key:
        raise RuntimeError("LLM API key not found. Set LLM_API_KEY.")

    if resolved_base_url:
        return OpenAI(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
        )

    return OpenAI(api_key=resolved_api_key)


def get_llm_section_response(
    model_name: str,
    system_prompt: str,
    section_prompt: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> str:

    client = get_openai_client(
        api_key=api_key,
        base_url=base_url,
    )

    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": section_prompt},
        ],
        temperature=0.1,
        top_p=1,
    )

    content = chat_completion.choices[0].message.content
    return (content or "").strip()


def get_llm_responses_for_all_sections(
    model_name: str,
    system_prompt: str,
    section_prompts: Dict[str, str],
    max_retries: int = 1,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> SectionLLMResults:

    log_header("STEP 5 — LLM SECTION PROCESSING")

    responses: Dict[str, str] = {}
    errors: Dict[str, JsonDict] = {}

    total_sections = len(section_prompts)
    completed_sections = 0

    log_step(f"Model: {model_name}")
    log_step(f"Total sections to process: {total_sections}")
    log_step(f"Maximum retries per section: {max_retries}")

    for section_index, (section_name, section_prompt) in enumerate(
        section_prompts.items(),
        start=1,
    ):
        log_section(
            f"Processing Section {section_index}/{total_sections}: "
            f"{section_name}"
        )

        for attempt in range(max_retries + 1):
            log_step(
                f"Sending LLM request "
                f"(attempt {attempt + 1}/{max_retries + 1})"
            )

            try:
                response = get_llm_section_response(
                    model_name=model_name,
                    system_prompt=system_prompt,
                    section_prompt=section_prompt,
                    api_key=api_key,
                    base_url=base_url,
                )

                responses[section_name] = response
                completed_sections += 1

                progress = completed_sections / total_sections * 100

                log_success(
                    f"Section completed successfully: {section_name}"
                )
                log_step(
                    f"Progress: {completed_sections}/{total_sections} "
                    f"sections completed ({progress:.1f}%)"
                )
                log_step(
                    f"Sections remaining: "
                    f"{total_sections - completed_sections}"
                )

                break

            except Exception as exc:
                log_warning(
                    f"Attempt {attempt + 1} failed for section: "
                    f"{section_name}"
                )
                log_error(str(exc))

                is_last_attempt = attempt == max_retries

                if is_last_attempt:
                    errors[section_name] = {
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }

                    completed_sections += 1

                    log_error(
                        f"Section permanently failed after "
                        f"{max_retries + 1} attempts: {section_name}"
                    )

        log_step(
            f"Overall processed sections: "
            f"{section_index}/{total_sections}"
        )

    log_header("LLM PROCESSING SUMMARY")
    log_success(f"Successful raw LLM responses: {len(responses)}")
    log_warning(f"Failed LLM sections: {len(errors)}")

    return {
        "responses": responses,
        "errors": errors,
    }


# =============================================================================
# JSON Parsing Helpers
# =============================================================================

def parse_llm_json_response(text: str) -> JsonDict:

    cleaned_text = text.strip()
    cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
    cleaned_text = re.sub(r"^```\s*", "", cleaned_text)
    cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

    parsed = json.loads(cleaned_text)

    if not isinstance(parsed, dict):
        raise ValueError("Expected LLM response JSON to be a dictionary.")

    return parsed


def parse_successful_and_failed_responses(
    llm_results: SectionLLMResults,
) -> FinalProcessingResult:

    log_header("STEP 6 — PARSING LLM JSON RESPONSES")

    success_response_json: JsonDict = {}
    failed_response_json: JsonDict = dict(llm_results.get("errors", {}))

    raw_responses = llm_results.get("responses", {})
    total_responses = len(raw_responses)

    log_step(f"Raw successful LLM responses to parse: {total_responses}")

    for index, (section_name, response_text) in enumerate(
        raw_responses.items(),
        start=1,
    ):
        log_section(f"Parsing JSON {index}/{total_responses}: {section_name}")

        try:
            success_response_json[section_name] = parse_llm_json_response(
                response_text
            )
            log_success(f"JSON parsed successfully for: {section_name}")

        except Exception as exc:
            failed_response_json[section_name] = {
                "error": f"Failed to parse LLM JSON response: {exc}",
                "raw_response": response_text,
                "traceback": traceback.format_exc(),
            }

            log_error(f"JSON parsing failed for: {section_name}")
            log_error(str(exc))

        log_step(f"JSON responses remaining: {total_responses - index}")

    log_success(f"Parsed successful JSON sections: {len(success_response_json)}")
    log_warning(f"Total failed sections/errors: {len(failed_response_json)}")

    return {
        "success_response_json": success_response_json,
        "failed_response_json": failed_response_json,
    }


# =============================================================================
# File Loading Helpers
# =============================================================================

def load_json_file(file_path: str | Path) -> JsonDict:

    file_path = Path(file_path)

    log_step(f"Loading JSON file: {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON root object to be a dictionary: {file_path}"
        )

    log_success(f"JSON file loaded successfully: {file_path}")

    return data


# =============================================================================
# Public Orchestration Function
# =============================================================================

def process_echr_application_form(
    form_file_path: str | Path,
    prompts_json_path: str | Path,
    model_name: str = DEFAULT_MODEL_NAME,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    max_retries: int = 2,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    enable_logs: bool = False,
) -> FinalProcessingResult:
    
    global ENABLE_LOGS
    ENABLE_LOGS = enable_logs
    log_header("ECHR APPLICATION PROCESSING PIPELINE")

    log_step(f"Form file path: {form_file_path}")
    log_step(f"Prompts file path: {prompts_json_path}")
    log_step(f"Selected model: {model_name}")

    log_step("Starting PDF parsing and OCR extraction")
    form_data = parse_echr_application(form_file_path)

    log_step("Loading prompts JSON")
    prompts = load_json_file(prompts_json_path)

    log_step("Attaching prompts to extracted form data")
    form_data_with_prompts = attach_prompts_to_output(
        form_data,
        prompts,
    )

    log_step("Building section-wise LLM prompts")
    section_prompts = build_section_prompts(form_data_with_prompts)

    log_step("Sending section prompts to LLM")
    llm_results = get_llm_responses_for_all_sections(
        model_name=model_name,
        system_prompt=system_prompt,
        section_prompts=section_prompts,
        max_retries=max_retries,
        api_key=api_key,
        base_url=base_url,
    )

    log_step("Parsing successful and failed LLM outputs")
    final_result = parse_successful_and_failed_responses(llm_results)

    log_header("FINAL PIPELINE SUMMARY")
    log_success(
        f"Successful parsed sections: "
        f"{len(final_result['success_response_json'])}"
    )
    log_warning(
        f"Failed sections/errors: "
        f"{len(final_result['failed_response_json'])}"
    )
    log_success("ECHR application processing completed")

    return final_result


# =============================================================================
# This is only for testing. It won't run when imported as a module, but allows quick execution of the entire pipeline when this script is run directly.
# =============================================================================

if __name__ == "__main__":
    print("Using llm model:", DEFAULT_MODEL_NAME)
    print("Base URL:", LLM_BASE_URL)
    start_time = time.time()
    result = process_echr_application_form(
        form_file_path="sample data/printed Filled ECHR application form.pdf",
        prompts_json_path="app data/prompts.json",
        enable_logs= True
    )
    end_time = time.time()
    total_seconds = round(end_time - start_time, 2)
    
    print(f"\n\nProcessing Time: {total_seconds} seconds")
    print("\n\nFinal Result")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
   
    # ------------------------------------------------------------------
    # Create History folder if it does not exist
    # ------------------------------------------------------------------

    history_dir = Path("History")
    history_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Generate timestamped filename
    # ------------------------------------------------------------------

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    output_file = history_dir / f"echr_result_{timestamp}.json"

    history_payload = {
    "metadata": {
        "timestamp": timestamp,
        "model_name": DEFAULT_MODEL_NAME,
        "base_url": LLM_BASE_URL,
        "generation_time_seconds": total_seconds,
    },
    "result": result,
    }

    # ------------------------------------------------------------------
    # Save result
    # ------------------------------------------------------------------

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(history_payload, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Result saved successfully:")
    print(f"📁 {output_file}")