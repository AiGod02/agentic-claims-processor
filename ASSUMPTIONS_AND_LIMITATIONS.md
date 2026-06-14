# Assumptions & Limitations — Plum Claims Processing System

> *"If you are stuck for more than two hours on something, make an assumption, document it, and move on."* — Assignment Brief

---

## Assumptions Made

### Policy Assumptions

| # | Assumption | Rationale |
|---|---|---|
| A1 | **Single policy for all members**: All members belong to `PLUM_GHI_2024`. | `policy_terms.json` defines one policy. Multi-policy support is documented in Future Enhancements. |
| A2 | **Co-pay is applied on post-discount amount** (not original billed amount). | Standard practice in Indian health insurance. Network discount reduces cost, co-pay is member's share of the reduced cost. |
| A3 | **Line items with "excluded" keywords are always excluded**, regardless of context. | E.g., "Teeth Whitening" is excluded even if paired with a covered procedure. The excluded amount is subtracted before other calculations. |
| A4 | **Diagnosis matching uses semantic similarity**, not exact string matching. | "Type 2 Diabetes Mellitus" should match the `diabetes` waiting period rule. We use LLM-based semantic matching for this. |
| A5 | **Treatment date is trusted** from the claim submission form, not extracted from documents. | In production, dates should be cross-validated between submitted and extracted values. |

### Technical Assumptions

| # | Assumption | Rationale |
|---|---|---|
| A6 | **Documents are images (JPEG/PNG)**, not PDFs in production mode. | Gemini vision works with images. PDF support via `pypdf` is included for text extraction but the primary path is image-based. |
| A7 | **LLM API keys are valid and have sufficient quota.** | No fallback to a free/local model if API keys are exhausted. System returns errors on API failure (with retry). |
| A8 | **Single-user, single-session operation.** | No concurrent access protection on the in-memory store. Race conditions possible with simultaneous claims. |
| A9 | **English-language documents only.** | Indian medical documents may contain Hindi, Tamil, or other regional languages. Current LLM prompts are English-only. |
| A10 | **Server runs in a trusted network.** | No authentication, no rate limiting, `CORS: *`. Production requires full security stack. |

### Evaluation Assumptions

| # | Assumption | Rationale |
|---|---|---|
| A11 | **Test case dates can be shifted to current year.** | Policy validity period is 2024-2025. Eval mode shifts dates to match treatment year so tests pass in 2026+. |
| A12 | **Test documents use `actual_type` injection**, bypassing real Gemini classification. | Enables deterministic unit tests without API calls. Production path uses real Gemini vision. |
| A13 | **`claims_history` in test cases accurately represents prior claims.** | Fraud detection relies on submitted history + in-memory store. In production, this would come from a database. |

---

## Known Limitations

### Functional Limitations

| # | Limitation | Impact | Mitigation |
|---|---|---|---|
| L1 | **No persistent storage** | All claims lost on server restart | Production: migrate to PostgreSQL |
| L2 | **No authentication/authorization** | Any user can access any claim | Production: JWT + role-based access |
| L3 | **No real PDF processing in vision pipeline** | PDFs must be converted to images first | Add PDF page rendering via `pdf2image` |
| L4 | **Synchronous API** — client waits 3-10s for result | Poor UX for slow claims | Production: async + job queue |
| L5 | **No claim editing/resubmission** | Users must create new claims for corrections | Add claim amendment workflow |
| L6 | **No multi-language document support** | Regional language documents may not extract correctly | Add multilingual prompts, train on Indian language medical docs |
| L7 | **No file size/type validation on upload** | Could accept non-image files or very large files | Add server-side validation (max 10MB, image/* only) |

### AI/ML Limitations

| # | Limitation | Impact | Mitigation |
|---|---|---|---|
| L8 | **Gemini extraction confidence is self-reported** | Model may report high confidence on incorrect extractions | Cross-validate extracted data against submitted data |
| L9 | **No document forgery detection** | Photoshopped or AI-generated documents would pass | Add metadata analysis, template matching |
| L10 | **Fraud detection is rule-based only** | Cannot detect novel fraud patterns | Add ML model trained on historical fraud data |
| L11 | **LLM rate limits not handled gracefully** | Rapid submissions may hit API rate limits | Add client-side rate limiting, queue overflow handling |
| L12 | **No A/B testing framework** | Cannot compare model versions or rule changes | Add feature flags + metrics collection |

### Scale Limitations

| # | Limitation | Current Capacity | Required for 10x |
|---|---|---|---|
| L13 | **Single process** | ~8 claims/hour | 80+ claims/hour → horizontal scaling |
| L14 | **In-memory store** | ~1000 claims before memory pressure | Unlimited → PostgreSQL |
| L15 | **No caching** | Policy loaded from disk on every claim | Redis cache with TTL |
| L16 | **No connection pooling** | One LLM connection per request | Connection pool for Gemini/Groq clients |
| L17 | **No queue system** | Direct processing on request thread | Celery + RabbitMQ for background processing |

---

## Scope Boundaries — What Was Deliberately Excluded

| Feature | Reason for Exclusion |
|---|---|
| Email/SMS notifications | Not required by assignment spec |
| Claim history dashboard (member-facing) | Assignment focuses on submission + decision, not member portal |
| Policy renewal/management | Single static policy is sufficient for evaluation |
| Provider network management | Network hospitals are defined in `policy_terms.json`, no CRUD needed |
| Payment processing | Out of scope — system determines approved amount, not payment |
| Appeal workflow | Assignment doesn't mention appeals or resubmission |
| Document retention/archival | Documents are processed and discarded (no persistent storage) |
| Internationalization (i18n) | All content is English |
| Accessibility (WCAG compliance) | Limited to standard HTML semantics, no ARIA roles added |
| Mobile-responsive frontend | Basic responsiveness via CSS, not fully mobile-optimized |
