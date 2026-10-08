# WorkingDay

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![Chrome MV3](https://img.shields.io/badge/Chrome_Extension-MV3-yellow.svg)](https://developer.chrome.com/docs/extensions/mv3/)

**WorkingDay** is an open-source, candidate-side resume parser and Chrome extension that autofills Workday-style job applications with significantly higher accuracy than Workday's built-in resume autofill.

> **Disclaimer**: WorkingDay is an independent, candidate-side tool and is **not affiliated with or endorsed by Workday, Inc.**

---

## 🎯 Core Principles

1. **Never Invent Data**: If a value is not present in the resume (e.g., no street address or no education start date), it remains `null` with an `empty_in_resume` provenance flag. Never takes text from filenames or PDF metadata.
2. **Confidence Scores & Provenance**: Every extracted field carries `{ value, confidence, source_span, flag }`. Low-confidence fields are visibly highlighted in amber for user review.
3. **Multiword Integrity**: Compound organization and title strings (such as `"Google Developer Student Club"`, `"Handshake AI"`, `"The University of Texas at Dallas"`, `"iCode [North Dallas]"`) are preserved intact and never split across spaces.
4. **User-Approved Autofill**: WorkingDay never auto-submits job applications. It displays an interactive review overlay and only populates form fields upon explicit candidate approval.

---

## 📊 Benchmark Evaluation Results

Evaluated against ground truth on Case #1 (real Workday autofill failure modes):

| Parser System | Matches / Total | Field-Level Accuracy | Multiword Company Integrity | Null Address Integrity |
| :--- | :---: | :---: | :---: | :---: |
| **Naive Token + Regex Baseline** | 4/14 | **28.6%** | ❌ Truncated / Split | ❌ False Street Injected |
| **Workday Built-in Autofill (Recorded)** | 4/14 | **28.6%** | ❌ Truncated (e.g. `'Google'`) | ❌ Injected `'14 AMresumepdf'` |
| **WorkingDay Parser (Ours)** | 14/14 | **100.0%** | ✅ 100% Intact | ✅ 100% (No Hallucination) |

---

## 🏗️ Monorepo Architecture

```
WorkingDay/
├── parser/                  # FastAPI & Pydantic v2 Ingestion & Parsing Engine
│   ├── src/workingday_parser/
│   │   ├── ingest/          # PyMuPDF block/bbox extraction, PDF links, DOCX, bullets
│   │   ├── segment/         # Layout & heading-based section classification
│   │   ├── rules/           # Specific rules: name, address, experience, education, links
│   │   ├── extract/         # Structured extraction orchestrator & schema validation
│   │   ├── llm/             # Schema-constrained LLM fallback interface
│   │   └── main.py          # FastAPI application endpoints
│   └── tests/               # Pytest suite with 16+ unit and end-to-end tests
│
├── extension/               # Chrome MV3 Extension (TypeScript + Vite)
│   ├── src/content/         # React-controlled input filler, fuzzy dropdowns, review overlay
│   ├── src/popup/           # Extension popup with resume upload & candidate name switcher
│   └── src/background/      # MV3 Service worker
│
├── sandbox/                 # React + TypeScript + Vite Workday-style mock portal
│   └── src/                 # Multi-step application form with real data-automation-ids
│
└── eval/                    # Evaluation benchmark suite
    ├── dataset/             # Hand-labeled ground truth & recorded Workday failure data
    ├── baselines/           # Naive parser baseline
    ├── metrics.py           # Precision, recall, exact-match evaluators
    └── run_eval.py          # Benchmark test runner
```

---

## 🚀 Quick Start Guide

### 1. Parser Server (Python 3.11+)

```bash
# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r parser/pyproject.toml   # or pip install fastapi uvicorn pydantic pymupdf pdfplumber python-docx nameparser rapidfuzz pytest

# Run unit & integration tests
PYTHONPATH=parser/src pytest parser/tests

# Start the parser API server
PYTHONPATH=parser/src uvicorn workingday_parser.main:app --host 0.0.0.0 --port 8000 --reload
```

API Documentation will be accessible at: `http://localhost:8000/docs`

### 2. Testing Sandbox (React + Vite)

```bash
cd sandbox
npm install
npm run dev
```

Open `http://localhost:5173` to test the Workday-style candidate application form with realistic `data-automation-id` attributes.

### 3. Chrome Extension (MV3)

```bash
cd extension
npm install
npm run build
```

**Loading the Extension in Chrome:**
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** in the top right.
3. Click **Load unpacked** and select the `WorkingDay/extension/dist` directory.
4. Click the WorkingDay extension icon, upload your resume PDF, and click **Launch Autofill Overlay** to autofill any Workday application or the Sandbox portal.

### 4. Running Benchmarks

```bash
PYTHONPATH=.:parser/src:parser python3 eval/run_eval.py
```

---

## 🛠️ Specific Rule Implementations

- **Name Parsing**: Detects conventions (given-first, family-first, two-surname, patronymic, mononym, caps-surname, `"Last, First"`). Utilizes particle matching (`van`, `de la`, `bin`, `Al-`, `O'`, `Mc`) and cross-checks with email handles and LinkedIn slugs. Provides candidate options in the UI for one-click switching.
- **Address Routing**: Isolates city/state/postal headers. Detects Address Line 2 indicators (`Apt`, `Unit`, `Suite`, `Bldg`, `Block #`) and places them in `addressLine2`. Strict preservation of `line1=null` if no street address is present on the resume.
- **Experience Blocks**: Robust extraction of multiword company names, dates with `"Present"`/`"Current"` parsing, and bracketed locations (`"Instructor - iCode [North Dallas]"`).
- **Education Normalization**: Normalizes degrees to canonical enums (`Associate's`, `Bachelor's`, `Master's`, `Doctorate`, `High School`, `Certificate`), isolates minor programs from primary major fields, and normalizes graduation dates.
- **Links Extraction**: Intercepts PDF hyperlink annotations, sanitizes glued delimiters (`|github.com`), and routes profiles to LinkedIn or generic portfolio website fields.
