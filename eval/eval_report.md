# Plum Claims Processing — Eval Report

**Total cases:** 12
**Passed:** 12
**Failed:** 0

---

## TC001 — Wrong Document Uploaded
| Field | Value |
|-------|-------|
| Expected Decision | `None` |
| Actual Decision | `None` |
| Matched | Yes |
| Confidence | 1.0 |
| Duration | 253ms |
| Graph Path | `document_agent → document_agent` |

**Reason:** You submitted ['PRESCRIPTION'] but a HOSPITAL_BILL is required for a CONSULTATION claim. Please upload a HOSPITAL_BILL to proceed.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_F74B4602",
  "started_at": "2024-11-11T00:00:00+00:00",
  "completed_at": "2024-11-11T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F001=DocumentType.PRESCRIPTION', 'F002=DocumentType.PRESCRIPTION']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "FAILED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "BLOCKING: 1 document problem(s) found. Pipeline halted.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": false,
          "expected": "HOSPITAL_BILL",
          "actual": "['PRESCRIPTION']",
          "detail": "You submitted ['PRESCRIPTION'] but a HOSPITAL_BILL is required for a CONSULTATION claim. Please upload a HOSPITAL_BILL to proceed.",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        }
      ],
      "llm_calls": [],
      "errors": [
        "You submitted ['PRESCRIPTION'] but a HOSPITAL_BILL is required for a CONSULTATION claim. Please upload a HOSPITAL_BILL to proceed."
      ],
      "confidence_impact": -1.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.0,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -1.0,
      "new_confidence": 0.0,
      "reason": "BLOCKING: 1 document problem(s) found. Pipeline halted."
    }
  ]
}
```

</details>


---

## TC002 — Unreadable Document
| Field | Value |
|-------|-------|
| Expected Decision | `None` |
| Actual Decision | `None` |
| Matched | Yes |
| Confidence | 1.0 |
| Duration | 24ms |
| Graph Path | `document_agent → document_agent` |

**Reason:** Your PHARMACY_BILL (file: blurry_bill.jpg) could not be read clearly. Please re-upload a clearer photo or scan of this document.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_31DAFEF6",
  "started_at": "2024-11-04T00:00:00+00:00",
  "completed_at": "2024-11-04T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-04T00:00:00+00:00",
      "completed_at": "2024-11-04T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.PHARMACY claim",
      "output_summary": "Classified 2 documents: ['F003=DocumentType.PRESCRIPTION', 'F004=DocumentType.PHARMACY_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "FAILED",
      "started_at": "2024-11-04T00:00:00+00:00",
      "completed_at": "2024-11-04T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.PHARMACY claim",
      "output_summary": "BLOCKING: 1 document problem(s) found. Pipeline halted.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > PHARMACY"
        },
        {
          "check_name": "required_document_PHARMACY_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PHARMACY_BILL present",
          "rule_source": "policy_terms.json > document_requirements > PHARMACY"
        },
        {
          "check_name": "document_readability_F004",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Your PHARMACY_BILL (file: blurry_bill.jpg) could not be read clearly. Please re-upload a clearer photo or scan of this document.",
          "rule_source": "document_agent.quality_checker"
        }
      ],
      "llm_calls": [],
      "errors": [
        "Your PHARMACY_BILL (file: blurry_bill.jpg) could not be read clearly. Please re-upload a clearer photo or scan of this document."
      ],
      "confidence_impact": -1.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.0,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -1.0,
      "new_confidence": 0.0,
      "reason": "BLOCKING: 1 document problem(s) found. Pipeline halted."
    }
  ]
}
```

</details>


---

## TC003 — Documents Belong to Different Patients
| Field | Value |
|-------|-------|
| Expected Decision | `None` |
| Actual Decision | `None` |
| Matched | Yes |
| Confidence | 1.0 |
| Duration | 25ms |
| Graph Path | `document_agent → document_agent` |

**Reason:** The patient name on your PRESCRIPTION reads 'Rajesh Kumar' but your HOSPITAL_BILL shows 'Arjun Mehta'. All documents must belong to the same patient. Please verify and resubmit.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_5D121373",
  "started_at": "2024-11-11T00:00:00+00:00",
  "completed_at": "2024-11-11T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F005=DocumentType.PRESCRIPTION', 'F006=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "FAILED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "BLOCKING: 1 document problem(s) found. Pipeline halted.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "patient_name_consistency",
          "passed": false,
          "expected": "Rajesh Kumar",
          "actual": "Arjun Mehta",
          "detail": "The patient name on your PRESCRIPTION reads 'Rajesh Kumar' but your HOSPITAL_BILL shows 'Arjun Mehta'. All documents must belong to the same patient. Please verify and resubmit.",
          "rule_source": "document_agent.integrity_checker"
        }
      ],
      "llm_calls": [],
      "errors": [
        "The patient name on your PRESCRIPTION reads 'Rajesh Kumar' but your HOSPITAL_BILL shows 'Arjun Mehta'. All documents must belong to the same patient. Please verify and resubmit."
      ],
      "confidence_impact": -1.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.0,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -1.0,
      "new_confidence": 0.0,
      "reason": "BLOCKING: 1 document problem(s) found. Pipeline halted."
    }
  ]
}
```

</details>


---

## TC004 — Clean Consultation â€” Full Approval
| Field | Value |
|-------|-------|
| Expected Decision | `APPROVED` |
| Actual Decision | `APPROVED` |
| Matched | Yes |
| Expected Amount | ₹1350 |
| Actual Amount | ₹1350.0 |
| Confidence | 0.9 |
| Duration | 10527ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim approved. ₹1350.00 will be reimbursed. Co-pay of ₹150.00 deducted.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_9BC2E7F2",
  "started_at": "2024-11-11T00:00:00+00:00",
  "completed_at": "2024-11-11T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F007=DocumentType.PRESCRIPTION', 'F008=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "All 2 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 2 documents",
      "output_summary": "Extracted: patient='Rajesh Kumar', diagnosis=['Viral Fever'], total=\u20b91500.0, line_items=3, extraction_confidence=1.00",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 1.00",
          "rule_source": "document_agent.extractor"
        },
        {
          "check_name": "patient_name_consistency",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Names match: 'Rajesh Kumar' \u2248 'Rajesh Kumar' (ratio: 1.00)",
          "rule_source": "document_agent.integrity_checker"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "PASSED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.CONSULTATION claim of \u20b91500.0",
      "output_summary": "Policy evaluation complete. Rejections: none. Approved amount: \u20b91350.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP001",
          "actual": "EMP001",
          "detail": "Member EMP001 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-11-01 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b91500.0",
          "detail": "Claimed \u20b91500.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 214. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": true,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b91500.0",
          "detail": "Claimed \u20b91500.0 vs per-claim limit \u20b95000",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        },
        {
          "check_name": "annual_opd_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Annual limit \u20b950000. YTD \u20b95000.0. Remaining \u20b945000.0.",
          "rule_source": "policy_terms.json > coverage > annual_opd_limit"
        },
        {
          "check_name": "network_discount",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Non-network hospital or no discount applicable.",
          "rule_source": "policy_terms.json > opd_categories > network_discount_percent"
        },
        {
          "check_name": "copay",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Co-pay 10% on \u20b91500.00: \u20b9150.00 deducted. Final: \u20b91350.00",
          "rule_source": "policy_terms.json > opd_categories > consultation > copay_percent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "WARNING",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP001, \u20b91500.0",
      "output_summary": "Fraud score: 0.40. Flags: ['SAME_DAY_CLAIM_PATTERN']. Manual review: False",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "2 existing claims on 2024-11-01 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: ['Unknown Provider']",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b91500.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.1
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-11-11T00:00:00+00:00",
      "completed_at": "2024-11-11T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: APPROVED | Approved: \u20b91350.00 | Confidence: 0.90",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: APPROVED, Approved: \u20b91350.00, Confidence: 0.90",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.9,
  "confidence_log": [
    {
      "after": "FraudAgent",
      "delta": -0.1,
      "new_confidence": 0.9,
      "reason": "Fraud score: 0.40. Flags: ['SAME_DAY_CLAIM_PATTERN']. Manual review: False"
    }
  ]
}
```

</details>


---

## TC005 — Waiting Period â€” Diabetes
| Field | Value |
|-------|-------|
| Expected Decision | `REJECTED` |
| Actual Decision | `REJECTED` |
| Matched | Yes |
| Actual Amount | ₹0.0 |
| Confidence | 1.0 |
| Duration | 1001ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim rejected: Waiting period not met for diabetes (WAITING_PERIOD_DIABETES — eligible from 2024-11-30).

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_770B63DC",
  "started_at": "2024-10-25T00:00:00+00:00",
  "completed_at": "2024-10-25T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F009=DocumentType.PRESCRIPTION', 'F010=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "All 2 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 2 documents",
      "output_summary": "Extracted: patient='Vikram Joshi', diagnosis=['Type 2 Diabetes Mellitus'], total=\u20b93000.0, line_items=0, extraction_confidence=1.00",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 1.00",
          "rule_source": "document_agent.extractor"
        },
        {
          "check_name": "patient_name_consistency",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Names match: 'Vikram Joshi' \u2248 'Vikram Joshi' (ratio: 1.00)",
          "rule_source": "document_agent.integrity_checker"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "FAILED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.CONSULTATION claim of \u20b93000.0",
      "output_summary": "Policy evaluation complete. Rejections: ['WAITING_PERIOD_DIABETES \u2014 eligible from 2024-11-30']. Approved amount: \u20b90.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP005",
          "actual": "EMP005",
          "detail": "Member EMP005 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-10-15 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b93000.0",
          "detail": "Claimed \u20b93000.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-09-01. Days since joining: 44. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "waiting_period_diabetes",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Diagnosis matches 'diabetes' semantically. Required: 90 days. Days since joining: 44. Eligible from: 2024-11-30.",
          "rule_source": "policy_terms.json > waiting_periods > specific_conditions > diabetes"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": true,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b93000.0",
          "detail": "Claimed \u20b93000.0 vs per-claim limit \u20b95000",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP005, \u20b93000.0",
      "output_summary": "Fraud score: 0.00. Flags: none. Manual review: False",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 existing claims on 2024-10-15 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: []",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b93000.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: REJECTED | Approved: \u20b90.00 | Confidence: 1.00",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: REJECTED, Approved: \u20b90.00, Confidence: 1.00",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 1.0,
  "confidence_log": []
}
```

</details>


---

## TC006 — Dental Partial Approval â€” Cosmetic Exclusion
| Field | Value |
|-------|-------|
| Expected Decision | `PARTIAL` |
| Actual Decision | `PARTIAL` |
| Matched | Yes |
| Expected Amount | ₹8000 |
| Actual Amount | ₹8000.0 |
| Confidence | 0.85 |
| Duration | 10139ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim partially approved. ₹8000.00 approved of ₹12000.0 claimed.
Approved: Root Canal Treatment (₹8000.0)
Rejected: Teeth Whitening — Excluded procedure/item per policy

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_C794AECD",
  "started_at": "2024-10-25T00:00:00+00:00",
  "completed_at": "2024-10-25T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 1 documents for ClaimCategory.DENTAL claim",
      "output_summary": "Classified 1 documents: ['F011=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "1/1 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.DENTAL claim",
      "output_summary": "All 1 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > DENTAL"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 1 documents",
      "output_summary": "Extracted: patient='Priya Singh', diagnosis=[], total=\u20b912000.0, line_items=2, extraction_confidence=0.67",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 0.67",
          "rule_source": "document_agent.extractor"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.15
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.DENTAL claim of \u20b912000.0",
      "output_summary": "Policy evaluation complete. Rejections: none. Approved amount: \u20b95000.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP002",
          "actual": "EMP002",
          "detail": "Member EMP002 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-10-15 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b912000.0",
          "detail": "Claimed \u20b912000.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 197. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": true,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b912000.0",
          "detail": "Claimed \u20b912000.0 vs per-claim limit \u20b95000 (dental line-item evaluation pending)",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        },
        {
          "check_name": "annual_opd_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Annual limit \u20b950000. YTD \u20b90.0. Remaining \u20b950000.0.",
          "rule_source": "policy_terms.json > coverage > annual_opd_limit"
        },
        {
          "check_name": "network_discount",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Non-network hospital or no discount applicable.",
          "rule_source": "policy_terms.json > opd_categories > network_discount_percent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP002, \u20b912000.0",
      "output_summary": "Fraud score: 0.00. Flags: none. Manual review: False",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 existing claims on 2024-10-15 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: []",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b912000.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-10-25T00:00:00+00:00",
      "completed_at": "2024-10-25T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: PARTIAL | Approved: \u20b98000.00 | Confidence: 0.85",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: PARTIAL, Approved: \u20b98000.00, Confidence: 0.85",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.85,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -0.15,
      "new_confidence": 0.85,
      "reason": "Extracted: patient='Priya Singh', diagnosis=[], total=\u20b912000.0, line_items=2, extraction_confidence=0.67"
    }
  ]
}
```

</details>


---

## TC007 — MRI Without Pre-Authorization
| Field | Value |
|-------|-------|
| Expected Decision | `REJECTED` |
| Actual Decision | `REJECTED` |
| Matched | Yes |
| Actual Amount | ₹0.0 |
| Confidence | 0.85 |
| Duration | 1244ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim rejected: Pre-authorization required but not obtained. For MRI/CT Scan/PET Scan above ₹10,000, obtain pre-auth from ICICI Lombard General Insurance first.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_E94C6C6F",
  "started_at": "2024-11-12T00:00:00+00:00",
  "completed_at": "2024-11-12T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-12T00:00:00+00:00",
      "completed_at": "2024-11-12T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 3 documents for ClaimCategory.DIAGNOSTIC claim",
      "output_summary": "Classified 3 documents: ['F012=DocumentType.PRESCRIPTION', 'F013=DocumentType.LAB_REPORT', 'F014=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "3/3 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-12T00:00:00+00:00",
      "completed_at": "2024-11-12T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.DIAGNOSTIC claim",
      "output_summary": "All 3 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > DIAGNOSTIC"
        },
        {
          "check_name": "required_document_LAB_REPORT",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "LAB_REPORT present",
          "rule_source": "policy_terms.json > document_requirements > DIAGNOSTIC"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > DIAGNOSTIC"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-12T00:00:00+00:00",
      "completed_at": "2024-11-12T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 3 documents",
      "output_summary": "Extracted: patient='None', diagnosis=['Suspected Lumbar Disc Herniation'], total=\u20b915000.0, line_items=1, extraction_confidence=0.67",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 0.67",
          "rule_source": "document_agent.extractor"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.15
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "FAILED",
      "started_at": "2024-11-12T00:00:00+00:00",
      "completed_at": "2024-11-12T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.DIAGNOSTIC claim of \u20b915000.0",
      "output_summary": "Policy evaluation complete. Rejections: ['PRE_AUTH_MISSING']. Approved amount: \u20b90.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP007",
          "actual": "EMP007",
          "detail": "Member EMP007 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-11-02 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b915000.0",
          "detail": "Claimed \u20b915000.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 215. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "pre_authorization",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization required but missing.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": true,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b915000.0",
          "detail": "Claimed \u20b915000.0 vs per-claim limit \u20b95000 (diagnostic claim limit exception)",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "PASSED",
      "started_at": "2024-11-12T00:00:00+00:00",
      "completed_at": "2024-11-12T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP007, \u20b915000.0",
      "output_summary": "Fraud score: 0.00. Flags: none. Manual review: False",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 existing claims on 2024-11-02 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: []",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b915000.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-11-12T00:00:00+00:00",
      "completed_at": "2024-11-12T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: REJECTED | Approved: \u20b90.00 | Confidence: 0.85",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: REJECTED, Approved: \u20b90.00, Confidence: 0.85",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.85,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -0.15,
      "new_confidence": 0.85,
      "reason": "Extracted: patient='None', diagnosis=['Suspected Lumbar Disc Herniation'], total=\u20b915000.0, line_items=1, extraction_confidence=0.67"
    }
  ]
}
```

</details>


---

## TC008 — Per-Claim Limit Exceeded
| Field | Value |
|-------|-------|
| Expected Decision | `REJECTED` |
| Actual Decision | `REJECTED` |
| Matched | Yes |
| Actual Amount | ₹0.0 |
| Confidence | 0.85 |
| Duration | 834ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim rejected: Claimed ₹7500.0 exceeds per-claim limit ₹5,000.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_416E5755",
  "started_at": "2024-10-30T00:00:00+00:00",
  "completed_at": "2024-10-30T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-30T00:00:00+00:00",
      "completed_at": "2024-10-30T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F015=DocumentType.PRESCRIPTION', 'F016=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-30T00:00:00+00:00",
      "completed_at": "2024-10-30T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "All 2 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-30T00:00:00+00:00",
      "completed_at": "2024-10-30T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 2 documents",
      "output_summary": "Extracted: patient='None', diagnosis=['Gastroenteritis'], total=\u20b97500.0, line_items=2, extraction_confidence=0.67",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 0.67",
          "rule_source": "document_agent.extractor"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.15
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "FAILED",
      "started_at": "2024-10-30T00:00:00+00:00",
      "completed_at": "2024-10-30T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.CONSULTATION claim of \u20b97500.0",
      "output_summary": "Policy evaluation complete. Rejections: ['PER_CLAIM_LIMIT_EXCEEDED']. Approved amount: \u20b90.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP003",
          "actual": "EMP003",
          "detail": "Member EMP003 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-10-20 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b97500.0",
          "detail": "Claimed \u20b97500.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 202. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": false,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b97500.0",
          "detail": "Claimed \u20b97500.0 vs per-claim limit \u20b95000",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "PASSED",
      "started_at": "2024-10-30T00:00:00+00:00",
      "completed_at": "2024-10-30T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP003, \u20b97500.0",
      "output_summary": "Fraud score: 0.00. Flags: none. Manual review: False",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 existing claims on 2024-10-20 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: []",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b97500.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-10-30T00:00:00+00:00",
      "completed_at": "2024-10-30T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: REJECTED | Approved: \u20b90.00 | Confidence: 0.85",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: REJECTED, Approved: \u20b90.00, Confidence: 0.85",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.85,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -0.15,
      "new_confidence": 0.85,
      "reason": "Extracted: patient='None', diagnosis=['Gastroenteritis'], total=\u20b97500.0, line_items=2, extraction_confidence=0.67"
    }
  ]
}
```

</details>


---

## TC009 — Fraud Signal â€” Multiple Same-Day Claims
| Field | Value |
|-------|-------|
| Expected Decision | `MANUAL_REVIEW` |
| Actual Decision | `MANUAL_REVIEW` |
| Matched | Yes |
| Actual Amount | ₹4320.0 |
| Confidence | 0.65 |
| Duration | 1511ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim flagged for manual review. Signals: Fraud score 0.80 exceeds threshold 0.8. Fraud flags: SAME_DAY_CLAIM_PATTERN, MULTIPLE_PROVIDERS_SAME_DAY. An operations team member will review within 2 business days.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_D7B4C35C",
  "started_at": "2024-11-09T00:00:00+00:00",
  "completed_at": "2024-11-09T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-09T00:00:00+00:00",
      "completed_at": "2024-11-09T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F017=DocumentType.PRESCRIPTION', 'F018=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-09T00:00:00+00:00",
      "completed_at": "2024-11-09T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "All 2 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-09T00:00:00+00:00",
      "completed_at": "2024-11-09T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 2 documents",
      "output_summary": "Extracted: patient='None', diagnosis=['Migraine'], total=\u20b94800.0, line_items=0, extraction_confidence=0.67",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 0.67",
          "rule_source": "document_agent.extractor"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.15
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "PASSED",
      "started_at": "2024-11-09T00:00:00+00:00",
      "completed_at": "2024-11-09T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.CONSULTATION claim of \u20b94800.0",
      "output_summary": "Policy evaluation complete. Rejections: none. Approved amount: \u20b94320.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP008",
          "actual": "EMP008",
          "detail": "Member EMP008 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-10-30 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b94800.0",
          "detail": "Claimed \u20b94800.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 212. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": true,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b94800.0",
          "detail": "Claimed \u20b94800.0 vs per-claim limit \u20b95000",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        },
        {
          "check_name": "annual_opd_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Annual limit \u20b950000. YTD \u20b90.0. Remaining \u20b950000.0.",
          "rule_source": "policy_terms.json > coverage > annual_opd_limit"
        },
        {
          "check_name": "network_discount",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Non-network hospital or no discount applicable.",
          "rule_source": "policy_terms.json > opd_categories > network_discount_percent"
        },
        {
          "check_name": "copay",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Co-pay 10% on \u20b94800.00: \u20b9480.00 deducted. Final: \u20b94320.00",
          "rule_source": "policy_terms.json > opd_categories > consultation > copay_percent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "WARNING",
      "started_at": "2024-11-09T00:00:00+00:00",
      "completed_at": "2024-11-09T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP008, \u20b94800.0",
      "output_summary": "Fraud score: 0.80. Flags: ['SAME_DAY_CLAIM_PATTERN', 'MULTIPLE_PROVIDERS_SAME_DAY']. Manual review: True",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "3 existing claims on 2024-10-30 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: ['City Clinic A', 'City Clinic B', 'Wellness Center']",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "3 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b94800.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.2
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-11-09T00:00:00+00:00",
      "completed_at": "2024-11-09T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: MANUAL_REVIEW | Approved: \u20b94320.00 | Confidence: 0.65",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: MANUAL_REVIEW, Approved: \u20b94320.00, Confidence: 0.65",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.6499999999999999,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -0.15,
      "new_confidence": 0.85,
      "reason": "Extracted: patient='None', diagnosis=['Migraine'], total=\u20b94800.0, line_items=0, extraction_confidence=0.67"
    },
    {
      "after": "FraudAgent",
      "delta": -0.2,
      "new_confidence": 0.6499999999999999,
      "reason": "Fraud score: 0.80. Flags: ['SAME_DAY_CLAIM_PATTERN', 'MULTIPLE_PROVIDERS_SAME_DAY']. Manual review: True"
    }
  ]
}
```

</details>


---

## TC010 — Network Hospital â€” Discount Applied
| Field | Value |
|-------|-------|
| Expected Decision | `APPROVED` |
| Actual Decision | `APPROVED` |
| Matched | Yes |
| Expected Amount | ₹3240 |
| Actual Amount | ₹3240.0 |
| Confidence | 1.0 |
| Duration | 1090ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim approved. ₹3240.00 will be reimbursed. Network discount of ₹900.00 applied. Co-pay of ₹360.00 deducted.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_2C2D36F1",
  "started_at": "2024-11-13T00:00:00+00:00",
  "completed_at": "2024-11-13T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-13T00:00:00+00:00",
      "completed_at": "2024-11-13T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F019=DocumentType.PRESCRIPTION', 'F020=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-13T00:00:00+00:00",
      "completed_at": "2024-11-13T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "All 2 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-13T00:00:00+00:00",
      "completed_at": "2024-11-13T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 2 documents",
      "output_summary": "Extracted: patient='Deepak Shah', diagnosis=['Acute Bronchitis'], total=\u20b94500.0, line_items=2, extraction_confidence=1.00",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 1.00",
          "rule_source": "document_agent.extractor"
        },
        {
          "check_name": "patient_name_consistency",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Names match: 'Deepak Shah' \u2248 'Deepak Shah' (ratio: 1.00)",
          "rule_source": "document_agent.integrity_checker"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "PASSED",
      "started_at": "2024-11-13T00:00:00+00:00",
      "completed_at": "2024-11-13T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.CONSULTATION claim of \u20b94500.0",
      "output_summary": "Policy evaluation complete. Rejections: none. Approved amount: \u20b93240.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP010",
          "actual": "EMP010",
          "detail": "Member EMP010 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-11-03 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b94500.0",
          "detail": "Claimed \u20b94500.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 216. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": true,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b94500.0",
          "detail": "Claimed \u20b94500.0 vs per-claim limit \u20b95000",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        },
        {
          "check_name": "annual_opd_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Annual limit \u20b950000. YTD \u20b98000.0. Remaining \u20b942000.0.",
          "rule_source": "policy_terms.json > coverage > annual_opd_limit"
        },
        {
          "check_name": "network_discount",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Network hospital 'Apollo Hospitals' \u2014 20% discount: \u20b94500.0 \u2192 \u20b93600.00",
          "rule_source": "policy_terms.json > opd_categories > network_discount_percent"
        },
        {
          "check_name": "copay",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Co-pay 10% on \u20b93600.00: \u20b9360.00 deducted. Final: \u20b93240.00",
          "rule_source": "policy_terms.json > opd_categories > consultation > copay_percent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "PASSED",
      "started_at": "2024-11-13T00:00:00+00:00",
      "completed_at": "2024-11-13T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP010, \u20b94500.0",
      "output_summary": "Fraud score: 0.00. Flags: none. Manual review: False",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 existing claims on 2024-11-03 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: []",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b94500.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-11-13T00:00:00+00:00",
      "completed_at": "2024-11-13T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: APPROVED | Approved: \u20b93240.00 | Confidence: 1.00",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: APPROVED, Approved: \u20b93240.00, Confidence: 1.00",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 1.0,
  "confidence_log": []
}
```

</details>


---

## TC011 — Component Failure â€” Graceful Degradation
| Field | Value |
|-------|-------|
| Expected Decision | `APPROVED` |
| Actual Decision | `APPROVED` |
| Matched | Yes |
| Actual Amount | ₹4000.0 |
| Confidence | 0.55 |
| Duration | 9199ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → decision_agent` |

**Reason:** Claim approved. ₹4000.00 will be reimbursed.

Note: Pipeline ran with simulated component failure. Manual review recommended due to incomplete processing. Confidence reduced to 0.55.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_52F224A7",
  "started_at": "2024-11-07T00:00:00+00:00",
  "completed_at": "2024-11-07T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-07T00:00:00+00:00",
      "completed_at": "2024-11-07T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.ALTERNATIVE_MEDICINE claim",
      "output_summary": "Classified 2 documents: ['F021=DocumentType.PRESCRIPTION', 'F022=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-07T00:00:00+00:00",
      "completed_at": "2024-11-07T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.ALTERNATIVE_MEDICINE claim",
      "output_summary": "All 2 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > ALTERNATIVE_MEDICINE"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > ALTERNATIVE_MEDICINE"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-11-07T00:00:00+00:00",
      "completed_at": "2024-11-07T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 2 documents",
      "output_summary": "Extracted: patient='None', diagnosis=['Chronic Joint Pain'], total=\u20b94000.0, line_items=2, extraction_confidence=0.67",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 0.67",
          "rule_source": "document_agent.extractor"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.15
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "PASSED",
      "started_at": "2024-11-07T00:00:00+00:00",
      "completed_at": "2024-11-07T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.ALTERNATIVE_MEDICINE claim of \u20b94000.0",
      "output_summary": "Policy evaluation complete. Rejections: none. Approved amount: \u20b94000.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP006",
          "actual": "EMP006",
          "detail": "Member EMP006 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-10-28 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b94000.0",
          "detail": "Claimed \u20b94000.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 210. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": true,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b94000.0",
          "detail": "Claimed \u20b94000.0 vs per-claim limit \u20b95000",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        },
        {
          "check_name": "annual_opd_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Annual limit \u20b950000. YTD \u20b90.0. Remaining \u20b950000.0.",
          "rule_source": "policy_terms.json > coverage > annual_opd_limit"
        },
        {
          "check_name": "network_discount",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Non-network hospital or no discount applicable.",
          "rule_source": "policy_terms.json > opd_categories > network_discount_percent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-11-07T00:00:00+00:00",
      "completed_at": "2024-11-07T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: APPROVED | Approved: \u20b94000.00 | Confidence: 0.55",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: APPROVED, Approved: \u20b94000.00, Confidence: 0.55",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.85,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -0.15,
      "new_confidence": 0.85,
      "reason": "Extracted: patient='None', diagnosis=['Chronic Joint Pain'], total=\u20b94000.0, line_items=2, extraction_confidence=0.67"
    }
  ]
}
```

</details>


---

## TC012 — Excluded Treatment
| Field | Value |
|-------|-------|
| Expected Decision | `REJECTED` |
| Actual Decision | `REJECTED` |
| Matched | Yes |
| Actual Amount | ₹0.0 |
| Confidence | 0.85 |
| Duration | 1380ms |
| Graph Path | `document_agent → document_agent → document_agent → policy_agent → fraud_agent → decision_agent` |

**Reason:** Claim rejected due to multiple policy violations:
• Waiting period not met for obesity_treatment (WAITING_PERIOD_OBESITY_TREATMENT — eligible from 2025-04-01).
• Treatment/procedure is excluded under your policy.
• Claimed ₹8000.0 exceeds per-claim limit ₹5,000.

<details><summary>Full Trace (JSON)</summary>

```json
{
  "claim_id": "CLM_86BBAB67",
  "started_at": "2024-10-28T00:00:00+00:00",
  "completed_at": "2024-10-28T00:00:00+00:00",
  "total_duration_ms": 0.0,
  "graph_path": [
    "document_agent",
    "document_agent",
    "document_agent",
    "policy_agent",
    "fraud_agent",
    "decision_agent"
  ],
  "steps": [
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-28T00:00:00+00:00",
      "completed_at": "2024-10-28T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Classifying 2 documents for ClaimCategory.CONSULTATION claim",
      "output_summary": "Classified 2 documents: ['F023=DocumentType.PRESCRIPTION', 'F024=DocumentType.HOSPITAL_BILL']",
      "checks_performed": [
        {
          "check_name": "document_classification",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "2/2 documents classified",
          "rule_source": "document_agent.classifier"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-28T00:00:00+00:00",
      "completed_at": "2024-10-28T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Quality and integrity check for ClaimCategory.CONSULTATION claim",
      "output_summary": "All 2 required documents present. Quality checks passed.",
      "checks_performed": [
        {
          "check_name": "required_document_PRESCRIPTION",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "PRESCRIPTION present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        },
        {
          "check_name": "required_document_HOSPITAL_BILL",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "HOSPITAL_BILL present",
          "rule_source": "policy_terms.json > document_requirements > CONSULTATION"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DocumentAgent",
      "node_name": "document_agent",
      "status": "PASSED",
      "started_at": "2024-10-28T00:00:00+00:00",
      "completed_at": "2024-10-28T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Extracting structured data from 2 documents",
      "output_summary": "Extracted: patient='None', diagnosis=['Morbid Obesity \u00e2\u20ac\u201d BMI 37'], total=\u20b98000.0, line_items=2, extraction_confidence=0.67",
      "checks_performed": [
        {
          "check_name": "extraction_completeness",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Extraction confidence: 0.67",
          "rule_source": "document_agent.extractor"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": -0.15
    },
    {
      "agent_name": "PolicyAgent",
      "node_name": "policy_agent",
      "status": "FAILED",
      "started_at": "2024-10-28T00:00:00+00:00",
      "completed_at": "2024-10-28T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Evaluating policy rules for ClaimCategory.CONSULTATION claim of \u20b98000.0",
      "output_summary": "Policy evaluation complete. Rejections: ['WAITING_PERIOD_OBESITY_TREATMENT \u2014 eligible from 2025-04-01', 'EXCLUDED_CONDITION', 'PER_CLAIM_LIMIT_EXCEEDED']. Approved amount: \u20b90.00",
      "checks_performed": [
        {
          "check_name": "member_exists",
          "passed": true,
          "expected": "EMP009",
          "actual": "EMP009",
          "detail": "Member EMP009 found",
          "rule_source": "policy_terms.json > members"
        },
        {
          "check_name": "policy_active",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Policy status: ACTIVE, treatment 2024-10-18 within 2024-04-01 to 2025-03-31",
          "rule_source": "policy_terms.json > policy_holder"
        },
        {
          "check_name": "submission_deadline",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "10 days since treatment. Deadline: 30 days.",
          "rule_source": "policy_terms.json > submission_rules > deadline_days_from_treatment"
        },
        {
          "check_name": "minimum_claim_amount",
          "passed": true,
          "expected": "\u2265 \u20b9500",
          "actual": "\u20b98000.0",
          "detail": "Claimed \u20b98000.0, minimum is \u20b9500",
          "rule_source": "policy_terms.json > submission_rules > minimum_claim_amount"
        },
        {
          "check_name": "initial_waiting_period",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Member joined 2024-04-01. Days since joining: 200. Required: 30 days.",
          "rule_source": "policy_terms.json > waiting_periods > initial_waiting_period_days"
        },
        {
          "check_name": "waiting_period_obesity_treatment",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Diagnosis matches 'obesity_treatment' semantically. Required: 365 days. Days since joining: 200. Eligible from: 2025-04-01.",
          "rule_source": "policy_terms.json > waiting_periods > specific_conditions > obesity_treatment"
        },
        {
          "check_name": "exclusion_check_obesity_and_weight_loss_programs",
          "passed": false,
          "expected": null,
          "actual": null,
          "detail": "Excluded condition/procedure detected: 'Obesity and weight loss programs' (Explanation: The patient's diagnosis and treatment line items directly relate to obesity treatment and weight loss programs.)",
          "rule_source": "policy_terms.json > exclusions"
        },
        {
          "check_name": "pre_authorization",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Pre-authorization not required.",
          "rule_source": "policy_terms.json > pre_authorization"
        },
        {
          "check_name": "per_claim_limit",
          "passed": false,
          "expected": "\u2264 \u20b95000",
          "actual": "\u20b98000.0",
          "detail": "Claimed \u20b98000.0 vs per-claim limit \u20b95000",
          "rule_source": "policy_terms.json > coverage > per_claim_limit"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "FraudAgent",
      "node_name": "fraud_agent",
      "status": "PASSED",
      "started_at": "2024-10-28T00:00:00+00:00",
      "completed_at": "2024-10-28T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Fraud assessment for member EMP009, \u20b98000.0",
      "output_summary": "Fraud score: 0.00. Flags: none. Manual review: False",
      "checks_performed": [
        {
          "check_name": "same_day_claims",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 existing claims on 2024-10-18 (limit: 2)",
          "rule_source": "policy_terms.json > fraud_thresholds > same_day_claims_limit"
        },
        {
          "check_name": "multiple_providers_same_day",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Same-day providers: []",
          "rule_source": "policy_terms.json > fraud_thresholds"
        },
        {
          "check_name": "monthly_claims_limit",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "0 claims this month (limit: 6)",
          "rule_source": "policy_terms.json > fraud_thresholds > monthly_claims_limit"
        },
        {
          "check_name": "high_value_claim",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Claimed \u20b98000.0 vs threshold \u20b925000",
          "rule_source": "policy_terms.json > fraud_thresholds > high_value_claim_threshold"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    },
    {
      "agent_name": "DecisionAgent",
      "node_name": "decision_agent",
      "status": "PASSED",
      "started_at": "2024-10-28T00:00:00+00:00",
      "completed_at": "2024-10-28T00:00:00+00:00",
      "duration_ms": 0.0,
      "input_summary": "Synthesizing final decision from policy + fraud evaluations",
      "output_summary": "Decision: REJECTED | Approved: \u20b90.00 | Confidence: 0.85",
      "checks_performed": [
        {
          "check_name": "final_decision",
          "passed": true,
          "expected": null,
          "actual": null,
          "detail": "Decision: REJECTED, Approved: \u20b90.00, Confidence: 0.85",
          "rule_source": "decision_agent"
        }
      ],
      "llm_calls": [],
      "errors": [],
      "confidence_impact": 0.0
    }
  ],
  "initial_confidence": 1.0,
  "final_confidence": 0.85,
  "confidence_log": [
    {
      "after": "DocumentAgent",
      "delta": -0.15,
      "new_confidence": 0.85,
      "reason": "Extracted: patient='None', diagnosis=['Morbid Obesity \u00e2\u20ac\u201d BMI 37'], total=\u20b98000.0, line_items=2, extraction_confidence=0.67"
    }
  ]
}
```

</details>


---
