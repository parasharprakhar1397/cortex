# Cortex Founder Decision Record — v1 Lock

> *Prepared by founding CTO, 2026-07-15*
> *These decisions are locked. All v1 work proceeds from this document.*
> *Reopen only if new evidence contradicts the assumptions below.*

---

## Decision 1: Initial Vertical

### Context
The architecture assumes dental. The founder review challenged this: does the founder have a network in dental? Without it, every pilot conversation starts cold. We also have zero data on which vertical is actually the right one — this is a bet, and we should be honest about it.

### Options Considered

**Option A: Dental practices**
Single or multi-location dental offices. Tools: Jane/Dentrix (practice mgmt), Stripe (payments), QuickBooks (accounting), Calendly/Acuity (booking), HubSpot (CRM).

**Option B: Home services (HVAC, plumbing, roofing)**
Field-service businesses with truck rolls, seasonal demand, and dispatch scheduling. Tools: ServiceTitan/Housecall Pro, Stripe, QuickBooks, Calendly, HubSpot.

**Option C: Marketing/creative agencies**
Project-based professional services with time tracking and retainer billing. Tools: Harvest, QuickBooks, HubSpot, Stripe, Asana.

**Option D: Physical therapy / chiropractic**
Appointment-based allied health. Similar to dental but less insurance complexity. Tools: Jane/Mindbody, Stripe, QuickBooks, Calendly.

**Option E: Vertical-agnostic (target any service SMB)**
No vertical specialization in v1. Generic causal templates. Broader TAM, weaker positioning.

### Analysis

| Factor | Dental (A) | Home Services (B) | Agencies (C) | PT/Chiro (D) | Agnostic (E) |
|--------|-----------|-------------------|-------------|-------------|-------------|
| Data richness | High (appointment-based, predictable patterns) | High (dispatches, seasons) | Medium (project-based, lumpy revenue) | High (appointment-based) | Low (no specialization) |
| Integration coverage | Good (Jane, Dentrix via Merge.dev) | Good (ServiceTitan via Merge.dev) | Medium (custom tools common) | Good (Jane, Mindbody) | Poor (no defaults) |
| Decision clarity | No-shows, pricing, scheduling gaps | Seasonal hiring, route optimization, pricing | Utilization, retainer pricing, hiring | No-shows, pricing, scheduling | Vague |
| Willingness to pay | High (insurance billing = data-savvy) | Medium (thin margins, price-sensitive) | Medium (low volume, but high margin) | Medium-High | Unknown |
| Founder domain expertise | Unknown — assume none | Unknown — assume none | Unknown — assume none | Unknown — assume none | N/A |
| Pilot recruitment difficulty | Medium (professionals, hard to reach cold) | Medium (owners are busy, not online) | Easy (online, network-driven) | Medium | Hardest (no angle) |
| Competition | Jane is adding AI features | ServiceTitan has analytics | No dominant vertical SaaS | Mindbody has analytics | None direct |
| HIPAA risk | Yes — patient data in PMS | No | No | Yes — patient data | No |
| Revenue per customer ($1-3M SMB) | High | Medium | High | Medium | Variable |

### Recommendation: **Option A — Dental, with a caveat**

**Why dental:**
1. Dental practices have the clearest, most immediate ROI decision: no-show reduction. A single no-show costs $150–500 in lost revenue. Reducing no-shows by 20% at a practice with 5 hygienists can save $40K+/year. This is a concrete, provable ROI story.
2. The data is appointment-based (predictable patterns), with clear causal relationships: day of week → no-show rate, lead time → cancellation probability, service type → price sensitivity.
3. Dental practices run on 4+ tools (PMS, payments, accounting, booking, sometimes CRM) — exactly our integration sweet spot.
4. The fractional COO comparison is vivid here: a dental practice can't afford a COO, but they feel the pain of scheduling inefficiency daily.
5. Dental is a large, fragmented market (120K practices in the US) with no dominant AI decision-support player.

**The caveat — and this is critical:**

I cannot assess whether dental is *your* right vertical without knowing your network. If you have zero dental connections, every pilot will be cold outreach, and pilot recruitment will take 6–8 weeks instead of 2–3. If you have a network in another vertical that's equally data-rich (e.g., you know 10 chiropractors or 10 agency owners), *that* is your vertical.

**Decision rule:** If founder has ≥3 warm connections in dental → dental. If founder has ≥3 warm connections in another service vertical with 3+ SaaS tools → that vertical. If founder has no warm connections in any service vertical → pick the vertical where you can get a warm intro fastest, even if it's not the "optimal" one. **A warm pilot beats a perfect vertical every time.**

### Why I Rejected the Alternatives

- **Home services (B):** Better TAM (500K businesses) but worse unit economics — thinner margins mean harder to justify $500/mo. Seasonal demand patterns make it harder to demonstrate ROI in a 3-month pilot. Revisit as vertical #2.
- **Agencies (C):** Project-based billing means lumpy, irregular revenue patterns — harder for our models to establish baselines quickly. But if the founder has agency connections, this could work. The "utilization" decision type is high-ROI for agencies.
- **PT/Chiro (D):** Very similar to dental but smaller TAM. If founder has PT connections and not dental, this is a fine substitute. Same data patterns, same decisions.
- **Vertical-agnostic (E):** This is what you do when you've proven the model in one vertical and want to expand. Starting agnostic means weaker positioning, generic messaging, and no natural pilot channel. Rejected for v1.

---

## Decision 2: LLM Strategy for v1

### Context
The architecture proposes self-hosted Llama 3 (8B + 70B) via vLLM on Vast.ai GPUs with GPT-4o as fallback. The founder review flagged this as premature for v1 — engineering overhead of 3–4 weeks, GPU reliability concerns, and minimal cost savings at 3–10 customers.

### Options Considered

**Option A: OpenAI API only**
GPT-4o-mini for routine decisions ($0.15/1M input tokens), GPT-4o for complex simulations ($2.50/1M input). No GPU infrastructure.

**Option B: Self-hosted Llama 3 (hybrid, per architecture)**
Llama 3 8B for routine (Tier 1), Llama 3 70B for deep analysis (Tier 2), GPT-4o as emergency fallback. Requires 1× A100 GPU ($1,500–2,000/mo) + vLLM setup + monitoring.

**Option C: Anthropic Claude as alternative API**
Claude 3.5 Sonnet for routine, Claude 3 Opus for complex. Different cost structure, potentially better at structured reasoning.

**Option D: Hybrid with OpenAI for v1, self-hosted later**
Start with OpenAI API now, build self-hosted infrastructure in parallel during Phase 2 (weeks 9–12), cut over when it's stable and cost-justified.

### Analysis

| Factor | OpenAI API (A) | Self-Hosted Llama (B) | Anthropic (C) | Hybrid Later (D) |
|--------|---------------|----------------------|---------------|-----------------|
| Time to ship | 1 day (API key) | 3–4 weeks (vLLM setup, GPU procurement, model loading, failover) | 1 day (API key) | 1 day now, 3–4 weeks later |
| Cost at 3 customers | ~$80–150/mo | $1,500–2,000/mo (GPU rental, 24/7) | ~$100–200/mo | $80–150/mo now, $1,500+ later |
| Cost at 10 customers | ~$200–400/mo | $1,500–2,000/mo (same GPU, more utilization) | ~$250–500/mo | $200–400/mo now |
| Cost at 50 customers | ~$800–1,500/mo | $1,500–2,000/mo (still 1 A100) | ~$1,000–2,000/mo | Breakeven point |
| Cost at 200 customers | ~$3,000–6,000/mo | $3,000–6,500/mo (2–4 A100s) | ~$4,000–8,000/mo | Self-hosted wins |
| Reliability | 99.5%+ uptime SLA | Vast.ai: no SLA, spot preemption risk. Modal: better but cold starts | 99.5%+ uptime | API reliable now |
| Engineering overhead | Zero | High (GPU ops, model updates, CUDA issues, failover) | Zero | Low now, high later |
| Decision quality | Excellent (GPT-4o is SOTA for reasoning) | Good (Llama 3 70B is strong but not GPT-4o level) | Excellent (comparable to GPT-4o) | Best of both |
| Data privacy | Data sent to OpenAI (zero-retention API available) | Data stays on our infrastructure | Data sent to Anthropic | API now, private later |
| Token latency | 1–5 seconds | 0.5–3 seconds (local, no network) | 1–5 seconds | API now |
| Model control | None (model updates forced) | Full (pin versions, fine-tune) | None | Control later |

### Recommendation: **Option D — OpenAI API for v1, self-host when cost-justified (50+ customers)**

**Why OpenAI now:**
1. **Time to ship:** This is the dominant factor. The founder is the only engineer. Spending 3–4 weeks on GPU infrastructure means 3–4 weeks not building integrations, not onboarding pilots, not validating the product. The entire v1 timeline collapses if we add self-hosted LLM setup.
2. **Cost is irrelevant at pilot scale:** At 3 customers, OpenAI API costs ~$80–150/mo. Self-hosting costs $1,500–2,000/mo. The "savings" of self-hosting are negative $1,350+ per month at this scale. The crossover point is around 50 customers — we're at least 9 months from that.
3. **Decision quality is better:** GPT-4o produces better structured reasoning than Llama 3 70B today. For generating clear, accurate business recommendations — the core product — API quality matters more than cost.
4. **Reliability:** OpenAI has 99.5%+ uptime. Vast.ai GPU instances can be preempted with 5 minutes notice. An inference outage during a pilot is a trust-killing event.
5. **Focus:** Every hour spent on vLLM config, CUDA versions, GPU procurement, and model server monitoring is an hour not spent on entity resolution, decision quality, or pilot onboarding — the things that actually determine whether Cortex works.

**The switch point:** At ~50 customers, when monthly API costs approach $1,500–2,000, begin the self-hosted migration. By then we'll have Engineer #2 to share the work, and the product will be stable enough to absorb the infrastructure change.

**Privacy note:** Use OpenAI's zero-data-retention API (no training on our data). For pilots, this is adequate. If enterprise customers demand on-premise inference, that's a v2 problem — and good evidence that someone wants to pay us.

### Why I Rejected the Alternatives

- **Self-hosted from day 1 (B):** Costs more, takes longer, produces worse decisions, and is less reliable at pilot scale. The only advantage is data privacy and long-term cost — neither of which matter for validation. This is the classic startup mistake of building infrastructure for scale before proving anyone wants the product.
- **Anthropic (C):** Comparable to OpenAI but slightly more expensive and with a smaller ecosystem. No compelling reason to prefer it over OpenAI for v1. If OpenAI has an outage, Claude is a fine fallback.
- **OpenAI-only forever (A):** At 200+ customers, API costs become material ($3–6K/mo vs. $3–6.5K for self-hosted, roughly comparable). But the real reason to eventually self-host is model control — fine-tuning per vertical, custom system prompts, latency optimization. This matters at scale, not at pilot.

---

## Decision 3: Pilot Pricing Strategy

### Context
The owner's stated goal: "Revenue is secondary to validation. I'd rather have 3 deeply engaged customers than 20 superficial ones." Yet the monetization doc proposes 30% pilot discount ($350/mo Essentials). The founder review challenged: if validation is the goal, why charge at all?

### Options Considered

**Option A: Free pilot (3-month term)**
No cost to the pilot. They get full Essentials tier. In exchange: weekly check-in calls, testimonial rights, and feedback participation.

**Option B: 30% pilot discount ($350/mo for Essentials)**
Per the monetization doc. Discounted for 12 months. Paid from day 1.

**Option C: Full price from day 1 ($500/mo)**
Standard pricing. No discounts. Month-to-month commitment.

**Option D: "Pay if you stay" — free for 2 months, then $500/mo**
The pilot period is free. If they continue past month 2, they convert to paid at full price.

### Analysis

| Factor | Free (A) | 30% Discount (B) | Full Price (C) | Pay If You Stay (D) |
|--------|----------|-----------------|----------------|---------------------|
| Pilot recruitment speed | Fastest (no objection) | Fast | Slow (harder to close) | Fast |
| Commitment signal | Weak — free users churn easily | Medium — "skin in the game" | Strong — serious buyers only | Medium initially, strong after conversion |
| Revenue during pilot | $0 | $350/mo/customer ($1,050/mo at 3 pilots) | $500/mo/customer ($1,500/mo at 3 pilots) | $0 for 2 months, then $500 |
| Feedback quality | Risk of politeness bias | Better — paying customers complain honestly | Best — high expectations, high feedback | Mixed |
| Pilot engagement | Risk of low engagement | Higher — payment drives usage | Highest | Risk of low engagement in free period |
| Churn after pilot period | Highest risk | Medium | Lowest | Medium |
| Founder sales difficulty | Easiest | Medium | Hardest | Easy initially, conversion conversation later |
| Alignment with owner's goal | Strong ("validation over revenue") | Moderate | Weak (optimizes for revenue) | Strong |
| Risk of "wrong" pilots | High — anyone will try free | Low — discount still filters | Lowest | Medium in free period |

### Recommendation: **Option D — "Pay if you stay" (2 months free, then $500/mo)**

**Why this structure:**

1. **It aligns with the owner's stated goal.** Validation over revenue. Making pilots free removes the biggest objection to trying Cortex. A dental practice owner who's curious but skeptical will say yes to "free for 2 months, no commitment" far faster than "$350/mo with a 30% discount."

2. **It has a built-in validation test.** The conversion from free → paid at month 3 is the single clearest signal of product-market fit. If all 3 pilots convert and pay $500/mo, that's validation. If 0 convert, that's also validation — just not the kind we want. The 30% discount obscures this signal: did they stay because Cortex is valuable, or because it's cheap?

3. **It still filters for serious buyers.** A practice owner who won't try Cortex for free isn't a customer we want. But one who will try it for free and then pay $500/mo — that's exactly the ICP. The free period creates a trial, and the conversion proves value.

4. **It's honest about the product's maturity.** We're selling an unproven product to early adopters. Charging full price for something that might break is a hard conversation. "It's free while we work out the kinks together, and if you see value, it's $500/mo after that" is a fair deal that builds trust.

5. **It accelerates the timeline.** Pilot recruitment is the gating factor for the entire v1 plan. Removing price friction could cut recruitment time from 4–6 weeks to 2–3 weeks.

**The terms:**
- 2 months free, full Essentials tier (5 integrations, 5 decision types)
- Weekly 30-minute check-in call (founder-led)
- At month 2: conversion conversation. "Here's what Cortex found. Here's the ROI. Would you like to continue at $500/mo?"
- Month-to-month after conversion, no annual lock-in
- Agree to provide a testimonial/case study if they renew past month 4

**Risk:** We get 3 pilots, none convert, we have zero revenue and 2 months of founder time spent. That's not failure — it's learning that the product isn't valuable enough yet. Better to learn that in 2 months than to spend 6 months trying to sell a product nobody wants while discounting to hide the signal.

### Why I Rejected the Alternatives

- **Free forever (not proposed, but implicit in "free pilot"):** No. The goal is validation for a paid product. If pilots never face a payment decision, we never test willingness to pay. Free pilot with mandatory conversion conversation is different from free forever.
- **30% discount (B):** This optimizes for a revenue number that doesn't matter yet. $350/mo × 3 pilots = $12,600/year. That's noise. The cost of the discount is that it muddies the PMF signal: if a pilot stays at $350/mo but would churn at $500/mo, we've learned the wrong lesson. Test the real price.
- **Full price (C):** This would be right if we were confident in the product. But we're not — that's the whole point of pilots. Making the founder sell an unproven, unbuilt product at full price to strangers burns political capital and slows everything down. Full price is for post-pilot customers.

---

## Decision 4: Onboarding Fee Structure

### Context
The monetization doc contradicts itself: principle #4 says "no setup fee for Essentials," but the fee table shows "$2,000." The architect's report flagged this. The onboarding fee exists to recover cost ($150/hr × 8 hours ≈ $1,200) and signal commitment. But for pilots, the goal is speed and engagement, not cost recovery.

### Options Considered

**Option A: No onboarding fee for anyone (pilot or otherwise)**
Onboarding is included in the subscription. Cost absorbed by the company.

**Option B: Onboarding fee for all ($2,000 Essentials)**
Per the monetization doc's fee table. Discounted to $1,400 for pilots (30% off).

**Option C: Free onboarding for pilots, paid for post-pilot customers**
Pilots get white-glove onboarding included. Customers who sign up after the pilot program pay $2,000.

**Option D: Onboarding fee waived with annual commitment**
Month-to-month customers pay $2,000. Annual customers get onboarding included.

### Analysis

| Factor | No Fee (A) | Fee for All (B) | Free for Pilots (C) | Waived w/ Annual (D) |
|--------|-----------|----------------|---------------------|---------------------|
| Pilot recruitment speed | Fastest | Slower (+$2K friction) | Fastest | N/A for pilots |
| Cost recovered | $0 | $2,000/customer | $0 for pilots, $2K for post-pilot | $0 for annual |
| Commitment signal | Weakest | Strongest | Medium (time commitment, not money) | Strong (annual lock-in) |
| Onboarding quality | Same | Same | Same | Same |
| Founder time cost | 8 hours × $150/hr = $1,200/customer | Recovered | $1,200/pilot (unrecovered) | Recovered |
| Alignment with validation goal | Strong | Weak (optimizes for cost recovery) | Strong | Medium |
| Perception of value | "They're investing in us" | "They're charging us before we see value" | "They're investing in us" | "Fair deal" |

### Recommendation: **Option C — Free onboarding for pilots, $2,000 for post-pilot customers**

**Why:**

1. **Onboarding is the product experience.** The first two weeks of Cortex — connecting tools, seeing the first insights, learning to trust the system — *is* the product. Charging for it before the customer has seen any value is like charging for a trial. For pilots, this is a non-starter: you're asking someone to pay $2,000 to help you test your unproven product.

2. **The cost is modest and the learning is invaluable.** Onboarding a pilot costs ~$1,200 in founder time. Three pilots = $3,600. That's not a cost — it's the cheapest product research you'll ever do. You'll learn more about entity resolution, integration friction, and decision quality from 3 pilot onboardings than from 3 months of internal testing.

3. **Post-pilot, the fee is justified.** Once Cortex has proven value (pilot conversions), a $2,000 onboarding fee signals: (a) this is a serious product for serious businesses, (b) the setup requires real work, and (c) you should be committed before we invest 8 hours. By this point, customers have reference stories and case studies to justify the fee.

4. **It creates a clean pilot → customer transition.** Pilot: free onboarding, free subscription for 2 months, then $500/mo. Post-pilot customer: $2,000 onboarding + $500/mo. The pilot discount is clear and time-bound.

**Risk:** Post-pilot customers balk at the $2,000 onboarding fee. Mitigation: if conversion data shows the fee is blocking sales, drop it to $1,000 or bundle it with an annual commitment. The fee isn't sacred — it's a hypothesis.

### Why I Rejected the Alternatives

- **No fee for anyone (A):** Fine for pilots, but post-pilot it leaves money on the table and removes a useful commitment signal. The $2,000 onboarding fee also creates a natural incentive for customers to commit to annual billing (where it can be waived).
- **Fee for all including pilots (B):** The worst option for our stated goal. Adding $2,000 friction to pilot recruitment when we're asking for a favor (test our unproven product) is tone-deaf. The pilot's "payment" is their time volunteering feedback, weekly calls, and the risk of wasting time on a product that might not work.
- **Waived with annual (D):** This is a post-pilot optimization, not a pilot decision. Doesn't apply to the 6-month validation window. Good idea for v1.1 when we have pricing data.

---

## v1 Product Lock Summary

Based on these four decisions, here is the locked v1 scope:

| Dimension | Decision | Rationale |
|-----------|----------|-----------|
| **Vertical** | Dental (or founder's warmest service vertical) | Highest ROI per decision. But a warm intro beats the perfect vertical. |
| **LLM** | OpenAI API (GPT-4o-mini + GPT-4o), migrate to self-hosted at 50+ customers | Speed to ship. Cost irrelevant at pilot scale. Better decision quality. |
| **Pilot pricing** | Free for 2 months, then $500/mo | Maximizes recruitment speed. Conversion is the PMF signal. |
| **Onboarding fee** | Free for pilots, $2,000 post-pilot | Removes friction for validation. Recovers cost once value is proven. |
| **Integrations** | 3 (Stripe, QuickBooks, Calendly) | Per founder review. HubSpot + GA4 added post-pilot. |
| **Decision types** | 4 (revenue trend, no-show risk, booking gap, churn risk) | Per founder review. Pricing optimization added post-pilot. |
| **Database** | Plain PostgreSQL (add TimescaleDB + pgvector as needed) | Per founder review. Don't optimize for scale before validation. |
| **Agents** | Celery task chain (Scheduler + Decision Engine), not LangGraph | Per founder review. Simpler, faster to build, easier to debug. |
| **Simulation** | Formula-based calculator, not Monte Carlo | Per founder review. "What-if" is important but doesn't need full simulation. |
| **Causal engine** | Deferred to v2 | Per founder review. Statistical tests + LLM explanation are sufficient for v1. |
| **Infrastructure** | Docker Compose on single DigitalOcean VM, no GPU | $500–800/mo total. No Vast.ai, no vLLM. |
| **Timeline** | 8–10 weeks to MVP, 12–14 weeks to pilots | Per founder review. Realistic for 1 founder. |

---

## Cost Model — v1 Pilot Phase (First 6 Months)

| Month | Activity | Infra Cost | OpenAI Cost | Total Burn |
|-------|----------|-----------|-------------|------------|
| 1 | Build (weeks 1–4) | $400 (DO VM + managed Postgres) | $20 (dev testing) | $420 |
| 2 | Build (weeks 5–8) | $500 | $50 | $550 |
| 3 | Build + Pilot 1 | $600 | $80 | $680 |
| 4 | Pilots 1–2 | $700 | $120 | $820 |
| 5 | Pilots 1–3 | $800 | $180 | $980 |
| 6 | Pilots stabilize, prep launch | $800 | $200 | $1,000 |

**Total 6-month infrastructure cost: ~$4,450**

This is 60% lower than the original roadmap's estimate of ~$11,500/month in Phase 2 — because we cut GPU ($1,500–2,000/mo), reduced complexity, and use API instead of self-hosted infrastructure.

---

## Open Question for Founder

**Which vertical has your warmest network?**

Before we commit to dental, answer this: if you had to get 3 practice owners on a 30-minute exploratory call next week, which industry would you call? Dental, chiropractic, home services, agencies, or something else? That answer — not the market analysis — determines our vertical for v1.

---

*This document supersedes any conflicting guidance in the architecture documents. All v1 engineering work proceeds from these decisions. Reopen only if pilot data contradicts the assumptions here.*
