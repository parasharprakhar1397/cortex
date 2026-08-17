# Cortex Agent Architecture

> *Revision 1 — Founding Systems Architect*
> *For engineers building the AI agent system*

---

## 1. Multi-Agent Design Philosophy

Cortex uses a **supervisor-based multi-agent system** (not a single monolithic agent). This is the right choice because:

1. **Specialization** — Different reasoning tasks need different models, tools, and context windows
2. **Debuggability** — When a decision is wrong, we know which agent failed
3. **Cost control** — Fast/cheap agents handle routine work; expensive/deep agents only invoked when needed
4. **Parallelism** — Multiple agents can work on different aspects of the same business simultaneously
5. **State management** — Each agent's state is scoped and manageable

---

## 2. Agent Roles

```
                        ┌─────────────────────────┐
                        │     SUPERVISOR AGENT    │
                        │   Orchestrates, routes,  │
                        │   manages context window │
                        └──────────┬──────────────┘
                                   │
         ┌─────────────────────────┼──────────────────────────┐
         │                         │                          │
         ▼                         ▼                          ▼
┌─────────────────┐    ┌─────────────────────┐    ┌────────────────────┐
│  MONITORING     │    │    ANALYSIS AGENT    │    │  DECISION AGENT    │
│  AGENT          │    │                      │    │                    │
│  • Watches for  │    │  • Queries business  │    │  • Generates       │
│    anomalies    │───►│    model              │───►│    recommendations │
│  • Checks data  │    │  • Runs statistical  │    │  • Estimates ROI   │
│    freshness    │    │    tests             │    │  • Writes          │
│  • Triggers     │    │  • Detects patterns  │    │    explanations    │
│    analysis     │    │  • Calls causal      │    │  • Ranks decisions │
│  • Scheduled    │    │    inference         │    │    by impact       │
│    runs every   │    │                      │    │                    │
│    15 min       │    │  • Triggered by      │    │  • Triggered by    │
│                 │    │    monitor or        │    │    analysis        │
│                 │    │    scheduled         │    │    completion      │
└─────────────────┘    └──────────────────────┘    └────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │  SIMULATION AGENT    │
                    │                      │
                    │  • Runs Monte Carlo  │
                    │    simulations       │
                    │  • Multi-variable    │
                    │    what-if scenarios │
                    │  • Generates         │
                    │    counterfactuals   │
                    │                      │
                    │  • Triggered by user │
                    │    query or decision │
                    │    agent             │
                    └──────────────────────┘
```

### 2.1 Supervisor Agent

**Role:** Orchestrator, router, and context manager.

**When it runs:** Continuously — listens for events and schedules work.

**Responsibilities:**
- Receive events from Monitoring Agent, user queries, and scheduled timers
- Route each event to the appropriate agent
- Manage the thread-level state per tenant (LangGraph thread)
- Decide when to escalate from Tier 1 (fast) to Tier 2 (deep)
- Handle agent failures (retry, fallback, degradation)
- Compile results into the final decision card structure

**Technology:** LangGraph `StateGraph` with router nodes

```python
class SupervisorState(TypedDict):
    tenant_id: str
    events: list[Event]
    active_agents: dict[str, AgentStatus]
    context: dict  # Tenant's business context, current thread state
    output_queue: list[Decision]

class SupervisorAgent:
    graph: StateGraph

    def __init__(self):
        builder = StateGraph(SupervisorState)

        builder.add_node("router", self.route_event)
        builder.add_node("collect_results", self.collect_results)
        builder.add_node("compile_decision", self.compile_decision)

        builder.add_conditional_edges(
            "router",
            self.select_agent,
            {
                "monitoring": "monitoring_agent",
                "analysis": "analysis_agent",
                "decision": "decision_agent",
                "simulation": "simulation_agent",
                "collect": "collect_results",
            }
        )
        builder.add_edge("collect_results", "compile_decision")
        builder.set_entry_point("router")

    def route_event(self, state: SupervisorState) -> SupervisorState:
        event = state["events"].pop(0)
        state["current_event"] = event
        return state

    def select_agent(self, state: SupervisorState) -> str:
        event = state["current_event"]
        if event.type == "scheduled_monitoring":
            return "monitoring"
        elif event.type == "analysis_complete":
            return "decision"
        elif event.type == "user_simulation":
            return "simulation"
        elif event.type == "user_query":
            return "analysis"  # on-demand analysis
        else:
            return "collect"
```

### 2.2 Monitoring Agent

**Role:** The "eyes" of the system — constantly watches for patterns worth investigating.

**When it runs:** Every 15 minutes (scheduled) and on-demand (webhook-triggered).

**Technology:** Lightweight Python process with scheduled Celery Beat tasks

**Responsibilities:**
1. **Freshness check:** Is every integration reporting data? If not, alert.
2. **Metric shift detection:** Compare recent metrics (last 2 hours) to rolling baseline (last 7 days). If deviation > 2σ, flag.
3. **Anomaly detection:** Use Merlion's Random Cut Forest + Statistical Thresholding to detect point anomalies.
4. **Pattern matching:** Check recent data against known decision patterns (e.g., "no-show spike" pattern, "booking gap" pattern, "revenue plateau" pattern).
5. **Event emission:** Publish `analysis_triggered.{tenant_id}` event to NATS when something interesting is found.

**Tool access:**
- Read-only access to metric_values hypertable
- Read-only access to entity graph
- Read-only access to integration health status

**Output:**
```python
@dataclass
class MonitoringAlert:
    tenant_id: str
    alert_type: str  # "metric_shift", "anomaly", "data_stale", "pattern_match"
    severity: str    # "info", "warning", "critical"
    metric_name: str
    entity_id: UUID | None
    current_value: float
    baseline_value: float
    deviation: float  # in standard deviations
    pattern_name: str | None  # if pattern matched
    raw_data_ref: dict       # pointers to the evidence
    timestamp: datetime
```

### 2.3 Analysis Agent

**Role:** The "brain" — investigates alerts and queries to find root causes.

**When it runs:** Triggered by Monitoring Agent alerts or user queries.

**Technology:** LangGraph agent with tool-use capabilities (ReAct pattern)

**Tools available:**
| Tool | Description | Implementation |
|------|-------------|---------------|
| `query_entity_graph` | Query the business entity graph | SQL via SQLAlchemy, returned as structured data |
| `query_time_series` | Get time-series data for a metric | TimescaleDB query with automatic aggregation |
| `run_statistical_test` | Run t-test, chi-squared, ANOVA, etc. | scipy + statsmodels |
| `run_causal_analysis` | Run causal inference on a hypothesis | DoWhy + EconML |
| `search_entity_vectors` | Semantic similarity search on entities | pgvector cosine similarity |
| `get_entity_details` | Get full details of a specific entity | SQL join across entity tables |
| `get_causal_graph` | Get the current causal graph for this business | Stored model parameters |
| `run_benchmark_comparison` | Compare metric to anonymized peers | Pre-computed benchmark distributions |

**Analysis workflow:**

```
1. Receive alert (e.g., "no-show rate jumped from 8% to 15%")
2. Query time_series for no_show_rate over last 30 days
3. Statistical test: is this significant? (p < 0.01? Yes.)
4. Decompose by dimensions:
   - by_employee: "Hygienist #3 has 22% vs. 5% average"
   - by_day: "Tuesday has 18% vs. 9%"
   - by_service: "Cleaning has 16% vs. 10%"
5. Causal analysis: "Is this due to employee scheduling or patient mix?"
   → Run double-ML: treatment = employee_assignment, outcome = no_show
   → Result: Hygienist #3's patients have higher no-show, controlling for day/patient demographics
6. Output structured analysis
```

**Output:**
```python
@dataclass
class AnalysisResult:
    alert_id: str
    root_cause: str  # "Hygienist #3 Tuesday panel has 3x higher no-show rate"
    confidence: float
    evidence: list[EvidencePiece]  # structured data, charts, stats
    causal_path: list[str]  # ["employee_panel", "scheduling", "no_show"]
    counterfactual: str | None  # "If Hygienist #3's panel were rescheduled, no-show rate would be 9.2%"
    suggested_action: str  # "Reschedule Hygienist #3's patient panel"
    estimated_impact: dict  # {revenue: $X, cost: $Y}
```

### 2.4 Decision Agent

**Role:** Takes analysis results and generates decision cards.

**When it runs:** Triggered by Analysis Agent completion.

**Technology:** LLM (Large — Tier 2) with structured output (Pydantic model)

**Why LLM here and not in analysis?**
- Analysis is quantitative and structured — better done by statistical tools
- Decision generation is qualitative — turning analysis into actionable advice requires natural language, framing, and persuasion

**Workflow:**

```
1. Receive AnalysisResult from Analysis Agent
2. Load business context: goals, past decisions, owner preferences
3. Query past similar decisions and their outcomes (from memory)
4. Generate decision card:
   - Title: "Reschedule Hygienist #3's Tuesday panel to reduce no-shows"
   - ROI estimate: $4,200/mo (from simulation)
   - Confidence: 82% (based on causal model quality)
   - Evidence summary: "We found 23 no-shows in April vs. 11 in March. 18 of 23 were on Tuesday, when Hygienist #3 works."
   - Explanation: "Your no-show rate is 15%. Changing Hygienist #3's schedule would reduce it to ~9%. Here's why..."
   - Action: "Talk to Hygienist #3 about schedule preferences or reassign her panel."
   - Simulation trigger: "See what-if analysis"
5. Rank decision against other pending decisions by ROI
6. Push to decision queue
```

**Output:**
```python
@dataclass
class DecisionCard:
    id: UUID
    tenant_id: str
    title: str
    category: str  # "pricing", "staffing", "marketing", "churn", "cash_flow", "operations"
    estimated_roi: RoiEstimate
    confidence: ConfidenceScore
    analysis_ref: AnalysisResult
    explanation: str  # Natural language with evidence
    action_items: list[str]
    status: str  # "active", "snoozed", "implemented", "dismissed"
    created_at: datetime
    expires_at: datetime  # auto-dismiss if stale
```

### 2.5 Simulation Agent

**Role:** Runs "what-if" scenarios on demand.

**When it runs:** Triggered by user query or Decision Agent request.

**Technology:** Custom Monte Carlo engine + causal graph model

**Simulation process:**
1. Parse the query: "What if I raise prices by 10%?"
2. Map to business model variables: `service.price *= 1.10`
3. Load causal model parameters for this business
4. Configure Monte Carlo (10,000 iterations, 95% CI)
5. Run simulation:
   - For each iteration: sample from posterior distributions, propagate through causal graph, record outcomes
6. Compute outcome distributions: revenue, profit, churn, utilization
7. Generate sensitivity analysis (tornado plot data)
8. Return structured results

**Output:**
```python
@dataclass
class SimulationResult:
    parameters: dict  # What was changed
    outcomes: dict[str, OutcomeDistribution]
    # {
    #   "revenue": OutcomeDistribution(mean=11800, ci_low=4200, ci_high=19100, p_positive=0.94),
    #   "profit":  OutcomeDistribution(mean=8400, ci_low=2100, ci_high=15200, p_positive=0.91),
    #   "churn":   OutcomeDistribution(mean=0.052, ci_low=0.03, ci_high=0.08, p_positive=0.12),
    # }
    sensitivity: dict[str, float]  # Variable importance scores
    key_assumptions: list[str]  # "Demand elasticity holds at 0.4"
    generated_at: datetime
```

---

## 3. Agent Orchestration

### 3.1 Orchestration Pattern: Supervisor + Shared State

```
┌────────────────────────────────────────────────────────────┐
│                    SUPERVISOR                               │
│                                                            │
│  Receives: monitoring alerts, user queries, timers         │
│                                                            │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐ │
│  │ Monitor  │──►│ Analysis │──►│ Decision │──►│ Deliver│ │
│  │ Agent    │   │ Agent    │   │ Agent    │   │ to UI  │ │
│  └──────────┘   └──────────┘   └──────────┘   └────────┘ │
│       │              │              │                      │
│       │              ▼              │                      │
│       │      ┌──────────────┐       │                      │
│       └─────►│ Simulation   │◄──────┘                      │
│              │ Agent        │  (on-demand)                │
│              └──────────────┘                              │
│                                                            │
│  State:                                                     │
│  - Shared Postgres database (entity graph, metrics)        │
│  - LangGraph thread state (per tenant, per conversation)   │
│  - NATS event bus (inter-agent communication)              │
└────────────────────────────────────────────────────────────┘
```

### 3.2 Communication Patterns

| Pattern | Where Used | Mechanism |
|---------|-----------|-----------|
| **Event-driven** | Agent → Supervisor → Agent | NATS publish/subscribe |
| **Direct call** | Supervisor → Agent (function call) | LangGraph node invocation |
| **Shared database** | Agent reads/writes business model | PostgreSQL via SQLAlchemy |
| **Streaming** | Agent → User (real-time progress) | WebSocket via FastAPI |

### 3.3 Scheduling

| Agent | Trigger | Frequency | Notes |
|-------|---------|-----------|-------|
| Monitoring Agent | Scheduled timer | Every 15 min per tenant | Lightweight, fast |
| Analysis Agent | Monitoring alert OR user query | On-demand | Heavy, may take 5-30s |
| Decision Agent | Analysis completion | On-demand | Fast, < 3s |
| Simulation Agent | User query OR decision agent request | On-demand | 5-30s |
| Deep analysis | Weekly review | Every Monday for each tenant | Comprehensive, ~2min |

**Scaling:** With 1,000 tenants, the monitoring agent does 1,000 × 96 = 96,000 checks/day. Each check is a simple DB query + statistical test — lightweight. The Analysis Agent runs ~50-200 times/day per tenant (depends on how many patterns are found).

---

## 4. Tool-Use Framework

### 4.1 How Agents Use Tools

Agents use a **ReAct (Reasoning + Acting)** pattern via LangGraph's tool-calling integration:

```
1. Agent receives input (alert or query)
2. Agent reasons: "I need to check if the no-show rate change is significant"
3. Agent calls tool: run_statistical_test(metric="no_show_rate", period1="last_30d", period2="previous_30d")
4. Tool returns result: p = 0.003, effect_size = 7.2%
5. Agent reasons: "Significant. Now I need to decompose by dimension."
6. Agent calls tool: query_time_series(metric="no_show_rate", group_by="employee", period="last_30d")
7. ...continues until conclusion reached
8. Agent returns structured analysis result
```

### 4.2 Tool Registry

Tools are registered in a central registry with metadata:

```python
class ToolRegistry:
    tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self.tools[tool.name] = tool

    def get_tools_for_agent(self, agent_role: str) -> list[ToolDefinition]:
        return [t for t in self.tools.values() if agent_role in t.allowed_roles]

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: list[ParameterSchema]
    allowed_roles: list[str]  # "monitoring", "analysis", "decision", "simulation"
    cost_tier: str  # "free" (DB query), "cheap" (statistical), "expensive" (causal)
    timeout_seconds: int
    rate_limit: int  # calls per minute per tenant
```

### 4.3 Tool Execution

```python
class ToolExecutor:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.db = DatabaseSession(tenant_id)
        self.causal_engine = CausalEngine(tenant_id)
        self.vector_store = VectorStore(tenant_id)

    async def execute(self, tool_name: str, params: dict) -> ToolResult:
        # Rate limit check
        if not self.rate_limiter.check(tool_name, self.tenant_id):
            return ToolResult(error="Rate limit exceeded", retry_after=60)

        # Execute
        try:
            if tool_name == "query_time_series":
                return await self._query_time_series(**params)
            elif tool_name == "run_causal_analysis":
                return await self._run_causal_analysis(**params)
            # ... etc
        except Exception as e:
            return ToolResult(error=str(e), retryable=True)
```

---

## 5. Agent State Management

### 5.1 State Persistence

**LangGraph thread state** is persisted to PostgreSQL:

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver(
    conn_string=os.environ["DATABASE_URL"],
    # Automatically scopes threads to tenant_id
    namespace="cortex_agent_state"
)

# Usage: each tenant gets its own thread
thread_id = f"{tenant_id}:{conversation_id}"
graph = app.compile(checkpointer=checkpointer)
result = await graph.ainvoke(
    input={"events": [event]},
    config={"configurable": {"thread_id": thread_id}}
)
```

### 5.2 What State Is Stored Per Agent

**Monitoring Agent:**
- Last check timestamp per metric
- Rolling baseline statistics (mean, std, N)
- Known anomalies (dedup key)

**Analysis Agent:**
- Current investigation context (which alert, what hypotheses tested)
- Intermediate results (tables, test outputs)
- Reasoning trace (for explainability)

**Decision Agent:**
- Active decisions (not yet delivered)
- Decision history (for deduplication)
- Owner feedback history (for preference learning)

**Simulation Agent:**
- Running simulation parameters and progress
- Results cache (same simulation = return cached)

---

## 6. Guardrails: Preventing Bad Recommendations

### 6.1 Pre-Generation Guardrails

Applied before any recommendation is generated:

| Guardrail | Check | Action |
|-----------|-------|--------|
| **Data sufficiency** | Is there enough data? (N > 30 observations) | If no, mark as "Emerging" (low confidence) |
| **Statistical significance** | Is the effect p < 0.10? | If no, don't generate a decision card |
| **Effect size** | Is the impact > $500? | If no, suppress (too small to act on) |
| **Causal validity** | Does the causal graph support the intervention? | If no, don't recommend causal action |
| **Simpson's paradox** | Check for confounding variables | If detected, decompose and re-analyze |
| **Freshness** | Is the data < 24h old? | If stale, degrade confidence |
| **Regulatory** | Is the recommendation legal? (e.g., price fixing, discriminatory pricing) | Block and log |

### 6.2 Post-Generation Guardrails

Applied after the decision card is drafted:

| Guardrail | Check | Action |
|-----------|-------|--------|
| **Self-consistency** | Does the LLM-generated explanation match the structured evidence? | Cross-check: extract key claims from text, verify against data. If mismatch, regenerate. |
| **Sensitivity scan** | Would a small change in assumptions flip the recommendation? | Run sensitivity analysis. If unstable, add warning. |
| **Peer comparison** | Is this recommendation outside the range of what similar businesses do? | Flag as "unusual — verify before acting" |
| **Contradiction check** | Does this contradict a previous recommendation? | If yes, explain why conditions changed. |
| **Actionability** | Can the owner actually do this? | If it requires 3 months of engineering, it's not actionable for an SMB. |

### 6.3 Feedback Loop

Every decision card includes feedback buttons. This creates a reinforcement learning signal:

- **"Useful"** → Positive reinforcement. Increase weight of similar patterns.
- **"Not useful"** → Negative reinforcement. Decrease weight. If repeated, suppress that pattern type.
- **"Already knew this"** → Adjustment: the pattern was too obvious. Increase novelty threshold.
- **"Snooze"** → Defer, don't repeat for 30 days.
- **"Implemented"** → Track outcome. After 30-90 days, compare predicted vs. actual outcome. Tune causal model.

---

## 7. Agent Monitoring & Observability

### 7.1 Agent-Specific Metrics

| Metric | What It Measures | Alert |
|--------|-----------------|-------|
| `agent.monitoring.cycle_time` | Time to complete one monitoring pass | > 60s |
| `agent.analysis.tool_call_count` | Number of tool calls per analysis | > 20 (potential infinite loop) |
| `agent.analysis.tool_error_rate` | % of tool calls that fail | > 5% |
| `agent.decision.confidence` | Average confidence of generated decisions | < 0.6 |
| `agent.simulation.latency` | Time to complete a simulation run | > 60s |
| `agent.supervisor.queue_depth` | Number of pending events | > 100 (backpressure) |
| `agent.all.token_usage` | LLM token consumption per tenant per day | > 500K tokens (cost alert) |

### 7.2 Agent Tracing

Every agent step is traced via OpenTelemetry:

```python
from opentelemetry import trace

tracer = trace.get_tracer("cortex.agents")

async def analyze(self, alert: MonitoringAlert) -> AnalysisResult:
    with tracer.start_as_current_span("analysis.run") as span:
        span.set_attribute("tenant_id", alert.tenant_id)
        span.set_attribute("alert_type", alert.alert_type)

        with tracer.start_as_current_span("analysis.tool_call") as tool_span:
            tool_span.set_attribute("tool", "query_time_series")
            result = await self.query_time_series(...)
            tool_span.set_attribute("rows", len(result))

        # ... more spans
```

---

## 8. Agent Scalability

### 8.1 Per-Tenant Isolation

Each tenant gets:
- A separate LangGraph thread (Postgres-backed, isolated state)
- Separate Celery task queue (with priority: paid customers > free)
- Separate rate limits for tool calls
- Separate causal model instance

### 8.2 Worker Scaling

```
Agent Type          Workers   Queue         Priority
─────────────────────────────────────────────────────
Monitoring Agent    2-5       monitoring    Low (batch-friendly)
Analysis Agent      5-20      analysis      Medium (on-demand)
Decision Agent      3-10      decision      High (user-facing)
Simulation Agent    2-5       simulation    Medium (user-triggered)
Supervisor          1-3       supervisor    High (routing)
```

Workers are Celery processes, auto-scaled by queue depth (using Celery's `autoscale` feature or a simple script that checks Redis queue length).

### 8.3 Cost Budgeting

Each tenant has a daily "compute budget" enforced by the Supervisor:

- Essentials tier: 50 analysis calls/day, 10 simulation runs/day, 5K LLM tokens/day
- Professional tier: 200 analysis calls/day, 50 simulation runs/day, 20K LLM tokens/day
- Enterprise tier: Unlimited (with fair-use threshold at 500/100/50K respectively)

When budget is exceeded, the Supervisor queues work for the next day and explains to the owner: "We've reached your daily analysis limit. New insights will be available tomorrow."