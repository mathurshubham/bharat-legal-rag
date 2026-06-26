---
doc_id: RELEASE_V4_0
effective_date: 2025-11-03
audience: public
visibility: public
version: v4.0
---

# Acme Tasks v4.0 — Release Notes

**Released November 3, 2025**

We're excited to ship Acme Tasks v4.0 — our biggest release since launch. This update brings a fully redesigned project view, two long-awaited enterprise features graduating to general availability, and a keyboard shortcut palette that'll change how you navigate the app. Read on for everything that's new.

---

## Highlights

- **Redesigned project view** — a faster, cleaner way to see and manage your work
- **SAML SSO is now generally available** on the Business and Enterprise plans
- **Audit log is now generally available** on the Business and Enterprise plans
- **Cmd+K shortcut palette** — navigate anywhere in Acme Tasks without touching your mouse
- **Legacy API v1 deprecated** — sunset date is July 1, 2026 (see Breaking Changes)

---

## New Features

### Redesigned Project View

The project view has been rebuilt from the ground up. The new layout puts your tasks, metadata, and activity feed in a single unified canvas, so you spend less time switching between panels and more time getting things done. Key changes include:

- A persistent sidebar for quick access to project settings, members, and filters
- Inline task editing — click any field to edit without opening a detail drawer
- Collapsible section groups with drag-and-drop reordering
- Improved density settings: choose Comfortable, Compact, or Cozy to match your workflow

The redesign is live for all plans, including Free.

### SAML SSO — General Availability

SAML 2.0 single sign-on is now fully available for Business and Enterprise customers. Configure your identity provider once and your team members will authenticate through your existing IdP — no separate Acme Tasks passwords required. Supported protocols include SAML 2.0, OIDC, and Google Workspace.

To set up SAML SSO, go to **Settings → Security → Single Sign-On**. Step-by-step guides for common identity providers are available in the Security section of our help center.

### Audit Log — General Availability

The audit log gives admins a complete, tamper-evident record of activity across your workspace — including member changes, permission updates, project creation and deletion, billing events, and authentication events. Audit log is available on Business and Enterprise plans.

Enterprise customers can also export the full audit log via the API or as a CSV download from the admin dashboard.

### Cmd+K Shortcut Palette

Press **Cmd+K** (Mac) or **Ctrl+K** (Windows/Linux) from anywhere in Acme Tasks to open the command palette. You can:

- Jump to any project, task, or team member by name
- Run common actions (create task, invite member, open settings) without navigating menus
- Search your workspace and filter results by type

The full list of keyboard shortcuts is available in **Settings → Keyboard Shortcuts**, or by pressing **?** anywhere in the app. Keyboard shortcuts are available on Pro, Business, and Enterprise plans.

---

## Improvements

- **Kanban board performance** — boards with more than 500 tasks now load up to 60% faster thanks to virtualized card rendering.
- **Notification preferences** — per-project notification controls are now available at the individual task level, so you can mute noisy threads without turning off all notifications.
- **GitHub integration** — pull request status now syncs in real time rather than on a polling interval, reducing lag from ~5 minutes to under 10 seconds.
- **Figma embeds** — Figma frames embedded in task descriptions now render at full resolution on high-DPI displays.
- **Mobile web** — the project view redesign is fully responsive; the mobile experience has been significantly improved across iOS and Android browsers.
- **API response times** — median API latency has been reduced by approximately 35% following infrastructure upgrades in our `us-east` and `eu-west` regions.

---

## Breaking Changes

### Legacy API v1 Deprecated

API v1 is now deprecated as of November 3, 2025, and **will be permanently shut down on July 1, 2026**.

If your integrations or internal tooling call any `api.acmetasks.com/v1/` endpoints, you'll need to migrate to API v2 before the sunset date. API v2 has been available since v3.0 and offers full feature parity with v1, plus support for webhooks, expanded filtering, and higher rate limits.

**What you should do now:**

1. Review your API usage in **Settings → API → Usage Logs** to identify any active v1 calls.
2. Consult the [API v2 migration guide](#) in our developer docs for a full endpoint mapping.
3. Update your integration credentials — v2 uses Bearer token authentication; v1's API key format is not compatible.

We'll send reminder emails to workspace admins with active v1 traffic at 90 days, 60 days, and 30 days before the July 1, 2026 sunset. If you have questions about the migration, reach out to our support team.

---

## Bug Fixes

- Fixed an issue where task due dates would shift by one day when viewed in time zones west of UTC-5.
- Fixed a race condition that could cause duplicate tasks to be created when submitting quickly via the keyboard.
- Fixed Slack notifications failing silently when a workspace's Slack token was rotated.
- Fixed the project member list not refreshing after removing a member without a page reload.
- Fixed an edge case where the kanban board would display a blank column header after renaming a status.
- Fixed incorrect seat count displayed on the billing page for workspaces mid-cycle after adding members.

---

Questions about anything in this release? Reach out via in-app chat or email us at support@acmetasks.com. We'd love to hear what you think.
