---
doc_id: DATA_EXPORT
effective_date: 2026-01-20
audience: public
visibility: public
---

# Exporting Your Acme Tasks Data

Whether you need a quick spreadsheet for a stakeholder report or a complete archive for compliance, Acme Tasks gives you several ways to get your data out. This article covers every export method and what to expect from each one.

---

## CSV Export

CSV export is the fastest way to pull task data from a single project into a spreadsheet.

**How to export a project as CSV:**

1. Open the project you want to export.
2. Click the **⋯ More** menu in the top-right corner of the project view.
3. Select **Export → Download as CSV**.
4. The file downloads immediately to your browser.

**What's included in the CSV:**
- Task name, description, and status
- Assignee and due date
- Labels, priority, and custom fields
- Parent task reference (for subtasks)
- Created and last-updated timestamps

**Things to know:**
- CSV export is available on all plans, including Free.
- Each export covers one project at a time. To export multiple projects, repeat the process for each one.
- Attachments and comments are not included in CSV exports. Use the [Full Archive](#full-archive) if you need those.
- Free plan workspaces have 7-day history, so tasks older than that won't appear in the export.

---

## API Export

If you need to automate exports, pull data into a data warehouse, or build a custom integration, the Acme Tasks REST API gives you full programmatic access to your workspace data.

**Getting started:**
1. Go to **Settings → API Tokens** and generate a personal access token.
2. Use the `/projects/{id}/tasks` endpoint to retrieve tasks for a specific project, or `/workspaces/{id}/tasks` for a broader pull.
3. All responses are returned as **JSON**.

**Rate limits by plan:**

| Plan | Requests per minute |
|---|---|
| Free | 30 |
| Pro | 300 |
| Business | 1,000 |
| Enterprise | 5,000 |

If you exceed your plan's rate limit, the API returns a `429 Too Many Requests` response. Build in exponential backoff or request queuing if you're running bulk exports.

**What the API can return:**
- Full task objects including subtasks, comments, attachments (as URLs), and activity history
- Project metadata, members, and custom field schemas
- Audit log entries (Business and Enterprise plans)

Full API reference documentation is available at **developer.acmetasks.io**.

---

## Full Archive

A full account archive packages everything in your workspace — all projects, tasks, comments, attachments, and member data — into a single downloadable file. This is the right option for offboarding, compliance reviews, or long-term backups.

**Who can request an archive:** Workspace admins only.

**How to request:**
1. Go to **Settings → Workspace → Data & Privacy**.
2. Click **Request Full Archive**.
3. Confirm the request. Acme Tasks will begin preparing your archive immediately.
4. You'll receive an email with a secure download link when the archive is ready. **This can take up to 24 hours** depending on workspace size.

**Important retention note:** Download links expire after **7 days**. Save the archive to a secure location as soon as you receive it — expired links cannot be reactivated and you'll need to submit a new request.

The archive is delivered as a `.zip` file containing structured JSON files (see [Data Formats](#data-formats) below) plus an `/attachments` folder with all uploaded files.

---

## Data Formats

Understanding the structure of your exported data makes it easier to work with downstream.

**CSV files** follow a flat, one-row-per-task structure. Column headers are human-readable (e.g., `Task Name`, `Due Date`, `Assignee Email`). Subtasks appear as separate rows with a `Parent Task ID` column linking them to their parent.

**JSON (API and full archive)** uses a nested object model:

```
workspace
  └── projects[]
        └── tasks[]
              ├── subtasks[]
              ├── comments[]
              └── attachments[]
```

All timestamps are in **ISO 8601 UTC** format (`2026-01-20T14:30:00Z`). Custom field values are included as a `custom_fields` array on each task object, with both the field ID and human-readable label.

The full archive JSON schema is versioned. The current schema version is **v4**, matching Acme Tasks v4.2. A `schema_version` key is included at the root of each exported file.

---

## GDPR Data Request

If you're a data subject requesting a copy of your personal data under GDPR (or a similar privacy regulation), you have the right to receive it in a portable, machine-readable format.

**For end users:**
1. Go to **Settings → Privacy → Request My Data**.
2. Submit the request. You'll receive an email with your personal data export within **30 days**, in line with GDPR Article 15 requirements.

The export includes all personal data associated with your account: profile information, tasks assigned to or created by you, comments you've authored, and login/activity history.

**For workspace admins handling a data subject request on behalf of a user:**
Contact our privacy team at **privacy@acmetasks.io** with the subject line `DSR Request – [workspace name]`. Include the user's email address and the nature of the request. We'll coordinate directly with you to fulfill it within the statutory timeframe.

**Data residency:** If your workspace is configured for EU data residency (`eu-west`), all personal data is stored and processed within the EU. You can confirm your workspace's data residency region under **Settings → Workspace → Security**.

For questions about our data processing practices, see the [Acme Tasks Privacy Policy](#) and [Data Processing Agreement](#) (available to Business and Enterprise customers).
