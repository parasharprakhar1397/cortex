# Cortex Founder Review — Critical Assessment

> *Prepared by team lead, 2026-07-15*
> *Not a summary. A challenge to the architecture so you can build a real company.*

---

## 1. The 10 Highest-Risk Assumptions

These are ordered by likelihood × impact — if any of these are wrong, the company dies or pivots hard.

### #1: SMB owners will pay $500–$2,500/mo for software that isn't a person.

The entire pricing model rests on the comparison to a fractional COO ($3K–$8K/mo). But SMB owners don't think in these terms. They pay for software that *does a job* (process payments, send emails, book appointments). Cortex sells *decisions* — a category that doesn't exist in their mental model or budget line item. They've never paid for it before. The "COO replacement" framing is how *we* see the product, not how they'll evaluate the purchase. This assumption is untestable until someone outside the founder's network pulls out a credit card.

### #2: Entity resolution across 5+ tools can be automated to acceptable accuracy.

The architecture treats entity resolution as a pipeline stage. In reality, matching "Jane Smith" across Stripe (email only), QuickBooks (name + company), Calendly (name + email), HubSpot (email + phone), and GA4 (anonymous) is the hardest problem in the system — and the one everything else depends on. A 15% error rate in entity matching cascades into wrong LTV, wrong churn risk, and wrong pricing recommendations. The docs mention fuzzy matching + graph resolution but don't specify accuracy targets. The cold-start problem is real: in the first 30 days, resolution confidence will be low, and the system will make bad matches that take weeks to detect.

### #3: Causal inference on SMB data will produce reliable, actionable ROI estimates.

DoWhy + EconML is the right architecture aspirationally, but causal inference requires: controlled variation (A/B test conditions), sufficient sample sizes, and well-understood confounders. An SMB with 200 customers and 1 year of data has none of these. The "causal graph templates" (40–80 variables per vertical) will produce wide confidence intervals for months, maybe years. The risk is that decision cards show "ROI: $12K (confidence: 35%)" and owners stop trusting the system.

### #4: The founder can build Phase 0–1 alone in 8 weeks.

The roadmap assigns 8 weeks for one person to: scaffold FastAPI + Docker + CI/CD, build PostgreSQL with 3 extensions, implement Clerk auth + multi-tenancy, build 5 native OAuth connectors with webhook handling, build data normalization + entity resolution, assemble the entity graph, derive time-series metrics, build 5 agent roles with LangGraph, generate 5 decision types with ROI estimates, build the dashboard UI with decision cards, implement the feedback loop, and add a morning digest email. This is a full-time job for 3–4 experienced engineers for 12 weeks, not one person for 8. The timeline assumes zero debugging, zero integration fires, and zero learning curve.

### #5: Self-hosted Llama 3 70B will be cheaper and reliable enough for v1.

The architecture bets heavily on self-hosted vLLM with 1× A100 at $1,500/mo. But: (a) Vast.ai GPU availability is spotty — you bid for capacity and can lose it mid-training, (b) operating vLLM in production adds non-trivial DevOps (model loading, memory management, request queuing), (c) at 50 customers × 10 decisions/day × multiple agent calls, you'll easily hit capacity limits and need a second GPU, and (d) the cost gap vs. OpenAI API narrows significantly when you factor in the engineering time to maintain self-hosted infra. For v1 with 10 customers, the API is simpler, more reliable, and the cost difference is maybe $200/mo — not worth the distraction.

### #6: Dental is the right starting vertical.

The docs argue dental because it's "data-rich" and has "high willingness to pay." But: does the founder have domain expertise or a network in dental? Without it, every pilot conversation starts cold. Dental practices are notorious for being tech-averse and price-sensitive. They also have HIPAA-adjacent data (patient health information in practice management systems) that complicates everything. The vertical should be wherever the founder already has relationships and credibility.

### #7: Merge.dev will solve the integration problem.

Merge.dev is a young company (Series B, ~$55M raised). Their connector quality varies dramatically — some are production-grade, some are thin wrappers that miss 40% of the fields we'd need. Their unified schemas are intentionally generic, which means we lose granularity (e.g., QuickBooks class tracking, Stripe subscription metadata). And they can change pricing or deprecate connectors with short notice. Betting the integration layer on them is reasonable, but the docs treat them as a solved problem when they're a managed risk at best.

### #8: 3 pilots are enough to validate product-market fit.

Three dental practices in the founder's network saying "this is useful" is not PMF. It's friends being polite. Real validation requires: (a) at least one customer from outside the founder's network, (b) renewal after the pilot discount ends, (c) expansion (they add integrations, upgrade tiers), and (d) they'd be "very disappointed" if Cortex disappeared. The 6-month target of 3 pilots is the right *milestone* but it's not *validation* — only a gate to decide if we continue.

### #9: CAC of $2,500 is achievable through founder-led sales.

The monetization doc models CAC at $2,500 for months 1–6. This implies the founder closes a customer for ~$3K of their time. But the founder is also building the entire product, doing customer support, and managing the pilot program. When does the selling happen? The roadmap has no dedicated time for outbound sales in Phase 0–2. The CAC model assumes a sales process that the timeline doesn't accommodate.

### #10: 80%+ gross margins are achievable at scale.

The COGS model shows 83% GM at 50 customers, rising to 85% at 200. But LLM inference costs are highly variable (complex simulations burn tokens), integration costs scale with data volume (more customers = more syncs = more Merge.dev charges), and support costs at 200 customers are likely 2–3× the estimate because SMB owners need hand-holding. If actual COGS is $300–400/customer instead of $200, GM drops to 60–70% — still good, but it changes the fundraise narrative.

---

## 2. Decisions That Require Founder Approval

These are binary choices the architect can't make. Decide before any code is written.

| # | Decision | Options | Architect's Recommendation | Why It Matters |
|---|----------|---------|---------------------------|----------------|
| D1 | **Starting vertical** | Dental vs. Home Services vs. Founder's network vertical | Dental (per docs) | Determines integration priorities, pilot outreach, and product positioning for 6+ months |
| D2 | **LLM strategy for v1** | Self-hosted Llama 3 70B vs. OpenAI API-only vs. Hybrid | Self-hosted (per docs) | Affects infrastructure cost, engineering complexity, and decision quality. Self-hosted saves money at scale but adds 3–4 weeks of v1 engineering |
| D3 | **Causal engine timing** | v1 (per AI arch) vs. v2 (per AI arch note) vs. v3 | v2 (contradiction in docs) | The AI architecture doc has the causal engine in v1's stack, but the architect's own notes recommend deferring to v2. This needs a clear call |
| D4 | **Number of v1 integrations** | 3 vs. 5 vs. 10 | 5 native + Merge.dev | More integrations = broader TAM but slower build. 3 (Stripe, QB, Calendly) would ship faster |
| D5 | **Pilot discount vs. full price** | 30% discount (per monetization) vs. Free pilot vs. Full price from day 1 | 30% discount | "Revenue is secondary to validation" per the owner — so why charge at all for pilots? Charging filters for commitment but slows recruitment |
| D6 | **Funding path** | Bootstrap to 30 customers then raise vs. Raise pre-seed now vs. Raise seed at 10 customers | Bootstrap to 30 (per roadmap) | Determines founder salary, hiring timeline, and whether we optimize for speed or runway |
| D7 | **Onboarding fee for Essentials** | $0 vs. $2,000 | Contradiction in docs — monetization says both | Free onboarding removes a friction point; paid onboarding signals commitment and recovers cost |
| D8 | **First hire timing** | Month 3 (per roadmap) vs. Month 6 vs. When revenue permits | Month 3 (hire engineer #2) | Hiring before the product works creates pressure to keep someone busy. Hiring too late burns out the founder |

---

## 3. Contradictions Between Architecture & Business Documents

These are not disagreements — they're factual inconsistencies that would confuse an investor or engineer.

### Contradiction 1: Onboarding Fee for Essentials
- **`monetization.md` line 17:** "No setup fee for Essentials tier" (pricing principle #4)
- **`monetization.md` line 62:** "$2,000" onboarding fee for Essentials
- **Impact:** Which is it? If you tell a pilot "no setup fee" and then invoice $2K, you lose trust. Fix: pick one.

### Contradiction 2: Infrastructure Cost in Roadmap vs. Infrastructure Doc
- **`roadmap.md` Phase 1:** "$500/mo infra (GPU + compute)"
- **`infrastructure.md`:** DigitalOcean $400–600 + Vast.ai GPU $1,500–2,000 = **$1,900–2,600/mo**
- **Impact:** The roadmap understates infrastructure costs by ~4× in Phase 1. The actual burn rate is higher.

### Contradiction 3: Team Size Projections
- **`roadmap.md`:** "Team size: 1 (founder) → 2 → 3 → 4" for 24 weeks
- **`hiring-roadmap.md`:** Shows Engineer #3 and CS #1 hired at month 6 (week 24), Engineer #4 at month 9 — that's 5 people by month 9, not 4 in 24 weeks
- **Impact:** The roadmap summary undercounts headcount. Budget projections are off by ~$200K/year.

### Contradiction 4: GPU Security Model
- **`security-compliance.md`:** "LLM model weights: Plaintext (inside secure enclave)"
- **`infrastructure.md`:** Uses Vast.ai for GPU — a spot market where you share physical hardware with other tenants. Not a secure enclave.
- **Impact:** If you tell enterprise customers or SOC 2 auditors the models run in a secure enclave, and they're actually on Vast.ai, that's a material misrepresentation.

### Contradiction 5: Causal Engine in v1 vs. v2
- **`ai-architecture.md`:** The causal inference engine (DoWhy + EconML) is in the Tier 2 (Deep Path) stack, which is part of the v1 architecture
- **`system-architecture.md` (architect's own notes in report):** "Recommend starting with simpler statistical methods in v1 and adding causal in v2"
- **Impact:** This is the biggest technical "what are we actually building?" question. The causal engine is the core differentiator. Either it's in v1 or it isn't. Pick.

### Contradiction 6: "First Insight Immediate" Claim
- **`product-strategy.md`:** "First insight (immediate) — Cortex surfaces the first decision card"
- **`data-pipelines.md`:** Initial sync takes 2–30 minutes, plus normalization, entity resolution, and model building
- **Impact:** If an owner signs up and doesn't see a decision card for 2 hours, the "immediate" promise is broken out of the gate.

### Contradiction 7: Growth Rate Assumptions
- **`monetization.md`:** "10% month-over-month growth" after launch
- **`roadmap.md`:** Phase 3 (4 weeks): 3→10 customers (233%). Phase 4 (8 weeks): 10→30 customers (200%). These are 33–58% monthly growth rates.
- **Impact:** The roadmap growth targets are 3–6× faster than the financial model assumes. If you hit the roadmap targets, the financials are too conservative. If you hit the financial targets, you missed the roadmap.

---

## 4. Top 5 Technical Risks

### TR1: Entity Resolution Quality (Critical)
If the system can't reliably match customers across tools, every downstream decision is suspect. Mitigation: start with exact email match only (the architect suggests this in the roadmap risks), add fuzzy matching later, and display "confidence: low" on entity matches. But be prepared for this to be the #1 source of customer complaints for 6+ months.

### TR2: Integration Fragility (High)
SaaS APIs change, OAuth tokens expire, rate limits trigger, Merge.dev has outages. In v1 with 5 integrations, each is a potential point of failure. The architecture has health checks and auto-healing, but in practice, integration maintenance will consume 20–30% of engineering time indefinitely. This is not a "build once" problem.

### TR3: Agent Hallucination in Decision Cards (High)
LLMs generating business advice will occasionally produce confident-sounding nonsense. The guardrails in `agents.md` (pre-generation + post-generation checks) are a good start, but they won't catch subtle errors like "recommend raising prices 10%" when the supporting data actually shows prices should go *down*. Mitigation: every decision card must be traceable to a statistical test result, not just an LLM output. The LLM should *format and explain* but never *originate* the quantitative claim.

### TR4: GPU Inference Reliability (Medium)
Self-hosted vLLM on Vast.ai means: spot instance preemption, cold starts when a GPU is allocated, CUDA version mismatches, and no SLA. If the inference layer goes down, agent cycles fail silently and owners get no decisions. Mitigation: OpenAI API as always-on fallback with automatic failover. This is in the architecture but must be tested continuously.

### TR5: Database Migration at Scale (Medium)
Schema-per-tenant means running Alembic migrations across 50+ schemas. One failed migration on schema #37 leaves the system in an inconsistent state. The architecture doesn't address migration failure recovery for multi-schema deployments. Mitigation: wrap migrations in per-schema transactions, implement pre-migration dry runs, and test rollback on every deploy.

---

## 5. Top 5 Business Risks

### BR1: No Budget Category for "Strategic Decision Software"
SMB owners budget for: payments, accounting, CRM, marketing, payroll. They do not budget for "autonomous strategic advisor." Cortex is creating a new category, which means every sale is an education sale — the hardest kind. Mitigation: don't sell "strategic advisor." Sell a specific, instantly understandable value: "Cortex finds $10K+ in missed revenue every month." Lead with the outcome, not the product.

### BR2: Founder Bottleneck (Critical for 6–12 months)
One person doing product, engineering, and sales means everything is gated on one person's time, energy, and context-switching capacity. The roadmap acknowledges this as a risk but doesn't mitigate it — the plan *relies* on the founder doing everything for 8 weeks. Mitigation: ruthlessly descope v1. 3 integrations, not 5. 3 decision types, not 5. OpenAI API, not self-hosted LLM. Buy every non-core component (Clerk for auth, Merge.dev for integrations). The founder's time is the scarcest resource.

### BR3: Pilot Churn Masking Real Demand (Medium)
30% monthly churn in the pilot phase is "expected," per the monetization doc. But if 3 customers become 2 by month 4, and the founder has to recruit replacements, the validation story weakens. Mitigation: over-recruit pilots (target 5–6 to end with 3). Accept that some will leave and don't treat it as failure — treat it as data on who stays and why.

### BR4: Vertical Lock-In (Medium)
If you build the entire v1 product around dental (dental-specific causal templates, dental integration packs, dental case studies), and dental turns out to be the wrong vertical, you've built 6 months of the wrong thing. Mitigation: keep the v1 product vertical-agnostic. Add dental-specific tuning in v1.1, not v1.0. The core decision types (pricing, churn, cash flow, no-show, booking gap) apply to any service business.

### BR5: Competition from Vertical SaaS (Medium, Long-Term)
Jane App, Mindbody, and ServiceTitan already have their customers' data. If any of them adds cross-tool AI recommendations, they have distribution that Cortex can't match. The defense is: (a) they're locked into their own ecosystem, (b) they don't want to integrate competitors' tools, and (c) our data moat grows with every customer. But this is a race — Cortex needs enough customers and enough data to be defensible before the vertical SaaS players wake up.

---

## 6. Prioritized MVP Implementation Order

If the goal is 3 paying pilots in 6 months with measurable business improvement, here's what to build and in what order. This replaces the roadmap in `roadmap.md` — it's more aggressive about descoping and more realistic about founder bandwidth.

### Phase 0: Skeleton (Weeks 1–2)
Build only what's absolutely necessary to connect one tool and show one insight.

| Week | Build | Don't Build |
|------|-------|-------------|
| 1 | FastAPI scaffold, Docker, GitHub Actions CI, Clerk auth, PostgreSQL (no pgvector, no TimescaleDB yet) | No multi-tenancy, no agents, no UI, no Merge.dev |
| 2 | Stripe connector only (OAuth + batch sync + webhook), raw data → Postgres, one dashboard endpoint: "connected, X invoices synced" | No entity resolution, no normalization layer, no other integrations |

**Deliverable:** A system that connects to Stripe and shows invoice count. That's it. Ship it.

### Phase 0.5: First Insight (Weeks 3–4)
Show one decision card, even if it's simple.

| Week | Build | Don't Build |
|------|-------|-------------|
| 3 | Add QuickBooks connector, basic normalization (map Stripe + QB to shared customer table), exact email match for entity resolution | No fuzzy matching, no Calendly, no agents yet |
| 4 | One decision type: "Revenue trend" — a simple time-series comparison with a plain-language summary. Hardcoded decision template. Dashboard UI with one decision card. | No ROI estimates, no simulation, no causal engine, no multi-agent system |

**Deliverable:** A system that connects Stripe + QuickBooks, matches customers by email, and shows "Your revenue is up/down X%. Here's a breakdown." This is NOT the final product — it's a learning instrument.

### Phase 1: Core Loop (Weeks 5–8)
Now add the feedback loop and a few more integrations.

| Week | Build | Don't Build |
|------|-------|-------------|
| 5 | Calendly connector, add booking data to entity graph, expand entity resolution (name + email fuzzy matching for Calendly ↔ Stripe/QB) | No agents yet |
| 6 | Add 2 more decision types: "No-show risk" (Calendly patterns), "Booking gap" (upcoming schedule vs. historical). All decisions are SQL + statistical test → LLM formats explanation. OpenAI API only. | No self-hosted LLM, no LangGraph, no causal engine |
| 7 | HubSpot connector, add contact/deal data, third decision: "Churn risk" (declining engagement). Feedback loop (✓/✗/implemented). | No GA4 yet |
| 8 | Morning digest email, simple simulation: "What if I change X by Y%?" using basic elasticity calculation (no Monte Carlo). | No multi-agent, no monitoring agent |

**Deliverable:** 4 integrations, 4 decision types, feedback loop, morning digest. All decisions use simple statistics + LLM formatting. This is the MVP.

### Phase 2: Pilots (Weeks 9–12)
Onboard 3 pilots, iterate on their feedback, fix what breaks.

**Do:**
- Recruit 5–6 pilot candidates (expect 3 to stay)
- White-glove onboarding: founder does setup personally
- Fix bugs within 24 hours
- Weekly check-in calls
- Track: daily usage, feedback rate, decisions implemented, ROI claimed

**Don't:**
- Build new features during pilot phase unless a pilot explicitly asks and it's blocking their usage
- Add integrations unless a pilot needs it
- Optimize performance unless it's visibly broken
- Write documentation (founder handles support)

### Phase 3: Launch Prep (Weeks 13–16)
Based on pilot feedback, determine the top 3 improvements and build only those. Add 2–3 more customers.

---

## 7. What Should Be Simplified Before Building

These are cuts I recommend before a single line of code is written:

### Cut #1: Self-hosted LLM → OpenAI API (for v1)
**Why:** Managing vLLM, GPU instances, model loading, and failover is a 3–4 week distraction when you're the only engineer. At 3–10 customers, OpenAI API costs maybe $200–400/mo. The cost savings of self-hosting don't materialize until 50+ customers. Switch to self-hosted in Phase 3 when you have an engineer to manage it.

### Cut #2: 5-Agent System → 2 Agents (for v1)
**Why:** The Monitoring, Analysis, Decision, Simulation, and Supervisor agents in LangGraph are elegant architecture but too complex for v1. Start with: (a) a **Scheduler** (cron-like, runs decision checks on a timer), and (b) a **Decision Engine** (statistical test → LLM formatting → decision card). You don't need LangGraph yet — a simple Celery task chain works. Add the multi-agent system in v2 when you have more decision types and need parallelism.

### Cut #3: Causal Inference Engine → Defer to v2
**Why:** DoWhy + EconML requires controlled data, domain expertise, and careful validation. In v1, "ROI estimates" can be simple: "Based on your utilization rate (72%) and the average price elasticity in your market (0.4), a 10% price increase would yield approximately +$8K–12K in annual revenue." This is a formula, not a causal model, and it's good enough. Label it "Estimated — not yet verified" and improve it over time.

### Cut #4: 5 Integrations → 3 for MVP (Stripe, QuickBooks, Calendly)
**Why:** These three cover revenue, expenses, and operations — the minimum dataset for meaningful decisions. HubSpot and GA4 add marketing analytics but require more complex normalization and produce lower-ROI decisions in v1. Add them in Phase 3.

### Cut #5: TimescaleDB + pgvector → Plain Postgres (Week 1–4)
**Why:** You don't need hypertables when you have 100 rows. You don't need vector embeddings when you have no agents doing semantic search. Add extensions when the data volume and query patterns demand them — probably around Week 6–8. Start with plain Postgres tables.

### Cut #6: Drop the Marketplace, Benchmarks, and Multi-Vertical from the 6-Month Plan
**Why:** These are v2/v3 features that appear in the roadmap and monetization docs as if they're part of the plan. They're not. For the first 6 months, the only goal is: 3 pilots, measurable ROI, validation. Everything else is a distraction.

### Cut #7: Simulation Engine → Simple "What-If" Calculator
**Why:** Monte Carlo simulation with uncertainty quantification is impressive but owners don't need it in v1. They need: "If I raise prices 10%, here's the projected impact based on your current data." A simple formula with a confidence band (pre-computed, not simulated) is enough. Build the simulation engine when you have enough data to validate its predictions.

---

## Summary: The Simplest Thing That Could Work

Here's what Cortex v1 actually needs to ship:

| Component | Full Architecture Says | Simplified v1 |
|-----------|----------------------|---------------|
| LLM | Self-hosted Llama 3 70B + 8B + GPT-4o fallback | OpenAI API (GPT-4o-mini for routine, GPT-4o for complex) |
| Agents | 5-agent LangGraph system | 2-function Celery task chain (Scheduler + Decision Engine) |
| Causal Engine | DoWhy + EconML + custom SCM | Simple formulas + statistical tests + "Estimated" label |
| Database | PostgreSQL + TimescaleDB + pgvector | PostgreSQL (add extensions as needed) |
| Integrations (v1) | 5 native + Merge.dev | 3 native (Stripe, QuickBooks, Calendly) |
| Decision Types | 5 | 4 (revenue trend, no-show risk, booking gap, churn risk) |
| Simulation | Monte Carlo with uncertainty | Formula-based calculator with pre-computed bands |
| Infrastructure | Docker Compose + Vast.ai GPU | Docker Compose + OpenAI API (no GPU) |
| Multi-tenancy | Schema-per-tenant | Schema-per-tenant (keep this — it's simple enough) |
| UI | Full dashboard + simulation + settings | Dashboard + decision cards + feedback buttons |

**Build time with 1 founder:** 8–10 weeks to MVP (not 4), 12–14 weeks to pilots.

**Monthly infra cost at 3–10 customers:** $500–800 (DigitalOcean + OpenAI API).

**The test:** If 3 pilots use this simplified version weekly and can point to real money saved or earned, you have validation. Then — and only then — add the causal engine, the multi-agent system, the self-hosted LLM, and the marketplace. Build the impressive architecture after you've proven the simple one works.
