# Cortex Data Pipeline Architecture

> *Revision 1 — Founding Systems Architect*
> *For engineers building data infrastructure*

---

## 1. Overview

The data pipeline transforms raw, heterogeneous SaaS API data into a unified, queryable, machine-understandable business model. It is the foundation upon which all intelligence is built.

**Design Principles:**
1. **Fail gracefully** — never lose data. Raw data is always preserved in the data lake.
2. **Provenance everywhere** — every value knows its source tool, sync time, and confidence.
3. **Incremental by default** — full re-syncs are exceptional; incremental syncs are the norm.
4. **Schema-on-read flexibility** — normalized schemas are strict; raw storage is schema-flexible (JSONB, Parquet).

---

## 2. Pipeline Architecture

```
                         SAAS TOOLS
     ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌─────────┐
     │ Stripe  │ │ QuickBooks│ │ Calendly│ │ HubSpot  │ │ GA4     │
     └────┬────┘ └─────┬────┘ └────┬────┘ └────┬─────┘ └────┬────┘
          │            │           │           │            │
     ┌────▼────────────▼───────────▼───────────▼────────────▼────┐
     │               INTEGRATION SERVICE                         │
     │  ┌────────────┐ ┌────────────┐ ┌──────────────────────┐  │
     │  │ Merge.dev  │ │ Native     │ │ Webhook              │  │
     │  │ Connectors │ │ Connectors │ │ Receivers            │  │
     │  │ (15 tools) │ │ (5 tools)  │ │ (all tools)          │  │
     │  └─────┬──────┘ └─────┬──────┘ └──────────┬───────────┘  │
     │        │              │                    │               │
     │        └──────────────┴────────────────────┘               │
     │                         │                                  │
     │                    ┌────▼────┐                             │
     │                    │  NATS   │                             │
     │                    │  Event  │                             │
     │                    │  Bus    │                             │
     │                    └─────────┘                             │
     └──────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
     ┌───────────────────────────────────────────────────────────┐
     │                    INGESTION LAYER                        │
     │                                                           │
     │  Event → Celery Task → Daft DataFrame → Raw JSON → Parquet│
     │                                                           │
     │  ┌──────────┐   ┌──────────┐   ┌────────────────────┐   │
     │  │ Event    │──►│ Daft     │──►│ S3 (data lake)     │   │
     │  │ Router   │   │ Ingest   │   │ /raw/{tool}/{date}/ │   │
     │  └──────────┘   └──────────┘   └────────────────────┘   │
     │                    │                                      │
     │                    ▼                                      │
     │              ┌──────────┐                                 │
     │              │ Queue    │                                 │
     │              │ Normalize│                                 │
     │              │ Task     │                                 │
     │              └──────────┘                                 │
     └──────────────────────────────────────────────────────────┘
                                │
                                ▼
     ┌───────────────────────────────────────────────────────────┐
     │                    NORMALIZATION LAYER                    │
     │                                                           │
     │  Daft DataFrame → Schema Mapping → Validation            │
     │                                                           │
     │  ┌──────────────────────────────────────────────────────┐ │
     │  │  Schema Mapper per Tool Category                     │ │
     │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │ │
     │  │  │ CRM      │ │Accounting│ │ Booking /        │    │ │
     │  │  │ Mapper   │ │ Mapper   │ │ Scheduling Mapper│    │ │
     │  │  └──────────┘ └──────────┘ └──────────────────┘    │ │
     │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │ │
     │  │  │ Payment  │ │ Marketing│ │ General          │    │ │
     │  │  │ Mapper   │ │ Mapper   │ │ (fallback)       │    │ │
     │  │  └──────────┘ └──────────┘ └──────────────────┘    │ │
     │  └──────────────────────────────────────────────────────┘ │
     │                    │                                      │
     │                    ▼                                      │
     │              ┌──────────┐                                 │
     │              │ Queue    │                                 │
     │              │ Resolve  │                                 │
     │              │ Entities │                                 │
     │              └──────────┘                                 │
     └──────────────────────────────────────────────────────────┘
                                │
                                ▼
     ┌───────────────────────────────────────────────────────────┐
     │                    ENTITY RESOLUTION LAYER                │
     │                                                           │
     │  Fuzzy Matching → Canonical ID → Resolution Graph        │
     │                                                           │
     │  ┌──────────────────────────────────────────────────────┐ │
     │  │  Customer Resolution (email + name + phone + addr)  │ │
     │  │  • Exact match: email                              │ │
     │  │  • Fuzzy match: name similarity + phone overlap    │ │
     │  │  • Graph-based: A paid invoice for B's email       │ │
     │  │  • Confidence score per resolution                  │ │
     │  │                                                     │ │
     │  │  Service Resolution (name + category + price)      │ │
     │  │  Employee Resolution (name + role + email)         │ │
     │  │  Campaign Resolution (name + platform + dates)     │ │
     │  └──────────────────────────────────────────────────────┘ │
     │                    │                                      │
     │                    ▼                                      │
     │              ┌──────────┐                                 │
     │              │ Queue    │                                 │
     │              │ Store    │                                 │
     │              └──────────┘                                 │
     └──────────────────────────────────────────────────────────┘
                                │
                                ▼
     ┌───────────────────────────────────────────────────────────┐
     │                    STORAGE LAYER                          │
     │                                                           │
     │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
     │  │ PostgreSQL   │  │ pgvector     │  │ S3             │ │
     │  │ • Entities   │  │ • Embeddings │  │ • Raw Parquet  │ │
     │  │ • Graph      │  │ • Similarity │  │ • Model state  │ │
     │  │ • Metrics    │  │   Indexes    │  │ • Export cache │ │
     │  │ • Users      │  │              │  │                │ │
     │  │              │  │              │  │                │ │
     │  │ TimescaleDB  │  │              │  │                │ │
     │  │ • Time series│  │              │  │                │ │
     │  │ • Aggregates │  │              │  │                │ │
     │  └──────────────┘  └──────────────┘  └────────────────┘ │
     └──────────────────────────────────────────────────────────┘
```

---

## 3. Integration Connectors

### 3.1 Connector Strategy

**Hybrid approach: Merge.dev (15+ tools) + Native connectors (top 5)**

| Connector Type | Count | Why | Technology |
|---------------|-------|-----|-----------|
| Merge.dev unified API | 15+ tools | Rapid coverage of long tail: Xero, Salesforce, Mailchimp, Meta Ads, etc. | Merge.dev SDK (Python) |
| Native connectors | 5 tools | Full control over schema, higher sync frequency, custom fields | Custom Python with tool-specific APIs |
| Generic webhook | All | Real-time event ingestion | FastAPI endpoint + NATS |

### 3.2 Native Connectors — v1 Priority

| Tool | Why Native | API | Key Data |
|------|-----------|-----|----------|
| **Stripe** | Core financial data, highest freshness requirements | Stripe Python SDK | Charges, invoices, subscriptions, customers, refunds |
| **QuickBooks Online** | Core accounting data, complex schema | QuickBooks OAuth 2.0 + API v3 | Accounts, invoices, payments, customers, items, employees |
| **Calendly** | Core booking data, need real-time webhooks | Calendly v2 API | Events, invitees, cancellation reasons |
| **Google Analytics 4** | Marketing attribution | GA4 Data API + Google Analytics Admin API | Events, user acquisition, e-commerce metrics |
| **HubSpot** | CRM core, pipeline data | HubSpot API v3 | Contacts, deals, companies, products, engagements |

### 3.3 Merge.dev Connectors — v1

| Tool | Merge Unified Object | Key Data |
|------|---------------------|----------|
| Xero | Accounting | Invoices, accounts, tax rates |
| Square | Payments | Orders, payments, refunds |
| Mailchimp | Marketing | Campaigns, lists, members |
| Meta Ads | Marketing | Campaigns, ads, insights |
| Google Ads | Marketing | Campaigns, ad groups, keywords |
| Jane App | Ticketing (bookings map) | Appointments, patients |
| Acuity Scheduling | Ticketing (bookings map) | Appointments, client info |
| Salesforce | CRM | Accounts, contacts, opportunities |
| Zoho CRM | CRM | Accounts, contacts, deals |
| Zapier | General (catch-all) | Custom data through Zaps |

---

## 4. ETL/ELT Design

### 4.1 Strategy: ELT with In-Flight Normalization

**Why ELT, not ETL:**
- Raw data goes to S3 first (write speed critical for webhook bursts)
- Transformation is asynchronous and can be retried
- Raw data is preserved for re-processing when schemas improve
- Enables "replay from raw" if normalization logic changes

### 4.2 Pipeline Stages

#### Stage 1: Ingestion (Batch + Streaming)

**Batch sync:**
- Scheduled via Celery Beat (every 2-6 hours depending on tool)
- Paginates through API, writes raw JSON lines to S3
- File naming: `/raw/{tenant_id}/{tool}/{entity}/{date_hour}/{batch_id}.parquet`
- Uses Daft's streaming mode to handle large result sets without OOM

```python
# Pseudocode for Stripe batch sync
async def sync_stripe_invoices(tenant_id: str, sync_cursor: str) -> SyncResult:
    raw_path = f"/raw/{tenant_id}/stripe/invoice/{datetime}"

    async for batch in stripe.Invoice.list_async(limit=100, starting_after=sync_cursor):
        # Write raw to S3 immediately
        df = daft.from_pydict({"records": batch.data})
        df.write_parquet(f"{raw_path}/{uuid4()}.parquet")

        # Update cursor
        sync_cursor = batch[-1].id

        # Emit event for normalization trigger
        await nats.publish(f"data.ingested.{tenant_id}", {
            "tool": "stripe",
            "entity": "invoice",
            "count": len(batch),
            "raw_path": raw_path,
        })

    return SyncResult(ok=True, count=total, cursor=sync_cursor)
```

**Streaming (webhook):**
- Real-time: sub-second to near-real-time
- Webhook → FastAPI → validate signature → NATS event → Celery task → normalize → store
- Rate-limited per tenant to prevent DoS from buggy SaaS apps

#### Stage 2: Normalization

Each tool category has a schema mapper that converts tool-specific API responses to Cortex's unified model:

```python
# Example: Stripe Invoice → Cortex Unified Invoice
class StripeInvoiceMapper(BaseMapper):
    source_tool = "stripe"
    target_entity = "invoice"

    def map(self, raw: dict) -> NormalizedRecord:
        return NormalizedRecord(
            entity_type="invoice",
            external_id=raw["id"],
            source_tool="stripe",
            attributes={
                "amount": raw["amount_due"] / 100,  # cents → dollars
                "currency": raw["currency"],
                "status": self._map_status(raw["status"]),
                "issue_date": from_unix(raw["created"]),
                "due_date": from_unix(raw["due_date"]) if raw.get("due_date") else None,
                "paid_date": from_unix(raw["status_transitions"]["paid_at"])
                    if raw.get("status_transitions") else None,
                "line_items": [self._map_line_item(li) for li in raw.get("lines", {}).get("data", [])],
                "customer_ref": raw.get("customer"),  # will be resolved later
            },
            provenance=Provenance(
                source_tool="stripe",
                synced_at=utcnow(),
                raw_record_id=raw["id"],
                raw_path=f"/raw/{self.tenant_id}/stripe/invoice/...",
            )
        )

    def _map_status(self, stripe_status: str) -> str:
        mapping = {
            "draft": "draft",
            "open": "sent",
            "paid": "paid",
            "uncollectible": "bad_debt",
            "void": "voided",
        }
        return mapping.get(stripe_status, "unknown")
```

**Unified schema categories** (detailed in Section 6)

#### Stage 3: Entity Resolution

Entity resolution is the hardest problem in the pipeline. A customer may appear as:
- `contact@email.com` in HubSpot
- `cus_abc123` in Stripe
- `Jane Smith` in Calendly (with phone number)
- `Client #42` in QuickBooks

**Resolution algorithm:**
1. **Exact match on email** (highest confidence) — merge immediately
2. **Fuzzy match on name + phone** (Jaro-Winkler distance > 0.9) — merge with medium confidence
3. **Graph-based resolution** — if Invoice A references Customer B, and Customer B in tool X is the same as Customer C in tool Y via a shared booking... transitive resolution
4. **Manual merge** — owner can say "these are the same" from the UI

```python
class EntityResolver:
    def resolve(self, new_record: NormalizedRecord) -> ResolvedRecord:
        entity_type = new_record.entity_type  # "customer"
        candidate_resolutions = []

        # 1. Exact email match
        for email in self._extract_emails(new_record):
            match = self.db.query("SELECT canonical_id FROM entity_emails WHERE email = :email", email=email)
            if match:
                candidate_resolutions.append((match, 1.0))

        # 2. Fuzzy name + phone match
        name = new_record.attributes.get("name", "")
        phone = self._normalize_phone(new_record.attributes.get("phone", ""))
        if name and phone:
            # Use trigram similarity index
            matches = self.db.query("""
                SELECT canonical_id, similarity(name, :name) as sim
                FROM entity_names
                WHERE phone = :phone AND similarity(name, :name) > 0.85
            """, name=name, phone=phone)
            candidate_resolutions.extend([(m.canonical_id, m.sim) for m in matches])

        if candidate_resolutions:
            best = max(candidate_resolutions, key=lambda x: x[1])
            return ResolvedRecord(
                canonical_id=best[0],
                confidence=best[1],
                resolution_method="exact_email" if best[1] == 1.0 else "fuzzy_name_phone",
            )
        else:
            # New entity — generate new canonical ID
            return ResolvedRecord(
                canonical_id=generate_id(),
                confidence=1.0,
                resolution_method="new_entity",
            )
```

#### Stage 4: Metric Derivation

Once entities and relationships exist, derive higher-order metrics:

```python
class MetricDeriver:
    def derive(self, tenant_id: str, canonical_customer_id: str):
        # LTV = sum(all payments) / customer_age_in_months
        invoice_amounts = self.db.query("""
            SELECT SUM(i.amount) as total, MIN(i.issue_date) as first_invoice
            FROM invoices i
            WHERE i.customer_canonical_id = :cid
              AND i.status IN ('paid', 'sent')
        """, cid=canonical_customer_id)

        age_months = max(1, months_between(invoice_amounts.first_invoice, now()))
        ltv = invoice_amounts.total / age_months

        # Also derive: churn risk, utilization rate, booking frequency, etc.
        return {"ltv": ltv, "customer_age_months": age_months}
```

#### Stage 5: Embedding Generation

After entity resolution and metric derivation, generate vector embeddings:

```python
class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-m3")

    def generate_customer_embedding(self, customer: dict) -> list[float]:
        # Create a text representation of the customer profile
        profile_text = f"""
        Customer: {customer['name']}
        Industry: {customer.get('vertical', 'unknown')}
        LTV: ${customer['ltv']:.0f}/mo
        Tenure: {customer['tenure_months']} months
        Active Services: {', '.join(customer['services'])}
        Acquisition Channel: {customer.get('channel', 'unknown')}
        Average Invoice: ${customer['avg_invoice']:.0f}
        Payment Method: {customer.get('payment_method', 'unknown')}
        """

        return self.model.encode(profile_text, normalize_embeddings=True).tolist()
```

---

## 5. Schema Design: Unified Business Data Model

### 5.1 Core Entity Tables

```sql
-- Each tenant has its own schema (multi-tenancy via schema-per-tenant, see system-architecture.md)

-- Core entities
CREATE TABLE customers (
    canonical_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name       TEXT,
    primary_email      TEXT,
    primary_phone      TEXT,
    vertical           TEXT,                          -- auto-detected or from onboarding
    segment            TEXT,                          -- derived (high_value, at_risk, etc.)
    attributes         JSONB,                         -- flexible: any tool-specific fields
    embedding          vector(1024),                  -- BGE-M3 embedding
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE services (
    canonical_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name               TEXT,
    category           TEXT,
    default_price      NUMERIC(10,2),
    duration_minutes   INTEGER,
    cost_of_goods      NUMERIC(10,2),                 -- materials, labor
    attributes         JSONB,
    embedding          vector(1024),
    created_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE employees (
    canonical_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name               TEXT,
    role               TEXT,
    email              TEXT,
    hourly_cost        NUMERIC(10,2),
    certifications     TEXT[],                        -- array of service categories they're qualified for
    attributes         JSONB,
    embedding          vector(1024),
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- Transactional entities
CREATE TABLE invoices (
    canonical_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id        UUID REFERENCES customers(canonical_id),
    amount             NUMERIC(12,2),
    currency           TEXT DEFAULT 'USD',
    status             TEXT,                          -- draft, sent, paid, overdue, bad_debt
    issue_date         TIMESTAMPTZ,
    due_date           TIMESTAMPTZ,
    paid_date          TIMESTAMPTZ,
    line_items         JSONB,                         -- array of {service_id, amount, quantity}
    source_tool        TEXT,
    external_id        TEXT,
    created_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE bookings (
    canonical_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id        UUID REFERENCES customers(canonical_id),
    employee_id        UUID REFERENCES employees(canonical_id),
    service_id         UUID REFERENCES services(canonical_id),
    start_time         TIMESTAMPTZ,
    end_time           TIMESTAMPTZ,
    status             TEXT,                          -- scheduled, completed, no_show, cancelled
    cancellation_reason TEXT,
    source_tool        TEXT,
    external_id        TEXT,
    created_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE payments (
    canonical_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id         UUID REFERENCES invoices(canonical_id),
    amount             NUMERIC(12,2),
    payment_method     TEXT,
    status             TEXT,
    paid_at            TIMESTAMPTZ,
    source_tool        TEXT,
    external_id        TEXT,
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- Marketing entities
CREATE TABLE campaigns (
    canonical_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name               TEXT,
    platform           TEXT,                          -- google_ads, meta_ads, email, etc.
    status             TEXT,
    total_spend        NUMERIC(12,2),
    start_date         DATE,
    end_date           DATE,
    attributes         JSONB,
    created_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE campaign_metrics (
    id                 BIGSERIAL PRIMARY KEY,
    campaign_id        UUID REFERENCES campaigns(canonical_id),
    date               DATE,
    impressions        INTEGER,
    clicks             INTEGER,
    conversions        INTEGER,
    spend              NUMERIC(10,2),
    source_tool        TEXT
);
```

### 5.2 Relationship Graph

```sql
-- Typed, property-bearing edges
CREATE TABLE business_edges (
    id                 BIGSERIAL PRIMARY KEY,
    source_id          UUID NOT NULL,                 -- canonical_id of source entity
    source_type        TEXT NOT NULL,                 -- "customer", "invoice", "service", etc.
    target_id          UUID NOT NULL,
    target_type        TEXT NOT NULL,
    relationship_type  TEXT NOT NULL,                 -- "has_invoice", "performed_by", "paid_with", etc.
    properties         JSONB,                         -- edge-specific metadata
    confidence         NUMERIC(3,2) DEFAULT 1.0,     -- entity resolution confidence
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- Indexes for graph traversal
CREATE INDEX idx_edges_source ON business_edges(source_id, source_type);
CREATE INDEX idx_edges_target ON business_edges(target_id, target_type);
CREATE INDEX idx_edges_type ON business_edges(relationship_type);
```

### 5.3 Time-Series Hypertables (TimescaleDB)

```sql
-- Create hypertables for time-series metrics
SELECT create_hypertable('metric_values', 'time', chunk_time_interval => INTERVAL '1 day');

CREATE TABLE metric_values (
    time               TIMESTAMPTZ NOT NULL,
    tenant_id          TEXT NOT NULL,
    metric_name        TEXT NOT NULL,                 -- "revenue", "utilization", "no_show_rate", etc.
    entity_id          UUID,                          -- optional: which entity this metric is about
    entity_type        TEXT,                          -- "customer", "service", "employee", NULL for global
    value              NUMERIC(14,4),
    tags               JSONB                          -- additional dimensions (location, channel, etc.)
);

-- Continuous aggregates for common rollups
CREATE MATERIALIZED VIEW metric_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS bucket,
       tenant_id,
       metric_name,
       entity_id,
       entity_type,
       AVG(value) AS avg_value,
       SUM(value) AS sum_value,
       COUNT(*) AS observation_count
FROM metric_values
GROUP BY bucket, tenant_id, metric_name, entity_id, entity_type;

-- Also create daily and weekly continuous aggregates
```

### 5.4 Provenance Tracking

```sql
-- Track where each piece of data came from and when
CREATE TABLE provenance_log (
    id                 BIGSERIAL PRIMARY KEY,
    entity_type        TEXT NOT NULL,
    canonical_id       UUID NOT NULL,
    source_tool        TEXT NOT NULL,
    external_id        TEXT,
    synced_at          TIMESTAMPTZ NOT NULL,
    sync_type          TEXT,                          -- "batch" or "webhook"
    batch_id           TEXT,
    raw_path           TEXT                           -- S3 path to raw Parquet
);

-- Helps answer: "Where did this decision's data come from?"
```

### 5.5 Resolution Graph

```sql
-- Track which external IDs map to which canonical IDs
CREATE TABLE entity_resolution (
    id                 BIGSERIAL PRIMARY KEY,
    canonical_id       UUID NOT NULL,
    external_tool      TEXT NOT NULL,
    external_id        TEXT NOT NULL,
    resolution_method  TEXT,                          -- "exact_email", "fuzzy_name", "graph", "manual"
    confidence         NUMERIC(3,2),
    resolved_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE(external_tool, external_id)
);
```

---

## 6. Real-Time vs. Batch Sync

### Synchronization Strategy

| Data Type | Sync Mode | Frequency | Why |
|-----------|-----------|-----------|-----|
| Financial transactions (invoices, payments) | Webhook + Batch | Webhook: real-time, Batch: every 2h | High value, owners care about cash flow |
| Bookings & appointments | Webhook + Batch | Webhook: real-time, Batch: every 1h | Operational decisions need freshness |
| CRM records | Batch | Every 6h | Lower velocity, changes are slow |
| Marketing campaigns & metrics | Batch | Every 4h | Marketing data has inherent delay (attribution windows) |
| Analytics events (GA4) | Batch | Every 6h | Heavy data, no real-time need |
| Historical backfill | Batch | Once (on onboarding) | 2 years of history, done as background job |

### Webhook Processing

```
Webhook received → Verify signature → Deduplicate (idempotency key) → 
Publish to NATS → Celery task → Normalize → Store
```

**Idempotency:** Each webhook has an `idempotency_key` (provided by the SaaS tool or generated by us as `{tool}:{event_id}:{timestamp}`). Stored in Redis with 24h TTL. Duplicates are silently dropped.

### Batch Cursor Management

```python
class SyncCursor:
    """Manage sync cursors for incremental API pulls."""

    def __init__(self, tenant_id: str, tool: str, entity: str):
        self.key = f"sync_cursor:{tenant_id}:{tool}:{entity}"

    def get(self) -> str | None:
        return redis.get(self.key)  # Returns pagination cursor or timestamp

    def set(self, cursor: str):
        redis.set(self.key, cursor)

    # For time-based cursors (most REST APIs)
    def get_time_cursor(self) -> datetime:
        val = self.get()
        return parse_timestamp(val) if val else (utcnow() - timedelta(days=7))
```

---

## 7. Data Quality & Conflict Resolution

### 7.1 Quality Checks

Each normalization step runs quality checks:

| Check | What It Catches | Action on Failure |
|-------|----------------|-------------------|
| **Type validation** | String in numeric field, null in required field | Reject record, log to data_quality_log |
| **Range check** | Invoice amount negative, booking duration > 24h | Flag as suspicious, still include with `quality: "suspect"` tag |
| **Freshness check** | No data from a connector in > 24h | Alert monitoring agent, degrade confidence of related decisions |
| **Consistency check** | Total invoice amounts don't match Stripe balance | Log discrepancy, flag for review |
| **Duplication check** | Same external_id appears twice | Deduplicate by keeping latest (by synced_at) |

### 7.2 Data Quality Dashboard

```sql
-- Quality log table
CREATE TABLE data_quality_log (
    id                 BIGSERIAL PRIMARY KEY,
    tenant_id          TEXT NOT NULL,
    tool               TEXT NOT NULL,
    entity_type        TEXT,
    check_type         TEXT,       -- "type_validation", "range_check", etc.
    severity           TEXT,       -- "error", "warning", "info"
    message            TEXT,
    record_ref         JSONB,      -- {external_id, canonical_id} for traceability
    created_at         TIMESTAMPTZ DEFAULT now()
);
```

### 7.3 Conflict Resolution Rules

| Conflict | Rule | Example |
|----------|------|---------|
| Same field, different value from 2 tools | Trust tool priority: Accounting > Payments > CRM > Booking | Invoice amount: QuickBooks says $100, Stripe says $95. Trust QuickBooks (accounting is source of truth). |
| Same field, same tool, updated value | Keep latest (by updated_at/synced_at) | Customer name changed in HubSpot → use new name |
| Entity exists in one tool but not another | Include with `source_tool: [known_tools]`, mark as partial | Customer in Stripe but not in CRM — include, mark `has_crm_profile: false` |
| Contradictory relationships | Keep both with confidence scores | Booking says customer A, invoice says customer B for same appointment → create both edges with confidence 0.5 |

---

## 8. Storage Architecture

### 8.1 What Goes Where

| Storage | What | Why |
|---------|------|-----|
| **PostgreSQL 16** (with extensions) | Entity tables, relationship graph, users, configuration, model state, simulation state | Transactional consistency for structured business data. Single system = simple ops. |
| **TimescaleDB** (PostgreSQL extension) | Time-series metrics, continuous aggregates | Hypertables auto-partition by time, native compression (90%+ space savings on older data), continuous aggregates for fast rollups. |
| **pgvector** (PostgreSQL extension) | Entity embeddings, similarity search | HNSW index for fast ANN search. Avoids separate vector DB (Qdrant, Pinecone). |
| **S3-compatible** (MinIO/Tigris) | Raw Parquet archive, model artifacts, export cache, large simulation outputs | Cheap, durable, infinite scale. Parquet for columnar efficiency. |
| **Redis** | Cache, sync cursors, rate limit counters, session store, idempotency keys | Fast, ephemeral, perfect for transient state. |

### 8.2 Data Lifecycle

| Stage | Storage | Retention | Deletion |
|-------|---------|-----------|----------|
| Raw ingested data | S3 (Parquet) | 90 days | Automatic lifecycle policy |
| Normalized entities | PostgreSQL | As long as customer is active | On account deletion |
| Time-series raw | TimescaleDB | 90 days | Chunk dropping after 90d |
| Time-series aggregated | TimescaleDB | 2 years | Chunk dropping after 2y |
| Causal model parameters | PostgreSQL | As long as customer is active | On account deletion |
| Embedding vectors | pgvector (in Postgres) | As long as entity exists | Cascade delete with entity |
| Decision history | PostgreSQL | 2 years (for learning) | Anonymized after 2 years |
| Usage logs | PostgreSQL | 90 days | Delete after 90 days |
| User feedback | PostgreSQL | Forever (for model improvement) | Anonymized on account deletion |

### 8.3 Backups

- **PostgreSQL:** pg_dump nightly to S3. WAL streaming to replica for point-in-time recovery (7-day window).
- **S3:** Cross-region replication for critical data. Versioning enabled.
- **Recovery time objective (RTO):** 4 hours for full restore. 15 minutes for replica promotion.
- **Recovery point objective (RPO):** 5 minutes for transactional data (WAL). 24 hours for time-series aggregates (can be recomputed).

---

## 9. Pipeline Monitoring

### Key Metrics

| Metric | What It Measures | Alert Threshold |
|--------|-----------------|-----------------|
| `data.ingestion.lag_seconds` | Time from data creation in source tool to ingestion | > 300s (5 min) |
| `data.normalization.failure_rate` | % of records failing normalization | > 1% |
| `data.entity_resolution.confidence` | Average confidence of entity resolutions | < 0.85 |
| `data.connector.health` | Integration up/down status | Any "down" > 15 min |
| `data.stale_cursors` | Connectors not synced in > 24h | Any |
| `data.volume.records_per_hour` | Unexpected drops or spikes in data volume | ± 50% from 7-day average |

### Pipeline Retry Strategy

- **Transient failures** (rate limit, network timeout): Retry with exponential backoff (3 attempts, 2x backoff starting at 30s)
- **Auth failures** (token expired): Immediately trigger OAuth refresh, retry once
- **Schema errors** (API returned unexpected structure): Bypass normalization, store raw, alert engineering
- **Hard failures** (tool permanently down, API removed): Set integration status to "error", notify owner