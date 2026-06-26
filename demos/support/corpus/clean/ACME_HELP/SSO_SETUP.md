---
doc_id: SSO_SETUP
effective_date: 2026-03-10
audience: public
visibility: public
---

# Setting Up SAML 2.0 SSO for Acme Tasks

Single sign-on (SSO) lets your team authenticate through your existing identity provider instead of managing separate Acme Tasks passwords. SAML 2.0 SSO is available on the **Business** and **Enterprise** plans and supports Okta, Azure AD, Google Workspace, and any SAML 2.0-compliant IdP.

Once SSO is configured, you can optionally enforce it so that all members must sign in through your IdP — a common requirement for security and compliance teams.

---

## Prerequisites

Before you start, make sure you have the following in place:

- **An active Business or Enterprise plan.** SAML 2.0 SSO is not available on Free or Pro. If you're on Pro and want to upgrade, go to **Settings → Billing → Change Plan**.
- **Admin access in Acme Tasks.** Only workspace admins can configure SSO. You'll need the **Admin Controls** permission, which is enabled by default for the workspace owner.
- **Admin access in your IdP.** You'll need permission to create and configure a new application in Okta, Azure AD, or Google Workspace.
- **Your Acme Tasks SP metadata.** You'll copy these values from **Settings → Security → SAML SSO** in Acme Tasks:
  - **SP Entity ID:** `https://app.acmetasks.com/saml/metadata`
  - **ACS (Assertion Consumer Service) URL:** `https://app.acmetasks.com/saml/acs`
  - **SP Metadata XML download** (optional, for IdPs that accept file upload)

---

## Configure Your IdP

### Okta

1. In the Okta Admin Console, go to **Applications → Applications → Create App Integration**.
2. Select **SAML 2.0** and click **Next**.
3. Give the app a name (e.g., "Acme Tasks") and upload your company logo if desired. Click **Next**.
4. Fill in the SAML settings:
   - **Single sign-on URL (ACS URL):** `https://app.acmetasks.com/saml/acs`
   - **Audience URI (SP Entity ID):** `https://app.acmetasks.com/saml/metadata`
   - **Name ID format:** `EmailAddress`
   - **Application username:** `Email`
5. Under **Attribute Statements**, add the following:
   | Name | Value |
   |---|---|
   | `email` | `user.email` |
   | `firstName` | `user.firstName` |
   | `lastName` | `user.lastName` |
6. Click **Next**, mark the app as internal, and click **Finish**.
7. On the app's **Sign On** tab, click **View SAML setup instructions** and copy the **IdP SSO URL** and **IdP Issuer**. Download the **X.509 certificate**.

### Azure AD

1. In the Azure portal, go to **Azure Active Directory → Enterprise Applications → New Application → Create your own application**.
2. Name the app (e.g., "Acme Tasks"), select **Integrate any other application you don't find in the gallery**, and click **Create**.
3. Go to **Single sign-on → SAML**.
4. Under **Basic SAML Configuration**, enter:
   - **Identifier (Entity ID):** `https://app.acmetasks.com/saml/metadata`
   - **Reply URL (ACS URL):** `https://app.acmetasks.com/saml/acs`
5. Under **Attributes & Claims**, confirm `user.mail` maps to the `emailaddress` claim. Add given name and surname claims if not already present.
6. Download the **Federation Metadata XML** from the **SAML Signing Certificate** section — you'll upload this to Acme Tasks in the next step.

### Google Workspace

1. In the Google Admin console, go to **Apps → Web and mobile apps → Add App → Add custom SAML app**.
2. Name the app and click **Continue**.
3. On the **Google IdP Info** screen, download the **IdP metadata XML** or copy the **SSO URL**, **Entity ID**, and **Certificate**. Click **Continue**.
4. Enter the service provider details:
   - **ACS URL:** `https://app.acmetasks.com/saml/acs`
   - **Entity ID:** `https://app.acmetasks.com/saml/metadata`
   - **Name ID format:** `EMAIL`
   - **Name ID:** `Basic Information > Primary email`
5. Click **Continue**, add attribute mappings for first and last name, then click **Finish**.
6. Assign the app to the relevant organizational units or groups.

---

## Configure Acme Tasks

Once your IdP application is set up, connect it to your Acme Tasks workspace:

1. Go to **Settings → Security → SAML SSO**.
2. Click **Configure SAML**.
3. Enter your IdP details using one of these two methods:
   - **Metadata XML upload (recommended):** Click **Upload metadata file** and select the XML you downloaded from your IdP. Acme Tasks will automatically populate the IdP SSO URL, Issuer, and certificate.
   - **Manual entry:** Paste the **IdP SSO URL**, **IdP Issuer / Entity ID**, and the **X.509 certificate** into the respective fields.
4. Set the **Name ID format** to `Email Address`.
5. Optionally, configure **Just-in-Time (JIT) provisioning** — when enabled, new users who authenticate via SSO are automatically added to your workspace. On Enterprise, you can use SCIM provisioning instead for more granular control.
6. Click **Save Configuration**. Acme Tasks will validate the certificate format and display a green confirmation banner if the metadata is accepted.

---

## Test the Connection

Always test SSO before enforcing it. Testing in non-enforced mode means members can still use their existing credentials if something goes wrong.

### SP-initiated flow (recommended first test)

1. Open a private/incognito browser window.
2. Go to `https://app.acmetasks.com/login`.
3. Enter your work email address and click **Continue**. Acme Tasks detects the SSO domain and redirects you to your IdP login page.
4. Authenticate with your IdP credentials.
5. Confirm you land back in Acme Tasks with your account intact and the correct workspace loaded.

### IdP-initiated flow

1. In your IdP's app dashboard (e.g., the Okta home screen or the Google Workspace app launcher), click the **Acme Tasks** tile.
2. Confirm you are redirected directly into Acme Tasks without being prompted for a password.

If both flows succeed, the **SAML SSO** settings page will show a **Last successful authentication** timestamp. This is your confirmation that the integration is working end-to-end.

---

## Enforce SSO

Enforcing SSO means that password-based login is disabled for all members of the workspace. Only workspace admins with a verified SSO session can disable enforcement — make sure at least one admin has successfully completed the test flow above before proceeding.

1. Go to **Settings → Security → SAML SSO**.
2. Toggle **Enforce SSO for all members** to on.
3. Review the confirmation dialog, which lists the number of members who will be affected.
4. Click **Enforce**. Members currently signed in with a password will be signed out at their next session expiry and required to authenticate via SSO.

> **Note:** Workspace admins are not exempt from SSO enforcement. Ensure every admin has an active account in the IdP before enabling this setting.

---

## Troubleshooting

### "Invalid SAML response" or "Audience mismatch"
The SP Entity ID in your IdP does not match `https://app.acmetasks.com/saml/metadata`. Double-check the **Identifier / Audience URI** field in your IdP configuration and ensure there are no trailing slashes.

### "ACS URL not allowed"
The ACS URL in your IdP is incorrect or contains a typo. It must be exactly `https://app.acmetasks.com/saml/acs`.

### Users see a "domain not verified" error
Your email domain must be verified before SSO can be activated. Go to **Settings → Security → Verified Domains** and complete the DNS TXT record verification for your domain.

### Attribute mapping errors / users land in the wrong workspace
Confirm that the `email` attribute in your IdP maps to the user's primary work email and that the Name ID format is set to `EmailAddress`. If users are being provisioned into the wrong workspace, check that the email domain matches the verified domain on your workspace.

### Certificate expiry warnings
SAML certificates typically expire after one to three years depending on your IdP. Acme Tasks will display a banner in **Settings → Security** 30 days before your certificate expires. Upload a new certificate from your IdP before the expiry date to avoid authentication failures — you can stage a new certificate alongside the existing one without disrupting active sessions.

### SSO enforcement locked out an admin
If an admin is locked out because their IdP account is inactive or misconfigured, contact **Acme Tasks Priority Support** (Business) or your **dedicated Customer Success Manager** (Enterprise) to initiate an emergency access recovery. Have your billing email and workspace URL ready.

---

For questions about plan eligibility or to upgrade to Business or Enterprise, visit **Settings → Billing** or reach out to [support@acmetasks.com](mailto:support@acmetasks.com).
