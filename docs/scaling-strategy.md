# Cortex Scaling Strategy

> *Revision 1 — Founding Systems Architect*
> *From 3 to 30 to 300 customers: technical, operational, and organizational scaling*

---

## 1. Scaling Philosophy

Cortex is designed for **leverage** — a small team running a highly automated system. We don't hire to solve people problems; we build to make people unnecessary.

**Core scaling principles:**
1. **Vertical-first, horizontal-second** — dominate one vertical (dental), prove the model, then expand
2. **Self-serve onboarding** — reduce per-customer setup time from 8 hours (v1) to 30 minutes (v3)
3. **Architecture for 100 before building for 1,000** — design decisions at each stage that don't require rewriting later
4. **Automation as a product** — every manual process is a feature request for the platform

---

## 2. Customer Growth Phases

```
Phase          Timeline    Customer Count   Team Size   Key Objective
────────────────────────────────────────────────────────────────────
Craft          0-3 mo      0-3             1-2         Find PMF with 3 deep pilots
Validate       3-6 mo      3-15            2-4         Prove repeatable onboarding
Scale Prep     6-9 mo      15-30           4-6         Build self-serve, automate ops
Scale          9-18 mo     30-150          6-12        Multi-vertical expansion
Hyper-Scale    18-36 mo    150-1,000       12-30       Platform market network effects
```

---

## 3. From 3 to 30 Customers (Months 0-9)

### 3.1 Acquisition Strategy (3 → 30)

**Initial 3 pilots** are founder-sourced through personal network, industry events, or cold outreach:
- Target: dental practices the founder knows from previous work/network
- Deal: 30% discount for 12 months + white-glove onboarding
- Contract: month-to-month (low pressure)
- Success criteria: weekly usage (5+ days), 3+ decisions implemented, positive NPS

**From 3 to 15 (months 3-6):**
- Content-driven: "How a dental practice recovered $48K/year with data" case studies
- Vertical community: post in dental practice management forums, LinkedIn groups
- Referral: ask the 3 pilots for 1 referral each (offer 1 month free)
- No paid ads yet — too early; we need to understand the message

**From 15 to 30 (months 6-9):**
- First content that ranks: "Xero vs QuickBooks for dental practices" (SEO play)  
- Partner with 1-2 dental practice management software vendors (Jane, practice-web)
- Launch comparison page: "Cortex vs. hiring a COO" (high-intent search)
- Founders begin limited targeted LinkedIn ads ($2K/mo)

### 3.2 Technical Scaling (Up to 30 Customers)

**Architecture at 30 customers:** No change from v1 architecture (Docker Compose on single VM).

| Resource | 3 Customers | 30 Customers | Bottleneck at 30? |
|----------|-------------|--------------|-------------------|
| API replicas | 1 (standalone) | 2-3 behind Nginx | No — FastAPI async handles 1K+ req/s |
| DB connections | 20 | 120 (4 per customer) | PgBouncer needed at ~50 customers |
| Celery workers | 3 | 10 | No — scale by adding workers |
| Storage (Postgres) | 5 GB | 50 GB | No — 1 TB within single instance range |
| LLM inference | 1× A100 (shared) | 1× A100 (shared) | At ~20 customers, queue builds during peak. Add second A100 at 25 customers. |
| Merge.dev cost | ~$5/mo | ~$45/mo | Negligible |

**Key infrastructure additions at 30 customers:**
- PgBouncer for connection pooling
- Redis Sentinel for high-availability cache
- Application-level read replicas for dashboard queries
- Prometheus + Grafana on dedicated monitoring VM

### 3.3 Operational Scaling (3 → 30)

**Onboarding process evolution:**

```
Early (3-10 customers):                     Scaling (10-30 customers):
  • Founder-led, 1:1 video calls              • Structured video + async
  • 8 hours/customer (manual setup)           • 4 hours/customer (semi-auto)
  • Custom entity resolution tuning           • Template-based tuning
  • Slack channel per customer                • Knowledge base + async support
  • Everything is special case                • Defined playbook with exceptions
```

**Customer success tier (3 → 30):**

| N of Customers | CS Approach | CS Team | Key Metric |
|---------------|-------------|---------|------------|
| 3 | Founder does all CS | 0 dedicated | NPS, weekly usage |
| 10 | Founder + first CS hire (part-time) | 1 (0.5 FTE) | Time-to-value < 3 weeks |
| 30 | CS team established | 1 (1.0 FTE) | Churn < 8%/mo |

---

## 4. From 30 to 300 Customers (Months 9-24)

### 4.1 Acquisition Scale (30 → 300)

**Channel mix evolution:**

| Channel | At 30 | At 100 | At 300 |
|---------|-------|--------|--------|
| Founder outbound | 70% | 20% | 0% |
| Content/SEO | 15% | 35% | 40% |
| Referrals | 10% | 25% | 30% |
| Partnerships | 5% | 15% | 20% |
| Paid acquisition | 0% | 5% | 10% |

**Key growth levers:**

1. **Vertical playbooks** — once we have 20+ dental practices, document "the dental playbook" (which integrations, which decisions, ROI benchmarks). This becomes a lead magnet and onboarding accelerator.
2. **Case study factory** — every customer who achieves >$20K in realized ROI gets a case study. Template-based production: interview → write → customer approve → publish → repurpose across content.
3. **Referral program** — "Give your friend $500 off. Get $500 credit." Simple, measurable.
4. **Partner channel** — software vendors, practice management consultants, accounting firms who recommend Cortex to their clients. Revenue share: 15% of first year subscription.

### 4.2 Technical Scaling (30 → 300)

#### Architecture Evolution

```
┌─ V1 (0-50 customers): Docker Compose on 1-3 VMs
│  api (3x) | worker (10x) | agent (1x) | db (1x) | redis (1x) | minio (1x)
│  Cost: ~$500/mo in infra
│
├─ V2 (50-300 customers): Orchestrated migration to k8s
│  • Managed k8s on DigitalOcean or GKE
│  • Service decomposition:
│    ┌─ api-gateway (stateless, auto-scale)
│    ├─ integration-service (stateful to Merge.dev, auto-scale)
│    ├─ data-pipeline (worker pool, auto-scale by queue depth)
│    ├─ agent-system (stateful per tenant, scale by tenant count)
│    ├─ simulation-engine (GPU-backed, scale on demand)
│    └─ analytics-api (read replicas, cached)
│  • Database: HA Postgres with read replicas + PgBouncer
│  • Cost: ~$3K-5K/mo in infra
│
└─ V3 (300+ customers): Multi-region, data-plane separation
   • Data-plane per region (US-East, US-West, EU-West)
   • Control-plane (global): user management, billing, marketplace
   • Sharded Postgres (by tenant_id hash)
   • Cost: ~$10-15K/mo in infra
```

#### Database Scaling Path

| Stage | Architecture | Connections | Storage | Read Capacity |
|-------|-------------|-------------|---------|---------------|
| 0-50 customers | Single Postgres 16 (4 vCPU, 16GB RAM) | 20-200 (via PgBouncer) | 100 GB | Single instance |
| 50-150 customers | Primary + Read Replica (8 vCPU, 32GB each) | 200-600 | 500 GB | Read replica for dashboards |
| 150-300 customers | Per-region Postgres with pg_partman sharding | 600-1,200 | 1.5 TB | 2-3 read replicas per shard |
| 300+ customers | Citus (distributed Postgres) or CockroachDB | 1,200+ | Multi-TB | Distributed queries |

**When to scale each component:**

| Component | Scaling Trigger | Action |
|-----------|----------------|--------|
| **API** | CPU > 70% sustained | Increase replicas (horizontal, easy) |
| **Agent system** | Queue depth > 100 pending | Add agent workers (horizontal) |
| **LLM inference** | Queue wait > 10s | Add GPU node or upgrade to H100 |
| **Postgres** | Connection pool exhaustion | Add PgBouncer → Add read replica → Shard |
| **Storage** | > 80% disk used | Increase volume size → Archive old data to S3 |
| **Redis** | Memory > 80% | Upgrade instance or add cluster |

#### Model Serving at Scale

| Phase | Model | Hardware | Cost/Month | Throughput |
|-------|-------|----------|-----------|------------|
| 0-30 cust | Llama 3 70B | 1× A100 (80GB) | $1,500 | ~50 req/min |
| 30-100 cust | Llama 3 70B | 2× A100 (80GB) | $3,000 | ~150 req/min |
| 100-300 cust | Llama 3 70B + 8B | 4× A100 (80GB) + 1× L4 | $6,500 | ~500 req/min |
| 300+ cust | Multiple fine-tuned 8B per vertical | 8× A100 or H100 | $15,000 | ~2K req/min |

### 4.3 Operational Scaling (30 → 300)

#### Onboarding Automation Targets

| Metric | Month 1 | Month 9 (30 cust) | Month 18 (100 cust) | Month 24 (300 cust) |
|--------|---------|-------------------|--------------------|--------------------|
| Onboarding time | 8 hours | 4 hours | 2 hours | 30 minutes |
| Manual steps | 15 | 10 | 5 | 1 (quality review) |
| Self-serve % | 0% | 20% | 60% | 90% |
| Success rate (active at 30 days) | 60% | 75% | 85% | 90% |

**Self-serve onboarding flow (v3 target):**
1. Sign up → OAuth → connect tools (all automated)
2. Data sync → progress bar (no human needed)
3. Automated data quality check → "Your data is 85% complete" (email if issues)
4. One 15-min video call to review first insights (optional at scale)
5. Onboarding complete — owner is live

#### Customer Support Tiers

| Tier | Response Time | Channel | Cost/Customer/Month | At Scale % of Customers |
|------|--------------|---------|-------------------|------------------------|
| **Self-serve** | Immediate | Docs, FAQ, in-app help | $0 | 60% |
| **Chatbot** | < 30s | In-app AI assistant (GPT-4o) | $1/cust | 25% |
| **Email support** | < 4 hours | support@ | $5/cust | 10% |
| **Dedicated CS (Enterprise)** | < 15 min | Slack + weekly call | $100/cust | 5% |

#### Support Team Growth

| Customers | Support Headcount | Support Structure |
|-----------|------------------|-------------------|
| 0-30 | 0 (founder handles) | — |
| 30-100 | 1 + AI chatbot | Generalist CS, handles all tiers |
| 100-300 | 3 (1 team lead + 2 CS) | Tiered: L1 chatbot → L2 email → L3 dedicated |
| 300-1,000 | 8 (1 lead + 5 CS + 2 onboarding specialists) | Full tiered org |

---

## 5. Multi-Vertical Expansion Strategy

### 5.1 Vertical Selection Framework

```
HIGH                      Home Services         Dental
ROI PER                     (roofing, HVAC,     (current, proving ground)
CUSTOMER                     plumbing)
       │
       │                   Agencies            Medical/Dental
       │                   (marketing,         (multi-specialty)
       │                    creative)
       │
       │                   Salons/Barbers      Physical Therapy
       │                                        /Chiropractic
       │
LOW      ─────────────────────────────────────────────────────────
         EASY                                   HARD
                    INTEGRATION COMPLEXITY
```

**Expansion order and rationale:**

1. **Dental** (months 0-6, proving ground)
   - Why first: most data-rich vertical (booking + payments + insurance + CRM), high willingness to pay, founder domain knowledge
   - Key integrations: Stripe/QuickBooks, Jane/Dentrix/Acuity, HubSpot
   - Decision patterns: no-show reduction, insurance claim timing, hygienist scheduling, equipment ROI

2. **Home Services** (months 6-12, first expansion)
   - Why: massive TAM (500K+ SMBs in US), similar data patterns, same integrations (add ServiceTitan/Housecall Pro via Merge.dev)
   - Key difference: field scheduling is more complex, seasonal demand patterns
   - Decision patterns: route optimization, seasonal hiring, truck roll efficiency, seasonal pricing

3. **Agencies & Professional Services** (months 9-15)
   - Why: project-based billing model, high tool stack (Asana, Harvest, Slack, Salesforce), high margins
   - Key addition: time tracking, project management tools
   - Decision patterns: utilization by project type, optimal team size per client, retainer vs. project pricing

4. **Medical/Allied Health** (months 12-18)
   - Why: similar to dental (appointment-based, insurance billing), but regulated (HIPAA)
   - Key addition: HIPAA compliance for data handling
   - Decision patterns: insurance claim denial reduction, provider scheduling, patient acquisition cost by specialty

### 5.2 Vertical-Specific Costs

| Vertical | Integration Cost | Model Calibration | Market Entry Cost |
|----------|-----------------|-------------------|-------------------|
| Dental | Low (existing integrations) | Low (similar to general SMB) | $20K (case studies, playbook) |
| Home Services | Medium (add ServiceTitan) | Medium (field scheduling is different) | $40K (content, partnerships) |
| Agencies | Medium (add Asana/Time tools) | Medium (project-based economics) | $30K (content, events) |
| Medical | High (add EHRs, HIPAA infra) | High (regulatory, insurance complexity) | $60K (HIPAA audit, legal) |

### 5.3 Vertical-Specific AI Tuning

Each vertical needs:
1. **Causal graph template** — 40-80 variables with known causal directions (domain expert needed)
2. **Decision template library** — 5-10 decision types unique to the vertical
3. **Benchmark database** — privacy-computed averages across customers in that vertical
4. **Integration pack** — pre-configured connection flow for the vertical's common tools

**Strategy: Hire one domain expert per vertical as a **"Vertical Principal"**** — part-time contractor with deep industry knowledge. They define the causal graph, validate decision quality, and review pilot customers. Cost: $500-1,000/week paid as consulting.

---

## 6. International Expansion Path

### 6.1 When to Expand

**Not before 200 US customers.** Reasons:
- Causal models are US-centric (pricing norms, tax structures, payment methods)
- Integration coverage is US-heavy (QuickBooks vs. Xero global; Stripe vs. Adyen)
- Support team would need to handle time zone and language
- Each new market = new compliance, new integrations, new pricing

### 6.2 Expansion Order

| Market | When | Key Changes | Revenue Opportunity |
|--------|------|------------|-------------------|
| Canada | Month 18+ | Add Xero for accounting, CAD handling, minimal compliance delta | +15% to TAM |
| UK | Month 24+ | Add Xero/FreeAgent, VAT handling, GBP, UK GDPR alignment | +25% to TAM |
| Australia/NZ | Month 30+ | Add MYOB/Xero, GST, AU-specific compliance | +10% to TAM |
| EU (Germany, France) | Month 36+ | Add regional accounting, EU GDPR, multi-language causal models | +40% to TAM |

### 6.3 Internationalization Strategy

| Component | Strategy |
|-----------|----------|
| **Integrations** | Focus on Merge.dev coverage (they support EU tools). Add native connectors only for high-value tools. |
| **Pricing** | Local currency pricing, adjusted for PPP. Canada: CAD 650/1,560/3,250; UK: GBP 400/960/2,000 |
| **Compliance** | GDPR for all EU customers from day 1 of expansion. DPA in place with all subprocessors. |
| **Models** | Causal templates adjusted for local market dynamics (pricing sensitivity, seasonality, holiday patterns). |
| **Support** | Email in English initially; expand to local language as volume warrants. |

---

## 7. Hiring Timeline & Org Scaling

Refer to [`hiring-roadmap.md`](./hiring-roadmap.md) for detail. This section covers timing rationale.

| Customer Count | New Hires | Why Now |
|---------------|-----------|---------|
| 3 | — | Founder builds everything |
| 10 | Engineer #2 (generalist) | Founder can't build + sell + support |
| 15 | Part-time CS / onboarding | Onboarding time becoming bottleneck |
| 30 | Engineer #3 (backend) + Sales #1 | Product needs reliability, pipeline needs nurturing |
| 50 | Engineer #4 (AI/ML) + CS #2 | Agent quality needs dedicated attention |
| 100 | Engineer #5 (infra) + Sales #2 + Marketing #1 | Scaling requires platform reliability + demand gen |
| 200 | 3 more engineers + 2 CS + 1 sales + 1 data scientist | Multi-vertical expansion, enterprise sales |

---

## 8. Partnership & Channel Strategy

### 8.1 Partner Types

| Partner Type | Value to Cortex | Value to Partner | Revenue Model |
|-------------|----------------|------------------|---------------|
| **Vertical SaaS** (Jane, ServiceTitan) | Integration + distribution | Differentiated product, reduced churn | Rev share 15% of sub or OEM embed fee |
| **Accounting firms** | Trusted advisor referral | Better client outcomes, new service line | 15% referral fee (first year) |
| **Practice management consultants** | Vertical domain expertise | Data-driven recommendations for clients | 15% referral fee |
| **Implementation partners** | Onboarding capacity | Recurring revenue stream | White-label onboarding: $1K/customer |

### 8.2 Partnership Program Structure

| Tier | Requirements | Benefits |
|------|-------------|----------|
| **Referral Partner** | Complete training (2h), refer 1+ customers/mo | 15% first year recurring, co-branded case studies |
| **Implementation Partner** | Certified onboarding training, pass customer success metrics | $500/customer setup fee + 10% recurring |
| **Technology Partner** | API integration completed, joint go-to-market | Co-marketing, featured in marketplace, rev share |

### 8.3 Partner Recruitment Phases

| Phase | Target Partners | Recruitment Method |
|-------|----------------|-------------------|
| Months 0-6 | 0 (too early) | — |
| Months 6-12 | 3-5 referral partners | Founder network + warm intros |
| Months 12-18 | 10-15 referral + 2-3 implementation | Published program, outreach to top agencies in vertical |
| Months 18-24 | 25-50 referral + 5-10 implementation + 2 tech partners | Dedicated partner manager hire, partner portal |

---

## 9. Risk Mitigation at Each Stage

| Stage | Key Risk | Mitigation |
|-------|---------|------------|
| 3 customers | No PMF, wrong vertical | Stay in 1 vertical. Listen obsessively. Willing to pivot. |
| 10 customers | Onboarding can't scale | Automate integration setup. Build self-serve calibration. |
| 30 customers | Model quality degrades with more customers | Invest in agent monitoring. Add AI/ML engineer. |
| 100 customers | Infrastructure costs outpace revenue | Right-size GPU usage (tiered model routing). Negotiate cloud discounts. |
| 200 customers | Customer support crushing team | Self-serve onboarding, AI chatbot, tiered support. |
| 300 customers | Multi-vertical complexity fragments focus | Keep 1 vertical as 60%+ of revenue. Expand cautiously. |
| 1,000 customers | Data privacy/compliance breach | SOC 2, penetration testing, encryption everywhere, privacy-by-design culture. |

---