---
doc_id: REFUND_POLICY_INTERNAL_V3
effective_date: 2026-01-01
audience: internal
visibility: internal
---

# Refund Discretion — Internal Runbook

**INTERNAL — DO NOT QUOTE TO CUSTOMERS.** This document tells frontline support agents how much latitude they have when authorizing refunds beyond the published policy. The published policy (Refunds v3) is the customer-facing source of truth.

## Authority ladder

| Refund amount (USD) | Authority |
|---|---|
| Up to $500     | **At-agent-discretion** — no approval needed |
| $500 – $2,000  | Requires **billing-lead** approval (Slack: `#billing-leads`, async OK) |
| $2,000 – $10,000 | Requires **director-of-support** approval (sync) |
| Over $10,000   | Requires **VP of Finance** approval (executive escalation) |

## Loyalty bonus

Customers with **more than 24 months tenure** automatically qualify for at-agent-discretion refunds up to **$1,000** (double the standard ceiling). Verify tenure in the admin panel before applying. This bonus stacks with the published policy — you do not need to deny first and then apply discretion.

## When to apply discretion

Default to using discretion when:

- The customer experienced a clear product failure (data loss, outage that affected their work).
- The refund request falls just outside the published 30-day window (treat day 31–45 as discretion territory).
- The refund unblocks a renewal or expansion conversation.

Do not use discretion when:

- The customer is attempting to recover monthly fees (per policy, monthly is non-refundable; do not erode this).
- There is a chargeback or fraud flag on the account.
- The customer has violated our acceptable-use policy.

## Documentation required

For every discretion refund, log in the case:

1. Customer ID and refund amount.
2. Reason code (one of: `product_failure`, `outside_window`, `retention`, `goodwill`).
3. Tenure (months).
4. Approver Slack handle (for any amount above $500).

Audit reviews are run monthly by the billing lead.

## Escalation

If the customer demands more than your authority allows, route to the next tier — do not promise refunds you can't authorize. Use the Support Escalation Matrix for the routing rules.
