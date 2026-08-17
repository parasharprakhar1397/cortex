# Cortex v1 — Product Specification

> **Revision 1 — Founding Systems Architect**
> **Status: Implementation-ready. This is the contract between strategy and engineering.**
> **Target: Buildable by 1 engineer (the founder) in 8-10 weeks.**

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [User Personas](#2-user-personas)
3. [User Journey — Full Specification](#3-user-journey--full-specification)
   - [3.1 Onboarding (First Session, Day 0)](#31-onboarding-first-session-day-0)
   - [3.2 Daily Use (Ongoing)](#32-daily-use-ongoing)
   - [3.3 Simulation (v1 Simple Version)](#33-simulation-v1-simple-version)
4. [v1 Feature List — Prioritized](#4-v1-feature-list--prioritized)
5. [Integration Specifications](#5-integration-specifications)
6. [Decision Type Specifications](#6-decision-type-specifications)
7. [Data Model Specification](#7-data-model-specification)
8. [API Specification](#8-api-specification)
9. [Dashboard & UI Specification](#9-dashboard--ui-specification)
10. [Success Metrics & Testing Criteria](#10-success-metrics--testing-criteria)
11. [v1 Out-of-Scope (Explicit)](#11-v1-out-of-scope-explicit)

---

## 1. Product Overview

### What Cortex v1 Is

Cortex v1 is an **autonomous decision-support system** that connects to a multi-location healthcare practice's existing software (PMS, payment gateway, accounting) and proactively surfaces operational decisions with estimated ROI. It is NOT a chatbot, a dashboard builder, or a general-purpose analytics tool. It is a **decision engine**: it tells the practice owner what to do, why, and what it's worth.

### What Cortex v1 Is NOT

- **NOT a chatbot.** There is no chat interface. Users do not type questions. Cortex surfaces decisions proactively.
- **NOT a BI dashboard.** There are no drag-and-drop widgets, no SQL query builder, no custom chart configuration.
- **NOT a practice management system.** Cortex does not book appointments, send invoices, or process payments. It reads data from tools that do those things.
- **NOT an AI co-pilot.** It does not wait to be asked. It monitors data continuously and pushes decisions to the owner.
- **NOT multi-vertical.** v1 supports healthcare practices only. D2C/e-commerce is the documented fallback but is not built into v1.

### Core User Promise

> **Cortex finds missed revenue in your practice operations and tells you exactly how to recover it — before you even know to look.**

Every recommendation answers five questions:

| Question | What the User Sees |
|----------|-------------------|
| **What happened?** | "Your no-show rate for Tuesday slots with Dr. Sharma is 22% — 3× your practice average." |
| **Why did it happen?** | "Dr. Sharma's Tuesday patients are primarily from Sector 14 (55% of panel). Average travel time to your Gurgaon clinic is 45+ minutes in morning traffic." |
| **What should I do?** | "Offer Dr. Sharma's Tuesday patients a ₹100 discount to switch to afternoon slots, or send automated reminder calls at 8 AM instead of 6 PM." |
| **What's the expected ROI?** | "Recovering 40% of Tuesday no-shows = ₹34,000/month. Implementation cost: ₹0 (use existing SMS gateway)." |
| **How confident is this?** | "Confidence: 78% (based on 34 observations, p=0.003). Data freshness: Appointment data synced 15 minutes ago." |

### v1 Scope Boundary

**IN SCOPE:**
- 3 integrations: PMS (Practo/DocEngage/Lybrate), Razorpay, Zoho Books (with Tally CSV fallback)
- 4 decision types: No-Show Prediction, Scheduling Gap Detection, Revenue Trend Analysis, Pricing Optimization
- Web dashboard (desktop-first, mobile-responsive secondary)
- Morning digest email (one email per day, 6:00 AM IST)
- Simple single-variable simulation ("What if I changed X by Y%?")
- Feedback loop (✓ Useful / ✗ Not Useful / Already Knew / Implemented)
- Multi-tenancy (schema-per-tenant in PostgreSQL)
- Pilot management (usage tracking, onboarding flow, calibration survey)

**EXPLICITLY OUT OF SCOPE:**
- LangGraph multi-agent system (we use 2-function Celery task chain)
- Causal inference engine (DoWhy/EconML deferred to v2)
- Self-hosted LLM (OpenAI API only: GPT-4o-mini for routine, GPT-4o for complex)
- TimescaleDB + pgvector (add only if query performance demands it — start with plain PostgreSQL)
- GPU infrastructure (no GPU servers)
- Mobile app (responsive web only)
- Slack/WhatsApp integration
- Multi-vertical support
- Marketplace for third-party decision modules
- Monte Carlo simulation (formula-based only)
- Voice interface
- Automated action execution (Cortex does not book, cancel, or modify anything)
- Peer benchmarking ("How do I compare to other dental practices?")
- White-label or embedded version

---

## 2. User Personas

### Primary Persona: Multi-Location Practice Owner

| Attribute | Detail |
|-----------|--------|
| **Name (archetype)** | Dr. Rajesh Kumar |
| **Age** | 38-48 |
| **Role** | Owner / Senior Dentist at "SmileCare Dental" — 3 locations across Gurgaon and South Delhi |
| **Revenue** | ₹3-8Cr annual (₹25-67L/month) |
| **Staff** | 12-25 (5-8 dentists, 3-5 hygienists, 4-8 support staff, 1-2 office managers) |
| **Tech stack** | Practo Prime for PMS, Razorpay for payments, Zoho Books for accounting, WhatsApp for patient communication |
| **Pain points** | "I know I'm losing money to no-shows and empty slots, but I don't have time to analyze it. My office manager tells me 'it was a slow week' but I don't know if it's a trend or a blip. One of my locations always underperforms and I can't figure out why." |
| **Daily routine** | Checks WhatsApp first thing. Reviews previous day's collections (office manager sends a WhatsApp message). Sees patients 10:00 AM–4:00 PM. Reviews business metrics in evening (if at all). Attends to business operations on weekends. |
| **Decision-making style** | Intuitive, experience-based. Makes operational decisions based on gut feel + spot checks. Does not use analytics tools. "I don't have time for dashboards." |
| **Technology comfort** | Uses smartphone heavily (WhatsApp, UPI, Instagram). Comfortable with Practo and Razorpay. Has never used an analytics tool. Distrusts "AI" hype but respects concrete results. |
| **Buying behavior** | Pays ₹3,000-8,000/mo for Practo. Pays per-transaction for Razorpay. Would pay for tools that demonstrably recover revenue. Needs to see ROI before committing. |
| **Objections** | "Another tool to check? I already have too many." "Is my patient data safe?" "Will this take time away from seeing patients?" "Show me proof it works for practices like mine." |

### Secondary Persona: Practice Manager / Office Manager

| Attribute | Detail |
|-----------|--------|
| **Name (archetype)** | Priya Sharma |
| **Age** | 28-35 |
| **Role** | Office Manager at SmileCare Dental (Gurgaon location) |
| **Reports to** | Dr. Rajesh Kumar |
| **Daily tools** | Practo (appointment scheduling, patient check-in), Razorpay (payment reconciliation), Excel (daily collection report, no-show tracking) |
| **Pain points** | "I spend 45 minutes every evening reconciling Practo appointments with Razorpay payments to tell Dr. Kumar what happened today. I know some patterns — like Tuesday mornings always have gaps — but I can't prove it with numbers and I can't prioritize what to fix." |
| **Daily routine** | Arrives 9:00 AM. Checks today's appointments, calls yesterday's no-shows for rescheduling. Manages front desk. End of day: prepares WhatsApp summary for Dr. Kumar. |
| **Technology comfort** | Comfortable with Practo. Uses Excel daily. Has WhatsApp on desktop. Would use a dashboard if it saved her 45 minutes of manual reconciliation. |
| **Role with Cortex** | Primary dashboard user. Checks decision cards every morning. Implements recommendations (sends reminder calls, adjusts scheduling). Marks decisions as implemented. Reports ROI numbers back to Dr. Kumar. |

### Context: Indian Healthcare, Delhi NCR

- **Cultural note:** Age and status hierarchies are real. The founder (student, 20-22) will NOT sell directly to Dr. Kumar. Sales go through practice management consultants or warm introductions from healthtech networks. The product must sell itself through demonstrable ROI — not through founder credibility.
- **Regulatory:** DPDP Act 2023 compliance required (consent, data minimization, breach notification). No HIPAA. No SOC 2.
- **Pricing psychology:** Healthcare practice owners in India evaluate software against tangible benefits: "Does this recover more money than it costs?" Not against "platform value" or "strategic insight." The ROI case must be immediate and concrete.
- **Work hours:** Practice hours are typically 9:00 AM–8:00 PM (Mon-Sat). Sunday is closed or half-day. The morning digest must arrive before 9:00 AM IST on working days.

---

## 3. User Journey — Full Specification

### 3.1 Onboarding (First Session, Day 0)

#### 3.1.1 Landing Page and Signup Flow

**Entry point:** `https://cortexapp.in` (or the live preview URL during development)

**Landing page content (v1 — minimal, conversion-focused):**

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│                    Cortex                                        │
│     AI-powered decisions for your practice.                      │
│                                                                  │
│   "We found ₹1.2L in missed revenue last month                   │
│    for a 3-location dental practice in Gurgaon."                 │
│                                                                  │
│   No dashboards. No reports. Just decisions you can act on.      │
│                                                                  │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ [Sign up free — 2 minutes]                                │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│   ✓ Free for 2 months    ✓ No credit card required              │
│   ✓ Connects to Practo, Razorpay, Zoho Books                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Signup flow (3 screens, <2 minutes):**

**Screen 1: Account creation**
- Fields: Full name, email, password (min 8 chars), practice name, mobile number (optional, for WhatsApp alerts in v2)
- OAuth option: Sign up with Google (uses Clerk)
- Submit → Clerk creates account, sends verification email
- After email verification → proceed to Screen 2

**Screen 2: Practice profile**
- Fields:
  - Practice type: dropdown [Dental, Physiotherapy, Diagnostic Center, Eye Care, Other]
  - Number of locations: number input [2-10]
  - Approximate annual revenue: dropdown [₹50L-1Cr, ₹1-3Cr, ₹3-5Cr, ₹5-10Cr, ₹10-20Cr, ₹20Cr+]
  - Number of providers (doctors/therapists): number input
  - City: text input (auto-suggest Delhi NCR cities)
- Submit → creates `practices` record in tenant schema

**Screen 3: Goals survey**
- "What are your top 3 operational goals?" (checkboxes, select up to 3):
  - Reduce patient no-shows
  - Fill empty appointment slots
  - Improve revenue per patient
  - Optimize pricing for services
  - Better understand revenue trends
  - Reduce staff idle time
- "What keeps you up at night about your practice?" (free text, optional)
- "How did you hear about Cortex?" (dropdown: Consultant referral, Healthtech event, LinkedIn/Twitter, Friend/colleague, Google search, Other)
- Submit → proceeds to integration wizard

#### 3.1.2 Integration Connection Wizard

**Design principle:** The wizard is a linear flow with clear progress indicator. Each integration is connected one at a time. The user cannot skip ahead. This prevents the "connect everything at once and nothing works" failure mode.

**Progress indicator** (persistent across wizard screens):

```
┌─────────────────────────────────────────────────────────────────┐
│  Setup Progress:  ○ Practice Profile  ● Connect Tools  ○ First Insights  │
└─────────────────────────────────────────────────────────────────┘
```

**Screen: Connect Your Tools**

Title: "Connect the tools you already use"

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Based on your practice (3-location Dental, ₹3-8Cr revenue),    │
│  we recommend connecting these tools:                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Step 1 of 3: Practice Management                           │ │
│  │                                                            │ │
│  │  ○ Practo         [Connect]  ← Your appointment data       │ │
│  │  ○ DocEngage      [Connect]                                │ │
│  │  ○ Lybrate        [Connect]                                │ │
│  │  ○ Other          [Enter manually]                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Step 2 of 3: Payments (Coming after Step 1)                │ │
│  │                                                            │ │
│  │  ○ Razorpay       [Locked until Step 1 complete]           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Step 3 of 3: Accounting (Coming after Step 2)              │ │
│  │                                                            │ │
│  │  ○ Zoho Books     [Locked until Step 2 complete]           │ │
│  │  ○ Tally (CSV)    [Locked until Step 2 complete]           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  We never store your passwords. Data is read-only.               │
│  You can disconnect any tool at any time.                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

#### 3.1.3 OAuth Flow for Each Integration

**PMS (Practo, DocEngage, or Lybrate):**

1. User clicks [Connect] for their PMS
2. Redirect to PMS OAuth consent screen (opens in new tab or popup)
3. PMS shows: "Cortex would like to: Read your appointments, Read patient records, Read provider schedules. Cortex will NOT: Modify appointments, Access patient clinical notes, Send messages on your behalf."
4. User approves → PMS redirects to Cortex callback URL with authorization code
5. Cortex exchanges code for access token + refresh token
6. Cortex stores encrypted tokens in `credentials` table
7. On success: wizard shows "✅ Practo connected. Found 2,847 appointments and 1,203 patients."
8. On failure: wizard shows error state (see Error States below)
9. Auto-advances to Step 2 (Razorpay) after 3 seconds

**Razorpay:**

1. User clicks [Connect]
2. Redirect to Razorpay OAuth consent screen
3. Razorpay shows: "Cortex would like to: Read your payments, Read your settlements, Read your refunds."
4. User approves → Razorpay redirects with authorization code
5. Cortex exchanges code, stores tokens
6. On success: "✅ Razorpay connected. Found 4,521 payments and 312 refunds."
7. Auto-advances to Step 3

**Zoho Books (or Tally CSV fallback):**

1. **Zoho Books path:** OAuth flow identical to above. "Read your invoices, Read your chart of accounts, Read your contacts."
2. **Tally CSV path:** User sees upload screen instead of OAuth:
   - "Tally doesn't support direct cloud connection. Please export your data as CSV."
   - Instructions: "In Tally Prime: Gateway of Tally → Display → Day Book → Export → CSV. Upload the file below."
   - File upload area (drag-and-drop, max 50MB)
   - "Upload frequency: We recommend uploading a fresh CSV every week for accurate insights. We'll remind you."
   - After upload: basic validation (checks column headers match expected format), shows row count, warns if data looks incomplete
3. On success: "✅ Accounting data connected. Found 856 invoices and 2,103 line items."

**Post-integration summary:**

```
┌──────────────────────────────────────────────────────────────────┐
│  ✅ All 3 tools connected!                                       │
│                                                                  │
│  📊 Data snapshot:                                                │
│     • 2,847 appointments (12 months history)                     │
│     • 1,203 patients                                             │
│     • 8 providers                                                │
│     • 4,521 payment transactions                                 │
│     • 856 invoices                                               │
│                                                                  │
│  We're now building your practice model. This usually takes       │
│  5-15 minutes. You'll receive an email when your first insights   │
│  are ready, or you can watch progress below.                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ████████████░░░░░░░░░░  52% — Analyzing appointment patterns│  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

#### 3.1.4 Data Discovery and Initial Sync

**What happens in the background (transparent to user):**

1. **Data pull (minutes 0-5):** Celery workers pull historical data from all connected tools. For each tool: pull up to 2 years of history (if available), paginating through API results. Raw data written to S3/MinIO as Parquet.
2. **Normalization (minutes 2-8):** Schema mappers convert PMS/Razorpay/Zoho Books data to unified entity model. Type coercion (Razorpay amounts in paise → rupees), date parsing, status mapping.
3. **Entity resolution (minutes 5-12):** Match patients across PMS → Razorpay → Zoho Books using exact email match. Where email is not available in PMS (some patients don't provide email), leave unresolved. Flag low-confidence entities for manual review later.
4. **Metric computation (minutes 8-15):** Derive baseline metrics: appointments per day, no-show rate, revenue per appointment, utilization rate, collections rate. Store in `metric_values` table.

**Progress indicator shown to user:**

A simple progress bar with 4 labeled stages:

1. `○ Pulling data from Practo...` → `● Pulling data from Practo... Done (2,847 records)`
2. `○ Normalizing data...` → `● Normalizing data... Done`
3. `○ Matching patient records...` → `● Matching patient records... 1,180 of 1,203 matched (98%)`
4. `○ Computing baseline metrics...` → progress bar fills

**Estimated time display:** "Usually takes 5-15 minutes. We'll email you at [email] when your first insights are ready."

**If the user closes the browser during sync:**
- Sync continues in background (Celery tasks)
- When sync completes, system sends email: "Your Cortex insights are ready! View your first decisions → [link to dashboard]"
- When user returns to dashboard, if sync is still in progress, they see the progress indicator. If sync is complete, they see their dashboard with the first decision cards.

**Error states during initial sync:**

| Error | User Sees | System Behavior |
|-------|-----------|-----------------|
| PMS OAuth fails (user denies permission) | "Connection to Practo was not authorized. You can try again or skip for now. Without your PMS data, Cortex won't be able to analyze appointments or no-shows." | Mark integration as `failed_auth`. Allow user to retry or skip. If user skips PMS, show warning that decision types requiring PMS data will be unavailable. |
| API returns HTTP 500 / timeout during data pull | "We're having trouble pulling data from Razorpay. This is usually temporary. We'll retry automatically in 5 minutes. [Retry Now] [Skip for Now]" | Retry with exponential backoff (3 attempts: 5 min, 15 min, 45 min). After 3 failures, mark integration as `degraded`. |
| Data sync times out (>30 minutes for initial sync) | "Initial sync is taking longer than expected. This can happen with larger practices. We're still working — you'll receive an email when complete. Feel free to explore Cortex in the meantime." | Continue sync in background. Show partial dashboard (whatever data has been processed so far) with a "Data still syncing" banner. |
| Entity resolution produces low-confidence matches (<70% of patients matched) | No user-facing error. System surfaces this as a data quality note on the dashboard: "We matched 65% of your patient records across tools. Some insights may be incomplete. [Review unmatched records]" | Log low resolution rate. Decisions that depend on cross-tool entity resolution show reduced confidence. Provide a "Review and merge" UI in Settings where users can manually match unresolved entities. |
| PMS has no API (user selected "Other") | "We don't have a direct connection for your PMS yet. You can upload appointment data as CSV, or we can build a custom connector. [Upload CSV] [Request Custom Connector]" | Store as `integration_type: csv_upload`. Decisions requiring PMS data are limited to what's in the CSV. |
| Tally CSV upload fails validation | "The uploaded file doesn't match the expected Tally export format. Expected columns: Date, Voucher Type, Ledger, Amount. Found: [list of actual columns]. Please re-export from Tally using the instructions above." | Reject the upload. Do not process. |

#### 3.1.5 Calibration Survey

Shown after integrations are connected, while initial sync is in progress. Can be completed now or skipped.

**Survey content:**

1. "How do you currently track no-shows?" (Dropdown: We don't track them systematically / Office manager keeps a log / We get reports from our PMS / Other)
2. "What does a single no-show cost your practice, on average?" (Number input, ₹, default: ₹1,500)
3. "What's your target monthly revenue?" (Number input, ₹, optional)
4. "Which day of the week is typically busiest?" (Dropdown: Mon-Sat)
5. "Do you send appointment reminders to patients?" (Yes, automated / Yes, manual calls/SMS / No)
6. "What's your biggest operational frustration?" (Free text)

**Purpose:** Provides calibration inputs for decision algorithms. For example: if the owner says a no-show costs ₹2,000, Cortex uses that instead of a default estimate. If they don't send reminders, the "Send reminder" recommendation becomes higher priority.

#### 3.1.6 First Insight Delivery

**Timing:** First decision card appears within 15 minutes of completing integration setup (assuming sync completes within that window). If sync takes longer, first insights appear when sync finishes.

**What the user sees:**

- Email notification (if they left the page): "Your first Cortex insights are ready"
- Dashboard loads with 1-3 decision cards (whatever the system can generate from initial data)
- Welcome banner: "Here's what we found in your practice data, Dr. Kumar. These insights are based on the last 12 months of appointments and payments."

**Minimum viable first insight:** Even with partial data, the system should surface at least one decision. Priority order for first insights:
1. No-show pattern (if PMS data is available — only requires appointment status history)
2. Revenue trend (if PMS + Razorpay data is available — compares recent revenue to historical average)
3. Scheduling gap (if PMS data is available — looks at next 7 days vs. historical patterns)

**If NO data is available yet (sync still in progress):** Show loading state with specific status: "Analyzing your appointment data from Practo (1,847 of 2,847 records processed)..."

**If sync completed but no decisions could be generated:** "We've processed your data but need a bit more history to generate reliable insights. We'll continue monitoring and alert you when patterns emerge. This usually takes 1-2 more days of data." This is the "cold start" case — the practice has too little data or the data is too sparse/irregular.

---

### 3.2 Daily Use (Ongoing)

#### 3.2.1 Dashboard

**URL:** `https://cortexapp.in/dashboard`

**What the user sees on load:**

```
┌──────────────────────────────────────────────────────────────────────┐
│  ☀️ Good morning, Dr. Kumar                    Thursday, 15 Jul 2026 │
│                                                                      │
│  SmileCare Dental — All Locations                                    │
│                                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ Revenue MTD   │ │ No-Show Rate │ │ Utilization  │ │ Collections │ │
│  │ ₹18.4L        │ │ 7.2% (↓1.1%) │ │ 68% (-4%)    │ │ 94% (+2%)   │ │
│  │ vs ₹16.8L est │ │ vs 8.3% avg  │ │ vs 72% goal  │ │ of billed    │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
│                                                                      │
│  ⚡ Today's Decisions                                        3 cards  │
│  ┌──────────────────────────────────────────────────────────────────┐│
│  │ 🔴 HIGH ROI  │ ₹34K/mo │ Recover 40% of Tuesday no-shows        ││
│  │ 78% confidence│          │ Dr. Sharma's morning slots —          ││
│  │              │          │ reminder calls + time change           ││
│  │              │          │                     [View Analysis ▸]  ││
│  ├──────────────────────────────────────────────────────────────────┤│
│  │ 🟡 MEDIUM ROI│ ₹12K/wk │ Fill Thursday afternoon gaps at        ││
│  │ 64% confidence│          │ Gurgaon location                      ││
│  │              │          │                     [View Analysis ▸]  ││
│  ├──────────────────────────────────────────────────────────────────┤│
│  │ 🟡 MEDIUM ROI│ ₹8K/mo  │ Revenue dip detected — 3-day trend     ││
│  │ 55% confidence│          │                     [View Analysis ▸]  ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  📊 Simulation Quick-Start                                           │
│  "What if I [changed no-show rate ▼] by [ -20% ▼] ?"    [Run ▸]     │
│                                                                      │
│  📋 Recent Activity                                    [View All ▸]  │
│  • Priya marked "Fill Thursday gaps" as Implemented — 2 hours ago    │
│  • New Razorpay data synced — 14 payments, 2 refunds — 15 min ago    │
│  • No-show alert: 3 cancellations today at South Delhi location      │
└──────────────────────────────────────────────────────────────────────┘
```

**Metric cards (top row) — specifications:**

| Metric | Computation | Refresh | States |
|--------|-----------|---------|--------|
| **Revenue MTD** | Sum of all Razorpay payment amounts where `paid_at` is in current month + sum of all Zoho Books invoice amounts marked as `paid` in current month (deduplicate on linked entities). Compare to: linear projection of last month's revenue × (days elapsed / total days). Show % difference. | Every 15 minutes (on new payment webhook or batch sync) | **Loading:** skeleton pulse animation. **No data:** "No revenue data yet — connect Razorpay." **Error:** "Unable to load — retrying." **Zero:** "₹0 (no payments this month)" |
| **No-Show Rate** | Count of PMS appointments with `status = 'no_show'` in current week ÷ total completed + no-show appointments. Compare to: trailing 4-week average. Show % difference with arrow (↓ good, ↑ bad). | Every hour (or on PMS webhook if available) | **Loading:** skeleton. **No data:** "No appointment data yet — connect your PMS." **Zero:** "0% — no no-shows this week! 🎉" |
| **Utilization** | Sum of scheduled appointment minutes ÷ (number of providers × available minutes per day × days in period). Available minutes = practice hours minus lunch break. For each provider, compute individual utilization. Show practice average. Compare to: goal set in calibration survey (default: 75%). | Every hour | **Loading:** skeleton. **Below goal:** yellow warning indicator. **Above goal:** green. |
| **Collections Rate** | Sum of paid invoice amounts ÷ sum of total invoiced amounts in trailing 30 days. Paid = payment exists with linked invoice. Total = all invoices issued. | Every hour | **Loading:** skeleton. **Below 90%:** red indicator. **90-95%:** yellow. **95%+:** green. |

**Location filter:**

A dropdown in the top bar: "📍 All Locations ▾" → expands to show individual locations: "All Locations", "Gurgaon Clinic", "South Delhi Clinic", "Noida Clinic". Selecting a location filters all metrics and decisions to that location. Multi-select is NOT supported in v1.

**Date range:** Default is "This week." Not configurable in v1 dashboard view (configurable in decision detail view for trend analysis).

#### 3.2.2 Decision Cards — Full Specification

Each decision card is a compact unit of insight. Cards appear on the dashboard in a list ranked by `estimated_roi × confidence`.

**Card anatomy (collapsed view — dashboard):**

```
┌──────────────────────────────────────────────────────────────────────┐
│ 🔴 HIGH ROI    │ ₹34,000/month estimated savings                     │
│ ───────────────────────────────────────────────────────────────────  │
│ Recover 40% of Tuesday no-shows in Dr. Sharma's morning slots        │
│                                                                      │
│ 5 of 23 Tuesday morning appointments were no-shows last month (22%). │
│ Practice average: 7.2%. Primary cause: Dr. Sharma's Tuesday patients │
│ are from Sector 14 (11+ km travel).                                  │
│                                                                      │
│ Suggested action: Send automated morning-of reminder calls + offer   │
│ ₹100 discount to reschedule to afternoon.                            │
│                                                                      │
│ Confidence: ████████░░ 78%  │  Based on 34 observations (p=0.003)   │
│                                                                      │
│ [View Full Analysis ▸]            [✓ Implemented]  [✗ Dismiss]      │
└──────────────────────────────────────────────────────────────────────┘
```

**Card anatomy (expanded view — decision detail page):**

URL: `https://cortexapp.in/decisions/:id`

```
┌──────────────────────────────────────────────────────────────────────┐
│ ← Back to Dashboard                                                  │
│                                                                      │
│ Recover 40% of Tuesday no-shows in Dr. Sharma's morning slots        │
│ 🔴 HIGH ROI · ₹34,000/mo · Confidence: 78%                          │
│ Generated: Today, 6:00 AM  ·  Data as of: 15 min ago                │
│ ───────────────────────────────────────────────────────────────────  │
│                                                                      │
│ 📊 WHAT HAPPENED                                                     │
│ ┌────────────────────────────────────────────────────────────────┐   │
│ │ No-Show Rate by Day of Week (Last 30 days)                     │   │
│ │                                                                 │   │
│ │  Mon ████████ 8.1%                                              │   │
│ │  Tue ████████████████████ 22.0%  ← Anomaly                     │   │
│ │  Wed ██████ 6.5%                                                │   │
│ │  Thu ███████ 7.2%                                               │   │
│ │  Fri █████ 5.8%                                                 │   │
│ │  Sat ██████ 6.1%                                                │   │
│ │                                                                 │   │
│ │ Source: Practo appointments (847 records, last 30 days)         │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ 🤔 WHY IT'S HAPPENING                                                │
│ ┌────────────────────────────────────────────────────────────────┐   │
│ │ Tuesday no-shows are concentrated in 9:00 AM–12:00 PM slots     │   │
│ │ (18 of 23 no-shows). These slots are all Dr. Sharma's.          │   │
│ │                                                                 │   │
│ │ Patient location analysis (from registration data):              │   │
│ │ • 55% of Dr. Sharma's Tuesday patients live in Sector 14-17     │   │
│ │ • Average travel time to Gurgaon clinic: 45+ min in AM traffic  │   │
│ │ • Non-Tuesday patients: 80% live within 5 km of clinic          │   │
│ │                                                                 │   │
│ │ Statistical test: Chi-squared test for Tuesday vs. other days   │   │
│ │ p = 0.003 (effect is real, not random chance)                    │   │
│ │ N = 34 Tuesday appointments in the analysis window               │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ 💡 WHAT TO DO                                                        │
│ ┌────────────────────────────────────────────────────────────────┐   │
│ │ RECOMMENDED ACTIONS (do both for maximum impact):               │   │
│ │                                                                 │   │
│ │ 1. Send morning-of reminder calls (automated)                   │   │
│ │    → Use Practo's SMS feature at 7:30 AM instead of 6:00 PM     │   │
│ │    → Add travel-time aware message: "Your appointment with      │   │
│ │      Dr. Sharma is at 10 AM. Travel time from Sector 14 is      │   │
│ │      ~45 min. See you soon!"                                    │   │
│ │    → Cost: ₹0 (existing Practo SMS credits)                     │   │
│ │    → Expected impact: Reduce Tuesday no-shows by 25-35%         │   │
│ │                                                                 │   │
│ │ 2. Offer afternoon rescheduling incentive                       │   │
│ │    → For new Tuesday bookings: "Save ₹100 by booking after      │   │
│ │      2 PM on Tuesdays!"                                         │   │
│ │    → Cost: ₹100 × ~8 patients/week = ₹3,200/month               │   │
│ │    → Expected impact: Shift 30-40% of AM patients to PM         │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ 💰 EXPECTED ROI                                                      │
│ ┌────────────────────────────────────────────────────────────────┐   │
│ │ ROI Estimate: ₹34,000/month (± ₹12,000)                        │   │
│ │                                                                 │   │
│ │ Calculation:                                                     │   │
│ │ • Current no-shows/month: 23                                    │   │
│ │ • Average revenue per completed appointment: ₹2,200             │   │
│ │ • Expected reduction (midpoint): 40% → 9 fewer no-shows         │   │
│ │ • Recovered revenue: 9 × ₹2,200 = ₹19,800                      │   │
│ │ • Rescheduled slots fill at 60% rate: +5 slots × ₹2,200         │   │
│ │   = ₹11,000                                                     │   │
│ │ • Less incentive cost: -₹3,200                                  │   │
│ │ • Net: ₹19,800 + ₹11,000 - ₹3,200 = ₹27,600                     │   │
│ │ • With variance: ₹27,600 ± ₹12,000 (80% confidence interval)    │   │
│ │                                                                 │   │
│ │ 📐 Methodology: Historical no-show rate × avg. revenue           │   │
│ │    × expected intervention effect. Labeled "Estimated" —        │   │
│ │    not yet verified by actual implementation.                    │   │
│ │                                                                 │   │
│ │ ⚠️ Limitations:                                                  │   │
│ │ • Assumes patient behavior follows historical patterns          │   │
│ │ • Reminder effectiveness based on industry average (30-50%)     │   │
│ │ • Does not account for seasonality or holidays                  │   │
│ │ • Confidence will improve after 8+ weeks of post-intervention   │   │
│ │   data collection                                               │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ ───────────────────────────────────────────────────────────────────  │
│                                                                      │
│ [✓ Mark as Implemented]  [✗ Not Useful]  [Already Knew This]        │
│ [⏰ Remind Me Later]                                                 │
│                                                                      │
│ ⚡ SIMULATE: "What if I changed [reminder timing ▼] to [8:00 AM ▼]?"│
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Card status badges — when they appear:**

| Badge | Trigger |
|-------|---------|
| **NEW** (blue) | Card generated within last 24 hours, user hasn't viewed it yet |
| **HIGH ROI** (red) | `estimated_roi >= ₹20,000/month` |
| **MEDIUM ROI** (yellow) | `estimated_roi >= ₹5,000/month and < ₹20,000/month` |
| **LOW ROI** (green) | `estimated_roi < ₹5,000/month` |
| **DATA STALE** (orange outline) | Underlying data is > 24 hours old |
| **IMPLEMENTED** (green check) | User marked as implemented |
| **SNOOZED** (grey) | User snoozed, will reappear after snooze period |

**Confidence score visualization:**

| Score Range | Bar Color | Interpretation |
|-------------|-----------|----------------|
| 80-100% | Green (██████████) | Strong evidence, large sample, act with confidence |
| 60-79% | Yellow (████████░░) | Moderate evidence, consider action, monitor results closely |
| 40-59% | Orange (██████░░░░) | Emerging pattern, limited data, treat as hypothesis |
| <40% | Red (████░░░░░░) | Insufficient data — surface as "potential pattern" only, do not recommend action |

**Decision cards are NEVER shown if:**
- Confidence < 35%
- Underlying data is > 7 days stale
- The same decision was already marked as "Implemented" or "Already Knew This" within the last 30 days
- The decision's estimated ROI is below ₹500/month (noise floor)

#### 3.2.3 Morning Digest Email

**Timing:** Sent at 6:00 AM IST, Monday through Saturday. Not sent on Sundays.

**Subject line:** "Cortex: 3 decisions for SmileCare Dental (Thu, 15 Jul)"

**Email content:**

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ☀️ Cortex — Morning Briefing                                     │
│  SmileCare Dental  ·  Thursday, 15 July 2026                     │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  Today's Top Decisions:                                          │
│                                                                  │
│  🔴 ₹34K/mo — Recover Tuesday no-shows                           │
│  22% of Dr. Sharma's morning slots were no-shows.                │
│  Send 7:30 AM reminders.                                         │
│  [View Analysis →]                                               │
│                                                                  │
│  🟡 ₹12K/wk — Fill Thursday afternoon gaps                       │
│  Gurgaon location has 32% open capacity 2-5 PM.                  │
│  Run a "Thursday afternoon discount" campaign.                   │
│  [View Analysis →]                                               │
│                                                                  │
│  🟡 ₹8K/mo — Revenue dip detected                                │
│  Last 3 days: 11% below trend. Primary driver: fewer             │
│  new patient bookings at Noida location.                         │
│  [View Analysis →]                                               │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  📊 Your Practice at a Glance:                                   │
│                                                                  │
│  Revenue MTD:  ₹18.4L  (+9% vs projection)                      │
│  No-Show Rate:  7.2%   (↓1.1%)                                  │
│  Utilization:   68%     (-4% vs target)                          │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  [View Full Dashboard →]  ·  [Adjust Email Settings →]          │
│                                                                  │
│  Cortex · Built in Delhi NCR                                     │
│  You're receiving this because you signed up at cortexapp.in     │
│  [Unsubscribe]                                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Email settings (user-configurable):**
- Frequency: Daily / Weekly (Mondays only) / Off
- Include metric snapshot: Yes / No
- Minimum decision count to send: 1 (default — send even if only 1 decision)

**Technical implementation:**
- Celery Beat job triggers at 5:45 AM IST
- Queries database for active decisions (not dismissed, not implemented, confidence > 35%)
- Selects top 3 by ROI × confidence
- Renders email with inlined CSS (no external images except logo)
- Sends via SendGrid or Resend (transactional email API)
- Tracks: delivery rate, open rate, click-through rate to dashboard

#### 3.2.4 Push Notifications (In-App)

Cortex v1 uses **browser push notifications** (via Web Push API — Service Workers). No mobile app required. User must grant notification permission during onboarding or from settings.

**What triggers a push notification:**

| Trigger | Message | Action on Click |
|---------|---------|-----------------|
| New high-ROI decision (≥₹20K/mo) | "🔴 ₹34K opportunity: Reduce Tuesday no-shows by sending earlier reminders." | Open decision detail page |
| Rapid revenue anomaly (>20% drop in 2 days) | "⚠️ Revenue dropped 22% in 2 days. Primary driver: fewer new bookings at Noida." | Open revenue trend analysis |
| Data sync failure (>12 hours stale) | "📡 Practo data hasn't synced in 12 hours. Insights may be outdated. Tap to reconnect." | Open integration settings |
| Weekly summary (every Monday 9:00 AM) | "📊 Last week: 2 decisions implemented, ₹41K estimated impact. View your weekly review." | Open dashboard |

**Notification frequency cap:** Maximum 3 push notifications per day per user. No notifications between 10:00 PM and 7:00 AM IST.

**Implementation:**
- Backend: `pywebpush` library to push to browser push service
- Frontend: Service Worker registration, VAPID key generation per user
- Database: `push_subscriptions` table with endpoint URL + encryption keys

#### 3.2.5 Decision Feedback Loop

Every decision card has four feedback options:

| Button | What It Means | What Happens |
|--------|--------------|--------------|
| **✓ Mark as Implemented** | "I did this / I'm doing this" | Decision moves to "Implemented" tab. System notes the timestamp. In 30/60/90 days, system re-evaluates and compares actual metrics to prediction. If actual outcome matches prediction, confidence model improves. User gets a follow-up: "Your Tuesday no-show rate dropped from 22% to 15% after implementing reminders. We predicted 12-15%." |
| **✗ Not Useful** | "This recommendation is wrong, irrelevant, or low quality" | Decision is hidden. If user selects a reason from dropdown (optional): "Wrong data" / "Irrelevant to my practice" / "Too obvious" / "Bad recommendation" / "Other". System decrements weight for this decision type for this practice. If 3+ "Not Useful" on same decision type within 30 days, system reduces frequency of that decision type for this practice. |
| **Already Knew This** | "This is correct but I'm already aware" | Decision is hidden, marked as "Acknowledged." System notes that pattern detection was valid but not novel. Does not penalize the algorithm. Decision type frequency unchanged. |
| **⏰ Remind Me Later** | "Not now, show me again" | Decision is snoozed. Default snooze: 3 days. User can pick: 1 day / 3 days / 1 week / Custom date. Reappears after snooze period. |

**Implementation:**
- `POST /decisions/:id/feedback` with `{ feedback_type: "implemented" | "not_useful" | "already_knew" | "snooze", snooze_days: int|null, reason: string|null }`
- Feedback stored in `decision_feedback` table
- Feedback counts aggregated in `decision_type_stats` table for preference learning

**How feedback affects future decisions:**
- **Implemented:** +10% weight for this decision type for this practice
- **Not Useful (with "Bad recommendation" reason):** -30% weight
- **Not Useful (with "Irrelevant" reason):** -20% weight
- **Not Useful (with "Wrong data" reason):** Flag for data quality review, -10% weight
- **Already Knew:** No weight change (neutral)
- After 5+ feedback events for a decision type, system begins to personalize frequency

---

### 3.3 Simulation (v1 Simple Version)

Cortex v1 simulation is a **formula-based, single-variable calculator.** It is explicitly labeled "Estimated — simplified model" and does NOT use Monte Carlo, causal inference, or multi-variable optimization.

**Access points:**
1. Dashboard "Simulation Quick-Start" bar
2. Decision detail page: "⚡ SIMULATE" section
3. Standalone simulation page: `https://cortexapp.in/simulate`

#### 3.3.1 Simulation Quick-Start (Dashboard)

```
┌──────────────────────────────────────────────────────────────────────┐
│ 📊 Simulation Quick-Start                                             │
│                                                                      │
│ "What if I [ changed no-show rate  ▼ ] by [ -20% ▼ ] ?"  [Run ▸]    │
│                                                                      │
│ Preset scenarios:  "Reduce no-shows" · "Raise prices 10%"            │
│                    · "Add Saturday hours" · "Custom..."              │
└──────────────────────────────────────────────────────────────────────┘
```

**Preset dropdown options:**

| Preset | Variable | Default Change | 
|--------|----------|---------------|
| Reduce no-shows | No-show rate | -20% |
| Raise prices | Average service price | +10% |
| Add Saturday hours | Available hours/week | +8 hours |
| Increase marketing spend | Monthly ad budget | +₹20,000 |
| Add a provider | Number of providers | +1 |
| Reduce appointment duration | Average appointment length | -10 min |
| Custom... | User selects variable + amount | — |

#### 3.3.2 Simulation Input Screen

URL: `https://cortexapp.in/simulate`

```
┌──────────────────────────────────────────────────────────────────────┐
│ What-If Simulation                                                    │
│                                                                      │
│ ───────────────────────────────────────────────────────────────────  │
│                                                                      │
│ Variable:  [No-Show Rate ▼]                                          │
│            (Current: 7.2% across all locations)                      │
│                                                                      │
│ Change by: [ -20 ] [ % ▼ ]   OR   Target: [ 5.8 ] %                  │
│                                                                      │
│ Scope:     [All Locations ▼]                                         │
│            (Gurgaon · South Delhi · Noida)                           │
│                                                                      │
│ Timeframe: [30 days ▼]                                               │
│            (30 · 60 · 90 days)                                       │
│                                                                      │
│ ───────────────────────────────────────────────────────────────────  │
│                                                                      │
│ [Run Simulation ▸]                                                   │
│                                                                      │
│ ⚡ Uses your practice's actual data. Results in <10 seconds.          │
│ ⚠️ This is a simplified model. Actual outcomes may vary.              │
│    Labeled "Estimated" until validated against real data.            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

#### 3.3.3 Simulation Output Screen

```
┌──────────────────────────────────────────────────────────────────────┐
│ Simulation Results                                                    │
│                                                                      │
│ "What if no-show rate drops from 7.2% → 5.8% (−20%)"                │
│ Scope: All locations · Timeframe: 30 days                            │
│                                                                      │
│ ───────────────────────────────────────────────────────────────────  │
│                                                                      │
│ 📈 PROJECTED IMPACT (30-day horizon)                                  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  Additional Completed Appointments:  12-18                   │   │
│  │  Additional Revenue:                 ₹26,400 — ₹39,600       │   │
│  │  Improved Utilization:               68% → 71% (+3%)         │   │
│  │                                                              │   │
│  │  Confidence: ████████░░ 80%                                  │   │
│  │  Based on: 847 historical appointments                      │   │
│  │  Methodology: Expected value = (current rate - target rate)  │   │
│  │              × appointments/month × avg. revenue/slot       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ 📐 HOW THIS IS CALCULATED                                            │
│                                                                      │
│  Formula:                                                            │
│  Additional Revenue = (Current No-Show Rate - Target Rate)           │
│                      × Appointments per Month                        │
│                      × Average Revenue per Appointment               │
│                      × Fill Rate (assume 100% rebooking)            │
│                                                                      │
│  = (0.072 − 0.058) × 520 × ₹2,200 × 1.0                            │
│  = 0.014 × 520 × ₹2,200                                              │
│  = ₹16,016 (lower bound, 60% fill) to ₹26,694 (upper, 100% fill)   │
│                                                                      │
│  ⚠️ LIMITATIONS:                                                     │
│  • Assumes all no-show slots are rebooked (actual fill: 50-80%)     │
│  • Does not account for seasonal variation                          │
│  • No-show reduction requires active intervention (reminders, etc.) │
│  • Simplified model — not causal inference                          │
│  • Actual results depend on patient response to interventions       │
│                                                                      │
│ ───────────────────────────────────────────────────────────────────  │
│                                                                      │
│  [Adjust Parameters]  [Save Simulation]  [Export as PDF]            │
│                                                                      │
│  💡 Related Decision: "Recover 40% of Tuesday no-shows"              │
│     This simulation aligns with that recommendation.                 │
│     [View Decision →]                                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Simulation technical specifications:**

| Variable | Formula | Input Parameters |
|----------|---------|-----------------|
| **No-Show Rate** | `ΔRevenue = (curr_rate − target_rate) × monthly_appointments × avg_revenue_per_slot × fill_rate` | `curr_rate` from PMS data, `target_rate` from user input, `fill_rate` = 0.8 (default, user can adjust), `avg_revenue_per_slot` from Razorpay ÷ completed appointments |
| **Average Price** | `ΔRevenue = Δprice × monthly_appointments × (1 − elasticity × Δprice / curr_price)` | `elasticity` = 0.4 default for healthcare (inelastic), user can adjust. `monthly_appointments` from PMS. |
| **Available Hours** | `ΔRevenue = new_hours × utilization_at_new_hours × avg_revenue_per_hour` | `utilization_at_new_hours` estimated from historical utilization for closest-matching time slots |
| **Number of Providers** | `ΔRevenue = new_provider_capacity × avg_utilization × avg_revenue_per_slot − new_provider_cost` | `new_provider_capacity` = available slots, `avg_utilization` from practice data, `new_provider_cost` from calibration survey or default ₹50,000/month |
| **Marketing Spend** | `ΔRevenue = Δspend × historical_ROAS` | `historical_ROAS` estimated from correlation of spend vs. new patient bookings (if available), else industry default 3.0x |

**All simulation outputs include:**
- "Estimated" label prominently displayed
- Confidence band (based on variance in underlying data, not Monte Carlo)
- Limitations section
- Link to related decision cards

**Saved simulations:** Each simulation run is saved to `simulation_runs` table with input parameters and output. User can view history: "My Simulations" tab shows past runs with date and summary.

---

## 4. v1 Feature List — Prioritized

### Priority Definitions

| Priority | Meaning | Ship Criteria |
|----------|---------|--------------|
| **P0** | Must ship before first pilot can use the product | No pilot onboarding without it |
| **P1** | Should ship during pilot phase (Weeks 9-14 based on pilot feedback) | Pilots can use product without it, but value is reduced |
| **P2** | Explicitly excluded from v1 | Built in v2 only |

### Feature Table

| # | Feature | Priority | Description | Dependencies | Acceptance Criteria | Effort |
|---|---------|----------|-------------|-------------|---------------------|--------|
| F1 | **User Authentication (Clerk)** | P0 | Signup, login, password reset, JWT token management via Clerk. Google OAuth signup. | None | User can create account, verify email, log in, log out. JWT appears in all API requests. | S (3 days with Clerk) |
| F2 | **Multi-Tenancy (Schema-per-Tenant)** | P0 | Each practice gets a dedicated PostgreSQL schema. All queries scoped by tenant. Middleware extracts tenant from JWT. | F1 (Clerk) | Two practices can be created. Each sees only their data. Cross-tenant data leak test passes. | M (5 days) |
| F3 | **PMS Integration (Practo, DocEngage, or Lybrate)** | P0 | OAuth connection, batch sync (every 2h), webhook listener. Pulls: appointments, patients, providers, services. Normalizes to unified schema. | F2 (multi-tenancy) | Connect a test PMS account. Appointments appear in database. Sync status shows in UI. Webhook received and processed. | L (7 days per PMS, first one is 10 days) |
| F4 | **Razorpay Integration** | P0 | OAuth connection, batch sync (every 2h) + webhook. Pulls: payments, refunds, settlements. Normalizes to unified schema. | F2 (multi-tenancy) | Connect test Razorpay account. Payments appear in database. Webhook updates in real-time. | M (5 days) |
| F5 | **Zoho Books Integration (+ Tally CSV Bridge)** | P0 | OAuth for Zoho Books. CSV upload for Tally. Pulls: invoices, contacts, chart of accounts. | F2 (multi-tenancy) | Connect Zoho Books. Invoices appear. Upload Tally CSV — validates format, ingests data. | M (5 days) |
| F6 | **Data Normalization Pipeline** | P0 | Schema mappers for each integration → unified entity model. Type coercion, date parsing, status mapping, unit conversion (paise→rupees). | F3, F4, F5 | PMS appointment → unified booking entity. Razorpay payment → unified payment entity. All type conversions correct. | M (5 days) |
| F7 | **Entity Resolution** | P0 | Match patients across PMS, Razorpay, Zoho Books. v1: exact email match only. Store resolution confidence. Expose low-confidence matches for manual review. | F6 (normalization) | Patient "a@b.com" in PMS matches Razorpay customer with same email. Patient without email in PMS gets new canonical ID. Resolution confidence stored. | L (7 days) |
| F8 | **No-Show Prediction Decision** | P0 | Statistical model: daily check of next 7 days' appointments. Compares each appointment slot's historical no-show rate. Ranks by probability × revenue at risk. Generates decision card. | F3 (PMS), F6 (normalization), F7 (entity resolution) | Decision card appears when no-show pattern detected. Card includes: which appointments, why, what to do, ROI, confidence. At least 8 weeks of historical data produces usable results. | L (7 days) |
| F9 | **Scheduling Gap Detection Decision** | P0 | Compares upcoming 7-day schedule density to historical average for same day-of-week × time-of-day. Flags slots with <50% of historical density. | F3 (PMS), F6 (normalization) | Gap detected when Tuesday 10 AM has 2 bookings vs. historical avg of 6. Card shows gap hours, revenue at risk, recommendation. | M (5 days) |
| F10 | **Revenue Trend Analysis Decision** | P0 | Weekly time-series decomposition. Compares trailing 7-day revenue to 28-day moving average. Detects anomalies (>1.5 standard deviations). Segments by location. | F4 (Razorpay), F5 (Zoho Books), F6 (normalization) | When revenue drops >1.5σ below trend, card appears: what changed, which location, is it a blip or trend, primary driver. | M (5 days) |
| F11 | **Pricing Optimization Decision** | P0 | Monthly check: services ranked by utilization rate at current price. Low utilization (<60%) + high margin (>40%) → recommendation to adjust price. Uses default elasticity (0.4). | F3 (PMS), F5 (Zoho Books for cost data), F6 (normalization) | Card appears when service has <60% utilization and margin >40%. Shows current price, suggested new price, projected impact. | M (5 days) |
| F12 | **Decision Card UI** | P0 | Dashboard card list + detail page. Card anatomy: title, ROI badge, confidence score, evidence summary, recommendation, feedback buttons. Expandable to full analysis. | F8-F11 (at least one decision type working) | Decision cards render correctly. Expand/collapse works. All five questions answered. Feedback buttons functional. | L (7 days) |
| F13 | **Dashboard UI** | P0 | Dashboard page with: metric cards (4 KPI tiles), decision card list (sorted by ROI×confidence), simulation quick-start, recent activity feed, location filter. | F12 (decision cards), F6 (for metric computation) | Dashboard loads < 500ms. Metric cards show correct values. Location filter works. | L (7 days) |
| F14 | **Feedback Loop** | P0 | Four feedback options on every decision card. Feedback stored in database. Affects future decision personalization. Implemented decisions tracked for outcome measurement. | F12 (decision card UI) | Click "Implemented" → decision moves to Implemented tab. "Not Useful" → decision hidden. Feedback counts updated. | S (3 days) |
| F15 | **Integration Connection Wizard** | P0 | Step-by-step wizard for connecting tools during onboarding. Progress indicator. Error states for each failure mode. | F3-F5 (integrations), F1 (auth) | Wizard guides user through connecting 3 tools. Error states display correctly. Progress persists across page reloads. | M (5 days) |
| F16 | **Onboarding Flow (Signup + Survey + First Insight)** | P0 | Landing page → signup → practice profile → calibration survey → integration wizard → initial sync progress → first insights. | F15 (wizard), F1 (auth), F13 (dashboard — for first insights display) | Complete onboarding end-to-end. First insight appears within 15 min of finishing setup. Email sent when insights ready. | M (5 days) |
| F17 | **Morning Digest Email** | P1 | Daily email at 6:00 AM IST with top 3 decision cards + metric snapshot. Sent Mon-Sat. Unsubscribe link. Frequency settings. | F8-F11 (decisions), email sending infra | Email arrives at correct time. Contains correct decisions for the practice. Open/click tracking works. | S (3 days) |
| F18 | **Browser Push Notifications** | P1 | Web Push API notifications for high-ROI decisions, anomalies, sync failures. Permission request during onboarding. Cap at 3/day. No notifications 10 PM-7 AM. | F12 (decision cards), Service Worker setup | Notification permission prompt appears. Notification delivered for new high-ROI decision. Cap enforced. | M (5 days) |
| F19 | **What-If Simulation** | P1 | Single-variable simulation with preset scenarios. Formula-based (not Monte Carlo). Output: projected impact, confidence band, methodology, limitations. Save and view history. | F6 (normalization), F13 (dashboard for quick-start) | Simulation runs for each preset. Results display with correct formula. Confidence band shown. History persists. | M (5 days) |
| F20 | **Data Freshness Indicators** | P0 | Every metric and decision shows when data was last synced. Stale data (>12h) gets yellow badge. Very stale (>24h) gets red badge. Data age affects decision confidence. | F3-F5 (integrations) | Sync timestamp visible on dashboard. Badge color changes at 12h and 24h thresholds. Decisions with stale data show reduced confidence. | S (2 days) |
| F21 | **Manual Entity Merge UI** | P1 | Settings page where users can review and merge unmatched patient records. Shows suggested matches (same name, different emails). Manual merge updates canonical IDs. | F7 (entity resolution) | User can view unmatched patients. Merge action updates entity resolution table. Merged entities reflected in decisions. | S (3 days) |
| F22 | **Integration Status Dashboard** | P0 | Settings page showing all integrations with status (healthy/degraded/down), last sync time, and reconnect button. | F3-F5 (integrations) | Each integration shows status color. Reconnect button triggers OAuth flow. Sync time updates after each batch. | S (2 days) |
| F23 | **Location Management** | P0 | Settings page to add/edit/remove practice locations. Each location has: name, address, providers assigned, operating hours. | F2 (multi-tenancy) | Add location → appears in location filter. Edit hours → utilization calculation updates. | S (2 days) |
| F24 | **Pilot Usage Tracking** | P1 | Internal analytics: daily active users, decisions viewed, feedback rate, decisions implemented, ROI claimed. Dashboard for founder to monitor pilot health. | F14 (feedback), authentication events | Founder can see per-practice: last active date, total decisions viewed, feedback count, implemented count. | S (2 days) |

**Effort estimates key:**
- S (Small): 2-3 days for a single developer
- M (Medium): 5 days
- L (Large): 7-10 days

**Total P0 effort estimate (assuming parallelizable work):** ~60 developer-days = 12 weeks for 1 developer with buffer. Target: 8-10 weeks with ruthless scope management. Features F17-F19 and F21, F24 can slip to week 11-14 (pilot phase) if timeline is tight.

---

## 5. Integration Specifications

### 5.1 PMS Integration (Practo / DocEngage / Lybrate)

The PMS is the primary data source. All three PMS options share a common data model (appointments, patients, providers, services), so the connector architecture is designed with a shared abstract base class and tool-specific API adapters.

#### Practo Prime

| Spec | Detail |
|------|--------|
| **API Documentation** | Practo Connect API (developer.practo.com) — REST API |
| **Authentication** | OAuth 2.0 (Authorization Code grant). Practo provides `client_id` and `client_secret` after app registration. |
| **Scopes** | `appointments:read`, `patients:read`, `providers:read`, `services:read` |
| **Rate Limits** | 100 requests/minute per practice |
| **API Base URL** | `https://api.practo.com/v1/` |

**Data entities pulled:**

| Entity | API Endpoint | Key Fields | Sync Strategy |
|--------|-------------|------------|---------------|
| **Appointments** | `GET /appointments?since={timestamp}&until={timestamp}` | `id`, `patient_id`, `provider_id`, `service_id`, `start_time`, `end_time`, `status` (scheduled/completed/no_show/cancelled), `cancellation_reason`, `location_id`, `created_at`, `updated_at` | **Batch:** Every 2 hours, pull appointments updated since last sync cursor. **Webhook:** Practo sends webhook on `appointment.updated` (register webhook URL during OAuth setup). |
| **Patients** | `GET /patients?since={timestamp}` | `id`, `first_name`, `last_name`, `email`, `phone`, `date_of_birth`, `gender`, `address` (area/sector), `created_at`, `updated_at` | **Batch:** Every 6 hours (slow-changing data) |
| **Providers** | `GET /providers` | `id`, `first_name`, `last_name`, `specialization`, `email`, `phone`, `location_ids[]` | **Batch:** Every 6 hours + on webhook `provider.updated` |
| **Services** | `GET /services` | `id`, `name`, `category`, `default_duration_minutes`, `default_price`, `location_ids[]` | **Batch:** Every 6 hours + on webhook `service.updated` |

**Webhook events (if available from PMS):**

| Event | Action |
|-------|--------|
| `appointment.created` | Insert new appointment, trigger scheduling gap recheck |
| `appointment.updated` | Update appointment status (especially: marked as no_show) |
| `appointment.cancelled` | Update appointment, record cancellation reason |
| `patient.created` / `patient.updated` | Upsert patient record |

**If PMS does not support webhooks:** Fall back to pure batch sync at 1-hour frequency. This is acceptable for v1. The data freshness indicator will show "synced 1 hour ago."

#### DocEngage / Lybrate

Same entity model, same sync strategy. Different API base URLs and authentication endpoints. If API documentation is unavailable or API quality is poor during testing, default to: ask the practice to export CSV from their PMS and use the CSV upload bridge (similar to Tally fallback). This is a v1 acceptable degradation — the pilot knows they're on a "limited data" mode.

#### PMS Normalization Rules

**Appointment → Unified Booking:**
```python
def map_practo_appointment(raw: dict) -> NormalizedBooking:
    return NormalizedBooking(
        external_id=f"practo_{raw['id']}",
        source_tool="practo",
        patient_external_id=raw['patient_id'],
        provider_external_id=raw['provider_id'],
        service_external_id=raw['service_id'],
        location_external_id=raw.get('location_id'),
        start_time=parse_iso(raw['start_time']),
        end_time=parse_iso(raw['end_time']),
        status=map_status(raw['status']),  # scheduled→scheduled, completed→completed, no_show→no_show, cancelled→cancelled
        cancellation_reason=raw.get('cancellation_reason'),
    )
```

**Patient → Unified Customer:**
```python
def map_practo_patient(raw: dict) -> NormalizedCustomer:
    return NormalizedCustomer(
        external_id=f"practo_{raw['id']}",
        source_tool="practo",
        first_name=raw['first_name'],
        last_name=raw['last_name'],
        email=raw.get('email'),  # May be None — many patients don't provide email
        phone=normalize_phone(raw.get('phone')),  # +91 format
        attributes={
            'gender': raw.get('gender'),
            'area': raw.get('address', {}).get('area'),
        }
    )
```

**Provider → Unified Employee:**
```python
def map_practo_provider(raw: dict) -> NormalizedEmployee:
    return NormalizedEmployee(
        external_id=f"practo_{raw['id']}",
        source_tool="practo",
        name=f"{raw['first_name']} {raw['last_name']}",
        email=raw.get('email'),
        phone=normalize_phone(raw.get('phone')),
        role=raw.get('specialization', 'Provider'),
        attributes={
            'specialization': raw.get('specialization'),
            'location_ids': raw.get('location_ids', []),
        }
    )
```

### 5.2 Razorpay Integration

| Spec | Detail |
|------|--------|
| **API Documentation** | https://razorpay.com/docs/api/ |
| **Authentication** | OAuth 2.0 (Authorization Code grant) for Razorpay Partner API. Alternative: API Keys (key_id + key_secret) — simpler, used for direct integrations. For v1: use API Keys (faster to implement, Razorpay OAuth for partners requires approval). |
| **Scopes** | `read_only` access to payments, refunds, settlements |
| **Rate Limits** | 100 requests/minute per merchant |
| **API Base URL** | `https://api.razorpay.com/v1/` |

**Important note on Razorpay authentication for v1:**
Razorpay's OAuth flow is designed for partner platforms. For direct integrations, Razorpay uses API Keys (`key_id` + `key_secret`). Since Cortex is connecting directly to the practice's Razorpay account, we store the API keys (encrypted with Fernet). The user generates read-only API keys from their Razorpay dashboard and enters them into Cortex. This is a v1 simplification — we can migrate to OAuth in v2.

**Data entities pulled:**

| Entity | API Endpoint | Key Fields | Sync Strategy |
|--------|-------------|------------|---------------|
| **Payments** | `GET /payments?from={timestamp}&to={timestamp}&count=100` | `id`, `amount` (paise), `currency`, `status` (captured/failed/refunded), `method`, `email`, `contact`, `notes`, `invoice_id`, `created_at` | **Batch:** Every 2 hours (paginated by `created_at`). **Webhook:** `payment.captured`, `payment.failed`, `refund.created` |
| **Refunds** | `GET /refunds?from={timestamp}&to={timestamp}` | `id`, `payment_id`, `amount`, `status`, `created_at` | **Batch:** Every 2 hours |
| **Settlements** | `GET /settlements?from={timestamp}&to={timestamp}` | `id`, `amount`, `status`, `created_at` | **Batch:** Every 6 hours (settlements are end-of-day) |

**Webhook registration:** Register webhook URL in Razorpay dashboard manually during setup (Razorpay requires manual webhook setup with secret validation). Webhook secret stored in `credentials` table.

**Razorpay Normalization Rules:**

Amount conversion: **ALL Razorpay amounts are in PAISE.** Divide by 100 to get rupees. This is the #1 data normalization bug risk — validate with a test case.

```python
def map_razorpay_payment(raw: dict) -> NormalizedPayment:
    return NormalizedPayment(
        external_id=f"razorpay_{raw['id']}",
        source_tool="razorpay",
        amount=raw['amount'] / 100,  # PAISE → RUPEES. CRITICAL.
        currency=raw['currency'],
        status=map_payment_status(raw['status']),
        # captured→completed, failed→failed, refunded→refunded, created→pending
        payment_method=raw.get('method'),
        customer_email=raw.get('email'),
        customer_phone=normalize_phone(raw.get('contact')),
        paid_at=datetime.fromtimestamp(int(raw['created_at'])),
        attributes={
            'razorpay_invoice_id': raw.get('invoice_id'),
            'notes': raw.get('notes', {}),
        }
    )
```

### 5.3 Zoho Books Integration

| Spec | Detail |
|------|--------|
| **API Documentation** | https://www.zoho.com/books/api/v3/ |
| **Authentication** | OAuth 2.0 (Authorization Code grant). Zoho provides `client_id` and `client_secret`. |
| **Scopes** | `ZohoBooks.invoices.READ`, `ZohoBooks.contacts.READ`, `ZohoBooks.chartofaccounts.READ` |
| **Rate Limits** | 250 requests/day for free tier, 1000/day for standard plan |
| **API Base URL** | `https://www.zohoapis.com/books/v3/` |

**Data entities pulled:**

| Entity | API Endpoint | Key Fields | Sync Strategy |
|--------|-------------|------------|---------------|
| **Invoices** | `GET /invoices?last_modified_time={timestamp}` | `invoice_id`, `customer_id`, `customer_name`, `date`, `due_date`, `total`, `status` (paid/sent/draft/overdue), `line_items[]`, `last_modified_time` | **Batch:** Every 4 hours (Zoho rate limits are tight). Pull invoices modified since last sync. |
| **Contacts** | `GET /contacts?last_modified_time={timestamp}` | `contact_id`, `contact_name`, `email`, `phone`, `contact_type` (customer/vendor) | **Batch:** Every 6 hours |
| **Chart of Accounts** | `GET /chartofaccounts` | `account_id`, `account_name`, `account_type` | **Batch:** Once on initial sync, then weekly |

**Zoho Books Normalization Rules:**

```python
def map_zoho_invoice(raw: dict) -> NormalizedInvoice:
    return NormalizedInvoice(
        external_id=f"zoho_{raw['invoice_id']}",
        source_tool="zoho_books",
        amount=float(raw['total']),
        currency='INR',  # Zoho Books India default
        status=map_invoice_status(raw['status']),
        # sent→sent, paid→paid, draft→draft, overdue→overdue
        issue_date=parse_date(raw['date']),
        due_date=parse_date(raw.get('due_date')),
        customer_external_id=raw.get('customer_id'),
        customer_name=raw.get('customer_name'),
        line_items=raw.get('line_items', []),  # Store as JSONB
    )
```

#### 5.3.1 Tally CSV Import Bridge

For practices using Tally instead of Zoho Books:

**Upload UX:**
- Screen: "Connect Tally" → "Tally doesn't support direct cloud connection. Upload a CSV export."
- Instructions with screenshots of Tally Prime export steps
- Drag-and-drop file upload (max 50MB)
- After upload: preview first 10 rows, validate columns, show row count

**Expected CSV format (Tally Day Book export):**

| Column | Expected Content | Validation |
|--------|-----------------|------------|
| `Date` | DD-Mon-YYYY (e.g., 15-Jul-2026) | Must parse as date |
| `Voucher Type` | Sales, Receipt, Payment, Journal, etc. | Must be non-empty |
| `Voucher Number` | String | Must be non-empty |
| `Ledger` | Account name (e.g., "Consultation Fees", "Rent Expense") | Must be non-empty |
| `Amount` | Number (₹) | Must be numeric, can be negative (credits) |
| `Debit/Credit` | "Dr" or "Cr" | Must be one of these |

**Validation rules:**
- File must have header row
- Required columns must exist (case-insensitive matching)
- At least 1 data row
- Amount column must be numeric (strip ₹ symbol and commas)
- Date column must parse as valid dates

**Error handling:**
- Missing columns → "Expected columns: Date, Voucher Type, Ledger, Amount. Found: [actual columns]. Please re-export."
- No data rows → "The uploaded file contains only headers. Please check the export."
- Unparseable amounts → "Row 23 has an invalid amount: 'N/A'. Please fix and re-upload."

**Normalization from Tally CSV:**

Tally CSV provides a transaction log, not structured invoices. The mapping is approximate:

- Each row is a ledger entry → stored as a `transaction` entity (new entity type, simpler than invoice)
- Revenue transactions: rows where ledger contains known revenue keywords (Fees, Consultation, Service, Treatment) AND amount is credit
- Expense transactions: rows where ledger contains expense keywords (Rent, Salary, Electricity, Supplies) AND amount is debit
- Customer name may NOT be in Tally data — many practices use Tally for aggregate accounting, not per-patient billing

**Limitations (displayed to user):**
- "Tally data provides aggregate revenue tracking. Per-patient billing details are not available from Tally CSV."
- "Insights that depend on patient-level billing (LTV, per-patient profitability) will not be available."
- "We recommend upgrading to Zoho Books for richer insights. [Learn more]"

### 5.4 Sync Schedule Summary

| Integration | Initial Sync | Incremental Batch | Webhook |
|-------------|-------------|-------------------|---------|
| PMS (Practo/DocEngage/Lybrate) | Full historical (2 years or available) | Every 2 hours | Yes (if PMS supports) |
| Razorpay | Full historical (2 years) | Every 2 hours | Yes (manual setup) |
| Zoho Books | Full historical (2 years) | Every 4 hours | No (Zoho rate limits) |
| Tally CSV | One-time upload | Weekly re-upload (manual) | N/A |

### 5.5 Data Freshness Indicator

Every data-dependent UI element shows a freshness indicator:

| Data Age | Icon | Color | Impact on Decision Confidence |
|----------|------|-------|-------------------------------|
| < 1 hour | ● | Green | No impact |
| 1-6 hours | ● | Green | No impact |
| 6-12 hours | ◑ | Yellow | -5% per stale source |
| 12-24 hours | ○ | Orange | -10% per stale source |
| > 24 hours | ◎ | Red | -15% per stale source (max -40%) |
| > 7 days | ⛔ | Red | Decision suppressed entirely |

**Implementation:** `provenance_log` table tracks `synced_at` per tool per entity. UI queries: `SELECT MAX(synced_at) FROM provenance_log WHERE source_tool = :tool AND tenant_schema = :schema`.

### 5.6 Integration Error Handling

| Error Type | Detection | Auto-Recovery | User-Facing Message |
|------------|-----------|---------------|---------------------|
| Rate limit (429) | HTTP 429 from API | Wait for retry-after header duration. If no header, exponential backoff: 30s → 2min → 5min. | No user notification on first 3 retries. After 3 failures: "Sync delayed — will retry in 5 minutes." |
| Auth expired (401) | HTTP 401 from API | Attempt token refresh. If refresh fails → mark as `needs_reauth`. | "Your [Tool] connection has expired. Please reconnect to restore insights. [Reconnect]" |
| Server error (5xx) | HTTP 500/502/503 from API | Retry 3× with exponential backoff. After 3 failures → mark `degraded`. | "We're having trouble reaching [Tool]. Their servers may be temporarily down. Insights using this data may be delayed." |
| Timeout (>30s) | HTTP request timeout | Retry 1×. If still times out → mark `degraded`. | "Connection to [Tool] is slow. Data sync will resume automatically." |
| Bad data / schema change | JSON parse failure, unexpected null, missing required field | Log error, skip the record, continue processing others. Alert engineering if >1% of records fail. | No user notification. Data quality counter increments. If >5% records affected: "We detected unexpected data format from [Tool]. Some data may be incomplete. Our team has been notified." |
| Webhook signature invalid | Hash mismatch | Reject webhook, return 400. Do NOT process. | No user notification (this is a security measure — silently reject). |
| Integration disconnected by user | User revokes OAuth from tool side | Mark as `disconnected`. All decisions using this tool suppressed. | "[Tool] has been disconnected. Reconnect to restore insights using this data. [Reconnect]" |

---

## 6. Decision Type Specifications

### 6.1 No-Show Prediction

**Data Sources:**
- PMS appointments: `bookings` table (status, start_time, patient_id, provider_id, service_id, location_id)
- Historical no-show patterns: same table, filtered for `status = 'no_show'` in trailing 12 weeks

**Algorithm:**

The no-show prediction uses a **logistic regression model** trained per practice. This is chosen over a simple historical average because it can weight multiple risk factors simultaneously.

**Features (input variables):**

| Feature | Type | Source | Description |
|---------|------|--------|-------------|
| `day_of_week` | Categorical (7) | `bookings.start_time` | Mon-Sun |
| `time_of_day` | Categorical (4) | `bookings.start_time` | morning (8-11), mid-day (11-2), afternoon (2-5), evening (5-8) |
| `lead_time_days` | Numeric | `bookings.created_at` − `bookings.start_time` | Days between booking and appointment |
| `patient_no_show_history` | Numeric (0-1) | Historical `bookings` for this patient | % of past appointments that were no-shows |
| `patient_total_appointments` | Numeric | Same | Total past appointments (proxy for patient loyalty) |
| `provider_no_show_rate` | Numeric (0-1) | Historical `bookings` for this provider | Provider's overall no-show rate |
| `service_type` | Categorical (N) | `services.category` | Type of service |
| `location_id` | Categorical | `bookings.location_id` | Which clinic location |
| `is_first_appointment` | Binary | Count of prior appointments = 0 | New patient vs. returning |
| `days_since_last_appointment` | Numeric | Datediff from prior appointment | Gap since last visit |

**Training:**
- Trained on trailing 12 weeks of appointment data
- Minimum 50 appointments with at least 5 no-shows to train (otherwise fall back to simple historical average)
- Retrained weekly (Celery Beat job, every Monday 2:00 AM IST)
- Model: scikit-learn `LogisticRegression(class_weight='balanced')` — balanced to handle no-show class imbalance (typically 5-15% no-shows)

**Fallback model (insufficient data):**
If <50 appointments or <5 no-shows in training window:
- No-show probability = provider's historical no-show rate × day-of-week multiplier
- Day-of-week multiplier = (no-shows on this day / total appointments on this day) ÷ (total no-shows / total appointments)
- If even this is insufficient (<20 appointments on a given day): use overall practice no-show rate (7-8% default)

**Prediction:**
- Run daily at 5:00 AM IST
- Score ALL appointments in the next 7 days
- Rank by: `predicted_probability × estimated_revenue_at_risk`
- `estimated_revenue_at_risk` = average revenue per completed appointment for this provider/service (from Razorpay data, trailing 4 weeks)
- Top 5 appointments become decision card candidates

**Output (Decision Card):**

| Field | Content |
|-------|---------|
| **What Happened** | "X of your next Y appointments have an elevated no-show risk (>25% probability). Total revenue at risk: ₹Z." |
| **Why** | Breakdown of highest-risk appointments with contributing factors: "Tuesday 10 AM with Dr. Sharma — patient Priya M. has missed 2 of last 4 appointments. Dr. Sharma's Tuesday no-show rate is 22%." |
| **What to Do** | Tiered recommendations: (1) Send automated reminder at optimal time, (2) Call high-risk patients 24h before, (3) Overbook slot if patient has >50% no-show probability. |
| **Expected ROI** | `(avg_revenue_per_slot × expected_reduction × high_risk_count) − implementation_cost` |
| **Confidence** | Based on: model accuracy on training data (AUC-ROC), number of training observations, data freshness |

**ROI Formula:**
```
ROI = Σ(probability_i × revenue_per_slot_i) × intervention_effectiveness − false_positive_cost
```
Where:
- `probability_i` = predicted no-show probability for high-risk appointment i
- `revenue_per_slot_i` = average revenue for that provider/service
- `intervention_effectiveness` = 0.35 (default: reminders reduce no-shows by 35%, based on industry literature)
- `false_positive_cost` = (1 − probability_i) × overbooking_disruption_cost (₹500 default)

**Refresh:** Daily at 5:00 AM IST. Re-runs if significant new data arrives (e.g., a batch of cancellations changes the risk profile significantly).

**Limitations (stated on card):**
- "Based on statistical patterns in your practice data. Individual patient behavior may differ."
- "No-show prediction accuracy improves with more data. Current model trained on N appointments."
- "Does not account for one-time events (weather, festivals, emergencies)."

### 6.2 Scheduling Gap Detection

**Data Sources:**
- PMS appointments: `bookings` table (start_time, end_time, provider_id, location_id, status)
- Historical booking patterns: same table, trailing 12 weeks

**Algorithm:**

A **density comparison** approach — not ML, just statistics.

**Step 1: Compute historical booking density.**

For each combination of `(location_id, day_of_week, time_slot)`:
- Time slots: 30-minute buckets during practice hours (e.g., 9:00-9:30, 9:30-10:00, ...)
- Historical: average number of bookings in this slot over trailing 4 weeks (same weekday only)
- Example: "Tuesdays, 9:00-9:30 AM, Gurgaon location → avg 3.2 bookings (last 4 Tuesdays)"

**Step 2: Compare upcoming schedule to historical.**

For the next 7 days, for each slot:
- `current_bookings` = count of bookings where `start_time` falls in this slot and `status != 'cancelled'`
- `historical_avg` = average from step 1
- `density_ratio` = `current_bookings / historical_avg`
- Gap detected if `density_ratio < 0.5` AND `historical_avg >= 2` (only flag slots that are normally booked)

**Step 3: Compute revenue gap.**

For each gap slot:
- `open_slots` = `historical_avg − current_bookings`
- `revenue_at_risk` = `open_slots × avg_revenue_per_slot` (from Razorpay, for that provider/service/time)

**Step 4: Rank gaps.**

Rank by `revenue_at_risk × (1 − density_ratio)` descending. Top 5 gaps become decision card candidates.

**Output (Decision Card):**

| Field | Content |
|-------|---------|
| **What Happened** | "X time slots in the next 7 days have significantly fewer bookings than usual. Estimated revenue gap: ₹Y." |
| **Why** | "Thursday 2:00-4:00 PM at Gurgaon: 2 bookings vs. usual 7. This slot typically fills with teeth cleaning appointments. Possible cause: school holiday season — fewer parent bookings." |
| **What to Do** | (1) Send promotional offer to patients due for cleaning, (2) Open slot to walk-ins with discount, (3) Reschedule a provider's admin time to fill the gap, (4) Run a social media post for "same-day appointments available." |
| **Expected ROI** | `open_slots × avg_revenue_per_slot × expected_fill_rate` where `expected_fill_rate` = 0.60 for last-minute interventions |
| **Confidence** | Based on: historical booking consistency (coefficient of variation of the slot), days until the gap (closer gaps = less fillable = lower confidence in ROI) |

**ROI Formula:**
```
ROI = Σ gap_hours_for_slot × avg_revenue_per_hour × fill_rate
```
- `fill_rate` = 0.60 for gaps <3 days out, 0.80 for gaps 3-7 days out
- `avg_revenue_per_hour` = from Razorpay data for that location/day-of-week/provider

**Refresh:** Daily at 5:30 AM IST (after no-show prediction). Re-runs when significant booking changes occur (≥3 cancellations in a day).

### 6.3 Revenue Trend Analysis

**Data Sources:**
- Razorpay payments: `payments` table (amount, paid_at, status)
- Zoho Books / Tally invoices: `invoices` table (amount, issue_date, status)
- PMS appointments: for correlation analysis (appointment volume vs. revenue)

**Algorithm:**

A **time-series decomposition** approach:

**Step 1: Build daily revenue series.**

- For each day in trailing 90 days: sum all captured payments + all paid invoices
- Deduplicate: if a payment is linked to an invoice (via entity resolution), count only once
- Store in `metric_values` table as `metric_name='daily_revenue'`

**Step 2: Decompose the series.**

Using `statsmodels.tsa.seasonal.seasonal_decompose`:
- `observed` = daily revenue
- `trend` = 7-day centered moving average
- `seasonal` = day-of-week pattern (Mondays higher, Sundays lower, etc.)
- `residual` = observed − trend − seasonal

**Step 3: Detect anomalies.**

- Compute rolling standard deviation of residuals (trailing 28 days)
- Flag days where `abs(residual) > 2.0 × rolling_std` as anomalies
- For each anomaly: determine direction (above/below trend) and magnitude

**Step 4: Root cause analysis (heuristic).**

For a negative anomaly (revenue dip):
1. Check: did appointment volume also drop? → If yes: "Fewer appointments this week — possible seasonal dip or reduced demand."
2. Check: did no-show rate spike? → If yes: "Revenue down despite normal bookings — 3 more no-shows than usual."
3. Check: did average revenue per appointment drop? → If yes: "Patients booking lower-cost services this week."
4. Check: is it concentrated in one location? → "The dip is specific to South Delhi location."
5. If none of the above: "Revenue dip without clear driver — monitoring for pattern."
6. Segment by new vs. returning patients, service type.

**Step 5: Trend classification.**

- If anomaly persists for 3+ consecutive days: classify as "emerging trend" (not a blip)
- If anomaly is isolated to 1-2 days: classify as "likely a blip — monitor"

**Output (Decision Card):**

| Field | Content |
|-------|---------|
| **What Happened** | "Revenue is 11% below expected trend over the last 3 days. This is the first sustained dip in 6 weeks." |
| **Why** | "Primary driver: Noida location revenue dropped 22%. Appointments are at normal levels (42 vs. 40 avg) but average revenue per appointment dropped from ₹2,100 to ₹1,600. Patients are booking lower-cost services." |
| **What to Do** | "Review Noida's service mix. Are providers suggesting higher-value treatments? Check if a new competitor has opened nearby offering lower prices." |
| **Expected ROI** | Revenue recovery amount if trend is reversed. |
| **Confidence** | Based on: anomaly magnitude (σ), duration (days), data quality. |

**ROI Formula:**
```
ROI = (expected_revenue − actual_revenue) × probability_trend_continues
```
Where `expected_revenue` = trend component value for the day, and `probability_trend_continues` is a heuristic based on anomaly persistence.

**Refresh:** Daily at 5:00 AM IST (uses trailing 90 days, updates with yesterday's data).

### 6.4 Pricing Optimization

**Data Sources:**
- PMS services: `services` table (name, category, default_price)
- PMS appointments: `bookings` table (service_id, status, start_time) — for utilization calculation
- Zoho Books line items: cost data if available — for margin calculation
- Razorpay payments: actual collected amounts

**Algorithm:**

A **utilization-based pricing recommendation** — formula-based, not causal inference.

**Step 1: Compute utilization per service.**

For each service in the practice:
```
utilization_rate = completed_appointments_last_90_days / total_available_slots_last_90_days
```
- `completed_appointments`: count of bookings where `service_id = X` AND `status = 'completed'`
- `total_available_slots`: (number of providers offering this service) × (available days in 90 days) × (slots per provider per day for this service duration)

**Step 2: Compute margin per service (if cost data available).**

```
margin_rate = (price − cost) / price
```
- `price`: from PMS `services.default_price`
- `cost`: from Zoho Books line items OR calibration survey (owner-provided cost estimate) OR default assumption (60% margin for dental, 50% for diagnostic)

**Step 3: Identify optimization candidates.**

For each service:
- If `utilization_rate > 85%` AND `margin_rate > 30%`: **Candidate for price increase** (demand exceeds capacity, healthy margin)
- If `utilization_rate < 60%` AND `margin_rate > 40%`: **Candidate for price decrease** (low utilization despite healthy per-unit economics — possibly priced too high)
- If `utilization_rate < 40%`: **Flag for review** — may be a poorly marketed or obsolete service

**Step 4: Estimate price elasticity effect.**

```
new_utilization_estimate = current_utilization × (1 − elasticity × price_change_pct)
new_revenue_estimate = new_utilization_estimate × available_slots × new_price
```

Where `elasticity = 0.4` (default for healthcare — relatively inelastic demand).

**Step 5: Generate recommendation.**

Only recommend if:
- For price increases: `new_revenue_estimate > current_revenue × 1.05` (at least 5% revenue improvement)
- For price decreases: `new_revenue_estimate > current_revenue` (revenue doesn't drop)
- `price_change_pct` is within ±20% (avoid extreme recommendations)
- Service has at least 10 completed appointments in trailing 90 days (minimum data threshold)

**Output (Decision Card):**

| Field | Content |
|-------|---------|
| **What Happened** | "Teeth Cleaning (₹800) has 92% utilization. At current demand, you're turning away patients or overworking providers." |
| **Why** | "At 92% utilization, your Teeth Cleaning service is capacity-constrained. Demand is high. Dental practices in your area typically charge ₹1,000-1,200 for comparable cleaning services." |
| **What to Do** | "Consider raising Teeth Cleaning price from ₹800 to ₹1,000 (+25%). At current demand elasticity (0.4), projected utilization would settle at ~83% — still healthy, with 27% higher revenue from this service." |
| **Expected ROI** | `Δrevenue = new_revenue − current_revenue` |
| **Confidence** | Based on: number of observations, variance in utilization rate, whether cost data is available (higher confidence with cost data) |

**ROI Formula:**
```
ΔRevenue = (new_price × new_utilization × available_slots) − (current_price × current_utilization × available_slots)
```
Where `new_utilization = current_utilization × (1 − elasticity × (new_price − current_price) / current_price)`

**Important: This is explicitly labeled "ESTIMATED — simplified pricing model."**

The card includes:
> ⚠️ This recommendation uses a simplified pricing model with assumed demand elasticity (0.4). Actual patient response to price changes may differ. We recommend: (1) Test the new price on new patients first, (2) Monitor weekly utilization after change, (3) Cortex will track actual outcomes and refine the recommendation.

**Refresh:** Monthly (1st of each month, or triggered manually from simulation).

---

## 7. Data Model Specification

### 7.1 Multi-Tenancy

**Schema-per-tenant isolation:**

```sql
-- Each tenant (practice) gets their own PostgreSQL schema
-- Schema naming: tenant_{tenant_id}
-- Example: tenant_abc123, tenant_def456

-- Public schema holds shared data:
--   - tenants (tenant_id, practice_name, created_at, status)
--   - feature_flags (per-tenant feature toggles)
--   - integration_registry (available integration types, not credentials)

-- In each tenant schema:
--   All business data tables below
--   credentials table (encrypted tokens)
--   user_preferences
```

**Tenant ID propagation:**
- Extracted from Clerk JWT (`org_id` claim maps to `tenant_id`)
- Set as PostgreSQL `search_path` at the beginning of each request: `SET search_path TO tenant_{tenant_id}`
- All queries automatically scoped to the tenant schema
- No `WHERE tenant_id = X` clauses needed on business tables (they're already isolated)

### 7.2 Core Entity Tables (per tenant schema)

```sql
-- ============================================================
-- PRACTICE & LOCATIONS
-- ============================================================

CREATE TABLE practice_profile (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    practice_name   TEXT NOT NULL,
    practice_type   TEXT NOT NULL,  -- dental, physiotherapy, diagnostic, eye_care, other
    annual_revenue_range TEXT,      -- ₹50L-1Cr, ₹1-3Cr, etc.
    total_providers INTEGER,
    city            TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE locations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,          -- "Gurgaon Clinic", "South Delhi Clinic"
    address         TEXT,
    city            TEXT,
    operating_hours JSONB,                  -- {"mon": {"open":"09:00","close":"20:00"}, ...}
    timezone        TEXT DEFAULT 'Asia/Kolkata',
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- PATIENTS / CUSTOMERS (unified across tools)
-- ============================================================

CREATE TABLE patients (
    canonical_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name      TEXT,
    last_name       TEXT,
    display_name    TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    primary_email   TEXT,                   -- From entity resolution
    primary_phone   TEXT,                   -- From entity resolution, +91 format
    date_of_birth   DATE,
    gender          TEXT,
    attributes      JSONB,                  -- Tool-specific attributes
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_patients_email ON patients(primary_email) WHERE primary_email IS NOT NULL;
CREATE INDEX idx_patients_phone ON patients(primary_phone) WHERE primary_phone IS NOT NULL;

-- ============================================================
-- PROVIDERS / EMPLOYEES
-- ============================================================

CREATE TABLE providers (
    canonical_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    role            TEXT,                   -- Dentist, Hygienist, Physiotherapist, etc.
    specialization  TEXT,
    attributes      JSONB,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE provider_locations (
    provider_id     UUID REFERENCES providers(canonical_id),
    location_id     UUID REFERENCES locations(id),
    PRIMARY KEY (provider_id, location_id)
);

-- ============================================================
-- SERVICES
-- ============================================================

CREATE TABLE services (
    canonical_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    category        TEXT,                   -- Consultation, Cleaning, RCT, Crown, etc.
    default_price   NUMERIC(10,2),          -- In rupees
    default_duration_minutes INTEGER,
    cost_estimate   NUMERIC(10,2),          -- From Zoho Books or calibration survey
    attributes      JSONB,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- APPOINTMENTS / BOOKINGS
-- ============================================================

CREATE TABLE bookings (
    canonical_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID REFERENCES patients(canonical_id),
    provider_id     UUID REFERENCES providers(canonical_id),
    service_id      UUID REFERENCES services(canonical_id),
    location_id     UUID REFERENCES locations(id),
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ NOT NULL,
    status          TEXT NOT NULL,          -- scheduled, completed, no_show, cancelled
    cancellation_reason TEXT,
    source_tool     TEXT NOT NULL,          -- practo, docengage, lybrate
    external_id     TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_bookings_start ON bookings(start_time);
CREATE INDEX idx_bookings_patient ON bookings(patient_id);
CREATE INDEX idx_bookings_provider ON bookings(provider_id);
CREATE INDEX idx_bookings_location_status ON bookings(location_id, status);
CREATE UNIQUE INDEX idx_bookings_external ON bookings(source_tool, external_id);

-- ============================================================
-- INVOICES
-- ============================================================

CREATE TABLE invoices (
    canonical_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID REFERENCES patients(canonical_id),  -- May be NULL for Tally data
    amount          NUMERIC(12,2) NOT NULL,
    currency        TEXT DEFAULT 'INR',
    status          TEXT NOT NULL,          -- draft, sent, paid, overdue, voided, bad_debt
    issue_date      DATE,
    due_date        DATE,
    paid_date       DATE,
    line_items      JSONB,                  -- [{service_id, description, amount, quantity}]
    source_tool     TEXT NOT NULL,          -- zoho_books, tally_csv
    external_id     TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_invoices_patient ON invoices(patient_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE UNIQUE INDEX idx_invoices_external ON invoices(source_tool, external_id);

-- ============================================================
-- PAYMENTS
-- ============================================================

CREATE TABLE payments (
    canonical_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id      UUID REFERENCES invoices(canonical_id),      -- May be NULL
    patient_id      UUID REFERENCES patients(canonical_id),      -- Resolved from customer email
    amount          NUMERIC(12,2) NOT NULL,
    currency        TEXT DEFAULT 'INR',
    status          TEXT NOT NULL,          -- completed, failed, refunded, pending
    payment_method  TEXT,                   -- upi, card, netbanking, wallet
    paid_at         TIMESTAMPTZ,
    source_tool     TEXT NOT NULL DEFAULT 'razorpay',
    external_id     TEXT NOT NULL,
    attributes      JSONB,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_payments_paid_at ON payments(paid_at);
CREATE INDEX idx_payments_patient ON payments(patient_id);
CREATE UNIQUE INDEX idx_payments_external ON payments(source_tool, external_id);

-- ============================================================
-- ENTITY RESOLUTION
-- ============================================================

CREATE TABLE entity_resolution (
    id              BIGSERIAL PRIMARY KEY,
    canonical_id    UUID NOT NULL,          -- The unified entity ID
    entity_type     TEXT NOT NULL,          -- patient, provider, service
    source_tool     TEXT NOT NULL,          -- practo, razorpay, zoho_books
    external_id     TEXT NOT NULL,
    match_method    TEXT NOT NULL,          -- exact_email, manual, new_entity
    confidence      NUMERIC(3,2) NOT NULL DEFAULT 1.0,
    resolved_at     TIMESTAMPTZ DEFAULT now(),
    UNIQUE(source_tool, external_id)
);

CREATE INDEX idx_resolution_canonical ON entity_resolution(canonical_id);

-- ============================================================
-- DECISIONS
-- ============================================================

CREATE TABLE decisions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_type   TEXT NOT NULL,          -- no_show_prediction, scheduling_gap, revenue_trend, pricing_optimization
    title           TEXT NOT NULL,          -- One-line summary
    summary         TEXT NOT NULL,          -- "What happened" — 2-3 sentences
    why_text        TEXT,                   -- Causal explanation in plain English
    recommendation  TEXT NOT NULL,          -- "What to do" — actionable steps
    estimated_roi   NUMERIC(12,2),          -- In rupees
    roi_methodology TEXT,                   -- How ROI was calculated
    confidence      NUMERIC(3,2) NOT NULL,  -- 0.00-1.00
    evidence_data   JSONB,                  -- Structured data for charts/tables
    limitations     TEXT,                   -- Known limitations of this decision
    status          TEXT DEFAULT 'active',  -- active, implemented, dismissed, snoozed, already_knew
    snooze_until    TIMESTAMPTZ,
    location_id     UUID REFERENCES locations(id),  -- NULL = all locations
    generated_at    TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_decisions_type_status ON decisions(decision_type, status);
CREATE INDEX idx_decisions_generated ON decisions(generated_at);

-- ============================================================
-- DECISION FEEDBACK
-- ============================================================

CREATE TABLE decision_feedback (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id     UUID REFERENCES decisions(id) ON DELETE CASCADE,
    feedback_type   TEXT NOT NULL,          -- implemented, not_useful, already_knew, snooze
    reason          TEXT,                   -- Optional reason for not_useful
    snooze_days     INTEGER,               -- For snooze feedback
    user_id         TEXT,                   -- Clerk user ID
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_feedback_decision ON decision_feedback(decision_id);

-- ============================================================
-- METRICS (time series)
-- ============================================================

CREATE TABLE metric_values (
    id              BIGSERIAL PRIMARY KEY,
    metric_name     TEXT NOT NULL,          -- daily_revenue, no_show_rate, utilization, collections_rate, appointment_count
    entity_type     TEXT,                   -- location, provider, service, or NULL for practice-level
    entity_id       UUID,                   -- ID of the entity
    date            DATE NOT NULL,
    value           NUMERIC(14,4) NOT NULL,
    tags            JSONB,                  -- Additional dimensions
    computed_at     TIMESTAMPTZ DEFAULT now(),
    UNIQUE(metric_name, entity_type, entity_id, date)
);

CREATE INDEX idx_metrics_name_date ON metric_values(metric_name, date);

-- ============================================================
-- PROVENANCE (data lineage)
-- ============================================================

CREATE TABLE provenance_log (
    id              BIGSERIAL PRIMARY KEY,
    entity_type     TEXT NOT NULL,
    canonical_id    UUID,
    source_tool     TEXT NOT NULL,
    external_id     TEXT,
    synced_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    sync_type       TEXT,                   -- batch, webhook, csv_upload
    record_count    INTEGER,
    status          TEXT DEFAULT 'success', -- success, partial, error
    error_message   TEXT
);

CREATE INDEX idx_provenance_tool_synced ON provenance_log(source_tool, synced_at);

-- ============================================================
-- SIMULATIONS
-- ============================================================

CREATE TABLE simulation_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variable_name   TEXT NOT NULL,          -- no_show_rate, avg_price, hours, providers, marketing_spend
    current_value   NUMERIC(14,4),
    target_value    NUMERIC(14,4),
    change_pct      NUMERIC(6,2),
    scope           TEXT,                   -- all_locations, location_id
    timeframe_days  INTEGER DEFAULT 30,
    projected_revenue_impact NUMERIC(12,2),
    projected_utilization_impact NUMERIC(6,4),
    confidence      NUMERIC(3,2),
    methodology     TEXT,
    result_data     JSONB,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- INTEGRATIONS & CREDENTIALS
-- ============================================================

CREATE TABLE credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool            TEXT NOT NULL,          -- practo, razorpay, zoho_books
    credential_type TEXT NOT NULL,          -- oauth, api_key, csv
    access_token_encrypted  TEXT,           -- Fernet-encrypted (NULL for CSV/API key)
    refresh_token_encrypted TEXT,
    api_key_encrypted       TEXT,           -- For Razorpay key_id + key_secret, JSON encrypted
    expires_at      TIMESTAMPTZ,
    scopes          TEXT[],
    status          TEXT DEFAULT 'active',  -- active, expired, revoked, error, disconnected
    last_error      TEXT,
    last_sync_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(tool)
);

-- ============================================================
-- PUSH NOTIFICATIONS
-- ============================================================

CREATE TABLE push_subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         TEXT NOT NULL,          -- Clerk user ID
    endpoint        TEXT NOT NULL,
    p256dh_key      TEXT NOT NULL,
    auth_key        TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, endpoint)
);

-- ============================================================
-- USER PREFERENCES
-- ============================================================

CREATE TABLE user_preferences (
    user_id         TEXT PRIMARY KEY,       -- Clerk user ID
    email_frequency TEXT DEFAULT 'daily',   -- daily, weekly, off
    email_include_metrics BOOLEAN DEFAULT true,
    push_enabled    BOOLEAN DEFAULT true,
    default_location_id UUID REFERENCES locations(id),  -- NULL = all
    no_show_cost_estimate NUMERIC(10,2),    -- From calibration survey
    calibration_data JSONB,                 -- Full survey responses
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);
```

### 7.3 Entity Resolution Rules

**Algorithm (v1 — exact email match + manual override):**

1. **Exact email match (highest priority):**
   - When a PMS patient has `email = 'priya@email.com'` AND a Razorpay payment has `customer_email = 'priya@email.com'` → same canonical patient
   - When a Zoho Books contact has `email = 'priya@email.com'` → same canonical patient
   - Email comparison is case-insensitive, whitespace-trimmed

2. **Exact phone match (fallback, added in v1.1):**
   - When email is not available in PMS: match on normalized phone number
   - Phone normalization: strip all non-digits, prefix with +91 if 10 digits, handle country codes

3. **No match — new entity:**
   - Patient has no email AND no phone match → create new canonical ID
   - Confidence: 1.0 (this is a new entity, not a low-confidence match)

4. **Manual merge (Settings UI):**
   - User sees list of "Unmatched patients" (patients without cross-tool links)
   - User can select 2+ patients and click "Merge" → creates resolution records linking them to same canonical ID
   - Match method: `manual`, Confidence: 1.0

**Resolution confidence computation:**

| Match Method | Confidence | Example |
|-------------|-----------|---------|
| `exact_email` | 0.95 | Both PMS and Razorpay have same email |
| `exact_email` (single source only) | 0.90 | Only one tool has the patient; no cross-reference needed |
| `manual` | 1.0 | User confirmed the match |
| `new_entity` | 1.0 | Truly new entity |
| `fuzzy_name_phone` (v1.1) | 0.70-0.90 | Name similarity + phone match |

### 7.4 Key Relationships

```
patients --< bookings >-- providers
patients --< invoices
patients --< payments
bookings >-- services
bookings >-- locations
providers >-- provider_locations --< locations
invoices --< payments (optional link)
```

---

## 8. API Specification

### 8.1 Authentication

All API endpoints require authentication via **Clerk JWT**.

**Request header:**
```
Authorization: Bearer <clerk_session_token>
X-Cortex-Tenant-ID: <tenant_id>
```

**Middleware flow:**
1. Nginx terminates TLS, forwards to FastAPI
2. FastAPI middleware: validate JWT with Clerk's JWKS endpoint
3. Extract `org_id` from JWT claims → `tenant_id`
4. Set PostgreSQL `search_path` to `tenant_{tenant_id}`
5. All subsequent queries are tenant-scoped

**Clerk organization mapping:**
- Each practice = one Clerk Organization
- Practice owner = Organization Admin
- Office manager = Organization Member (view + feedback permissions)

### 8.2 REST API Endpoints

**Base URL:** `https://api.cortexapp.in/api/v1`

#### Decisions

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/decisions` | List active decision cards | Query: `?status=active&limit=10&offset=0&location_id={uuid}` | `{ decisions: Decision[], total: int }` |
| `GET` | `/decisions/:id` | Decision detail with all evidence | — | `{ decision: DecisionDetail }` |
| `POST` | `/decisions/:id/feedback` | Submit feedback | `{ feedback_type: "implemented"\|"not_useful"\|"already_knew"\|"snooze", reason?: string, snooze_days?: int }` | `{ ok: true }` |

**Decision schema:**
```json
{
  "id": "uuid",
  "decision_type": "no_show_prediction",
  "title": "Recover 40% of Tuesday no-shows",
  "summary": "5 of 23 Tuesday morning appointments were no-shows...",
  "why_text": "Dr. Sharma's Tuesday patients are from Sector 14...",
  "recommendation": "Send morning-of reminder calls...",
  "estimated_roi": 34000.00,
  "roi_methodology": "Historical no-show rate × avg revenue × intervention effect",
  "confidence": 0.78,
  "evidence_data": { ... },
  "limitations": "Does not account for seasonal variation...",
  "status": "active",
  "badge": "high_roi",
  "location_id": null,
  "generated_at": "2026-07-15T06:00:00+05:30",
  "data_freshness": {
    "practo": { "last_synced": "2026-07-15T05:45:00+05:30", "age_minutes": 15 },
    "razorpay": { "last_synced": "2026-07-15T05:30:00+05:30", "age_minutes": 30 }
  }
}
```

#### Insights / Metrics

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/insights` | Dashboard summary metrics | Query: `?location_id={uuid}` | `{ metrics: { revenue_mtd, no_show_rate, utilization, collections_rate } }` |
| `GET` | `/insights/:metric/timeseries` | Timeseries data for a metric | Query: `?from=2026-06-01&to=2026-07-15&entity_type=location&entity_id={uuid}` | `{ metric_name, values: [{ date, value }] }` |

**Metrics response schema:**
```json
{
  "metrics": {
    "revenue_mtd": {
      "value": 1840000.00,
      "comparison_value": 1680000.00,
      "change_pct": 9.5,
      "change_direction": "up",
      "data_freshness_minutes": 30,
      "formatted": "₹18.4L"
    },
    "no_show_rate": {
      "value": 0.072,
      "comparison_value": 0.083,
      "change_pct": -13.3,
      "change_direction": "down",
      "formatted": "7.2%"
    },
    "utilization": {
      "value": 0.68,
      "target": 0.75,
      "formatted": "68%"
    },
    "collections_rate": {
      "value": 0.94,
      "formatted": "94%"
    }
  }
}
```

#### Simulations

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `POST` | `/simulations` | Run a simulation | `{ variable: string, current_value: number, target_value: number, change_pct: number, scope?: string, timeframe_days: int }` | `{ simulation: SimulationResult }` |
| `GET` | `/simulations` | List saved simulations | Query: `?limit=10` | `{ simulations: SimulationResult[] }` |
| `GET` | `/simulations/:id` | Get saved simulation | — | `{ simulation: SimulationResult }` |

**Simulation request schema:**
```json
{
  "variable": "no_show_rate",
  "current_value": 7.2,
  "target_value": 5.8,
  "change_pct": -19.4,
  "scope": "all_locations",
  "timeframe_days": 30
}
```

**Simulation result schema:**
```json
{
  "id": "uuid",
  "variable_name": "no_show_rate",
  "current_value": 7.2,
  "target_value": 5.8,
  "change_pct": -19.4,
  "timeframe_days": 30,
  "projected_revenue_impact": 33000.00,
  "revenue_impact_lower": 26400.00,
  "revenue_impact_upper": 39600.00,
  "projected_utilization_impact": 0.03,
  "confidence": 0.80,
  "methodology": "Expected value = (current_rate - target_rate) × appointments/month × avg_revenue/slot",
  "limitations": ["Assumes all no-show slots are rebooked", "Does not account for seasonality"],
  "created_at": "2026-07-15T10:30:00+05:30"
}
```

#### Integrations

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/integrations` | List all integrations + status | — | `{ integrations: Integration[] }` |
| `POST` | `/integrations/connect` | Start OAuth flow | `{ tool: "practo"\|"docengage"\|"lybrate"\|"razorpay"\|"zoho_books" }` | `{ redirect_url: string }` |
| `GET` | `/integrations/callback` | OAuth callback (handled by auth provider) | Query: `?code=&state=` | Redirects to integration settings |
| `POST` | `/integrations/:tool/disconnect` | Disconnect an integration | — | `{ ok: true }` |
| `GET` | `/integrations/:tool/status` | Get integration health | — | `{ tool, status, last_sync_at, data_freshness_minutes }` |
| `POST` | `/integrations/tally/upload` | Upload Tally CSV | `multipart/form-data: file` | `{ ok: true, rows_processed: int, validation_errors: [] }` |

**Integration schema:**
```json
{
  "tool": "practo",
  "status": "healthy",
  "status_color": "green",
  "last_sync_at": "2026-07-15T05:45:00+05:30",
  "data_freshness_minutes": 15,
  "record_count": 2847,
  "can_disconnect": true,
  "can_reconnect": false,
  "setup_instructions": null
}
```

#### Business Profile

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/business/profile` | Get practice profile | — | `{ practice: PracticeProfile }` |
| `PATCH` | `/business/profile` | Update practice profile | `{ practice_name?, practice_type?, ... }` | `{ practice: PracticeProfile }` |
| `GET` | `/business/locations` | List locations | — | `{ locations: Location[] }` |
| `POST` | `/business/locations` | Add location | `{ name, address?, operating_hours?, ... }` | `{ location: Location }` |
| `PATCH` | `/business/locations/:id` | Update location | `{ name?, operating_hours?, ... }` | `{ location: Location }` |
| `GET` | `/business/settings` | Get user preferences | — | `{ preferences: UserPreferences }` |
| `PATCH` | `/business/settings` | Update preferences | `{ email_frequency?, push_enabled?, ... }` | `{ preferences: UserPreferences }` |

#### Entity Resolution (Manual)

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `GET` | `/entities/unmatched` | List patients with low/no cross-tool matches | Query: `?entity_type=patient&limit=20` | `{ entities: UnmatchedEntity[] }` |
| `POST` | `/entities/merge` | Merge two entities | `{ canonical_id, merge_entity_id }` | `{ ok: true, canonical_id }` |
| `POST` | `/entities/split` | Undo a merge | `{ canonical_id, split_entity_id }` | `{ ok: true }` |

#### Notifications

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|-------------|----------|
| `POST` | `/notifications/push/subscribe` | Register push subscription | `{ endpoint, p256dh_key, auth_key }` | `{ ok: true }` |
| `DELETE` | `/notifications/push/unsubscribe` | Remove push subscription | `{ endpoint }` | `{ ok: true }` |

### 8.3 Standard Error Responses

```json
{
  "error": {
    "code": "invalid_token",
    "message": "The authentication token has expired. Please log in again.",
    "status": 401
  }
}
```

**Error codes:**

| Code | Status | When |
|------|--------|------|
| `invalid_token` | 401 | JWT expired, invalid, or missing |
| `tenant_not_found` | 404 | Tenant schema doesn't exist |
| `insufficient_permissions` | 403 | User doesn't have required role |
| `integration_not_connected` | 400 | Requested operation requires a connected integration |
| `integration_auth_failed` | 400 | OAuth token exchange failed |
| `rate_limited` | 429 | Too many requests |
| `validation_error` | 422 | Request body validation failed |
| `simulation_failed` | 500 | Simulation computation error |
| `data_sync_in_progress` | 202 | Data is still syncing, try again later |

### 8.4 Pagination Convention

```json
{
  "data": [...],
  "pagination": {
    "total": 42,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

---

## 9. Dashboard & UI Specification

### 9.1 Technology Stack

- **Framework:** TanStack Start (React + Vite + Tailwind CSS)
- **Routing:** TanStack Router (file-based)
- **State Management:** TanStack Query (server state) + React Context (UI state)
- **Charts:** Recharts (lightweight, React-native, sufficient for v1 bar/line charts)
- **Date Handling:** date-fns + date-fns-tz (IST timezone)
- **Forms:** React Hook Form + Zod validation
- **Auth:** Clerk React SDK

### 9.2 Screen List

| Route | Page | Priority |
|-------|------|----------|
| `/` | Landing page (unauthenticated) | P0 |
| `/signup` | Signup flow (Clerk-hosted or embedded) | P0 |
| `/onboarding` | Onboarding wizard (profile → goals → integrations → sync) | P0 |
| `/dashboard` | Main dashboard (decisions + metrics + simulation quick-start) | P0 |
| `/decisions/:id` | Decision detail (expanded view with all evidence) | P0 |
| `/simulate` | Simulation page (full input + output) | P1 |
| `/integrations` | Integration settings (status, connect, disconnect) | P0 |
| `/settings` | Practice settings (profile, locations, preferences, entity merge) | P0 |
| `/settings/entities` | Entity resolution review (unmatched patients, merge UI) | P1 |

### 9.3 Screen Specifications

#### 9.3.1 Landing Page (`/`)

**States:**
- **Default:** Marketing content with "Sign Up Free" CTA
- **Authenticated:** Redirect to `/dashboard`

**Content (v1 minimal):**
- Hero: "AI-powered decisions for your healthcare practice" + "We found ₹1.2L in missed revenue for a 3-location dental practice in Gurgaon."
- Three value props (with icons): "Connect your tools" / "Get actionable decisions" / "Watch revenue grow"
- Social proof (when available): "Used by practices in Delhi NCR"
- Footer: "Built in Delhi NCR" · Privacy · Terms · Contact

#### 9.3.2 Dashboard (`/dashboard`)

**States:**

| State | Condition | What Renders |
|-------|-----------|-------------|
| **Loading** | Initial data fetch in progress | Skeleton pulse animation on metric cards and decision list. "Loading your insights..." |
| **Empty — no integrations** | User signed up but connected no tools | "Welcome to Cortex! Connect your tools to start receiving insights. [Connect Tools →]" |
| **Empty — syncing** | Integrations connected, initial sync in progress | Progress bar: "We're analyzing your practice data. This usually takes 5-15 minutes. [View progress]" |
| **Empty — no decisions** | Data synced but no decisions generated (cold start) | "We've processed your data but need more history to generate reliable insights. This is normal for new accounts. We'll alert you when patterns emerge — usually within 1-2 days." |
| **Normal** | Data available, decisions present | Full dashboard with metrics, decision cards, simulation quick-start |
| **Partial data** | Some integrations healthy, some degraded | Normal dashboard with yellow banner: "Practo data hasn't synced in 18 hours. Some insights may be stale. [Check connection]" |
| **Error** | API request failed | "Unable to load dashboard. [Retry]" with error details |

**Layout (desktop — 1440px reference):**

```
┌──────────────────────────────────────────────────────────────────────┐
│  LEFT SIDEBAR (240px)          │  MAIN CONTENT (1200px)              │
│                                │                                      │
│  ☰ Cortex                      │  ☀️ Good morning, Dr. Kumar         │
│                                │  SmileCare Dental   📍 [All ▼]      │
│  📊 Dashboard                  │                                      │
│  ⚡ Decisions                  │  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  📈 Simulation                 │  │Revenue  │ │No-Show  │ │Utilizat│ │
│  ⚙️ Settings                   │  │MTD      │ │Rate     │ │ion     │ │
│      Integrations             │  └─────────┘ └─────────┘ └────────┘ │
│      Practice Profile         │                                      │
│      Entity Review            │  ⚡ Today's Decisions                 │
│                                │  ┌─────────────────────────────────┐ │
│  ────────────────────────      │  │ Decision Card 1                 │ │
│                                │  ├─────────────────────────────────┤ │
│  Dr. Rajesh Kumar              │  │ Decision Card 2                 │ │
│  SmileCare Dental              │  ├─────────────────────────────────┤ │
│  [Log Out]                     │  │ Decision Card 3                 │ │
│                                │  └─────────────────────────────────┘ │
│                                │                                      │
│                                │  📊 Simulation Quick-Start           │
│                                │                                      │
│                                │  📋 Recent Activity                  │
└────────────────────────────────┴──────────────────────────────────────┘
```

**Sidebar:**
- Logo + "Cortex"
- Navigation items with icons
- Active item highlighted
- User info at bottom (from Clerk)
- Collapsible on mobile (hamburger menu)

**Responsive behavior:**
- **Desktop (≥1024px):** Full sidebar + dashboard layout
- **Tablet (768-1023px):** Collapsed sidebar (icons only). Metric cards: 2×2 grid.
- **Mobile (<768px):** Hidden sidebar (hamburger toggle). Metric cards: stacked vertically. Decision cards: full-width. Simplified charts.

#### 9.3.3 Decision Detail (`/decisions/:id`)

Full-width page (no sidebar). Scrollable.

**Sections (vertical scroll):**
1. Header: Title, ROI badge, confidence, generated time, data freshness
2. "What Happened" — chart(s), summary text
3. "Why It's Happening" — evidence breakdown, statistical test results
4. "What To Do" — numbered recommendations, implementation steps, costs
5. "Expected ROI" — calculation breakdown, confidence interval, methodology, limitations
6. Feedback buttons (sticky at bottom on mobile)
7. "Simulate This" — inline simulation widget

**Chart types used:**
- Bar chart: no-show rate by day of week
- Line chart: revenue trend over time with anomaly highlight
- Horizontal bar: utilization by provider/service
- Simple number cards: metric values

#### 9.3.4 Integration Settings (`/integrations`)

```
┌──────────────────────────────────────────────────────────────────────┐
│  Integrations                                                        │
│                                                                      │
│  Connected Tools (3/3)                                               │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ ✅ Practo                    ● Connected     Last sync: 15m ago│ │
│  │    Appointments: 2,847    Patients: 1,203    Providers: 8       │ │
│  │    [Disconnect]  [Re-sync Now]                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ ✅ Razorpay                  ● Connected     Last sync: 30m ago│ │
│  │    Payments: 4,521    Refunds: 312                              │ │
│  │    [Disconnect]  [Re-sync Now]                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ ⚠️ Zoho Books               ○ Degraded      Last sync: 8h ago  │ │
│  │    Invoices: 856    Contacts: 342                               │ │
│  │    "Sync delayed due to Zoho rate limits. Will retry in 2h."    │ │
│  │    [Reconnect]  [Retry Now]                                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  + Add Integration                                                   │
│  Available: Tally (CSV import)                                       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 9.4 UI Components Library

**Shared components (built once, reused):**

| Component | Usage |
|-----------|-------|
| `MetricCard` | Dashboard KPI tiles |
| `DecisionCard` | Dashboard decision list + detail page |
| `ConfidenceBar` | Visual confidence indicator |
| `ROIBadge` | Colored ROI level badge |
| `FreshnessIndicator` | Data age dot + tooltip |
| `IntegrationStatusCard` | Integration settings listing |
| `ProgressBar` | Sync progress, simulation progress |
| `Skeleton` | Loading states |
| `EmptyState` | No-data states (icon + message + CTA) |
| `ErrorBanner` | Dismissible error messages |
| `SimulationInput` | Variable selector + change input |
| `SimulationOutput` | Results display with methodology |

### 9.5 Design Tokens (Tailwind Config)

**Colors:**
- Primary: `#4F46E5` (Indigo-600) — buttons, links, active states
- Success: `#10B981` (Emerald-500) — high confidence, revenue up
- Warning: `#F59E0B` (Amber-500) — medium confidence, data stale
- Danger: `#EF4444` (Red-500) — low confidence, revenue down, errors
- Neutral: `#6B7280` (Gray-500) — secondary text
- Background: `#F9FAFB` (Gray-50) — page background
- Card: `#FFFFFF` — card backgrounds
- Border: `#E5E7EB` (Gray-200) — card borders

**Typography:**
- Font: Inter (sans-serif) — loaded from Google Fonts
- Headings: 24px (dashboard title), 20px (card titles), 16px (section headers)
- Body: 14px (main content), 12px (secondary/meta text)
- Numbers: Tabular figures (`font-variant-numeric: tabular-nums`) for metric alignment

**Spacing:**
- Page padding: 24px
- Card padding: 20px
- Card gap: 16px
- Section gap: 32px

---

## 10. Success Metrics & Testing Criteria

### 10.1 What "The Product Works" Means — Per Feature

| Feature | Test Scenario | Pass Criteria |
|---------|--------------|---------------|
| **Auth (Clerk)** | New user signs up, verifies email, logs in, logs out, resets password | All flows complete without error. JWT present in API calls. |
| **Multi-Tenancy** | Practice A and Practice B created. Each connects PMS. Practice A's dashboard shows only Practice A's data. | Cross-tenant data leak test: query Practice A's API with Practice B's tenant ID → 403 or empty results. |
| **PMS Integration** | Connect test Practo account. Wait for initial sync. Check bookings table has records. | Bookings appear within 15 minutes. Status values map correctly. Appointments from last 30 days present. |
| **Razorpay Integration** | Connect test Razorpay account. Make a test payment. Check webhook received and payment appears. | Payment appears within 5 minutes of webhook. Amount correctly converted from paise to rupees. |
| **Zoho Books Integration** | Connect test Zoho Books account. Pull invoices. Verify invoice amounts. | Invoices appear. Status mapping correct. Contact data linked to patients where email matches. |
| **Tally CSV Bridge** | Upload valid Tally CSV. Upload invalid CSV. Upload empty CSV. | Valid: rows ingested, transactions appear. Invalid: rejection with error message listing expected columns. Empty: rejection with "no data rows" message. |
| **Entity Resolution** | Patient with email exists in PMS and Razorpay. Patient without email exists only in PMS. | Email-match patient gets single canonical ID across both tools. No-email patient gets new canonical ID. Resolution records created. |
| **No-Show Prediction** | Practice with 12 weeks of appointment data (some no-shows). Run prediction. | Decision card generated. Risk scores assigned. Top 5 risky appointments listed. Confidence > 50%. |
| **Scheduling Gap Detection** | Practice with sparse upcoming schedule in normally-busy slot. | Gap detected. Revenue at risk calculated. Decision card shows open slots + recommendation. |
| **Revenue Trend Analysis** | Simulate a 3-day revenue dip (below 2σ). | Anomaly detected. Root cause analysis runs (checks appointments, no-shows, locations). Decision card identifies primary driver. |
| **Pricing Optimization** | Service with 92% utilization, healthy margin. | Recommendation to raise price appears. Elasticity formula applied. Projected revenue change calculated. |
| **Dashboard** | User logs in, dashboard loads with metrics + decisions. | Loads in < 500ms (local dev) or < 2s (production). All 4 metric cards render with correct values. Decision cards sorted by ROI×confidence. |
| **Decision Card UI** | Click card → expands to detail. Click "Implemented" → card moves. Click "Not Useful" → card hidden. | All interactions work. Feedback stored in DB. Detail page shows all 5 question-answers. |
| **Morning Digest Email** | Two practices with different decision sets. Email job runs at 6:00 AM IST. | Each practice gets email with THEIR decisions only. Time is ±5 min of 6:00 AM IST. Open tracking works. |
| **Push Notifications** | New high-ROI decision generated. User has push enabled. | Notification appears in browser. Click opens decision detail. No more than 3 notifications in a day. |
| **Simulation** | Run "Reduce no-shows by 20%." Run "Raise prices 10%." | Each produces output with: projected impact, confidence band, methodology, limitations. Saved to history. |
| **Location Filter** | Practice with 3 locations. Select "Gurgaon" from filter. | Metrics and decisions update to show Gurgaon-only data. "All Locations" restores full view. |

### 10.2 Pre-Pilot Internal QA Checklist

Before the first pilot sees the product:

1. **End-to-end onboarding:** Complete full signup → survey → integration wizard → initial sync → first insight. Time the process. Target: < 30 minutes from signup to first decision card.
2. **Data integrity:** Verify 10 random appointments, 10 payments, and 10 invoices. Cross-check amounts, dates, status values against source tool raw data.
3. **Entity resolution accuracy:** Manually verify 20 patient matches. Count correct/incorrect/total. Target: > 90% accuracy for exact email matches.
4. **Decision quality spot check:** Review 10 generated decision cards. Verify: ROI calculation is mathematically correct, evidence data supports the conclusion, recommendation is actionable, confidence score is justified by sample size.
5. **Zero-state handling:** Create a fresh practice with no data. Verify every screen handles empty state gracefully.
6. **Error recovery:** Disconnect a tool. Verify: status shows correctly, related decisions are suppressed, reconnect flow works. Reconnect. Verify: data resumes syncing, decisions reappear.
7. **Email delivery:** Verify morning digest arrives at correct time with correct content for 2 different practices.
8. **Browser compatibility:** Test on Chrome (latest), Firefox (latest), Safari (latest). Mobile: Chrome on Android, Safari on iOS. Verify responsive layout.
9. **Performance:** Dashboard load < 2 seconds on a simulated 3G connection. Simulation result < 10 seconds.
10. **Security:** Verify tenant isolation (cannot access another tenant's data even with direct API call). Verify tokens encrypted at rest. Verify no secrets in logs.

### 10.3 Pilot Success Metrics

For each pilot, track daily:

| Metric | Target | How to Measure |
|--------|--------|---------------|
| **Daily Active Usage** | ≥ 3 days/week (owner or office manager logs in) | `last_active_at` timestamp updated on each authenticated API call |
| **Decisions Viewed** | ≥ 5/week (view decision detail, not just dashboard list) | Count `GET /decisions/:id` per practice per week |
| **Feedback Rate** | ≥ 60% of viewed decisions receive feedback | `(feedback_count / viewed_count) × 100` |
| **Decisions Implemented** | ≥ 2/week (user clicks "Implemented") | Count `feedback_type = 'implemented'` per week |
| **ROI Claimed** | Pilot can point to ₹X saved or earned | Qualitative: weekly check-in call. "Can you point to one thing Cortex helped with this week? What was the impact?" |
| **Net Promoter Score** | ≥ 7/10 ("How likely are you to recommend Cortex to another practice owner?") | Ask at end of pilot month 1 and month 2 |
| **Conversion Intent** | ≥ 2 of 3 pilots willing to pay after free period | Direct ask: "The free period ends in 2 weeks. Would you continue at ₹4,999/month?" |

**Pilot health dashboard (founder-only, internal):**

```
┌──────────────────────────────────────────────────────────────────────┐
│  Pilot Health                                                        │
│                                                                      │
│  Practice        Status    Active    Decisions   Implemented   ROI   │
│  ─────────────────────────────────────────────────────────────────── │
│  SmileCare       🟢 Active  5/7 days  12 viewed    4 done      ₹41K │
│  Delhi Physio    🟡 3/7      2/7 days   5 viewed    1 done      ₹8K  │
│  ClearVision     🟢 Active  6/7 days  15 viewed    6 done      ₹67K │
│                                                                      │
│  ⚠️ Delhi Physio: Low engagement. Schedule check-in call.            │
└──────────────────────────────────────────────────────────────────────┘
```

**Pilot exit criteria — pilot is successful if:**
- Active for 6+ weeks
- Feedback rate > 50%
- At least 5 decisions implemented
- Owner can name at least one concrete ROI example
- Willing to be a reference/case study
- Converts to paid at ₹4,999/mo

**Pilot exit criteria — pilot needs investigation if:**
- Active < 2 days/week for 2 consecutive weeks
- Feedback rate < 30%
- Zero decisions implemented after 4 weeks
- Owner says "I don't know if it's helping"

---

## 11. v1 Out-of-Scope (Explicit)

The following features are **explicitly excluded** from Cortex v1. They are documented here to prevent scope creep. Any request to add one of these during v1 development should be deflected: "This is planned for v2. Let's validate the core first."

### Architecture & AI
- ❌ LangGraph multi-agent system (we use 2-function Celery task chain: Scheduler + Decision Engine)
- ❌ Causal inference engine (DoWhy + EconML + structural causal models). v1 uses statistical tests + formula-based estimation
- ❌ Self-hosted LLM (Llama 3 8B/70B via vLLM). v1 uses OpenAI API only (GPT-4o-mini for routine, GPT-4o for complex)
- ❌ GPU infrastructure or GPU instances
- ❌ TimescaleDB hypertables (plain PostgreSQL tables for metrics — add TimescaleDB only if query perf demands it)
- ❌ pgvector (no vector embeddings needed for v1 decisions — add when we do semantic similarity)
- ❌ Monte Carlo simulation engine (formula-based single-variable estimation only)
- ❌ Multi-variable simulation (single-variable only)
- ❌ Multi-model tier routing (no "Small LLM" tier — all LLM calls go through OpenAI API)
- ❌ Feature store (Feast) for ML training
- ❌ Federated learning / cross-practice model sharing

### Product Features
- ❌ Chat interface (no chatbot, no conversational AI, no "ask Cortex anything")
- ❌ Custom metric builder / custom dashboard builder
- ❌ Peer benchmarking ("How does my practice compare to others?")
- ❌ Automated action execution (Cortex recommends, does NOT execute — no auto-booking, no auto-messaging)
- ❌ Mobile app (iOS/Android). Responsive web only.
- ❌ Slack / WhatsApp / Teams integration
- ❌ Multi-vertical support (healthcare only; D2C is the documented fallback if healthcare fails, not a concurrent vertical)
- ❌ Marketplace for third-party decision modules
- ❌ White-label / embedded version
- ❌ Multi-language support (English only for v1; Hindi in v2)
- ❌ Voice interface
- ❌ PDF report export (save simulation as PDF is listed in UI mockups but deferred — v1 uses "Copy link" instead)
- ❌ Patient-facing features (patient portal, self-scheduling, patient notifications)
- ❌ Insurance claims integration

### Integrations
- ❌ Integrations beyond PMS + Razorpay + Zoho Books/Tally
- ❌ Website analytics (Google Analytics, Meta Pixel)
- ❌ Marketing platforms (Meta Ads, Google Ads)
- ❌ Email marketing (Mailchimp, Klaviyo)
- ❌ WhatsApp Business API
- ❌ SMS gateway integration (Cortex recommends reminders but does not send them)
- ❌ HRIS integration (attendance, payroll)
- ❌ Inventory/supply chain integration
- ❌ Zapier / generic webhook catch-all

### Business & Operations
- ❌ Self-serve billing / payment processing (founder handles billing manually for pilots)
- ❌ Annual subscription billing (monthly only, manual)
- ❌ GST-compliant invoicing (founder issues manual invoices)
- ❌ SOC 2 / ISO 27001 compliance (DPDP Act compliance only, minimal)
- ❌ Dedicated customer success manager
- ❌ Onboarding call service (self-serve onboarding only; founder may choose to do calls but it's not a product feature)
- ❌ SLA guarantees for uptime or data freshness
- ❌ Multi-user roles beyond Owner + Viewer (no "Manager" role in v1)

### When to Revisit These
Each of these exclusions has a trigger for v2 consideration:

| Feature | v2 Trigger |
|---------|-----------|
| Causal inference engine | 3 paying customers with ≥ 6 months of data; founder has engineering bandwidth |
| Self-hosted LLM | ≥ 20 paying customers; API costs exceed ₹15,000/month |
| TimescaleDB + pgvector | Query latency exceeds 2 seconds for metric timeseries or entity search |
| Multi-agent system | ≥ 5 decision types running daily; need parallel processing |
| Mobile app | ≥ 30% of dashboard traffic from mobile devices |
| Marketplace | ≥ 20 paying customers in 2+ verticals |
| WhatsApp integration | ≥ 3 pilots requesting WhatsApp notifications during pilot phase |

---

## Appendix A: Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Runtime** | Python 3.12+ | 3.12 | Backend language |
| **Web Framework** | FastAPI | 0.111+ | REST API |
| **Frontend** | TanStack Start (React 19 + Vite) | Latest | Web UI |
| **CSS** | Tailwind CSS | 4.x | Styling |
| **Charts** | Recharts | 2.x | Dashboard charts |
| **Database** | PostgreSQL | 16 | Primary data store |
| **Queue** | Celery + Redis | 5.4+ / 7.x | Async task processing |
| **Auth** | Clerk | Latest | User management, JWT |
| **LLM** | OpenAI API (GPT-4o-mini, GPT-4o) | Latest | Natural language generation |
| **ML** | scikit-learn, statsmodels | 1.5+ / 0.14+ | Logistic regression, time-series |
| **Email** | Resend or SendGrid | Latest | Transactional email |
| **Encryption** | Fernet (cryptography) | 42+ | Credential encryption |
| **Infrastructure** | Docker Compose | Latest | Deployment |
| **Hosting** | DigitalOcean (Bangalore) | — | Production VPS |
| **CI/CD** | GitHub Actions | — | Testing, deployment |
| **Monitoring** | Sentry (free tier) | Latest | Error tracking |

---

## Appendix B: Directory Structure

```
cortex/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── middleware.py         # Auth, tenant, rate-limiting
│   │   ├── routes/
│   │   │   ├── decisions.py
│   │   │   ├── insights.py
│   │   │   ├── simulations.py
│   │   │   ├── integrations.py
│   │   │   ├── business.py
│   │   │   ├── entities.py
│   │   │   └── notifications.py
│   │   └── schemas.py           # Pydantic models
│   ├── core/
│   │   ├── config.py            # Environment, settings
│   │   ├── database.py          # DB connection, schema management
│   │   ├── security.py          # Encryption, token validation
│   │   └── tenant.py            # Schema-per-tenant management
│   ├── integrations/
│   │   ├── base.py              # Abstract connector
│   │   ├── practo.py
│   │   ├── docengage.py
│   │   ├── lybrate.py
│   │   ├── razorpay.py
│   │   ├── zoho_books.py
│   │   └── tally_csv.py
│   ├── pipeline/
│   │   ├── ingestion.py         # Pull data from integrations
│   │   ├── normalization.py     # Map to unified schema
│   │   ├── entity_resolution.py # Match entities across tools
│   │   └── metrics.py           # Compute derived metrics
│   ├── decisions/
│   │   ├── no_show.py           # No-show prediction logic
│   │   ├── scheduling_gap.py    # Gap detection logic
│   │   ├── revenue_trend.py     # Revenue analysis logic
│   │   ├── pricing.py           # Pricing optimization logic
│   │   └── card_builder.py      # Decision card assembly + LLM
│   ├── simulation/
│   │   └── engine.py            # Single-variable formula engine
│   ├── notifications/
│   │   ├── email_digest.py      # Morning digest email
│   │   └── push.py              # Web push notifications
│   ├── tasks/
│   │   ├── celery_app.py        # Celery configuration
│   │   ├── sync_tasks.py        # Scheduled sync jobs
│   │   └── decision_tasks.py    # Decision generation jobs
│   └── db/
│       └── migrations/          # Alembic migrations
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── index.tsx        # Landing page
│   │   │   ├── dashboard.tsx
│   │   │   ├── decisions.$id.tsx
│   │   │   ├── simulate.tsx
│   │   │   ├── integrations.tsx
│   │   │   ├── settings.tsx
│   │   │   └── onboarding.tsx
│   │   ├── components/
│   │   │   ├── MetricCard.tsx
│   │   │   ├── DecisionCard.tsx
│   │   │   ├── ConfidenceBar.tsx
│   │   │   ├── ROIBadge.tsx
│   │   │   ├── LoadingSkeleton.tsx
│   │   │   └── ...
│   │   ├── hooks/
│   │   │   ├── useDecisions.ts
│   │   │   ├── useMetrics.ts
│   │   │   └── useAuth.ts
│   │   └── styles/
│   │       └── app.css
│   └── ...
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.worker
├── Dockerfile.frontend
├── nginx.conf
└── README.md
```

---

*This document is the binding product specification for Cortex v1. All implementation decisions should reference sections above. Any deviation requires updating this spec and flagging to the team lead.*

*Version: 1.0 — 2026-07-15*
*Author: Founding Systems Architect*
