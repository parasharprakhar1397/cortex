# Cortex Infrastructure & DevOps

> *Revision 1 — Founding Systems Architect*
> *Building for reliability, cost efficiency, and team leverage*

---

## 1. Cloud Provider Selection

### Decision: DigitalOcean (Primary) + Vast.ai / Modal (GPU)

| Provider | Why We Chose | Why We Didn't Choose |
|----------|-------------|---------------------|
| **DigitalOcean** (primary compute) | Simple pricing (no surprise bills), good DX, managed Postgres + Redis, k8s (DOKS) when ready, $200-400/mo for v1 VM | No GPU instances (need separate provider for inference) |
| **Vast.ai / Modal** (GPU inference) | Vast: 1/3 the cost of AWS/GCP for A100s. Modal: serverless GPU, auto-scales to zero. | Vast: less reliable, no SLA. Modal: cold starts on GPU. |
| **Hetzner** (EU expansion) | 50% cheaper than DigitalOcean for equivalent compute, EU data residency | Not suitable for primary (timezone, support lag) |
| **AWS/GCP** | NOT chosen for v1. Too complex, too expensive, too much cognitive overhead for a small team. | Will revisit at 200+ customers for managed k8s, multi-region, compliance certifications. |

**Why NOT serverless (Lambda, Cloud Run) for everything:**
- Long-running agent processes (simulation, causal analysis) exceed serverless timeouts
- Stateful agent memory doesn't fit serverless well
- GPU inference can't run on Lambda
- Serverless is more expensive at sustained load (our 10-30 worker agents are always-on)
- Trade-off accepted: we manage a few VMs but get full control and predictable cost

### Cost Comparison (v1, 3-50 customers)

| Provider | Monthly Cost | What's Included |
|----------|-------------|-----------------|
| DigitalOcean | $400-600 | 1 app VM (8 vCPU, 16GB), 1 DB VM (dedicated Postgres, 4 vCPU, 8GB), 1 Redis VM, 1 MinIO VM, 1 monitoring VM, backups |
| Vast.ai (GPU) | $1,500-2,000 | 1× A100 80GB, 24/7 availability |
| **Total infra** | **$1,900-2,600/mo** | For 50 customers = $38-52/customer/mo (well within COGS target) |

---

## 2. Infrastructure as Code

### Decision: Terraform (with OpenTofu compatibility)

**Why Terraform, not Pulumi:**
- Larger community, more examples, easier to hire for
- OpenTofu compatible (no vendor lock-in risk after HashiCorp license change)
- DigitalOcean has official Terraform provider
- Everyone on the team can read HCL (even non-infra engineers)

**Directory structure:**

```
terraform/
├── environments/
│   ├── dev/          # Shared dev environment
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── staging/      # Pre-production (mirrors prod)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── prod/         # Production
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── modules/
│   ├── compute/      # Application VM + Docker Compose config
│   ├── database/     # Postgres with extensions
│   ├── redis/        # Redis cache + queue
│   ├── storage/      # S3-compatible object storage
│   └── monitoring/   # Prometheus, Grafana, Loki
├── state/            # Remote state config (S3-compatible backend)
└── versions.tf
```

**State management:** Terraform state stored in a DigitalOcean Spaces bucket (S3-compatible) with state locking via DynamoDB-equivalent (DO Spaces does not have native locking — use a simple Redis lock as fallback).

---

## 3. CI/CD Pipeline

### Toolchain: GitHub Actions + Docker + ArgoCD (v2)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CI/CD PIPELINE                               │
│                                                                     │
│  DEVELOPER PUSHES TO MAIN                                           │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────────┐                                                │
│  │ 1. LINT + TEST  │  • Ruff (Python lint), mypy (type check)      │
│  │                 │  • Pytest (unit + integration)                 │
│  │                 │  • Semgrep (SAST security scan)                │
│  │                 │  • pip-audit (dependency vuln scan)            │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │ 2. BUILD        │  • Docker build with cache layer optimization  │
│  │                 │  • Multi-stage build (Python base → deps → app)│
│  │                 │  • Tag: git-sha-short + timestamp              │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │ 3. REGISTRY     │  • Push to GitHub Container Registry (ghcr.io) │
│  │                 │  • Also push to DO Container Registry (DR)     │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │ 4. DEPLOY STAG  │  • SSH into staging VM → docker-compose pull   │
│  │                 │  • docker-compose up -d (zero-downtime if 2+   │
│  │                 │    replicas)                                    │
│  │                 │  • Run smoke tests: healthcheck, API test      │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │ 5. DEPLOY PROD  │  • Manual approval gate (Github Environments)  │
│  │ (manual gate)   │  • Same deploy process as staging              │
│  │                 │  • Rollback: docker-compose up -d with prev tag│
│  └─────────────────┘                                                │
│                                                                     │
│  ON PUSH TO FEATURE BRANCH                                          │
│  • Lint + test only (no deploy)                                    │
│  • Preview deployment: ephemeral environment on a subdomain         │
│    (future: use DigitalOcean App Platform preview envs)              │
└─────────────────────────────────────────────────────────────────────┘
```

### Docker Compose Structure (v1)

```yaml
# docker-compose.yml (production)
version: "3.9"

services:
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes: [./nginx.conf:/etc/nginx/nginx.conf, ./static:/static, ./certs:/etc/letsencrypt]
    depends_on: [api, ui]

  api:
    image: ghcr.io/cortex-dev/api:${DEPLOY_TAG}
    build: ./api
    env_file: .env.production
    environment:
      - DATABASE_URL=postgres://...
      - REDIS_URL=redis://redis:6379
      - NATS_URL=nats://nats:4222
    deploy:
      replicas: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      retries: 3

  ui:
    image: ghcr.io/cortex-dev/ui:${DEPLOY_TAG}
    build: ./ui
    ports: ["3000:3000"]  # TanStack Start dev server
    depends_on: [api]

  worker:
    image: ghcr.io/cortex-dev/api:${DEPLOY_TAG}
    command: celery -A cortex.worker worker --concurrency=4 --queues=default,analysis,monitoring
    env_file: .env.production
    deploy:
      replicas: 5

  agent:
    image: ghcr.io/cortex-dev/agent:${DEPLOY_TAG}
    build: ./agent
    command: python -m cortex.agent.supervisor
    env_file: .env.production
    deploy:
      replicas: 2

  db:
    image: postgres:16-alpine
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    # In production: use managed DigitalOcean Postgres (not this container)

  redis:
    image: redis:7-alpine
    volumes: [redisdata:/data]

  nats:
    image: nats:2-alpine
    command: -js  # JetStream enabled

  minio:
    image: minio/minio
    command: server /data
    volumes: [miniodata:/data]
    # In production: use DigitalOcean Spaces (S3-compatible)
```

### Database Migration Strategy

- **Alembic** for schema migrations
- Migrations run as part of deploy (init container or CI step)
- Backward-compatible migrations only (no breaking changes to existing data)
- Rollback: Alembic downgrade step in deploy rollback script

---

## 4. Environment Strategy

| Environment | Purpose | Infrastructure | Data | Access |
|-------------|---------|---------------|------|--------|
| **Dev** | Engineering development, feature testing | Single DO droplet, Docker Compose, shared | Synthetic data (generated) + anonymized subset | All engineers |
| **Staging** | Pre-production validation, integration tests | Mirrors prod (smaller scale), managed Postgres | Anonymized production data (subset, rotated weekly) | All engineers + CI |
| **Production** | Live customer traffic | Managed Postgres, Redis, S3, GPU inference | Real customer data | Engineers on-call only |
| **Ephemeral** (v2) | Per-branch preview for testing | DO App Platform preview envs | Synthetic data | CI only |

**Promotion flow:**
```
Dev → (feature branch, CI passes) → Staging → (smoke tests pass, QA) → Production (manual approval)
```

---

## 5. Container Orchestration Evolution

### v1 (0-50 customers): Docker Compose on VMs

**Architecture:** Single VM (or 2-3 VMs) with Docker Compose.

**Pros:**
- Simple: one ssh command to deploy, one docker-compose.yml to understand
- Low cognitive overhead: every engineer can debug a Docker Compose setup
- Fast iteration: edit, docker-compose up -d, done
- Cheap: $200-400/mo for a beefy VM

**Cons:**
- No auto-scaling (manual scale by editing replicas)
- No rolling updates (brief downtime with single replica)
- No self-healing (if a container crashes, it stays down)
- No service discovery (manual)

**Acceptable for v1 because:** 50 customers with predictable traffic patterns don't need auto-scaling. A crashed container is caught by Sentry alert within 5 minutes and an engineer restarts it. The cost of k8s complexity ($1K+/mo in ops overhead) exceeds the benefit.

### v1.5 (50-100 customers): Docker Compose on Multiple VMs

**Architecture:** 3-5 VMs, each running a subset of services:
- VM 1: API + UI (2 replicas each)
- VM 2: Workers + Agents (10-15 Celery workers)
- VM 3: Database (managed Postgres)
- VM 4: Monitoring (Prometheus, Grafana, Loki)
- VM 5: GPU (A100, vLLM serving)

**Orchestration:** Simple Ansible or Fabric scripts to manage multi-VM Docker Compose. No k8s yet.

### v2 (100-300 customers): Managed k8s

**Architecture:** DigitalOcean Kubernetes (DOKS) or GKE Autopilot.

**Why k8s finally:**
- Need auto-scaling for variable agent workloads
- Need zero-downtime deploys for a growing customer base
- Need resource isolation between services (API gets priority, batch workers don't starve it)
- Need canary deployments for agent updates (deploy new agent to 5% of customers first)

**Migration approach:**
1. Containerize services (already done with Docker)
2. Create Helm charts for each service
3. Deploy stateless services first (API, UI, workers)
4. Then stateful services (DB, Redis, NATS — use managed services)
5. Run k8s and Docker Compose in parallel for 1 month
6. Cut over fully

### v3 (300+ customers): Multi-Region k8s

- Data planes per region (US, EU)
- Global control plane (API gateway, billing, marketplace)
- Service mesh (Istio or Linkerd) for mTLS, traffic splitting, observability
- GitOps with ArgoCD

---

## 6. Monitoring, Alerting & Observability

### Stack

| Layer | Tool | Hosting | Cost |
|-------|------|---------|------|
| **Metrics** | Prometheus + Grafana | Self-hosted (Prometheus) + Grafana Cloud (free tier) | $0 for v1 |
| **Logs** | Grafana Loki (via Promtail) | Self-hosted or Grafana Cloud | $0-50/mo |
| **Tracing** | OpenTelemetry → Jaeger or Grafana Tempo | Self-hosted | $0-200/mo |
| **Error tracking** | Sentry | Sentry SaaS (free tier: 5K events/mo) | $0-26/mo |
| **Uptime monitoring** | Better Uptime or Checkly | SaaS | $0-30/mo |
| **Alerting** | PagerDuty | SaaS | $0 (free up to 2 users) |
| **Dashboard** | Grafana | Self-hosted | $0 |

### Key Dashboards

**Engineering Dashboard:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  CORTEX PRODUCTION                                                  │
│                                                                     │
│  API: p50 45ms │ p95 180ms │ p99 450ms │ Error Rate 0.2%         │
│  Queues: default 12 │ analysis 3 │ monitoring 0 │ simulation 1    │
│  DB: CPU 23% │ Connections 47/200 │ IOPS 1,200 │ Replication lag 2s│
│  GPU: Memory 42GB/80GB │ Utilization 38% │ Queue wait 0.3s       │
│  Agents: 2/2 healthy │ Last cycle: 14s ago │ Decisions/hr: 34    │
│  Integrations: 142/150 healthy │ 5 degraded │ 3 down              │
└─────────────────────────────────────────────────────────────────────┘
```

**Business Dashboard:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  CORTEX BUSINESS                                                    │
│                                                                     │
│  Active Customers: 42 │ MRR: $38,400 │ Gross Margin: 78%           │
│  Churn (MTD): 4.2% │ NRR: 112% │ CAC: $1,800                     │
│  Decisions Surfaced: 1,280/d │ Feedback Rate: 34% │ Positive: 68% │
│  Avg Integration Depth: 4.8 tools │ Time-to-Value: 6.2 days       │
└─────────────────────────────────────────────────────────────────────┘
```

### Alerting Rules

| Alert | Condition | Severity | Channel |
|-------|-----------|----------|---------|
| API error rate > 2% | 5-min window | CRITICAL | PagerDuty |
| API p95 > 500ms | 5-min window | WARNING | Slack |
| Queue depth > 100 | Any queue, sustained 5 min | WARNING | Slack |
| DB connection pool > 80% | 5-min window | CRITICAL | PagerDuty |
| GPU queue wait > 30s | 5-min window | WARNING | Slack |
| Integration down > 15 min | Any critical tool (Stripe, QB) | CRITICAL | PagerDuty |
| Agent cycle failure | 3 consecutive failures | WARNING | Slack |
| Disk > 80% | Any node | WARNING | Slack |
| LLM cost > $X/day | Per-customer or total | WARNING | Slack |

### Logging Standards

```python
# Structured JSON logging with structlog
import structlog

logger = structlog.get_logger()

# Every log line includes:
# - timestamp (ISO8601)
# - level (INFO, WARNING, ERROR)
# - service_name
# - correlation_id (traceable across services)
# - tenant_id (if applicable)
# - message
# - extra fields (structured, queryable)

logger.info("decision.generated", 
    tenant_id="abc123",
    decision_type="pricing",
    confidence=0.82,
    estimated_roi=11800,
    analysis_duration_ms=3400,
    correlation_id="req-7f3a1b2c"
)
```

---

## 7. Disaster Recovery & Backup Strategy

### 7.1 Backup Schedule

| Data | Method | Frequency | Retention | Restore RTO | Restore RPO |
|------|--------|-----------|-----------|-------------|-------------|
| PostgreSQL (entity data) | pg_dump → S3 (encrypted) | Daily | 30 days | 4 hours | 24 hours |
| PostgreSQL (WAL archive) | Continuous WAL streaming to S3 | Continuous (every 5 min) | 7 days | 15 min (replica promotion) | 5 min |
| Time-series data | TimescaleDB chunk backup | Daily (via pg_dump) | 30 days | 4 hours | 24 hours |
| S3/MinIO objects | Cross-region replication | Automatic | 90 days | 1 hour | < 5 min |
| Configuration (Terraform state) | Remote state with versioning | Every apply | 90 days | 1 hour | Last apply |
| LLM model weights | Weights & Biases / S3 | On update | All versions | 1 hour | Last version |

### 7.2 Disaster Scenarios

| Scenario | Impact | Recovery Strategy | Time to Restore |
|----------|--------|-------------------|-----------------|
| **Single AZ outage** | Service degraded | Failover to read replica in different AZ | 5-15 min |
| **Region outage** | Complete service loss | Deploy to secondary region (US-West → US-East) | 2-4 hours |
| **Data corruption** | Incorrect decisions | Restore from pg_dump backup | 4 hours |
| **Accidental deletion** | Lost customer data | Restore from backup + re-sync from source tools | 4-8 hours |
| **Ransomware** | All data encrypted | Restore from offline backup (S3 with versioning + immutability) | 8 hours |
| **LLM model corruption** | Bad decisions | Roll back to previous model version | 1 hour |

### 7.3 Disaster Recovery Plan: Quick Reference

```
1. DETECT: Alert fires (PagerDuty)
2. ASSESS: On-call determines severity, opens incident
3. COMMUNICATE: Status page updated (e.g., "Cortex is investigating an issue")
4. DECIDE: 
   - If RTO < 30 min: promote read replica, failover
   - If RTO > 30 min: restore from backup
5. EXECUTE: Run restore playbook (documented in runbook.md)
6. VERIFY: Run smoke tests, check data integrity
7. RESTORE: Point DNS to restored system
8. COMMUNICATE: Update status page, notify affected customers
9. POST-MORTEM: Write incident report within 72 hours
```

---

## 8. Cost Optimization Approach

### 8.1 Cost Categories & Targets

| Category | % of Total Cost | Optimization Levers | Target Cost per Customer |
|----------|----------------|-------------------|--------------------------|
| **GPU compute** | 50-60% | Model quantization (FP16 → FP8 → INT4), tiered model routing, batch inference, spot instances | $10-30/cust/mo |
| **General compute** | 15-20% | Right-size VMs, reserved instances, autoscaling workers | $5-10/cust/mo |
| **Database** | 10-15% | Connection pooling, data compression (TimescaleDB: 90%+ on older data), archive to S3 | $5-8/cust/mo |
| **Storage** | 5-10% | Lifecycle policies (delete raw after 90d), S3 compression, deduplication | $2-5/cust/mo |
| **Networking** | 3-5% | CDN for static assets, internal traffic (same-AZ, no egress) | $1-3/cust/mo |
| **SaaS tools** | 5-10% | Merge.dev, Clerk, Sentry, Grafana Cloud | $5-10/cust/mo |

### 8.2 Specific Optimizations

| Optimization | Impact | When to Implement |
|-------------|--------|-------------------|
| **Model quantization** | 2x throughput on same GPU | v1 (from day 1 — use Llama 3 70B in FP8) |
| **Tiered model routing** | 70% of decisions handled by 8B model (90% cheaper) | v1 (from day 1 — see AI Architecture) |
| **Batch inference** | 3-5x throughput for scheduled agent processing | v2 (when GPU queue builds) |
| **Spot GPU instances** | 60-70% discount on GPU | v2 (when fault tolerance is in place) |
| **TimescaleDB compression** | 90%+ storage reduction on old time-series data | v1 (from day 1) |
| **S3 lifecycle policies** | Auto-delete raw data after 90 days | v1 (from day 1) |
| **Reserved instances** | 20-40% discount on predictable compute | v2 (when usage is stable) |
| **CDN for static assets** | Reduce origin load, faster global load times | v1 (from day 1 — use DO CDN or Cloudflare) |

### 8.3 Cost Monitoring

- Budget alerts per category (email when > 80% of monthly budget)
- Cost dashboard in Grafana (per-customer infrastructure cost, by tier)
- Weekly cost review in engineering standup
- Quarterly cost optimization review (with explicit targets)

---

## 9. Local Development Environment

```yaml
# docker-compose.yml (development)
# Lightweight: no GPU, no production data, mocked external services

services:
  api:
    build: ./api
    command: uvicorn --reload
    volumes: [./api:/app]  # Hot reload
    ports: ["8000:8000"]
    depends_on: [db, redis, nats]

  worker:
    build: ./api
    command: celery -A cortex.worker worker --concurrency=2 --loglevel=info
    volumes: [./api:/app]
    depends_on: [redis, nats]

  db:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    volumes: [pgdata_dev:/var/lib/postgresql/data]
    environment:
      POSTGRES_PASSWORD: cortex_dev
      POSTGRES_DB: cortex_dev

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  nats:
    image: nats:2-alpine
    command: -js -m 8222  # JetStream + monitoring
    ports: ["4222:4222", "8222:8222"]

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]

  # Mock services for integration testing
  mock-merge:
    image: mockoon/cli
    command: ["--data", "/data/merge-mock.json", "--port", "3001"]
    volumes: [./tests/mocks/merge-mock.json:/data/merge-mock.json]
    ports: ["3001:3001"]
```

**Developer experience goals:**
- `docker compose up` = full local environment in < 30 seconds
- API hot-reloads on file save (uvicorn --reload)
- Worker restarts on code change (via watchdog)
- Pre-seeded with synthetic data: 10 customers, 100 invoices, 200 bookings
- Mock Merge.dev endpoint returns realistic data
- GPU not needed for local dev (LLM calls return mock responses)

---

## 10. Infrastructure Runbook: Common Operations

| Operation | Command / Procedure |
|-----------|--------------------|
| **Deploy new version** | `./deploy.sh staging` (auto) → GitHub manual approval → `./deploy.sh prod` |
| **Rollback** | `docker-compose up -d <service>=<prev_tag>` |
| **View logs** | `docker-compose logs -f <service>` or Grafana Loki |
| **Scale workers** | `docker-compose up -d --scale worker=10` |
| **Restart service** | `docker-compose restart <service>` |
| **Database backup** | `pg_dump -Fc tenant_abc123 > backup.dump` (automated daily) |
| **Database restore** | `pg_restore -d postgresql://... backup.dump` |
| **Check GPU status** | `nvidia-smi` on GPU VM |
| **Rebuild and redeploy** | `docker-compose build <service> && docker-compose up -d <service>` |
| **Full infra restart** | `docker-compose down && docker-compose up -d` (5-min downtime) |

---