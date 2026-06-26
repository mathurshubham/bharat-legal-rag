---
doc_id: RELEASE_V4_1
effective_date: 2026-02-18
audience: public
visibility: public
version: v4.1
---

# Acme Tasks v4.1 Release Notes

**Released February 18, 2026**

We're shipping v4.1 today with a handful of features we know you've been waiting for — GitHub sync, offline support on mobile, and a brand-new template library. No breaking changes, no migrations required. Here's what's new.

## What's New

### GitHub Integration

Pro and Business plans now connect Acme Tasks directly to your GitHub repositories. Once linked, you can:

- **Reference pull requests and issues** from any task — paste a GitHub URL and it auto-previews inline.
- **Sync PR status automatically** — when a pull request moves from open to merged, the linked task updates its status to match.
- **Filter your board by branch or PR state** so engineering teams always know what's blocked on a code review.

To connect a repository, go to **Settings → Integrations → GitHub** and follow the OAuth prompt. You'll need admin access to the repository you're linking.

### Mobile Offline Mode

The Acme Tasks mobile app now works without a network connection. Changes you make offline — creating tasks, editing descriptions, updating statuses — sync automatically the moment your connection is restored.

A small sync indicator in the top bar shows whether you're live or working offline, and a brief confirmation appears once everything has pushed. No data is lost if you close the app before reconnecting.

Offline mode is available on iOS 16+ and Android 12+. It ships enabled by default; no settings change needed.

### Project Templates

Stop rebuilding the same project structure from scratch. v4.1 introduces a template library with ready-made setups for common workflows:

- **Sprint planning** — backlog, in-progress, review, and done columns pre-configured with default labels.
- **Product launch** — phases from discovery through go-live, with milestone tasks included.
- **Bug triage** — severity labels, assignee slots, and a linked GitHub integration hook built in.
- **Onboarding** — a repeatable checklist structure for bringing new team members up to speed.

Templates are available on Pro and above. To use one, click **New Project → Start from template** and pick from the library. You can customize any template before saving — nothing is locked in.

## Fixes and Improvements

- Keyboard shortcuts now work correctly inside task description fields on Firefox.
- The Slack integration no longer sends duplicate notifications when a task is moved between projects.
- Board column drag-and-drop is noticeably smoother on large projects (500+ tasks).
- Date picker on mobile no longer dismisses unexpectedly when rotating the device.

## No Breaking Changes

v4.1 is a fully backward-compatible release. Existing API integrations, webhooks, and workspace configurations continue to work without any changes on your end. The API rate limits remain unchanged across all plans.

---

Questions or feedback? Reach out via **Help → Contact Support** or join the conversation in the Acme Tasks community forum.
