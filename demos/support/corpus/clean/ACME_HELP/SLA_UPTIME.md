---
doc_id: SLA_UPTIME
effective_date: 2026-01-01
audience: public
visibility: public
---

# Service Level Agreement

This Service Level Agreement (SLA) applies to all paid Acme Tasks plans. Enterprise customers should also review the **Enterprise SLA Addendum** which supplements (and where it conflicts, supersedes) this document for their accounts.

## Uptime commitment

We commit to **99.9% monthly uptime** for the Acme Tasks service (the web application at `app.acmetasks.com` and the public API at `api.acmetasks.com`).

## Credit ladder

If monthly uptime falls below 99.9%, eligible customers receive a service credit on the next invoice:

| Monthly uptime | Service credit |
|---|---|
| 99.0% – 99.9%  | 5%  |
| 98.0% – 99.0%  | 10% |
| Below 98.0%    | 25% |

Service credits are capped at one month of fees per incident.

## How we measure uptime

- Uptime is measured at **1-minute intervals** against `api.acmetasks.com`.
- A "minute of downtime" is any minute in which two or more consecutive probes fail.
- Public status page: **status.acmetasks.com**.

## Exclusions

The following are excluded from the uptime calculation:

- **Scheduled maintenance** (announced ≥72 hours in advance, max 4 hours/month).
- **Force majeure** (natural disasters, network-layer outages outside our control).
- **Customer-side issues** (misconfigured firewalls, expired API keys).
- **Beta features** explicitly labeled as beta.

## How to request a credit

Email **billing@acmetasks.com** within 30 days of the affected period. Include:

- Your workspace ID
- Affected dates and times (UTC)
- A brief description of impact

Credits are applied to your next invoice within one billing cycle of approval.
