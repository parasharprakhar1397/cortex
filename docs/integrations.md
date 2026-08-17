# Cortex Integration Framework

> *Revision 1 — Founding Systems Architect*
> *For engineers building data connectors*

---

## 1. Integration Strategy: Hybrid Approach

### Decision: Native Connectors + Merge.dev iPaaS + Generic Webhook

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION STRATEGY                        │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ NATIVE           │  │ MERGE.DEV iPaaS  │  │ GENERIC WEBHOOK  │ │
│  │ (5 tools, v1)    │  │ (15+ tools, v1)  │  │ (all tools, v1)  │ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤ │
│  │ Full schema      │  │ 20+ connectors   │  │ Real-time events  │ │
│  │ control          │  │ Unified API      │  │ No schema control │ │
│  │ Custom fields    │  │ OAuth managed    │  │ Must normalize    │ │
│  │ Higher frequency │  │ Rate-limit mgmt  │  │ Webhook only      │ │
│  │ More data        │  │ Schema drift     │  │ Best-effort       │ │
│  │ More effort      │  │ handled          │  │ delivery          │ │
│  │                  │  │ Less control     │  │                   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                     │
│  All three feed into the same: Normalization → Resolution → Store  │
└─────────────────────────────────────────────────────────────────────┘
```

**Why Merge.dev (not building 20 native connectors):**
- Building and maintaining 20+ OAuth integrations is a full-time job for 1-2 engineers
- Every API changes weekly; Merge.dev absorbs that maintenance
- Unified schemas across CRM, accounting, HRIS, ticketing, etc. — saves normalization effort
- Handles: OAuth token refresh, rate limiting, pagination, error handling
- Cost: ~$0.15/connected account/month (acceptable for $500-2,500/mo subscription)

**Why native connectors at all (instead of all Merge.dev):**
- Merge.dev's unified schemas are intentionally generic — they may miss custom fields that hold valuable data
- Some tools (Stripe, Calendly) have deep APIs that Merge.dev doesn't fully expose
- Higher sync frequency for critical financial data
- Control over webhook processing (some tools send webhooks directly, not through Merge)
- Redundancy: if Merge.dev has an outage, native connectors keep working

**Merge.dev API coverage for our key categories:**
- **Accounting:** QuickBooks, Xero, FreshBooks, Wave, Sage, NetSuite
- **CRM:** HubSpot, Salesforce, Zoho, Pipedrive, Close, Attio
- **Ticketing (bookings):** Calendly, Acuity, Square Appointments, Mindbody, Jane App
- **HRIS:** BambooHR, Gusto, Justworks
- **ATS:** Lever, Greenhouse, Ashby

---

## 2. Priority Integrations for v1

### Top 10 (Must-Have Before Launch)

| # | Tool | Category | Connect Method | Justification |
|---|------|----------|---------------|---------------|
| 1 | **Stripe** | Payments | Native + Webhook | Core financial data. Revenue, LTV, payment patterns. Most popular payment processor for SMBs. |
| 2 | **QuickBooks Online** | Accounting | Native + Merge | Complete ledger, P&L, expenses. Accounting data is critical for causal models. Merge falls back for Xero users. |
| 3 | **Calendly** | Booking | Native + Webhook | Scheduling data — utilization, no-show analysis, time gaps. Core operational data. |
| 4 | **HubSpot** | CRM | Native + Merge | Customer pipeline, deal stages, contact enrichment. Most popular SMB CRM. |
| 5 | **Google Analytics 4** | Analytics | Native | Website traffic, conversion data. Needed for marketing ROI models. |
| 6 | **Gmail/Google Workspace** | Communication | OAuth | Future: calendar and email analysis for scheduling patterns (stretch). For v1: only calendar integration. |
| 7 | **Xero** | Accounting | Merge.dev | Second most popular SMB accounting tool. Merge covers it well. |
| 8 | **Square** | Payments + POS | Merge.dev | Common in retail, food service, and service SMBs. |
| 9 | **Meta Ads** | Marketing | Merge.dev | Facebook/Instagram advertising data. Needed for marketing attribution. |
| 10 | **Google Ads** | Marketing | Merge.dev | Search advertising data. Needed for complete marketing ROI picture. |

### Next 5 (v2, First Month After Launch)

| # | Tool | Category | Connect Method | Justification |
|---|------|----------|---------------|---------------|
| 11 | **Mailchimp** | Email Marketing | Merge.dev | Most popular SMB email platform. Needed for engagement analysis. |
| 12 | **Jane App** | Practice Mgmt | Merge.dev | Dominant in allied health (physio, chiro, massage). |
| 13 | **Acuity Scheduling** | Booking | Merge.dev | Popular solo-practitioner booking tool. |
| 14 | **Salesforce** | CRM | Merge.dev | For larger SMBs ($10M+) who use Salesforce. |
| 15 | **Zapier** | Automation (catch-all) | Webhook | Lets users connect any tool via Zapier, even if we don't have a native connector. |

---

## 3. Authentication & Credential Management

### 3.1 OAuth 2.0 Flow (All Tools)

```
                CORTEX                          SAAS TOOL
                  │                                │
                  │  1. Redirect owner to OAuth    │
   Owner ────────►│  consent page                  │
                  │───── Authorization Request ────►│
                  │                                │
                  │◄──── Authorization Code ───────│
                  │                                │
                  │  2. Exchange code for tokens   │
                  │───── Token Request ───────────►│
                  │◄──── Access + Refresh Token ───│
                  │                                │
                  │  3. Store encrypted            │
                  │     (or delegate to Merge)     │
                  │                                │
                  │  4. Use access token for API   │
                  │───── API Request + Token ─────►│
                  │◄──── Data ────────────────────│
```

**For native connectors:** We store tokens encrypted in our `credentials` table. Encrypted at rest with Fernet (symmetric AES-256). Decrypted only in memory for the duration of an API call.

**For Merge.dev connectors:** Merge.dev manages all tokens. We never see them. When an owner connects via Merge, we get back a `linked_account_id` (a Merge reference to the OAuth connection). All subsequent API calls go through Merge's unified API using this ID.

### 3.2 Token Refresh

```python
class TokenManager:
    async def get_valid_token(self, tenant_id: str, tool: str) -> str:
        """Get a valid access token, refreshing if necessary."""

        # Check if we use Merge for this tool
        if self.uses_merge(tool):
            # Merge handles refresh automatically
            return None  # We use linked_account_id instead

        # Native connector token management
        cred = await self.db.fetch_one(
            "SELECT * FROM credentials WHERE tenant_id = :tid AND tool = :tool",
            tid=tenant_id, tool=tool
        )

        if not cred:
            raise CredentialNotFoundError(tenant_id, tool)

        # Check if token is expired
        if cred.expires_at <= utcnow() + timedelta(minutes=5):
            return await self._refresh_token(cred)

        return self._decrypt(cred.access_token_encrypted)

    async def _refresh_token(self, cred: Credential) -> str:
        """Refresh an expired OAuth token."""
        try:
            new_tokens = await self.oauth_client.refresh_token(
                refresh_token=self._decrypt(cred.refresh_token_encrypted),
                client_id=config.OAUTH_CLIENT_IDS[cred.tool],
                client_secret=config.OAUTH_CLIENT_SECRETS[cred.tool],
            )

            # Store new tokens
            await self.db.execute("""
                UPDATE credentials
                SET access_token_encrypted = :access,
                    refresh_token_encrypted = :refresh,
                    expires_at = :expires,
                    updated_at = now()
                WHERE id = :id
            """, id=cred.id,
                access=self._encrypt(new_tokens["access_token"]),
                refresh=self._encrypt(new_tokens.get("refresh_token", cred.refresh_token)),
                expires=utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600))
            )

            return new_tokens["access_token"]

        except Exception as e:
            # Token refresh failed — mark integration as unhealthy
            await self._mark_connection_error(cred.tool, str(e))
            raise TokenRefreshError(f"Failed to refresh {cred.tool} token: {e}")
```

### 3.3 Credential Storage Schema

```sql
CREATE TABLE credentials (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                   TEXT NOT NULL,
    tool                        TEXT NOT NULL,
    integration_type            TEXT NOT NULL,  -- "native" or "merge"
    merge_linked_account_id     TEXT,           -- if using Merge.dev
    access_token_encrypted      TEXT,           -- Fernet-encrypted (NULL for Merge)
    refresh_token_encrypted     TEXT,           -- Fernet-encrypted (NULL for Merge)
    expires_at                  TIMESTAMPTZ,
    scopes                      TEXT[],
    status                      TEXT DEFAULT 'active',
        -- 'active', 'expired', 'revoked', 'error'
    last_error                  TEXT,
    last_successful_sync        TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ DEFAULT now(),
    updated_at                  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(tenant_id, tool)
);
```

---

## 4. Handling API Rate Limits, Pagination, Webhooks

### 4.1 Rate Limit Handling

**Strategy: Token Bucket (per tenant, per tool, per endpoint)**

```python
class RateLimiter:
    def __init__(self):
        self.redis = redis_client

    async def wait_if_needed(self, tenant_id: str, tool: str, endpoint: str):
        """Wait if we're about to hit the rate limit."""
        key = f"rate_limit:{tenant_id}:{tool}:{endpoint}"
        limits = RATE_LIMITS[tool][endpoint]  # e.g., 100 requests per 60 seconds

        # Check current count
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, limits.window_seconds)

        if current > limits.max_requests:
            # Wait until the window resets
            ttl = await self.redis.ttl(key)
            await asyncio.sleep(ttl + 1)
```

**Rate limit table** (known limits for v1 tools):

| Tool | Endpoint | Limit | Window | When We Slow |
|------|----------|-------|--------|-------------|
| Stripe | /v1/charges | 100 read | 1 sec | ~50/sec to be safe |
| Stripe | /v1/invoices | 100 read | 1 sec | ~50/sec |
| QuickBooks | /v3/company/*/query | 1000 | 1 min | ~500/min |
| Calendly | /scheduled_events | 200 | 1 min | ~100/min |
| HubSpot | /crm/v3/objects/contacts | 100 | 10 sec | ~50/10s |
| GA4 | /v1beta/properties/*/runReport | 50 | 1 day (project) | ~25/day |

**Graceful degradation:** When rate-limited, we back off, log, and the Monitoring Agent marks the integration as "degraded — slow sync." Decisions using this data get a `stale_data` flag.

### 4.2 Pagination

All batch syncs use cursor-based pagination (preferred) or offset pagination (fallback):

```python
class Paginator:
    async def paginate(self, tool: str, endpoint: str, fetch_fn, **kwargs):
        """Generic paginator for any API."""
        results = []
        cursor = None
        page_count = 0
        max_pages = kwargs.get("max_pages", 1000)  # safety limit

        while page_count < max_pages:
            page_count += 1

            if cursor and tool in ["stripe", "calendly"]:
                # Cursor-based pagination
                data = await fetch_fn(starting_after=cursor, limit=100)
                items = data["data"]
                cursor = items[-1]["id"] if items else None
            elif cursor and tool in ["hubspot", "quickbooks"]:
                # Offset-based (HubSpot uses offset; QB uses page number)
                data = await fetch_fn(offset=page_count * 100, limit=100)
                items = data.get("results", data.get("data", []))
            else:
                data = await fetch_fn(limit=100)
                items = data.get("data", data.get("results", []))

            if not items:
                break

            results.extend(items)

            # Early exit: no more pages
            if len(items) < 100:
                break

            # Rate limit: small delay between pages
            await asyncio.sleep(0.1)

        return results
```

### 4.3 Webhook Processing

**Architecture:**
```
SaaS Tool → Webhook → FastAPI → Signature Validation →
Deduplication (Redis idempotency) → NATS Event →
Celery Task → Normalize → Store
```

**Webhook registration:**
- During integration setup, we register a webhook URL at the SaaS tool
- URL format: `https://api.cortex.dev/webhooks/v1/{tool}`
- Each tool has a secret signing key stored in our credentials table

**Signature validation:**

```python
async def validate_stripe_webhook(request: Request, payload: bytes, sig_header: str):
    """Validate Stripe webhook signature."""
    try:
        stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=config.STRIPE_WEBHOOK_SECRET
        )
        return True
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
```

**Idempotency/Deduplication:**

```python
async def deduplicate(event_key: str) -> bool:
    """Return True if this event was already processed."""
    key = f"webhook_idempotency:{event_key}"
    if await redis.setnx(key, "1"):
        # First time seeing this event — set TTL
        await redis.expire(key, 86400)  # 24 hours
        return False  # Not a duplicate
    return True  # Duplicate
```

**Webhook event types we handle:**

| Tool | Webhook Events | Action |
|------|---------------|--------|
| Stripe | `invoice.paid`, `invoice.payment_failed`, `charge.refunded`, `customer.subscription.*` | Immediate metric update, anomaly check |
| Calendly | `invitee.created`, `invitee.canceled`, `invitee.no_show` | Real-time booking status update |
| QuickBooks | None (no webhooks for QuickBooks Online webhook is limited) | Batch sync only |
| HubSpot | `contact.creation`, `deal.update`, `contact.privacy_deletion` | Real-time CRM updates |

---

## 5. Schema Mapping: Unified Model Per Category

Each tool category has a schema mapper that converts tool-specific API responses to Cortex's unified model.

### 5.1 Payment/Category Mapper

| Unified Field | Stripe | Square | Merge.dev (Payments) |
|--------------|--------|--------|---------------------|
| `amount` | `amount / 100` | `amount_money.amount / 100` | `amount` |
| `currency` | `currency` | `amount_money.currency` | `currency` |
| `status` | `status` (succeeded/pending/failed) | `status` (completed/pending/refunded) | `status` |
| `customer_ref` | `customer` (cus_*) | `customer_id` | `contact.id` |
| `paid_at` | `created` (unix timestamp) | `created_at` (ISO8601) | `paid_at` |
| `payment_method` | `payment_method_details.type` | `card_details.card_type` | N/A |

### 5.2 Accounting/Invoicing Mapper

| Unified Field | QuickBooks | Xero (via Merge) | Merge.dev (Accounting) |
|--------------|------------|-------------------|----------------------|
| `invoice_id` | `Id` | `InvoiceID` | `id` |
| `amount` | `TotalAmt` | `Total` | `total` |
| `status` | Map from `DocStatus` | Map from `Status` | `status` |
| `issue_date` | `MetaData.CreateTime` | `Date` | `issue_date` |
| `due_date` | `DueDate` | `DueDate` | `due_date` |
| `customer_ref` | `CustomerRef.value` | `Contact.ContactID` | `contact.id` |
| `line_items` | `Line[]` | `LineItems[]` | `line_items` |

### 5.3 Booking/Scheduling Mapper

| Unified Field | Calendly | Acuity (via Merge) | Merge.dev (Ticketing) |
|--------------|----------|---------------------|----------------------|
| `start_time` | `start_time` | `datetime` | `start_time` |
| `end_time` | `end_time` | `end_datetime` | `end_time` |
| `status` | `status` (active/canceled) | `canceled` (bool) | `status` |
| `customer` | `email` from `invitee` | `email` from `client` | `contact.email` |
| `cancellation_reason` | `cancellation.reason` | (in custom fields) | N/A |
| `service_name` | `event_type.name` | `appointment_type` | `ticket.title` |

### 5.4 CRM Mapper

| Unified Field | HubSpot | Salesforce (via Merge) | Merge.dev (CRM) |
|--------------|---------|------------------------|-----------------|
| `name` | `properties.firstname + lastname` | `Name` | `first_name + last_name` |
| `email` | `properties.email` | `Email__c` or `Email` | `email_addresses` |
| `phone` | `properties.phone` | `Phone` | `phone_numbers` |
| `company` | `properties.company` | `Account.Name` | `company` |
| `lifecycle_stage` | `properties.lifecyclestage` | `StageName` | `status` |
| `owner` | `properties.hubspot_owner_id` | `OwnerId` | `owner` |

### 5.5 Analytics Mapper

| Unified Field | GA4 | Merge.dev (Analytics) |
|--------------|-----|----------------------|
| `date` | `dimensionValues[date]` | `date` |
| `sessions` | `metricValues[sessions]` | `sessions` |
| `pageviews` | `metricValues[totalUsers]` | `page_views` |
| `conversions` | `metricValues[conversions]` or `keyEvents` | `conversions` |
| `revenue` | `metricValues[totalRevenue]` | `revenue` |
| `source` | `dimensionValues[sessionSource]` | `source` |

### 5.6 Marketing Mapper

| Unified Field | Meta Ads | Google Ads | Merge.dev (Marketing) |
|--------------|----------|------------|----------------------|
| `campaign_name` | `campaign_name` | `campaign.name` | `campaign.name` |
| `spend` | `spend` | `cost_micros / 1e6` | `spend` |
| `impressions` | `impressions` | `impressions` | `impressions` |
| `clicks` | `clicks` | `clicks` | `clicks` |
| `conversions` | `actions[offsite_conversion.fb_pixel_purchase]` | `conversions` | `conversions` |

---

## 6. Fallback & Error Handling

### 6.1 Integration Health States

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│   HEALTHY  │────►│  DEGRADED  │────►│    DOWN    │
│            │     │            │     │            │
│ • Synced   │     │ • Slow     │     │ • Auth     │
│   recently │     │   sync     │     │   failed   │
│ • No errors│     │ • Partial  │     │ • API down │
│            │     │   data     │     │ • Removed  │
│            │     │ • Stale    │     │   by owner │
└────────────┘     └────────────┘     └────────────┘
       ▲                 │                  │
       │                 │                  │
       └─────────────────┴──────────────────┘
                  Auto-recovery
```

### 6.2 Degradation Responses

| State | Decision Impact | Owner Notification |
|-------|----------------|-------------------|
| **HEALTHY** | Full confidence | None |
| **DEGRADED** (stale < 24h) | Confidence reduced 20% | Subtle badge: "Data syncing slowly" |
| **DEGRADED** (stale > 24h) | Decisions excluded | Alert: "We haven't received data from QuickBooks in 2 days. Check your connection." |
| **DOWN** | All decisions using this tool suppressed | Critical alert: "QuickBooks connection failed. Reconnect to restore your full insights." |

### 6.3 Auto-Healing

```python
class IntegrationHealthManager:
    async def check_and_heal(self, tenant_id: str, tool: str):
        """Check integration health and attempt to heal."""
        cred = await self.get_credentials(tenant_id, tool)

        if cred.status != "healthy":
            # Attempt auto-heal
            if cred.last_error_type == "rate_limit":
                await self.schedule_retry_with_backoff(cred, delay=30)
            elif cred.last_error_type == "token_expired":
                try:
                    await self.refresh_token(tenant_id, tool)
                    await self.set_healthy(tenant_id, tool)
                except TokenRefreshError:
                    # Can't auto-heal — needs owner intervention
                    await self.set_status(tenant_id, tool, "down")
                    await self.notify_owner(tenant_id, tool,
                        "Your QuickBooks connection expired. Please reconnect.")
            elif cred.last_error_type == "api_error":
                # Transient — retry with exponential backoff
                retry_count = cred.error_retry_count or 0
                delay = min(2 ** retry_count * 60, 3600)  # 1min, 2min, 4min... up to 1h
                await self.schedule_retry(cred, delay=delay)
```

### 6.4 Data Freshness Impact on Decisions

```python
def compute_decision_confidence(
    base_confidence: float,
    data_freshness: dict[str, timedelta],  # tool_name → age
) -> float:
    """Reduce confidence based on data staleness."""
    penalty = 0.0

    for tool, age in data_freshness.items():
        if age > timedelta(hours=24):
            penalty += 0.15  # -15% per stale tool
        elif age > timedelta(hours=12):
            penalty += 0.10
        elif age > timedelta(hours=6):
            penalty += 0.05

    return max(base_confidence - penalty, 0.4)  # Never below 40%
```

---

## 7. Integration Configuration UI

### Setup Wizard Screens

**Screen: Connected Tools**
```
┌─────────────────────────────────────────────────────────┐
│  Connected Tools                    [+ Add Integration] │
│                                                         │
│  ✅ Stripe          ● Connected       Last sync: 2m ago │
│  ✅ QuickBooks      ● Connected       Last sync: 15m ago│
│  ✅ Calendly        ● Connected       Last sync: 1m ago │
│  ⚠️ HubSpot         ○ Stale data      Last sync: 28h ago│
│     [Reconnect]                                          │
│  ❌ Google Ads      ○ Disconnected    [Connect]          │
│                                                         │
│  Data Quality: 87%                                       │
│  "HubSpot data is stale — reconnect for best insights." │
└─────────────────────────────────────────────────────────┘
```

**Screen: Connect New Tool**
```
┌─────────────────────────────────────────────────────────┐
│  Connect your tools                                     │
│                                                         │
│  Based on your business (Dental Practice):              │
│                                                         │
│  Essential:                                             │
│  [Connect] Stripe          [Connect] QuickBooks         │
│  [Connect] Calendly        [Connect] HubSpot            │
│                                                         │
│  Recommended:                                            │
│  [Connect] Google Analytics  [Connect] Google Ads       │
│  [Connect] Meta Ads         [Connect] Mailchimp         │
│                                                         │
│  All Integrations (24 available):                       │
│  [Search...]                                    [View] │
│                                                         │
│  Connecting: We'll keep your data up-to-date and secure.│
│  Cortex never shares your data with other businesses.   │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Integration Testing & Monitoring

### 8.1 Integration Test Suite

Each connector must pass:

1. **Auth test:** Can we obtain and refresh tokens?
2. **Schema test:** Does the API response match our expected schema? (run monthly)
3. **Pagination test:** Can we fetch 10,000+ records?
4. **Rate limit test:** Does our limiter prevent 429s?
5. **Webhook test:** Can we receive, validate, and process webhooks?
6. **Error recovery test:** Can we survive a 500 error and recover?

### 8.2 Metrics

| Metric | Measures | Alert |
|--------|----------|-------|
| `integration.{tool}.sync_lag` | Time since last successful sync | > 2h for critical tools, > 12h for others |
| `integration.{tool}.error_rate` | % of API calls that error | > 5% |
| `integration.{tool}.data_volume` | Records synced per hour | Drop > 80% = likely schema change |
| `integration.{tool}.rate_limit_hits` | Times we hit rate limits | > 10/day = adjust limiter |
| `integration.{tool}.token_refresh_count` | How often tokens refresh | Expected: ~1/60min. If > 5/day, investigate |