---
doc_id: NOTIFICATIONS
effective_date: 2026-02-01
audience: public
visibility: public
---

# Managing Notification Settings in Acme Tasks

Stay on top of what matters — and tune out what doesn't. Acme Tasks gives you fine-grained control over how and when you're notified, across every channel you use.

## Notification channels

Acme Tasks delivers notifications through four channels. You can enable or disable each one independently in **Settings → Notifications**.

| Channel | Where to find it | Available on |
|---|---|---|
| **In-app** | Bell icon (top-right) | Web, desktop |
| **Email** | Your account email address | All plans |
| **Mobile push** | Acme Tasks mobile app | iOS, Android |
| **Slack** | Connected Slack workspace | Pro and above |

**In-app notifications** appear in real time and are always on by default. A red badge on the bell icon shows your unread count; clicking it opens a feed you can mark as read individually or all at once.

**Email notifications** are sent immediately by default, but you can switch to digest mode (see [Email digest](#email-digest) below).

**Mobile push** requires the Acme Tasks mobile app and notification permissions granted at the OS level. If you've installed the app but aren't receiving pushes, go to **Mobile app → Settings → Push notifications** and confirm the toggle is on, then check your device's notification settings for Acme Tasks.

**Slack notifications** are available on the Pro plan ($19/seat/month) and above. See [Slack integration](#slack-integration) for setup steps.

## Per-project preferences

Global notification settings are a starting point — you can override them for any individual project.

### Setting global defaults

Go to **Settings → Notifications → Default preferences**. For each event type below, choose **All activity**, **Only mine** (tasks you're assigned to or watching), or **Off**.

Supported event types:

- **Mentions** — someone @-mentions you in a comment or description
- **Comments** — new comments added to tasks
- **Due dates** — reminders at 24 hours and 1 hour before a due date
- **Status changes** — a task moves to a new status (e.g., In Progress → Done)
- **Assignments** — a task is assigned to or unassigned from you
- **Attachments** — a file is added to a task you're watching

### Overriding settings for a specific project

1. Open the project and click the **⋯** menu in the top-right corner.
2. Select **Notification preferences**.
3. Toggle each event type on or off. A **project-level** badge appears next to any setting that differs from your global default.

Project-level overrides only affect you — they don't change settings for other members.

### Watching and unwatching tasks

Click the **eye icon** on any task to watch it. Watched tasks send you notifications for all activity regardless of your project preferences. Click the icon again to unwatch. You can see all your watched tasks under **My Work → Watching**.

## Mute & Do Not Disturb

Sometimes you need silence. Acme Tasks offers two ways to pause notifications.

### Muting a project

Open the project's **⋯** menu and select **Mute project**. While muted, no notifications from that project are delivered to any channel. A mute icon appears next to the project name in the sidebar as a reminder. Muting is indefinite until you unmute.

### Do Not Disturb (DND) hours

DND suppresses all notifications — across all channels — during a recurring time window you define.

To set DND hours:

1. Go to **Settings → Notifications → Do Not Disturb**.
2. Toggle **Enable DND** on.
3. Set your start and end times and select which days apply.
4. Choose your timezone (defaults to your account timezone).

During DND, in-app notifications are still collected and waiting when you return. Email and push notifications are held and delivered as a single batch when your DND window ends. Slack notifications are suppressed entirely during DND.

> **Tip:** If you're in a meeting or need a quick break, use **Pause notifications** (the same settings page) to silence everything for 30 minutes, 1 hour, 2 hours, or until tomorrow morning — no schedule required.

## Email digest

Instead of individual emails for every event, you can receive a single digest that summarizes your activity.

To switch to digest mode, go to **Settings → Notifications → Email → Delivery mode** and choose one of:

- **Immediate** — one email per event (default)
- **Hourly digest** — batched summary every hour
- **Daily digest** — one email per day, sent at a time you choose

The daily digest includes: open mentions, tasks due in the next 48 hours, status changes on tasks you're watching, and any unread comments. You can customize which sections appear in the digest under **Email digest content**.

> Digest mode applies to all projects. If you need immediate alerts for a high-priority project, consider keeping email on **Immediate** and using project-level muting for lower-priority projects instead.

## Slack integration

Connect Acme Tasks to Slack to receive notifications directly in a channel or as a direct message from the Acme Tasks bot.

### Connecting your Slack workspace

1. Go to **Settings → Integrations → Slack** and click **Connect workspace**.
2. Authorize Acme Tasks in the Slack OAuth flow.
3. Choose a **default channel** for notifications, or select **Direct message** to receive them privately.

Slack integration is available on the **Pro plan and above**.

### Configuring Slack notification types

Once connected, return to **Settings → Notifications → Slack** to choose which event types route to Slack. You can send different event types to different channels — for example, route all **@mentions** to your DMs and all **status changes** for a specific project to a shared `#eng-tasks` channel.

### Per-project Slack routing

Override the default channel for any project:

1. Open the project → **⋯** menu → **Notification preferences**.
2. Under **Slack channel**, select a channel from your connected workspace or enter a channel name.

### Disconnecting Slack

Go to **Settings → Integrations → Slack** and click **Disconnect**. All Slack notifications stop immediately; your other channel settings are unaffected.

---

**Still have questions?** Reach out to our support team via the in-app chat or email us at support@acmetasks.com.
