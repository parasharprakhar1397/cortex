# Cortex Security & Compliance

> *Revision 1 — Founding Systems Architect*
> *Designing for trust from day 1. Security is not a v2 feature.*

---

## 1. Security Design Principles

1. **Least privilege** — every service, agent, and user gets the minimum access needed. Nothing more.
2. **Defense in depth** — if one layer fails, others contain the breach.
3. **Privacy by design** — customer data is never visible across tenants. Never.
4. **Assume compromise** — design for the case where credentials leak, bugs exist, or insiders go rogue.
5. **Audit everything** — every access to customer data is logged, traceable, and reviewable.

---

## 2. Data Protection Architecture

### 2.1 Encryption at Rest

| Layer | Encryption Standard | Key Management |
|-------|--------------------|----------------|
| **PostgreSQL volumes** | AES-256 (cloud provider level) | Cloud KMS (AWS KMS / GCP Cloud KMS) |
| **Application-level PII fields** | AES-256-GCM via Fernet | Application key in Vault, rotated every 90 days |
| **OAuth tokens** (native connectors) | AES-256-GCM via Fernet | Separate encryption key from data encryption key |
| **S3/MinIO objects** | AES-256 (SSE-S3 or SSE-KMS) | Automatic with bucket policy |
| **Backups** | AES-256 | Same key as database encryption |
| **LLM model weights** | Plaintext (inside secure enclave) | Access restricted to inference servers only |
| **Redis cache** | AES-256 (Redis Enterprise or Elasticache) | Managed KMS |

### 2.2 Application-Level Encryption

PII and credentials get an additional encryption layer beyond volume-level encryption:

```python
from cryptography.fernet import Fernet

class FieldEncryptor:
    """Encrypts sensitive fields before storing in PostgreSQL.
    
    Used for:
    - Customer names, emails, phones (if stored separately from core entity)
    - OAuth tokens
    - Any custom field flagged as PII
    """

    def __init__(self):
        key = vault.get_secret("cortex/field-encryption-key-v2")
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

### 2.3 Encryption in Transit

| Channel | Protocol | Cipher | Certificate |
|---------|----------|--------|-------------|
| End-user ↔ API | TLS 1.3 | TLS_AES_256_GCM_SHA384 | Let's Encrypt (auto-renewed) |
| Service ↔ Service (internal) | mTLS | Same as above | Internal CA (Vault PKI) |
| Agent ↔ LLM (local) | Unix socket | No encryption (local IPC) | N/A |
| Merge.dev ↔ Cortex | TLS 1.3 | Standard | Merge.dev certs |
| OpenAI API fallback | TLS 1.3 | Standard | OpenAI certs |
| Database connections | PostgreSQL SSL | AES-256 | Internal CA |

---

## 3. Access Control Model

### 3.1 Tenant Isolation

**v1 (0-50 customers): Schema-per-tenant**
```
postgres/
  ├── public/           # Shared: integration configs, feature flags, billing
  ├── tenant_abc123/    # All business data, entity graph, time series
  ├── tenant_def456/
  └── ...
```

Each tenant schema has its own tables. A tenant can never query another tenant's schema because:
1. The API gateway enforces `X-Cortex-Tenant-ID` from JWT
2. Database sessions use `SET search_path TO tenant_<id>` 
3. Alembic migrations iterate across schemas, never cross-contaminate

**v2 (50+ customers): Hybrid** — active tenants stay schema-per-tenant, small/inactive tenants share a "pool" schema with `tenant_id` row-level filter.

### 3.2 RBAC Within Tenant

| Role | Permissions | Who Gets It |
|------|-------------|-------------|
| **Owner** | Full access: connect/disconnect integrations, view all data, implement decisions, manage team members | Business owner (signup) |
| **Manager** | View all data, run simulations, see decisions, CANNOT connect/disconnect integrations or manage team | Office manager, practice manager |
| **Viewer** | Read-only dashboard and decisions. No simulation, no settings. | External accountant, consultant |
| **API** (service account) | Programmatic access to specific endpoints (decisions, metrics) | Future: embedded Cortex partners |

### 3.3 Authentication & Authorization Flow

```
Browser ──► Clerk (auth provider)
  │                  │
  │  1. Sign in     │  Clerk handles: OAuth (Google/Microsoft),
  │  (OAuth/Email)  │  MFA, passwordless, session management
  │                  │
  ▼                  ▼
Cortex API Gateway ──► JWT Validation
  │                  │
  │  2. Validates   │  Clerk JWT verified via JWKS endpoint
  │  JWT signature  │  Extracts: user_id, tenant_id, role
  │                  │
  ▼                  ▼
FastAPI Middleware ──► Policy Enforcement
  │                  │
  │  3. Enforces    │  Checks: X-Cortex-Tenant-ID matches JWT claim
  │  tenant scope   │  Role allowed for this endpoint?
  │  + role         │  Rate limit check (per tenant, per endpoint)
  │                  │
  ▼
Route Handler
  │  Session has: tenant_id, role, user_email
```

### 3.4 API Key Management

For programmatic access (future embed/API use case):
- Keys are generated as `cortex_<base64_urlsafe(32 bytes)>`
- Stored as bcrypt hash (never plaintext)
- Scoped to specific API operations (read-only decisions, for example)
- Revocable by owner at any time
- Expiration: optional (max 1 year)

---

## 4. PII Handling & Data Minimization

### 4.1 What Constitutes PII

Cortex classifies the following as PII:

| Data Element | PII Level | Collection Minimization | Retention |
|-------------|-----------|----------------------|-----------|
| Customer name | Sensitive | Required for entity resolution | Duration of customer relationship |
| Customer email | Sensitive | Required for entity resolution & communication | Duration of customer relationship |
| Customer phone | Sensitive | Required for entity resolution (many SMB tools use phone as key) | Duration of customer relationship |
| Customer address | Sensitive | Only if needed for territory analysis | Duration of customer relationship |
| Employee name | Sensitive | Required for staffing/utilization analysis | Duration of employment + 30 days |
| Employee email | Sensitive | Required for scheduling | Duration of employment + 30 days |
| Business name | Business identity | Required | Forever |
| Business address | Business identity | Required for location-based analysis | Forever |
| Financial amounts | Non-PII | Required for analysis | Max 2 years |
| Booking times | Non-PII | Required for analysis | Max 2 years |
| Service descriptions | Non-PII | Required for analysis | Max 2 years |

### 4.2 Data Minimization Practices

1. **We don't ask for what we don't need** — no SSN, no DOB, no government ID, no health records
2. **We filter at ingestion** — raw data is examined and only relevant fields are normalized and stored
3. **We aggregate for learning** — cross-customer learning uses only anonymized, aggregated statistics
4. **We prune aggressively** — old raw data deleted after 90 days; time-series raw after 90 days
5. **We never sell data** — it's in our terms of service, our privacy policy, and our culture

### 4.3 Data Deletion on Account Termination

```
Owner requests deletion ──►
  1. Drop tenant PostgreSQL schema (all entity data, time series, decisions)
  2. Delete S3 prefix (raw data, exports, model artifacts)
  3. Delete Redis keys matching tenant_id pattern
  4. Run anonymization on decision history (extract non-identifiable patterns)
  5. Log deletion in audit trail:
     - tenant_id (hashed)
     - deletion_timestamp
     - data_categories_deleted
     - operator (owner or admin)
  6. Confirm deletion to owner
  7. Anonymized pattern data survives (no reverse mapping possible)
```

---

## 5. SOC 2 Path & Timeline

### 5.1 SOC 2 Type II — Target: Month 18

**Why SOC 2 matters:**
- Required for $10M+ SMBs who have compliance requirements
- Enterprise customers (and their CFOs) demand it
- Opens channel partnerships (SaaS platforms require SOC 2)
- Differentiator vs. competitors without it

### 5.2 Readiness Timeline

| Phase | Timeline | Activities | Cost |
|-------|----------|-----------|------|
| **Pre-work** | Months 0-6 | Implement security controls (this document), encryption, access control, logging | $0 (engineering time) |
| **Gap analysis** | Month 12 | Hire SOC 2 consultant (1 week engagement) to assess current state vs. SOC 2 criteria | $5K |
| **Remediation** | Months 12-15 | Fix gaps: formalize policies, add missing controls, implement vendor management | $10-15K (engineering time) |
| **Audit (Type I)** | Month 15 | Point-in-time audit. Takes ~2 weeks. | $15-20K |
| **Audit (Type II)** | Months 15-18 | 3-month observation period. Continuous evidence collection. | $20-25K |
| **Certification** | Month 18 | SOC 2 Type II report issued. | Complete |

### 5.3 SOC 2 Trust Services Criteria Coverage

| Criterion | Our Controls |
|-----------|-------------|
| **Security** | Encryption at rest/transit, access control, audit logging, intrusion detection, vulnerability management |
| **Availability** | Multi-AZ deployment, backup/restore, incident response, uptime monitoring (99.9% SLA target) |
| **Processing Integrity** | Pipeline monitoring, data quality checks, anomaly detection on data pipelines |
| **Confidentiality** | Tenant isolation, PII encryption, data classification, access reviews |
| **Privacy** | Data minimization, retention/deletion policies, consent management, privacy notice |

---

## 6. GDPR & CCPA Compliance

### 6.1 GDPR (EU Customers — Required for International Expansion)

| Requirement | Our Approach | Implementation |
|-------------|-------------|----------------|
| **Right to be informed** | Privacy notice at signup | In-app + email upon first data collection |
| **Right of access** | Export all data about a subject | API endpoint: `GET /api/v1/privacy/subject-data` |
| **Right to rectification** | Edit entity data | UI: owner can edit customer/employee data |
| **Right to erasure** | Full account deletion + data purge | Automated deletion pipeline |
| **Right to restrict processing** | Pause analysis while preserving data | Feature flag per tenant |
| **Data portability** | Export in JSON/CSV | API endpoint + UI download button |
| **Right to object** | Opt out of specific analysis types | Preference settings per decision type |
| **Automated decision-making** | Right to human review | Every decision card has "appeal" button → founder reviews |

### 6.2 Data Processing Agreement (DPA)

We maintain a DPA with all subprocessors:

| Subprocessor | Service | DPA in Place? | Data Location |
|-------------|---------|---------------|---------------|
| Clerk | Authentication | Yes (SOC 2) | US + EU option |
| Merge.dev | Integration iPaaS | Yes (SOC 2) | US |
| OpenAI | LLM fallback | Yes (zero-retention) | US (no training) |
| Modal Labs / Vast.ai | GPU compute | Yes | US |
| DigitalOcean / GCP | Cloud infrastructure | Yes | US initially |

### 6.3 CCPA (US Customers in California)

- **Right to know:** Same as GDPR right of access
- **Right to delete:** Same deletion pipeline
- **Right to opt out of sale:** We do not sell data. Statement in privacy policy.
- **Non-discrimination:** No price increase for exercising CCPA rights

---

## 7. Integration Security

### 7.1 OAuth Token Management

**For Merge.dev connectors:** Merge.dev manages token lifecycle. We store only a `linked_account_id` reference. Tokens never enter our infrastructure.

**For native connectors:**

```python
class CredentialStore:
    """Securely stores and manages OAuth credentials for native connectors."""

    # Credentials table is:
    # - Separate from main business data
    # - Accessible only by integration-service (not api, not agents)
    # - Encrypted at rest (AES-256-GCM via Fernet)
    # - No SELECT access from application-level accounts

    def get_credentials(self, tenant_id: str, tool: str) -> Credentials:
        """Fetch credentials with automatic refresh and logging."""
        # 1. Fetch from credentials table (encrypted)
        # 2. Decrypt in memory only
        # 3. Check expiry, auto-refresh if needed
        # 4. Log access (who, when, why)
        # 5. Return decrypted token (memory only, never logged)

    def audit_access(self, tenant_id: str, tool: str, action: str):
        """Log all credential access for audit trail."""
```

### 7.2 Webhook Security

All incoming webhooks are:
1. **Signature-verified** — each SaaS tool signs webhooks with a shared secret; we verify before processing
2. **Idempotency-checked** — duplicate webhooks are silently dropped (Redis idempotency keys with 24h TTL)
3. **Rate-limited** — per tenant, per tool. Prevents DoS from buggy SaaS apps.
4. **Logged** — all webhook receipts logged with tool, event type, timestamp, processing result

### 7.3 Credential Rotation Policy

| Credential Type | Rotation Cadence | Rotation Method |
|----------------|-----------------|-----------------|
| OAuth tokens (native) | Auto-refreshed on expiry | OAuth refresh flow (automatic) |
| API signing secrets | Every 90 days | Manual rotation via tool admin UI |
| Database passwords | Every 90 days | Rotate via cloud provider + update in Vault |
| Encryption keys (Fernet) | Every 90 days | Key rotation with re-encryption of existing data |
| Merge.dev API key | Every 180 days | Regenerate in Merge.dev dashboard |
| Clerk JWT signing key | Managed by Clerk | Automatic |

---

## 8. Incident Response Plan

### 8.1 Incident Severity Levels

| Level | Definition | Examples | Response Time |
|-------|-----------|----------|---------------|
| **SEV-1** | Data breach or active data loss. Customer data exposed to unauthorized party. | Database compromised, tenant isolation broken, credentials leaked | < 15 min |
| **SEV-2** | Service outage or data corruption. Some customers affected. | Pipeline down > 1 hour, incorrect data written, LLM hallucination producing harmful recs | < 30 min |
| **SEV-3** | Partial degradation. Minor impact. | Integration sync stale, dashboard slow, one agent type failing | < 2 hours |
| **SEV-4** | Cosmetic or non-urgent. | UI bug, typo in decision text, slow simulation | < 24 hours |

### 8.2 Incident Response Process

```
DETECTION
  • Automated: Sentry error monitoring, Grafana alerts, pipeline failure alerts
  • Manual: Customer support ticket, Slack report, engineer observation
  │
  ▼
TRIAGE (within severity SLA)
  • On-call engineer acknowledges (PagerDuty)
  • Assess: Is data exposed? Is the system compromised? Which customers affected?
  • Assign severity level
  • Open incident channel in Slack (#incidents)
  │
  ▼
CONTAINMENT
  • For SEV-1: Rotate credentials, block suspicious IPs, isolate affected component
  • For SEV-2: Roll back deployment, failover to replica, disable affected feature
  • Document containment actions in incident log
  │
  ▼
ERADICATION
  • Identify root cause
  • Fix vulnerability, deploy patch
  • Verify fix with automated tests
  │
  ▼
RECOVERY
  • Restore from backup if needed
  • Verify data integrity
  • Confirm with affected customers
  │
  ▼
POST-MORTEM (within 72 hours)
  • Write incident report: timeline, root cause, impact, remediation, prevention
  • Share with team (and customers if SEV-1/2)
  • Add action items to engineering backlog
  • Update runbooks
```

### 8.3 Key Contacts

| Role | Contact Method | Backups |
|------|---------------|---------|
| Security lead | Founder (first 6 months) | Engineer #2 |
| On-call engineer | PagerDuty (after engineer #2 hired) | Rotating schedule |
| Legal counsel | External retainer ($500/mo for incident response) | — |
| Customer communication | Founder → CS team (after hired) | Email template library |

---

## 9. Third-Party Risk Management

### 9.1 Subprocessor Risk Assessment

| Vendor | Risk Level | Audit Evidence | Contractual Protections |
|--------|-----------|---------------|----------------------|
| **Merge.dev** | Medium | SOC 2 Type II, pentest results shared | DPA, SLA, data deletion rights |
| **OpenAI** (API fallback) | Low | SOC 2 Type II, no-training API option | DPA, zero-data-retention policy |
| **Clerk** | Low | SOC 2, penetration tests | DPA, EU-US data framework |
| **DigitalOcean / GCP** | Medium | SOC 2/3, FedRAMP (GCP) | DPA, CISO contact available |
| **Modal Labs** (GPU) | Medium | SOC 2 (pending, 2026) | DPA, encryption at rest |
| **Sentry** | Low | SOC 2 | DPA, data minimization (no PII in logs) |
| **Grafana Cloud** | Low | SOC 2 | DPA, metric-only (no PII) |

### 9.2 Vendor Security Requirements

All third-party vendors with access to customer data must:
1. Have current SOC 2 Type II report (or equivalent)
2. Sign a DPA
3. Support encryption at rest and in transit
4. Provide data deletion on request
5. Notify within 72 hours of security incident affecting our data
6. Allow us to audit their controls (or share recent audit results)

### 9.3 Merge.dev Specific Risk

Merge.dev is the highest-risk dependency because it mediates access to customer tool data:

| Risk | Mitigation |
|------|------------|
| Merge.dev outage | Native connectors keep working. Degraded experience (fewer integrations). Decision cards note "some data stale." |
| Merge.dev data breach | We store only `linked_account_id`, not credentials. Impact limited to our data flowing through Merge's API. |
| Merge.dev changes pricing | At 500+ customers, evaluate building native connectors for top 10 tools (breakeven analysis). |
| Merge.dev deprecates connector | Fall back to generic webhook or build native connector (2-4 weeks effort for a single tool). |

---

## 10. Penetration Testing Cadence

| Phase | Type | Scope | Frequency | Who Does It |
|-------|------|-------|-----------|-------------|
| Pre-launch (month 1-4) | Internal security review | Code review, dependency scan, OWASP Top 10 check | Once | Founder (using automated tools: Semgrep, Bandit, npm audit) |
| Pre-pilot (month 8) | External pentest | Full application: API, web UI, auth, data pipelines | Once | External firm ($10-15K) |
| Post-launch | Automated scanning | Weekly dependency scan, daily SAST | Continuous | GitHub Dependabot + Semgrep in CI |
| Quarterly | External pentest | Full scope, focused on new features | Every 3 months | External firm ($5K/quarter retainer) |
| Annual | Red team exercise | Full scope, social engineering included | Yearly | External firm ($20K) |
| After significant change | Targeted pentest | Changed components only | Per change | External firm (hourly) |

### Vulnerability Disclosure Program

- `security@cortex.dev` — monitored within 4 hours
- 90-day disclosure timeline standard
- Bug bounty: TBD (start with thank-you + swag; move to paid bounties at $1M ARR)

---

## 11. Compliance Checklist Summary

| Requirement | Status (v1 launch) | Target Certification Date |
|-------------|-------------------|--------------------------|
| Encryption at rest (AES-256) | ✅ Implemented | — |
| Encryption in transit (TLS 1.3) | ✅ Implemented | — |
| Tenant isolation (schema-per-tenant) | ✅ Implemented | — |
| RBAC (Owner/Manager/Viewer) | ✅ Implemented | — |
| Audit logging (all data access) | ✅ Implemented | — |
| Data deletion pipeline | ✅ Implemented | — |
| SOC 2 Type I | ❌ Not started | Month 15 |
| SOC 2 Type II | ❌ Not started | Month 18 |
| GDPR readiness | ⚠️ Basic controls in place | Month 18 (before EU expansion) |
| CCPA readiness | ⚠️ Basic controls in place | Month 12 |
| HIPAA readiness | ❌ Not planned until medical vertical | Month 24+ |
| Penetration testing | ⚠️ Internal only | Month 8 (first external) |
| Vendor risk program | ⚠️ Basic assessment done | Continuous |
| Incident response plan | ❌ Written but not tested | Month 4 (tabletop exercise) |

---