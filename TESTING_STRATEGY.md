# Testing Strategy — Plum Claims Processing System

---

## Overview

The testing strategy uses a **three-tier approach**:

1. **Unit Tests** (9 tests) — Validate individual agent behavior for critical paths.
2. **Eval Runner** (12 cases) — End-to-end automated evaluation against all official test cases.
3. **Manual Testing Guide** — Step-by-step instructions for UI-based verification.

---

## Tier 1: Unit Tests

### Framework & Tools

| Tool | Purpose |
|---|---|
| `pytest` | Test runner and assertions |
| `pytest-asyncio` | Async test support (all agents are async) |
| `freezegun` | Freeze `datetime.now()` and `date.today()` to `2024-11-15` |

### Test Coverage

| Test | File | Test Case | What It Validates |
|---|---|---|---|
| `test_wrong_document_type` | `test_agents.py` | TC001 | DocumentAgent blocks when required doc type is missing |
| `test_unreadable_document` | `test_agents.py` | TC002 | DocumentAgent blocks on unreadable documents with actionable error |
| `test_patient_name_mismatch` | `test_agents.py` | TC003 | DocumentAgent blocks when patient names don't match across documents |
| `test_clean_approval_tc004` | `test_agents.py` | TC004 | Full pipeline produces APPROVED with correct amount (₹1,350) |
| `test_waiting_period_diabetes_tc005` | `test_agents.py` | TC005 | PolicyAgent correctly rejects for waiting period violation |
| `test_dental_partial_tc006` | `test_agents.py` | TC006 | PolicyAgent correctly produces PARTIAL with excluded line items |
| `test_network_discount_order_tc010` | `test_agents.py` | TC010 | Financial calculation applies network discount BEFORE co-pay |
| `test_graceful_degradation_tc011` | `test_agents.py` | TC011 | System doesn't crash when FraudAgent fails, produces degraded result |
| `test_fraud_same_day_tc009` | `test_agents.py` | TC009 | FraudAgent correctly flags same-day claim pattern → MANUAL_REVIEW |
| `test_excluded_bariatric_tc012` | `test_agents.py` | TC012 | PolicyAgent correctly rejects excluded conditions |

### Running Unit Tests

```bash
cd backend
python -m pytest tests/test_agents.py -v
```

### Key Testing Patterns

**Test Case Injection**: Documents include `actual_type`, `quality`, `patient_name_on_doc`, and `content` fields that bypass real Gemini vision calls. This enables:
- **Deterministic testing** — no LLM variability between runs.
- **No API key requirement** — unit tests run without Gemini/Groq keys.
- **Fast execution** — tests complete in <1s per case (no network calls for blocked claims).

**Date Freezing**: All unit tests freeze time to `2024-11-15` using `@freeze_time("2024-11-15")`. This ensures:
- Policy validity period (2024-04-01 to 2025-03-31) is active.
- Waiting period calculations are consistent.
- Submission deadline checks pass.

---

## Tier 2: Eval Runner (12 Official Test Cases)

### Overview

The eval runner (`tests/test_cases_runner.py`) loads all 12 test cases from `test_cases.json`, processes each through the full pipeline, and generates a detailed markdown report.

### Running the Eval

```bash
cd backend

# Set eval mode
set PLUM_EVAL_MODE=true

# Run all 12 cases
python -m tests.test_cases_runner
```

### What It Validates Per Case

1. **Decision Match**: Does the actual decision match the expected decision?
2. **Amount Match**: For APPROVED/PARTIAL, does the approved amount match (within ₹1 tolerance)?
3. **Blocking Behavior**: For TC001-TC003, does the system halt with `decision=None`?
4. **Error Messages**: Are error messages specific and actionable?
5. **Trace Completeness**: Does every step have checks with `rule_source`?
6. **Confidence Scores**: Are confidence scores within expected ranges?

### Eval Report

The eval report is generated at `eval/eval_report.md`. It contains:
- Summary table (12/12 passed, 0 failed).
- Per-case details: expected vs. actual decision, amount, confidence, duration.
- Full trace JSON (collapsible) for each case.
- Analysis of any mismatches.

---

## Tier 3: Manual Testing (UI-Based)

Manual testing is performed by running the application (FastAPI backend + React frontend) locally or on the deployed URL, and submitting claims through the Claim Form UI.

For the detailed step-by-step setup instructions and the exact parameters for all 12 manual testing scenarios (including which documents to upload for each case), please refer to the [Deployment and Manual Testing Guide](./deployment_and_testing_guide.md).



---

## What Is NOT Tested (And Why)

| Area | Why Not Covered in Automated Unit Tests | Manual Verification Status |
|---|---|---|
| **Frontend React components** | No automated Jest/RTL tests are setup. | **Fully Verified** — Manually tested via the React UI, verifying claim submissions, decisions, trace screens, and interactive graphs. |
| **API integration tests** | Covered by unit tests directly invoking the `process_claim()` orchestrator. | **Fully Verified** — Manually tested with Vite dev server proxying to FastAPI. |
| **Real document processing** | Mocked in unit tests using the test case injection pattern to ensure deterministic and API-keyless execution. | **Fully Verified** — Tested using actual PDF/image uploads, confirming that Gemini and Groq extract data and classify documents correctly. |
| **Load/stress testing** | Not required for evaluation. | Documented as a future enhancement in [FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md). |
| **Concurrent access** | In-memory store is not thread-safe. | Documented as a known limitation in [ASSUMPTIONS_AND_LIMITATIONS.md](./ASSUMPTIONS_AND_LIMITATIONS.md). |
| **Cross-browser testing** | CSS uses modern standard variables and layout. | **Fully Verified** — UI tested and works perfectly in standard Chrome, Edge, and Safari browser instances. |


---

## CI/CD Recommendations (Production)

For production deployment, the following CI/CD pipeline is recommended:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run unit tests
        run: |
          cd backend
          python -m pytest tests/test_agents.py -v --tb=short
      - name: Run eval (12 test cases)
        env:
          PLUM_EVAL_MODE: "true"
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          cd backend
          python -m tests.test_cases_runner
```
