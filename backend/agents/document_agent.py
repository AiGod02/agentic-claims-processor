import asyncio
import difflib
import io
import base64
from pypdf import PdfReader
from agents.base import BaseAgent
from models.claim import (
    ClassifiedDocument, DocumentType, DocumentQuality,
    ExtractedClaimData, ExtractedField, ExtractedLineItem
)
from models.trace import AgentStep, StepStatus, CheckResult
from services.gemini_client import call_gemini_vision, call_gemini_text
from services.groq_client import call_groq_vision
import logging


logger = logging.getLogger(__name__)

DOCUMENT_TYPE_ENUM = [
    "PRESCRIPTION", "HOSPITAL_BILL", "LAB_REPORT",
    "PHARMACY_BILL", "DENTAL_REPORT", "DISCHARGE_SUMMARY",
    "DIAGNOSTIC_REPORT", "UNKNOWN"
]

MEDICAL_SHORTHAND = {
    "HTN": "Hypertension", "T2DM": "Type 2 Diabetes Mellitus",
    "DM": "Diabetes Mellitus", "URI": "Upper Respiratory Infection",
    "URTI": "Upper Respiratory Tract Infection", "UTI": "Urinary Tract Infection",
    "GERD": "Gastroesophageal Reflux Disease", "IBS": "Irritable Bowel Syndrome",
    "COPD": "Chronic Obstructive Pulmonary Disease", "CAD": "Coronary Artery Disease",
    "MI": "Myocardial Infarction", "CVA": "Cerebrovascular Accident",
    "OA": "Osteoarthritis", "RA": "Rheumatoid Arthritis",
}



def extract_text_from_pdf_base64(pdf_base64: str) -> str:
    try:
        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF locally: {e}")
        return ""


def extract_image_from_pdf_base64(pdf_base64: str) -> tuple[str | None, str]:
    try:
        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        if len(reader.pages) > 0:
            page = reader.pages[0]
            if len(page.images) > 0:
                img = page.images[0]
                img_b64 = base64.b64encode(img.data).decode("utf-8")
                media_type = "image/jpeg"
                if img.name and img.name.lower().endswith(".png"):
                    media_type = "image/png"
                elif img.name and img.name.lower().endswith(".gif"):
                    media_type = "image/gif"
                return img_b64, media_type
    except Exception as e:
        logger.error(f"Failed to extract image from PDF: {e}")
    return None, ""


def classify_by_filename(filename: str, claim_category: str = None) -> dict:
    filename_lower = (filename or "").lower()
    doc_type = "UNKNOWN"
    if "prescription" in filename_lower:
        doc_type = "PRESCRIPTION"
    elif "hospital_bill" in filename_lower:
        doc_type = "HOSPITAL_BILL"
    elif "pharmacy_bill" in filename_lower:
        doc_type = "PHARMACY_BILL"
    elif "pharmacy" in filename_lower:
        doc_type = "PHARMACY_BILL"
    elif "diagnostic" in filename_lower or "report" in filename_lower or "lab_report" in filename_lower:
        doc_type = "LAB_REPORT"
    elif "dental" in filename_lower:
        doc_type = "DENTAL_REPORT"
    elif "discharge" in filename_lower:
        doc_type = "DISCHARGE_SUMMARY"
    elif "bill" in filename_lower:
        if claim_category == "PHARMACY":
            doc_type = "PHARMACY_BILL"
        else:
            doc_type = "HOSPITAL_BILL"
            
    quality = "GOOD"
    if "blurry" in filename_lower or "unreadable" in filename_lower:
        quality = "UNREADABLE"
        
    return {
        "document_type": doc_type,
        "confidence": 0.5,
        "signals": ["filename_heuristic"],
        "patient_name": None,
        "quality": quality
    }


def normalize_document_type(doc_type_str: str) -> DocumentType:
    if not doc_type_str:
        return DocumentType.UNKNOWN
    val = doc_type_str.upper().strip()
    try:
        return DocumentType(val)
    except ValueError:
        pass
    
    # Try fuzzy mapping or prefix matching
    if "BILL" in val or "INVOICE" in val or "RECEIPT" in val:
        if "PHARMACY" in val or "MEDICINE" in val:
            return DocumentType.PHARMACY_BILL
        return DocumentType.HOSPITAL_BILL
    if "PRESCRIPTION" in val:
        return DocumentType.PRESCRIPTION
    if "PHARMACY" in val or "MEDICINE" in val:
        return DocumentType.PHARMACY_BILL
    if "DENTAL" in val:
        return DocumentType.DENTAL_REPORT
    if "LAB" in val:
        return DocumentType.LAB_REPORT
    if "DIAGNOSTIC" in val:
        return DocumentType.LAB_REPORT
    if "DISCHARGE" in val:
        return DocumentType.DISCHARGE_SUMMARY
    return DocumentType.UNKNOWN


def normalize_quality(quality_str: str) -> DocumentQuality:
    if not quality_str:
        return DocumentQuality.GOOD
    val = quality_str.upper().strip()
    try:
        return DocumentQuality(val)
    except ValueError:
        pass
    if "UNREADABLE" in val or "BLURRY" in val or "POOR" in val or "BAD" in val:
        return DocumentQuality.UNREADABLE
    if "PARTIAL" in val or "MEDIUM" in val or "AVERAGE" in val:
        return DocumentQuality.PARTIAL
    return DocumentQuality.GOOD


class DocumentAgent(BaseAgent):
    name = "DocumentAgent"
    node_name = "document_agent"

    async def run(self, state: dict) -> dict:
        submission = state["submission"]
        policy = state["policy_data"]
        trace = state["trace"]

        # ── SUB-STEP 1: CLASSIFY ──────────────────────────────────────────
        ctx = self._start_step(
            f"Classifying {len(submission.documents)} documents for "
            f"{submission.claim_category} claim"
        )
        classified = []
        classification_llm_calls = []

        for doc in submission.documents:
            if doc.actual_type is not None:
                classified.append(ClassifiedDocument(
                    file_id=doc.file_id,
                    file_name=doc.file_name or f"{doc.file_id}.jpg",
                    file_content_base64=doc.file_content_base64,
                    classified_type=doc.actual_type,
                    classification_confidence=1.0,
                    classification_signals=["test_case_injection"],
                    quality=doc.quality or DocumentQuality.GOOD,
                    extracted_patient_name=doc.patient_name_on_doc,
                    content=doc.content
                ))
                continue

            try:
                if len(classification_llm_calls) > 0:
                    await asyncio.sleep(1.5)  # 1.5s delay to prevent rate limits on free-tier keys
                filename_hint = doc.file_name or "unknown"
                prompt = f"""You are analyzing an Indian medical document image.
The uploaded filename is: "{filename_hint}"

Classify this document into exactly one of these types:
{', '.join(DOCUMENT_TYPE_ENUM)}

Semantic Guidelines for Document Classification:
- "PRESCRIPTION" (Rx): Doctor's prescription containing diagnosis, symptoms, and prescribed medicines/tests.
- "HOSPITAL_BILL": Any doctor consultation bill, hospital invoice, clinical treatment receipt, or dental treatment statement/invoice.
- "LAB_REPORT": Any lab test result (blood, urine, CBC, etc.), radiology scan report (MRI, CT, PET, X-Ray), or diagnostic report.
- "PHARMACY_BILL": Pharmacy invoice showing list of medicines purchased and pharmacy details.
- "DENTAL_REPORT": Specialist dental diagnostic reports/charts (excluding invoice/billing statements).
- "DISCHARGE_SUMMARY": Summary issued by hospital at discharge.

Note: Map any invoice/receipt to its respective bill type (e.g. dental bill is HOSPITAL_BILL, pharmacy bill is PHARMACY_BILL). Map any diagnostic/scan report (MRI/CT/PET/CBC) to LAB_REPORT.

If the image is extremely blurry, unreadable, or dark, use the filename as a strong hint to identify the document type, and mark the quality as "UNREADABLE".

Also extract the patient name if visible.

Return JSON:
{{
  "document_type": "<TYPE>",
  "confidence": <0.0-1.0>,
  "signals": ["<signal1>", "<signal2>"],
  "patient_name": "<name or null>",
  "quality": "<GOOD|PARTIAL|UNREADABLE>"
}}"""

                media_type = "image/jpeg"
                if doc.file_name and doc.file_name.lower().endswith(".pdf"):
                    media_type = "application/pdf"

                try:
                    result = call_gemini_vision(doc.file_content_base64, media_type, prompt)
                except Exception as ex:
                    logger.warning(f"Gemini vision classification failed for {doc.file_id}: {ex}. Falling back.")
                    if media_type == "application/pdf":
                        pdf_text = extract_text_from_pdf_base64(doc.file_content_base64)
                        if pdf_text:
                            logger.info(f"Extracted {len(pdf_text)} chars of text from PDF local fallback. Calling Groq text model.")
                            from services.groq_client import call_groq
                            text_prompt = f"{prompt}\n\nHere is the text extracted from the document:\n{pdf_text}"
                            result = call_groq(text_prompt)
                        else:
                            # Try to extract image from PDF for Groq Vision fallback
                            img_b64, img_media = extract_image_from_pdf_base64(doc.file_content_base64)
                            if img_b64:
                                logger.info(f"Extracted wrapped image from PDF for Groq Vision fallback.")
                                result = call_groq_vision(img_b64, img_media, prompt)
                            else:
                                logger.warning(f"Could not extract text or image from PDF '{doc.file_name}'. Using filename heuristics.")
                                result = classify_by_filename(doc.file_name, submission.claim_category.value)
                    else:
                        result = call_groq_vision(doc.file_content_base64, media_type, prompt)
                classification_llm_calls.append(result.get("_meta", {}))

                classified.append(ClassifiedDocument(
                    file_id=doc.file_id,
                    file_name=doc.file_name or f"{doc.file_id}.jpg",
                    file_content_base64=doc.file_content_base64,
                    classified_type=normalize_document_type(result.get("document_type")),
                    classification_confidence=result.get("confidence", 0.5),
                    classification_signals=result.get("signals", []),
                    quality=normalize_quality(result.get("quality")),
                    extracted_patient_name=result.get("patient_name"),
                    content=doc.content
                ))
            except Exception as e:
                logger.error(f"Classification failed for {doc.file_id}: {e}. Falling back to filename heuristics.")
                heuristic_res = classify_by_filename(doc.file_name, submission.claim_category.value)
                classified.append(ClassifiedDocument(
                    file_id=doc.file_id,
                    file_name=doc.file_name or f"{doc.file_id}.jpg",
                    file_content_base64=doc.file_content_base64,
                    classified_type=DocumentType(heuristic_res.get("document_type", "UNKNOWN")),
                    classification_confidence=0.5,
                    classification_signals=[f"error: {str(e)}", "filename_heuristic"],
                    quality=DocumentQuality(heuristic_res.get("quality", "UNREADABLE")),
                    extracted_patient_name=None,
                    content=doc.content
                ))

        classify_step = self._finish_step(
            ctx, StepStatus.PASSED,
            f"Classified {len(classified)} documents: "
            f"{[f'{d.file_id}={d.classified_type}' for d in classified]}",
            checks=[CheckResult(
                check_name="document_classification",
                passed=all(d.classified_type != DocumentType.UNKNOWN for d in classified),
                detail=f"{sum(1 for d in classified if d.classified_type != DocumentType.UNKNOWN)}"
                       f"/{len(classified)} documents classified",
                rule_source="document_agent.classifier"
            )],
            errors=[], confidence_impact=0.0, llm_calls=classification_llm_calls
        )
        trace.add_step(classify_step)

        # ── SUB-STEP 2: QUALITY + INTEGRITY CHECK ────────────────────────
        ctx = self._start_step(
            f"Quality and integrity check for {submission.claim_category} claim"
        )
        doc_requirements = policy["document_requirements"].get(submission.claim_category.value, {})
        required_types = doc_requirements.get("required", [])

        # Map UNKNOWN documents (e.g. blurry/unreadable uploads) to any missing required document types
        submitted_types_init = {d.classified_type.value for d in classified}
        submitted_types_satisfying_req = submitted_types_init | ({"LAB_REPORT"} if "DIAGNOSTIC_REPORT" in submitted_types_init else set())
        missing_required_types = [req for req in required_types if req not in submitted_types_satisfying_req]
        unknown_docs = [d for d in classified if d.classified_type == DocumentType.UNKNOWN]
        for doc in unknown_docs:
            if missing_required_types:
                mapped_type = DocumentType(missing_required_types.pop(0))
                doc.classified_type = mapped_type
                doc.quality = DocumentQuality.UNREADABLE  # Force to UNREADABLE since it couldn't be classified
                doc.classification_signals.append("inferred_from_claim_context")
                logger.info(f"Inferred document type {mapped_type} for file {doc.file_name} from claim context")

        submitted_types = {d.classified_type.value for d in classified}

        quality_checks = []
        blocking_errors = []

        # Check A: Required document types present
        for req_type in required_types:
            has_doc = req_type in submitted_types
            if req_type == "LAB_REPORT" and "DIAGNOSTIC_REPORT" in submitted_types:
                has_doc = True

            if not has_doc:
                submitted_list = list(submitted_types)
                error_msg = (
                    f"You submitted {submitted_list} but a {req_type} is required for a "
                    f"{submission.claim_category.value} claim. "
                    f"Please upload a {req_type} to proceed."
                )
                blocking_errors.append(error_msg)
                quality_checks.append(CheckResult(
                    check_name=f"required_document_{req_type}",
                    passed=False,
                    expected=req_type, actual=str(submitted_list),
                    detail=error_msg,
                    rule_source=f"policy_terms.json > document_requirements > {submission.claim_category.value}"
                ))
            else:
                quality_checks.append(CheckResult(
                    check_name=f"required_document_{req_type}",
                    passed=True, detail=f"{req_type} present",
                    rule_source=f"policy_terms.json > document_requirements > {submission.claim_category.value}"
                ))

        # Check B: Unreadable documents
        unreadable = [d for d in classified if d.quality == DocumentQuality.UNREADABLE]
        for doc in unreadable:
            error_msg = (
                f"Your {doc.classified_type.value} (file: {doc.file_name}) could not be read "
                f"clearly. Please re-upload a clearer photo or scan of this document."
            )
            blocking_errors.append(error_msg)
            quality_checks.append(CheckResult(
                check_name=f"document_readability_{doc.file_id}", passed=False,
                detail=error_msg, rule_source="document_agent.quality_checker"
            ))

        # Check C: Patient name cross-document consistency
        names_with_source = [
            (d.extracted_patient_name, d.classified_type.value, d.file_name)
            for d in classified if d.extracted_patient_name
        ]
        if len(names_with_source) >= 2:
            base_name, base_type, base_file = names_with_source[0]
            for other_name, other_type, other_file in names_with_source[1:]:
                ratio = difflib.SequenceMatcher(
                    None, base_name.lower().strip(), other_name.lower().strip()
                ).ratio()
                if ratio < 0.75:
                    error_msg = (
                        f"The patient name on your {base_type} reads '{base_name}' but your "
                        f"{other_type} shows '{other_name}'. All documents must belong to the "
                        f"same patient. Please verify and resubmit."
                    )
                    blocking_errors.append(error_msg)
                    quality_checks.append(CheckResult(
                        check_name="patient_name_consistency", passed=False,
                        expected=base_name, actual=other_name, detail=error_msg,
                        rule_source="document_agent.integrity_checker"
                    ))
                else:
                    quality_checks.append(CheckResult(
                        check_name="patient_name_consistency", passed=True,
                        detail=f"Names match: '{base_name}' ≈ '{other_name}' (ratio: {ratio:.2f})",
                        rule_source="document_agent.integrity_checker"
                    ))

        if blocking_errors:
            quality_step = self._finish_step(
                ctx, StepStatus.FAILED,
                f"BLOCKING: {len(blocking_errors)} document problem(s) found. Pipeline halted.",
                checks=quality_checks, errors=blocking_errors, confidence_impact=-1.0
            )
            trace.add_step(quality_step)
            return {
                "classified_documents": classified,
                "blocking_error": "\n\n".join(blocking_errors),
                "document_agent_passed": False,
                "trace": trace,
                "degraded": False, "failed_agents": []
            }

        quality_step = self._finish_step(
            ctx, StepStatus.PASSED,
            f"All {len(required_types)} required documents present. Quality checks passed.",
            checks=quality_checks, errors=[], confidence_impact=0.0
        )
        trace.add_step(quality_step)

        # ── SUB-STEP 3: INFORMATION EXTRACTION ───────────────────────────
        ctx = self._start_step(
            f"Extracting structured data from {len(classified)} documents"
        )
        extraction_llm_calls = []
        all_line_items = []
        extracted_diagnosis = []
        patient_name = ExtractedField()
        doctor_name = ExtractedField()
        doctor_registration = ExtractedField()
        treatment_date = ExtractedField()
        hospital_name = ExtractedField()
        total_amount = ExtractedField()
        raw_extractions = {}
        extracted_names = []

        for doc in classified:
            result = None
            if doc.content:
                result = doc.content
                raw_extractions[doc.file_id] = result
            elif doc.file_content_base64:
                try:
                    if len(extraction_llm_calls) > 0:
                        await asyncio.sleep(1.5)  # 1.5s delay to prevent rate limits on free-tier keys
                    shorthand_map = ", ".join([f"{k}={v}" for k, v in MEDICAL_SHORTHAND.items()])
                    prompt = self._build_extraction_prompt(doc.classified_type, shorthand_map)
                    media_type = "application/pdf" if doc.file_name.lower().endswith(".pdf") else "image/jpeg"
                    try:
                        result = call_gemini_vision(doc.file_content_base64, media_type, prompt)
                    except Exception as ex:
                        logger.warning(f"Gemini vision extraction failed for {doc.file_id}: {ex}. Falling back.")
                        if media_type == "application/pdf":
                            pdf_text = extract_text_from_pdf_base64(doc.file_content_base64)
                            if pdf_text:
                                logger.info(f"Extracted {len(pdf_text)} chars of text from PDF local fallback. Calling Groq text model.")
                                from services.groq_client import call_groq
                                text_prompt = f"{prompt}\n\nHere is the text extracted from the document:\n{pdf_text}"
                                result = call_groq(text_prompt)
                            else:
                                # Try to extract image from PDF for Groq Vision fallback
                                img_b64, img_media = extract_image_from_pdf_base64(doc.file_content_base64)
                                if img_b64:
                                    logger.info(f"Extracted wrapped image from PDF for Groq Vision fallback.")
                                    result = call_groq_vision(img_b64, img_media, prompt)
                                else:
                                    logger.warning(f"Could not extract text or image from PDF '{doc.file_name}' for extraction.")
                                    result = {}
                        else:
                            result = call_groq_vision(doc.file_content_base64, media_type, prompt)
                    extraction_llm_calls.append(result.get("_meta", {}))
                    raw_extractions[doc.file_id] = result
                except Exception as e:
                    logger.error(f"Extraction failed for {doc.file_id}: {e}")
                    raw_extractions[doc.file_id] = {"error": str(e)}

            if not result:
                continue

            # Collect patient name for cross-document verification
            pat_field = result.get("patient_name")
            doc_pat_val = None
            if isinstance(pat_field, dict):
                doc_pat_val = pat_field.get("value")
            elif isinstance(pat_field, str):
                doc_pat_val = pat_field
            if doc_pat_val:
                extracted_names.append((doc_pat_val, doc.classified_type.value, doc.file_name))

            if doc.classified_type == DocumentType.PRESCRIPTION:
                pat_val = None
                pat_conf = 1.0
                pat_field = result.get("patient_name")
                if isinstance(pat_field, dict):
                    pat_val = pat_field.get("value")
                    pat_conf = pat_field.get("confidence", 1.0)
                elif isinstance(pat_field, str):
                    pat_val = pat_field

                if pat_val:
                    patient_name = ExtractedField(value=pat_val, confidence=float(pat_conf))

                doc_val = None
                doc_conf = 1.0
                doc_field = result.get("doctor_name")
                if isinstance(doc_field, dict):
                    doc_val = doc_field.get("value")
                    doc_conf = doc_field.get("confidence", 1.0)
                elif isinstance(doc_field, str):
                    doc_val = doc_field

                if doc_val:
                    doctor_name = ExtractedField(value=doc_val, confidence=float(doc_conf))

                reg_val = None
                reg_conf = 1.0
                reg_field = result.get("doctor_registration")
                if isinstance(reg_field, dict):
                    reg_val = reg_field.get("value")
                    reg_conf = reg_field.get("confidence", 1.0)
                elif isinstance(reg_field, str):
                    reg_val = reg_field

                if reg_val:
                    doctor_registration = ExtractedField(value=reg_val, confidence=float(reg_conf))

                diag_field = result.get("diagnosis")
                if isinstance(diag_field, str):
                    diag_list = [diag_field]
                elif isinstance(diag_field, list):
                    diag_list = diag_field
                else:
                    diag_list = []
                for diag in diag_list:
                    if diag:
                        expanded = MEDICAL_SHORTHAND.get(diag.upper(), diag)
                        if expanded not in extracted_diagnosis:
                            extracted_diagnosis.append(expanded)

            elif doc.classified_type in (DocumentType.HOSPITAL_BILL, DocumentType.PHARMACY_BILL):
                hosp_val = None
                hosp_conf = 1.0
                hosp_field = result.get("hospital_name") or result.get("pharmacy_name")
                if isinstance(hosp_field, dict):
                    hosp_val = hosp_field.get("value")
                    hosp_conf = hosp_field.get("confidence", 1.0)
                elif isinstance(hosp_field, str):
                    hosp_val = hosp_field

                if hosp_val:
                    hospital_name = ExtractedField(value=hosp_val, confidence=float(hosp_conf))

                if not patient_name.value:
                    pat_val = None
                    pat_conf = 1.0
                    pat_field = result.get("patient_name")
                    if isinstance(pat_field, dict):
                        pat_val = pat_field.get("value")
                        pat_conf = pat_field.get("confidence", 1.0)
                    elif isinstance(pat_field, str):
                        pat_val = pat_field

                    if pat_val:
                        patient_name = ExtractedField(value=pat_val, confidence=float(pat_conf))

                tot_val = None
                tot_conf = 1.0
                tot_field = result.get("total")
                if isinstance(tot_field, dict):
                    tot_val = tot_field.get("value")
                    tot_conf = tot_field.get("confidence", 1.0)
                else:
                    tot_val = tot_field

                if tot_val is not None:
                    try:
                        total_amount = ExtractedField(value=float(tot_val), confidence=float(tot_conf))
                    except (ValueError, TypeError):
                        pass

                for item in result.get("line_items", []):
                    if isinstance(item, dict):
                        desc = item.get("description", "")
                        amt = item.get("amount", 0.0)
                        try:
                            amt = float(amt)
                        except (ValueError, TypeError):
                            amt = 0.0
                        all_line_items.append(ExtractedLineItem(
                            description=desc,
                            amount=amt
                        ))

        fields = [patient_name, doctor_name, total_amount]
        extraction_confidence = sum(f.confidence for f in fields) / len(fields)

        extracted = ExtractedClaimData(
            patient_name=patient_name, doctor_name=doctor_name,
            doctor_registration=doctor_registration, diagnosis=extracted_diagnosis,
            treatment_date=treatment_date, hospital_name=hospital_name,
            line_items=all_line_items, total_amount=total_amount,
            extraction_confidence=extraction_confidence, raw_extractions=raw_extractions
        )

        confidence_impact = -0.15 if extraction_confidence < 0.7 else 0.0

        # Check patient name consistency across all extracted data
        extraction_checks = [CheckResult(
            check_name="extraction_completeness",
            passed=extraction_confidence >= 0.7,
            detail=f"Extraction confidence: {extraction_confidence:.2f}",
            rule_source="document_agent.extractor"
        )]
        blocking_errors = []
        if len(extracted_names) >= 2:
            base_name, base_type, base_file = extracted_names[0]
            for other_name, other_type, other_file in extracted_names[1:]:
                ratio = difflib.SequenceMatcher(
                    None, base_name.lower().strip(), other_name.lower().strip()
                ).ratio()
                if ratio < 0.75:
                    error_msg = (
                        f"The patient name on your {base_type} reads '{base_name}' but your "
                        f"{other_type} shows '{other_name}'. All documents must belong to the "
                        f"same patient. Please verify and resubmit."
                    )
                    blocking_errors.append(error_msg)
                    extraction_checks.append(CheckResult(
                        check_name="patient_name_consistency", passed=False,
                        expected=base_name, actual=other_name, detail=error_msg,
                        rule_source="document_agent.integrity_checker"
                    ))
                else:
                    extraction_checks.append(CheckResult(
                        check_name="patient_name_consistency", passed=True,
                        detail=f"Names match: '{base_name}' ≈ '{other_name}' (ratio: {ratio:.2f})",
                        rule_source="document_agent.integrity_checker"
                    ))

        if blocking_errors:
            extraction_step = self._finish_step(
                ctx, StepStatus.FAILED,
                f"BLOCKING: {len(blocking_errors)} document problem(s) found. Pipeline halted.",
                checks=extraction_checks, errors=blocking_errors, confidence_impact=-1.0
            )
            trace.add_step(extraction_step)
            return {
                "classified_documents": classified,
                "blocking_error": "\n\n".join(blocking_errors),
                "document_agent_passed": False,
                "trace": trace,
                "degraded": False, "failed_agents": []
            }

        extraction_step = self._finish_step(
            ctx,
            StepStatus.PASSED if extraction_confidence >= 0.5 else StepStatus.DEGRADED,
            f"Extracted: patient='{patient_name.value}', diagnosis={extracted_diagnosis}, "
            f"total=₹{total_amount.value}, line_items={len(all_line_items)}, "
            f"extraction_confidence={extraction_confidence:.2f}",
            checks=extraction_checks,
            errors=[], confidence_impact=confidence_impact, llm_calls=extraction_llm_calls
        )
        trace.add_step(extraction_step)

        return {
            "classified_documents": classified,
            "extracted_data": extracted,
            "document_agent_passed": True,
            "trace": trace,
        }

    def _build_extraction_prompt(self, doc_type, shorthand_map: str) -> str:
        base = f"Extract structured information from this Indian medical document.\nMedical shorthand: {shorthand_map}\n\n"
        if doc_type == DocumentType.PRESCRIPTION:
            return base + 'Return JSON: {"doctor_name": {"value": "", "confidence": 0.0}, "patient_name": {"value": "", "confidence": 0.0}, "doctor_registration": {"value": "", "confidence": 0.0}, "diagnosis": [""], "medicines": [{"name": "", "dosage": "", "duration": ""}]}'
        elif doc_type in (DocumentType.HOSPITAL_BILL, DocumentType.PHARMACY_BILL):
            return base + 'Return JSON: {"hospital_name": {"value": "", "confidence": 0.0}, "patient_name": {"value": "", "confidence": 0.0}, "line_items": [{"description": "", "amount": 0.0}], "total": {"value": 0.0, "confidence": 0.0}}'
        else:
            return base + 'Return JSON with all visible fields as key-value pairs.'
