# Vertical Selection Analysis — Cortex v1 Launch

> *Prepared by founding CTO, 2026-07-15*
> *Replaces the dental assumption in the Decision Record. This analysis is the new source of truth for vertical selection.*

---

## Evaluation Framework

Six verticals evaluated against seven criteria. Each criterion scored 1–5. Weighted composite determines ranking.

### Criteria Definitions

| Criterion | What It Measures | Why It Matters for Pilots |
|-----------|-----------------|--------------------------|
| **Urgency of pain** | How badly does the owner feel the problem *today*? | Urgent pain = faster pilot commitment. "I need this now" vs. "this would be nice." |
| **Ease of integration** | How clean and accessible is their data? Dominant tools? API quality? Merge.dev coverage? | Integration friction is the #1 source of pilot delays. Bad integrations = bad first experience. |
| **Measurable ROI** | Can we point to a specific dollar amount Cortex saved/earned? | The pilot must produce a number the owner can quote. "$12K saved on no-shows" is a story. "Better decision-making" is not. |
| **Sales cycle length** | How fast can we get from first contact to signed pilot? | 3 pilots in 6 months. Long sales cycles kill the timeline. |
| **Willingness to pay** | Will they pay $500/mo after the pilot? Evidence of spending on comparable tools? | The pilot is free; validation requires conversion to paid. Willingness to pay at $500/mo is the test. |
| **Data availability** | How digital is this vertical? Structured data? Years of history? | Cortex needs data to produce decisions. Sparse or messy data = weak first impressions. |
| **Pilot comparability** | Can 3 pilots in this vertical produce comparable, generalizable results? | 3 pilots with completely different business models = 3 one-off integrations, not a vertical play. |

---

## Vertical Analysis

### 1. Multi-Location Healthcare Practices
*Dental, physical therapy, chiropractic, optometry, veterinary clinics with 2+ locations*

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **5** | No-shows cost $150–500 per slot. Schedule gaps are visible tomorrow morning. Understaffing = patients leave. This pain is *daily and dollar-quantified*. |
| Ease of integration | **4** | Dominant tools: Jane, Mindbody, Dentrix, Eaglesoft, WebPT. Merge.dev covers most. Payments via Stripe/Square. Accounting via QuickBooks. Booking via Calendly/Acuity. The tool stack is standardized and API-accessible. |
| Measurable ROI | **5** | No-show reduction: $40K+/yr for a 5-provider practice. Utilization improvement: $60K+/yr. Pricing optimization: $30K+/yr. Every decision type maps to a line item on their P&L. |
| Sales cycle length | **3** | Practice owners are busy professionals. Initial contact → signed pilot: 3–6 weeks. Gatekeepers (office managers) can slow things down. |
| Willingness to pay | **5** | Already paying $300–800/mo for practice management software. Used to SaaS subscriptions. A single no-show reduction tip pays for a year of Cortex. |
| Data availability | **5** | Appointment data, revenue by provider, patient retention, insurance mix — all digital, structured, and typically going back 2+ years. |
| Pilot comparability | **5** | Two dental practices + one PT clinic share appointment-based economics. Same integration stack. Same decision types (no-shows, utilization, pricing). Results generalize within and across specialties. |
| **Composite** | **4.6** | |

**Product fit assessment:** Exceptional. Appointment-based services are Cortex's ideal data shape — regular, recurring, revenue-per-slot is known, utilization is calculable immediately. The integration stack is standardized and well-covered by Merge.dev. The ROI story writes itself.

---

### 2. Home Service Companies
*HVAC, plumbing, roofing, electrical, pest control with 10+ technicians*

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **5** | Seasonal demand mismatch is existential. An HVAC company that staffs for summer but gets a mild June loses $100K+. Truck rolls to wrong addresses, idle technicians, emergency overtime — all dollar-measurable daily. |
| Ease of integration | **3** | Dominant tools: ServiceTitan, Housecall Pro, Jobber. Merge.dev covers ServiceTitan. But: these PMS systems are deep and complex. Dispatch data, job costing, inventory — normalization is harder than healthcare. |
| Measurable ROI | **5** | Route optimization: $30K+/yr. Seasonal hiring timing: $50K+/yr. Pricing by job type: $40K+/yr. Large dollar amounts, clear cause-and-effect. |
| Sales cycle length | **3** | Owners are pragmatic and ROI-driven. "Show me the money." Can move fast if convinced. But they're busy — 3–5 weeks. |
| Willingness to pay | **3** | Margins vary: HVAC/high-ticket trades have 20–30% margins and will pay. Plumbing/roofing are thinner at 10–15%. $500/mo is a harder sell to a roofer with 8% net margins. |
| Data availability | **3** | Good in the PMS, but field data (technician notes, job site conditions) is unstructured. Seasonal patterns are valuable but noisy. Historical data quality varies. |
| Pilot comparability | **4** | Three HVAC companies in different regions have comparable operations. Same PMS, same decision types. But seasonal patterns differ by geography — a Florida HVAC company and a Minnesota one have opposite peak seasons. |
| **Composite** | **3.7** | |

**Product fit assessment:** Strong but rougher edges. The pain is as urgent as healthcare, and the dollar amounts are larger, but integration is more complex and data is messier. Home services would be the #1 vertical if we had 6 months to build integrations instead of 8–10 weeks. For v1 speed, healthcare's cleaner data wins.

---

### 3. Specialty Retail Chains
*3–20 location apparel, home goods, electronics, sporting goods, or food/beverage retailers*

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **3** | Inventory stockouts and overstocks hurt but aren't daily crises. Staffing mismatches cause long lines but don't threaten the business. The pain is real but less acute than an empty appointment slot. |
| Ease of integration | **4** | Shopify/Lightspeed/Square POS + Stripe + QuickBooks + Klaviyo/Mailchimp. Clean, modern APIs. Merge.dev covers most. |
| Measurable ROI | **3** | Inventory optimization: meaningful but hard to attribute. Staffing efficiency: real but the calculation is complex. Promotion ROI: high value but depends on marketing data quality. |
| Sales cycle length | **3** | Multi-location retailers have more stakeholders. Owner + GM + maybe a board. 4–6 weeks. |
| Willingness to pay | **2** | Retail margins are 5–15%. $500/mo is 0.5–2% of revenue at a $1M store — significant. They'll pay for tools that directly drive sales (Shopify, marketing) but "strategic decisions" is a harder line item. |
| Data availability | **5** | POS data is the cleanest data in any vertical. Every transaction is timestamped, SKU-level, and linked to a customer. Beautiful for analysis. |
| Pilot comparability | **3** | Three specialty retailers could be a clothing boutique, an electronics store, and a food retailer — very different inventory dynamics, seasonality, and margins. Hard to build one model that works for all. |
| **Composite** | **3.3** | |

**Product fit assessment:** The data is the best of any vertical. But the pain isn't urgent enough and the margin structure makes $500/mo a tough sell. Retail is a strong v2 vertical once we have reference pricing. For v1 pilots, the "decisive moment" isn't sharp enough.

---

### 4. Automotive Service Businesses
*Independent repair shops, tire centers, quick-lube franchises, collision centers*

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **4** | Bay utilization is make-or-break. An empty bay is $100–200/hr lost. Technician scheduling and parts inventory are genuine daily pains. |
| Ease of integration | **2** | Shop management systems (RO Writer, Mitchell1, Shop-Ware, ALLDATA) are legacy-heavy. Many still use on-premise software with limited or no APIs. Merge.dev coverage is thin for this vertical. |
| Measurable ROI | **4** | Bay utilization improvement: $50K+/yr. Parts inventory optimization: $20K+/yr. Pricing by job type: $30K+/yr. The dollars are there. |
| Sales cycle length | **3** | Independent shop owners are pragmatic. Can say yes quickly. But many are tech-skeptical — they run on paper and phone calls. |
| Willingness to pay | **2** | Notoriously price-sensitive. Many shops run on 5–10% net margins. $500/mo is real money. They'll pay for tools that directly generate revenue (tire distributors, parts systems) but balk at analytics. |
| Data availability | **2** | If they use a modern PMS, data is decent. But many don't. And the data that exists is often incomplete (missing job costing, inconsistent service codes). |
| Pilot comparability | **3** | Three independent shops would be comparable. But the integration work to connect legacy PMSs is high-effort and non-repeatable. |
| **Composite** | **2.9** | |

**Product fit assessment:** Hidden value, but hidden behind integration walls. The operational problems are a perfect Cortex use case — bay utilization, technician efficiency, parts inventory. But the integration burden is too high for v1. If a modern, API-first shop PMS emerges and gains adoption, this vertical becomes much more attractive. Revisit in v2.

---

### 5. Coaching Institutes & Private Education Providers
*Tutoring centers, test prep, language schools, professional certification, music/dance academies*

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **3** | Class under-enrollment, instructor scheduling, seasonal demand swings. Real pain but less acute than a no-show — an empty class is scheduled weeks in advance, not discovered tomorrow. |
| Ease of integration | **2** | Tool stack is highly fragmented. Some use Teachable/Thinkific, some use Calendly, some use custom registration systems. No dominant PMS. Merge.dev coverage is weak for this category. |
| Measurable ROI | **3** | Class fill rate improvement, instructor utilization, pricing optimization. All real but harder to quantify than healthcare ROI. "We filled 2 more classes this semester" is a softer story. |
| Sales cycle length | **3** | Owner-operated, can decide quickly. But education owners aren't typically business-operations focused — they're educators first. |
| Willingness to pay | **2** | Education margins are 5–20%. Many owners underprice their services. $500/mo is a significant expense for a tutoring center doing $300K/year. |
| Data availability | **2** | Enrollment data is often in spreadsheets. Payment data in Stripe/Square is clean, but the link between "student enrolled" and "student paid" is manual in many cases. |
| Pilot comparability | **2** | A test prep center, a music academy, and a language school have fundamentally different business models (one-on-one vs. group vs. subscription). Three pilots would be three custom integrations. |
| **Composite** | **2.4** | |

**Product fit assessment:** Weak for v1. The pain is real but diffuse, the tools are fragmented, and three pilots would teach us three different things instead of one repeatable pattern. Cortex could serve this vertical well eventually, but it's not the right proving ground.

---

### 6. Real Estate Agencies
*Residential brokerages with 10–100+ agents, or commercial real estate firms*

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **2** | Agent productivity and pipeline management are real concerns, but they're slow-burn problems. Market conditions dominate outcomes. A down market makes everything look like Cortex's fault. |
| Ease of integration | **2** | CRM-heavy (Follow Up Boss, BoomTown, kvCORE) + transaction management (Dotloop, SkySlope) + accounting. Merge.dev covers some CRMs. But agent adoption of tools is inconsistent — data quality suffers. |
| Measurable ROI | **2** | Agent productivity is notoriously hard to attribute. Did Cortex improve conversion, or did the agent just have a good month? Market cycles make ROI isolation nearly impossible in a 3-month pilot. |
| Sales cycle length | **2** | Brokerages are committee-driven or broker-owner fiefdoms. 6–8 weeks to a decision, often longer. |
| Willingness to pay | **3** | Real estate margins are 20–40% at the brokerage level. They spend on leads, CRMs, and coaching. But willingness to pay for "analytics" is unproven — they pay for leads, not insights. |
| Data availability | **3** | Transaction data is clean (MLS, closing records). But agent activity data (calls, showings, follow-ups) is inconsistently tracked. |
| Pilot comparability | **2** | A residential brokerage in Phoenix and one in Seattle operate in different market conditions, regulatory environments, and price points. Results don't generalize well. |
| **Composite** | **2.3** | |

**Product fit assessment:** The weakest fit. Real estate is a market-dependent business where external factors dominate internal decisions. Cortex's value proposition — "our recommendations caused this improvement" — is nearly impossible to prove in a 3-month pilot when the market moved 5% in either direction. Revisit only if the founder has extraordinary real estate connections and a specific, narrow use case (e.g., property management).

---

## Composite Ranking

| Rank | Vertical | Composite | Pain | Integration | ROI | Sales Cycle | WTP | Data | Comparability |
|------|----------|-----------|------|-------------|-----|-------------|-----|------|---------------|
| **1** | **Multi-location healthcare** | **4.6** | 5 | 4 | 5 | 3 | 5 | 5 | 5 |
| **2** | Home services | 3.7 | 5 | 3 | 5 | 3 | 3 | 3 | 4 |
| **3** | Specialty retail | 3.3 | 3 | 4 | 3 | 3 | 2 | 5 | 3 |
| **4** | Automotive service | 2.9 | 4 | 2 | 4 | 3 | 2 | 2 | 3 |
| **5** | Coaching / private education | 2.4 | 3 | 2 | 3 | 3 | 2 | 2 | 2 |
| **6** | Real estate | 2.3 | 2 | 2 | 2 | 2 | 3 | 3 | 2 |

---

## Recommendation

### Launch vertical: Multi-location healthcare practices

**The argument is not theoretical — it's structural.**

Cortex's core product loop is: connect data → detect pattern → estimate ROI → recommend action → measure outcome. This loop works best when the business has:

1. **Recurring, schedulable revenue units** (appointments) — so we can detect deviations from baseline immediately. An empty appointment slot tomorrow is a signal. A slow retail month is noise.

2. **Known revenue per unit** — so ROI estimates are specific. "A no-show costs $350. Reducing no-shows by 20% saves $42K/yr." This math is impossible in real estate, hard in retail, and straightforward in healthcare.

3. **Standardized tool stack** — so the integration work for pilot #1 reduces the work for pilots #2 and #3. Jane, Mindbody, and Dentrix are different PMSes, but they all model the same thing: provider → schedule → patient → payment.

4. **A clear, emotionally resonant decision type** — "Your no-show rate is 18%. The industry average is 12%. Here's which patients are likely to cancel, and here's what to do." This is a decision the owner *already knows they should be making* but can't because the data is scattered across their PMS, payment system, and booking tool.

**Why not home services (ranked #2)?**

Home services is a close second and will likely be the best second vertical. But it has two v1-killing problems:

- **Integration complexity.** ServiceTitan's API is deep and complex. Normalizing dispatch data, job costing, and field technician workflows is 2–3× the work of normalizing appointment data. In an 8–10 week build window, that matters.

- **Data messiness.** Field service data is inherently noisier than appointment data. A "no-show" in healthcare is unambiguous. A "truck roll that took 2 hours instead of 1" in home services could be traffic, a difficult job, a new technician, or bad dispatch — disentangling those requires more data and more sophisticated models than v1 will have.

Home services is the right second vertical — revisit at month 6 when the integration pipeline is mature and the causal models are tuned.

**Caveat: The founder's network overrides the ranking.**

If the founder has ≥3 warm connections in home services and zero in healthcare, build for home services. The integration will be harder, but a warm pilot beats a perfect vertical analysis every time. The same applies to any vertical: if you can get 3 owners on a call next week in specialty retail, and you can't get a single healthcare practice owner to respond to email, build for specialty retail. Speed to pilots is the binding constraint, not market optimality.

---

## Updated Decision Record

This analysis supersedes the "Dental" assumption in the Decision Record. The locked v1 vertical is:

> **Multi-location healthcare practices** — specifically dental, physical therapy, chiropractic, and optometry practices with 2+ locations, $1M–10M revenue, running on a modern PMS (Jane, Mindbody, Dentrix, WebPT) plus Stripe and QuickBooks.
>
> If the founder's network supports a different vertical with ≥3 warm connections, that vertical overrides this recommendation.

---

*This document is the binding vertical selection for v1. Reopen only if pilot recruitment fails in the primary vertical and the founder's network points elsewhere.*
