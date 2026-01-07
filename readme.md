# Transcript PDF Parser

A **robust, parser-grade system** for extracting structured academic transcript data from PDFs.
Designed specifically for **testing PDF parsers**, not just visual inspection.

This project focuses on **structural correctness**, **edge-case handling**, and **repeatable parsing**, making it suitable for real-world transcripts where layout inconsistencies are common.

---

## Features

* Upload and parse academic transcript PDFs
* Robust text extraction using `pypdf`
* Semantic, state-machine–based parsing (not column or spacing dependent)
* Handles:

  * Multi-line course titles
  * Single-line course titles with inline numeric data
  * In-progress courses (missing grades/points)
  * Multiple academic terms
  * Term totals and career totals
* Streamlit UI for:

  * Uploading PDFs
  * Triggering parsing
  * Inspecting raw text, JSON output, and tables
* Output ready for conversion to pandas DataFrames

---

## Project Structure

```
.
├── app.py                 # Streamlit UI
├── parser.py              # Main transcript parser
├── validation_helpers.py  # Structural boundary helpers
├── parsing_helpers.py     # Course / totals parsing helpers
├── README.md
```

---

## Installation

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install streamlit pypdf pandas
```

> Note: `cryptography` is required for AES-encrypted PDFs (very common for transcripts).
> It is installed automatically via `pypdf`, but can be installed explicitly if needed:

```bash
pip install cryptography
```

---

## Running the App

```bash
streamlit run app.py
```

Then open the URL shown in your terminal (usually `http://localhost:8501`).

---

## How It Works

### 1. PDF Text Extraction

* Uses `pypdf.PdfReader`
* Supports encrypted (AES) PDFs
* Extracts raw text exactly as seen by a parser

```python
reader = PdfReader(uploaded_file)
raw_text = "\n".join(page.extract_text() for page in reader.pages)
```

---

### 2. Semantic Parsing (Core Design)

This parser **does not rely on column positions or whitespace alignment**.

Instead, it uses:

* Semantic headers (e.g. `"Beginning of … Record"`)
* Term headers (`Fall 2025`, `Spring 2026`, etc.)
* Course code patterns (`CECS 553`)
* Numeric tails (`3.000 0.000 0.000`)
* Explicit state transitions

This makes the parser resilient to:

* Layout changes
* Line wrapping differences
* Regenerated PDFs
* Overlay-based mock PDFs

---

### 3. Course Parsing Logic (Important)

The parser supports **both** formats:

**Multi-line course**

```
CECS 551 Adv Artificial
Intelligence
3.000 0.000 0.000
```

**Single-line course**

```
CECS 553 Machine Vision 3.000 0.000 0.000
```

This is handled by detecting a **numeric tail at the end of a line**, not by assuming numeric-only rows.

---

## Output Format

### Parsed JSON Structure

```json
{
  "student": {
    "name": "...",
    "student_id": "...",
    "print_date": "DD/MM/YYYY"
  },
  "terms": [
    {
      "term": "Fall 2025",
      "program": "Masters Degree",
      "plan": "Computer Science Major",
      "courses": [...],
      "totals": {...}
    }
  ],
  "career_totals": {...},
  "raw": {
    "warnings": []
  }
}
```

### Pandas-Friendly

The output is designed to be easily flattened into:

* Courses DataFrame
* Term totals DataFrame
* Career totals DataFrame

---

## Streamlit App Features

* Upload transcript PDF
* View raw extracted text
* Click **Parse Transcript**
* Inspect:

  * Parsed JSON
  * Courses table
  * Term totals table
  * Career totals table
  * Parser warnings

Warnings are intentionally exposed to help identify:

* Malformed rows
* Missing numeric data
* Unexpected layout changes

---

## Why This Parser Is Different

Most PDF parsers fail because they assume:

* Fixed column widths
* Clean tables
* Consistent line breaks

This project instead:

* Treats parsing as a **state machine**
* Uses **semantic markers**
* Handles real-world transcript inconsistencies
* Is suitable for **parser testing and regression testing**

---

## Common Use Cases

* Testing PDF parsers against multiple transcript variants
* Generating mock transcripts (overlay-based)
* Validating GPA calculations
* Building ingestion pipelines for academic records
* Debugging PDF extraction edge cases

---

## Known Limitations

* Assumes English transcript text
* Assumes recognizable term headers (`Fall`, `Spring`, `Summer`)
* Assumes numeric values use `x.xxx` formatting

These are intentional constraints for parser reliability.

---

## Future Improvements (Optional)

* Unit tests with real extracted text fixtures
* Batch transcript uploads
* Export parsed data to CSV / JSON
* Regression diffing between transcripts
* Support for undergraduate / transfer records

---