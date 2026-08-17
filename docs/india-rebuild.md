# Cortex — India Context Rebuild

> *Prepared by founding CTO, 2026-07-15*
> *Delhi NCR, India. Solo student founder. Limited capital. Zero network.*
> *This document supersedes ALL previous vertical, pricing, GTM, and integration assumptions. Core product architecture is unchanged; everything above it is rewritten.*

---

## Part 1: What Breaks

The previous plan assumed US healthcare practices, US pricing ($500/mo), US networking channels, US tools (Stripe/QuickBooks), US regulatory environment (HIPAA/SOC 2), and a founder with professional credibility. None of these assumptions survive the India context. Here is what changes, in order of impact:

### Break #1: The Vertical

US multi-location healthcare was chosen because: appointment-based data, clean ROI (no-shows = dollars), standardized tool stack, high willingness to pay. In Delhi NCR:

- **Indian healthcare practices are different.** Most are single-location, single-doctor clinics. Multi-location chains exist (Clove Dental, MyDentist, Axiss) but are corporate entities with centralized procurement — they buy software through RFPs, not founder conversations. The owner-operator SMB dynamic that Cortex needs is rare in Indian healthcare at the multi-location level.

- **Tools are different.** Indian dental practices don't use Jane or Dentrix. They use custom PMS (if any), Tally for accounting, and manual scheduling. Integration surface is much smaller.

- **A student approaching a 50-year-old dentist to "shadow their operations" does not work in Indian culture.** Age and status hierarchies are real. The credibility gap is too wide.

**Verdict: Healthcare is not the launch vertical in India. Pivot.**

### Break #2: Pricing

$500/mo = ₹42,000/mo. Indian SMB SaaS pricing benchmarks:

| Tool | Monthly Price (₹) | What It Does |
|------|-------------------|-------------|
| Zoho One (all apps) | ₹1,500–3,000/user | CRM + Books + Analytics + 40+ apps |
| Tally Prime | One-time ₹20,000–60,000 | Accounting |
| Razorpay | Per-transaction (2%) | Payments |
| Shopify India | ₹1,499–5,599/mo | E-commerce storefront |
| Freshworks CRM | ₹999–4,999/user/mo | CRM |
| LeadSquared | ₹1,250–5,000/user/mo | Marketing automation + CRM |
| Dukaan | ₹699–2,999/mo | E-commerce platform |

Indian SMBs pay ₹500–5,000/mo for individual SaaS tools. A "premium" tool might command ₹5,000–15,000/mo. ₹42,000/mo for "strategic decisions" is a non-starter — no Indian SMB has that budget line.

**Verdict: Pricing must be rebuilt for Indian willingness to pay. Target: ₹5,000–15,000/mo ($60–180).**

### Break #3: Integration Stack

The US stack (Stripe, QuickBooks, Calendly, HubSpot, GA4) doesn't exist in India. Replacements:

| US Tool | Indian Replacement | API Quality | Merge.dev Coverage | 
|---------|-------------------|-------------|--------------------|
| Stripe | Razorpay, Cashfree, PhonePe PG | Good | Merge.dev supports Razorpay |
| QuickBooks | Tally, Zoho Books | Tally: poor API. Zoho Books: good API | Merge.dev supports Zoho Books |
| Calendly | Calendly (global), Zoho Bookings | Good | Merge.dev supports Calendly |
| HubSpot | Zoho CRM, LeadSquared | Good | Merge.dev supports both |
| GA4 | GA4 (global) | Good | Native |
| Meta Ads | Meta Ads (global) | Good | Merge.dev supports |

Critical issue: **Tally is the dominant accounting tool for Indian SMBs, but its API is notoriously bad.** Many Indian businesses export Tally data as CSV spreadsheets. This makes automated integration difficult. Zoho Books is growing but still smaller than Tally in the SMB segment.

**Verdict: Integration strategy must shift. Priority #1: Razorpay. Priority #2: Zoho Books (not Tally). Accept that some pilots will use Tally and we'll need a CSV import bridge.**

### Break #4: Networking Channels

The US plan relied on: healthcare study clubs, dental conferences, local business associations, shadowing office managers. In Delhi NCR:

| US Channel | Indian Equivalent | Viability | Accessibility for Student |
|------------|------------------|-----------|--------------------------|
| Healthcare study clubs | Indian Dental Association chapters, medical associations | Medium | Low (age/status gap) |
| Chamber of Commerce | FICCI, CII, PHD Chamber — too corporate | Low | Very low |
| Industry conferences | D2C summits, SaaS meetups, e-commerce events | High | High |
| Local business groups | TiE Delhi, NASSCOM 10K Startups, incubator events | High | High |
| Coffee meetings | Chai + samosa meetings — same dynamic, lower formality | High | High |

**Verdict: The startup ecosystem in Delhi NCR is the founder's natural habitat, not industry associations. This changes the target vertical.**

### Break #5: Founder Credibility

A US-based professional with work experience approaching SMB owners has baseline credibility. An Indian university student approaching business owners faces a different dynamic:

- **Age hierarchy matters.** A 20-22 year old approaching a 45-year-old business owner is culturally unusual. The owner's first question will be: "Who are you, and why should I trust you with my business data?"

- **The startup ecosystem is different.** In the Delhi NCR startup ecosystem (Gurgaon, South Delhi, Noida), young founders are normal. A 22-year-old building a SaaS product is not unusual — it's expected. The credibility gap is smallest here.

- **"Build in public" works in India too.** Sharing the build journey on LinkedIn/Twitter, attending startup events, winning a hackathon — these build credibility among the startup crowd. They don't build credibility with dentists.

**Verdict: The founder's natural peer group is the startup/D2C ecosystem in Delhi NCR. The vertical must be one where this credibility advantage applies.**

### Break #6: Regulatory Environment

No HIPAA. No SOC 2 urgency. Instead:

- **DPDP Act 2023** (Digital Personal Data Protection Act): India's data protection law. Requires consent for data collection, data minimization, breach notification. Less prescriptive than GDPR, more than nothing. Compliance is achievable for a small startup.

- **No mandatory compliance certification** for B2B SaaS at pilot scale. SOC 2 is irrelevant for Indian SMBs.

- **RBI guidelines** for payment data: if we process payment data, we need to be aware of data localization requirements. But we're reading data (not processing payments), which reduces the burden.

**Verdict: Compliance burden is lighter. No SOC 2 distraction. DPDP compliance is manageable.**

### Break #7: Infrastructure

DigitalOcean Bangalore region exists. AWS Mumbai, GCP Delhi NCR. But:

- **GPU availability in India:** Limited. AWS Mumbai has GPU instances but expensive. Vast.ai doesn't have India presence. Self-hosted LLM is even less viable than before.

- **Latency:** Indian users connecting to OpenAI API (US) experience 200-300ms additional latency. Acceptable for batch decision generation, noticeable for real-time queries.

- **Cost:** Indian cloud pricing is comparable to US (AWS Mumbai ~5% premium over US East). But the founder's limited capital makes every dollar count.

**Verdict: OpenAI API remains the right call. India cloud region for the app (DigitalOcean Bangalore), but LLM inference stays on OpenAI API in US. Latency is acceptable for batch decisions.**

---

## Part 2: New Vertical Selection for India

Given the constraints — Delhi NCR, student founder, zero network, limited capital — I evaluate Indian verticals from first principles.

### Evaluation Framework (India-Specific)

Same seven criteria, but calibrated for Indian reality:

| Criterion | India Calibration |
|-----------|-------------------|
| Urgency of pain | Does the owner feel this pain *this week*? Indian businesses are more reactive — pain must be immediate. |
| Ease of integration | Can we access their data via API? If they use Tally (bad API), that's a problem. If they use Zoho/Razorpay (good API), that's good. |
| Measurable ROI | Can we point to ₹X saved or earned in a 2-month pilot? Indian owners need faster proof than US owners. |
| Sales cycle length | How fast can a student founder get a meeting? |
| Willingness to pay | Will they pay ₹5,000–15,000/mo after the pilot? |
| Data availability | How digital is this vertical? Indian businesses are less digitized than US equivalents. |
| Pilot comparability | Can 3 pilots in the same vertical use the same integration stack? |
| **NEW: Founder credibility** | Does the founder have natural credibility with this vertical? |

### Vertical Candidates

**A. D2C / E-commerce Brands (Delhi NCR)**

Delhi NCR is India's D2C capital. Hundreds of digitally-native brands in Gurgaon, Noida, South Delhi selling on Shopify, Amazon, Flipkart, and their own websites. Revenue: ₹1–50 Cr ($120K–$6M).

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **4** | Ad costs rising, attribution broken, inventory tied up in slow-moving SKUs. CAC:LTV ratio is existential for funded D2C brands. |
| Ease of integration | **5** | Shopify (excellent API), Razorpay (good API), Shiprocket/Delhivery (good API), Meta/Google Ads (good API), Zoho Books (good API). Merge.dev covers several. |
| Measurable ROI | **4** | "Pause these 3 underperforming ad sets → save ₹50K/mo." "Restock SKU X → ₹2L in missed revenue." Attribution is complex but directionally clear. |
| Sales cycle | **4** | D2C founders are 25-40, active on LinkedIn/Twitter, attend startup events. A student founder can get a meeting through a warm intro or event. |
| Willingness to pay | **3** | D2C margins are 30-60%. They pay for tools that drive revenue (Shopify, ad platforms, Klaviyo). A ₹10K/mo tool that demonstrably saves ₹50K in ad spend is an easy yes. |
| Data availability | **5** | All digital. Shopify orders, Razorpay transactions, ad platform data, shipping data. 1-3 years of history typically available. |
| Pilot comparability | **4** | Two apparel D2C brands + one food D2C brand share Shopify, Razorpay, and ad platforms. Different products but same data shape. |
| Founder credibility | **5** | This is the founder's peer group. Same age range, same ecosystem, same events. |
| **Composite** | **4.3** | |

**B. Small SaaS Companies (Delhi NCR / Bangalore)**

Bootstrapped or seed-stage SaaS companies with ₹50L–5Cr ARR. Use Stripe/Razorpay, Chargebee/Paddle, CRM, analytics.

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **3** | Churn is painful but slow-burn. Pricing optimization is valuable but not urgent. SaaS metrics move slowly. |
| Ease of integration | **5** | SaaS tools have the best APIs. But: many SaaS companies use Chargebee (complex billing models), making normalization harder. |
| Measurable ROI | **3** | "Improve trial conversion by 10%" is meaningful but takes 3-6 months to prove. Pilot timeline is too short. |
| Sales cycle | **3** | SaaS founders are accessible but cautious. "Let me see your metrics first" is a common objection. |
| Willingness to pay | **4** | SaaS founders understand SaaS pricing. If Cortex shows value, they'll pay ₹10-15K/mo. |
| Data availability | **5** | Excellent. But data volume is smaller (fewer transactions than D2C). |
| Pilot comparability | **3** | B2B SaaS and B2C SaaS have different metrics, different funnels. Harder to generalize. |
| Founder credibility | **5** | Peer group. Excellent fit. |
| **Composite** | **3.6** | |

**C. Professional Services Firms (CA, Architecture, Law, Consulting)**

Delhi NCR has thousands of mid-sized professional services firms. Use billing software, maybe a CRM, some project management.

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **2** | Billable hour leakage is real but invisible. Most firms don't know what they're losing. The pain isn't felt daily. |
| Ease of integration | **2** | Highly fragmented. Some use custom billing, some use spreadsheets, some use Tally. No standard tool stack. |
| Measurable ROI | **2** | Billable hour recovery is hard to prove in 2 months without baseline data. |
| Sales cycle | **3** | Senior partners are 45+. Credibility gap for a student founder is wide. |
| Willingness to pay | **3** | CA firms and law firms have money but spend it on people, not SaaS. |
| Data availability | **1** | Low digitization. Timesheets in Excel. Billing in Tally. |
| Pilot comparability | **1** | Every firm is different. No standard tool stack. |
| Founder credibility | **1** | Age/status gap is significant. |
| **Composite** | **1.9** | |

**D. Coaching / Test Prep Centers (Delhi NCR)**

Delhi is India's coaching capital. IIT-JEE, NEET, UPSC, CAT prep centers. Also: skill academies (coding bootcamps, design schools).

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **3** | Batch optimization, student churn, fee collection. Real but cyclical (admission-season spikes). |
| Ease of integration | **2** | Most use custom or semi-custom LMS + Razorpay + WhatsApp. No standard stack. WhatsApp is the CRM — unstructured. |
| Measurable ROI | **3** | "Fill 2 more batches this cycle = ₹5L" — real but seasonal. |
| Sales cycle | **4** | Coaching owners are accessible. Many are first-generation entrepreneurs. Less status-conscious than doctors/lawyers. |
| Willingness to pay | **2** | Thin margins (₹2K-20K/student). ₹10K/mo is significant. |
| Data availability | **1** | Student data is often in spreadsheets and WhatsApp groups. Not API-accessible. |
| Pilot comparability | **2** | IIT coaching ≠ CAT coaching ≠ coding bootcamp. Different models. |
| Founder credibility | **4** | Student founder has natural empathy with educators. |
| **Composite** | **2.6** | |

**E. Small Manufacturing / Exporters (NCR Industrial Belt)**

Gurgaon, Faridabad, Noida have thousands of small manufacturers and exporters. Use Tally, some use basic ERP, logistics tools.

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Urgency of pain | **3** | Inventory carrying cost, order fulfillment delays. Real but not digitally monitored. |
| Ease of integration | **1** | Tally (bad API) + spreadsheets. Very low digital maturity. |
| Measurable ROI | **3** | Inventory optimization has clear value. But requires clean data. |
| Sales cycle | **2** | Factory owners are 45+. Significant age/status gap. |
| Willingness to pay | **2** | Low. Manufacturing margins in India are 5-15%. Every rupee counts. |
| Data availability | **1** | Very low. Tally data is often incomplete. |
| Pilot comparability | **2** | Garments ≠ auto parts ≠ pharma. Very different businesses. |
| Founder credibility | **1** | High age/status gap. |
| **Composite** | **1.9** | |

### Composite Ranking

| Rank | Vertical | Score | Key Driver |
|------|----------|-------|------------|
| **1** | **D2C / E-commerce** | **4.3** | Founder's natural peer group. Excellent digital infrastructure. Fast sales cycle. |
| 2 | Small SaaS | 3.6 | Peer group, but slower ROI proof and more complex billing models. |
| 3 | Coaching / Test Prep | 2.6 | Accessible but low digitization and thin margins. |
| 4 | Professional Services | 1.9 | Low digitization, credibility gap, slow sales. |
| 5 | Manufacturing | 1.9 | Low digitization, credibility gap, thin margins. |

### Recommendation: D2C / E-commerce Brands in Delhi NCR

**Why this works for a student founder in Delhi:**

1. **Peer group access.** D2C founders in India are young (25-35), attend the same events, are active on the same platforms. A university student building a SaaS tool is credible here in a way they wouldn't be with doctors or factory owners.

2. **Digital infrastructure is excellent.** Shopify, Razorpay, Shiprocket, Meta/Google Ads — all have clean, well-documented APIs. Merge.dev covers several. The integration surface is the richest of any Indian vertical.

3. **Pain is urgent and measurable.** A D2C brand spending ₹5L/mo on Meta ads that are underperforming is losing ₹1-2L/month in provable waste. "Pause these ad sets, reallocate to these → save ₹1.2L" is a concrete, verifiable ROI story.

4. **Delhi NCR concentration.** Gurgaon alone has 200+ D2C brands. Events like D2C Insider Summit, Shopify Meetups, and e-commerce founder gatherings happen monthly within metro reach. The founder can attend 2-3 events per month without leaving the NCR.

5. **The "what happened" question is visceral.** "Why did my revenue drop 20% last month while my ad spend stayed the same?" — a D2C founder asks this constantly. Cortex can answer it by connecting Shopify (revenue), Razorpay (actual collections), and ad platforms (spend and attribution).

**Decision types for D2C v1 (replacing no-show/utilization):**

| Decision | Data Sources | ROI Estimation |
|----------|-------------|----------------|
| **Ad spend efficiency** | Meta Ads + Google Ads + Shopify revenue | ROAS by campaign → pause/scale recommendations |
| **Revenue anomaly detection** | Shopify + Razorpay | "Revenue dropped 18% this week. Here's what changed." |
| **Customer LTV vs CAC** | Shopify + ad platforms | "Customers from Instagram cost ₹X to acquire but spend ₹Y. Google customers: ₹A vs ₹B." |
| **Inventory slow-mover alert** | Shopify inventory + order velocity | "SKU X hasn't moved in 30 days. ₹1.5L tied up." |

---

## Part 3: India Pricing

Indian SMB SaaS follows different rules. Core principle: price in INR, benchmark against Indian alternatives, anchor to measurable savings not "COO replacement."

| Tier | Monthly (₹) | Monthly ($) | Max Integrations | Decision Types | Best For |
|------|------------|-------------|-----------------|----------------|----------|
| **Starter** | ₹4,999 | ~$60 | 3 | 3/day | ₹50L–2Cr revenue, single brand |
| **Growth** | ₹9,999 | ~$120 | 6 | 10/day | ₹2–10Cr, multi-channel |
| **Scale** | ₹19,999 | ~$240 | 10 | Unlimited | ₹10–50Cr, multi-brand |

**Pilot pricing:** Free for 2 months. Then ₹4,999/mo (Starter tier).

**Onboarding fee:** Free for pilots. ₹9,999 post-pilot.

**Justification:**
- ₹4,999/mo is comparable to Shopify India (₹1,499–5,599) and Zoho CRM (₹999–4,999). It positions Cortex as a premium SaaS tool, not an enterprise one.
- A D2C brand with ₹2Cr revenue (₹16.7L/mo) spending ₹5K/mo on Cortex = 0.3% of monthly revenue — affordable.
- The ROI math: if Cortex saves ₹50K in ad waste, that pays for 10 months of the Starter plan.

**Annual discount:** 15% (₹4,249/mo billed annually = ₹50,988/yr).

---

## Part 4: India Integration Stack

Rebuilt from first principles for Indian D2C:

| Priority | Tool | Category | API Quality | Connect Method | Why |
|----------|------|----------|-------------|----------------|-----|
| **P0** | Shopify | E-commerce | Excellent REST/GraphQL | Native + Webhook | Revenue, orders, products, customers — single source of truth |
| **P0** | Razorpay | Payments | Good REST API | Native + Webhook | Actual collections, refunds, payment method data |
| **P1** | Meta Ads API | Marketing | Good | Native or Merge.dev | Ad spend, ROAS, campaign performance |
| **P1** | Google Ads API | Marketing | Good | Native or Merge.dev | Search ad performance |
| **P2** | Shiprocket / Delhivery | Logistics | Good REST API | Native | Shipping costs, delivery performance, RTO rates |
| **P2** | Zoho Books | Accounting | Good REST API | Merge.dev or native | Expenses, P&L. (Tally users get CSV import bridge) |
| **P2** | Klaviyo / Mailchimp | Email marketing | Good API | Merge.dev | Email campaign revenue attribution |

**v1 MVP integrations (first 8 weeks):** Shopify + Razorpay + Meta Ads = 3 integrations. This covers the core loop: revenue data + ad spend data.

**The Tally problem:** If a pilot uses Tally instead of Zoho Books, we cannot integrate via API. The Tally API requires Tally to be running on a local machine and exposes data via XML over HTTP — it's fragile and not designed for cloud integration. The bridge: a simple CSV uploader. The pilot exports a Tally report once, Cortex ingests it. Not real-time, but sufficient for v1 pilot with manual refresh every week. If Tally is dominant among our pilots, we build a proper Tally connector in v2 using Tally Prime's XML API.

---

## Part 5: India Networking Strategy (Delhi NCR)

Complete rewrite of the acquisition strategy for Delhi NCR, student founder, zero network.

### Where D2C Founders Congregate in Delhi NCR

| Venue | Type | Frequency | Cost | Founder Fit |
|-------|------|-----------|------|-------------|
| D2C Insider events (Gurgaon) | Conference/meetup | Monthly | Free–₹2,000 | Excellent — largest D2C community in India |
| Shopify Meetups Delhi | Community meetup | Quarterly | Free | Excellent — Shopify users are our ICP |
| Incubator demo days (IIT Delhi, NSRCEL, etc.) | Startup events | Monthly | Free | Good — broad startup, some D2C |
| SaaS Insider / SaaSBOOMi Delhi chapters | Community | Monthly | Free–₹1,000 | Good — SaaS founders, adjacent |
| YourStory / Inc42 events | Media events | Quarterly | ₹500–2,000 | Good — broad startup audience |
| Twitter/X D2C community | Online | Daily | Free | Excellent — many Indian D2C founders are active here |
| LinkedIn D2C/startup groups | Online | Daily | Free | Good |
| LinkedIN Local Delhi | Networking | Monthly | Free–₹500 | Medium |
| TiE Delhi NCR | Mentorship network | Weekly events | ₹2,000/yr membership | Medium — more corporate but good connections |
| College entrepreneurship cells | Student events | Monthly | Free | Good for early practice, lower-quality leads |

### Revised Acquisition Phases (Delhi NCR)

**Phase 0 (Weeks 1–4): Build a D2C Network**

| Week | Activity | Cost |
|------|----------|------|
| 1 | Join D2C Insider community (free). Follow 20 D2C founders on Twitter/LinkedIn. Engage with their content (not pitch — comment thoughtfully). | ₹0 |
| 2 | Attend first D2C Insider meetup in Gurgaon. Don't pitch. Introduce yourself: "I'm a student building analytics for D2C brands. I'm here to learn how you manage your ad spend and revenue data." Collect 5-10 contacts. | ₹0–2,000 |
| 3 | Follow up with 3 most interesting contacts from the meetup. Offer: "Can I buy you chai and learn more about your ad-to-revenue tracking? 30 minutes." Not a sales meeting — a learning meeting. | ₹300 |
| 4 | Write a Twitter/LinkedIn thread about what you learned: "I spoke to 3 D2C founders this week. Here's what surprised me about how they track marketing ROI." This builds credibility. Engage with D2C community replies. | ₹0 |

**Phase 0 outcome:** 8-12 D2C founders who know the founder by name. 3-4 who've had substantive conversations. Zero pitches made.

**Phase 1 (Weeks 5–8): Warm the Leads While Building**

| Week | Activity | 
|------|----------|
| 5 | Send personal update to warm leads: "I'm building the ad spend dashboard we discussed. Here's a preview screenshot of what it looks like with Shopify + Meta data connected. Would love your feedback." |
| 6 | Attend second D2C event. You now have real product screenshots to show — not a pitch deck. "Here's what I'm building. Here's what 3 founders told me. Does this resonate?" |
| 7 | Reach out to 2 micro-agencies that run ads for D2C brands. They manage multiple brands' ad accounts. "I'm building a tool that shows cross-platform ROAS. Your clients would see which campaigns actually drive revenue." Potential referral channel. |
| 8 | Product functional (Shopify + Razorpay + Meta connected). Reach out to the 2-3 warmest leads: "Want to try it for free? I'll set it up in 1 hour. You just connect your Shopify and Razorpay." Target: 1-2 pilots. |

**Phase 2 (Weeks 9–12): Onboard and Refer**

| Week | Activity |
|------|----------|
| 9 | Pilot #1 onboarding. Sit with them (virtual or in-person in Gurgaon). Watch them connect tools. See their face when the first decision card appears. |
| 10 | Ask Pilot #1 for introductions. "Who else in your D2C circle complains about ad attribution?" |
| 11 | Pilot #2 onboarded (from referral). Pilot #1's ROI story is your sales collateral. |
| 12 | Pilot #3 onboarded. If referrals aren't producing, attend another D2C event — now with a working product and a real case study. |

### The Founder's Weekly Split (Delhi NCR)

| Activity | Hours/Week | Notes |
|----------|-----------|-------|
| Coding (product) | 25–30 | Mornings. Deep work. |
| Networking (events, DMs, chai meetings) | 8–10 | Afternoons. 1 event/week + follow-ups. |
| Pilot support | 3–5 | Grows as pilots onboard. |
| Strategy/writing/content | 3–5 | Build-in-public content on LinkedIn/Twitter. |
| **Total** | **40–50** | Sustainable. Student schedule is flexible — use this advantage. |

### Cost Estimate (First 12 Weeks)

| Category | Cost (₹) | Notes |
|----------|--------|-------|
| Event tickets/registrations | ₹5,000 | 4-5 events |
| Travel (Delhi Metro, auto) | ₹3,000 | Local NCR travel |
| Chai/coffee meetings | ₹2,000 | 6-8 meetings |
| DigitalOcean (Bangalore) | ₹2,500/mo × 3 = ₹7,500 | App hosting |
| OpenAI API | ₹1,500/mo × 3 = ₹4,500 | LLM inference |
| **Total** | **₹22,000** | ~$260 USD for 12 weeks |

This is the advantage of India: pilot acquisition costs are near-zero when the founder is local and the events are free.

---

## Part 6: Updated Decision Record

This supersedes all previous decisions. The following are locked for v1 India:

| Decision | Previous (US) | Updated (India) | Rationale |
|----------|--------------|-----------------|-----------|
| **Vertical** | Multi-location healthcare | D2C/e-commerce brands | Founder's natural peer group. Best digital infra in India. Fastest sales cycle. Delhi NCR concentration. |
| **Pricing** | $500–2,500/mo | ₹4,999–19,999/mo ($60–240) | Calibrated to Indian SMB SaaS benchmarks and D2C revenue levels |
| **Pilot pricing** | Free 2 months → $500/mo | Free 2 months → ₹4,999/mo | Same structure, India price point |
| **Onboarding fee** | $2,000 (post-pilot) | ₹9,999 (post-pilot) | Recovering cost at ~₹500/hr for ~20 hours |
| **LLM** | OpenAI API | OpenAI API (unchanged) | Still the right call. India GPU availability is worse, not better |
| **Integrations (v1)** | Stripe, QuickBooks, Calendly | Shopify, Razorpay, Meta Ads | Rebuilt for Indian D2C stack |
| **Infrastructure** | DigitalOcean US | DigitalOcean Bangalore region | India region for lower latency |
| **Networking** | Healthcare study clubs | D2C Insider events, Shopify Meetups, Twitter/LinkedIn D2C community | Rebuilt for Delhi NCR D2C ecosystem |
| **Compliance** | SOC 2 (mo 18) | DPDP Act 2023 compliance (mo 6) | No HIPAA, no SOC 2 urgency |
| **Decision types (v1)** | No-show risk, booking gap, churn, cash flow | Ad spend efficiency, revenue anomaly, LTV:CAC, inventory alerts | Rebuilt for D2C economics |
| **Database** | Plain PostgreSQL | Plain PostgreSQL (unchanged) | Same architecture |
| **Agents** | Celery task chain | Celery task chain (unchanged) | Same simplified approach |
| **Causal engine** | Deferred to v2 | Deferred to v2 (unchanged) | Same decision |
| **Infra cost (6 months)** | ~$4,450 | ~₹60,000 ($720) | India cloud + lower usage at pilot scale |

---

## Part 7: What Stays the Same

Not everything changes. The core product architecture is robust across geographies:

- AI architecture (two-tier LLM, living business model, simulation engine) — unchanged
- Agent architecture (LangGraph → Celery simplification) — unchanged
- Data pipeline architecture (Daft, normalization, entity resolution) — unchanged, just different source APIs
- System architecture (FastAPI, PostgreSQL, Docker Compose) — unchanged
- Security architecture (schema-per-tenant, encryption) — unchanged
- The core insight: connect data → detect patterns → recommend decisions → measure outcomes — unchanged

---

## Part 8: Risks Specific to India

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| D2C brands churn after ad spend optimization (they got the one thing they needed) | Medium | Medium | Layer additional decision types quickly. LTV:CAC, inventory, pricing. Never be a one-trick tool. |
| Shopify + Razorpay integration is insufficient (pilots want more tools connected) | Medium | Medium | v1 scope is tight for a reason. Add Shiprocket and Meta Ads in Phase 2 based on pilot demand. |
| Tally dominance blocks accounting integration | Medium | Low | Zoho Books is growing fast among D2C. If pilot uses Tally, offer CSV import bridge. If all 3 use Tally, build Tally XML connector in Phase 2. |
| Indian D2C market consolidates or funding winter reduces willingness to pay | Low | Medium | Target bootstrapped D2C brands (they need efficiency more than funded ones). Also: ₹5K/mo is affordable even in a downturn if ROI is proven. |
| Student founder credibility doesn't translate to paid conversions | Medium | High | Free pilot period proves value before payment. If the product works, the price is small relative to the savings. The founder's age becomes irrelevant when ROI is visible. |
| DPDP Act compliance becomes burdensome | Low | Low | The Act is still being implemented. Consent and data minimization are straightforward. Consult a law student peer for guidance (Delhi has excellent law schools — leverage the university ecosystem). |

---

## Part 9: Updated 6-Month Budget

| Month | Activity | Infra (₹) | API (₹) | Events/Travel (₹) | Total (₹) |
|-------|----------|----------|---------|--------------------|----------|
| 1 | Build + begin networking | 2,500 | 500 | 1,000 | 4,000 |
| 2 | Build + networking | 2,500 | 1,000 | 1,500 | 5,000 |
| 3 | Build + Pilot 1 | 3,000 | 1,500 | 1,000 | 5,500 |
| 4 | Pilots 1-2 | 3,500 | 2,000 | 1,500 | 7,000 |
| 5 | Pilots 1-3 | 4,000 | 2,500 | 1,000 | 7,500 |
| 6 | Stabilize, convert | 4,000 | 3,000 | 500 | 7,500 |

**Total 6-month burn: ~₹36,500 ($440 USD)**

This assumes the founder has a laptop, internet, and basic living costs covered separately. The ₹36,500 is purely business infrastructure + events. At $440 total, this is bootstrap-friendly for a student with even modest savings or a small stipend.

---

*This document is the binding India-context plan for Cortex v1. All previous GTM, pricing, vertical, and integration documents are superseded. The core product architecture documents remain valid. Begin execution from here.*
