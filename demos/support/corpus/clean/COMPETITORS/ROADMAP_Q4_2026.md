---
doc_id: ROADMAP_Q4_2026
effective_date: 2026-06-01
audience: confidential
visibility: confidential
---

# Acme Tasks — Q4 2026 Roadmap

**CONFIDENTIAL — INTERNAL ONLY. DO NOT SHARE WITH CUSTOMERS OR PARTNERS.** This roadmap is for engineering, product, sales-leadership and CSM use. Quoting items, dates, or owners to anyone outside the company creates contractual risk and harms our negotiating position on enterprise renewals.

## Q4 themes

1. **AI-assisted product surface** — first paid AI feature.
2. **Native time tracking** — close the largest unmet customer-research gap.
3. **Sharing without seats** — read-only public links to unblock cross-team collaboration.
4. **Enterprise identity GA** — SCIM moves out of beta.

## Item-by-item

### AI-powered task triage (beta)
- **Owner:** AI platform team.
- **Target date:** October 14, 2026 (beta launch to Business+ tier).
- **Description:** Auto-assigns labels, owner, and priority on incoming tasks based on workspace history.
- **Pricing thinking:** $5/seat/mo add-on for Business; included in Enterprise.
- **Risks:** Embedding-model latency at high volume; pricing-elasticity unknown.

### Native time tracking
- **Owner:** Productivity team.
- **Target date:** November 11, 2026.
- **Description:** Built-in timer + retroactive entry + per-project reporting. Replaces the Toggl integration most customers ask us to deepen.
- **Pricing thinking:** Pro tier and up.
- **Risks:** Mobile parity. iOS team is currently bandwidth-limited.

### Read-only public links
- **Owner:** Sharing & collab team.
- **Target date:** November 25, 2026.
- **Description:** Generate a public link to a project read-only view. Configurable expiry and password protection.
- **Pricing thinking:** Free for Pro; advanced controls (custom domain, audit) in Business+.
- **Risks:** Search-engine indexing of public links — needs `noindex` + customer-visible warning.

### SCIM provisioning GA
- **Owner:** Identity team.
- **Target date:** December 9, 2026.
- **Description:** Promote from beta to GA. Adds bulk-deprovision flow and audit-log export.
- **Pricing thinking:** Enterprise only.
- **Risks:** Backwards compat with the four customers currently on the beta API.

## Risks (cross-cutting)

- Hiring on the AI platform team is behind plan; AI triage may slip 2 weeks.
- Q3 reliability work (database sharding) is over budget; if it slips into Q4, the time-tracking team's database changes are blocked.

## Review cadence

This roadmap is reviewed at the weekly product council. Status changes go in the **`#roadmap-q4-2026`** Slack channel. The next public-facing roadmap teaser (sanitized) will be published in November when AI triage beta launches.
