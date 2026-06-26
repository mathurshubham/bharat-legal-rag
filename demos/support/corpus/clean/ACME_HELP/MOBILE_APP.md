---
doc_id: MOBILE_APP
effective_date: 2026-03-22
audience: public
visibility: public
---

# Acme Tasks Mobile App

Acme Tasks is available on iOS and Android, so you can manage tasks, update projects, and stay on top of notifications wherever you are.

## Download

Install the app from your device's app store:

- **iOS** — requires iOS 16 or later. Search for "Acme Tasks" in the App Store, or tap the link in your workspace invitation email.
- **Android** — requires Android 10 or later. Search for "Acme Tasks" in Google Play.

The mobile app is included on every plan, including Free. No separate download code or license is needed.

## Sign In

Open the app and enter your workspace URL (for example, `yourteam.acmetasks.com`). You can then sign in with:

- **Email and password** — standard credentials you use on the web.
- **SSO** — if your workspace is on the Business or Enterprise plan and has Google Workspace, SAML 2.0, or OIDC configured, tap **Sign in with SSO** and you'll be redirected to your identity provider automatically.

If your admin has enforced SSO, the email/password option will not appear. Contact your workspace admin if you're unsure which method to use.

## Offline Mode

Acme Tasks caches your most recently viewed projects and tasks so you can keep working without a connection. While offline you can:

- View and edit task titles, descriptions, and due dates.
- Add comments (they sync when you reconnect).
- Update task status on your kanban board.

Changes sync automatically the moment your connection is restored. A small banner at the top of the screen indicates when you're working offline. Offline mode does not support creating new projects or uploading file attachments.

## Biometric Lock

For an extra layer of security, you can require Face ID, Touch ID, or your device's fingerprint sensor before the app opens.

To enable it: go to **Profile → Security → Biometric lock** and toggle it on. You'll be prompted to authenticate once to confirm the setting. After that, the app locks itself whenever it's sent to the background for more than 60 seconds.

If biometric authentication fails three times in a row, the app falls back to your Acme Tasks password. You can disable biometric lock at any time from the same settings screen.

## Limitations

The mobile app covers the most common day-to-day workflows, but a few features are only available on the web:

- **Audit log** — audit log access is not available on mobile, regardless of plan.
- **Admin controls** — workspace settings, member management, SSO configuration, and billing are web-only.
- **API rate-limit management** — API key creation and rate-limit monitoring require the web dashboard.
- **Bulk actions** — selecting and editing multiple tasks at once is not yet supported on mobile.

If you run into something that isn't working as expected, tap **Help → Send feedback** inside the app or visit [support.acmetasks.com](https://support.acmetasks.com).
