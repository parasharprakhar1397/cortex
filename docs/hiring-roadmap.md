# Cortex Hiring Roadmap

> *Revision 1 — Founding Systems Architect*
> *When to hire, who to hire, and how to build the team*

---

## 1. Hiring Philosophy

1. **Small team, big leverage** — every hire must multiply the team's impact, not just add to it
2. **Generalists first, specialists later** — the first 5 hires can wear multiple hats; specialists come at 10+ 
3. **Hire for slope, not intercept** — we care more about learning velocity than current skill level
4. **No mediocre hires** — in a 5-person startup, one bad hire is a 20% problem. We can't afford it.
5. **Remote-first** — best talent is distributed; we build async communication muscle from day 1

---

## 2. First 5 Hires

```
TIMING:               Month 0          Month 3          Month 6          Month 9          Month 12
                        │                │                │                │                │
                        │                │                │                │                │
Founder (CTO)          ██████████████████████████████████████████████████████████████████████
                        │
Engineer #2            │                ████████████████████████████████████████████████████
(Full-stack generalist)│                │
                        │
Engineer #3            │                │                █████████████████████████████████████
(Python backend)       │                │                │
                        │
CS #1                  │                │                █████████████████████████████████████
(Customer success /    │                │                │
 onboarding specialist)│                │                │
                        │
Engineer #4            │                │                │                ████████████████████
(AI/ML engineer)       │                │                │                │
                        │                │                │                │
                        ▼                ▼                ▼                ▼                ▼
Customers:             0-3             3-15             15-30            30-100           100-200
```

### Hire #1: Engineer #2 (Month 3)

**Role:** Full-stack generalist
**Why now:** Founder is doing all the building. With 3 pilots onboarding, founder needs to split time between development and customer discovery. Engineer #2 handles the backend and integration work while founder focuses on product architecture and sales.

**Profile:**
- 3-5 years experience
- Python-heavy (FastAPI, SQLAlchemy, Celery)
- Comfortable with React/Vite frontend work
- Has built an integration connector before (Stripe API, QuickBooks, etc.)
- Startup experience preferred (they know what "move fast" means)
- Can work independently without detailed specs

**Cost:** $100-130K/yr + 0.5-1.0% equity (ISO, 4yr vest, 1yr cliff)

**Onboarding (first 4 weeks):**
1. Week 1: Set up dev environment, pair on a connector, write first API endpoint
2. Week 2: Own one integration (Calendly), deliver independently
3. Week 3: Take over data pipeline maintenance, fix entity resolution bugs
4. Week 4: Ship a complete feature (decision card type) end-to-end

### Hire #2: Engineer #3 (Month 6)

**Role:** Python backend / data engineer
**Why now:** 15+ customers are generating real data. The pipeline needs dedicated attention: data quality monitoring, performance optimization, alerting. Engineer #2 is stretched between features and pipeline health.

**Profile:**
- 2-5 years experience
- Strong SQL (PostgreSQL, query optimization, schema design)
- Experience with ETL/data pipelines (Airflow, Dagster, or similar)
- Bonus: experience with TimescaleDB or time-series data
- Comfortable with async Python (asyncio, Celery)

**Cost:** $100-120K/yr + 0.25-0.5% equity

**Onboarding focus:**
1. Data pipeline ownership — monitoring, alerting, performance
2. Entity resolution improvements
3. Integration health monitoring and auto-healing
4. Occasional feature work during pipeline downtime

### Hire #3: CS #1 (Month 6)

**Role:** Customer success / onboarding specialist
**Why now:** 15 customers means the founder is spending 20+ hours/week on support and onboarding. This time needs to be redirected to product and architecture. A dedicated CS person handles onboarding, support, and health monitoring.

**Profile:**
- 2-4 years in customer success or account management at a B2B SaaS startup
- Technical enough to understand APIs, OAuth, and data integrations
- Excellent written communicator (most support is async)
- Comfortable with small team ambiguity
- Bonus: experience with SMB customers

**Cost:** $70-90K/yr + 0.1-0.25% equity

**Responsibilities:**
- Onboard new customers (guided setup, training calls)
- Tier 1 support (triage, answer questions, escalate bugs)
- Customer health monitoring (usage dashboards, proactive outreach to at-risk customers)
- Feedback collection and prioritization (bridge between customer and engineering)
- Knowledge base creation and maintenance
- NPS surveys and reference calls

### Hire #4: Engineer #4 (Month 9)

**Role:** AI/ML engineer
**Why now:** 30+ customers means agent quality is critical. Causal models need tuning, decision accuracy needs improvement, and the cold-start problem needs solving. One engineer dedicated to AI full-time.

**Profile:**
- 3-5 years in ML/AI engineering
- Experience with LLMs (fine-tuning, prompt engineering, RAG)
- Experience with causal inference (DoWhy, EconML) preferred but teachable
- Python-heavy (PyTorch, transformers, scikit-learn)
- Understands production ML (ML pipelines, monitoring, A/B testing)
- Bonus: experience with LangGraph or similar agent frameworks

**Cost:** $130-160K/yr + 0.25-0.5% equity

**Responsibilities:**
- Improve decision accuracy (reduce false positives, increase relevant recommendations)
- Tune causal models per vertical
- Implement cross-customer learning (federated parameter estimation)
- Monitoring agent quality (decision confidence, feedback rates)
- Build simulation engine improvements
- Optimize LLM cost and latency

---

## 3. Second Wave Hires (Months 9-18, at 30-100 Customers)

| Hire | When | Why | Cost |
|------|------|-----|------|
| **Engineer #5** (infrastructure/DevOps) | Month 12 | 50+ customers need reliable infrastructure. Docker Compose → k8s migration. GPU scaling. | $130-150K + 0.15-0.3% |
| **Sales #1** (SMB sales) | Month 12 | Founder can't run sales at 50+ customers. Need someone to handle inbound and outbound. | $80-100K + commission + 0.15-0.3% |
| **Marketing #1** (content/demand gen) | Month 12 | Need consistent pipeline. SEO, content, case studies, events. | $80-100K + 0.1-0.2% |
| **CS #2** | Month 15 | 80+ customers exceeds one CS person's capacity. | $70-90K + 0.05-0.1% |
| **Engineer #6** (frontend/full-stack) | Month 15 | Dashboard, simulation UI, marketplace, mobile need dedicated frontend focus. | $110-140K + 0.1-0.2% |

---

## 4. Founder Transition Plan

### Month 0-6: Full-Stack Founder

| Activity | % Time |
|----------|--------|
| Product design & architecture | 30% |
| Coding (backend, integrations, agents) | 35% |
| Customer discovery & sales | 20% |
| Customer support | 10% |
| Strategy & fundraising prep | 5% |

### Month 6-12: Architect/CTO Emerging

| Activity | % Time | Who Takes Over |
|----------|--------|----------------|
| Product vision & architecture | 30% | — |
| Code review & technical direction | 20% | — |
| Customer discovery & sales | 10% | Engineer #2 (technical demos), CS #1 (support) |
| Customer support | 0% | CS #1 |
| Fundraising | 20% | — |
| Hiring & team building | 20% | — |

### Month 12-24: Full CTO

| Activity | % Time | Who Takes Over |
|----------|--------|----------------|
| Product vision & architecture | 25% | — |
| AI/ML strategy & roadmap | 20% | — |
| Technical team management | 20% | Engineering lead (Engineer #2 promoted) |
| Fundraising & investor relations | 20% | — |
| Strategic partnerships | 10% | — |
| Sales | 0% | Sales #1 |
| Customer support | 0% | CS team |
| Day-to-day coding | 5% | Engineering team |

---

## 5. Org Chart Evolution

### Solo (0-3 months)
```
Founder (CTO)
```

### 3 People (6 months)
```
Founder (CTO)
├── Engineer #2 (full-stack)
└── (outsourced: design, legal, accounting)
```

### 6 People (12 months)
```
Founder (CTO)
├── Engineering
│   ├── Engineer #2 (lead)
│   ├── Engineer #3 (backend/data)
│   └── Engineer #4 (AI/ML)
├── Customer Success
│   └── CS #1
└── (outsourced: design, legal, accounting)
```

### 12 People (18 months)
```
Founder (CTO)
├── Engineering (7 people)
│   ├── Engineer #2 → Engineering Manager
│   │   ├── Engineer #3 (backend/data)
│   │   ├── Engineer #5 (infrastructure)
│   │   └── Engineer #6 (frontend)
│   └── Engineer #4 → AI Lead
│       ├── Engineer #7 (AI/ML)
│       └── Data Science intern
├── Go-to-Market (3 people)
│   ├── Sales #1
│   └── Marketing #1
├── Customer Success (2 people)
│   ├── CS #1 (lead)
│   └── CS #2
└── Operations (1 person)
    └── Part-time operations / finance
```

### 20 People (24 months — post-Series A)
```
CEO (new hire or founder transition) / Founder (CTO)
├── Engineering (8-10)
├── Product (2)
├── Sales (3)
├── Marketing (2)
├── Customer Success (3)
├── Operations/Finance (1-2)
└── (outsourced: HR, legal, recruiting)
```

---

## 6. Equity & Compensation Philosophy

### Cash Compensation

| Role | Salary Range | Benchmark Source |
|------|-------------|-----------------|
| Engineer (early) | $100-160K | Levels.fyi (Series A, remote) |
| CS | $70-95K | BuiltIn / Glassdoor (SaaS startup) |
| Sales | $80-100K base + $60-100K variable | Industry standard for SMB SaaS (1.5x OTE) |
| Marketing | $80-110K | Levels.fyi (SaaS marketing IC) |
| Operations | $70-90K | Glassdoor |

**Note:** Salaries are 10-20% lower than market because equity is meaningful. We're transparent about this.

### Equity Pool

| Pool Size | When | Purpose |
|-----------|------|---------|
| 10% | Pre-seed | Founder + first 5 hires + advisors |
| 15% | Seed round | New hires + retention grants |
| 10% | Series A | New hires + retention grants |
| Total: 35% | Over 24 months | — |

### Equity Grants (Indicative)

| Hire # | Role | Equity | Vesting |
|--------|------|--------|---------|
| 1 (Founder) | CTO | 60-80% (founder shares) | 4yr, 1yr cliff |
| 2 | Engineer | 0.5-1.0% | 4yr, 1yr cliff |
| 3 | Engineer | 0.25-0.5% | 4yr, 1yr cliff |
| 4 | CS | 0.1-0.25% | 4yr, 1yr cliff |
| 5 | AI/ML Engineer | 0.25-0.5% | 4yr, 1yr cliff |
| 6-8 | Hires (post-seed) | 0.1-0.3% | 4yr, 1yr cliff |
| Advisors | Domain experts | 0.15-0.25% (each) | 2yr, 6mo cliff |

### Benefits

- Remote-first: $1K/yr home office stipend
- Health insurance: 80% premium coverage (US employees)  
- Unlimited PTO (with minimum 15 days enforced)
- Conference budget: $2K/yr per engineer
- Equipment: $3K laptop + accessories budget
- 401(k): Not until 15+ employees

---

## 7. Remote/Office Strategy

### Decision: Remote-First, With Optional Co-Working

**Why remote-first:**
- Best AI/ML talent is distributed (not in SF/NYC only)
- SMB customers are everywhere (distributed team = broader perspective)
- Lower burn rate ($0 office overhead vs. $5-10K/mo)
- Founder is coding → deep work requires quiet, which remote enables
- Our core market (SMB owners) are not in SF either

**When to get office:**
- Post-Series A (20+ people): small office in a low-cost city (Austin, Denver, Raleigh)
- Purpose: team bonding, offsites, customer meetings
- Not before: it's a distraction and a cash drain at early stage

**Team coordination practices:**
- Daily async standup (written, Slack, or Linear) — no meetings for status
- Weekly all-hands (30 min, written + optional video)
- Bi-weekly 1:1s for every manager-direct report pair
- Quarterly offsite (3 days, all expenses paid, at founder's home or rental)
- Core working hours overlap: 4 hours minimum (10am-2pm ET / 7am-11am PT)
- Documentation is the default (written culture over verbal culture)

### Hiring Geography

| Role | Preferred Timezone | Why |
|------|-------------------|-----|
| Engineering | Americas (ET/CT/MT/PT) | Overlap with founder (ET) |
| CS | Americas (ET/CT) | Overlap with SMB customers (US business hours) |
| Sales | Americas (ET/CT) | Same as above |
| Marketing | Any US timezone | Async-friendly role |
| AI/ML | Americas or Europe | Core overlap hours during afternoon EU time |

---

## 8. Hiring Process

### Timeline (Per Role)

```
Week 1: Post job description (AngelList, LinkedIn, personal network)
Week 2: Review applications (target: 50-100 applications)
Week 3: Phone screen (30 min, founder) → 5-8 candidates
Week 4: Take-home exercise (2-4 hours) → 3-4 candidates
Week 5: Final interview loop (2 hours: technical + cultural) → 1-2 candidates
Week 6: Reference checks + offer
Week 7: Start date (if accepted)
```

### What We Evaluate

| Role | Technical | Cultural | Signals We Look For |
|------|-----------|----------|---------------------|
| **Engineer** | Take-home: build a small data pipeline or API endpoint. Pair programming on an actual Cortex feature. | Async communication, ownership mindset, low ego | Personal projects, open-source contributions, technical writing |
| **CS** | Role-play: handle a difficult customer scenario. Write a support email for a data quality issue. | Empathy, patience, proactive communication | Startup experience, technical background, customer-facing roles |
| **Sales** | Mock demo: sell Cortex to a mock SMB owner. Handle objections. | Authenticity, listening skills, resilience | Previous SaaS sales, experience selling to SMBs |
| **Marketing** | Portfolio review: content, campaigns, SEO results. Write a case study from raw notes. | Creativity, data-driven, written communication | B2B SaaS marketing, SMB focus, self-starter evidence |

### Red Flags

- **"At my last company, we did it this way"** without first understanding why Cortex does it differently
- **Unwilling to do async work** — "I need daily standups" = potential remote-first culture mismatch
- **Uncomfortable with ambiguity** — startup life is constant ambiguity
- **Doesn't ask questions** — the best candidates probe our assumptions
- **Equity isn't important** — at this stage, equity is a core part of compensation

---