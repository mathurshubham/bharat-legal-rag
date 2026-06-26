---
doc_id: INTEGRATIONS_OVERVIEW
effective_date: 2026-05-01
audience: public
visibility: public
---

# Acme Tasks Integrations Overview

Connect Acme Tasks to the tools your team already uses. Integrations keep your workflow in one place — no more switching tabs to check whether a pull request closed or a design file changed.

---

## Available Integrations

Integrations are available on **Pro and above**. Some integrations require a **Business or Enterprise** plan.

| Integration | Available on | What it does |
|---|---|---|
| Slack | Pro+ | Post task notifications to channels; create tasks from messages |
| GitHub | Pro+ | Link pull requests and commits to tasks; auto-close tasks on merge |
| GitLab | Business+ | Link merge requests and pipelines to tasks |
| Figma | Business+ | Embed live Figma frames directly on task cards |
| Zapier | Business+ | Connect Acme Tasks to 5,000+ apps via no-code automation |
| Webhooks | Pro+ | Send real-time HTTP events to any endpoint you control |

> **On the Free plan?** Upgrade to Pro ($19/month, up to 10 seats) to unlock Slack, GitHub, and webhooks. Head to **Settings → Billing** to upgrade.

---

## Setting Up Slack

The Slack integration posts task activity to any channel and lets your team create tasks without leaving Slack.

### What you'll need
- An Acme Tasks **Pro, Business, or Enterprise** workspace
- Slack workspace admin permission (or permission to add apps)

### Steps

1. In Acme Tasks, go to **Settings → Integrations → Slack** and click **Connect to Slack**.
2. You'll be redirected to Slack's authorization screen. Select the workspace you want to connect and click **Allow**.
3. Back in Acme Tasks, choose which events trigger a notification — for example, *task assigned*, *due date changed*, or *status moved to Done*.
4. Pick a default channel for notifications. You can override this per-project under **Project Settings → Notifications**.
5. Click **Save**. Acme Tasks will post a confirmation message to the channel you chose.

### Creating tasks from Slack

Once connected, use the `/acmetasks` slash command in any channel:

```
/acmetasks create "Fix login timeout bug" --project Backend --assignee @maya
```

The task appears instantly in your Acme Tasks project and a link is posted back to the channel thread.

---

## Setting Up GitHub

Link pull requests, commits, and issues to Acme Tasks cards so your engineering context lives alongside your project work.

### What you'll need
- An Acme Tasks **Pro, Business, or Enterprise** workspace
- GitHub repository admin access

### Steps

1. Go to **Settings → Integrations → GitHub** and click **Connect GitHub**.
2. Authorize the Acme Tasks GitHub App. Choose whether to grant access to all repositories or select specific ones — we recommend selecting specific repos to start.
3. Once authorized, open any task and paste a GitHub pull request or issue URL into the **Linked items** field. Acme Tasks will fetch the current status automatically.
4. Optionally, enable **Auto-close on merge**: when a linked PR merges, the associated task moves to your *Done* column. Toggle this under **Project Settings → GitHub → Auto-close tasks**.

### Referencing tasks from GitHub

Add the task ID (e.g., `ACM-412`) anywhere in a commit message or PR description. Acme Tasks will detect the reference and link the commit or PR to that task automatically.

---

## Webhooks

Webhooks let you push real-time events from Acme Tasks to any URL — your own backend, a logging service, or a custom Slack bot.

### Creating a webhook

1. Go to **Settings → Integrations → Webhooks** and click **New Webhook**.
2. Enter a **Payload URL** — the HTTPS endpoint that will receive events.
3. Choose the events you want to subscribe to (e.g., `task.created`, `task.updated`, `task.completed`, `project.archived`).
4. Click **Save**. Acme Tasks will send a test `ping` event immediately so you can confirm delivery.

### Payload format

Every webhook event is a JSON POST with a consistent envelope:

```json
{
  "event": "task.completed",
  "timestamp": "2026-05-12T14:32:00Z",
  "workspace_id": "ws_abc123",
  "data": { ... }
}
```

### Security

Each webhook includes an `X-Acme-Signature` header — an HMAC-SHA256 signature computed with your webhook secret. Always verify this signature before processing the payload. Your secret is shown once at creation time; rotate it any time under **Webhook Settings → Regenerate Secret**.

### Retry behavior

If your endpoint returns anything other than a `2xx` response, Acme Tasks retries up to **5 times** with exponential backoff over 24 hours. Failed deliveries are logged under **Settings → Integrations → Webhooks → Delivery Log**.

---

## API

Every integration above is built on the same public REST API available to your workspace.

| Plan | API rate limit |
|---|---|
| Free | 30 requests / minute |
| Pro | 300 requests / minute |
| Business | 1,000 requests / minute |
| Enterprise | 5,000 requests / minute |

Generate a personal API token under **Settings → API → New Token**. Tokens are scoped to your user; workspace admins can also create service-account tokens for CI/CD pipelines.

Full API reference — including endpoint docs, code samples, and an interactive playground — is available at **acmetasks.com/docs/api**.

---

**Need help?** Pro and Business customers can reach support via the in-app chat. Enterprise customers have a dedicated Customer Success Manager — reach them directly or open a ticket tagged **Priority**.
