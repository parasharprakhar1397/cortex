# Cortex Implementation Roadmap

> *Revision 1 — Founding Systems Architect*
> *24-week plan to ship, validate, and scale. Buildable by a small team.*

---

## 1. Timeline Overview

```
Weeks 1-4       Weeks 5-8        Weeks 9-12       Weeks 13-16       Weeks 17-24
PHASE 0         PHASE 1          PHASE 2          PHASE 3           PHASE 4
FOUNDATION      ALPHA            BETA             LAUNCH            GROWTH
│               │                │                │                 │
├─ Architecture  ├─ Core system   ├─ 3 pilots      ├─ 10 customers   ├─ 30+ customers
├─ Integrations  ├─ 5 decisions   ├─ Feedback      ├─ Iteration      ├─ Vertical exp.
├─ Prototype     ├─ Agents        ├─ Iteration     ├─ 5 more ints.   ├─ Self-serve
├─ Auth/DB       ├─ Simulation    ├─ Tuning        ├─ Docs           ├─ Partners
└─ CI/CD         └─ Dashboard     └─ Refinement    └─ Launch         └─ Scale
```

**Team size:** 1 (founder) → 2 (add engineer #2) → 3 (add part-time CS) → 4 (add engineer #3)

---

## 2. Phase 0: Foundation (Weeks 1-4)

### Goal: Working prototype that connects to one integration and surfaces one decision.

### What's Built

| Week | Deliverable | Details | Dependencies |
|------|------------|---------|-------------|
| 1 | **Project scaffolding** | FastAPI project, Docker setup, CI/CD pipeline, Terraform for dev environment, GitHub repo + project board | None |
| 2 | **Database foundation** | PostgreSQL 16 with pgvector + TimescaleDB, schema-per-tenant isolation, Alembic migrations, first entity tables (customers, invoices) | Week 1 |
| 3 | **Auth + multi-tenancy** | Clerk integration, JWT validation, X-Cortex-Tenant-ID middleware, role scaffolding (Owner/Manager/Viewer), signup flow | Week 2 |
| 4 | **Stripe native connector** | OAuth flow, batch sync (invoices, customers, charges), webhook receiver (invoice.paid, payment_failed), raw data → S3, first normalization mapper | Week 3 |

### Who Builds It

| Role | Person | Time Allocation |
|------|--------|-----------------|
| Founder (CTO) | Full-time | 100% — building everything |
| AI/ML consultant | Contractor | 10 hrs/week — causal graph design, model architecture |

### Success Criteria

- [ ] Developer can run `docker compose up` and see a working system
- [ ] Stripe OAuth flow works end-to-end (connect → sync → store)
- [ ] Webhook received and processed (invoice.paid)
- [ ] Multi-tenant: two test tenants have data isolated
- [ ] CI/CD: push to main deploys to staging automatically
- [ ] Dashboard shows "Connected to Stripe, 143 invoices synced"

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Stripe OAuth flow complexity | Medium | High | Use Stripe's Connect SDK for OAuth; don't build from scratch |
| Docker networking issues | Medium | Medium | Use docker-compose networking; keep it simple |
| TimescaleDB setup complexity | Low | Medium | Use managed Postgres with TimescaleDB support (DigitalOcean or Timescale Cloud) |
| Founder burnout | Medium | High | Work 50-hour weeks, not 80-hour. Sleep. Exercise. |

### Cost: $0 (all founder time) + $300/mo infra + $2K consultant

---

## 3. Phase 1: Alpha (Weeks 5-8)

### Goal: End-to-end decision loop — connect, analyze, recommend, get feedback. Four more integrations, five decision types.

### What's Built

| Week | Deliverable | Details | Dependencies |
|------|------------|---------|-------------|
| 5 | **QuickBooks + Calendly connectors** | OAuth, batch sync, webhooks, normalization mappers for both. Entity resolution: customer matching across Stripe/QB/Calendly. | Phase 0 |
| 6 | **HubSpot + GA4 connectors** | OAuth, batch sync, normalization mappers. Entity graph: customer, invoice, booking, campaign entities with relationships. | Week 5 |
| 7 | **Business model graph + first agents** | Entity graph assembly, time-series metric derivation, Monitoring Agent (15-min cycle), Analysis Agent (statistical tests for no-show detection, revenue trend), first causal template (dental). | Week 6 |
| 8 | **Decision cards + dashboard UI** | Decision Agent generates first 5 decision types: pricing optimization, no-show risk, booking gap, churn risk, cash flow dip. Web UI shows decision cards, morning digest email, feedback loop (✓/✗/implemented). | Week 7 |

### Who Builds It

| Role | Person | Time Allocation |
|------|--------|-----------------|
| Founder (CTO) | Full-time | 100% — system architecture, agents, integrations |
| *No new hires yet* | — | — |

### Integration Coverage

| Tool | Status | Sync Type | Entity Coverage |
|------|--------|-----------|-----------------|
| Stripe | ✅ Existing | Webhook + Batch (2h) | Invoices, customers, charges, refunds |
| QuickBooks | ✅ New | Batch (4h) | Invoices, customers, accounts, items |
| Calendly | ✅ New | Webhook + Batch (1h) | Events, invitees, cancellations |
| HubSpot | ✅ New | Batch (6h) | Contacts, deals, companies |
| GA4 | ✅ New | Batch (6h) | Events, sessions, conversions |

### Decision Types (v1)

| Decision | Data Sources | ROI Estimation Method |
|----------|-------------|----------------------|
| **Pricing optimization** | Stripe + QB + Calendly | Price elasticity from historical data + peer benchmark |
| **No-show risk** | Calendly + Stripe | Causal model: employee, day, service → no-show probability |
| **Booking gap detection** | Calendly | Time-series anomaly: expected vs. actual bookings |
| **Churn risk** | Stripe + HubSpot | Behavioral signals: declining frequency, negative reviews |
| **Cash flow dip** | Stripe + QB | A/R aging + expense anomaly + revenue forecast |

### Success Criteria

- [ ] All 5 integrations syncing data reliably
- [ ] Entity resolution: customer "Jane Smith" matched across 3+ tools
- [ ] Monitoring Agent runs every 15 min, detects metric shifts
- [ ] Analysis Agent generates analysis from detected shifts
- [ ] Decision Agent produces decision cards with ROI estimates
- [ ] Dashboard shows 5 decision types, all with data
- [ ] Feedback loop: owner can mark cards "useful" or "not useful"
- [ ] Internal test: founder uses it daily for 2 weeks, catches 1 real insight

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Entity resolution quality is poor | High | Medium | Start with exact email match only. Add fuzzy matching in phase 2. |
| Causal inference gives noisy results | Medium | High | Fall back to simple correlation-based analysis. Add "Low confidence" badge. |
| Self-hosted LLM not ready | Medium | Medium | Use OpenAI API for Tier 2 (LLM fallback already in architecture). Set up vLLM in parallel. |
| Agent infinite loops | Medium | Medium | Hard timeout per agent (5 min). Supervisor kills infinite loops. |
| Data volume overwhelms pipeline | Low | Medium | Daft streaming handles 10M+ records. Start with 1 month of data, not 2 years. |

### Cost: $0 (founder) + $500/mo infra (GPU + compute) + $200/mo API costs

---

## 4. Phase 2: Beta (Weeks 9-12)

### Goal: 3 paying pilot customers actively using Cortex weekly. Measurable business improvements.

### What's Built

| Week | Deliverable | Details | Dependencies |
|------|------------|---------|-------------|
| 9 | **Pilot onboarding flow** | Structured onboarding process (see monetization.md), integration setup wizard, calibration survey, first insight delivery | Phase 1 |
| 10 | **Pilot 1 onboarded** | Dental practice #1 (personal network). White-glove: founder does setup, reviews first 10 decisions with owner. | Week 9 |
| 11 | **Pilot 2 onboarded** | Dental practice #2 (referral from pilot 1). Semi-automated onboarding. | Week 10 |
| 12 | **Pilot 3 onboarded** | Dental practice #3 (cold outreach). Test signup flow without founder hand-holding. | Week 11 |

### Additional Technical Work

| Feature | Priority | Effort | Why |
|---------|----------|--------|-----|
| Simple simulation engine (single-variable) | P1 | 2 weeks | Owner needs "what if?" — turns a recommendation into action |
| Decision deduplication | P1 | 0.5 week | Preventing "same recommendation 3 days in a row" |
| Data quality alerts | P1 | 1 week | "Calendly data is stale — insights may be degraded" |
| Morning digest email | P1 | 0.5 week | Daily habit formation, async engagement |
| Snooze/dismiss decisions | P1 | 0.5 week | Owner control over what they see |
| First hire: Engineer #2 | P0 | — | Needed to accelerate Phase 3 |

### Pilot Selection Criteria

For each pilot customer:
- [ ] Revenue: $1-5M (sweet spot for Essentials tier)
- [ ] Vertical: Dental practice (single or multi-location)
- [ ] Tool stack: At least 3 of the 5 supported integrations (Stripe, QB, Calendly, HubSpot, GA4)
- [ ] Owner willingness: Weekly check-in call for first 4 weeks
- [ ] Pain point: "I don't know what's happening in my business until it's too late"
- [ ] Budget: Can afford $500/mo (or $350 with pilot discount)

### Pilot Engagement Metrics

| Metric | Target | How We Measure |
|--------|--------|----------------|
| Daily active usage | 5+ days/week | Dashboard login + decision view events |
| Feedback rate | 50%+ of decisions rated | Feedback button clicks |
| Decisions implemented | 2+ per week | Owner clicks "Implemented" or auto-detected |
| NPS | 30+ | Monthly survey |
| ROI realized | $2K+/mo by week 4 | Owner-reported dollar impact |
| Time-to-first-insight | < 2 hours | Time from signup to first decision card |

### Success Criteria

- [ ] 3 pilots active, all using Cortex 5+ days/week
- [ ] At least 2 pilots have implemented 2+ decisions and seen measurable impact
- [ ] NPS > 30 (average)
- [ ] At least 1 pilot willing to provide a case study testimonial
- [ ] Founder can articulate: "Here's exactly what we're good at and what we're not"

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Pilots don't use the product | Medium | Critical | Weekly check-in calls. Founder watches usage daily. If inactive for 3 days, call. |
| ROI is too small to justify price | Medium | High | Focus on pricing decisions first (highest ROI). If < $2K/mo, adjust pricing or features. |
| Integration gaps (missing tool) | Medium | Medium | Offer to build any missing integration as part of pilot (2-3 day effort). |
| Founder doing too much support | High | Medium | Engineer #2 hired in week 10 to offload development. Founder handles support. |
| Pilot churns after 1 month | Expected | Medium | Accept 1-2 churns. Replace with new pilots. 3 loyal customers out of 5-6 attempts is success. |

### Cost: $3K/mo (infra) + $8K/mo (engineer #2 salary) + $500/mo (misc)

---

## 5. Phase 3: Launch (Weeks 13-16)

### Goal: 10 paying customers, iterate on pilot feedback, add integrations, validate the model.

### What's Built

| Week | Deliverable | Details | Dependencies |
|------|------------|---------|-------------|
| 13 | **Pilot feedback analysis** | Compile all feedback from 3 pilots. Prioritize: must-fix bugs, must-have features, nice-to-haves. | Phase 2 |
| 14 | **Top 5 fixes/improvements** | Based on pilot feedback. Likely: entity resolution tuning, better decision deduplication, more vertical-specific calibration. | Week 13 |
| 15 | **5 more integrations** | Xero, Square, Mailchimp, Meta Ads, Google Ads (via Merge.dev). Broader TAM for customer acquisition. | Phase 1 pipeline |
| 16 | **Customer 4-10 onboarded** | Use improved onboarding flow. Target: 7 new customers (3 pilots + 7 new = 10 total). | Week 15 |

### Additional Technical Work

| Feature | Priority | Effort | Why |
|---------|----------|--------|-----|
| Multi-variable simulation (v2) | P1 | 3 weeks | "What if prices +10% AND add Saturday hours?" |
| Anomaly detection agent (Merlion) | P1 | 2 weeks | Autonomous detection without manual monitoring rules |
| Data quality dashboard | P1 | 1 week | Customer-facing: "Your data health is 87%" |
| Knowledge base / docs | P1 | 2 weeks | Self-serve support: "How to connect Xero" |
| Slack integration (push alerts) | P2 | 1 week | Where SMB owners actually work |
| Implemented-action tracking | P1 | 2 weeks | Auto-detect if owner acted (e.g., price changed in Stripe) |

### Customer Acquisition (4-10)

| Channel | Expected Conversions | Cost per Conversion |
|---------|--------------------|--------------------|
| Founder outbound (warm intros) | 3-4 | $1,000 (time) |
| Pilot referrals | 1-2 | $200 (referral discount) |
| Content (case study from pilot) | 1-2 | $500 (content production) |
| Dental industry forums | 0-1 | $0 |

### Success Criteria

- [ ] 10 paying customers, < 8% monthly churn
- [ ] MRR: $8,000-10,000 (mix of tiers)
- [ ] Time-to-value: < 3 days (from signup to first insight)
- [ ] Feedback positive rate: > 60% of decisions marked "useful"
- [ ] At least 3 customers claim > $5K/mo in ROI
- [ ] First vertical-specific tuning: dental practice causal model is measurably better than generic
- [ ] No SEV-1/2 incidents in 30 days

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Scaling support to 10 customers | Medium | High | Hire CS #1 (part-time) in week 14. Build knowledge base. |
| Integration quality issues | Medium | Medium | Monitor integration health dashboard daily. Fix top issues. |
| Pricing too low for value | Medium | Medium | Raise prices for new customers. Test $600/$1,400/$3,000 for customers 11+. |
| Causal model still not accurate | Medium | High | Be transparent: "Estimated — not yet verified." Focus on improving with more data. |
| Competitor launches similar product | Low | High | Don't panic. Our data moat (entity resolution, causal models) takes months to replicate. |

### Cost: $5K/mo (infra) + $16K/mo (2 engineers) + $2K/mo (CS, part-time) + $1K/mo (marketing)

---

## 6. Phase 4: Growth (Weeks 17-24)

### Goal: 30+ customers, vertical expansion, self-serve onboarding, validate unit economics.

### What's Built

| Week | Deliverable | Details | Dependencies |
|------|------------|---------|-------------|
| 17 | **Self-serve onboarding v1** | Reduce onboarding time from 4 hours to 1 hour. Automated integration setup, calibration survey, data quality check, first insight delivery. | Phase 3 improvements |
| 18 | **Home services vertical expansion** | Add ServiceTitan/Housecall Pro integration (via Merge.dev). Home services causal template (seasonal demand, field scheduling, truck roll efficiency). | Phase 3 integration pipeline |
| 19 | **Customer 11-20 onboarded** | Mix of dental + home services. Test if home services market is viable. | Week 18 |
| 20 | **Decision module marketplace v1** | Framework for third-party decision modules. First 2 modules: "Dental Capacity Optimizer," "Home Services Route Planner." | Week 18 |
| 21 | **Customer 21-30 onboarded** | Target: 30 paying customers. Experiment with paid acquisition ($2K/mo Google Ads). | Week 20 |
| 22 | **Infrastructure hardening** | Multi-VM deployment (Docker Compose split across 3-4 VMs). GPU upgrade (2× A100). PgBouncer. Read replicas. | Phase 3 architecture |
| 23 | **Partner program launch** | 3 referral partners onboarded. Referral fee structure live. Partner portal (basic). | Week 22 |
| 24 | **Month 6 review + funding prep** | Prepare investor materials. 6-month retrospective. Plan for months 7-12. | All |

### Key Decisions at Month 6

| Decision | Options | How We Decide |
|----------|---------|---------------|
| **Raise seed round?** | Yes / No / Bootstrap longer | If MRR > $30K and growth > 15% MoM, raise. If < $15K MRR, delay. |
| **Double down on dental vs. expand?** | Stay dental / Expand to 2nd vertical / Expand to 3rd | If dental cohort has > 80% retention and $2K+ MRR/customer, dominate dental. Otherwise, test other verticals. |
| **Hire sales vs. keep founder-led?** | Hire sales / Stay founder-led | If pipeline > 50 leads and conversion rate > 20%, hire sales. Otherwise, founder keeps selling. |
| **Self-hosted LLM vs. API?** | Continue self-host / Switch to API / Hybrid | Compare cost per decision. If self-hosted < $0.02/decision and API > $0.05, stay self-hosted. |

### Success Criteria

- [ ] 30+ paying customers across 2 verticals (dental + home services)
- [ ] MRR: $30,000-50,000
- [ ] Gross margin: > 75%
- [ ] Churn: < 5% monthly
- [ ] NRR: > 110%
- [ ] Self-serve onboarding: 50% of new customers onboard without human help
- [ ] 3+ referral partners generating leads
- [ ] 2 case studies published with named customers (or anonymized if preferred)
- [ ] Seed fundraise started (if appropriate)

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Growth stalls at 15-20 customers | Medium | Critical | Deep-dive into why. Is it product, pricing, or distribution? Pivot accordingly. |
| Home services vertical doesn't work | Medium | Medium | Cut losses. Focus on dental until we find a clear second vertical. |
| LLM costs balloon | Medium | Medium | Tighten tiered routing. Push more to 8B model. Re-negotiate GPU pricing. |
| Team friction (2-3 people) | Medium | Medium | Weekly 1:1s, clear ownership, written culture doc. |
| Running out of cash | Low | Critical | Keep burn low. Bootstrap as long as possible. Raise only when metrics justify it. |

### Cost: $8K/mo (infra) + $30K/mo (team of 4) + $3K/mo (marketing + sales) + $2K/mo (misc) = $43K/mo

---

## 7. Rollout Plan Summary

```
Phase 0: Foundation (Weeks 1-4)
  Budget: $2,300
  Team: 1 founder + 1 contractor
  Outcome: Stripe connected, data flowing, auth working

Phase 1: Alpha (Weeks 5-8)
  Budget: $700
  Team: 1 founder
  Outcome: 5 integrations, 5 decisions, working dashboard

Phase 2: Beta (Weeks 9-12)
  Budget: $11,500/mo
  Team: 1 founder + 1 engineer
  Outcome: 3 pilots, real feedback, usage patterns

Phase 3: Launch (Weeks 13-16)
  Budget: $24,000/mo
  Team: 2 engineers + 1 part-time CS
  Outcome: 10 customers, refined product, validated model

Phase 4: Growth (Weeks 17-24)
  Budget: $43,000/mo
  Team: 3 engineers + 1 CS + 1 founder
  Outcome: 30 customers, 2 verticals, ready for seed
```

**Total cash required for 24 weeks:** ~$150K (including salaries, infra, and all costs). This is bootstrap-friendly if the founder has runway. If not, a pre-seed of $500K-750K provides 12-18 months of runway to reach 50+ customers.

---

## 8. Post-Roadmap: Months 7-12

After the 24-week roadmap, the next priorities are:

| Quarter | Priority | Goal |
|---------|----------|------|
| Q3 (mo 7-9) | Scale to 100 customers | $100K MRR, dominate dental vertical, 3 verticals total |
| Q3 (mo 7-9) | SOC 2 Type I | Unlock enterprise customers |
| Q4 (mo 10-12) | Decision marketplace live | Platform flywheel begins |
| Q4 (mo 10-12) | Embed API v1 | Partner distribution channel |
| Q4 (mo 10-12) | Series A raise | $4M for 18 months of hyper-growth |

---