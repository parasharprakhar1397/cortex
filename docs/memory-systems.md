# Cortex Memory & State Systems

> *Revision 1 — Founding Systems Architect*
> *For engineers building the learning and persistence layer*

---

## 1. What Does Cortex Remember?

Cortex maintains multiple categories of memory about each business:

### 1.1 Business Facts (Long-Term, Explicit)

| Memory Type | Example | Storage | Durability |
|-------------|---------|---------|------------|
| Entity data | "Customer Jane Smith, LTV $3,200/mo" | PostgreSQL entities | Permanent (while customer active) |
| Entity relationships | "Jane Smith has invoices 1042, 1043, 1044" | PostgreSQL business_edges | Permanent |
| Metric history | "Revenue was $42K in Mar 2026" | TimescaleDB hypertable | 2 years |
| Integration config | "Stripe connected via OAuth token #abc" | PostgreSQL integration_config | Permanent |
| Causal model parameters | "Own-price elasticity = -0.4" | PostgreSQL causal_params | Permanent (adaptive) |

### 1.2 Decision History (Long-Term, Explicit)

| Memory Type | Example | Storage | Durability |
|-------------|---------|---------|------------|
| Past decisions | "On 2026-03-15, we recommended raising prices 10%" | PostgreSQL decision_log | 2 years |
| Owner feedback | "That decision was useful" | PostgreSQL feedback_log | 2 years |
| Outcome tracking | "Price increase was implemented; actual Δrevenue was +8.2%" | PostgreSQL outcome_log | 2 years |
| Preference patterns | "Owner ignores marketing recommendations, values pricing ones" | Derived → PostgreSQL user_preferences | Permanent |

### 1.3 Learned Patterns (Long-Term, Implicit)

| Memory Type | Example | Storage | Durability |
|-------------|---------|---------|------------|
| Seasonal patterns | "No-show rates peak in January (resolutions fading)" | TimescaleDB seasonality model | Re-computed quarterly |
| Customer segments | "High-value segment: 35-50, married, suburban" | PostgreSQL segment_membership | Re-clustered monthly |
| Event correlations | "Rainy weeks → 12% fewer bookings + 8% more cancellations" | Causal graph | Permanent (Bayesian update) |
| Anomaly baselines | "Normal no-show rate: 7-9% (95% of weeks)" | PostgreSQL anomaly_baselines | Rolling 90-day window |

### 1.4 Per-User Preferences (Long-Term, Explicit)

| Memory Type | Example | Storage | Durability |
|-------------|---------|---------|------------|
| Goals | "Goal: increase profit margin to 25%" | PostgreSQL user_preferences | Until changed |
| Communication preference | "Email daily at 7am, no push notifications on weekends" | PostgreSQL user_preferences | Until changed |
| Decision tastes | "Show me pricing decisions first, staffing second" | Derived from feedback → user_preferences | Adaptive |
| Snoozed topics | "Don't mention Google Ads for 30 days" | PostgreSQL snoozed_topics | Temporal (auto-expire) |

---

## 2. Memory Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        MEMORY SYSTEM                             │
│                                                                  │
│                         ┌──────────────┐                        │
│                         │  Working     │                        │
│                         │  Memory      │                        │
│                         │  (Redis)     │                        │
│                         │  TTL: 30min  │                        │
│                         │              │                        │
│                         │ • Current    │                        │
│                         │   thread     │                        │
│                         │ • Session    │                        │
│                         │   state      │                        │
│                         │ • Tool cache │                        │
│                         └──────┬───────┘                        │
│                                │                                 │
│                                ▼                                 │
│     ┌────────────────────────────────────────────┐              │
│     │            POSTGRESQL (principal store)    │              │
│     │                                            │              │
│     │  ┌──────────────┐  ┌───────────────────┐  │              │
│     │  │ Entity Memory │  │ Episodic Memory  │  │              │
│     │  │ (facts)       │  │ (decisions +      │  │              │
│     │  │               │  │  outcomes)        │  │              │
│     │  │ • Customers   │  │                   │  │              │
│     │  │ • Invoices    │  │ • Decision cards  │  │              │
│     │  │ • Bookings    │  │ • Owner feedback  │  │              │
│     │  │ • Services    │  │ • Outcome metrics │  │              │
│     │  │ • Employees   │  │ • Simulation      │  │              │
│     │  │ • Campaigns   │  │   history         │  │              │
│     │  └──────────────┘  └───────────────────┘  │              │
│     │                                            │              │
│     │  ┌──────────────┐  ┌───────────────────┐  │              │
│     │  │ Model Memory  │  │ Procedural Memory│  │              │
│     │  │ (parameters)  │  │ (patterns)       │  │              │
│     │  │               │  │                   │  │              │
│     │  │ • Causal graph│  │ • Seasonal        │  │              │
│     │  │ • Elasticities│  │   decomposition   │  │              │
│     │  │ • Segment     │  │ • Anomaly         │  │              │
│     │  │   definitions │  │   thresholds      │  │              │
│     │  │ • Calibration  │  │ • Clustering      │  │              │
│     │  │   params      │  │   centroids       │  │              │
│     │  └──────────────┘  └───────────────────┘  │              │
│     └────────────────────────────────────────────┘              │
│                                │                                 │
│                                ▼                                 │
│     ┌────────────────────────────────────────────┐              │
│     │            VECTOR STORE (pgvector)         │              │
│     │                                            │              │
│     │  • Entity embeddings (customers, services) │              │
│     │  • Decision embeddings (for similarity)    │              │
│     │  • Pattern embeddings (for matching)       │              │
│     └────────────────────────────────────────────┘              │
└──────────────────────────────────────────────────────────────────┘
```

### 2.1 Memory Tiers

| Tier | Storage | Access Speed | Persistence | Capacity |
|------|---------|-------------|-------------|----------|
| **Working Memory** | Redis | < 1ms | Ephemeral (TTL 30min) | Small (per session) |
| **Episodic Memory** | PostgreSQL | 5-50ms | Long-term | Moderate (2y of decisions) |
| **Semantic Memory** | PostgreSQL + pgvector | 10-200ms | Long-term | Large (full entity graph) |
| **Procedural Memory** | PostgreSQL | 5-50ms | Long-term | Small (model params) |

---

## 3. Short-Term vs. Long-Term Memory

### 3.1 Short-Term Memory (Working Memory)

**Storage:** Redis with TTL

**Contents per session:**
- Current conversation context (user query, agent state)
- Intermediate analysis results (tables, stats)
- Tool call cache (same parameters → cached result for 5 min)
- Rate limit counters

**Eviction:** TTL-based. 30 minutes for session state, 5 minutes for cache.

**Why Redis:** Sub-millisecond access, automatic TTL, no schema. Perfect for transient state that doesn't need durability.

### 3.2 Long-Term Memory (Persistent)

**Storage:** PostgreSQL + pgvector

**Contents:**
- Everything described in Section 1 ("What Does Cortex Remember?")
- Historical data that survives restarts and scales with the business

**Why PostgreSQL (not a graph DB like Neo4j):**
- Our entity graph is small per tenant (10K-100K entities) — easy for PostgreSQL with recursive CTEs
- Graph DBs add operational complexity for minimal benefit at this scale
- Recursive CTEs handle 5-level graph traversals in < 50ms (fast enough)
- pgvector keeps vectors in the same system (no cross-DB joins)

---

## 4. Memory Persistence & Improvement Over Time

### 4.1 Continuous Learning Loops

Cortex has three continuous learning loops that run at different cadences:

```
Loop 1: Immediate (per decision)
  Decision → Feedback → Update preference weights
  (PostgreSQL user_preferences table, simple weight update)

Loop 2: Daily
  Batch decisions → Analyze accuracy → Update pattern matching thresholds
  (Celery daily job: compare predicted vs actual outcomes)

Loop 3: Weekly
  Review metrics → Re-cluster segments → Re-estimate elasticities →
  Update causal graph parameters
  (Celery weekly job: full model update)
```

### 4.2 Causal Parameter Adaptation

The most important learning mechanism: Bayesian updating of causal model parameters.

```python
class CausalParameterUpdater:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def update_elasticity(self, metric: str, observed_delta: float, predicted_delta: float):
        """
        Bayesian update of elasticity parameter.
        Prior: from initial calibration (or cross-customer average)
        Likelihood: observed outcome given prediction
        Posterior: updated parameter
        """
        # Load current parameter (prior)
        prior = self.db.query("""
            SELECT mean, std FROM causal_params
            WHERE tenant_id = :tid AND param_name = :metric
        """, tid=self.tenant_id, metric=metric)

        # Or use cross-customer prior if no observation yet
        if not prior:
            prior = {"mean": self.cross_customer_avg(metric), "std": 0.2}

        # Simple conjugate update (Normal-Normal)
        # Prior: N(μ₀, σ₀²)
        # Likelihood: N(observed|θ, σ²)
        # Posterior: N(μ₁, σ₁²)
        mu_0 = prior["mean"]
        sigma_0 = prior["std"]
        sigma_likelihood = 0.1  # observation noise

        n = 1  # single observation (can batch)
        mu_1 = (mu_0 / sigma_0**2 + observed_delta / sigma_likelihood**2) / \
               (1 / sigma_0**2 + 1 / sigma_likelihood**2)
        sigma_1 = 1 / (1 / sigma_0**2 + 1 / sigma_likelihood**2)

        # Store updated parameter
        self.db.execute("""
            INSERT INTO causal_params (tenant_id, param_name, mean, std, n_observations, updated_at)
            VALUES (:tid, :param, :mean, :std, :n, now())
            ON CONFLICT (tenant_id, param_name)
            DO UPDATE SET mean = :mean, std = :std, n_observations = causal_params.n_observations + 1, updated_at = now()
        """, tid=self.tenant_id, param=metric, mean=mu_1, std=sigma_1, n=n)
```

### 4.3 Cross-Customer Priors

New customers start with cross-customer priors for causal parameters:

| Parameter | Prior Mean | Prior Std | Source |
|-----------|-----------|-----------|--------|
| Price elasticity (dental) | -0.35 | 0.15 | Industry research + aggregated Cortex data |
| Price elasticity (home services) | -0.50 | 0.20 | Industry research + aggregated Cortex data |
| No-show rate (dental) | 0.08 | 0.03 | Aggregated Cortex data (all dental practices) |
| No-show rate (salon) | 0.12 | 0.04 | Aggregated Cortex data (all salons) |
| Email open rate (SMB) | 0.22 | 0.05 | Industry benchmarks |
| ... | ... | ... | ... |

These priors shrink the confidence interval by 40%+ in the first 30 days compared to starting from scratch.

---

## 5. Customer-Specific Fine-Tuning vs. Shared Base Model

### Strategy: Shared Base + Per-Customer Light Adaptation

| Approach | What | When | How |
|----------|------|------|-----|
| **Shared base LLM** | Llama 3 70B (same for all customers) | Always | Self-hosted vLLM, no per-customer modifications |
| **Per-customer causal params** | Elasticities, effect sizes, segment definitions | Continuously updated | Bayesian updates in PostgreSQL |
| **Per-customer few-shot prompts** | Customer-specific examples in system prompt | Updated weekly | Include 3-5 recent "useful" decisions and their outcomes |
| **Per-customer decision classifier** | LightGBM trained on customer feedback | Monthly (if enough data) | Small model, < 1MB, stored in PostgreSQL as ONNX |
| **Per-customer embedding drift** | Entity embeddings shift as business changes | Continuously | BGE-M3 is frozen; embedding drift comes from changing entity attributes |

**Why NOT fine-tune the LLM per customer:**
- Cost: Fine-tuning a 70B model costs ~$10K+ per customer
- Complexity: Requires MLOps infra for training, evaluation, deployment, rollback
- Diminishing returns: The causal parameters + few-shot prompts capture 90%+ of the value
- Data volume: Most SMBs generate < 100 feedback events per month — not enough for meaningful fine-tuning
- Latency: Fine-tuned models would need separate deployments or LoRA adapters (complex ops)

**Exception (v3+):** If a customer generates 10,000+ feedback events and wants extreme personalization, we could use LoRA adapters (one per customer, simultaneously served by vLLM). This is a v3 stretch goal.

---

## 6. Memory Schema (PostgreSQL)

### 6.1 Decision & Feedback Tables

```sql
-- Decision history
CREATE TABLE decision_log (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id          TEXT NOT NULL,
    decision_type      TEXT NOT NULL,  -- "pricing", "staffing", etc.
    title              TEXT NOT NULL,
    estimated_roi      NUMERIC(12,2),
    estimated_roi_ci_low NUMERIC(12,2),
    estimated_roi_ci_high NUMERIC(12,2),
    confidence         NUMERIC(3,2),
    status             TEXT NOT NULL DEFAULT 'active',
        -- 'active', 'dismissed', 'snoozed', 'implemented'
    snoozed_until      TIMESTAMPTZ,
    created_at         TIMESTAMPTZ DEFAULT now(),
    delivered_at       TIMESTAMPTZ,
    embedding          vector(1024)     -- decision embedding (for similarity search)
);

-- Feedback events
CREATE TABLE feedback_log (
    id                 BIGSERIAL PRIMARY KEY,
    decision_id        UUID REFERENCES decision_log(id),
    tenant_id          TEXT NOT NULL,
    feedback_type      TEXT NOT NULL,  -- "useful", "not_useful", "already_knew", "snooze", "implemented"
    comment            TEXT,
    created_at         TIMESTAMPTZ DEFAULT now()
);

-- Outcome tracking (actual results vs. predictions)
CREATE TABLE outcome_log (
    id                 BIGSERIAL PRIMARY KEY,
    decision_id        UUID REFERENCES decision_log(id),
    tenant_id          TEXT NOT NULL,
    predicted_roi      NUMERIC(12,2),
    actual_roi         NUMERIC(12,2),       -- NULL until enough time has passed
    predicted_metric   NUMERIC(12,4),
    actual_metric      NUMERIC(12,4),
    evaluation_period  INTERVAL,             -- e.g., '90 days'
    calculated_at      TIMESTAMPTZ DEFAULT now()
);

-- Inference: which patterns perform well for this customer
CREATE TABLE user_preferences (
    tenant_id          TEXT PRIMARY KEY,
    goals              TEXT[],               -- array of goal descriptions
    vertical           TEXT,
    preferred_decisions TEXT[],              -- which decision types get priority
    suppressed_patterns TEXT[],              -- pattern types to ignore
    communication_prefs JSONB,               -- {digest_time, push_enabled, etc.}
    active_snoozes     JSONB,                -- {pattern_type: expires_at}
    updated_at         TIMESTAMPTZ DEFAULT now()
);
```

### 6.2 Causal Model State

```sql
-- Per-tenant causal model parameters
CREATE TABLE causal_params (
    tenant_id          TEXT NOT NULL,
    param_name         TEXT NOT NULL,         -- "price_elasticity", "no_show_baseline", etc.
    mean               NUMERIC(10,4),
    std                NUMERIC(10,4),
    n_observations     INTEGER DEFAULT 0,
    source             TEXT,                  -- "prior", "bayesian_update", "manual"
    updated_at         TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (tenant_id, param_name)
);

-- Per-tenant causal graph structure
CREATE TABLE causal_graph_edges (
    tenant_id          TEXT NOT NULL,
    source_variable    TEXT NOT NULL,
    target_variable    TEXT NOT NULL,
    edge_type          TEXT,                  -- "causal", "confounding", "selection"
    strength           NUMERIC(5,3),          -- 0-1 how confident we are in this edge
    discovered_by      TEXT,                  -- "domain_expert", "algorithm_pc", "algorithm_fci"
    PRIMARY KEY (tenant_id, source_variable, target_variable)
);
```

### 6.3 Pattern Memory

```sql
-- Known patterns (shared across customers, privacy-preserving)
CREATE TABLE pattern_library (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name       TEXT NOT NULL UNIQUE,   -- "no_show_tuesday_spike"
    description        TEXT,
    required_metrics   TEXT[],                 -- which metrics must exist
    detection_query    TEXT,                   -- SQL template for detection
    decision_type      TEXT,                   -- which decision card to generate
    min_confidence     NUMERIC(3,2) DEFAULT 0.7,
    vertical_restrictions TEXT[],              -- which verticals this applies to
    avg_roi            NUMERIC(12,2),          -- cross-customer average
    success_rate       NUMERIC(3,2),           -- % of "useful" feedback
    created_at         TIMESTAMPTZ DEFAULT now(),
    last_updated       TIMESTAMPTZ DEFAULT now()
);
```

---

## 7. Forgetting & Pruning Strategy

### 7.1 Why Forgetting Matters

1. **Data volumes grow:** A busy SMB generates 50K+ metric data points/day
2. **Relevance degrades:** 2-year-old pricing patterns aren't useful today
3. **Model drift:** Old data misleads causal estimates (business conditions change)
4. **Privacy compliance:** Right-to-be-forgotten (CCPA/GDPR) requires deletion capabilities
5. **Cost:** Storage costs; vector indexes slow down as they grow

### 7.2 Pruning Rules

| Data Type | Retention | Pruning Method | Action |
|-----------|-----------|----------------|--------|
| Raw ingested data (S3 Parquet) | 90 days | S3 lifecycle policy | Delete objects older than 90d |
| Time-series raw (1-min granularity) | 90 days | TimescaleDB chunk drop | Drop hypertable chunks older than 90d |
| Time-series hourly aggregates | 1 year | TimescaleDB chunk drop | Keep 90d-1y hourly, drop older |
| Time-series daily aggregates | 2 years | Manual retention policy | Keep for benchmarking |
| Entity data | Duration of customer + 30d | Soft delete | Mark deleted_at, purge after 30d |
| Decision/feedback logs | 2 years | Hard delete | Delete rows older than 2y (anonymize first) |
| Causal parameters | Keep latest only | Overwrite | Bayesian update replaces old params |
| Embedding vectors | Duration of entity | Cascade delete | Delete with entity |
| Working memory (Redis) | 30 minutes | TTL | Automatic |
| Cached simulation results | 24 hours | Redis TTL | Automatic |

### 7.3 Anonymization for Long-Term Learning

Before deletion, sensitive data is anonymized and aggregated for cross-customer learning:

```python
class Anonymizer:
    def anonymize_decision(self, decision: DecisionLog) -> AnonymizedDecision:
        return AnonymizedDecision(
            # Strip all PII, tenant IDs, specific dollar amounts
            decision_type=decision.decision_type,
            pattern_name=decision.pattern_name,
            feedback_positive=decision.feedback_positive,
            # Generalize dollar amounts to ranges
            roi_range=self._range_bucket(decision.estimated_roi),
            # Keep vertical (for benchmark building)
            vertical=decision.vertical,
        )
```

Anonymized data feeds into:
- Cross-customer prior estimates
- Pattern library success rates
- Vertical benchmarks ("what's typical for dental practices?")
- Decision classifier training (shared)

### 7.4 Right to be Forgotten

When a customer deletes their account:

1. Drop their PostgreSQL schema
2. Delete their S3 prefix (raw data, exports)
3. Delete their Redis keys (by pattern `{tenant_id}:*`)
4. Run anonymization on their decision history (extract patterns, strip identity)
5. Log deletion in audit trail (retained for compliance, minimal metadata only)
6. Anonymized data survives (no way to reverse-map to original tenant)

---

## 8. Vector Memory

### 8.1 What Gets Vectors

| Entity | Vector Purpose | Dimension | Index |
|--------|---------------|-----------|-------|
| Customer | Similarity search for churn analysis | 1024 | HNSW (cosine) |
| Service | Price elasticity groups | 1024 | HNSW (cosine) |
| Decision card | Find similar past decisions | 1024 | HNSW (cosine) |
| Pattern | Match patterns to current conditions | 1024 | HNSW (cosine) |
| User query | Semantic matching to patterns | 1024 | HNSW (cosine) |

### 8.2 Vector Index Configuration

```sql
-- HNSW index for fast approximate nearest neighbor search
CREATE INDEX idx_customer_embedding ON customers
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- Parameters:
-- m = 16: good balance of recall vs. memory
-- ef_construction = 200: high-quality index build
-- ef_search = 50: default search quality (adjustable per query)
```

### 8.3 When to Regenerate Embeddings

Embeddings are regenerated when entity attributes change significantly:

- Customer: when LTV changes by > 25%, or new services purchased
- Service: when price changes by > 10%
- Decision: static (generated once)
- Pattern: static (pre-computed)