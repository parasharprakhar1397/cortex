# Cortex Architecture & Strategy — Master Index

> *Revision 2 — Founding Systems Architect*
> *Complete business design: architecture, strategy, go-to-market, and operations*

This index links all fourteen architecture and strategy documents for the Cortex autonomous strategic decision-support system.

---

## Documents

### Core Architecture (Existing)

| # | Document | Description |
|---|----------|-------------|
| 1 | [`product-strategy.md`](./product-strategy.md) | Product vision, user journey, decision taxonomy, competitive landscape, v1/v2/v3 roadmap |
| 2 | [`system-architecture.md`](./system-architecture.md) | High-level system design, component breakdown, data flow, multi-tenancy, API philosophy |
| 3 | [`ai-architecture.md`](./ai-architecture.md) | Intelligence system design: living business model, causal reasoning, simulation engine, ROI estimation |
| 4 | [`data-pipelines.md`](./data-pipelines.md) | Integration connectors, ETL/ELT design, entity resolution, schema design, storage architecture |
| 5 | [`agents.md`](./agents.md) | Multi-agent system: agent roles, orchestration, tool-use framework, guardrails, scheduling |
| 6 | [`memory-systems.md`](./memory-systems.md) | Memory architecture: short-term/long-term, persistence, per-customer tuning, forgetting strategy |
| 7 | [`integrations.md`](./integrations.md) | Integration strategy, priority list, credential management, rate limiting, schema mapping |

### Business & Go-to-Market Design (New)

| # | Document | Description |
|---|----------|-------------|
| 8 | [`monetization.md`](./monetization.md) | Pricing tiers, unit economics (CAC/LTV/gross margin), expansion revenue, future revenue streams, competitive pricing analysis |
| 9 | [`scaling-strategy.md`](./scaling-strategy.md) | 3→30→300 customer growth path, technical scaling (DB/k8s/GPU), operational scaling, multi-vertical expansion, internationalization, partnership strategy |
| 10 | [`security-compliance.md`](./security-compliance.md) | Encryption architecture, access control (RBAC + tenant isolation), PII handling, SOC 2 roadmap, GDPR/CCPA, incident response plan, vendor risk management |
| 11 | [`infrastructure.md`](./infrastructure.md) | Cloud provider selection, CI/CD pipeline, Docker Compose→k8s evolution, monitoring/alerting stack, disaster recovery, cost optimization, IaC (Terraform) |
| 12 | [`roadmap.md`](./roadmap.md) | Phase 0-4 timeline (24 weeks), deliverables per phase, team size, success criteria, key risks, budget, milestones |
| 13 | [`hiring-roadmap.md`](./hiring-roadmap.md) | First 5 hires (roles, timing, cost, profiles), founder transition plan, org chart evolution, equity philosophy, remote/office strategy |
| 14 | [`pitch-deck.md`](./pitch-deck.md) | 13-slide investor deck outline, problem narrative, demo flow, market sizing, business model, competitive moat, team, $1.5M ask, technical appendix |

---

## Architecture Tenets (Cross-Cutting)

These principles apply across all documents:

1. **SMBs have no data teams** — everything must auto-configure, auto-heal, and require zero SQL
2. **Proactive > Reactive** — Cortex pushes decisions before the owner asks
3. **Explainability is a first-class requirement** — every recommendation must justify itself
4. **Composability** — each component can be independently developed, tested, and scaled
5. **Cold-start problem** — the system must deliver value from day 1, even with sparse data
6. **Privacy by design** — customer data never leaks across tenants; models can be per-tenant
7. **Small team, big leverage** — use managed services and open-source building blocks; don't build infrastructure
8. **Unit economics drive architecture** — every design choice is evaluated against cost per customer at scale
9. **Security is not a v2 feature** — encryption, access control, and audit logging from day 1

---

## Quick Reference: Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Backend framework | FastAPI (Python) | Async, native Pydantic integration, excellent DX for small team |
| Database | PostgreSQL 16 + pgvector + TimescaleDB | Single database covers entities, vectors, and time series |
| Message queue | Redis + Celery | Simple, battle-tested async task system |
| Vector store | pgvector (in Postgres) | Avoids operational overhead of a separate vector DB |
| Object storage | S3-compatible (MinIO / Tigris) | Raw data lake, model artifacts, simulation outputs |
| Agent orchestration | LangGraph + custom supervisor loop | Structured agent graphs with state persistence |
| LLM inference | Self-hosted vLLM (Llama 3 70B) + OpenAI API fallback | Cost control for core reasoning; premium for complex analysis |
| Embedding model | BGE-M3 (self-hosted) | State-of-the-art multi-lingual, multi-vector embeddings |
| Data pipeline | Daft (Python DataFrame framework) | Rust-powered, streaming-capable, unified batch/stream |
| Authentication | Clerk + JWT | Zero-config auth that SMB admins understand |
| Frontend | React + Vite + Tailwind (via TanStack Start) | Consistent with team's existing toolchain |
| iPaaS | Merge.dev | 20+ pre-built connectors with unified schemas |
| Monitoring | Sentry + Grafana + Grafana Loki | Error tracking, metrics, and logs on self-hosted or managed |
| CI/CD | GitHub Actions + Docker + (future) ArgoCD | Standard, low-overhead |
| Cloud provider | DigitalOcean (compute) + Vast.ai/Modal (GPU) | Simple pricing, good DX, GPU cost 1/3 of AWS/GCP |
| IaC | Terraform (OpenTofu-compatible) | Larger community, familiar HCL, DO provider available |

---

## Document Relationships

```
                    PRODUCT STRATEGY (what & why)
                           │
              ┌────────────┼────────────┐
              │            │            │
      SYSTEM ARCHITECTURE  │     MONETIZATION (pricing, unit econ)
      (how it works)       │            │
              │            │            │
      ┌───────┼───────┐   │   ┌────────┴────────┐
      │       │       │   │   │                 │
  AI ARCH   DATA     AGENTS│  SCALING STRATEGY  │
  (causal,  PIPELINES (multi-│  (growth path,   │
   sim,     (ETL,    agent, │   vertical exp.)  │
   LLM)     entity   tools) │                   │
             graph)         │   INFRASTRUCTURE  │
      │       │       │   │   (cloud, k8s,     │
      │       │       │   │    monitoring, DR)  │
      MEMORY SYSTEMS   │   │                   │
      (learning,  │       │   SECURITY &        │
       forgetting,│       │   COMPLIANCE        │
       storage)   │       │   (SOC 2, PII,      │
                  │       │    encryption)      │
                  │       │                   │
                  │       │   ROADMAP (24-wk   │
                  │       │    execution plan) │
                  │       │                   │
                  │       │   HIRING ROADMAP   │
                  │       │   (team building)  │
                  │       │                   │
                  │       │   PITCH DECK       │
                  │       │   (investor story) │
                  └───────┴───────────────────┘

All documents are grounded in the same design philosophy:
a small team building a defensible, capital-efficient system
for a massive underserved market.
```