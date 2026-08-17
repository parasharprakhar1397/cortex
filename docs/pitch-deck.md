# Cortex Investor Pitch Deck Outline

> *Revision 1 — Founding Systems Architect*
> *For pre-seed and seed fundraising. Target: $1.5M seed at $8-12M valuation.*

---

## Slide 1: Title

**Cortex — The Autonomous Strategic Brain for Service Businesses**

*Tagline: "A 24/7 COO that connects your tools, finds hidden opportunities, and tells you what to do before you ask."*

- Logo + tagline
- Founder name + title
- "Pre-seed / Seed — Raising $1.5M"

---

## Slide 2: Problem — "SMB Owners Are Flying Blind"

**The narrative:** Millions of service-based businesses (dental, home services, agencies) run on 4-10 SaaS tools — Stripe, QuickBooks, Calendly, HubSpot, Meta Ads, GA4… but none of them talk to each other.

**The pain:**
```
Tool 1: Stripe → "Revenue is down 5% this month"
Tool 2: Calendly → "Bookings are up 12%"
Tool 3: QuickBooks → "Expenses rose 8%"
Tool 4: HubSpot → "22 new leads this week"

Owner: ??? Are we doing well? What do I DO?
```

**Key data points:**
- The average SMB owner spends 4+ hours/week manually cross-referencing reports from different tools
- 67% of small businesses say they don't have a single source of truth for business performance (Source: Intuit 2025 SMB Survey)
- 41% of decisions at $1-20M businesses are made on gut feel (Source: OnDeck SMB Decision Making Study)

**The alternatives suck:**
- **Fractional COO:** $3K-8K/mo, part-time, slow, doesn't scale
- **BI dashboards:** Require data teams, tell you what happened not what to do
- **Vertical SaaS AI:** Only sees within one tool — misses the cross-tool insights

---

## Slide 3: Solution — Cortex

**What it is:** An autonomous strategic decision system that:
1. **Connects** to your existing tools (Stripe, QuickBooks, Calendly, etc.) in minutes via OAuth
2. **Learns** your business — builds a living model of your customers, revenue, operations, and causal relationships
3. **Surfaces** the highest-impact decisions automatically, with estimated ROI and confidence
4. **Simulates** "what if" scenarios so you see outcomes before you act

**Demo flow (3 decision cards):**
```
Decision 1: [ROI: $12K] "Raise hygienist prices 10% — demand is inelastic at 72% utilization"
Decision 2: [ROI: $6K] "Reschedule hygienist #3's Friday block — 3 no-shows in a row"
Decision 3: [ROI: $3K] "Pause Google Ads 'teeth-whitening' — 0.3% conversion, 2.1% CTR"
```

**Key differentiator — Every decision answers:**
- What happened? → Evidence
- Why did it happen? → Causal analysis
- What should I do? → Actionable recommendation
- What's the ROI? → Dollar estimate with confidence range

---

## Slide 4: Product Demo (Screenshots/Video)

Show 3 screen states (can be mockups for early pitch):

**1. Dashboard:** Metrics (Revenue YTD +14%, Utilization 72% +3%, Churn Risk 4.2% -0.3%) + Today's top 3 decisions

**2. Decision Card (expanded):**
```
Header: "Raise hygienist prices 10% — demand is inelastic"
ROI: $12,000 (80% CI: $4,200 - $19,100) | Confidence: 82%
Evidence panel: Price elasticity chart, utilization trend, competitor pricing map
Causal trace: "Your utilization is 72% → price increase won't reduce demand much"
Simulation: [See what happens if we raise prices 10%]
Feedback: [✓ Useful] [✗ Not useful] [Implemented]
```

**3. Simulation UI:**
```
"What if I raise prices 10%?"
Revenue Impact: +$11,800 | Profit Impact: +$8,400
Patient Churn: 4-6% | Confidence: ████████░░ 82%
Key drivers: Utilization room (72%), demand elasticity (0.4), competitor pricing (+15%)
```

---

## Slide 5: The Core Technology

**Not an AI wrapper.** This is a vertically-integrated intelligence system.

```
                          CORTEX INTELLIGENCE
┌──────────────────────────────────────────────────────────────┐
│                    DATA → MODEL → DECISIONS                    │
│                                                               │
│  1. CONNECT                                                    │
│     + Stripe, QuickBooks, Calendly, HubSpot, GA4...           │
│     + OAuth auto-connect, no engineering needed                │
│                                                               │
│  2. BUILD LIVING MODEL                                         │
│     + Entity graph: customers, invoices, bookings, campaigns   │
│     + Entity resolution: "Jane Smith" in CRM = "jsmith@..."   │
│     + Causal graph: what drives revenue, churn, utilization    │
│     + Bayesian updating: model improves with every data point  │
│                                                               │
│  3. ANALYZE & RECOMMEND                                        │
│     + Monitoring agent: detects anomalies every 15 minutes     │
│     + Analysis agent: finds root causes via statistical tests  │
│     + Decision agent: generates ranked recommendations         │
│     + Simulation agent: runs "what-if" Monte Carlo scenarios   │
│                                                               │
│  4. IMPROVE                                                    │
│     + Feedback loop: "useful" / "not useful" / "implemented"   │
│     + Outcome tracking: predicted vs. actual ROI               │
│     + Cross-customer learning: privacy-preserving benchmarks   │
└──────────────────────────────────────────────────────────────┘
```

---

## Slide 6: Market Sizing

**Total Addressable Market (TAM):**
- Service-based SMBs ($1M-$20M revenue) in the US: ~1.2M businesses
- These businesses spend $2K-10K/mo on SaaS tools (4-10 tools each)
- Average addressable spend on analytics/decisions: $500-2,500/mo

```
TAM: $1.2M businesses × $1,200/yr avg = $17.3B/yr (US only)
SAM: $1.2M × 30% (addressable with our integration set) × $1,200 = $4.3B/yr
SOM: 30,000 customers (2.5% penetration) = $432M/yr
```

**Vertical depth:**
| Vertical | # of SMBs | Target Penetration | Revenue Potential |
|----------|----------|-------------------|-------------------|
| Dental practices | 120,000 | 5% = 6,000 | $86M/yr |
| Home services | 500,000 | 1% = 5,000 | $72M/yr |
| Agencies/Consulting | 300,000 | 1% = 3,000 | $43M/yr |
| Allied Health | 200,000 | 1% = 2,000 | $29M/yr |

---

## Slide 7: Target Customer & Traction

**Ideal customer profile:**
- Service-based SMB, $1M-20M revenue
- Currently uses 4+ SaaS tools
- Owner spends 4+ hours/week on operational reporting
- Has tried (or wants to try) a fractional COO
- Monthly pain: revenue leakage from no-shows, bad pricing, or marketing waste

**Traction (at time of fundraise — update with real numbers):**

| Metric | Current | Target (6 months) | Target (12 months) |
|--------|---------|-------------------|--------------------|
| Paying customers | 3 pilots | 30 | 100 |
| MRR | $2,400 | $30K+ | $120K+ |
| Gross margin | 60% | 75% | 83% |
| Churn (monthly) | 0% (too early) | < 8% | < 5% |
| Avg integrations/customer | 4.2 | 5.5 | 6.5 |
| NPS | 45 | 40+ | 45+ |

---

## Slide 8: Business Model

**Revenue model:**
| Tier | Price | Target Customer |
|------|-------|----------------|
| Essentials | $500/mo | $1-3M revenue, single location |
| Professional | $1,200/mo | $3-10M, multi-location |
| Enterprise | $2,500/mo | $10-20M, custom needs |

**Onboarding fee:** $2K-5K one-time (integration setup + calibration)

**Unit economics (at 100 customers):**
| Metric | Value |
|--------|-------|
| Blended ARPU | $1,000/mo |
| Blended COGS | $200/customer/mo |
| Gross margin | 80% |
| CAC (blended) | $1,200 |
| Payback period | 1.2 months |
| LTV (3yr) | $31,680 |
| LTV:CAC | 26:1 |

**Expansion revenue:**
- Tier upgrades (30% upgrade rate in 12 months)
- Decision module marketplace (70/30 rev share, v3)
- Team seat add-ons ($100/mo per seat)
- Simulation credits beyond tier limit

---

## Slide 9: Competitive Landscape

```
                    PROACTIVE (surfaces decisions)
                         │
                         │
                  ● Cortex (cross-tool, causal)
                         │
                         │
  VERTICAL SaaS ─────────┼────────────────────── GENERAL BI
  (ServiceTitan,         │                    (Tableau, Domo,
   Mindbody, Jane)       │                     Metabase)
                         │
                         │
                  ● AI Chatbots (ChatGPT, Claude)
                  ● Platform AI (HubSpot, Klaviyo)
                         │
                    REACTIVE (answers questions)
```

**Our unfair advantages:**
1. **Cross-tool data:** Only system that connects CRM + accounting + booking + payments + marketing
2. **Causal AI:** Correlation finds patterns; causal understanding finds what actually works
3. **Self-improving:** Every decision and feedback makes the model smarter
4. **Data moat:** 500+ causal parameters per business × 1000s of businesses = defensible intelligence

---

## Slide 10: Competitive Moat

| Moat Type | How Cortex Builds It | Time to Build | Sustainability |
|-----------|---------------------|---------------|----------------|
| **Data network effects** | Anonymized benchmarks get better with more customers. "How does my utilization compare to peers?" is network-effected. | 12-18 months | High — data moats are hard to replicate |
| **Causal model library** | 40+ variable causal graphs per vertical, refined across hundreds of customers. Takes domain expertise + data. | 12-24 months | High — requires both data and domain knowledge |
| **Integration infrastructure** | Entity resolution across 10+ tools is non-trivial. We solve it once per customer; competitors start from scratch. | 6-12 months | Medium — can be copied with enough engineering effort |
| **Decision pattern library** | Hundreds of vetted decision patterns with known ROI. "Pricing optimization for dental practices" with 82% success rate. | 18-24 months | Medium-High — comes from customer feedback data |
| **Switching costs** | Customer has 6 months of integrated data, calibrated models, proven ROI. Losing that is painful. | 6 months | High — time-based moat |

---

## Slide 11: Team

**Current:**
- **Founder (CTO):** [Name], [background — e.g., "Ex-Engineer at X, built Y, sold Z. Previously built data platforms at scale."]
- *1-2 engineers joining by close*

**Planned hires (with funding):**
| Role | Timeline | 
|------|----------|
| Engineer #2 (full-stack) | Month 1 |
| Engineer #3 (backend/data) | Month 3 |
| CS/Onboarding specialist | Month 3 |
| AI/ML engineer | Month 6 |
| Sales #1 | Month 9 |
| Marketing #1 | Month 9 |

**Advisors:**
- [Name] — Former CTO of [SaaS company], experience scaling from 0 to $10M ARR
- [Name] — Domain expert in dental / home services operations
- [Name] — AI/ML professor or senior researcher (causal inference expertise)

---

## Slide 12: Ask

**Raising:** $1.5M seed

**Use of funds:**

| Category | Amount | Detail |
|----------|--------|--------|
| Engineering (4 hires) | $720K/yr | 4 engineers × $180K (loaded) |
| GTM (1 sales + 1 marketing + 1 CS) | $360K/yr | 3 non-engineering × $120K loaded |
| Infrastructure & GPU | $180K/yr | $15K/mo for compute, DB, GPU |
| Marketing & sales budget | $120K/yr | Content, ads, events, partner program |
| Legal, compliance, accounting | $60K/yr | SOC 2 prep, legal, DPA work |
| Founder salary | $60K/yr | $60K (below market — committed) |
| **Total 18-month runway** | **$1.5M** | |

**Milestones to next round (Series A):**
| Milestone | Target |
|-----------|--------|
| Customers | 100 paying |
| MRR | $120K+ |
| Gross margin | 80%+ |
| Churn (monthly) | < 4% |
| LTV:CAC | > 5:1 |
| Vertical dominance | 1 vertical (dental) with > 5% market share |
| SOC 2 Type II | Complete |
| Decision marketplace | 5+ third-party modules live |

---

## Slide 13: Appendix — Technical One-Pager

*For technical investors — one-slide summary of architecture depth.*

**Architecture stack:**
| Layer | Stack |
|-------|-------|
| Backend | FastAPI (Python 3.12, async) |
| Database | PostgreSQL 16 + pgvector + TimescaleDB |
| Queue/Events | Redis + Celery + NATS JetStream |
| LLM Inference | Self-hosted vLLM (Llama 3 70B + 8B), GPT-4o fallback |
| Agents | LangGraph (multi-agent supervisor pattern) |
| Causal Engine | DoWhy + EconML + custom SCM |
| Embeddings | BGE-M3 (self-hosted, 1024-dim) |
| Frontend | TanStack Start (React + Vite + Tailwind) |
| Infrastructure | Docker Compose → k8s (DigitalOcean) |
| CI/CD | GitHub Actions + Docker |

**Key design decisions:**
- **Schema-per-tenant** isolation for customer data (not row-level — absolute boundaries)
- **Self-hosted LLM** (not API-only) because at 1,000 customers × 50 decisions/day, API cost is $1,500/day. Self-hosted: $720/day for unlimited inference.
- **Hybrid integration strategy:** Merge.dev for 15+ tools (rapid coverage), native connectors for top 5 (control + custom fields)
- **Causal > correlational:** Correlation-based recommendations fail when conditions change. Causal models understand "what if we intervene?"

**Data flow (5 phases):**
```
SaaS Tools → Ingestion (Daft) → Entity Resolution (fuzzy matching) → 
Business Model Graph (Postgres) → Agent Analysis (LangGraph) → 
Decision Cards (ROI ranked) → Owner Dashboard + Push
```

---

## Full Slide Deck Summary

| # | Slide | Key Message |
|---|-------|-------------|
| 1 | Title | Cortex — Autonomous strategic brain for SMBs |
| 2 | Problem | SMB owners are flying blind with disconnected tools |
| 3 | Solution | Cortex connects, learns, recommends, simulates |
| 4 | Demo | Dashboard, decision cards, simulation |
| 5 | Technology | Not an AI wrapper — vertically integrated intelligence |
| 6 | Market | $17B TAM (1.2M service SMBs) |
| 7 | Traction | 3 pilots, $2.4K MRR, growing |
| 8 | Business Model | $500-2,500/mo + onboarding. 80% GM. 26:1 LTV:CAC |
| 9 | Competition | Only cross-tool, proactive, causal AI system |
| 10 | Moat | Data network effects, causal models, switching costs |
| 11 | Team | Founder ex-[X], building first team |
| 12 | Ask | $1.5M for 18 months to 100 customers, $120K MRR |
| 13 | Appendix | Architecture deep-dive for technical investors |

---