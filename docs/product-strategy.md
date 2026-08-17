# Cortex Product Strategy

> *Revision 1 — Founding Systems Architect*
> *Target investor and internal alignment audience*

---

## 1. Core User Journey

### Phase 1: Onboarding (Day 0-1)

The SMB owner signs up via a simple landing page. No sales call required.

1. **Account creation** (2 min) — Email + OAuth (Google/Microsoft). Owner enters business name, industry vertical, revenue range, employee count.
2. **Integration selection** (5 min) — Guided wizard shows "Connect your tools." Vertical-specific defaults pre-selected. Owner clicks "Connect QuickBooks," "Connect Stripe," "Connect Calendly," etc. OAuth flows fire; no API keys pasted.
3. **Data discovery** (background, 2-30 min) — Cortex scans all connected tools, builds a "business sketch": how many customers, what's the revenue trajectory, what services are sold, staffing patterns. A loading bar shows progress.
4. **Calibration survey** (3 min) — "What are your top 3 goals this quarter?" (dropdown: increase revenue, reduce costs, improve utilization, hire smarter). "What keeps you up at night?" (free text). "Do you have a target profit margin?" (optional).
5. **First insight** (immediate) — Cortex surfaces the first decision card: *"Your top 3 customers generate 47% of revenue but average 22% lower margins. Here's why and what to do."*

### Phase 2: Normalization (Week 1-2)

The system learns the business's rhythms:

- Syncs historical data (up to 2 years back from each tool)
- Builds entity resolution across tools (e.g., "Jane Smith" in CRM = "jsmith@email.com" in Stripe = "Client 1043" in accounting)
- Establishes baselines for key metrics (weekly revenue, booking lead time, churn rate, CAC, LTV)
- Generates the initial "Business Model Graph" (see AI Architecture)
- Owner receives a daily digest: 1-3 decision cards per day

### Phase 3: Calibration (Week 2-4)

The system tunes its models to the specific business:

- Decision cards include feedback buttons: "Useful ✓" / "Not useful ✗" / "Already knew this"
- Owner can dismiss, snooze, or implement recommendations
- Cortex learns which decision types the owner values
- Simulation engine calibrates against actual outcomes
- System identifies data quality issues: *"We notice 12% of your invoices are missing service codes. This limits our pricing analysis. Would you like help fixing this?"*

### Phase 4: Daily Use (Month 2+)

Cortex becomes the owner's default morning dashboard:

- **Morning briefing** (daily): top 3 decisions for today, ranked by estimated ROI
- **Push alerts** (as-needed): *"Your booking gap for next week just hit a critical threshold. Estimated revenue at risk: $4,200."*
- **On-demand simulation**: owner types "what if I raised prices 15% on Tuesday mornings?" — gets a response in 30 seconds
- **Weekly review** (Monday): "Here's what we predicted vs. what happened. Our accuracy is improving."
- **Monthly report**: "Here are the decisions you acted on and the measured impact."

---

## 2. User Interface: What the Owner Sees

### Dashboard (Home Screen)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ☀️ Good morning, Dr. Chen                    Mar 17, 2026 (Mon)  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Revenue YTD   │  │ Utilization  │  │ Churn Risk   │              │
│  │ $847K (+14%)  │  │ 72% (+3%)    │  │ 4.2% (↓0.3%) │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
│  ⚡ Today's Top Decisions                                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ [ROI: $12K] Raise hygienist prices 10% → demand is inelastic │ │
│  │            at your current utilization rate.  Show analysis ▸ │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ [ROI: $6K] Reschedule Sarah's Friday block → 3 no-shows in a  │ │
│  │            row suggest a time-slot problem.  Show analysis ▸  │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ [ROI: $3K] Google Ads campaign "teeth-whitening" has 2.1% CTR │ │
│  │            but 0.3% conversion. Pause and reallocate budget. ▸ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  📊 Simulation Quick-Start:  "What if I..."                        │
│  [___________________________________________________]  [Run]      │
└─────────────────────────────────────────────────────────────────────┘
```

### Decision Card (Expanded View)

Each decision card is a self-contained module:

- **Header**: Decision title, estimated ROI badge (green/yellow/red), confidence score
- **Evidence panel**: Data visualizations showing the pattern Cortex detected
- **Causal explanation**: "Why this is happening" — plain English with drill-down
- **Recommendation**: Specific action with step-by-step implementation
- **Simulate**: "See what happens if we do this" button
- **Feedback**: ✓ Useful | ✗ Not Useful | Snooze | Implemented (auto-tracks outcome)

### Simulation UI

```
┌────────────────── What-If Simulation ──────────────────────────────┐
│ "What if I raise hygienist prices by 10%?"                         │
│                                                                     │
│  Parameters:                                                        │
│  ┌────────────┬────────────┬───────────────┐                       │
│  │ Price Δ    │ Timeframe  │ Patient Loss  │                       │
│  │ +10% ──o── │ 90 days    │ 8% (est.)     │                       │
│  └────────────┴────────────┴───────────────┘                       │
│                                                                     │
│  Results:                                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Revenue Impact: +$11,800 (projected)                        │  │
│  │ Profit Impact:  +$8,400  (higher margin, fewer but better $)│  │
│  │ Patient Churn:  4-6% (within acceptable range)              │  │
│  │ Confidence:     ████████░░ 82%                              │  │
│  │                                                            │  │
│  │ Key Drivers:                                                │  │
│  │ • Your current utilization (72%) has room to absorb loss   │  │
│  │ • Demand elasticity in your ZIP is 0.4 (inelastic)         │  │
│  │ • Competitors within 5mi charge 15% more on average        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  [Accept Recommendation]  [Adjust Parameters]  [Export PDF]        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Decision Taxonomy

Cortex surfaces decisions across six domains:

### 3.1 Pricing & Packaging
- Optimal price points per service/product (price elasticity analysis)
- Bundle recommendations (which services to package)
- Discount optimization (when to offer, how much, to whom)
- Tier/plan structuring for recurring revenue
- *v1 priority* — highest ROI for SMBs, most data available

### 3.2 Staffing & Scheduling
- Under/overstaffing detection (compare booked capacity to scheduled staff)
- Optimal shift patterns based on historical demand
- Hiring trigger: "Revenue growing at 8%/mo — you'll hit capacity in 6 weeks"
- Skill gap analysis (which certifications/services are undersold due to lack of qualified staff)
- No-show prediction and overbooking optimization

### 3.3 Marketing Spend Allocation
- Channel ROI comparison (AdWords, Meta, SEO, referrals)
- Campaign pause/scale recommendations based on CAC trends
- Seasonal budget allocation
- Attribution correction (last-click vs. multi-touch)
- *Note: requires website analytics integration*

### 3.4 Churn Intervention
- At-risk customer identification (behavioral triggers)
- Optimal timing for retention outreach
- Personalized offer generation (discount vs. service change)
- Segment-level churn drivers

### 3.5 Cash Flow & Financial Health
- Cash flow forecasting (7/30/90 day)
- A/R aging intervention: "5 invoices are 45+ days overdue — here's a collection sequence"
- Expense anomaly detection: "Your supply costs jumped 22% this month"
- Profitability per service line (not just revenue)

### 3.6 Operational Bottlenecks
- Booking-to-service cycle time analysis
- Appointment gap detection: "You have a $4,200 gap in your schedule next Thursday"
- Inventory/capacity utilization: "You're underutilizing Room 3 — it's empty 40% of the time"
- Workflow friction points (e.g., time between check-in and service start)

---

## 4. Competitive Landscape

### Quadrant Positioning

```
                         │ PROACTIVE
                         │   (surfaces decisions without being asked)
                         │
                         │          ● Cortex
                         │
                         │
    VERTICAL SaaS ───────┼─────────────────────── GENERAL BI
    (e.g., ServiceTitan,  │   (e.g., Tableau, Domo)
     Mindbody, Jane)      │
                         │
                         │  ● AI Chatbots
                         │  (e.g., ChatGPT, Claude, Copilot)
                         │
                         │  ● Klaviyo, HubSpot (narrow AI features)
                         │
                         │ REACTIVE
                         │   (answers questions / visualizes data on demand)
```

### Detailed Competitive Analysis

| Competitor | What They Do | Why They DON'T Solve This | Cortex Advantage |
|-----------|-------------|--------------------------|------------------|
| **Vertical SaaS** (ServiceTitan, Mindbody, JaneApp) | All-in-one scheduling, billing, CRM for specific verticals | Data is locked inside their silo. They can't cross-reference CRM with accounting, or compare your pricing to competitors. No multi-tool causal analysis. | Cross-tool integration discovers insights no single tool can. Example: "Your Calendly shows bookings are down, but Stripe shows actual revenue is up — the problem is a no-show surge, not demand." |
| **BI Tools** (Tableau, Domo, Metabase) | Dashboards + SQL queries | Require data teams. Reactive. No proactive recommendations. No simulation. | Zero-config, proactive, speaks in decisions not charts. |
| **AI Chatbots** (ChatGPT with code interpreter, Claude) | Answer questions on uploaded data | No persistent data connection. No automation. No cross-tool integration. Requires manual data uploads. | Always-on data sync, persistent memory, autonomous decision surfacing. |
| **HubSpot/Salesforce AI features** | In-platform predictions (lead scoring, deal probability) | Only works within their ecosystem. Narrow scope. | Cross-platform, broad decision scope, simulation engine. |
| **Financial planning tools** (Plaid-based cash flow, Float, Pulse) | Cash flow projections only | Single-domain. No operational decisions. | Holistic — connects financial data to operational levers. |
| **Fractional COO services** | Human consultants | Expensive ($3K-$10K/mo). Not always available. Slow. | 24/7, $500-$2,500/mo, instant, consistent, learns over years. |

### Core Differentiator

> **Cortex connects the dots across tools and proactively acts on them.** Every other solution either stays within one silo or waits to be asked. Cortex is the first system that treats the *entire business* as the unit of analysis and *decisions* as the unit of output.

---

## 5. Feature Prioritization: v1 / v2 / v3

### v1 ("Prove Value") — Ship in 8 weeks

**Goal:** One working decision loop — connect, analyze, recommend, get feedback.

| Feature | Priority | Effort | Why v1 |
|---------|----------|--------|--------|
| 5 core integrations (Stripe, QuickBooks, Calendly, Google Analytics, HubSpot) | P0 | 3 weeks | Covers 70% of SMBs' financial + booking data |
| Automated data sync (batch every 6 hours + webhooks) | P0 | 1 week | Freshness baseline |
| Business model graph (entities + relationships) | P0 | 2 weeks | Core representation layer |
| 5 decision types (pricing, no-show risk, booking gap, churn risk, cash flow dip) | P0 | 2 weeks | Narrow but high-value |
| Decision card UI with ROI estimate | P0 | 1 week | User-facing output |
| Feedback loop (✓/✗) | P0 | 0.5 week | Learning signal |
| Simple "What if?" simulation (single-variable) | P1 | 2 weeks | Delight + engagement |
| Morning digest email | P1 | 0.5 week | Daily habit formation |
| Auth + multi-tenancy | P0 | 1 week | Required for any customer |

**v1 metrics target:** 10 customers, 80%+ feedback response rate, 2+ decisions acted on per customer per week

### v2 ("Scale Insights") — Month 2-4

**Goal:** Broaden coverage, deepen analysis, improve accuracy.

| Feature | Priority | Effort | Why v2 |
|---------|----------|--------|--------|
| 10 more integrations (Xero, Square, Mailchimp, Meta Ads, Google Ads, Jane, Acuity, Salesforce, Shopify, Zapier) | P0 | 4 weeks | Broader TAM |
| Multi-variable simulation engine | P0 | 3 weeks | Deeper "what if" capability |
| Causal inference engine (beyond correlation) | P0 | 4 weeks | Core differentiation |
| Decision types expanded to 15 | P0 | 2 weeks | More decisions = more value |
| Vertical-specific tuning (dental, home services, agencies) | P1 | 3 weeks | Better accuracy per vertical |
| Agent-based monitoring (autonomous anomaly detection) | P1 | 2 weeks | Scale without manual rules |
| Implemented-action tracking (auto-detect if owner acted) | P1 | 2 weeks | Validate ROI claims |
| Data quality alerts | P1 | 1 week | Prevent bad recommendations |

### v3 ("Platform") — Month 4-8

**Goal:** Defensible platform with marketplace and network effects.

| Feature | Priority | Effort | Why v3 |
|---------|----------|--------|--------|
| Decision module marketplace (third-party vertical modules) | P0 | 6 weeks | Platform flywheel |
| Custom metric builder (owner defines their own KPIs) | P1 | 3 weeks | Power user retention |
| Shared benchmark database (anonymized cross-customer) | P0 | 4 weeks | "How does my business compare?" — massive value |
| Slack/MS Teams integration | P1 | 1 week | Where SMB owners actually work |
| Mobile app (read-only, push alerts) | P1 | 4 weeks | On-the-go decisions |
| API for embedded Cortex (partners embed decisions in their apps) | P2 | 4 weeks | Distribution channel |
| Natural language conversation (advanced querying) | P1 | 4 weeks | Reduce friction |
| Automated action execution (Cortex books the change) | P2 | 6 weeks | Full autonomy (high risk, high reward) |

---

## 6. Success Metrics & KPIs

### Product-Level (Investor-Facing)
- **Net Revenue Retention** > 120% by month 12
- **Monthly Active Customers** using Cortex 5+ days/week
- **Cumulative ROI Delivered** — sum of customer-reported dollar impact
- **Integration Depth** — avg number of live data sources per customer
- **Time-to-First-Insight** — target < 2 hours from signup

### Decision Quality (Internal)
- **Feedback Positive Rate** — % of decision cards marked "Useful"
- **Implementation Rate** — % of recommendations acted on
- **Prediction Accuracy** — simulated outcome vs. actual outcome
- **Decision Diversity** — spread across the 6 domains (prevents one-note system)

---

## 7. Pricing Tiers

| Tier | Price | Max Integrations | Decision Types | Decisions/Day | Best For |
|------|-------|-----------------|----------------|---------------|----------|
| **Essentials** | $500/mo | 5 | 5 | 3 | $1-3M revenue, single-location |
| **Professional** | $1,200/mo | 10 | 15 | 10 | $3-10M revenue, multi-location |
| **Enterprise** | $2,500/mo | Unlimited | All | Unlimited | $10-20M, custom integrations |

Onboarding fee: $2K (Essentials) / $5K (Enterprise) — covers integration setup and model calibration.

*Future: Usage-based add-on for simulation credits ($0.50/run beyond tier allocation).*