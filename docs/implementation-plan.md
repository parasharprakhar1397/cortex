# Cortex v1 — Implementation Plan

> **Build Order for Solo Founder | Delhi NCR | 2026**
> **Baseline:** Product Spec v1 (`product-spec.md`). Strategy locked (Plan Revision 5).
> **Principle:** Every task ends with something demonstrable. Defer everything not needed for first pilot.

---

## How to Use This Plan

Work through tasks in order. Each task is designed to be completed in 1-3 days. Do not start task N+1 until task N's acceptance criteria are met. After each task, you should be able to open a browser and see something new working.

**Effort estimates assume:** 5-6 focused hours/day of development. The remaining 2-4 hours/day go to networking (per the acquisition strategy) and pilot support.

---

## PHASE 0: SKELETON (Week 1-2)

> *Goal: A running web application with authentication. Zero business logic. Just the frame.*

---

### Task 0.1: Project Scaffolding
**Why this comes first:** Nothing else can be built without a project to build in.

**Objective:** Create the project repository with a running FastAPI app, Docker setup, and CI.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, health check
│   └── requirements.txt     # fastapi, uvicorn, sqlalchemy, etc.
├── docker-compose.yml       # api + postgres + redis services
├── Dockerfile
├── .github/workflows/
│   └── ci.yml               # lint + test on push
├── .env.example
└── README.md
```

**Dependencies:** None.

**Acceptance criteria:**
- [ ] `docker compose up` starts API on http://localhost:8000
- [ ] `GET /health` returns `{"status": "ok", "version": "0.1.0"}`
- [ ] Push to GitHub triggers CI, tests pass
- [ ] Hot reload works (edit a file, API restarts automatically)

**Effort:** 1 day.

**Demonstrable:** Running API. Browser shows `{"status": "ok"}`.

---

### Task 0.2: Database Foundation
**Why this comes next:** Every feature needs a database.

**Objective:** PostgreSQL running with Alembic migrations and schema-per-tenant isolation.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py           # SQLAlchemy Base, get_session
│   │   ├── migrations/       # Alembic env + versions/
│   │   └── tenant.py         # set_tenant_schema() middleware
│   └── alembic.ini
```

**Dependencies:** Task 0.1.

**Acceptance criteria:**
- [ ] `docker compose up` starts PostgreSQL alongside API
- [ ] API connects to PostgreSQL at startup (fail fast if DB unreachable)
- [ ] `alembic upgrade head` creates tables
- [ ] Can create a tenant schema: `SET search_path TO tenant_test; CREATE TABLE test (id UUID);`
- [ ] Test: insert row into tenant schema, query it back, no data in public schema

**Effort:** 1.5 days.

**Demonstrable:** API can create and query tenant-isolated data. No business tables yet — just the isolation mechanism.

---

### Task 0.3: Authentication
**Why this comes next:** Every subsequent feature is gated on knowing who the user is and which tenant they belong to.

**Objective:** Clerk integration with JWT validation and tenant-scoped sessions.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── clerk.py          # JWT verification against Clerk JWKS
│   │   ├── middleware.py     # Extract tenant_id from JWT, set schema
│   │   └── dependencies.py   # FastAPI Depends: get_current_user, get_tenant
│   ├── routers/
│   │   └── auth.py           # GET /api/v1/me — returns user info
│   └── .env                  # CLERK_SECRET_KEY, CLERK_JWKS_URL
├── ui/                       # (placeholder for now — just a static page)
```

**Dependencies:** Task 0.2.

**Acceptance criteria:**
- [ ] Clerk account created, application configured
- [ ] Frontend sign-in form (Clerk hosted or embedded) works
- [ ] API validates Clerk JWT on every request
- [ ] `GET /api/v1/me` returns user email, tenant_id, role
- [ ] Request without valid JWT returns 401
- [ ] Request to tenant-scoped endpoint sets correct PostgreSQL search_path

**Effort:** 2 days.

**Demonstrable:** Sign in through Clerk → API recognizes you. Tenant IDs are mapped. A request to `/api/v1/me` returns your user info.

---

### Task 0.4: Web UI Skeleton
**Why this comes now:** Give the auth system a frontend. Start building the surface pilots will see.

**Objective:** React app with routing, auth integration, and a placeholder dashboard.

**Files to create/modify:**
```
cortex/
├── ui/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx           # Router with auth guard
│   │   ├── components/
│   │   │   └── AuthGuard.tsx  # Redirects to Clerk if not signed in
│   │   └── pages/
│   │       ├── Dashboard.tsx  # Placeholder: "Welcome, {name}"
│   │       ├── Settings.tsx   # Placeholder
│   │       └── Onboarding.tsx # Placeholder
```

**Dependencies:** Task 0.3 (auth must work before UI can use it).

**Acceptance criteria:**
- [ ] UI starts on port 3000, proxies API calls to port 8000
- [ ] Unauthenticated user is redirected to Clerk sign-in
- [ ] Signed-in user sees their name on the Dashboard
- [ ] Navigation between Dashboard, Settings, Onboarding works
- [ ] Tailwind CSS configured, design tokens applied (per product spec §9)
- [ ] Docker Compose updated: UI service added alongside API

**Effort:** 2 days.

**Demonstrable:** Full sign-in flow in browser. Dashboard shows "Welcome, {name}." Three placeholder pages render. The frame of the application exists.

---

## PHASE 1: FIRST DATA (Week 3)

> *Goal: Connect to one tool, pull real data, show it on screen.*

---

### Task 1.1: Razorpay Connector — Auth & Basic Pull
**Why Razorpay first:** It's the simplest integration (API keys, no OAuth complexity). Revenue data is the single most important signal for every decision type.

**Objective:** Connect a practice's Razorpay account and pull payment data.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseConnector abstract class
│   │   └── razorpay/
│   │       ├── __init__.py
│   │       ├── connector.py     # RazorpayConnector(BaseConnector)
│   │       ├── auth.py          # API key validation + Fernet encryption
│   │       └── models.py        # SQLAlchemy models for stored credentials
│   ├── routers/
│   │   └── integrations.py      # POST /integrations/connect, GET /integrations
│   └── db/
│       └── credentials.py       # Encrypted credential store
```

**Dependencies:** Task 0.4.

**Acceptance criteria:**
- [ ] `POST /api/v1/integrations/connect` with `{tool: "razorpay", key_id: "...", key_secret: "..."}`
- [ ] API keys validated against Razorpay (GET /payments?count=1)
- [ ] Validated keys encrypted with Fernet, stored in credentials table
- [ ] Invalid keys return clear error: `{"error": "Invalid Razorpay credentials. Check your key_id and key_secret."}`
- [ ] `GET /api/v1/integrations` returns `[{tool: "razorpay", status: "connected", connected_at: "..."}]`

**Effort:** 2 days.

**Demonstrable:** API endpoint accepts Razorpay keys, validates them live, stores them encrypted, confirms connection. No data pulled yet — just the connection is established.

---

### Task 1.2: Razorpay Data Sync
**Why this comes next:** Connection is validated. Now pull actual payment data and store it.

**Objective:** Pull payment history from Razorpay and store normalized payment records.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── integrations/
│   │   └── razorpay/
│   │       ├── sync.py          # sync_payments(tenant_id) — batch pull
│   │       └── normalize.py     # map_razorpay_payment() → NormalizedPayment
│   ├── models/
│   │   └── payments.py          # Payment SQLAlchemy model
│   └── db/
│       └── migrations/
│           └── versions/
│               └── 002_create_payments.py
```

**Dependencies:** Task 1.1.

**Acceptance criteria:**
- [ ] `sync_payments()` pulls payments from Razorpay (paginated, handles >100 records)
- [ ] Amounts correctly converted from paise to rupees (TEST THIS: ₹100 = 10000 paise)
- [ ] Payments stored with source provenance: `source_tool = "razorpay"`, `external_id = "razorpay_pay_xxx"`
- [ ] Duplicate sync doesn't create duplicate records (idempotency on external_id)
- [ ] Sync cursor stored: only pulls payments since last sync
- [ ] If Razorpay API is down, logs error, returns partial sync status
- [ ] Sync results logged: "Synced 247 payments. 0 duplicates. 0 errors."

**Effort:** 2 days.

**Demonstrable:** Run sync → 247 payment records in the database. Run it again → 0 new (already synced). A real Razorpay payment made 10 minutes ago → appears in the next sync.

---

### Task 1.3: First Dashboard Data
**Why this comes now:** Data in the database is invisible. Show it on the dashboard. This is the first "Cortex is alive" moment.

**Objective:** Compute and display revenue metrics on the dashboard.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── insights.py           # GET /api/v1/insights/metrics
│   └── services/
│       └── metrics.py            # compute_revenue_metrics(tenant_id)
├── ui/
│   └── src/
│       └── pages/
│           └── Dashboard.tsx     # Replace placeholder with real data
```

**Dependencies:** Task 1.2.

**Acceptance criteria:**
- [ ] `GET /api/v1/insights/metrics` returns:
  ```json
  {
    "revenue": {
      "mtd": 847000,
      "mtd_change_pct": 14.2,
      "last_7_days": [/* daily revenue for last 7 days */],
      "by_location": {}
    }
  }
  ```
- [ ] Dashboard shows: "Revenue (MTD): ₹8,47,000 (+14.2%)"
- [ ] Dashboard shows a simple 7-day revenue sparkline
- [ ] If no Razorpay connected, dashboard shows: "Connect Razorpay to see revenue data" with a CTA button
- [ ] If Razorpay connected but no data synced, dashboard shows: "Syncing your payment data. Check back in a few minutes."

**Effort:** 1.5 days.

**Demonstrable:** Dashboard with real revenue data from the practice's actual Razorpay account. A number that changes when new payments come in.

---

### Task 1.4: Razorpay Webhook Receiver
**Why this comes now:** Batch sync means data is stale by up to 2 hours. Webhooks give near-real-time updates for critical events.

**Objective:** Receive and process Razorpay webhooks for payment events.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── webhooks.py           # POST /webhooks/razorpay
│   └── integrations/
│       └── razorpay/
│           └── webhooks.py       # verify_signature(), process_event()
```

**Dependencies:** Task 1.2.

**Acceptance criteria:**
- [ ] Webhook endpoint accepts POST, verifies Razorpay signature (HMAC-SHA256)
- [ ] `payment.captured` event → insert/update payment record within 30 seconds
- [ ] `refund.created` event → insert refund record
- [ ] Duplicate webhooks silently ignored (idempotency key on event_id, 24h TTL in Redis)
- [ ] Invalid signatures return 401
- [ ] Webhook processing logged: "webhook received: payment.captured (pay_xxx). Processed in 1.2s."

**Effort:** 1.5 days.

**Demonstrable:** Make a payment through Razorpay → API receives webhook → payment appears in database within 30 seconds (no batch sync needed).

---

## PHASE 2: SECOND INTEGRATION (Week 4)

> *Goal: Connect the PMS. Now we have appointments + payments = the core loop.*

---

### Task 2.1: PMS Connector — Auth & Discovery
**Why this comes now:** Payments alone show revenue. PMS adds appointments, providers, patients — the operational data that makes decisions possible.

**Objective:** Connect a practice's PMS (Practo as primary target) and pull basic data.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── integrations/
│   │   └── practo/
│   │       ├── __init__.py
│   │       ├── connector.py     # PractoConnector(BaseConnector)
│   │       └── auth.py          # OAuth 2.0 flow for Practo
```

**Dependencies:** Task 1.1 (base connector pattern established).

**Acceptance criteria:**
- [ ] OAuth flow: user clicks "Connect Practo" → redirected to Practo authorization → redirected back with code → tokens exchanged and stored
- [ ] `GET /api/v1/integrations` now shows both Razorpay and PMS
- [ ] `POST /integrations/practo/discover` returns: `{appointments: 1847, patients: 623, providers: 8, services: 24}`
- [ ] If OAuth fails (user denies): show clear error, don't leave broken state
- [ ] If Practo API is unreachable: graceful degradation, "Practo is temporarily unavailable"

**Effort:** 2 days.

**Demonstrable:** Full OAuth dance completed. API reports 1,847 appointments, 623 patients available to sync.

---

### Task 2.2: PMS Data Sync + Normalization
**Why this comes next:** Connection established. Pull the data that enables every decision.

**Objective:** Pull and normalize appointment, patient, provider, and service data from PMS.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── integrations/
│   │   └── practo/
│   │       ├── sync.py          # sync_appointments(), sync_patients(), etc.
│   │       └── normalize.py     # map_practo_appointment(), etc.
│   ├── models/
│   │   ├── bookings.py          # Unified booking/appointment model
│   │   ├── patients.py          # Unified patient model
│   │   ├── providers.py         # Unified provider model
│   │   └── services.py          # Unified service model
│   └── db/
│       └── migrations/
│           └── versions/
│               └── 003_create_pms_tables.py
```

**Dependencies:** Task 2.1.

**Acceptance criteria:**
- [ ] Appointments synced with status mapping: scheduled/completed/no_show/cancelled
- [ ] Patients synced with email and phone
- [ ] Providers synced with location assignments
- [ ] Services synced with prices and durations
- [ ] Sync handles 1,000+ records without timeout (batch processing)
- [ ] No-show appointments correctly identified (status = "no_show")
- [ ] Historical data: pull up to 12 months of past appointments
- [ ] Sync cursor saves position; next sync only pulls new/updated records

**Effort:** 2.5 days.

**Demonstrable:** Database now has appointments, patients, providers, and services alongside payments. Two independent data sources coexisting in one database.

---

### Task 2.3: Entity Resolution — Exact Email Match
**Why this comes now:** PMS has patients. Razorpay has customers. They're the same people. Without linking them, decisions can't connect revenue to appointments.

**Objective:** Match patients across PMS and Razorpay using exact email match.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── services/
│   │   └── entity_resolution.py  # resolve_entities(tenant_id)
│   ├── models/
│   │   └── entity_resolution.py  # EntityResolution SQLAlchemy model
│   └── db/
│       └── migrations/
│           └── versions/
│               └── 004_create_entity_resolution.py
```

**Dependencies:** Task 2.2 (PMS data must exist to match against).

**Acceptance criteria:**
- [ ] Patients matched across PMS and Razorpay where `primary_email` matches exactly (case-insensitive)
- [ ] Matched entities get a shared `canonical_id`
- [ ] Unmatched entities get their own `canonical_id`
- [ ] Resolution confidence stored: `exact_email` = 0.95, `no_match` = 0.0
- [ ] Resolution results logged: "Matched 412/623 patients (66%). 211 unmatched."
- [ ] Re-running resolution is idempotent (same matches, same canonical_ids)
- [ ] Phone-only patients (no email in PMS) are NOT matched in v1 — they get their own canonical_id
- [ ] UI on settings page shows: "412 patients matched, 211 unmatched" with a link to "review unmatched" (stub for Task 6.4)

**Effort:** 2 days.

**Demonstrable:** 412 patients now linked across PMS and Razorpay. A patient's appointments and payments are connected to the same person. The foundation for every decision.

---

## PHASE 3: FIRST DECISION (Week 5-6)

> *Goal: One decision type working end-to-end. This is the moment Cortex becomes real.*

---

### Task 3.1: Time-Series Metrics Derivation
**Why this comes now:** Decisions need trend data. Raw tables need to become computed metrics.

**Objective:** Derive time-series metrics from normalized data: daily revenue, daily appointments, no-show rates, utilization.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── services/
│   │   └── metrics_derivation.py  # derive_daily_metrics(tenant_id)
│   ├── models/
│   │   └── metric_values.py       # MetricValue SQLAlchemy model
│   └── db/
│       └── migrations/
│           └── versions/
│               └── 005_create_metric_values.py
```

**Dependencies:** Task 2.2 (PMS data), Task 1.2 (payment data), Task 2.3 (entity resolution).

**Acceptance criteria:**
- [ ] Daily metrics computed and stored for each location:
  - `revenue`: sum of completed payments for that day
  - `appointments_scheduled`: count of scheduled appointments
  - `appointments_completed`: count of completed appointments
  - `no_show_rate`: no_show_count / scheduled_count
  - `utilization`: completed_appointment_minutes / available_provider_minutes
  - `avg_revenue_per_appointment`: revenue / completed_appointments
- [ ] Metrics computed for last 12 months (backfill) + incrementally for new data
- [ ] Metrics stored by location + date
- [ ] `GET /api/v1/insights/metrics/timeseries?metric=revenue&days=30` returns 30 data points

**Effort:** 2 days.

**Demonstrable:** API returns time-series data for any metric. A 30-day revenue chart is possible. The data layer for decisions is complete.

---

### Task 3.2: Revenue Trend Analysis Decision
**Why this comes first of all decisions:** Revenue is the simplest decision — it only needs payment data (no entity resolution dependency). It's the highest-confidence decision for a cold-start practice. If the pilot sees "Your revenue dropped 12% this week" and it's correct, trust is built.

**Objective:** Detect revenue anomalies and generate a decision card with explanation.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── services/
│   │   └── decisions/
│   │       ├── __init__.py
│   │       ├── base.py            # BaseDecisionGenerator abstract class
│   │       └── revenue_trend.py   # RevenueTrendDecision
│   ├── models/
│   │   └── decisions.py           # Decision SQLAlchemy model
│   ├── workers/
│   │   └── celery_app.py          # Celery config
│   │   └── tasks.py               # generate_decisions task
│   └── celery_worker.py           # Worker entry point
```

**Dependencies:** Task 3.1 (metrics), Task 1.2 (payments).

**Acceptance criteria:**
- [ ] Weekly: compare trailing 7-day revenue to 28-day moving average
- [ ] Anomaly detected when: `|current - avg| > 1.5 × std_dev`
- [ ] When anomaly detected, decision card generated with:
  - Title: "Revenue this week is ₹X — Y% below your 4-week average"
  - Evidence: 30-day revenue chart with anomaly highlighted
  - Root cause analysis (heuristic, see below)
  - Recommendation: "No action needed — this appears to be a normal fluctuation" (if within 2σ) or "Investigate: check if any location had unusual closures or if a major patient cancelled"
  - ROI: "If this is a trend (not a blip), projected monthly revenue loss = ₹X"
  - Confidence: based on standard deviation distance
- [ ] Root cause heuristic checks:
  - Is the drop concentrated in one location? → "Location X accounts for 80% of the decline"
  - Is the drop concentrated on specific days? → "Tuesday and Wednesday were 40% below average"
  - Is it a payment delay? (check Razorpay settlements) → "Payment settlement delayed — actual appointments unchanged"
- [ ] Decision stored in decisions table with status "active"
- [ ] If no anomaly detected, no decision generated (don't surface noise)
- [ ] Decision generation runs on schedule: daily at 6:00 AM IST via Celery Beat

**Effort:** 3 days.

**Demonstrable:** Run the Celery task. A decision card appears in the database. The API returns it. It correctly identifies which location drove the decline. This is the first time Cortex "thinks."

---

### Task 3.3: Decision Card API + Dashboard Integration
**Why this comes now:** Decision exists in the database. Surface it to the user.

**Objective:** API endpoint for decisions and a decision card on the dashboard.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── decisions.py           # GET /decisions, GET /decisions/:id, POST /decisions/:id/feedback
├── ui/
│   └── src/
│       ├── components/
│       │   └── DecisionCard.tsx   # Card component per product spec §3.2
│       └── pages/
│           └── Dashboard.tsx      # Show decision cards below metrics
```

**Dependencies:** Task 3.2.

**Acceptance criteria:**
- [ ] `GET /api/v1/decisions` returns list of active decision cards, sorted by estimated_roi × confidence
- [ ] Decision card in UI shows:
  - Title with ROI badge (green > ₹50K, yellow ₹10-50K, grey <₹10K)
  - Confidence score with bar
  - Evidence summary (1-2 lines)
  - Expand → full analysis with all 5 questions answered
- [ ] Decision card matches product spec §3.2 design
- [ ] If no decisions exist yet, dashboard shows: "Cortex is analyzing your practice data. First insights typically appear within 24-48 hours."

**Effort:** 1.5 days.

**Demonstrable:** Dashboard now has a real decision card generated from real data. The card expands to show the full analysis. This is the product.

---

### Task 3.4: Feedback Loop
**Why this comes now:** Decision cards without feedback are one-way. Feedback teaches Cortex what the owner values.

**Objective:** Four feedback buttons on every decision card, with stored feedback that affects future behavior.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── decisions.py           # Add POST /decisions/:id/feedback
│   ├── models/
│   │   └── decision_feedback.py   # DecisionFeedback model
│   └── db/
│       └── migrations/
│           └── versions/
│               └── 006_create_decision_feedback.py
├── ui/
│   └── src/
│       └── components/
│           └── DecisionCard.tsx   # Add feedback buttons
```

**Dependencies:** Task 3.3.

**Acceptance criteria:**
- [ ] Four buttons on every decision card: ✓ Useful | ✗ Not Useful | Already Knew | Implemented
- [ ] Clicking "Implemented" → decision marked as implemented, moves to "Implemented" tab on dashboard, user prompted to enter actual outcome: "How much did this save/earn you? (optional)"
- [ ] Clicking "Not Useful" → decision hidden from dashboard, feedback reason stored: "Tell us why (optional): Not relevant / Too obvious / Wrong / Other"
- [ ] Clicking "Already Knew" → decision hidden, stored reason
- [ ] Clicking "Useful" → positive signal stored
- [ ] Feedback rate tracked per practice per week
- [ ] Decision types with high "Not Useful" rate are deprioritized

**Effort:** 2 days.

**Demonstrable:** Click "Implemented" on a decision → it moves to implemented tab. Owner can optionally enter "saved ₹12,000." Feedback is stored and visible in pilot usage tracking.

---

## PHASE 4: MORE DECISIONS (Week 7)

> *Goal: Three more decision types. Now we have a real product.*

---

### Task 4.1: Scheduling Gap Detection
**Why this comes next:** No-show prediction needs more historical data. Scheduling gaps are detectable immediately — compare this week's schedule to last week's. Faster time-to-first-value.

**Objective:** Detect abnormally empty time slots and recommend filling them.

**Files to create/modify:**
```
cortex/
├── api/
│   └── services/
│       └── decisions/
│           └── scheduling_gap.py  # SchedulingGapDecision
```

**Dependencies:** Task 3.1 (metrics), Task 2.2 (PMS data), Task 3.3 (decision card UI — reuse existing).

**Acceptance criteria:**
- [ ] Daily: compare each time slot (day × hour) for next 7 days against 4-week historical average for that slot
- [ ] Gap detected when: `upcoming_bookings < 0.5 × historical_average AND upcoming_bookings < 3`
- [ ] Decision card:
  - Title: "3 gaps detected next week — ₹12,600 in potential revenue at risk"
  - Evidence: calendar view with gaps highlighted
  - Which slots, which providers, which locations
  - Recommendation: "Send promotional offer for these slots" or "Reschedule non-urgent appointments into these gaps"
  - ROI: gap_hours × avg_revenue_per_hour × fill_probability (default 0.6)
- [ ] Ranked by revenue_at_risk (high-value slots first)
- [ ] Only surfaces if at least one gap detected

**Effort:** 2 days.

**Demonstrable:** A practice with a half-empty Tuesday afternoon next week gets a decision card flagging it. The card shows exactly which slots are empty and what they're worth.

---

### Task 4.2: No-Show Prediction
**Why this comes now:** This is the highest-ROI decision type. But it needs at least 8 weeks of historical appointment data to produce meaningful predictions. By week 7, if pilots were recruited in week 1-2 and have connected their PMS, we should have enough data.

**Objective:** Predict which upcoming appointments are likely to no-show.

**Files to create/modify:**
```
cortex/
├── api/
│   └── services/
│       └── decisions/
│           └── no_show.py         # NoShowPredictionDecision
```

**Dependencies:** Task 3.1 (metrics), Task 2.2 (PMS data), Task 2.3 (entity resolution — for patient history).

**Acceptance criteria:**
- [ ] Daily: for each appointment in next 7 days, compute no-show probability
- [ ] **Cold start rule (less than 50 historical no-shows):** Simple historical average
  - `P(no_show) = practice_no_show_rate` (default 12% if no data)
  - Decision card includes: "⚠️ Limited data — confidence will improve as Cortex learns your patterns."
- [ ] **Standard model (50+ historical no-shows):** Logistic regression with features:
  - Day of week, appointment time (morning/afternoon/evening)
  - Lead time (days between booking and appointment)
  - Patient no-show history (how many of their last 5 appointments were no-shows?)
  - Service type
  - Provider
  - Location
- [ ] Output: ranked list of at-risk appointments with probability × slot_revenue
- [ ] Decision card:
  - Title: "8 appointments at high risk of no-show — ₹18,400 at stake"
  - List of at-risk appointments, patient name, probability, slot value
  - Recommendation: "Send reminder SMS to these patients" or "Call top 3 highest-risk patients"
  - ROI: sum of (probability × revenue_per_slot) for top-N predictions
- [ ] **Model does not use LLM.** Pure scikit-learn. LLM is used only to format the natural-language explanation after the prediction is made.

**Effort:** 2.5 days.

**Demonstrable:** Dashboard shows a no-show prediction card. 8 appointments listed with probabilities. The top one: "Mrs. Gupta, Tuesday 10 AM, Dr. Sharma, 62% no-show risk. Based on: 2 of her last 3 appointments were no-shows, and she booked 45 days in advance."

---

### Task 4.3: Pricing Optimization
**Why this comes last of the four:** It's a monthly check, not daily. It produces recommendations less frequently. Good to have before pilots but lower urgency than gap detection and no-show prediction.

**Objective:** Flag underpriced services based on utilization rates.

**Files to create/modify:**
```
cortex/
├── api/
│   └── services/
│       └── decisions/
│           └── pricing.py         # PricingOptimizationDecision
```

**Dependencies:** Task 3.1 (metrics), Task 2.2 (PMS service data + Razorpay payment data), Task 5.3 (Zoho Books for cost data — can run without it, just uses lower confidence).

**Acceptance criteria:**
- [ ] Monthly (1st of month): for each service, calculate utilization rate
  - `utilization = appointments_completed / (appointments_scheduled - cancellations)`
- [ ] Service flagged when: `utilization < 60% AND margin > 40%`
  - Margin estimated from: (avg_price - estimated_cost) / avg_price
  - If Zoho Books not connected, estimated_cost = 30% of price (default assumption)
- [ ] Recommendation: "Raise/lower price by X%"
  - `Δprice = (target_utilization - current_utilization) / elasticity × current_price`
  - Default elasticity: 0.4 (healthcare is price-inelastic)
  - Target utilization: 75%
- [ ] Decision card:
  - Title: "Scaling & Polishing at ₹800 has 52% utilization — consider adjusting"
  - Current price, utilization, margin
  - Suggested price: ₹920 (+15%)
  - Projected impact: utilization may drop to 46% but revenue per slot increases, net revenue +₹8,400/month
  - ⚠️ "ESTIMATED — simplified pricing model. Actual patient response may vary."
- [ ] If cost data unavailable: "⚠️ Margin estimated at 70% (default). Connect Zoho Books for cost-based pricing."

**Effort:** 2 days.

**Demonstrable:** Monthly check runs. A service with 52% utilization and high margin gets flagged. The card suggests a specific price change with projected impact.

---

## PHASE 5: ONBOARDING & PILOT-READY (Week 8-9)

> *Goal: Someone who isn't the founder can sign up, connect tools, and see decisions.*

---

### Task 5.1: Onboarding Flow
**Why this comes now:** Without onboarding, every pilot setup requires the founder to run SQL queries. Onboarding makes the product self-service enough for a pilot.

**Objective:** Guided setup wizard: signup → practice profile → connect tools → calibration survey → first insights.

**Files to create/modify:**
```
cortex/
├── ui/
│   └── src/
│       ├── pages/
│       │   └── Onboarding.tsx    # Multi-step wizard
│       └── components/
│           └── onboarding/
│               ├── StepSignup.tsx
│               ├── StepProfile.tsx
│               ├── StepConnectTools.tsx
│               ├── StepCalibration.tsx
│               └── StepSyncing.tsx
├── api/
│   ├── routers/
│   │   └── onboarding.py         # POST /onboarding/profile, GET /onboarding/status
│   └── models/
│       └── practice_profile.py
```

**Dependencies:** Task 1.1 (Razorpay connector), Task 2.1 (PMS connector), Task 0.3 (auth).

**Acceptance criteria:**
- [ ] Step 1: Practice profile — name, type (dental/PT/diagnostic/eye-care), city, revenue range, number of locations
- [ ] Step 2: Connect tools — "Connect Razorpay" → API key input → validate → success. "Connect PMS" → OAuth flow → success.
  - Error states per product spec §3.1.2: connection failed → specific error message + retry button
- [ ] Step 3: Calibration survey — "Top 3 goals this quarter" (dropdown), "What keeps you up at night?" (free text), "Target profit margin?" (optional)
- [ ] Step 4: Initial sync — progress bar. "Pulling 1,847 appointments from Practo... 67% complete. Estimated time remaining: 8 minutes."
  - If sync takes >15 minutes, show: "Still syncing. We'll email you when it's done. You can close this page."
- [ ] Step 5: First insights — redirect to dashboard with "Cortex is analyzing your data. First insights in 15-30 minutes."
- [ ] Onboarding progress persists across page reloads
- [ ] User can leave and return mid-onboarding (resume where they left off)

**Effort:** 3 days.

**Demonstrable:** Complete onboarding flow from signup to dashboard. Tools connected. Data syncing. First decision appears within 30 minutes.

---

### Task 5.2: Integration Management UI
**Why this comes now:** Pilots will need to reconnect tools, check sync status, and see data freshness.

**Objective:** Settings page showing integration health and reconnection.

**Files to create/modify:**
```
cortex/
├── ui/
│   └── src/
│       └── pages/
│           └── Settings.tsx      # Replace placeholder with integration management
```

**Dependencies:** Task 1.1, 1.2, 2.1, 2.2 (integrations must exist).

**Acceptance criteria:**
- [ ] Each connected tool shows: name, status (green/yellow/red dot), last sync time, data volume
- [ ] Green: synced within 2 hours. Yellow: 2-12 hours. Red: >12 hours or error.
- [ ] Reconnect button for each tool
- [ ] Disconnect button with confirmation: "Disconnecting Practo will remove all your appointment data. This cannot be undone."
- [ ] Data freshness indicators match product spec §3.2.5

**Effort:** 1.5 days.

**Demonstrable:** Settings page shows all integrations, their health, and last sync time. Disconnect/reconnect works.

---

### Task 5.3: Zoho Books Integration (or Tally CSV Bridge)
**Why this comes now:** The least critical of the three integrations. Accounting data improves pricing optimization and enables expense analysis. But it's not needed for the first three decision types. Defer if timeline is tight.

**Objective:** Connect accounting data — Zoho Books via OAuth, or Tally via CSV upload.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── integrations/
│   │   ├── zoho_books/
│   │   │   ├── connector.py
│   │   │   ├── auth.py
│   │   │   ├── sync.py
│   │   │   └── normalize.py
│   │   └── tally/
│   │       └── csv_import.py    # CSV upload + validation + normalization
│   ├── models/
│   │   └── invoices.py
│   └── db/
│       └── migrations/
│           └── versions/
│               └── 007_create_invoices.py
```

**Dependencies:** Task 1.1 (base connector pattern).

**Acceptance criteria:**
- [ ] Zoho Books OAuth flow works
- [ ] Invoices and contacts synced and normalized
- [ ] **Tally CSV bridge:** Upload Tally export CSV → validate columns → normalize → store
  - Required columns: Date, Voucher Type, Voucher No, Ledger, Amount
  - Validation: check required columns exist, dates parse correctly, amounts are numeric
  - Error: "Column 'Ledger' not found. Your Tally export must include: Date, Voucher Type, Voucher No, Ledger, Amount."
- [ ] Invoices linked to patients via entity resolution
- [ ] If neither Zoho Books nor Tally CSV connected, pricing optimization shows "cost data unavailable — using default estimates"

**Effort:** 2 days.

**Demonstrable:** Zoho Books connected → 342 invoices synced. OR: Upload Tally CSV → 156 vouchers imported. Expense data now available for pricing optimization.

---

### Task 5.4: Location Management
**Why this comes now:** Pilots are multi-location. Without location awareness, decisions are useless — "revenue is down" without saying where is noise.

**Objective:** Settings to add/edit practice locations with operating hours.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── settings.py            # CRUD for locations
│   └── models/
│       └── locations.py           # (already created in Task 0.2 DDL)
├── ui/
│   └── src/
│       └── pages/
│           └── Settings.tsx       # Add location management tab
```

**Dependencies:** Task 2.2 (PMS data includes location info).

**Acceptance criteria:**
- [ ] Add location: name, address, city, operating hours (day × open/close time)
- [ ] Edit location: change hours, mark inactive
- [ ] Location filter on dashboard: dropdown to view metrics for "All Locations", "Gurgaon", "South Delhi"
- [ ] Location-specific metrics compute correctly when filtered
- [ ] Operating hours used in utilization calculation (provider X is available 9 AM-6 PM = 9 available hours)

**Effort:** 1 day.

**Demonstrable:** Dashboard with location filter. Select "Gurgaon" → metrics and decisions update to show only Gurgaon data.

---

## PHASE 6: PILOT SUPPORT & POLISH (Week 10-11)

> *Goal: Everything needed to monitor pilots and keep them engaged.*

---

### Task 6.1: Morning Digest Email
**Why this comes now:** Email creates a daily habit. The owner doesn't need to remember to check Cortex — Cortex comes to them.

**Objective:** Daily email at 6:00 AM IST with top decisions and metric snapshot.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── workers/
│   │   └── tasks.py               # Add send_morning_digest task
│   └── services/
│       └── email_digest.py        # Compose digest content
```

**Dependencies:** Task 3.2-4.3 (decisions must exist to email about them).

**Acceptance criteria:**
- [ ] Email sent at 6:00 AM IST, Mon-Sat (not Sunday)
- [ ] Subject: "Cortex Morning Digest — [Date] | Top decisions for [Practice Name]"
- [ ] Body: top 3 decision cards (condensed), 4 KPI tiles (revenue, utilization, no-show rate, appointments), simulation quick-start link
- [ ] Email renders correctly on mobile (most owners check email on phone)
- [ ] Unsubscribe link in footer
- [ ] If no new decisions since yesterday, email says: "No new decisions today. Here's your practice at a glance."
- [ ] Uses a simple email sending service (Resend, SendGrid, or AWS SES). Do not build an email server.
- [ ] Email enabled/disabled per user setting

**Effort:** 2 days.

**Demonstrable:** 6:00 AM email arrives. "Good morning. 2 new decisions today. Top: ₹18,400 at risk from 8 high-risk appointments."

---

### Task 6.2: Pilot Usage Tracking
**Why this comes now:** The founder needs to know if pilots are actually using the product. This is the internal dashboard for the 6-month validation goal.

**Objective:** Track and display pilot engagement metrics for the founder.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── admin.py               # GET /admin/pilots (founder-only)
│   └── services/
│       └── pilot_tracking.py      # Aggregate usage metrics
├── ui/
│   └── src/
│       └── pages/
│           └── Admin.tsx          # Pilot health dashboard
```

**Dependencies:** Task 3.4 (feedback loop), Task 0.3 (auth — admin page is founder-only).

**Acceptance criteria:**
- [ ] Admin dashboard (founder-only, hidden from pilot users) shows per-practice:
  - Last active date (when they last logged in)
  - Days active this week / this month
  - Total decisions viewed
  - Feedback rate (% of decisions given feedback)
  - Decisions implemented
  - ROI claimed (cumulative)
  - Integration health status
- [ ] Warning indicators: inactive 3+ days → yellow. Inactive 7+ days → red. Low feedback → yellow.
- [ ] Founder can see which features each pilot uses most
- [ ] Data is aggregated, not real-time (runs on Celery Beat, every 6 hours)

**Effort:** 2 days.

**Demonstrable:** Founder dashboard shows Pilot #1: last active 2 hours ago, 14 decisions viewed this week, 3 implemented, ₹34,000 claimed ROI. Pilot #2: inactive 4 days ⚠️.

---

### Task 6.3: What-If Simulation
**Why this comes now:** Simulation turns recommendations into action. "What if I raise prices 10%?" is the question every owner asks after seeing a pricing decision. This closes the loop.

**Objective:** Simple single-variable simulation with preset scenarios.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── simulations.py          # POST /simulations, GET /simulations/:id
│   ├── services/
│   │   └── simulation.py           # run_simulation(variable, change, scope)
│   └── models/
│       └── simulations.py
├── ui/
│   └── src/
│       ├── components/
│       │   └── SimulationCard.tsx
│       └── pages/
│           └── Simulate.tsx
```

**Dependencies:** Task 3.1 (metrics — simulation needs current values).

**Acceptance criteria:**
- [ ] Preset scenarios: "Reduce no-shows", "Raise prices", "Add Saturday hours", "Add a provider", "Custom"
- [ ] User selects variable → inputs change amount → selects scope (all locations or specific) → clicks Run
- [ ] Result shows within 10 seconds:
  - Projected impact (revenue delta, utilization change, etc.)
  - Confidence band (upper/lower range)
  - Formula breakdown (per product spec §3.3.3)
  - Limitations called out: "Assumes all no-show slots are rebooked. Actual fill: 50-80%."
- [ ] Results can be saved and viewed later
- [ ] Simulation labeled: "ESTIMATED — simplified model. Not causal inference."

**Effort:** 2.5 days.

**Demonstrable:** Run "Reduce no-shows by 20%" → "Projected additional revenue: ₹26,400–39,600/month. Based on 520 monthly appointments at ₹2,200 avg. 80% confidence."

---

### Task 6.4: Manual Entity Merge UI
**Why this comes now:** During pilot phase, the founder or office manager will notice patients who should be linked but weren't (phone-only patients, name variants). This gives them a way to fix it.

**Objective:** Settings page to review and merge unmatched patient records.

**Files to create/modify:**
```
cortex/
├── api/
│   ├── routers/
│   │   └── settings.py            # Add merge endpoints
│   └── services/
│       └── entity_resolution.py   # Add get_unmatched(), merge_entities()
├── ui/
│   └── src/
│       └── pages/
│           └── Settings.tsx       # Add "Patients" tab with merge UI
```

**Dependencies:** Task 2.3 (entity resolution must exist with unmatched records).

**Acceptance criteria:**
- [ ] Settings > Patients shows: "412 matched, 211 unmatched"
- [ ] Unmatched list shows patients from each source tool with name, email, phone
- [ ] Suggested matches displayed: same name but different email → "Link these?"
- [ ] Manual merge: select two patients → click "Merge" → new canonical_id created → all appointments and payments now linked
- [ ] Merge is reversible for 24 hours (undo button)
- [ ] Merge history logged

**Effort:** 1.5 days.

**Demonstrable:** Two patient records — "Priya Sharma (PMS)" and "Priya Sharma (Razorpay)" with different emails → merged manually → all her appointments and payments now linked.

---

## PHASE 7: HARDENING (Week 12)

> *Goal: Production-ready. Error handling everywhere. No silent failures.*

---

### Task 7.1: Error Handling & Monitoring
**Why this comes now:** Before pilots rely on Cortex daily, every failure mode must be handled gracefully. Silent failures destroy trust.

**Objective:** Comprehensive error handling across all integrations, API endpoints, and background tasks.

**Files to modify:** All routers, all connectors, all Celery tasks. No new files — hardening pass across existing code.

**Dependencies:** All prior tasks.

**Acceptance criteria:**
- [ ] Every integration failure produces a specific, user-visible error (not "something went wrong")
- [ ] Sentry configured for error tracking
- [ ] Celery task failures logged with full context, retried with exponential backoff (max 3 retries)
- [ ] API returns consistent error format: `{"error": {"code": "INTEGRATION_FAILED", "message": "...", "details": {...}}}`
- [ ] Rate limit handling: when Razorpay returns 429, wait and retry with backoff
- [ ] Database connection pool exhaustion → clear error, not hang
- [ ] Redis unavailable → degraded gracefully (no webhooks processed, batch sync still works)
- [ ] Health check endpoint includes: database reachable, Redis reachable, integration status summary
- [ ] Cron-style monitoring: if no decision generated in 48 hours for a practice, log warning

**Effort:** 3 days.

**Demonstrable:** Simulate Razorpay API being down → user sees "Razorpay is temporarily unavailable. Last sync: 2 hours ago. We'll retry automatically." No 500 errors. No silent failures.

---

### Task 7.2: Performance & Load Testing
**Why this comes now:** 3 pilots won't stress the system, but the first pilot onboarding with 1,847 appointments + 4,000 payments needs to feel fast.

**Objective:** Ensure dashboard loads in <500ms and sync handles realistic data volumes.

**Dependencies:** All prior tasks. Data must exist to test against.

**Acceptance criteria:**
- [ ] Dashboard API response <500ms with 12 months of data
- [ ] Decision card detail <1s
- [ ] Razorpay sync of 5,000 payments completes in <5 minutes
- [ ] PMS sync of 2,000 appointments completes in <3 minutes
- [ ] Entity resolution of 1,000 patients completes in <30 seconds
- [ ] Simulation result returned in <10 seconds
- [ ] PostgreSQL query plans reviewed (no sequential scans on large tables)
- [ ] Database indexes added where needed (payments.date, bookings.start_time, metric_values.metric+date)

**Effort:** 2 days.

**Demonstrable:** Dashboard loads instantly. Sync runs silently in background. No user-facing slowness.

---

### Task 7.3: Pre-Pilot QA Checklist
**Why this comes now:** Final validation before a real practice owner sees the product.

**Objective:** Run through every user flow. Fix everything that's broken. Do not show a pilot something that doesn't work.

**Dependencies:** All prior tasks.

**Acceptance criteria:**
- [ ] Fresh onboarding: create new account, connect Razorpay (test keys), connect PMS (if test account available), complete calibration survey → dashboard shows within 30 minutes
- [ ] All 4 decision types generate at least once during a 48-hour test period with synthetic data
- [ ] Morning digest email arrives at correct time with correct content
- [ ] Simulation runs for all presets without error
- [ ] Integration disconnect/reconnect cycle works
- [ ] Location filter works correctly
- [ ] Feedback buttons work, feedback stored, decision hidden/shown appropriately
- [ ] Mobile browser: dashboard is readable, cards are tappable, no horizontal scroll
- [ ] No console errors in browser
- [ ] No unhandled exceptions in API logs
- [ ] Every error path tested (wrong API keys, network timeout, empty data, very large data)

**Effort:** 1 day.

**Demonstrable:** A clean run-through of the entire product. No surprises. Ready for a pilot.

---

## TASK DEPENDENCY GRAPH

```
0.1 Scaffolding
 └─ 0.2 Database
     └─ 0.3 Auth
         └─ 0.4 UI Skeleton
             ├─ 1.1 Razorpay Auth ── 1.2 Razorpay Sync ── 1.3 Dashboard Data ── 1.4 Webhooks
             │                                                                    │
             ├─ 2.1 PMS Auth ── 2.2 PMS Sync ── 2.3 Entity Resolution          │
             │                                    │                              │
             │                                    ├─ 3.1 Metrics ───────────────┤
             │                                    │    │                         │
             │                                    │    ├─ 3.2 Revenue Trend ────┤
             │                                    │    │    └─ 3.3 Decision UI ─┤
             │                                    │    │        └─ 3.4 Feedback  │
             │                                    │    │                         │
             │                                    │    ├─ 4.1 Scheduling Gap     │
             │                                    │    ├─ 4.2 No-Show Prediction │
             │                                    │    └─ 4.3 Pricing Opt.       │
             │                                    │                              │
             ├─ 5.1 Onboarding ──────────────────┤                              │
             ├─ 5.2 Integration Mgmt ─────────────┤                              │
             ├─ 5.3 Zoho Books ───────────────────┤                              │
             └─ 5.4 Location Mgmt ────────────────┘                              │
                                                                                  │
             6.1 Digest ── 6.2 Pilot Tracking ── 6.3 Simulation ── 6.4 Entity UI │
                                                                                  │
             7.1 Error Handling ── 7.2 Performance ── 7.3 QA ────────────────────┘
```

---

## EFFORT SUMMARY

| Phase | Tasks | Dev-Days | Calendar Weeks |
|-------|-------|----------|----------------|
| 0: Skeleton | 0.1–0.4 | 6.5 | 1.5 |
| 1: First Data | 1.1–1.4 | 7 | 1.5 |
| 2: Second Integration | 2.1–2.3 | 6.5 | 1.5 |
| 3: First Decision | 3.1–3.4 | 8.5 | 2 |
| 4: More Decisions | 4.1–4.3 | 6.5 | 1.5 |
| 5: Onboarding | 5.1–5.4 | 7.5 | 1.5 |
| 6: Polish | 6.1–6.4 | 8 | 2 |
| 7: Hardening | 7.1–7.3 | 6 | 1.5 |
| **Total** | **28 tasks** | **~56 days** | **~12 weeks** |

This is realistic for a solo developer working 5-6 hours/day on product (with remaining time on networking per the acquisition strategy). The critical path runs through Phases 0-3 — once Task 3.3 is complete (first decision on dashboard), the product is demonstrable to pilots even if Phases 4-7 aren't finished.

**Minimum viable pilot demo:** Complete through Task 3.3 (end of Week 6). A practice owner can see their revenue data and one decision card. This is enough for the first pilot conversation.

**Pilot-ready:** Complete through Task 5.2 (end of Week 9). Pilots can self-onboard, connect tools, and see all four decision types.

**Production-ready:** Complete through Task 7.3 (end of Week 12). Fully hardened, monitored, and QA'd.

---

## WHAT TO DEFER IF TIMELINE IS TIGHT

If you're at week 8 and Phases 4-6 aren't complete, ship with:
- **2 decision types** (revenue trend + scheduling gap) — these need the least historical data
- **No Zoho Books** (pricing optimization will use default cost estimates)
- **No morning digest** (pilot checks dashboard directly)
- **No simulation** (defer to pilot feedback phase)
- **No manual entity merge** (founder runs SQL to fix matches)

You can add the remaining decision types, email, simulation, and entity merge during the pilot phase while pilots are using the product. The pilots will tell you which of these they actually want.

---

*This implementation plan is the build order. Work through it task by task. After each task, something new works in the browser. Do not skip tasks. Do not optimize prematurely. Ship the simplest thing that demonstrates progress.*
