# Trade-offs & Design Rationale — Plum Claims Processing System

> *"Make conscious trade-offs and document them — your judgment about what to cut is part of what we are evaluating."* — Assignment Brief

This document catalogs every significant trade-off made during system development. Each entry explains **what we chose**, **what we gave up**, **why**, and **the impact**.

---

## 1. Speed vs. Accuracy — Dual LLM Strategy

| Dimension | Chosen Approach | Alternative |
|---|---|---|
| **Vision (Documents)** | Gemini 2.0 Flash Lite — fast, cheap, excellent at handwritten docs | GPT-4o — slightly better accuracy on edge cases, 10x more expensive |
| **Reasoning (Policy)** | Llama 3.3 70B via Groq — 150+ tok/s, near-instant | GPT-4o — better reasoning but 50-80 tok/s, 5x higher latency |

**What we gained**: Sub-second LLM responses for most operations. Total pipeline latency ≈ 3-10 seconds.  
**What we gave up**: Marginal accuracy improvement on extremely messy documents. GPT-4o would handle edge cases (e.g., heavily stamped documents with overlapping text) slightly better.  
**Why this is the right call**: At Plum's 75,000+ claims/year volume, speed and cost matter more than 2-3% accuracy improvement on edge cases. Edge cases already route to `MANUAL_REVIEW` via the confidence threshold.

---

## 2. Simplicity vs. Persistence — In-Memory Storage

| Dimension | Chosen | Given Up |
|---|---|---|
| **Setup complexity** | Zero-config (just `pip install`) | Database configuration, migrations, connection pooling |
| **Data persistence** | Lost on server restart | Permanent storage across restarts |
| **Query capability** | Linear scan of Python dict | SQL queries, indexes, aggregations |

**What we gained**: Evaluators can run the entire system in under 2 minutes with no external dependencies.  
**What we gave up**: Data persistence, concurrent access safety, query performance at scale.  
**Why this is the right call**: With 12 test cases and 10 members, the entire dataset fits in ~50KB of memory. Adding PostgreSQL would add 30+ minutes of setup time for zero functional benefit during evaluation.  
**Migration path**: See [FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md) § Database Layer.

---

## 3. Determinism vs. Intelligence — Rule-Based Fraud Detection

| Dimension | Chosen | Given Up |
|---|---|---|
| **Approach** | 5 weighted rules, pure Python | LLM-based fraud analysis, ML model |
| **Determinism** | 100% — same input → same output | Probabilistic with variance between runs |
| **Auditability** | Every flag and weight in the trace | Black-box "fraud score: 0.7" |

**What we gained**: Deterministic, auditable, fast (50ms vs 3-5s for LLM), zero API costs.  
**What we gave up**: Ability to detect novel fraud patterns, natural language reasoning about suspicious behavior, adaptive learning from historical data.  
**Why this is the right call**: Insurance fraud detection requires auditability for regulatory compliance. "The LLM thought this claim looked suspicious" is not acceptable in court. Every flag must trace back to a specific, documented rule.

---

## 4. Completeness vs. Time — Test Coverage Strategy

| Tested | Not Tested |
|---|---|
| All 12 test cases via automated eval runner | Frontend React components (no unit tests) |
| 9 unit tests covering critical paths | API route-level integration tests |
| Date handling, financial calculations, edge cases | Load/stress testing |
| Graceful degradation simulation | Concurrent claim submission |

**What we gained**: Confidence that all 12 expected outcomes are correct with full trace validation.  
**What we gave up**: Frontend test coverage, API integration tests, performance benchmarks.  
**Why this is the right call**: The assignment weights Engineering Quality at 25% and Observability at 20%. Backend correctness and trace completeness deliver 45% of the grade. Frontend tests (which would verify React rendering) don't directly impact the evaluation criteria. With 2-3 days, backend testing is the highest-ROI investment.

---

## 5. Flexibility vs. Safety — Policy Data as Raw Dict

| Dimension | Chosen | Given Up |
|---|---|---|
| **Policy data format** | Raw `dict` loaded from JSON | Pydantic model with typed fields |
| **Access pattern** | `policy_data["coverage"]["annual_opd_limit"]` | `policy.coverage.annual_opd_limit` |
| **Error behavior** | `KeyError` on missing keys | `ValidationError` at load time |

**What we gained**: Flexible key access across agents. No need to model every nested structure. Easy to extend with new policy fields without schema changes.  
**What we gave up**: Compile-time type safety, auto-completion in IDEs, early validation of policy file structure.  
**Why this is the right call**: The policy file has deeply nested, heterogeneous structures (e.g., `waiting_periods.specific_conditions` contains both `diabetes: {days: 90}` and arrays). Modeling this as Pydantic would require 15+ nested models for a file that changes rarely. The flexibility of raw dict access outweighs the safety benefit.

---

## 6. Security vs. Evaluation Convenience — CORS & Authentication

| Dimension | Chosen | Production Requirement |
|---|---|---|
| **CORS** | `allow_origins=["*"]` | Specific allowed origins only |
| **Authentication** | None | JWT/OAuth2 for all API endpoints |
| **Rate limiting** | None | Per-user rate limits to prevent abuse |
| **API key exposure** | Keys in `.env` file | Secrets manager (AWS Secrets Manager, GCP Secret Manager) |

**What we gained**: Evaluators can test from any origin, any tool (Postman, curl, browser), without auth setup.  
**What we gave up**: All production security controls.  
**Why this is the right call**: This is an assessment. Adding authentication would add complexity without demonstrating claims processing ability. The `.env` file is `.gitignore`'d. Production security requirements are documented in [FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md).

---

## 7. Monolith vs. Microservices

| Dimension | Chosen | Alternative |
|---|---|---|
| **Architecture** | Monolithic FastAPI app | Microservices (Document Service, Policy Service, Decision Service) |
| **Deployment** | Single process on Render | Container orchestration (K8s) |
| **Communication** | In-process function calls | HTTP/gRPC between services |

**What we gained**: Simplicity. One process, one deployment, one log stream, no network latency between agents.  
**What we gave up**: Independent scaling, independent deployment, team ownership boundaries.  
**Why this is the right call**: At current scale (75K claims/year ≈ 200 claims/day ≈ 8 claims/hour), a single FastAPI process handles all traffic with room to spare. Microservices add operational overhead (service discovery, distributed tracing, network failures) that isn't justified until we hit 10x+ volume. The modular agent architecture makes future extraction into microservices straightforward — each agent already has a clean interface contract.

---

## 8. Synchronous vs. Asynchronous API

| Dimension | Chosen | Alternative |
|---|---|---|
| **Claim processing** | Synchronous — `/submit` waits for result | Async — `/submit` returns job ID, `/status` polls |
| **User experience** | ~3-10s wait, then full result | Instant acknowledgment, background processing |

**What we gained**: Simpler frontend logic. No polling, no WebSockets, no loading states beyond the initial spinner.  
**What we gave up**: Responsive UI during processing, ability to show real-time progress of individual agents.  
**Why this is the right call**: With pipeline latency of 3-10s, synchronous processing is acceptable for evaluation. The user sees a loading indicator, then the full result. An async architecture would require job queues (Celery/Redis), WebSocket connections, and complex frontend state management — disproportionate engineering effort for the benefit.

---

## 9. Custom Trace vs. OpenTelemetry

| Dimension | Chosen | Alternative |
|---|---|---|
| **Trace format** | Custom `ClaimTrace` → `AgentStep` → `CheckResult` | OpenTelemetry spans with custom attributes |
| **Integration** | Self-contained, JSON-serializable | Requires OTEL collector, Jaeger/Tempo backend |

**What we gained**: Purpose-built trace structure that maps perfectly to claims processing (checks, rule_source, confidence_impact). Self-contained — no external infrastructure.  
**What we gave up**: Integration with industry-standard observability tools (Grafana, Jaeger, DataDog).  
**Why this is the right call**: OpenTelemetry is designed for distributed systems with spans/traces across service boundaries. Our monolithic agent architecture needs domain-specific trace fields (`rule_source`, `checks_performed`, `confidence_log`) that don't map cleanly to OTEL's span model. A custom trace gives us exactly the observability the assignment requires.

---

## 10. Time Investment Distribution

| Area | Time Spent | Justification |
|---|---|---|
| **System Design & Architecture** | 25% | Assignment weights this at 30%. LangGraph orchestration, agent contracts, state management. |
| **Agent Implementation** | 30% | Core business logic — document verification, policy rules, fraud detection, decision synthesis. |
| **Observability & Tracing** | 15% | Assignment weights this at 20%. Trace system, CheckResult with rule_source, confidence logging. |
| **Testing & Eval** | 15% | 9 unit tests + 12-case eval runner + eval report generation. |
| **Frontend & UX** | 10% | React SPA — ClaimForm, DecisionView, TraceViewer, GraphVisualizer. |
| **Documentation** | 5% | Architecture docs, contracts, trade-offs, future enhancements. |

**Key Trade-off**: We invested heavily in backend architecture and observability (70% of time) at the expense of frontend polish (10%). This directly maps to the assignment's evaluation weights: System Design (30%) + Observability (20%) + Engineering Quality (25%) = 75% of the grade comes from backend quality.

---

## Summary of Conscious Cuts

Things we deliberately **did not build** and why:

| Feature | Why Cut |
|---|---|
| **Local OCR fallback (Tesseract)** | Requires heavy system binaries (~100MB), performs poorly on handwritten Indian medical docs, and adds significant build time on free-tier platforms. Two cloud APIs (Gemini + Groq Vision) provide sufficient redundancy for assessment. See [ADR-013](./ARCHITECTURE_DECISIONS.md#adr-013-vision-fallback-chain--no-local-ocr). |
| **Database persistence** | Not needed for 12 test cases. Zero-config is more valuable for evaluators. |
| **Authentication/authorization** | Assessment doesn't require it. Would add complexity without demonstrating claims processing ability. |
| **Frontend unit tests** | Backend test coverage has higher ROI against evaluation criteria. |
| **Real-time processing updates** | Sync API is sufficient for 3-10s processing times. |
| **ML-based fraud model** | No training data. Rule-based is deterministic and auditable. |
| **Multi-language support** | All documents are in English (Indian medical context). Not required by spec. |
| **PDF rendering/preview** | Files are processed server-side. Frontend shows extracted data, not raw documents. |
| **Claim editing/resubmission** | Assignment requires submission and review, not iterative editing. |
