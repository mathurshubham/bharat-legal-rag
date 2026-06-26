---
doc_id: SECURITY_COMPLIANCE
effective_date: 2026-05-05
audience: public
visibility: public
---

## Security & Compliance Overview

Acme Tasks is built with security as a first-class concern — not a checkbox. This article explains the certifications we hold, how your data is protected in transit and at rest, where it lives, and what to do if you need compliance documentation.

---

## Certifications

Acme Tasks has completed independent third-party audits for the following frameworks:

- **SOC 2 Type II** — Our controls for security, availability, and confidentiality are audited annually by an accredited CPA firm. The report covers a 12-month observation period, not just a point-in-time snapshot.
- **ISO 27001** — Our information security management system (ISMS) is certified to the ISO/IEC 27001 standard, demonstrating a systematic approach to managing sensitive company and customer information.
- **GDPR-ready** — Acme Tasks supports GDPR compliance obligations for customers operating in or serving users in the European Economic Area. We offer a Data Processing Addendum (DPA) and support data subject rights requests. See *How to request our SOC 2 report* below for DPA access.

SOC 2 Type II and ISO 27001 certifications are available to Business and Enterprise customers on request.

---

## Encryption

Your data is protected at every stage of its lifecycle.

- **At rest:** All customer data — including task content, attachments, comments, and metadata — is encrypted using **AES-256**.
- **In transit:** All data moving between your browser or API client and Acme Tasks infrastructure is encrypted with **TLS 1.3**. Older protocol versions are not accepted.
- **Key management:** Encryption keys are managed through a dedicated key management service, with automatic annual rotation and access scoped to least-privilege roles. Key usage is logged and monitored continuously.

---

## Data Residency

Acme Tasks offers three data residency regions, letting you control where your workspace data is stored and processed:

| Region | Location |
|---|---|
| **us-east** | United States (East) |
| **eu-west** | European Union (West) |
| **ap-south** | Asia-Pacific (South) |

Data residency is configurable at workspace creation for **Business** and **Enterprise** plans. If you need to migrate an existing workspace to a different region, contact our support team — migrations are handled with zero data loss and a scheduled maintenance window.

EU-based customers who select **eu-west** can rely on data remaining within the EEA for GDPR purposes. Our DPA reflects the applicable Standard Contractual Clauses (SCCs) for cross-border transfers where relevant.

---

## Penetration Testing & Bug Bounty

### Annual penetration test

Acme Tasks commissions a full-scope penetration test from an independent third-party security firm every year. Testing covers our web application, API surface, and internal network boundaries. Findings are triaged by severity, remediated on a defined schedule, and reviewed by our security team before the next release cycle.

Customers on Enterprise plans may request a summary letter from their dedicated Customer Success Manager (CSM).

### Bug bounty program

We run a public bug bounty program through **HackerOne**. Security researchers are invited to responsibly disclose vulnerabilities in Acme Tasks products and infrastructure. Rewards are scoped by severity (P1–P4), and our team commits to an initial response within two business days for all valid submissions.

To report a vulnerability, visit our HackerOne program page or email **security@acmetasks.com** for sensitive disclosures that shouldn't be filed publicly.

---

## Incident Response

Acme Tasks maintains a formal incident response plan that is reviewed and tested at least annually. The plan follows a structured lifecycle: preparation → detection → containment → investigation → eradication → recovery → post-mortem.

**What to expect if an incident affects your data:**

1. **Detection & triage** — Our security monitoring systems alert on-call engineers around the clock. Severity is assessed within 15 minutes of alert.
2. **Containment** — Affected systems are isolated to prevent further exposure.
3. **Customer notification** — If your workspace data is involved in a confirmed breach, we will notify affected account owners within **72 hours** of confirmation, in line with GDPR Article 33 timelines.
4. **Post-mortem** — A written post-mortem is completed for all P1 incidents, with a summary available to Enterprise customers upon request.

Current service status and historical incident records are published at **status.acmetasks.com**.

---

## How to Request Our SOC 2 Report

Our SOC 2 Type II report is available under NDA to customers on **Business** and **Enterprise** plans.

**To request a copy:**

1. Log in to your Acme Tasks workspace.
2. Go to **Settings → Security & Compliance**.
3. Click **Request compliance documents** and select the report(s) you need (SOC 2 Type II, ISO 27001 certificate, or DPA).
4. A member of our security team will respond within **two business days** with a secure download link and NDA if applicable.

Alternatively, reach out directly to your account manager or email **compliance@acmetasks.com** with your workspace domain and the documents you require.

> **Free and Pro plan customers:** Compliance documentation is available to Business and Enterprise plans. If you're evaluating an upgrade, contact our sales team and we can facilitate access as part of a formal security review.
