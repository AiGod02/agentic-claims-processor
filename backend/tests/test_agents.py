import pytest
import asyncio
from datetime import date
from freezegun import freeze_time
from models.claim import (
    ClaimSubmission, ClaimCategory, ClaimDecision,
    UploadedDocument, DocumentType, DocumentQuality
)
from graph.orchestrator import process_claim


def make_submission(**kwargs) -> ClaimSubmission:
    defaults = dict(
        member_id="EMP001",
        policy_id="PLUM_GHI_2024",
        claim_category=ClaimCategory.CONSULTATION,
        treatment_date=date(2024, 11, 1),
        claimed_amount=1500.0,
        documents=[
            UploadedDocument(file_id="F1", file_name="rx.jpg",
                             actual_type=DocumentType.PRESCRIPTION,
                             content={"patient_name": "Rajesh Kumar",
                                      "doctor_name": "Dr. A", "doctor_registration": "KA/1/2020",
                                      "diagnosis": "Viral Fever"}),
            UploadedDocument(file_id="F2", file_name="bill.jpg",
                             actual_type=DocumentType.HOSPITAL_BILL,
                             content={"patient_name": "Rajesh Kumar",
                                      "hospital_name": "City Clinic",
                                      "line_items": [{"description": "Consultation", "amount": 1500}],
                                      "total": 1500})
        ]
    )
    defaults.update(kwargs)
    return ClaimSubmission(**defaults)


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_wrong_document_type():
    """TC001 — Two prescriptions submitted for CONSULTATION"""
    sub = make_submission(documents=[
        UploadedDocument(file_id="F1", file_name="rx1.jpg", actual_type=DocumentType.PRESCRIPTION,
                         content={"patient_name": "Rajesh Kumar", "diagnosis": "Fever"}),
        UploadedDocument(file_id="F2", file_name="rx2.jpg", actual_type=DocumentType.PRESCRIPTION,
                         content={"patient_name": "Rajesh Kumar", "diagnosis": "Fever"}),
    ])
    result = await process_claim(sub)
    assert result.decision is None
    assert "HOSPITAL_BILL" in result.reason
    assert "PRESCRIPTION" in result.reason


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_unreadable_document():
    """TC002 — Unreadable pharmacy bill"""
    sub = make_submission(
        claim_category=ClaimCategory.PHARMACY,
        member_id="EMP004",
        claimed_amount=800.0,
        documents=[
            UploadedDocument(file_id="F3", file_name="rx.jpg",
                             actual_type=DocumentType.PRESCRIPTION,
                             quality=DocumentQuality.GOOD,
                             content={"patient_name": "Sneha Reddy", "diagnosis": "Fever"}),
            UploadedDocument(file_id="F4", file_name="bill.jpg",
                             actual_type=DocumentType.PHARMACY_BILL,
                             quality=DocumentQuality.UNREADABLE,
                             content={}),
        ]
    )
    result = await process_claim(sub)
    assert result.decision is None
    assert "re-upload" in result.reason.lower()


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_patient_name_mismatch():
    """TC003 — Documents belong to different patients"""
    sub = make_submission(documents=[
        UploadedDocument(file_id="F5", file_name="rx.jpg",
                         actual_type=DocumentType.PRESCRIPTION,
                         patient_name_on_doc="Rajesh Kumar",
                         content={"patient_name": "Rajesh Kumar", "diagnosis": "Fever"}),
        UploadedDocument(file_id="F6", file_name="bill.jpg",
                         actual_type=DocumentType.HOSPITAL_BILL,
                         patient_name_on_doc="Arjun Mehta",
                         content={"patient_name": "Arjun Mehta",
                                  "hospital_name": "City Clinic", "total": 1500,
                                  "line_items": [{"description": "Consultation", "amount": 1500}]}),
    ])
    result = await process_claim(sub)
    assert result.decision is None
    assert "Rajesh Kumar" in result.reason
    assert "Arjun Mehta" in result.reason


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_clean_approval_tc004():
    """TC004 — Clean consultation, expect APPROVED ₹1350 after 10% copay"""
    result = await process_claim(make_submission())
    assert result.decision == ClaimDecision.APPROVED
    assert result.approved_amount == pytest.approx(1350.0, abs=1.0)
    assert result.confidence_score > 0.85


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_waiting_period_diabetes_tc005():
    """TC005 — EMP005 joined 2024-09-01, claims diabetes on 2024-10-15 (within 90-day wait)"""
    sub = make_submission(
        member_id="EMP005",
        treatment_date=date(2024, 10, 15),
        claimed_amount=3000.0,
        documents=[
            UploadedDocument(file_id="F9", file_name="rx.jpg",
                             actual_type=DocumentType.PRESCRIPTION,
                             content={"patient_name": "Vikram Joshi",
                                      "diagnosis": "Type 2 Diabetes Mellitus",
                                      "doctor_name": "Dr. Sunil", "doctor_registration": "GJ/1/2014",
                                      "medicines": ["Metformin 500mg"]}),
            UploadedDocument(file_id="F10", file_name="bill.jpg",
                             actual_type=DocumentType.HOSPITAL_BILL,
                             content={"patient_name": "Vikram Joshi",
                                      "hospital_name": "City Clinic",
                                      "line_items": [{"description": "Consultation", "amount": 3000}],
                                      "total": 3000}),
        ]
    )
    result = await process_claim(sub)
    assert result.decision == ClaimDecision.REJECTED
    assert any("WAITING_PERIOD" in r for r in result.rejection_reasons)
    assert "eligible from" in result.reason.lower()


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_dental_partial_tc006():
    """TC006 — Root canal (covered) + teeth whitening (excluded) = PARTIAL ₹8000"""
    sub = make_submission(
        member_id="EMP002",
        claim_category=ClaimCategory.DENTAL,
        treatment_date=date(2024, 10, 20),
        claimed_amount=12000.0,
        documents=[
            UploadedDocument(file_id="F11", file_name="bill.jpg",
                             actual_type=DocumentType.HOSPITAL_BILL,
                             content={"patient_name": "Priya Singh",
                                      "hospital_name": "Smile Dental Clinic",
                                      "line_items": [
                                          {"description": "Root Canal Treatment", "amount": 8000},
                                          {"description": "Teeth Whitening", "amount": 4000}
                                      ],
                                      "total": 12000})
        ]
    )
    result = await process_claim(sub)
    assert result.decision == ClaimDecision.PARTIAL
    assert result.approved_amount == pytest.approx(8000.0, abs=1.0)


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_network_discount_order_tc010():
    """TC010 — Apollo Hospitals: 20% network discount THEN 10% copay = ₹3240"""
    sub = make_submission(
        member_id="EMP010",
        claimed_amount=4500.0,
        hospital_name="Apollo Hospitals",
        ytd_claims_amount=8000.0,
        documents=[
            UploadedDocument(file_id="F19", file_name="rx.jpg",
                             actual_type=DocumentType.PRESCRIPTION,
                             content={"patient_name": "Deepak Shah", "diagnosis": "Acute Bronchitis",
                                      "doctor_name": "Dr. S. Iyer", "doctor_registration": "TN/1/2013"}),
            UploadedDocument(file_id="F20", file_name="bill.jpg",
                             actual_type=DocumentType.HOSPITAL_BILL,
                             content={"patient_name": "Deepak Shah",
                                      "hospital_name": "Apollo Hospitals",
                                      "line_items": [{"description": "Consultation", "amount": 4500}],
                                      "total": 4500}),
        ]
    )
    result = await process_claim(sub)
    assert result.decision == ClaimDecision.APPROVED
    assert result.approved_amount == pytest.approx(3240.0, abs=1.0)
    # Verify order: network discount applied before copay
    bd = result.financial_breakdown
    assert bd.get("network_discount") == pytest.approx(900.0, abs=1.0)
    assert bd.get("copay") == pytest.approx(360.0, abs=1.0)


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_graceful_degradation_tc011():
    """TC011 — simulate_component_failure=True: no crash, degraded=True, lower confidence"""
    sub = make_submission(
        member_id="EMP006",
        claim_category=ClaimCategory.ALTERNATIVE_MEDICINE,
        treatment_date=date(2024, 10, 28),
        claimed_amount=4000.0,
        simulate_component_failure=True,
        documents=[
            UploadedDocument(file_id="F21", file_name="rx.jpg",
                             actual_type=DocumentType.PRESCRIPTION,
                             content={"patient_name": "Kavita Nair",
                                      "diagnosis": "Chronic Joint Pain",
                                      "doctor_name": "Vaidya T. Krishnan",
                                      "doctor_registration": "AYUR/KL/2345/2019"}),
            UploadedDocument(file_id="F22", file_name="bill.jpg",
                             actual_type=DocumentType.HOSPITAL_BILL,
                             content={"patient_name": "Kavita Nair",
                                      "hospital_name": "Ayur Wellness Centre",
                                      "line_items": [{"description": "Panchakarma Therapy", "amount": 4000}],
                                      "total": 4000}),
        ]
    )
    result = await process_claim(sub)
    assert result.decision is not None
    assert result.degraded is True
    assert result.confidence_score < 0.85
    assert "manual review" in result.reason.lower() or "degraded" in result.reason.lower()


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_fraud_same_day_tc009():
    """TC009 — 4th claim same day → MANUAL_REVIEW"""
    sub = make_submission(
        member_id="EMP008",
        treatment_date=date(2024, 10, 30),
        claimed_amount=4800.0,
        claims_history=[
            {"claim_id": "CLM_0081", "date": "2024-10-30", "amount": 1200, "provider": "City Clinic A"},
            {"claim_id": "CLM_0082", "date": "2024-10-30", "amount": 1800, "provider": "City Clinic B"},
            {"claim_id": "CLM_0083", "date": "2024-10-30", "amount": 2100, "provider": "Wellness Center"},
        ]
    )
    result = await process_claim(sub)
    assert result.decision == ClaimDecision.MANUAL_REVIEW
    assert "SAME_DAY_CLAIM_PATTERN" in result.fraud_signals


@pytest.mark.asyncio
@freeze_time("2024-11-15")
async def test_excluded_bariatric_tc012():
    """TC012 — Bariatric consultation + diet program → REJECTED"""
    sub = make_submission(
        member_id="EMP009",
        treatment_date=date(2024, 10, 18),
        claimed_amount=8000.0,
        documents=[
            UploadedDocument(file_id="F23", file_name="rx.jpg",
                             actual_type=DocumentType.PRESCRIPTION,
                             content={"patient_name": "Anita Desai",
                                      "diagnosis": "Morbid Obesity — BMI 37",
                                      "doctor_name": "Dr. P. Banerjee",
                                      "doctor_registration": "WB/1/2015",
                                      "treatment": "Bariatric Consultation"}),
            UploadedDocument(file_id="F24", file_name="bill.jpg",
                             actual_type=DocumentType.HOSPITAL_BILL,
                             content={"patient_name": "Anita Desai",
                                      "hospital_name": "City Clinic",
                                      "line_items": [
                                          {"description": "Bariatric Consultation", "amount": 3000},
                                          {"description": "Personalised Diet Program", "amount": 5000}
                                      ],
                                      "total": 8000}),
        ]
    )
    result = await process_claim(sub)
    assert result.decision == ClaimDecision.REJECTED
    assert "EXCLUDED_CONDITION" in result.rejection_reasons
    assert result.confidence_score > 0.90
