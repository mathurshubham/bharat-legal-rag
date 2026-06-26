---
doc_id: API_RATE_LIMITS
effective_date: 2026-04-22
audience: public
visibility: public
---

# Acme Tasks API Rate Limits

Every request your integration makes to the Acme Tasks API counts against a per-minute rate limit tied to your workspace's plan. Understanding how limits work — and how to handle them gracefully — keeps your integration running smoothly and your users happy.

## Limits by Plan

Rate limits are measured on a rolling 60-second window, per workspace.

| Plan | Requests per minute |
|---|---|
| Free | 30 |
| Pro | 300 |
| Business | 1,000 |
| Enterprise | 5,000 |

A few things worth knowing:

- **Limits are workspace-wide.** All API tokens and OAuth apps sharing a workspace draw from the same bucket. If you have multiple integrations running in parallel, their requests add up.
- **The clock is rolling, not fixed.** The window slides continuously rather than resetting on the minute boundary, so bursts are smoothed out more fairly.
- **Upgrading takes effect immediately.** If you upgrade your plan mid-billing cycle, your new rate limit applies to the next request — no restart or re-authentication needed.

## Burst Behavior

To accommodate short-lived spikes — a webhook fan-out, a bulk import, a dashboard that fires several requests on load — Acme Tasks allows a **2× burst** above your plan limit for up to **10 seconds**.

For example, a Pro workspace normally capped at 300 req/min can send up to 600 requests in a 10-second window before the standard limit kicks back in. Once the burst window closes, the rolling-minute limit resumes as normal.

Burst capacity is designed for genuine spikes, not sustained high-volume traffic. Consistently hitting the burst ceiling is a signal that your integration would benefit from either request batching or a plan upgrade.

## Rate Limit Headers

Every API response includes three headers that tell you exactly where you stand:

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Your plan's maximum requests per minute |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Unix timestamp (UTC) when the window resets |

Reading these headers proactively is the most reliable way to avoid hitting a limit in the first place. A well-behaved client checks `X-RateLimit-Remaining` before each request and slows down as it approaches zero, rather than waiting for a `429` to signal a problem.

A typical response header set might look like this:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 47
X-RateLimit-Reset: 1745318460
```

## Handling 429 Responses

When you exceed your rate limit, the API returns an **HTTP 429 Too Many Requests** response. The response includes a `Retry-After` header specifying the number of seconds to wait before retrying:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
```

**Best practices for handling 429s:**

1. **Respect `Retry-After` exactly.** Don't retry sooner — the window won't have reset and you'll receive another 429.
2. **Implement exponential backoff with jitter.** If you receive consecutive 429s (which can happen if multiple workers are retrying simultaneously), add a small random delay on top of the `Retry-After` value to spread out the retry storm.
3. **Queue, don't drop.** For write operations especially, treat a 429 as a pause signal rather than a failure. Hold the request in a queue and replay it after the wait period.
4. **Alert on sustained 429 rates.** An occasional 429 is normal. If more than a small percentage of your requests are returning 429s over a sustained period, your integration's request pattern needs attention — or your plan limit needs to grow.

A minimal retry loop in pseudocode:

```
response = api.request(...)
if response.status == 429:
    wait(response.headers["Retry-After"])
    response = api.request(...)  # retry once
```

## Requesting Higher Limits

If your use case consistently requires more throughput than your current plan provides, you have a couple of options:

**Upgrade your plan.** Moving from Pro to Business raises your limit from 300 to 1,000 req/min; moving to Enterprise raises it to 5,000 req/min. Upgrades take effect immediately. See the [pricing page](#) for a full plan comparison.

**Enterprise custom limits.** Enterprise workspaces can discuss custom rate limit arrangements with their dedicated Customer Success Manager. If you're already on Enterprise and 5,000 req/min isn't enough for your workload, reach out to your CSM directly.

**Optimize your integration first.** Before upgrading solely for rate limit headroom, it's worth reviewing whether your integration can reduce request volume through batching (combining multiple updates into one call), caching (storing responses locally for data that doesn't change frequently), or webhooks (receiving push notifications instead of polling). These changes often resolve limit pressure without any plan change.

To get in touch about Enterprise limits or to discuss your integration's needs, contact [support@acmetasks.com](#) or reach out through the in-app chat.
