---
doc_id: TWO_FACTOR_AUTH
effective_date: 2026-03-05
audience: public
visibility: public
---

# Two-Factor Authentication

Two-factor authentication (2FA) adds a second layer of protection to your Acme Tasks account. Even if your password is compromised, an attacker still can't sign in without your second factor. We recommend enabling 2FA on every account — it takes about two minutes to set up.

> **Before you start:** 2FA is available on all plans. If your organization uses SSO (SAML 2.0, OIDC, or Google Workspace), manage two-factor requirements through your identity provider instead of Acme Tasks directly.

> **Note on SMS:** Acme Tasks does not support SMS as a 2FA method. Text-message codes are vulnerable to SIM-swapping attacks, so we've deliberately excluded them in favor of more secure options: authenticator apps and hardware security keys.

---

## Enable 2FA

1. Click your avatar in the top-right corner and choose **Account settings**.
2. Select the **Security** tab.
3. Under **Two-factor authentication**, click **Set up 2FA**.
4. Choose your preferred method: **Authenticator app** or **Hardware key**.
5. Complete the setup flow for your chosen method (see sections below).
6. **Save your backup codes** — they appear once at the end of setup. Store them somewhere safe before closing the dialog.

Once enabled, Acme Tasks will prompt you for your second factor every time you sign in from a new device or browser session.

---

## Authenticator App

Acme Tasks works with any TOTP-compatible authenticator app, including Google Authenticator, 1Password, and Authy.

### Set up your authenticator app

1. Open your authenticator app and choose **Add account** (the exact label varies by app).
2. In Acme Tasks, go to **Account settings → Security → Set up 2FA** and select **Authenticator app**.
3. Scan the QR code displayed on screen, or tap **Can't scan? Enter code manually** to copy the setup key.
4. Give the account a recognizable name in your app (e.g., *Acme Tasks – work@example.com*).
5. Enter the 6-digit code your app generates and click **Verify**.
6. Save your backup codes and click **Done**.

### Sign in with your authenticator app

After entering your password, you'll be prompted for a verification code. Open your authenticator app, find the Acme Tasks entry, and type in the current 6-digit code. Codes refresh every 30 seconds — if one expires mid-entry, just use the next one.

> **Tip:** If your code is consistently rejected, your device clock may be out of sync. Enable automatic time sync in your device settings and try again.

---

## Hardware Keys

Hardware security keys (YubiKey and any other FIDO2/WebAuthn-compatible device) are the strongest 2FA option available in Acme Tasks.

### Register a hardware key

1. Plug your security key into a USB port (or hold it near your device if it supports NFC).
2. Go to **Account settings → Security → Set up 2FA** and select **Hardware key**.
3. Click **Register key** — your browser will prompt you to interact with the key (tap the button or touch the sensor).
4. Give the key a name (e.g., *YubiKey – desk*) so you can identify it later if you register more than one.
5. Click **Save**, then store your backup codes.

You can register up to **5 hardware keys** on a single account, which is useful if you want a primary key and a spare kept somewhere secure.

### Sign in with a hardware key

After entering your password, click **Use security key** when the 2FA prompt appears. Insert or tap your key when the browser asks. No code to type — authentication completes automatically.

---

## Backup Codes

Backup codes are single-use emergency codes generated when you first enable 2FA. Keep them somewhere safe — a password manager, a printed sheet in a secure location, or an encrypted note.

**Each code can only be used once.** After use, it's permanently invalidated.

### View or regenerate backup codes

1. Go to **Account settings → Security**.
2. Under **Two-factor authentication**, click **View backup codes**.
3. Verify your identity with your active 2FA method.
4. If you've used all your codes (or suspect they've been exposed), click **Regenerate codes**. This immediately invalidates the old set and creates a fresh one.

> **Important:** Regenerating codes invalidates every unused code from the previous set. Make sure you save the new codes before closing the dialog.

---

## Lost Device Recovery

If you lose access to your authenticator app or hardware key, use a backup code to get back in.

### Sign in with a backup code

1. On the 2FA prompt, click **Try another method**.
2. Select **Use a backup code**.
3. Enter one of your saved codes and click **Verify**.

Once you're signed in, go to **Account settings → Security** to remove the lost device and set up a new 2FA method.

### If you've also lost your backup codes

If you no longer have access to any 2FA method *and* have no remaining backup codes, contact our support team:

- **Email:** support@acmetasks.com
- **In-app:** click **Help** in the bottom-left corner → **Contact support**

Our team will verify your identity through account ownership checks before restoring access. For security reasons, this process cannot be expedited — please allow up to **1 business day** for a response. Business and Enterprise customers with priority support can expect a faster turnaround.

> **Prevention tip:** Register a second hardware key or save backup codes in a password manager so you always have a fallback. A few minutes of preparation now avoids a lockout later.
