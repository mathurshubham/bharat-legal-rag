---
doc_id: RELEASE_V4_2
effective_date: 2026-05-12
audience: public
visibility: public
version: v4.2
---

# Acme Tasks v4.2 Release Notes

**Released May 12, 2026**

Welcome to Acme Tasks v4.2. This release brings enterprise identity management into beta, a brand-new design integration, and a search experience that's dramatically faster. Here's everything that's new.

---

## Highlights

**SCIM provisioning is now in beta for Enterprise plans.** You can now automate user lifecycle management — provisioning, deprovisioning, and group sync — directly through your identity provider. No more manual seat cleanup or offboarding tickets.

**Figma is now a first-class integration on Pro and Business plans.** Attach Figma frames and files directly to tasks, and see live previews without leaving Acme Tasks.

**Search is 3× faster.** We've rebuilt the search index from the ground up. Results now appear in under 200 ms on average across workspaces of all sizes.

---

## New Features

### SCIM Provisioning (Enterprise — Beta)

Enterprise workspaces can now connect Acme Tasks to any SCIM 2.0-compatible identity provider. Once configured:

- New users added to your IdP are automatically provisioned in Acme Tasks with the correct role.
- Removing a user from your IdP immediately deactivates their Acme Tasks seat.
- Group memberships sync to Acme Tasks teams, keeping permissions consistent without manual intervention.

SCIM provisioning is available today in beta for all Enterprise customers. To enable it, go to **Settings → Security → SCIM Provisioning** and follow the setup guide. Your dedicated Customer Success Manager can walk you through the rollout if you'd like hands-on help.

> **Note:** SCIM provisioning is planned for general availability in Q4 2026. We welcome feedback during the beta period — use the in-app feedback button on the SCIM settings page.

### Figma Integration (Pro and Business)

The Figma integration is available now on Pro ($19/seat) and Business ($49/seat) plans. To connect your Figma workspace:

1. Go to **Settings → Integrations → Figma** and click **Connect**.
2. Authorize Acme Tasks in the Figma OAuth prompt.
3. Paste any Figma file or frame URL into a task description or comment to generate a live embed.

Embeds update automatically when the linked frame changes in Figma, so your team always sees the latest design without re-pasting links. The integration joins the existing Slack and GitHub integrations available on Pro and above.

---

## Improvements

### 3× Faster Search

Search has been completely re-indexed. Key improvements:

- **Average result latency dropped to under 200 ms** across all plan tiers.
- Fuzzy matching now handles typos and partial words more reliably — searching "onbording" will surface "onboarding" tasks correctly.
- Filters (assignee, project, label, due date) now apply in real time as you type rather than after you submit the query.
- Search now covers task comments in addition to titles and descriptions on Business and Enterprise plans.

### Keyboard Shortcut Expansion (Pro and above)

Eight new keyboard shortcuts have been added, including quick-assign (`A`), cycle priority (`P`), and copy task link (`⌘ + Shift + C` / `Ctrl + Shift + C`). Open the shortcut reference any time with `?`.

### Audit Log Performance (Business and Enterprise)

Audit log queries over large date ranges now load up to 40% faster. Export to CSV for date ranges up to one year (Business) or unlimited history (Enterprise) is no longer subject to a timeout on workspaces with more than 10,000 events.

### API Rate Limit Transparency

The API now returns `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers on every response, making it easier to build clients that stay within your plan's limits (300 req/min on Pro, 1,000 on Business, 5,000 on Enterprise).

---

## Bug Fixes

- **Kanban board** — Fixed a drag-and-drop issue where cards occasionally snapped back to their original column after being moved on Firefox 125+.
- **Slack integration** — Resolved a race condition that caused duplicate task-created notifications when a task was created via the API and a Slack workflow simultaneously.
- **Templates** — Fixed a bug where due-date offsets in templates were calculated from the creation timestamp rather than the project start date when using the "relative dates" option.
- **SSO (SAML 2.0)** — Corrected an edge case where users with accented characters in their display name were rejected during SAML assertion validation.
- **Mobile web** — Fixed layout overflow in task detail view on viewports narrower than 375 px.
- **History panel** — On Business plans, the 1-year history cutoff was incorrectly displaying a "history limit reached" banner two weeks early. This is now resolved.

---

Questions about any of these features? Reach out via in-app chat or visit our Help Center. Enterprise customers can contact their dedicated Customer Success Manager directly.
