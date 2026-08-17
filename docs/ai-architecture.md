# Cortex AI Architecture

> *Revision 1 — Founding Systems Architect*
> *For engineers, ML practitioners, and technically-savvy investors*
> *This is NOT an AI wrapper. This is the intelligence system.*

---

## 1. Design Principles

1. **Causal > Correlational** — Cortex must understand *why*, not just *what*. Correlation-based recommendations fail when underlying conditions change.
2. **Business-first, LLM-second** — The LLM is a reasoning engine that operates on a structured business model, not a chat window. The structure does the heavy lifting.
3. **Explainability is non-negotiable** — An SMB owner will not trust a black box. Every decision must be traceable to specific data.
4. **Cold-start aware** — The system must work with limited data (day 1) and improve over time (month 12).
5. **Cost-controlled** — We cannot burn $0.50 per API call for every customer decision. Tiered model usage: cheap/fast for routine analysis, expensive/deep for complex simulation.

---

## 2. Model Architecture

### The "Stack"

```
┌──────────────────────────────────────────────────────────────────┐
│                    ROUTING LAYER (Decision Router)               │
│   Classifies incoming query/alert → selects model strategy       │
│   (Small LM / Causal Model / Full LLM / Simulation)             │
└──────────────┬───────────────────────────────────┬───────────────┘
               │                                   │
     ┌─────────▼─────────┐             ┌───────────▼───────────┐
     │  TIER 1: FAST      │             │  TIER 2: DEEP        │
     │  < $0.005/call     │             │  < $0.10/call        │
     │  < 1s latency      │             │  < 10s latency       │
     │                    │             │                      │
     │ ┌──────────────┐  │             │ ┌──────────────────┐ │
     │ │ Small LM     │  │             │ │ Large LLM        │ │
     │ │ (Llama 3 8B) │  │             │ │ (Llama 3 70B /   │ │
     │ │ Self-hosted  │  │             │ │  GPT-4o fallback)│ │
     │ │ via vLLM     │  │             │ │ vLLM + fallback  │ │
     │ └──────┬───────┘  │             │ └────────┬─────────┘ │
     │        │          │             │          │            │
     │ ┌──────┴───────┐  │             │ ┌────────┴────────┐  │
     │ │ Statistical  │  │             │ │ Causal          │  │
     │ │ Models       │  │             │ │ Inference       │  │
     │ │ (scipy,      │  │             │ │ Engine          │  │
     │ │  statsmodels)│  │             │ │ (DoWhy + custom)│  │
     │ └──────────────┘  │             │ └─────────────────┘  │
     └───────────────────┘             └──────────────────────┘
               │                                   │
               └────────────────┬──────────────────┘
                                │
              ┌─────────────────▼──────────────────┐
              │      SHARED INFRASTRUCTURE         │
              │                                    │
              │  ┌────────────┐  ┌──────────────┐  │
              │  │ Embedding  │  │ Business     │  │
              │  │ Model      │  │ Model Graph  │  │
              │  │ (BGE-M3)   │  │ (Postgres +  │  │
              │  │ Self-hosted│  │  pgvector)   │  │
              │  └────────────┘  └──────────────┘  │
              │                                    │
              │  ┌────────────┐  ┌──────────────┐  │
              │  │ Simulation │  │ Causal Graph │  │
              │  │ Engine     │  │ (per-tenant) │  │
              │  │ (Monte     │  │              │  │
              │  │  Carlo)    │  │              │  │
              │  └────────────┘  └──────────────┘  │
              └────────────────────────────────────┘
```

### 2.1 Tier 1: Fast Path (Routine Decisions)

**Used for:** Pattern detection, metric anomalies, simple correlations, daily briefings.

**Components:**

| Component | Technology | Purpose | Cost |
|-----------|-----------|---------|------|
| Small LLM | Llama 3 8B (self-hosted via vLLM) | Natural language generation from structured data | ~$0.002/call |
| Statistical models | scipy + statsmodels | Time-series decomposition, trend detection, seasonality | ~$0.0001/call |
| Decision classifier | LightGBM (trained per-vertical) | Classifies patterns into decision types, scores confidence | ~$0.0001/call |

**How it works:**

1. **Monitoring Agent** detects shift in a metric (e.g., utilization dropped from 72% to 65% in 2 days)
2. **Statistical models** decompose the signal: is this seasonal, trend-based, or anomalous?
3. **Decision classifier** maps the anomaly type to a decision category (scheduling, staffing, pricing)
4. **Small LLM** generates a concise alert with the evidence panel text, using the structured data as context
5. Result: 3-second cycle, $0.003 total cost

### 2.2 Tier 2: Deep Path (Complex Decisions & Simulation)

**Used for:** Causal analysis, "What if" simulation, strategic recommendations, high-stakes decisions.

**Components:**

| Component | Technology | Purpose | Cost |
|-----------|-----------|---------|------|
| Large LLM | Llama 3 70B (self-hosted vLLM) → GPT-4o fallback | Reasoning, multi-step analysis, natural language | ~$0.03-0.10/call |
| Causal engine | DoWhy + EconML + custom structural causal models | Causal inference (what happens if we change X?) | ~$0.01/run |
| Simulation engine | Custom Monte Carlo + discrete-event simulator | Simulate business processes | ~$0.02/run |

**How it works:**

1. **Analysis Agent** identifies a complex pattern (e.g., "revenue flat but bookings up — pricing or no-show issue?")
2. **Causal engine** constructs a causal graph from business entities and tests hypotheses using double-ML or instrumental variables
3. **Large LLM** takes the causal analysis output and generates a structured recommendation with full reasoning chain
4. **Simulation engine** optionally runs "what-if" scenarios to validate the recommendation
5. Result: 10-30 second cycle, $0.05-0.15 total cost

### 2.3 Tier Routing Logic

```
IF (new data arrives AND metric crosses threshold):
    → Fast Path (Tier 1)

IF (Tier 1 confidence < 70% AND decision impact estimate > $500):
    → Queue for Deep Path (Tier 2)

IF (user asks "What if X?"):
    → Deep Path + Simulation (Tier 2)

IF (user provides negative feedback on Tier 1 decision):
    → Re-analyze via Deep Path (Tier 2)

IF (weekly/monthly strategic review):
    → Deep Path (Tier 2)
```

---

## 3. The Living Business Model

This is the core of Cortex's intelligence. A machine-readable representation of the business that supports query, simulation, and reasoning.

### 3.1 Representation: Hybrid Entity Graph + Vector Embeddings

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS MODEL GRAPH                         │
│                                                                 │
│  ┌──────────┐    ┌─────────────┐    ┌──────────┐              │
│  │ Customer ├────┤ Invoice     ├────┤ Payment  │              │
│  │ (entity) │    │ (entity)    │    │ (entity) │              │
│  └────┬─────┘    └─────────────┘    └──────────┘              │
│       │                                                        │
│       │  ┌─────────────┐    ┌──────────┐                      │
│       ├──┤ Booking     ├────┤ Service  │                      │
│       │  │ (entity)    │    │ (entity) │                      │
│       │  └─────────────┘    └──────────┘                      │
│       │                                                        │
│       │  ┌─────────────┐                                      │
│       └──┤ Review      │                                      │
│          │ (entity)    │                                      │
│          └─────────────┘                                      │
│                                                                 │
│  ┌──────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │ Employee ├────┤ Time Entry  │    │ Schedule    │           │
│  │ (entity) │    │ (entity)    │    │ (entity)    │           │
│  └──────────┘    └─────────────┘    └─────────────┘           │
│                                                                 │
│  Each entity has:                                               │
│  • Structured attributes (JSONB)                                │
│  • Vector embedding (pgvector, 1024-dim, BGE-M3)              │
│  • Relationships (typed edges with properties)                  │
│  • Time-series metric references (hypertable pointers)         │
│  • Provenance (which source tool, last updated)                │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Entity Types (v1)

| Entity | Core Attributes | Source Tools | Vector Embedding Purpose |
|--------|----------------|-------------|--------------------------|
| `Business` | Name, vertical, revenue, location, employee count | Onboarding form + enrichment | Matching to peer benchmarks |
| `Customer` | Name, email, phone, LTV, acquisition channel, segment | CRM, Stripe, accounting | Finding similar customers for churn analysis |
| `Service` | Name, category, price, duration, materials cost | Booking, accounting, POS | Pricing elasticity groups |
| `Invoice` | Amount, date, status, line items | Accounting, Stripe | Revenue patterns, aging analysis |
| `Booking` | Time, service, employee, customer, outcome (show/no-show) | Calendly, Jane, Acuity | Capacity planning, no-show prediction |
| `Payment` | Amount, method, date, invoice_id | Stripe, Square | Cash flow forecasting |
| `Campaign` | Channel, spend, impressions, clicks, conversions | Google Ads, Meta Ads | ROAS computation |
| `Employee` | Name, role, hourly_rate, certifications | HRIS, scheduling | Utilization analysis |
| `Expense` | Category, amount, date, vendor | Accounting | Anomaly detection |

### 3.3 Graph Construction Pipeline

```
Raw Data → Entity Extraction → Relationship Linking → Metric Derivation → Embedding
```

1. **Entity Extraction:** Normalized records from data pipeline → typed entities with structured attributes
2. **Relationship Linking:** Foreign key resolution across sources (e.g., `stripe_invoice.customer_email` → `crm_contact.email`)
3. **Metric Derivation:** Compute derived metrics per entity (Customer LTV = sum of all payments / customer age in months)
4. **Embedding:** Generate vector embedding for each entity using BGE-M3 — this enables semantic similarity search
   - "Find customers similar to our top 10% by value"
   - "Find services with similar price elasticity profiles"

### 3.4 Query Patterns the Graph Supports

| Query Type | Example | How It's Answered |
|-----------|---------|-------------------|
| **Aggregate** | "What's my revenue this month?" | Hypertable time-series query |
| **Relational** | "Which customers have unpaid invoices >30 days?" | Graph traversal: Customer → Invoice WHERE status=unpaid AND age>30d |
| **Similarity** | "Find customers like Jane Smith" | Vector similarity search on customer embeddings |
| **Temporal** | "Show me booking patterns for Tuesdays" | Time-series with day-of-week filter |
| **Causal** | "What drives no-show rates?" | Causal graph query → variable importance scores |
| **Composite** | "Which services are both high-margin and low-utilization?" | Cross-entity graph query with metric thresholds |

---

## 4. Causal Reasoning Engine

### 4.1 Why Causal ML, Not Just Correlation

**The problem with correlation-only approaches:**
- "No-show rates are correlated with Tuesday appointments" → might be because Tuesday is the day Dr. Smith works, and Dr. Smith's patients have higher no-show rates. The intervention "stop Tuesday bookings" would have unexpected effects.
- "Customers who bought teeth whitening have higher LTV" → might be that teeth whitening is bought by wealthier customers who already had higher LTV. Recommending teeth whitening to all customers would fail.

**Causal approach:**
1. Build a structural causal model (SCM) per business/vertical
2. Use domain knowledge + data to define the causal graph
3. Apply causal inference methods (do-calculus, IV, difference-in-differences, double-ML)
4. Answer: "What is the effect of *intervening* on X?"

### 4.2 Causal Graph Construction

For a dental practice, the initial causal graph might look like:

```
┌──────────┐    ┌────────────┐    ┌───────────┐
│ Season   ├───►│ Scheduling │◄───│ Staff     │
│ (month)  │    │ Quality    │    │ Experience │
└──────────┘    └─────┬──────┘    └───────────┘
                      │              │
                      ▼              ▼
                 ┌────────┐    ┌──────────┐
                 │ Booking │    │ Price    │
                 │ Volume  │    │          │
                 └────┬───┘    └─────┬────┘
                      │              │
                      ▼              ▼
                 ┌────────┐    ┌──────────┐
                 │ No-Show│    │ Patient  │
                 │ Rate   │    │ Churn    │
                 └────┬───┘    └────┬─────┘
                      │              │
                      └──────┬──────┘
                             ▼
                      ┌──────────┐
                      │ Revenue  │
                      └──────────┘
```

**How the graph is built:**
- **v1 (cold start):** Template-based — each vertical has a hand-crafted causal DAG from domain expert knowledge. For a dental practice: 40+ variables with known causal directions.
- **v2 (data-driven refinement):** Use causal discovery algorithms (PC algorithm, FCI, GES) to suggest edge additions/removals from data, reviewed by a confidence threshold
- **v3 (personalized):** Per-business causal parameters learned via Bayesian structural time series

### 4.3 Causal Inference Methods

| Method | When Used | Example | Library |
|--------|-----------|---------|---------|
| **Double ML** | Continuous treatment, high-dimensional controls | "Effect of price change on demand" | EconML |
| **Difference-in-differences** | Natural experiment, before/after | "Effect of adding Saturday hours on revenue" | DoWhy |
| **Instrumental variables** | Unobserved confounders | "Effect of ad spend on bookings" (using platform outages as IV) | DoWhy + custom |
| **Causal forest** | Heterogeneous treatment effects | "Which customers respond to retention emails?" | EconML (CausalForest) |
| **Do-calculus** | Identifiability analysis | "Can we estimate this effect from observational data?" | DoWhy (back-door criterion) |
| **Bayesian structural time series** | Counterfactual estimation | "What would revenue have been without last month's promotion?" | CausalImpact (R → Python port) |

### 4.4 Confidence Scoring

Each causal estimate includes:
- **Statistical significance** (p-value, confidence interval)
- **Sensitivity analysis** (how robust is the estimate to unobserved confounders?)
- **Data density** (N observations behind the estimate)
- **Model fit** (R², cross-validation RMSE)

Results below confidence threshold (p > 0.10, N < 30) are surfaced as "emerging patterns, not yet confident" rather than recommendations.

---

## 5. Simulation Engine

### 5.1 Architecture

```
┌─────────────── User Query ───────────────┐
"What if I raise prices by 10%?"           │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│      QUERY PARSER (Large LLM)                │
│  • Extract: variable (price), delta (+10%),  │
│    scope (all services / specific),          │
│    timeframe (90 days)                       │
│  • Map to business model variables           │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│      SIMULATION CONFIGURATOR                 │
│  • Select relevant causal subgraph           │
│  • Set intervention on price variable        │
│  • Configure Monte Carlo parameters          │
│    (10,000 iterations, 95% CI)               │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│      MONTE CARLO SIMULATOR                   │
│  • Sample from posterior distributions       │
│    of causal parameters                      │
│  • Propagate through causal graph            │
│  • Compute outcome distributions             │
│    (revenue, profit, churn, utilization)     │
│  • Multiple horizons: 30/60/90 days          │
└──────────────────┬───────────────────────────┘
                   ▼
┌──────────────────────────────────────────────┐
│      RESULT INTERPRETER (Large LLM)          │
│  • Translate numerical distributions to      │
│    natural language                          │
│  • Highlight key risks and assumptions       │
│  • Generate sensitivity tornado plot data    │
│  • Estimated ROI with confidence bands       │
└──────────────────┬───────────────────────────┘
                   ▼
        ┌──────────────────────┐
        │ Decision Card +      │
        │ Simulation UI        │
        └──────────────────────┘
```

### 5.2 Simulation Types

| Type | Method | Latency | Use Case |
|------|--------|---------|----------|
| **Single-variable** (v1) | Change one variable, propagate through causal graph | 3-5s | "What if prices +10%?" |
| **Multi-variable** (v2) | Change multiple variables, capture interactions | 10-20s | "What if prices +10% and add Saturday hours?" |
| **Policy simulation** (v2) | Change a business rule | 15-30s | "What if we implement a no-show fee?" |
| **Adversarial** (v3) | Worst-case scenario testing | 30-60s | "What if our best employee quits AND the economy enters a recession?" |
| **Optimization** (v3) | Search for optimal parameter values | 60-300s | "What's the optimal price for teeth whitening?" |

### 5.3 Parameter Uncertainty

All simulations include uncertainty quantification:
- **Aleatoric uncertainty** (inherent randomness): captured by Monte Carlo sampling from noise distributions
- **Epistemic uncertainty** (model uncertainty): captured by sampling from posterior of causal parameters
- **Structural uncertainty** (model misspecification): captured by sensitivity analysis (varying the causal graph)

**Result format:**
```
ROI Estimate: $11,800 (80% CI: $4,200 - $19,100)
Probability of positive ROI: 94%
Key assumption: Current demand elasticity of 0.4 holds.
Sensitivity to: Competitor response (unknown), seasonality (modeled)
```

---

## 6. ROI Estimation Methodology

### 6.1 The ROI Formula

For each decision, Cortex estimates:

```
ROI = (ΔRevenue + ΔSavings) × Confidence - Implementation Cost
```

Where each term is estimated from the causal model:

- **ΔRevenue:** Expected change in revenue from intervention (from Monte Carlo simulation)
- **ΔSavings:** Expected reduction in costs (waste, churn prevention, efficiency gains)
- **Confidence:** Composite score (0-1) combining statistical confidence, data recency, and model fit
- **Implementation Cost:** Estimated effort to execute the decision (owner provides this feedback; default is industry average)

### 6.2 Validation Loop

```
Decision Generated ──► Owner Acts ──► Data Flows In ──► Compare to Prediction
        │                                                            │
        └────────────────────◄ Feedback ◄────────────────────────────┘
```

1. Cortex predicts "raising prices 10% will increase revenue by $11,800 in 90 days"
2. Owner implements price change
3. 90 days later, actual data flows in through integrations
4. Cortex compares actual Δrevenue to predicted Δrevenue
5. Error signal tunes the causal model parameters (Bayesian update)
6. Over time, per-business calibration improves accuracy

### 6.3 ROI Badging

| Label | Condition | Visual |
|-------|-----------|--------|
| **Verified** | Similar recommendation implemented ≥3 times across customers with ≥80% accuracy | Green checkmark |
| **Estimated** | Statistical estimate, not yet validated | Blue percentage |
| **Emerging** | Low confidence, needs more data | Gray / dashed border |
| **Simulated** | Hypothetical, no empirical support yet | Purple / sparkle icon |

---

## 7. Explainability Architecture

### 7.1 The Explanation Chain

Every decision card includes a chain of reasoning:

```
├── "Your hygienist no-show rate increased to 15%"
│   └── Evidence: 23 no-shows in April vs. 11 in March (data source: Calendly)
│       └── Breakdown: 18 of 23 were Tuesday slots (p < 0.01)
│           └── Root cause: Tuesday is the only day hygienist #3 works
│               └── Hygienist #3 has 3x higher no-show rate (6.2% vs 2.1%), 
│                   possibly due to patient demographics in her panel
├── "If you reschedule hygienist #3's panel, you could recover $4,200/mo"
│   └── Simulation: Rescheduling 18 no-shows at avg $210/appt = $3,780
│       └── Plus: freed slots booked by other patients at 60% fill rate = $1,260
│           └── Net: $3,780 + $1,260 - $840 (staffing adjustment) = $4,200
│               └── Monte Carlo: 80% CI [$2,100, $6,800], P(positive) = 93%
└── "I suggest: Talk to hygienist #3 about scheduling preferences or 
     adjust her patient panel to better-matched demographics"
    └── Confidence: High (N=34 observations, p=0.003)
```

### 7.2 Explanation Components

| Component | Technology | Content |
|-----------|-----------|---------|
| **Evidence panel** | Structured data (charts, tables) | Raw data supporting the pattern |
| **Causal trace** | Causal graph path highlighting | "X affects Y through Z" visual path |
| **Statistical summary** | Statsmodels output | Effect size, p-value, confidence intervals |
| **Counterfactual** | DoWhy counterfactual query | "What would have happened if..." |
| **Natural language** | LLM-generated (Tier 1 or 2) | Plain English summary |
| **Source attribution** | Provenance metadata | "This data came from QuickBooks (last synced 2h ago)" |

### 7.3 Counterfactual Explanations

One especially powerful explainability technique: *counterfactual minimal edits.*

> "Your no-show rate is 15%. If you reschedule hygienist #3's Tuesday panel, it would drop to 9.2%."

This is computed by the causal engine: intervene on the causal graph (remove the hygienist #3→Tuesday edge), recompute the outcome, and compare.

---

## 8. Memory & Adaptation

(See also `memory-systems.md` for full detail)

### 8.1 Per-Business Adaptation

Cortex personalizes through multiple mechanisms:

| Mechanism | What Adapts | Data Volume Needed | Update Frequency |
|-----------|------------|-------------------|-----------------|
| **Causal graph parameters** | Elasticities, effect sizes | 30+ observations per relationship | After each new observation batch |
| **Embedding vectors** | Entity similarity space | 100+ entities | After each normalization run |
| **Decision preference** | Which decisions the owner values | 10+ feedback events | After each feedback event |
| **Small LM prompt** | Few-shot examples from past decisions | N/A (prompt engineering) | Weekly (batch analyze feedback) |
| **Tier routing thresholds** | When to use deep vs. fast path | 50+ decisions | Monthly |

### 8.2 Cross-Business Learning (Privacy-Preserving)

Cortex learns from all customers collectively *without* sharing raw data:

- **Federated parameter estimation:** Causal model parameters are averaged across businesses in the same vertical (differential privacy ε=1.0)
- **Vertical-specific base models:** Pre-trained on aggregate statistics from 50+ businesses in a vertical, fine-tuned per business
- **Decision pattern library:** Anonymized decision patterns (not data) shared to improve pattern detection
- **Benchmark distributions:** Customers see "your utilization is in the top 20% of dental practices like yours"

---

## 9. AI Stack Choices — Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| **Self-hosted LLM** | Llama 3 70B via vLLM + SGLang backend | Cost control (~$0.03/inference vs $0.10+ for API). Complete data privacy. Low latency on 1-2 A100s. |
| **Small LM** | Llama 3 8B via vLLM | Fast, cheap, sufficient for routine generation. Same infrastructure (vLLM), different model. |
| **Cloud LLM fallback** | GPT-4o (OpenAI API) | For complex reasoning tasks the 70B can't handle. Only when Tier 2 confidence < 60%. |
| **Embedding model** | BGE-M3 (self-hosted via Sentence-Transformers) | State-of-the-art multilingual, multi-vector. Supports dense + sparse + multi-vec. 8192 context length. |
| **Causal inference** | DoWhy + EconML (Python) | Most mature Python causal inference ecosystem. DoWhy for graph handling, EconML for estimation methods. |
| **Statistical analysis** | scipy + statsmodels | Standard, well-tested. No reason to reinvent. |
| **Time series** | statsmodels (ARIMA, ETS) + Prophet for seasonality | Prophet handles multiple seasonalities well (daily, weekly, yearly patterns in SMB data). |
| **Anomaly detection** | Merlion (by Salesforce) | Production-ready time-series anomaly detection with multiple algorithms (Isolation Forest, Random Cut Forest, etc.) |
| **Vector store** | pgvector (PostgreSQL extension) | Avoid separate vector DB ops overhead. 1024-dim with HNSW index. |
| **ML pipeline** | BentoML | Model serving, monitoring, and deployment. Built-in Prometheus metrics and canary deployment. |
| **Feature store** | Feast (optional, v2+) | For training ML models across customers; avoid in v1. |
| **LightGBM** | Decision classifier (pattern → decision type) | Fast to train, interpretable, handles categorical features well. |

### Why self-hosting is critical

1. **Cost at scale:** 1,000 customers × 50 decisions/day × $0.03 = $1,500/day API cost. Self-hosted on 2× A100s: ~$30/hr all-in = $720/day for unlimited inference.
2. **Latency:** Self-hosted vLLM: 50-100ms per call. API: 500-2000ms per call.
3. **Privacy:** SMB data never leaves our infrastructure. Important for healthcare (HIPAA) and financial data.
4. **Customization:** We can fine-tune the model on decision card generation, causal reasoning, and vertical-specific language.