from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import date, datetime


class ClaimCategory(str, Enum):
    CONSULTATION = "CONSULTATION"
    DIAGNOSTIC = "DIAGNOSTIC"
    PHARMACY = "PHARMACY"
    DENTAL = "DENTAL"
    VISION = "VISION"
    ALTERNATIVE_MEDICINE = "ALTERNATIVE_MEDICINE"


class DocumentType(str, Enum):
    PRESCRIPTION = "PRESCRIPTION"
    HOSPITAL_BILL = "HOSPITAL_BILL"
    LAB_REPORT = "LAB_REPORT"
    PHARMACY_BILL = "PHARMACY_BILL"
    DENTAL_REPORT = "DENTAL_REPORT"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    DIAGNOSTIC_REPORT = "DIAGNOSTIC_REPORT"
    UNKNOWN = "UNKNOWN"


class DocumentQuality(str, Enum):
    GOOD = "GOOD"
    PARTIAL = "PARTIAL"
    UNREADABLE = "UNREADABLE"


class ClaimDecision(str, Enum):
    APPROVED = "APPROVED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class UploadedDocument(BaseModel):
    file_id: str
    file_name: str = ""
    file_content_base64: Optional[str] = None
    actual_type: Optional[DocumentType] = None      # injected in test cases
    quality: Optional[DocumentQuality] = None       # injected in test cases (TC002)
    patient_name_on_doc: Optional[str] = None       # injected in test cases (TC003)
    content: Optional[Dict[str, Any]] = None        # injected structured content for tests


class ClassifiedDocument(BaseModel):
    file_id: str
    file_name: str
    file_content_base64: Optional[str] = None
    classified_type: DocumentType
    classification_confidence: float
    classification_signals: List[str] = []
    quality: DocumentQuality = DocumentQuality.GOOD
    extracted_patient_name: Optional[str] = None
    content: Optional[Dict[str, Any]] = None


class ExtractedField(BaseModel):
    value: Optional[Any] = None
    confidence: float = 0.0
    note: Optional[str] = None


class ExtractedLineItem(BaseModel):
    description: str
    amount: float
    coverage_status: Optional[str] = None  # COVERED, EXCLUDED, UNKNOWN


class ExtractedClaimData(BaseModel):
    patient_name: ExtractedField = ExtractedField()
    doctor_name: ExtractedField = ExtractedField()
    doctor_registration: ExtractedField = ExtractedField()
    diagnosis: List[str] = []
    treatment_date: ExtractedField = ExtractedField()
    hospital_name: ExtractedField = ExtractedField()
    line_items: List[ExtractedLineItem] = []
    total_amount: ExtractedField = ExtractedField()
    extraction_confidence: float = 1.0
    raw_extractions: Dict[str, Any] = {}

    @classmethod
    def empty(cls) -> "ExtractedClaimData":
        return cls(extraction_confidence=0.0)


class LineItemDecision(BaseModel):
    description: str
    claimed_amount: float
    approved_amount: float
    status: str
    reason: Optional[str] = None


class ClaimSubmission(BaseModel):
    member_id: str
    policy_id: str
    claim_category: ClaimCategory
    treatment_date: date
    claimed_amount: float
    documents: List[UploadedDocument]
    hospital_name: Optional[str] = None
    ytd_claims_amount: Optional[float] = 0.0
    claims_history: Optional[List[Dict[str, Any]]] = []
    simulate_component_failure: Optional[bool] = False


class ClaimResult(BaseModel):
    claim_id: str
    member_id: str
    treatment_date: Optional[date] = None
    hospital_name: Optional[str] = None
    decision: Optional[ClaimDecision] = None
    approved_amount: Optional[float] = None
    claimed_amount: float
    reason: str
    confidence_score: float
    financial_breakdown: Dict[str, float] = {}
    line_items: List[LineItemDecision] = []
    rejection_reasons: List[str] = []
    fraud_signals: List[str] = []
    manual_review_reasons: List[str] = []
    degraded: bool = False
    failed_agents: List[str] = []
    graph_path: List[str] = []   # which nodes executed in what order
    trace: Optional[Any] = None
    created_at: str = ""
