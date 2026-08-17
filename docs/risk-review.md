# Cortex v1 — Pre-Implementation Risk Review

> **Review date:** 2026-07-19
> **Scope:** All approved baseline documents (Business Plan Rev 5, System Architecture, Product Spec, Implementation Plan)
> **Objective:** Determine whether the project is robust enough to begin implementation

---

## CRITICAL RISKS (3)

---

### R1: PMS API Availability Is Unvalidated

**Severity:** Critical

**Description:** The entire product depends on connecting to a practice management system (Practo, DocEngage, or Lybrate). The product spec and implementation plan assume these systems have REST APIs with OAuth 2.0, specific endpoints (GET /appointments, GET /patients, etc.), webhook support, and accessible developer documentation. None of these assumptions have been verified against a real API.

**Why this is a risk:** If Practo's API is restricted (requires partnership approval), deprecated, rate-limited beyond usability, or doesn't expose the fields we need, the PMS integration — which feeds 3 of 4 decision types — doesn't work. The fallbacks (DocEngage, Lybrate) have the same unvalidated assumption. The secondary fallback (CSV export from PMS) degrades the product to manual data upload, which breaks the "autonomous, always-on" value proposition.

**Likelihood:** Medium-High. Indian healthtech APIs are often gated behind partnership agreements, not openly available. Practo's developer portal may list APIs that require commercial contracts.

**Impact if ignored:** The product ships without a working PMS integration. No-shows, scheduling gaps, and pricing optimization decisions cannot be generated. The pilot sees only revenue data from Razorpay — not enough to demonstrate Cortex's value. Pilot fails. Company dies.

**Smallest possible mitigation:** Before writing Task 0.1, verify Practo's API availability:
1. Visit developer.practo.com and attempt to create a developer account
2. Check if API endpoints are publicly documented or require approval
3. Attempt to register an OAuth application
4. If Practo is gated, repeat for DocEngage and Lybrate
5. If all three are gated, the CSV fallback becomes the primary integration path — this changes the product from "autonomous sync" to "periodic CSV upload" for v1, which requires updating the product spec and pilot expectations

**Validation required:** Attempt to create a developer account on developer.practo.com. Document what access is available. If gated, contact Practo partnership team. Set a 1-week timebox — if no API access after 1 week, escalate to the fallback decision.

**Documents affected:** Product Specification §5.1 (PMS integration spec must reflect actual API availability). Implementation Plan Task 2.1-2.2 (connector implementation may need to change to CSV-based).

**Recommendation:** Validate Before Implementation

---

### R2: Docker Compose in Production With No Auto-Recovery

**Severity:** Critical

**Description:** The infrastructure plan uses Docker Compose on a single DigitalOcean VM in production. Docker Compose does not auto-restart crashed containers unless `restart: unless-stopped` is explicitly configured. The implementation plan does not include this configuration. If the API, Celery worker, or PostgreSQL container crashes at 3 AM, the system stays down until the founder wakes up and manually restarts it.

**Why this is a risk:** Pilots are healthcare practices. If an owner checks their dashboard at 9 AM and sees an error (or stale data because the Celery worker died overnight), trust is damaged. One bad morning experience during the 2-month free pilot period could cause churn. At 3 pilots, losing even one is a 33% failure rate.

**Likelihood:** Medium. Docker containers crash occasionally (memory leaks, OOM kills, unhandled exceptions). At 3 pilots with light load, crashes are infrequent but not zero over a 3-month pilot period.

**Impact if ignored:** Pilot experiences downtime. Trust erodes. Churn risk increases significantly. The founder is woken up by an angry WhatsApp message instead of proactively fixing the issue.

**Smallest possible mitigation:** Add `restart: unless-stopped` to every service in docker-compose.yml. Add a simple healthcheck to the Celery worker that the API can monitor. Add a dead-man's switch: if no decision generated in 48 hours for any practice, log a CRITICAL error (already in Task 7.1 — elevate from "log warning" to "Sentry alert"). Configure Sentry to email/SMS the founder on CRITICAL events. Total effort: 30 minutes of config changes, not a redesign.

**Validation required:** After initial deploy, manually `docker kill` the Celery worker container and verify it restarts automatically within 10 seconds by running `docker ps`.

**Documents affected:** Implementation Plan Task 7.1 (add `restart: unless-stopped` to acceptance criteria). Infrastructure document (note the auto-restart configuration).

**Recommendation:** Mitigate Before Implementation (adds 30 minutes to Task 0.1)

---

### R3: Founder Time Split Is Unsustainable for 12 Weeks

**Severity:** Critical

**Description:** The acquisition strategy requires 8-10 hours/week of networking (events, consultant outreach, chai meetings) while the implementation plan requires 25-30 hours/week of focused coding. Combined: 33-40 hours/week of productive output. With context switching between networking (social, unpredictable) and coding (deep work, requires focus), the actual time required is closer to 45-55 hours/week. As a university student with academic commitments, this is at the edge of sustainability.

**Why this is a risk:** The founder is the single point of failure for both product development and pilot acquisition. If either falls behind — product not ready when pilots are recruited, or no pilots when product is ready — the 6-month validation goal fails. Burnout in weeks 8-10 (the heaviest phase — Onboarding + Polish) could cause both tracks to stall simultaneously. There is no buffer and no backup.

**Likelihood:** High. Solo-founder burnout is the #1 cause of early-stage startup failure. Combining deep technical work with outbound networking is two full-time jobs compressed into one person's schedule. University commitments add a third demand.

**Impact if ignored:** Product ships late. Or networking doesn't happen. Or the founder burns out and stops. Any of these kills the 6-month target.

**Smallest possible mitigation:**
1. Ruthlessly prioritize: Phase 5 (Onboarding) and Phase 6 (Polish) features can slip to the pilot phase. Ship at Task 3.3 (end of Week 6 — first decision on dashboard) and begin pilot conversations immediately, even with an incomplete product. A pilot who sees one real decision from their data is more valuable than a polished product with no users.
2. Reduce networking to 1 event/week (4 hours, not 8-10) until Task 3.3 is complete. The acquisition timeline extends by 2-4 weeks, but the product actually exists when pilots are recruited.
3. Accept that the 12-week plan may take 14-16 weeks. This is still within the 6-month validation window.

**Validation required:** Track actual hours (coding, networking, university) for the first 2 weeks. If total > 50 hours/week consistently, reduce scope immediately.

**Documents affected:** Implementation Plan (add "Ship at Task 3.3" as an explicit milestone). Acquisition Strategy (reduce Phase 0 networking intensity until product is demo-ready).

**Recommendation:** Mitigate Before Implementation

---

## HIGH RISKS (7)

---

### R4: Entity Resolution "Exact Email Match" Confidence Is Overstated

**Severity:** High

**Description:** The product spec assigns 0.95 confidence to exact email matches. In reality, Indian healthcare practices have significant data quality issues: patients may share email addresses (family accounts), the same patient may use different emails across tools (personal Gmail in PMS, work email in Razorpay), or emails may be missing entirely (phone-only patients are common in India). The 66% match rate assumed in the implementation plan (412/623 patients matched) may be optimistic.

**Why this is a risk:** Overconfident entity resolution cascades errors into every decision. If two different patients are incorrectly merged (shared family email), their combined LTV, churn risk, and no-show history are wrong. The practice owner sees "Mrs. Sharma has a 62% no-show risk" when the bad data is actually from her husband's appointments. One bad recommendation from bad entity resolution destroys trust faster than no recommendation at all.

**Likelihood:** Medium. The exact scope of the problem depends on the practice's data quality, which varies widely. Urban, tech-forward practices (our target) likely have better data. But even 5-10% incorrect matches produce noticeable errors.

**Impact if ignored:** Incorrect decisions erode pilot trust. The owner checks a no-show prediction, sees it's wrong, and dismisses all future predictions. The product loses credibility.

**Smallest possible mitigation:**
1. Reduce displayed confidence from 0.95 to 0.80 for exact email match (acknowledges email-sharing risk)
2. Add a "Same email, different name?" check: if two patients share an email but have different names in different tools, flag as "low confidence — possible family account" and do NOT merge automatically
3. Surface entity resolution stats on the settings page: "412 matched (412 high confidence, 0 low confidence), 211 unmatched, 18 flagged for review"
4. During pilot onboarding, ask the practice owner or office manager to review the top 10 highest-value merged patients (those with the most appointments + payments)

**Validation required:** After first pilot's PMS data is synced, manually review 50 entity matches. Count: correct matches, incorrect merges, and missed matches. If incorrect merges > 5%, reduce confidence further and prioritize manual review UI (Task 6.4 earlier — move to Phase 3).

**Documents affected:** Product Spec §7.2 (entity resolution confidence and family account handling). Implementation Plan Task 2.3 (add family account check to acceptance criteria). Consider moving Task 6.4 (Manual Entity Merge UI) to Phase 3 instead of Phase 6.

**Recommendation:** Mitigate Before Implementation

---

### R5: No SSL/TLS or Domain Configuration in Implementation Plan

**Severity:** High

**Description:** The architecture document specifies TLS 1.3 with Let's Encrypt via Nginx. The implementation plan starts with FastAPI serving HTTP directly (Task 0.1). There is no task for setting up Nginx, SSL certificates, or domain configuration before pilot deployment. The product would be served over plain HTTP — browsers will show "Not Secure" warnings. Clerk OAuth redirects may fail without HTTPS. Razorpay webhooks require an HTTPS endpoint.

**Why this is a risk:** A pilot opening their dashboard and seeing a "Not Secure" browser warning immediately destroys credibility. "You want me to connect my payment gateway to an insecure website?" is a non-starter. The pilot conversation ends there. Additionally, Clerk's OAuth flow and Razorpay's webhook verification require HTTPS.

**Likelihood:** Certain if not addressed. The current implementation plan has no HTTPS task. It will be discovered during pilot deployment (Task 5.1) or earlier when testing Clerk/Razorpay integrations that require HTTPS.

**Impact if ignored:** Pilot onboarding fails. Clerk OAuth redirects may not work. Razorpay webhooks won't verify. Browser shows security warning. Trust destroyed before the product is even seen.

**Smallest possible mitigation:** Add a task between Task 0.4 and Task 1.1: "Nginx + SSL Setup" (1 day):
1. Add Nginx service to docker-compose.yml (port 80/443, proxy to API:8000, serve UI static files)
2. Configure Let's Encrypt via Certbot (auto-renewal)
3. Purchase domain (cortexapp.in or similar) — ₹500-1,000/year
4. Configure DNS to point to DigitalOcean VM
5. Verify HTTPS works, Clerk OAuth redirects work

**Validation required:** Ensure `curl https://cortexapp.in/health` returns 200 with valid TLS certificate before Task 1.1 begins.

**Documents affected:** Implementation Plan (insert new task between 0.4 and 1.1). Infrastructure document (note domain and SSL configuration).

**Recommendation:** Mitigate Before Implementation

---

### R6: Razorpay Test Accounts Require Business Verification

**Severity:** High

**Description:** To build and test the Razorpay connector, the founder needs a Razorpay account with test API keys. Razorpay requires business verification (GST, PAN, bank account) to issue live API keys. Test mode keys are available without verification but have limited functionality — they can simulate payments but may not support all endpoints or realistic data volumes needed for development.

**Why this is a risk:** The founder is a student without a registered business. Getting a Razorpay account with test data may require using a practice's account (which means asking a pilot for API keys before the product exists) or building against limited test-mode data that doesn't match real-world API behavior. Additionally, the Razorpay webhook registration requires a public HTTPS URL — which needs the domain and SSL setup from Risk R5.

**Likelihood:** Medium-High. Razorpay's test mode is accessible without business verification. But test mode data is artificial and may not expose edge cases (refunds, settlements, payment failures) that real data would.

**Impact if ignored:** The Razorpay connector is built and tested against artificial data. When connected to a real practice, edge cases (failed payments, partial refunds, UPI-specific payment methods) cause bugs. The paise-to-rupees conversion bug (identified in the spec as the "#1 normalization risk") might only manifest with specific real-world data.

**Smallest possible mitigation:**
1. Use Razorpay test mode keys (no verification needed) for initial development
2. Generate realistic test data: create 500+ payments with varied statuses, methods, and amounts using Razorpay's test card numbers
3. Test specifically: UPI payments, netbanking, card payments, wallet payments, EMI, refunds (partial and full), settlements
4. For the first pilot, use their Razorpay test mode keys first (validate connector works with real merchant ID), then switch to live read-only keys
5. Document the test data generation script so it can be reused

**Validation required:** Before Task 1.1, verify: (a) Razorpay test mode account can be created without business documents, (b) test mode supports all payment methods and statuses we need, (c) webhook simulation is possible in test mode.

**Documents affected:** None (implementation approach clarified, not changed).

**Recommendation:** Validate During Implementation (confirmed in first 2 hours of Task 1.1)

---

### R7: Tally CSV Export Format Varies by Version and Configuration

**Severity:** High

**Description:** The Tally CSV bridge assumes specific column names (Date, Voucher Type, Voucher No, Ledger, Amount). Tally's export format varies across Tally ERP 9, Tally Prime, and different configurations (language settings, company preferences). A Tally export from a practice in Delhi might use Hindi column headers, different date formats, or include additional columns that break the parser.

**Why this is a risk:** If the first pilot uses Tally (common among Indian SMBs), the CSV import fails on their first export. The founder either: (a) manually fixes their CSV (unscalable, breaks "autonomous" promise), (b) builds a custom parser for their specific Tally version (one-off work), or (c) tells them to switch to Zoho Books (unlikely to happen). Any of these delays the pilot and damages the onboarding experience.

**Likelihood:** Medium. Tally is the dominant accounting tool for Indian SMBs. At least 1 of 3 pilots will likely use Tally. The CSV format variation is well-documented in the Indian developer community.

**Impact if ignored:** The Tally CSV bridge fails on real data. The accounting integration (needed for pricing optimization's cost data) doesn't work for Tally users. The pilot gets a degraded experience.

**Smallest possible mitigation:**
1. Before building the CSV parser, collect 5-10 real Tally export files from Indian practice owners (ask in founder networks, LinkedIn, Tally user forums)
2. Identify common variations: column naming, date formats, number formats (Indian comma formatting: 1,00,000), language settings
3. Build the parser with configurable column mapping: the user selects which column is "Date", which is "Amount", etc. instead of hardcoding column names
4. Add a CSV preview step: user uploads CSV → Cortex shows a preview of detected columns → user confirms mapping → import proceeds
5. If the CSV is unparseable, show specific error: "Column 'Ledger' not found. Your export should include a ledger/account column. Detected columns: Date, Particulars, Vch Type, Vch No, Debit, Credit."

**Validation required:** Test CSV parser against 3+ real Tally export files from different practices before marking Task 5.3 complete.

**Documents affected:** Product Spec §5.3 (add configurable column mapping to Tally CSV bridge). Implementation Plan Task 5.3 (add "CSV preview + column mapping" to acceptance criteria).

**Recommendation:** Mitigate Before Implementation

---

### R8: OpenAI API Free-Tier Rate Limits May Block Decision Generation

**Severity:** High

**Description:** OpenAI's free tier (Tier 0) limits GPT-4o-mini to 3 requests per minute (RPM) and GPT-4o to a lower limit. The implementation plan uses GPT-4o-mini for routine decisions and GPT-4o for complex reasoning. At 10 decisions/day across 3 pilots = 30 LLM calls/day, this is within rate limits. But decision generation (4 types × formatting each card with LLM explanation) and simulation runs could batch multiple calls simultaneously, hitting the 3 RPM limit.

**Why this is a risk:** If the Celery task generates 3 decision cards in parallel and each makes an LLM call, the rate limit is hit. OpenAI returns 429 errors. If retry logic isn't perfect, some decisions fail silently and don't appear on the dashboard. The pilot sees fewer decisions than expected. Additionally, the founder may need to prepay for API credits to move to Tier 1 (higher limits) — this requires a payment method, which may be blocked for Indian accounts.

**Likelihood:** Medium. At 3 pilots, 30 LLM calls/day is below the typical rate limit. But burst calls (4 decisions all generated within the same minute by a Celery Beat schedule) could trigger the limit.

**Impact if ignored:** Some decisions silently fail to generate. The pilot sees fewer decision cards than expected. No error is visible unless the founder checks Sentry. A pilot checking their dashboard on Monday morning might see 0 decisions when they should see 3.

**Smallest possible mitigation:**
1. Implement LLM call queueing with rate limiting in the Celery task: never make > 2 concurrent OpenAI calls; queue excess calls with 30-second spacing
2. Add OpenAI API cost and usage tracking from day 1 (log tokens consumed per decision, per day)
3. Pre-fund the OpenAI account with ₹2,000-5,000 to reach Tier 1 (higher rate limits)
4. If rate-limited, the decision is generated without LLM formatting (structured data only, no natural language explanation) and flagged "Simplified — detailed analysis unavailable due to temporary service limit"
5. Decision generation schedule: stagger the 4 decision types across different hours (revenue at 6:00 AM, scheduling gap at 6:15 AM, no-show at 6:30 AM, pricing at 7:00 AM on the 1st only)

**Validation required:** After Task 3.2, generate 5 decision cards in rapid succession. Verify all succeed without 429 errors. Check OpenAI dashboard for actual rate limit tier.

**Documents affected:** Implementation Plan Task 3.2 (add LLM call queueing and staggered scheduling to acceptance criteria).

**Recommendation:** Mitigate Before Implementation

---

### R9: No Backup Strategy in Implementation Plan

**Severity:** High

**Description:** The architecture document specifies daily pg_dump backups to S3 with 30-day retention and continuous WAL archiving. The implementation plan has zero tasks related to database backups, disaster recovery, or data restoration. A single DigitalOcean VM with no backup means: VM failure, accidental `DROP TABLE`, filesystem corruption, or ransomware would permanently destroy all pilot data.

**Why this is a risk:** Pilot data is irreplaceable. If 2 months of pilot data is lost, the entity resolution, calibrated no-show models, and decision history are gone. The pilot would need to reconnect all tools and start from scratch. They won't — they'll churn. At 3 pilots, losing even one's data is catastrophic for validation.

**Likelihood:** Low-Medium for catastrophic VM failure. Higher for accidental data loss (wrong migration, manual query error during development).

**Impact if ignored:** Pilot data is permanently lost. Pilot churns. Validation data (ROI claimed, decisions implemented) is gone. The 6-month validation story is incomplete.

**Smallest possible mitigation:**
1. Add a 1-day task after Task 0.2: "Database Backups" — configure `pg_dump` cron job to run daily at 2:00 AM IST, upload encrypted backup to DigitalOcean Spaces (S3-compatible, ~₹150/month for 50GB)
2. Keep 7 daily backups + 4 weekly backups = 11 restore points
3. Test restore: manually restore a backup to a fresh database within Task 0.2+1
4. Document restore procedure in a RUNBOOK.md
5. WAL archiving (continuous backup) deferred to v2 — acceptable for 3-pilot v1

**Validation required:** Before first pilot onboarding, perform a test restore: take a backup, drop the database, restore from backup, verify all data is present.

**Documents affected:** Implementation Plan (insert backup task after 0.2). Infrastructure document (note backup configuration).

**Recommendation:** Mitigate Before Implementation

---

### R10: First Pilot May Not Match Ideal Profile

**Severity:** High

**Description:** The ideal pilot is: multi-location (2-5), ₹1-5Cr revenue, uses a PMS with API + Razorpay + Zoho Books, owner aged 30-45, tech-forward, referred by a consultant. The acquisition strategy acknowledges that from zero network, the first person who says "yes" may not match this profile. They might be: single-location, using a PMS we haven't built a connector for, using Tally with messy data, older and less tech-comfortable, or not the actual decision-maker (office manager says yes but owner doesn't engage).

**Why this is a risk:** A non-ideal pilot produces poor validation data. Single-location = no location comparison feature used. Wrong PMS = CSV-only mode, which defeats the "autonomous sync" value proposition. Owner doesn't engage = no feedback, no ROI claims, churns silently. At 3 pilots, having 1-2 non-ideal pilots means we only have 1-2 meaningful validation data points.

**Likelihood:** Medium-High. The first person who says "yes" to a free pilot from a student founder is unlikely to be the ideal customer. Ideal customers have options and may wait for social proof.

**Impact if ignored:** Pilots produce weak validation data. The 6-month milestone of "3 pilots with measurable business improvement" is not met, even if 3 practices signed up.

**Smallest possible mitigation:**
1. Define a "pilot readiness score" (1-5) based on: multi-location, PMS with API, Razorpay, owner engagement in first call
2. If a candidate scores < 3, accept them but classify them as a "learning pilot" — useful for product feedback, not counted toward the 3-pilot validation target
3. Continue recruiting until 3 pilots score 4+ on the readiness scale
4. Recruit 5-6 pilots expecting 3 to be "validation-grade" and 2-3 to be "learning-grade"
5. Be willing to say no to a willing pilot if they're a poor fit — an engaged "wrong" pilot is better than no pilot, but not much better

**Validation required:** Score every pilot candidate against the readiness criteria before onboarding. Track scores. If after 3 onboardings, none score 4+, reassess the acquisition strategy.

**Documents affected:** Acquisition Strategy (add pilot readiness scoring). Implementation Plan (note multi-pilot recruitment target — 5-6 recruited, 3 validation-grade).

**Recommendation:** Accept Risk (the mitigation is process, not code — implement during pilot recruitment)

---

## MEDIUM RISKS (8)

---

### R11: Onboarding Wizard OAuth State Management Is Complex

**Severity:** Medium

**Description:** The onboarding wizard (Task 5.1) requires 5 steps, including OAuth redirects for PMS and Zoho Books. The user leaves the Cortex domain, authenticates on the PMS/Zoho domain, and is redirected back. During this flow: the browser back button, page refresh, session timeout, or network interruption can break the OAuth state. Restoring state after a redirect is a known frontend complexity.

**Likelihood:** Medium. OAuth state management bugs are common in first implementations. They're fixable but can take 2-3 extra days of debugging.

**Mitigation:** Store onboarding progress in localStorage with the current step and any partial state. On OAuth redirect back, restore the wizard at the correct step. Test with: browser back button during OAuth, refresh during OAuth, close tab and reopen during OAuth, 10-minute timeout between steps. Add this to Task 5.1 acceptance criteria.

**Documents affected:** Implementation Plan Task 5.1 (add OAuth state persistence tests to acceptance criteria).

**Recommendation:** Validate During Implementation

---

### R12: Alembic Migrations Across Multiple Tenant Schemas

**Severity:** Medium

**Description:** Schema-per-tenant means Alembic must run migrations against every tenant schema. The implementation plan says "Alembic iterates across schemas." If migration 004 runs successfully on schemas 1-2 but fails on schema 3 (e.g., a constraint violation due to different data), the database is in an inconsistent state: schemas 1-2 are upgraded, 3 is not. This is difficult to detect and hard to roll back.

**Likelihood:** Low-Medium. Early in v1 with 3 tenants and controlled data, migration failures are unlikely. The risk increases as pilots accumulate.

**Mitigation:** Wrap all migrations in per-schema transactions. If any schema migration fails, roll back ALL schemas (not just the failed one). This ensures all schemas are at the same version. Test: introduce a deliberate migration failure on schema 3, verify schemas 1-2 are rolled back.

**Documents affected:** Implementation Plan Task 0.2 (add "all-or-nothing migration" to acceptance criteria).

**Recommendation:** Mitigate Before Implementation

---

### R13: Morning Digest Email May Silently Fail

**Severity:** Medium

**Description:** Task 6.1 implements a daily email at 6:00 AM IST. If the email service (Resend/SendGrid) is down, the API fails, or the Celery task crashes, the email is not sent — and neither the founder nor the pilot knows. The pilot doesn't realize they missed an email; they just don't form the daily Cortex habit.

**Likelihood:** Low. Email services are reliable. But Celery task failures do happen.

**Mitigation:** Add a "last digest sent" timestamp to the practice settings page (visible to the pilot: "Last digest: July 20, 6:02 AM"). Add a Sentry alert if a digest fails to send. Add a manual "Resend today's digest" button in admin panel (founder-only).

**Documents affected:** Implementation Plan Task 6.1 (add status tracking and alert to acceptance criteria).

**Recommendation:** Validate During Implementation

---

### R14: "First Insight Within 15-30 Minutes" Promise Depends on PMS API Speed

**Severity:** Medium

**Description:** During onboarding, the product spec promises first insights within 15-30 minutes of completing setup. This depends on: PMS API sync speed (which we don't control), entity resolution speed, metric derivation speed, and decision generation speed. If the PMS API is slow (rate-limited, large dataset, network latency from India to wherever the PMS API is hosted), sync could take hours.

**Likelihood:** Medium. Indian SaaS APIs vary in performance. Practo's API response time is unknown.

**Mitigation:** The onboarding flow already includes "We'll email you when it's done. You can close this page." Keep this. Set expectations during onboarding: "Initial data sync typically takes 15-30 minutes for most practices, but can take up to 2 hours for practices with large appointment histories." Under-promise; over-deliver.

**Documents affected:** Product Spec §3.1.5 (update time estimate to "15 minutes to 2 hours").

**Recommendation:** Validate During Implementation (test with real PMS API during pilot onboarding)

---

### R15: Razorpay API Key Storage Security

**Severity:** Medium

**Description:** The product spec stores Razorpay API keys encrypted with Fernet (AES-256-GCM). The Fernet key is stored in an environment variable. In Docker Compose, environment variables are in the `.env` file or docker-compose.yml — both are on the VM filesystem. An attacker with filesystem access (via compromised container, SSH, or dependency vulnerability) could read the Fernet key and decrypt all stored Razorpay API keys.

**Likelihood:** Low. The attack surface at 3 pilots is minimal. No sensitive patient data is stored (patient names/emails are not encrypted with Fernet — only API keys). The risk is theoretical for v1 but becomes real at scale.

**Mitigation:** For v1 with 3 pilots, this is an acceptable risk. The worst case: an attacker decrypts read-only Razorpay API keys, which can only view payment data, not modify it. Document this as a v2 hardening item. Post-pilot: migrate to HashiCorp Vault or cloud KMS for key storage.

**Documents affected:** None (accept as-is for v1).

**Recommendation:** Accept Risk

---

### R16: No Dead Man's Switch for Decision Generation

**Severity:** Medium

**Description:** Task 7.1 includes a "log warning if no decision generated in 48 hours." But if the founder doesn't check logs daily (which they won't — they're busy networking), this warning goes unseen. Decisions silently stop. The pilot sees an empty dashboard and assumes Cortex has nothing to say, not that Cortex is broken.

**Likelihood:** Medium. Celery Beat can silently fail if Redis restarts without persistence. LLM API errors can cause decisions to fail without surfacing to the UI.

**Mitigation:** Elevate the 48-hour "log warning" to a Sentry CRITICAL alert. Sentry emails the founder. The dashboard also shows: "Last decision generated: July 19, 6:14 AM" — visible to the pilot. If > 24 hours, show "Cortex is running — checking for new insights. Next analysis in..." so the pilot knows the system is alive but found nothing notable.

**Documents affected:** Implementation Plan Task 7.1 (change "log warning" to "Sentry CRITICAL alert"), Task 3.3 (add "last decision timestamp" to dashboard).

**Recommendation:** Mitigate Before Implementation (adds 15 minutes of config)

---

### R17: Pricing Optimization "Default" Elasticity Is Unvalidated

**Severity:** Medium

**Description:** The pricing optimization decision uses a default price elasticity of 0.4 for healthcare services. This number is borrowed from general healthcare economics literature (mostly US-based) and has not been validated against Indian healthcare consumer behavior. Indian patients may be more price-sensitive (higher elasticity) due to lower disposable income and more out-of-pocket healthcare spending.

**Likelihood:** Medium. The elasticity value directly affects the pricing recommendation. If actual elasticity is 0.8 (more price-sensitive) and we recommend a 15% price increase based on 0.4, the practice could lose significantly more patients than projected.

**Mitigation:** Add a caveat to the pricing decision card (already present): "Based on assumed price sensitivity. We recommend testing new prices on a subset of appointment slots first." During the pilot phase, track actual outcomes: if the practice implements a price change, compare projected vs. actual utilization change. After 2-3 pilots, recalibrate the default elasticity with real Indian data.

**Documents affected:** None (caveats already in product spec §6.4).

**Recommendation:** Accept Risk (track during pilot phase)

---

### R18: Indian Mobile Browser Compatibility Not Tested

**Severity:** Medium

**Description:** The product spec says "mobile-responsive secondary" but doesn't specify which mobile browsers. In India, the dominant mobile browsers are Chrome for Android (85%+) and a mix of older Android WebView implementations. Safari on iOS is used by a small minority. The implementation plan doesn't include mobile browser testing in the QA checklist (Task 7.3).

**Likelihood:** Medium. Most Indian practice owners will check email on mobile and click through to the dashboard. The dashboard must render on a ₹8,000 Android phone, not an iPhone 15.

**Mitigation:** Add to Task 7.3 QA: test dashboard, decision cards, and onboarding on (a) Chrome Android (latest), (b) Chrome Android (2 versions back — common on budget phones), (c) Safari iOS. Test on a 360×640 viewport (common low-end Android resolution). Ensure no horizontal scroll, cards are tappable, touch targets are > 44px.

**Documents affected:** Implementation Plan Task 7.3 (add mobile browser testing).

**Recommendation:** Mitigate Before Implementation

---

## LOW RISKS (4)

---

### R19: DigitalOcean Bangalore Region Availability

**Severity:** Low

**Description:** The infrastructure plan selects DigitalOcean Bangalore region. DO Bangalore is relatively new and may have fewer services available than US regions (e.g., managed PostgreSQL may not be available, or Spaces may not have a Bangalore endpoint).

**Mitigation:** Verify DO Bangalore service availability during Task 0.1. If managed PostgreSQL is not available in Bangalore, use DO Mumbai or Singapore region (latency difference is ~20-30ms, acceptable). If Spaces is not available, use AWS S3 Mumbai for backups (₹1-2/month additional).

**Recommendation:** Validate During Implementation (Task 0.1)

---

### R20: doctor_patient@ Email Sharing

**Severity:** Low

**Description:** Some Indian families share a single email for all healthcare appointments (e.g., the husband manages bookings for the entire family using his email). Exact email match would merge all family members into one "patient," producing nonsensical no-show predictions and LTV calculations.

**Mitigation:** Already partially addressed in R4 (entity resolution confidence). Additionally: after entity resolution, check if the same email has appointments under different patient names in the PMS. If yes, flag the email as "shared — not merged." The entity resolution should use email + name together (exact match on both), not email alone. Update the implementation plan to reflect this.

**Documents affected:** Implementation Plan Task 2.3 (change "exact email match" to "exact email + name match").

**Recommendation:** Mitigate Before Implementation

---

### R21: Indian Number Formatting Breaks Display

**Severity:** Low

**Description:** Indian number formatting uses lakhs and crores (1,00,000 not 100,000). The dashboard displays "₹8,47,000" which is correct Indian formatting. But if any JavaScript formatting library uses US formatting, numbers will display incorrectly (₹847,000). This is a minor display bug, not a functional one, but it signals "built for US, not India" to the pilot.

**Mitigation:** Use `Intl.NumberFormat('en-IN')` for all currency and number displays. Test with amounts > ₹99,999 to verify lakh formatting.

**Recommendation:** Validate During Implementation (Task 1.3)

---

### R22: Clerk Organization Limit on Free Tier

**Severity:** Low

**Description:** Clerk's free tier supports 1 organization. The multi-tenancy design maps Clerk organizations to Cortex tenants. At 3 pilots, we need 3 organizations. This may exceed the free tier limit.

**Mitigation:** Check Clerk's current pricing during Task 0.3. If free tier is insufficient, Clerk's Pro plan is ~$25/month — within budget. Alternative: use Clerk's `user_metadata` to store tenant_id instead of Clerk organizations, keeping all users in a single Clerk organization with tenant isolation handled entirely in Cortex.

**Recommendation:** Validate During Implementation (Task 0.3)

---

## SUMMARY

| Severity | Count | Risks |
|----------|-------|-------|
| **Critical** | 3 | R1 (PMS API unvalidated), R2 (Docker no auto-restart), R3 (founder time split) |
| **High** | 7 | R4 (entity resolution confidence), R5 (no SSL/domain), R6 (Razorpay test accounts), R7 (Tally CSV variability), R8 (OpenAI rate limits), R9 (no backups), R10 (non-ideal pilots) |
| **Medium** | 8 | R11-R18 (OAuth state, migrations, email failures, first insight timing, key storage, dead man's switch, pricing elasticity, mobile browsers) |
| **Low** | 4 | R19-R22 (DO Bangalore, shared emails, number formatting, Clerk limits) |
| **Total** | **22** | |

---

## FINAL ASSESSMENT

### 1. Is Cortex ready for implementation?

**Yes, with 6 pre-implementation mitigations required.** The architecture is sound. The product spec is detailed and buildable. The implementation plan is well-sequenced. The risks are concentrated in two areas: unvalidated external dependencies (PMS API, Razorpay test accounts, Tally CSV format) and infrastructure gaps (SSL, backups, auto-restart, rate limits). These are all fixable with small, targeted changes — not redesigns. The 6 mitigations required before code (R1 validation, R2 auto-restart, R4 entity resolution fix, R5 SSL+domain, R9 backups, R12 migration transactions, R16 dead man's switch, R20 email+name matching) total approximately 3-4 days of additional work, not a replan.

### 2. What assumptions must be validated before writing code?

1. **Practo/DocEngage/Lybrate API availability** (R1). Attempt developer registration and API access. If gated, the entire PMS integration strategy changes. Timebox: 1 week.
2. **Razorpay test mode capabilities** (R6). Verify test mode supports all payment methods and webhook simulation without business verification. Timebox: 2 hours.
3. **Clerk organization/pricing limits** (R22). Verify free tier supports ≥3 organizations or switch to metadata-based tenant isolation. Timebox: 1 hour.

### 3. What assumptions can safely be validated during implementation?

All other risks. The PMS API format (exact fields, rate limits), Tally CSV variations, OpenAI rate limit tier, DO Bangalore service availability, and mobile browser compatibility can all be validated as each task is implemented. None of these block the start of Phase 0.

### 4. Which risks are most likely to delay pilot deployment?

**R1 (PMS API)** is the #1 delay risk. If the API is gated, the PMS integration becomes CSV-based, which adds 1-2 weeks of development and degrades the product experience. **R3 (founder burnout)** is the #2 delay risk — if the founder falls behind in weeks 8-10, pilot deployment slips by 2-4 weeks. **R10 (non-ideal pilots)** is the #3 delay risk — spending 4 weeks onboarding a pilot who doesn't produce validation data is sunk time.

### 5. If I were responsible for delivering Cortex to its first paying pilot, would I approve implementation today?

**Yes.** The plan is strong enough. The 6 pre-implementation mitigations are small, concrete, and don't change the architecture. The 22 identified risks are real but manageable — none are showstoppers that require a fundamental rethink. The product spec is detailed enough that an engineer can build from it without asking "what should this do?" The implementation plan is sequenced correctly with clear dependencies. The biggest risk (PMS API availability) has a clear, time-boxed validation step before any code is written.

**The path forward:**
1. Validate R1 (PMS API) — 1 week, no code
2. Apply the 6 pre-implementation mitigations — 3-4 days
3. Begin Task 0.1

The project is approved for implementation.
