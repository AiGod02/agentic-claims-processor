# Future Enhancements — Plum Claims Processing System

> *"What are the limitations of your current design and how would you address them at 10x the current load?"* — Assignment Brief

This document outlines the production roadmap, scaling strategy, and feature enhancements for moving from the current assessment prototype to a system capable of handling Plum's target of **10 million lives by 2030** (estimated 1M+ claims/year).

---

## Table of Contents

1. [Scaling Strategy: 75K → 1M+ Claims/Year](#1-scaling-strategy-75k--1m-claimsyear)
2. [Database Layer](#2-database-layer)
3. [Async Processing Pipeline](#3-async-processing-pipeline)
4. [Security & Compliance](#4-security--compliance)
5. [Advanced Fraud Detection](#5-advanced-fraud-detection)
6. [Document Processing Improvements](#6-document-processing-improvements)
7. [Observability & Monitoring](#7-observability--monitoring)
8. [Multi-Tenancy & Policy Engine](#8-multi-tenancy--policy-engine)
9. [Operational Dashboard](#9-operational-dashboard)
10. [Performance Benchmarks](#10-performance-benchmarks)

---

## 1. Scaling Strategy: 75K → 1M+ Claims/Year

### Current Capacity
- **Single process**: FastAPI with uvicorn, single worker.
- **Throughput**: ~8 claims/hour (limited by LLM API latency of 3-10s per claim).
- **Bottleneck**: Sequential LLM calls within each claim.

### Phase 1: 10x Scale (750K claims/year)

```
┌─────────────────────────────────────────────────────────────┐
│                     NGINX / ALB                             │
│                    (Load Balancer)                           │
└──────────┬────────────┬───────────────┬─────────────────────┘
           │            │               │
    ┌──────▼──────┐ ┌───▼────────┐ ┌───▼────────┐
    │  FastAPI #1  │ │ FastAPI #2  │ │ FastAPI #3  │  (Gunicorn workers)
    └──────┬──────┘ └───┬────────┘ └───┬────────┘
           │            │               │
           └────────────┼───────────────┘
                        │
                ┌───────▼────────┐
                │   PostgreSQL    │   (Claims, Members, Policies)
                │   + Redis       │   (Caching, Rate Limiting)
                └────────────────┘
```

**Key changes:**
- **Horizontal scaling**: Run 4-8 Gunicorn workers behind a load balancer.
- **PostgreSQL**: Persistent storage with connection pooling (PgBouncer).
- **Redis**: Cache policy data (changes rarely), rate limit LLM API calls.
- **Estimated throughput**: ~50-80 claims/hour per worker × 8 workers = 400-640 claims/hour.

### Phase 2: 100x Scale (7.5M claims/year)

```
┌───────────────────────────────────────────────────────────────────────┐
│                          API Gateway                                  │
│                    (Kong / AWS API Gateway)                            │
└────────────┬───────────────┬──────────────────┬───────────────────────┘
             │               │                  │
     ┌───────▼──────┐  ┌────▼────────┐  ┌──────▼──────┐
     │   API Service  │  │  API Service │  │ API Service  │  (K8s pods)
     └───────┬──────┘  └────┬────────┘  └──────┬──────┘
             │               │                  │
             └───────────────┼──────────────────┘
                             │
                     ┌───────▼────────┐
                     │  Message Queue  │   (RabbitMQ / SQS)
                     └───────┬────────┘
                             │
             ┌───────────────┼───────────────┐
     ┌───────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
     │  Worker #1    │ │  Worker #2  │ │  Worker #N   │  (Celery workers)
     │  LangGraph    │ │  LangGraph  │ │  LangGraph   │
     └──────────────┘ └────────────┘ └──────────────┘
```

**Key changes:**
- **Async job queue**: API returns claim ID immediately, processing happens in background workers.
- **Celery + RabbitMQ**: Distribute claim processing across N workers.
- **Kubernetes**: Auto-scale workers based on queue depth.
- **LLM API management**: Separate rate limiters per API key, automatic key rotation.
- **Estimated throughput**: 50-100 concurrent workers × 6 claims/hour/worker = 300-600 claims/hour = 2.6M-5.2M claims/year.

---

## 2. Database Layer

### Schema Design

```sql
-- Core tables
CREATE TABLE members (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    policy_id VARCHAR(30) REFERENCES policies(id),
    join_date DATE NOT NULL,
    plan_type VARCHAR(20) DEFAULT 'INDIVIDUAL',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE policies (
    id VARCHAR(30) PRIMARY KEY,
    holder_name VARCHAR(100),
    status VARCHAR(10) DEFAULT 'ACTIVE',
    validity_start DATE NOT NULL,
    validity_end DATE NOT NULL,
    terms JSONB NOT NULL,  -- Full policy_terms.json
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE claims (
    id VARCHAR(20) PRIMARY KEY,
    member_id VARCHAR(20) REFERENCES members(id),
    policy_id VARCHAR(30) REFERENCES policies(id),
    category VARCHAR(30) NOT NULL,
    treatment_date DATE,
    hospital_name VARCHAR(100),
    claimed_amount DECIMAL(12,2) NOT NULL,
    approved_amount DECIMAL(12,2),
    decision VARCHAR(20),  -- APPROVED, PARTIAL, REJECTED, MANUAL_REVIEW
    reason TEXT,
    confidence_score DECIMAL(5,4),
    trace JSONB,  -- Full ClaimTrace as JSON
    financial_breakdown JSONB,
    rejection_reasons JSONB DEFAULT '[]',
    fraud_signals JSONB DEFAULT '[]',
    degraded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_claims_member ON claims(member_id);
CREATE INDEX idx_claims_decision ON claims(decision);
CREATE INDEX idx_claims_date ON claims(treatment_date);
CREATE INDEX idx_claims_created ON claims(created_at);

-- Partial index for pending manual reviews
CREATE INDEX idx_claims_manual_review ON claims(decision)
    WHERE decision = 'MANUAL_REVIEW';
```

### Migration Strategy
1. Add SQLAlchemy models alongside existing Pydantic models.
2. Use Alembic for schema migrations.
3. Implement `ClaimsRepository` interface (abstract class) with `InMemoryRepo` and `PostgresRepo` implementations.
4. Feature flag to switch between repositories.

---

## 3. Async Processing Pipeline

### Current → Future

```
CURRENT (Sync):
  POST /submit → [Process 3-10s] → Return result

FUTURE (Async):
  POST /submit → Return {claim_id, status: "PROCESSING"} → (background)
  GET /claims/{id}/status → Return current status + progress
  WebSocket /ws/claims/{id} → Real-time agent updates
```

### Implementation Plan
1. **Celery task**: `process_claim_async.delay(submission)` → background worker.
2. **Status endpoint**: `GET /api/v1/claims/{id}/status` returns `{status: "document_agent", progress: 0.25}`.
3. **WebSocket**: Real-time updates as each agent completes.
4. **Frontend**: Progress bar showing agent pipeline stages with live trace updates.

---

## 4. Security & Compliance

### Authentication & Authorization
```
POST /api/v1/auth/login → JWT token
Authorization: Bearer <token>

Roles:
  - MEMBER: Submit claims, view own claims
  - OPERATIONS: View all claims, approve manual reviews
  - ADMIN: Manage policies, members, system config
```

### HIPAA / IRDAI Compliance
- **Data encryption**: AES-256 at rest, TLS 1.3 in transit.
- **Audit logging**: Every access to claim data logged with user ID, timestamp, action.
- **Document storage**: Uploaded medical documents stored in encrypted S3 bucket with lifecycle policies.
- **PII masking**: Patient names, member IDs masked in logs (show only last 4 chars).
- **Data retention**: Claims data retained for 8 years per IRDAI guidelines, then archived.

### API Security
- **Rate limiting**: 100 requests/minute per user, 10 claims/hour per member.
- **Input sanitization**: File upload validation (max size, allowed types, virus scanning).
- **CORS**: Whitelist specific frontend domains only.

---

## 5. Advanced Fraud Detection

### Phase 1: Enhanced Rule Engine
- **Geographic anomaly**: Member in Mumbai, hospital in Chennai, treatment same day.
- **Provider clustering**: Track which providers are associated with suspicious claims.
- **Seasonal patterns**: Spike in specific claim types around policy renewal dates.
- **Amount rounding**: Claims consistently hitting exact round numbers (₹5000, ₹10000).

### Phase 2: ML-Based Detection
- **Training data**: Historical claims with human-labeled fraud flags.
- **Model**: Gradient Boosted Trees (XGBoost) — handles tabular data well, interpretable.
- **Features**: Member history, provider history, claim amount distribution, time patterns.
- **Hybrid approach**: ML model produces a score, rule engine adds explainable flags. Final fraud decision is always traceable.

### Phase 3: Network Analysis
- **Graph database** (Neo4j): Map relationships between members, providers, and claims.
- **Anomaly detection**: Identify clusters of members all claiming from the same provider on the same day.
- **Link analysis**: Detect collusion patterns between members and providers.

---

## 6. Document Processing Improvements

### OCR Enhancement
- **Fallback chain**: Gemini → Groq Vision → Google Cloud Vision API → Tesseract (last resort).
- **Confidence threshold**: If primary extraction confidence < 0.7, automatically retry with backup model.
- **Multi-page support**: Handle multi-page discharge summaries and itemized hospital bills.

### Document Verification
- **Digital signature validation**: Verify digitally signed prescriptions (NMC Digital Prescription format).
- **Tamper detection**: Compare document metadata (EXIF, creation date) against claim timeline.
- **Template matching**: Learn common hospital bill formats to improve extraction accuracy.

### Supported Document Types (Extended)
- Insurance cards
- Pre-authorization letters
- Discharge summaries (multi-page)
- Lab reports with reference ranges
- Pharmacy invoices with GST breakdowns

---

## 7. Observability & Monitoring

### Metrics (Prometheus + Grafana)
```
# Business metrics
claims_processed_total{decision="APPROVED"} counter
claims_processing_duration_seconds histogram
agent_execution_duration_seconds{agent="document_agent"} histogram

# LLM metrics
llm_calls_total{model="gemini-2.0-flash-lite", status="success"} counter
llm_latency_seconds{model="llama-3.3-70b-versatile"} histogram
llm_tokens_total{model="llama-3.3-70b-versatile", type="completion"} counter

# Error metrics
agent_errors_total{agent="policy_agent", error_type="timeout"} counter
degraded_claims_total counter
```

### Distributed Tracing (OpenTelemetry)
- Instrument each agent with OTEL spans.
- Trace context propagation across async boundaries.
- Export to Jaeger/Tempo for visualization.
- Correlate LLM API calls with claim processing traces.

### Alerting
- `claims_processing_duration_seconds > 30s` → P2 alert.
- `llm_calls_total{status="error"} rate > 10/min` → P1 alert.
- `degraded_claims_total rate > 5/hour` → P2 alert.

---

## 8. Multi-Tenancy & Policy Engine

### Current Limitation
The system uses a single `policy_terms.json` file. At scale, Plum manages 6,000+ companies, each with different policy configurations.

### Future Architecture
```
┌──────────────────────────────────┐
│        Policy Engine Service      │
│                                   │
│  ┌─────────────────────────────┐ │
│  │   Policy Template Library    │ │
│  │   (Base plans, riders, etc.) │ │
│  └──────────────┬──────────────┘ │
│                 │                 │
│  ┌──────────────▼──────────────┐ │
│  │   Company-Specific Overrides │ │
│  │   (Limits, exclusions, etc.) │ │
│  └──────────────┬──────────────┘ │
│                 │                 │
│  ┌──────────────▼──────────────┐ │
│  │   Compiled Policy (cached)   │ │
│  │   Per company, per plan tier  │ │
│  └─────────────────────────────┘ │
└──────────────────────────────────┘
```

- **Policy versioning**: Track changes over time, apply correct version based on claim date.
- **Rule DSL**: Domain-specific language for expressing policy rules without code changes.
- **A/B testing**: Compare old vs. new policy rule implementations on historical claims.

---

## 9. Operational Dashboard

### For Operations Team
- **Claims queue**: Filter by status (pending review, manual review, processing).
- **Bulk actions**: Approve/reject multiple manual review claims.
- **Search**: Find claims by member ID, date range, decision, hospital.
- **Analytics**: 
  - Approval rate by category, hospital, member segment.
  - Average processing time trend.
  - Fraud detection rate and false positive analysis.
  - Top rejection reasons distribution.

### For Management
- **Financial overview**: Total claimed vs. approved amounts, loss ratio.
- **SLA monitoring**: % of claims processed within 24 hours.
- **Agent performance**: Per-agent latency, error rates, degradation frequency.
- **Cost tracking**: LLM API costs per claim, total monthly spend.

---

## 10. Performance Benchmarks

### Current Baseline (Assessment)

| Metric | Value |
|---|---|
| End-to-end latency (approved claim) | 3-10s |
| End-to-end latency (blocked claim) | 200-500ms |
| DocumentAgent (with LLM) | 2-5s |
| PolicyAgent (with LLM) | 1-3s |
| FraudAgent (rules only) | ~50ms |
| DecisionAgent | ~100ms |
| Concurrent claims | 1 (single process) |

### Target Baseline (Production — Phase 1)

| Metric | Target |
|---|---|
| End-to-end latency (p95) | < 15s |
| Throughput | 500 claims/hour |
| Availability | 99.9% |
| Document extraction accuracy | > 95% |
| Decision match rate (vs human) | > 90% |
| Concurrent claims | 50 |

### Target Baseline (Production — Phase 2)

| Metric | Target |
|---|---|
| End-to-end latency (p95) | < 30s (async, user doesn't wait) |
| Throughput | 5,000 claims/hour |
| Availability | 99.95% |
| Document extraction accuracy | > 98% |
| Decision match rate (vs human) | > 95% |
| Concurrent claims | 500 |

---

## Implementation Priority Matrix

| Enhancement | Impact | Effort | Priority |
|---|---|---|---|
| PostgreSQL migration | High | Medium | P0 — Week 1 |
| Authentication/authorization | High | Medium | P0 — Week 1 |
| Async processing (Celery) | High | High | P1 — Week 2-3 |
| Enhanced fraud rules | Medium | Low | P1 — Week 2 |
| Prometheus metrics | Medium | Low | P1 — Week 2 |
| OpenTelemetry integration | Medium | Medium | P2 — Week 3-4 |
| Document fallback chain | Medium | Medium | P2 — Week 3-4 |
| ML fraud model | High | High | P3 — Month 2-3 |
| Multi-tenancy / Policy Engine | Critical | Very High | P3 — Month 3-6 |
| Operational dashboard | High | High | P3 — Month 2-4 |
| Graph-based fraud detection | Medium | Very High | P4 — Month 6+ |
