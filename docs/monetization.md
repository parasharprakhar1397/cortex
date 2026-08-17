# Cortex Monetization & Pricing Strategy

> *Revision 1 — Founding Systems Architect*
> *For investors, pricing decisions, and unit economics modeling*

---

## 1. Pricing Philosophy

Cortex prices on **value delivered**, not cost-plus or competitor-matching. Every SMB owner we target spends $3K–$10K/mo on a fractional COO or data analyst, or loses $10K–$50K/mo in preventable revenue leakage (no-shows, pricing errors, churn). Cortex delivers comparable insights for 80% less while being always-on and proactive.

**Core pricing principles:**
1. **Price correlates to data complexity** — more integrations = more powerful insights = higher price
2. **Free-forever plan never offered** — SMBs that don't pay don't engage; pilots pay from day 1
3. **Outcome not output** — price for decisions and ROI, not dashboards or data volume
4. **Low friction to start** — month-to-month with annual discount; no setup fee for Essentials tier

---

## 2. Pricing Tiers

| Tier | Monthly Price | Annual (per mo) | Max Integrations | Decision Types | Decisions/Day | Simulation Runs/mo | Best For |
|------|--------------|-----------------|-----------------|----------------|---------------|-------------------|----------|
| **Essentials** | $500 | $450 ($5,400/yr) | 5 | 5 | 3 | 10 | $1-3M, single-location, solo owner |
| **Professional** | $1,200 | $1,080 ($12,960/yr) | 10 | 15 | 10 | 50 | $3-10M, multi-location, small team |
| **Enterprise** | $2,500 | $2,250 ($27,000/yr) | Unlimited | All | Unlimited | Unlimited | $10-20M, custom needs, complex org |

### Justification for Each Price Point

**Essentials ($500/mo):**
- Replaces ~$3K/mo fractional COO input at 1/6 the cost
- Comparable to a single software seat (HubSpot Enterprise, Salesforce) but delivers cross-tool intelligence
- Low enough to be an impulse decision for a $1-3M business ($6K/yr = 0.3% of revenue at $2M)
- High enough to signal value — $50/mo tools don't get used; $500/mo tools get adoption pressure

**Professional ($1,200/mo):**
- The "sweet spot" — covers the bulk of our TAM ($3-10M revenue)
- 10 integrations captures the typical SMB stack (payments + accounting + booking + CRM + marketing + analytics)
- 10 decisions/day = 300/mo = $4 per decision — cheaper than any analyst hour
- Pricing designed so the owner can point to a single recommendation (e.g., "raise prices 10% = $12K") and justify 12 months of subscription

**Enterprise ($2,500/mo):**
- For $10-20M businesses that have 3-5 locations, an admin team, and complex workflows
- Unlimited simulations enable multi-variable what-if analysis for strategic planning
- Custom integrations (e.g., connecting proprietary scheduling or inventory systems)
- Still a fraction of a full-time operations hire ($80-120K/yr fully loaded)

### Grandfathering & Discounts

| Type | Discount | Terms |
|------|----------|-------|
| **Pilot customers** (first 10) | 30% off for 12 months | $350/$840/$1,750 |
| **Annual prepayment** | 10% discount | Billed annually |
| **Non-profit** | 20% discount | Must verify 501(c)(3) |
| **Referral** | 1 month free | Referred customer stays 6+ months |

---

## 3. Onboarding Fee Structure

| Tier | One-Time Fee | What's Covered | Hours of Engagement |
|------|-------------|----------------|-------------------|
| **Essentials** | $2,000 | Integration setup (5 tools), business calibration, 2 training sessions | ~8 hours |
| **Professional** | $3,500 | All integrations, entity resolution tuning, custom metric definition, 3 training sessions | ~15 hours |
| **Enterprise** | $5,000 | Full integration suite, vertical-specific causal model calibration, custom dashboard, 5 training sessions, dedicated Slack channel | ~25 hours |

### Why Charge Onboarding Rather Than Including It

1. **Commitment signal** — a customer willing to pay $2K-5K to set up is serious about adoption
2. **Cost recovery** — a typical onboarding consumes 8-25 engineering/support hours at ~$150/hr blended cost
3. **Resource allocation** — paid onboarding forces us to deliver efficiently; free onboarding encourages scope creep
4. **Churn reduction** — customers who invest in setup have 40%+ lower churn (industry data from B2B SaaS)

### Onboarding Process

```
Week 1: Discovery & Integration
  - Kickoff call (60 min): goals, pain points, current tool stack
  - Integration provisioning: connect tools via OAuth, verify data flow
  - Business profile setup: vertical, revenue range, locations, team size
  - Data quality assessment: report on data completeness and gaps

Week 2: Calibration
  - Historical data sync (up to 2 years back)
  - Entity resolution review: owner verifies customer merging is correct
  - Causal model initialization: load vertical-specific priors
  - Goal setting: owner enters top 3-5 business goals

Week 3: First Insights & Tuning
  - First batch of decision cards delivered
  - Feedback review session (30 min): owner reviews first 10 decisions
  - Preference tuning: suppress unhelpful decision types
  - Simulation demo: run the owner's first "what if"

Month 2: Handoff
  - Last training session: owner is self-sufficient
  - Support moves from onboarding team to CS
  - Success criteria: 3+ decisions acted on per week
```

---

## 4. Unit Economics

### Cost Structure (Monthly per Customer at 100 Customers)

| Cost Category | Essentials | Professional | Enterprise |
|--------------|------------|-------------|------------|
| **Infrastructure** (compute, storage, DB) | $45 | $120 | $350 |
| **LLM inference** (self-hosted vLLM) | $12 | $35 | $80 |
| **Integration costs** (Merge.dev fees) | $3 | $8 | $20 |
| **Customer support** (blended) | $25 | $50 | $100 |
| **Total COGS** | **$85** | **$213** | **$550** |
| **Gross margin** | **83%** | **82%** | **78%** |

Note: Gross margins improve as customer count scales (infrastructure costs sub-linear). At 1,000 customers, target margins of 85-88%.

### CAC Estimates by Channel (First 18 Months)

| Channel | CAC (Blended) | Time to Payback | Notes |
|---------|--------------|-----------------|-------|
| **Founder-led outbound** (months 1-6) | $2,500 | 2.1 months (Essentials) | Founder's time "cost" allocated at $3K/sale |
| **Content/SEO** (months 6-12) | $800 | 0.7 months | Blogs, case studies, comparison pages |
| **Referrals** (months 6+) | $200 | 0.2 months | Viral loop via ROI sharing |
| **Partner channel** (months 9+) | $1,200 | 1 month | Implementation partners, vertical SaaS integrations |
| **Paid acquisition** (months 12+) | $1,800 | 1.5 months | Google Ads + Meta targeted at SMB owners |

### Unit Economics Summary

| Metric | Month 3 | Month 6 | Month 12 | Month 24 |
|--------|---------|---------|----------|----------|
| Customers | 3 | 15 | 50 | 200 |
| Blended ARPU | $1,000 | $1,100 | $1,200 | $1,300 |
| Blended GM % | 75% | 80% | 83% | 85% |
| Blended CAC | $2,500 | $1,800 | $1,200 | $800 |
| Payback period | 3.3 mo | 2.0 mo | 1.2 mo | 0.7 mo |
| LTV (3yr) | $27,000 | $31,680 | $37,440 | $43,200 |
| LTV:CAC ratio | 10.8:1 | 17.6:1 | 31.2:1 | 54:1 |

### Churn Assumptions

| Period | Monthly Gross Churn | Net Revenue Retention |
|--------|-------------------|----------------------|
| Months 1-6 (pilot phase) | 30% (high — expect losses) | 70% |
| Months 6-12 | 8% | 115% |
| Months 12-24 | 4% | 125% |
| Months 24+ | 2% | 130% |

Churn in months 1-6 is high because pilots will churn. That's by design — we want the 3 who stay. After product-market fit, churn drops sharply. Target NRR > 120% by month 12 is aggressive but achievable given upsell from Essentials → Professional as businesses grow.

---

## 5. Expansion Revenue Strategy

### 5.1 Within-Tier Upsells

| Mechanism | Revenue Impact | Trigger |
|-----------|---------------|---------|
| **Integration add-ons** | +$200/mo per 5 integrations beyond tier limit | "You've reached your integration limit. Unlock 5 more for $200/mo." |
| **Additional locations** | +$300/mo per location (Professional/Enterprise) | "Your second location data is flowing. Add multi-location analytics for $300/mo." |
| **Team seats** | +$100/mo per additional user | "Add your office manager to Cortex so they see staffing recommendations." |
| **Simulation credits** | $0.50/run beyond tier limit | "You've used all 10 simulations this month. Need more?" |

### 5.2 Tier Migration Path

```
Essentials ($500/mo)          Professional ($1,200/mo)        Enterprise ($2,500/mo)
┌──────────────────┐          ┌─────────────────────┐         ┌─────────────────────┐
│  • 5 integrations │ ──────►  │  • 10 integrations  │ ──────►  │  • Unlimited        │
│  • 3 decisions/day│  $700   │  • 10 decisions/day │  $1,300  │  • All decisions    │
│  • 10 sims/mo    │  expand │  • 50 sims/mo        │  expand  │  • Unlimited sims   │
│                   │         │  • Multi-location    │          │  • Custom           │
│                   │         │  • Team seats        │          │  • Dedicated CS     │
└──────────────────┘         └─────────────────────┘         └─────────────────────┘
```

Target: 30% of Essentials customers upgrade to Professional within 12 months. Trigger: they add a second location or start asking for integrations beyond 5.

### 5.3 Expansion Through Features (v2/v3)

| Feature | Revenue Model | Launch Timeline | Estimated Uplift per Customer |
|---------|--------------|-----------------|------------------------------|
| **Decision marketplace** | 70/30 rev share with third-party module developers | v3 (mo 8+) | $200/mo avg |
| **Peer benchmarks** | Included in Professional+, standalone $150/mo | v2 (mo 4+) | 10% upgrade rate |
| **Automated actions** | Premium add-on $400/mo | v3 (mo 6+) | $400/mo for power users |
| **White-label embed** | $1,000/mo + $0.50 per end-customer | v3 (mo 10+) | Partner channel |
| **API access** | Metered $0.01/API call | v2 (mo 5+) | Low initially |

---

## 6. Future Revenue Streams

### 6.1 Decision Module Marketplace (v3)

Third-party domain experts build decision modules on Cortex's platform:

```
Marketplace Model:
  • Developer builds module: "Dental Practice Capacity Optimizer"
  • Cortex provides: data pipeline, causal model framework, simulation engine
  • Developer provides: domain-specific patterns, decision templates, calibration
  • Revenue: 70% to developer, 30% to Cortex
  • Price: $100-500/mo per module (set by developer)
  • Cortex vets: quality, ROI accuracy, data privacy compliance
```

**Why developers would build:**
- Access to Cortex's data pipeline (no integration work)
- Existing customer base to sell to (network effect)
- Easy distribution (one-click install from marketplace)
- Higher margins than building their own SaaS

**Why customers buy:**
- Vertical-specific intelligence ("this module was built for dental practices like mine")
- Proven ROI from peer practices

### 6.2 Industry Benchmarks

Anonymized, aggregated data from all Cortex customers creates massive value:

| Product | Description | Price |
|---------|-------------|-------|
| **Standard Benchmarks** | "Your utilization vs. peers" (already included in Pro+) | Included |
| **Deep Benchmarks** | Drill-down by location, revenue tier, staffing mix | $150/mo add-on |
| **Custom Cohort** | Compare against hand-picked peer group | $500/mo |
| **Industry Reports** | Annual "State of SMB Operations" | $2K/report (published) |

Data moat: after 500+ customers, Cortex has the richest operational benchmark dataset in SMB. This is defensible and hard to replicate.

### 6.3 Embedded Cortex (OEM/API)

Vertical SaaS platforms embed Cortex directly:

- **For software vendors** (Jane App, ServiceTitan, Mindbody): embed Cortex-powered insights inside their product
- **Pricing:** $0.50/mo per active end-customer (cheaper than building their own AI)
- **Value to vendor:** differentiated product, reduced churn, potential revenue share
- **Value to Cortex:** distribution at scale, data network effects

### 6.4 Professional Services

| Service | Description | Price | Who Delivers |
|---------|-------------|-------|-------------|
| **Business audit** | Full operational analysis + ROI roadmap | $5K one-time | Founder/CTO |
| **Custom integration** | Connect proprietary/internal tools | $2-10K | Engineering team |
| **Workshop** | "Running your business on data" (half-day) | $3K | Founder/COO-type hire |
| **Retainer advisory** | Monthly strategy call + custom analysis | $3K/mo | Future COO hire |

---

## 7. Competitive Pricing Analysis

### 7.1 vs. Alternatives (Monthly Cost Comparison)

| Solution | Monthly Cost | Annual Cost | What You Get |
|----------|-------------|-------------|--------------|
| **Cortex Essentials** | $500 | $5,400 | 5 integrations, proactive decisions, simulation |
| **Cortex Professional** | $1,200 | $12,960 | 10 integrations, full decision set, multi-location |
| **Cortex Enterprise** | $2,500 | $27,000 | Unlimited, custom, dedicated CS |
| | | | |
| **Fractional COO** | $3,000-8,000 | $36K-96K | Human, part-time, reactive |
| **BI Consultant** | $5,000-15,000 | $60K-180K | Custom dashboards, one-time |
| **Full-time Ops Manager** | $6,000-8,000 | $72K-96K | Employee (salary + benefits) |
| | | | |
| **Tableau/Domo** | $70-150/seat | $840-1,800 | Dashboards only, no recommendations |
| **HubSpot Enterprise** | $1,500/mo | $18,000 | CRM-only AI features |
| **Klaviyo (growth tier)** | $700-1,200 | $8,400-14,400 | Email marketing AI only |
| | | | |
| **ChatGPT Team** | $25/user | $300 | Chat only, no data connections |
| **Vertical SaaS AI add-on** | $200-600 | $2,400-7,200 | Single-tool insights only |

### 7.2 Positioning Map

```
Value:
HIGH ┼──────────────────────────────────────────●──
     │                                        Cortex
     │                                   (1-3 tools analyzed
     │                                    across all domains)
     │
     │                    ● Fractional COO
     │                    (human, expensive, slow)
     │
     │     ● Vertical SaaS AI   ● BI Tools
     │     (single tool,        (data teams required,
     │      limited scope)      reactive only)
     │
     │● AI Chatbots
     │ (no persistent data,
     │  manual uploads)
     │
LOW  ┼─────────────────────────────────────────────
     LOW                                        HIGH
              AUTOMATION / 24/7 AVAILABILITY
```

### 7.3 Cortex Pricing Advantage Over Each Alternative

| Alternative | Why We Win on Price | Why We Win on Value |
|-------------|--------------------|--------------------|
| **Fractional COO** | 4-16x cheaper | Always-on, data-driven, doesn't forget, scales across locations |
| **BI Tools** | 3-17x cheaper | Zero config, proactive decisions, no SQL needed |
| **HubSpot/Salesforce AI** | Equally or less expensive | Cross-tool (not just CRM), simulation engine |
| **Vertical SaaS AI** | 2-4x more expensive but broader | Covers entire business, not just scheduling or just accounting |
| **ChatGPT** | 20x more expensive for same data coverage | Data auto-syncs, persistent business model, always analyzing |

### 7.4 Potential Pricing Objections & Responses

| Objection | Response |
|-----------|----------|
| "$500/mo is expensive for 3 decisions/day" | "Each decision has an estimated ROI. If even one saves you $6K/year, you've paid for the entire year. Our pilot customers average $4,200/mo in ROI." |
| "I can just use ChatGPT" | "ChatGPT doesn't know your business unless you upload files. It won't notice your no-show rate spiked at 3am or that your booking gap cost $4K. Cortex lives in your data 24/7." |
| "I already have dashboards" | "Dashboards tell you what happened. Cortex tells you what to do about it and what happens if you do it. There's no 'what-if' button on a dashboard." |
| "I'll just hire an analyst part-time" | "A part-time analyst costs $2K-4K/mo and works 20 hours/week. Cortex works 168 hours/week and delivers decisions, not raw data." |

---

## 8. Key Financial Assumptions

### Revenue Projection (Conservative)

| Month | Customers | ARR Run Rate | Revenue (MRR) | Gross Margin |
|-------|-----------|-------------|---------------|--------------|
| 3 | 3 | $28,800 | $2,400 | 60% (setup-heavy) |
| 6 | 15 | $180,000 | $15,000 | 75% |
| 9 | 28 | $369,600 | $30,800 | 80% |
| 12 | 50 | $720,000 | $60,000 | 83% |
| 18 | 100 | $1,560,000 | $130,000 | 84% |
| 24 | 200 | $3,120,000 | $260,000 | 85% |

Assumes: Blended ARPU of $1,000/mo (weighted mix of tiers), 10% month-over-month growth in customers after launch.

### Cash Requirements

| Phase | Duration | Monthly Burn | Cumulative Burn | Milestone |
|-------|----------|-------------|-----------------|-----------|
| Pre-seed (founder) | 3 months | $15K (founder salary) | $45K | 3 pilots live |
| Seed (raise $1.5M) | 12 months | $85K (team of 5 + infra) | $1.02M | 50 customers, $720K ARR |
| Series A (raise $4M) | 12 months | $200K (team of 12 + scaling) | $2.4M | 200 customers, $3.12M ARR |

---