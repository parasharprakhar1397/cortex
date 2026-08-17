# Cortex System Architecture

> *Revision 1 — Founding Systems Architect*
> *For the engineering team building Cortex*

---

## 1. High-Level System Diagram

```
                            ┌──────────────────────────────────────────┐
                            │              PUBLIC INTERNET            │
                            ├────────────────────┬─────────────────────┤
                            │ SMB Owner Browser  │  Partner Embed via  │
                            │ (React SPA)        │  iframe / API       │
                            └────────┬───────────┴──────────┬──────────┘
                                     │                      │
                                     │ HTTPS (TLS 1.3)      │ HTTPS
                                     ▼                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        PUBLIC API GATEWAY                                 │
│                    FastAPI + Nginx (auth, rate-limit, TLS termination)   │
└──────────────────────────────────────────────────────────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   WEB UI SERVICE    │  │  PUBLIC API (REST)  │  │  WEBHOOK RECEIVER   │
│   TanStack Start    │  │  FastAPI + Pydantic │  │  FastAPI (async)    │
│   Port 3000         │  │  /api/v1/*          │  │  /webhooks/*        │
└─────────────────────┘  └──────────┬──────────┘  └──────────┬──────────┘
                                     │                      │
                                     │ Internal gRPC        │ Events
                                     ▼                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     INTERNAL SERVICE MESH                               │
│           (Docker Compose → k8s, NATS for async messaging)              │
└──────────────────────────────────────────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────┐
         │                           │                       │
         ▼                           ▼                       ▼
┌─────────────────┐  ┌──────────────────────────┐  ┌─────────────────────┐
│ INTEGRATION      │  │     DATA PIPELINE         │  │   AGENT SYSTEM      │
│ SERVICE          │  │                           │  │                     │
│                  │  │  ┌───────────────────┐   │  │  ┌───────────────┐  │
│ ┌──────────────┐ │  │  │ Ingestion Worker │   │  │  │ Supervisor    │  │
│ │ Connector    │ │  │  │ (Daft + Celery)  │   │  │  │ Agent         │  │
│ │ Manager      │◄─┼──┼──┤                  │   │  │  │ (LangGraph)  │  │
│ │ (Merge.dev)  │ │  │  │ • Normalize      │   │  │  └───────┬───────┘  │
│ └──────┬───────┘ │  │  │ • Entity Resolve  │   │  │          │         │
│        │         │  │  │ • Validate        │   │  │          │         │
│ ┌──────┴───────┐ │  │  └────────┬──────────┘   │  │  ┌───────┴───────┐  │
│ │ Native       │ │  │           │               │  │  │ Analysis     │  │
│ │ Connectors   │ │  │  ┌────────▼──────────┐   │  │  │ Agent        │  │
│ │ (top 5)      │ │  │  │ Business State    │   │  │  └───────────────┘  │
│ └──────────────┘ │  │  │ Store (Postgres)  │   │  │  ┌───────────────┐  │
│                  │  │  │ • Entity graph    │   │  │  │ Decision      │  │
│ ┌──────────────┐ │  │  │ • Time series     │   │  │  │ Agent         │  │
│ │ Webhook      │ │  │  │ • Metric defs     │   │  │  └───────────────┘  │
│ │ Handler      │◄─┼──┼──┤ • Customer model │   │  │  ┌───────────────┐  │
│ └──────────────┘ │  │  └───────────────────┘   │  │  │ Simulation    │  │
└─────────────────┘  │                           │  │  │ Agent         │  │
                     │  ┌───────────────────┐   │  │  └───────────────┘  │
                     │  │ Vector Store      │   │  │  ┌───────────────┐  │
                     │  │ (pgvector)        │   │  │  │ Monitoring    │  │
                     │  │ • Embeddings      │   │  │  │ Agent         │  │
                     │  │ • Semantic search │   │  │  └───────────────┘  │
                     │  └───────────────────┘   │  └─────────────────────┘
                     │                           │
                     │  ┌───────────────────┐   │
                     │  │ Object Store      │   │
                     │  │ (S3/MinIO)        │   │
                     │  │ • Raw data lake   │   │
                     │  │ • Model artifacts │   │
                     │  │ • Sim. results    │   │
                     │  └───────────────────┘   │
                     └──────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Redis    │  │ Celery   │  │ NATS     │  │ Grafana  │  │ Sentry   │ │
│  │ Cache +  │  │ Task     │  │ Event    │  │ Metrics  │  │ Error    │ │
│  │ Queue    │  │ Workers  │  │ Bus      │  │ + Loki   │  │ Tracking │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### 2.1 API Gateway & Public Surface

**Technology:** Nginx → FastAPI (Python 3.12+)

**Responsibilities:**
- TLS termination, rate limiting (Redis-backed token bucket)
- Auth verification via Clerk JWTs
- Request routing to internal services
- Webhook ingress from SaaS platforms

**Design choices:**
- FastAPI over Django REST: async-native, Pydantic validation built-in, automatic OpenAPI docs. For a small team, this is dramatically faster to iterate.
- Nginx in front: handles static files, buffers slow clients, provides clean error pages during deploys.

### 2.2 Web UI Service

**Technology:** TanStack Start (React + Vite + Tailwind)

**Why:** Consistent with team's existing toolchain. Server functions enable seamless server-side data loading without a separate BFF layer.

**Key pages:** Dashboard, Decision Cards (list + detail), Simulation UI, Integration Settings, Business Profile

### 2.3 Integration Service

**Technology:** FastAPI microservice + Merge.dev SDK + native connector workers

**Responsibilities:**
- Orchestrates all external data connections
- Manages OAuth token lifecycle (refresh, rotation, revocation)
- Routes webhooks to the data pipeline
- Health-checks all integrations every 15 minutes
- Reports integration status to the parent API

**Design choice: Merge.dev in v1**
- 20+ pre-built connectors with unified schemas (accounting, CRM, ticketing, HRIS, etc.)
- Unified OAuth management (we don't store credentials — Merge does)
- Handles rate limiting, pagination, and schema drift
- Cost: ~$0.15 per connected account per month at scale
- Trade-off: we give up some control over schema granularity. Mitigation: we overlay our own normalization on top of Merge's unified objects.

**Native connectors (top 5 for v1):** Stripe, Calendly, QuickBooks, Google Analytics 4, HubSpot
These get native workers so we can pull data at higher frequency and with custom fields Merge may not expose.

### 2.4 Data Pipeline

**Technology:** Daft (DataFrames) + Celery workers

**Why Daft over Spark/Polars/vanilla Pandas:**
- Rust-powered: handles 10M+ records on a single machine
- Streaming mode: processes data as it arrives, doesn't need full dataset in memory
- Native cloud storage support (S3, GCS)
- Column pruning and predicate pushdown for efficiency
- Unified batch and streaming API

**Pipeline stages (see `data-pipelines.md` for detail):**
1. **Ingest:** Pull raw data from integration service or webhook
2. **Normalize:** Map to unified schema (business entity model)
3. **Entity Resolve:** Match identities across data sources (customer "Jane Smith" in CRM = "jsmith@email.com" in Stripe)
4. **Validate:** Type checks, range checks, freshness checks
5. **Store:** Write to Postgres (structured), pgvector (embeddings), S3 (raw parquet)

### 2.5 Business State Store

**Technology:** PostgreSQL 16 with pgvector and TimescaleDB extensions

**Why not a separate vector DB or time-series DB?**
- Operational simplicity: one database system to manage, backup, and monitor
- pgvector gives us HNSW-indexed vector search natively
- TimescaleDB gives hypertables + continuous aggregates for time series
- Transactional consistency across entities, vectors, and time series
- A small team can't afford to operate 3 databases

**What's stored here:**
- **Entity graph:** businesses, customers, services, employees, invoices, campaigns — with typed relationships
- **Time series:** revenue by hour, utilization by day, churn by week, any metric over time
- **Embeddings:** vector representations of business entities, decisions, customer personas
- **Business models:** per-customer calibration parameters, causal graphs, simulation state
- **User data:** preferences, feedback history, alert configurations

### 2.6 Agent System

**Technology:** LangGraph (graph-based agent orchestration) + custom supervisor loop

**Why LangGraph:**
- First-class support for cyclic graphs (agents can loop, reflect, retry)
- Built-in state management with configurable persistence (Postgres-backed)
- Thread-level isolation per customer (critical for multi-tenancy)
- Streaming of intermediate steps (so UI can show "thinking...")

**Agent roles** (detailed in `agents.md`):
1. **Supervisor Agent** — orchestrates, decides which agent handles what, manages context window
2. **Analysis Agent** — queries the business model, detects patterns, runs statistical tests
3. **Decision Agent** — generates recommendations from patterns, estimates ROI
4. **Simulation Agent** — runs "what-if" scenarios against the business model
5. **Monitoring Agent** — watches for anomalies, triggers alerts, checks data freshness

### 2.7 Object Store

**Technology:** S3-compatible (MinIO for self-hosted, Tigris for managed)

**Contents:**
- Raw Parquet files from data ingestion (data lake)
- Model weights/checkpoints (if we fine-tune)
- Simulation run outputs (large result sets)
- Exported reports

---

## 3. Data Flow: Raw SaaS Data → Business Model → Decisions

```
Phase 1: RAW DATA
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Stripe  │  │ QB      │  │ Calendly│
│ Invoices│  │ Ledger  │  │ Events  │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     ▼            ▼            ▼
┌─────────────────────────────────────┐
│      INGESTION (Daft + Celery)      │
│  • Pull via API or receive webhook  │
│  • Write raw JSON → S3 (data lake)  │
│  • Queue normalization task         │
└──────────────────┬──────────────────┘
                   │
                   ▼
Phase 2: NORMALIZED ENTITIES
┌─────────────────────────────────────┐
│      NORMALIZATION LAYER            │
│  • Map to unified schema           │
│  • Type coercions, unit conversions │
│  • Tag source provenance           │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      ENTITY RESOLUTION              │
│  • Match: fuzzy join on email, name,│
│    phone across all sources         │
│  • Generate: canonical_entity_id    │
│  • Store: resolution graph          │
└──────────────────┬──────────────────┘
                   │
                   ▼
Phase 3: BUSINESS MODEL
┌─────────────────────────────────────┐
│      ENTITY GRAPH ASSEMBLY          │
│  • Build relationship links         │
│    Customer ← Invoice ← Payment     │
│    Employee ← Service ← Booking     │
│  • Derive metrics from graph        │
│    (LTV, CAC, utilization, etc.)   │
│  • Generate embeddings for each     │
│    entity (BGE-M3)                  │
│  • Store in Postgres + pgvector     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      TIME SERIES DERIVATION         │
│  • Roll up metrics into timescale   │
│    hypertables (15min/1h/1d/1w)    │
│  • Continuous aggregates for speed  │
│  • Anomaly baseline computation     │
└──────────────────┬──────────────────┘
                   │
                   ▼
Phase 4: ANALYSIS (Agent Layer)
┌─────────────────────────────────────┐
│      PATTERN DETECTION              │
│  • Statistical tests on time series │
│  • Correlation analysis             │
│  • Causal inference (see AI arch)   │
│  • Benchmark vs. anonymized peers   │
└──────────────────┬──────────────────┘
                   │
                   ▼
Phase 5: DECISIONS
┌─────────────────────────────────────┐
│      DECISION GENERATION            │
│  • Rank findings by projected ROI   │
│  • Generate natural language        │
│    explanation with evidence        │
│  • Create simulation if requested   │
│  • Push to queue for delivery       │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      DELIVERY                       │
│  • Update dashboard in real-time    │
│  • Push notification (webpush/Slack)│
│  • Add to morning digest queue      │
│  • Log for feedback tracking        │
└─────────────────────────────────────┘
```

---

## 4. Multi-Tenancy Design

### Isolation Model: Schema-per-Tenant (v1) → Hybrid (v2)

**v1 (first 50 customers): Schema-per-tenant**
```
postgres/
  ├── public/          # shared: integration configs, feature flags
  ├── tenant_abc123/   # all business data, entity graph, time series
  ├── tenant_def456/
  └── ...
```

- **Why:** Absolute data isolation. One tenant can't accidentally impact another. Dropping a tenant = dropping one schema. Simple backup/restore per customer.
- **Trade-off:** Schema migration requires iterating across all schemas. Mitigation: use Alembic with `--schema` flag and a loop script.
- **Connection pooling:** Use PgBouncer with schema search path routing. Each tenant request sets `SET search_path TO tenant_abc123`.

**v2 (50-500 customers): Hybrid**
- Active tenants: schema-per-tenant (fast queries, no row-level filtering overhead)
- Small/inactive tenants: row-level tenant isolation in shared schemas (reduces connection count)
- Migration path: automated from shared→dedicated when a tenant hits activity thresholds

### Customer ID Propagation

Every request includes `X-Cortex-Tenant-ID` header (set by API gateway after JWT decode). This is threaded through:
1. HTTP requests → FastAPI middleware → route handler
2. Celery tasks → task kwargs → database session
3. Agent invocations → LangGraph thread ID → state

### Vector Store Isolation
- pgvector: tenant_id column on every vector table with BRIN index
- Agent context: separate LangGraph thread per tenant (built-in isolation)

---

## 5. Latency Requirements

| Operation | Target Latency | Freshness | Pattern | Why |
|-----------|---------------|-----------|---------|-----|
| Dashboard load | < 500ms | Real-time (cached) | Synchronous API | Owner must see data instantly |
| Decision card load | < 1s | Real-time | Synchronous API | Cards are pre-computed, just need to be fetched |
| Simulation run | < 30s | Current state | Async WebSocket | Complex computation; show progress |
| Data sync (webhook) | < 30s to reflect | Near-real-time | Event-driven | Webhook → queue → normalize → store |
| Data sync (batch) | < 2h per full sync | Stale by < 2h | Scheduled Celery | Nightly is fine for historical data |
| Agent decision cycle | < 5min per cycle | Current state | Scheduled (every 4h) | Decisions don't need sub-second freshness |
| Anomaly detection | < 1min from data arrival | Near-real-time | Streaming trigger | Fast detection prevents damage |
| Onboarding initial sync | < 30min | Historical (2yr) | Batch + progress | Owner doesn't wait; they come back |

**Key insight:** Most operations are batch or near-real-time. The only truly synchronous path is the UI reading pre-computed state. The agents, pipelines, and simulations are async. This means we can avoid expensive real-time infrastructure (Kafka, Flink) in v1.

---

## 6. API Design Philosophy

### Primary: REST over JSON

**Why REST, not GraphQL:**
- Simpler caching (HTTP caching headers, CDN-friendly)
- Better tooling maturity (every HTTP client works)
- GraphQL's flexibility is a liability here — we control the client
- Our query patterns are known: read pre-computed state, trigger actions

### API Structure

```
GET    /api/v1/decisions              # List active decision cards
GET    /api/v1/decisions/:id          # Decision detail with evidence
POST   /api/v1/decisions/:id/feedback # Submit feedback (useful/not/snooze)

GET    /api/v1/insights               # Dashboard summary metrics
GET    /api/v1/insights/:metric/timeseries  # Raw data for a metric

POST   /api/v1/simulations            # Run a simulation
GET    /api/v1/simulations/:id        # Poll for result
GET    /api/v1/simulations/:id/stream # WebSocket for live result push

GET    /api/v1/integrations           # List connected tools
POST   /api/v1/integrations/connect   # Start OAuth flow
POST   /api/v1/integrations/:id/disconnect
GET    /api/v1/integrations/:id/status

GET    /api/v1/business/profile       # Business entity data
PATCH  /api/v1/business/profile       # Update goals, vertical, etc.
```

### Event-Driven Internally

While the public API is REST, internal communication is event-driven via **NATS**:

- `data.ingested.{tenant_id}` — new data available for processing
- `data.normalized.{tenant_id}` — entity graph updated
- `analysis.completed.{tenant_id}` — new insights ready
- `anomaly.detected.{tenant_id}` — time-series anomaly found
- `integration.status.{tenant_id}.{tool}` — connection health changed

**Why NATS vs Kafka vs Redis Pub/Sub:**
- NATS: < 1ms latency, persistent (JetStream), exactly-once delivery, built-in backpressure
- Kafka: overkill for v1; operational complexity doesn't match our scale
- Redis Pub/Sub: no persistence, messages lost on restart — fine for cache invalidation but not business events

### Versioning
- URL-based versioning (`/api/v1/`): simple, unambiguous, cache-friendly
- Breaking change → new version (v2). We expect few versions given our controlled client.
- Backward-compatible additions don't require a version bump.

---

## 7. Deployment Architecture

### v1 (Monolith + Workers — first 50 customers)

```
docker-compose.yml:
  - api: FastAPI (3 replicas)
  - ui: TanStack Start (2 replicas, static served via Nginx)
  - worker: Celery (5-10 workers, auto-scaled by queue depth)
  - agent: LangGraph server (1 supervisor + workers)
  - db: PostgreSQL 16 + TimescaleDB + pgvector
  - redis: Redis 7 + Redis Stack
  - nats: NATS JetStream (3-node cluster)
  - minio: S3-compatible object storage
```

**Single VM on a $200-400/mo provider (Hetzner, Vultr, or DigitalOcean)** with Docker Compose.
Why not k8s? Too early. Small team. Simple deployment.

### v2 (Microservices — 50-500 customers)

Gradual migration to Kubernetes (managed k8s on DigitalOcean or equivalent):
- Horizontal scaling per service
- Blue/green deployments
- Canary testing for agent updates
- Helm charts for repeatable deployment

---

## 8. Observability

### Logging
- Structured JSON logs via `structlog` (Python)
- Correlation ID per request/event chain
- Logs shipped to Grafana Loki via Promtail
- Retention: 30 days hot, 90 days cold

### Metrics
- Prometheus metrics exposed at `/metrics` on each service
- Key metrics: request latency (p50/p95/p99), error rate, queue depth, agent cycle time, integration health
- Grafana dashboards for engineering + business KPIs

### Tracing
- OpenTelemetry for distributed tracing (especially important for agent chains)
- Traces sampled at 10% (100% for errors)
- Exported to Jaeger or Grafana Tempo

### Alerting
- PagerDuty for: pipeline failure, integration outage > 15min, agent loop error
- Email for: data quality warnings, decision confidence below threshold

---

## 9. Security Architecture

### Data Encryption
- TLS 1.3 for all external communication
- At-rest: AES-256 on database volumes (RDS/machine-level encryption)
- Application-level encryption for sensitive fields (API keys, PII) using Fernet

### Authentication & Authorization
- Clerk for user management (SMB owner + optional team members)
- JWT-based with short expiration (15min access tokens + 7-day refresh)
- RBAC: Owner (full) / Viewer (read-only) / Manager (read + simulate but not connect/disconnect tools)

### Integration Security
- OAuth 2.0 for all external tool connections
- No long-lived API keys stored (Merge.dev handles token management for their connected accounts)
- For native connectors: tokens encrypted at rest, stored in a separate `credentials` table with limited access
- Credentials never logged, never exposed in error messages