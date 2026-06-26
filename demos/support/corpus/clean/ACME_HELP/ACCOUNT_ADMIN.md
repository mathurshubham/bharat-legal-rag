---
doc_id: ACCOUNT_ADMIN
effective_date: 2026-04-10
audience: public
visibility: public
---

# Managing Your Acme Tasks Workspace

Whether you're onboarding a new hire or locking down access before a contractor wraps up, this guide covers everything workspace Owners and Admins need to manage people and permissions in Acme Tasks.

---

## Roles

Acme Tasks has four roles. Assign the one that matches what each person actually needs — least privilege is your friend.

| Role | What they can do |
|---|---|
| **Owner** | Full workspace control: billing, settings, role changes, deletion. One per workspace. |
| **Admin** | Invite/remove members, manage projects, access audit log (Business+). Cannot change billing or transfer ownership. |
| **Member** | Create and edit tasks, comment, manage their own projects. Standard day-to-day role. |
| **Guest** | View and comment on specific projects they've been explicitly added to. Cannot create projects or see workspace-level settings. |

**A few things to keep in mind:**

- Every workspace has exactly one Owner at a time.
- Guests do not count toward your seat limit on Pro and above, but they are limited to the projects you explicitly share with them.
- On the Free plan (up to 3 seats), Guests still occupy a seat slot.

---

## Invite & Remove

### Inviting users

1. Go to **Settings → Members → Invite people**.
2. Enter one or more email addresses (comma-separated).
3. Choose a role from the dropdown — Member is the default.
4. Click **Send invites**.

Invitees receive an email with a link valid for **72 hours**. If they miss it, resend from **Settings → Members → Pending invites → Resend**.

> **Seat limits:** Free workspaces cap at 3 seats, Pro at 10, and Business at 50. Enterprise seats are unlimited. If you've hit your limit, you'll see an error at step 4 — upgrade your plan or remove an existing member first.

### Removing users

1. Go to **Settings → Members**.
2. Find the person, click the **⋯** menu next to their name, and select **Remove from workspace**.
3. Confirm in the dialog.

Removed users lose access immediately. Any tasks they own are reassigned to the Admin or Owner who performed the removal — you can bulk-reassign afterward from the task list. Pending invitations can be cancelled from the **Pending invites** tab.

---

## Transfer Ownership

Ownership transfers are permanent until reversed, so take a moment before confirming.

1. The current Owner goes to **Settings → Members**.
2. Click **⋯** next to the intended new Owner and select **Transfer ownership**.
3. Enter your account password to confirm.
4. Both parties receive a confirmation email.

The previous Owner is automatically downgraded to **Admin** — they keep full access to projects and settings but lose billing and deletion rights. If you need to remove them entirely, do so as a separate step after the transfer completes.

> **Note:** Only the current Owner can initiate a transfer. If the Owner is unavailable (e.g., they've left the company), contact [support](mailto:support@acmetasks.com) with proof of account authority. Escalations of this type are reviewed within one business day.

---

## Audit Log

The audit log is available on **Business and Enterprise plans**. It gives Admins and Owners a timestamped record of workspace activity — useful for security reviews, compliance audits, and diagnosing unexpected changes.

### What's logged

- Member invitations, removals, and role changes
- Project creation and deletion
- SSO and authentication events
- Billing and plan changes
- API token creation and revocation

### Accessing the audit log

1. Go to **Settings → Security → Audit log**.
2. Filter by date range, actor, or event type.
3. Click any row to expand full event details, including IP address and user agent.

**Retention:** Business plan workspaces retain audit log data for **1 year**. Enterprise workspaces retain it indefinitely and can export raw logs (JSON or CSV) via **Settings → Security → Audit log → Export**.

---

## SCIM Provisioning

SCIM (System for Cross-domain Identity Management) automates user provisioning and deprovisioning through your identity provider. It's available on the **Enterprise plan**.

Supported identity providers include any IdP that speaks SCIM 2.0 — including Okta and Azure AD.

### Setting up SCIM

1. Go to **Settings → Security → SCIM provisioning**.
2. Click **Generate SCIM token**. Copy it immediately — it won't be shown again.
3. In your IdP, create a new SCIM application and enter:
   - **Base URL:** `https://api.acmetasks.com/scim/v2`
   - **Auth method:** Bearer token (paste the token from step 2)
4. Map your IdP groups to Acme Tasks roles. Recommended mappings:

   | IdP group | Acme Tasks role |
   |---|---|
   | `acmetasks-admins` | Admin |
   | `acmetasks-members` | Member |
   | `acmetasks-guests` | Guest |

5. Run a test sync in your IdP and verify users appear under **Settings → Members**.

### How provisioning works

- **New IdP user added to a mapped group** → automatically invited and activated in Acme Tasks.
- **User removed from all mapped groups** → deprovisioned immediately; their tasks are reassigned per your workspace's default reassignment setting.
- **User's group changes** → role updated automatically on next sync (typically within 60 seconds).

> **Heads up:** SCIM-managed users cannot have their roles changed manually inside Acme Tasks — those fields will appear locked. Make all role changes in your IdP.

If you run into provisioning errors, check **Settings → Security → SCIM provisioning → Sync log** for a per-user error breakdown, or reach out to your dedicated Customer Success Manager.
