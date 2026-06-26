---
doc_id: ESCALATION_MATRIX
effective_date: 2026-02-01
audience: internal
visibility: internal
---

# Support Escalation Matrix

**INTERNAL — DO NOT QUOTE TO CUSTOMERS.** This document defines who owns each class of escalation. When you escalate, you remain the case owner until acknowledged by the receiving team.

## Trigger → team

| Trigger | Route to | Response SLA | Channel |
|---|---|---|---|
| Legal threat / lawyer mention | **legal-ops**    | 15 min | `#legal-ops-escalations` |
| Billing dispute over $200     | **billing-lead** | 1 hr   | `#billing-leads` |
| Suspected fraud / compromised account | **trust-and-safety** | Immediate | PagerDuty `tns-oncall` |
| P1 outage report from customer | **SRE oncall**  | Immediate | PagerDuty `sre-oncall` |
| PII / GDPR / DPA request      | **privacy team** | 24 hr  | `#privacy-requests` |
| Press / analyst contact       | **comms**        | Same day | `#comms-inbound` |
| Acquisition / partnership ask | **bizdev**       | Same day | `#bizdev-inbound` |

## Response SLAs

Response SLAs above are **acknowledgement** times (a human responds and takes ownership), not resolution times.

## Escalation channels

- **Slack:** the channel above for non-urgent escalations.
- **PagerDuty:** for legal threats, P1 outages, and fraud — page immediately, do not wait for Slack.
- **Phone:** for legal threats that name a specific lawsuit or court — call legal-ops directly via the contact list below.

## Contact list

See the pinned post in `#support-leads-internal` for the current on-call contact list. Names change quarterly; do not memorize them.

## Sample escalation message

> P1 outage reported by Acme Tasks customer `acme-corp-prod`. They report total inability to log in since 14:22 UTC. CSM is Diane (paged). No internal incident open yet. Case ID: `SUP-48119`. Paging SRE-oncall now.

## What NOT to do

- Never share the matrix or response SLAs with the customer.
- Never tell the customer the escalation channel (Slack / PagerDuty) — those are internal.
- Never name the specific engineer / lawyer / SRE you've paged.

Use the customer-facing version: "I've routed this to our [billing team / security team / engineering team]; they'll respond within [response window]."
