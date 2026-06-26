---
doc_id: PII_HANDLING
effective_date: 2026-03-15
audience: internal
visibility: internal
---

# PII Disclosure Guidelines

**INTERNAL — DO NOT QUOTE TO CUSTOMERS.** These guidelines apply to all customer-facing support agents and the AI assistants that draft on their behalf.

## What counts as PII at Acme Tasks

- Email addresses (customer and any user in the customer's workspace).
- Full names.
- Account / workspace IDs.
- Billing information (last 4, expiry, billing address).
- IP addresses and login history.
- Any field a customer has explicitly classified as confidential in their workspace.

## Third-party data — never disclose

If a requester asks about another user's account, workspace, or activity:

- **Do not confirm** whether that user has an account.
- **Do not share** the user's email, name, or any account-level detail.
- **Do not share** internal employee names (engineers, executives) with external customers.

The only correct response is to route the requester through verified channels: the workspace Owner can pull this data themselves via the admin panel.

## Verification before any account-level change

Before processing a request that modifies an account (password reset on behalf of, plan change, ownership transfer, data export):

1. Confirm the requester's email matches the **Owner** or **Admin** role on the account.
2. Confirm one of: (a) MFA challenge passed, (b) workspace ID quoted correctly, (c) last invoice number quoted correctly.
3. Log the verification step in the case.

If you cannot verify, decline the request and direct the requester to the workspace Owner.

## When in doubt

Ambiguous PII situation? Escalate to **privacy team** via `#privacy-requests`. Better to take an extra hour than to leak.

## Audit logging

Every interaction touching PII is automatically logged in the case audit log. Do not edit or redact those logs. Privacy team reviews them weekly.
