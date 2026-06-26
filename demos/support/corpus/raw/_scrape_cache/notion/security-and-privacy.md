---
source_url: https://www.notion.so/help/security-and-privacy
source_site: notion
scraped_at_iso: 2026-06-26T11:11:37Z
---

* * *

## [Data security](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#data-security)

- **Access monitoring:** Notion has enabled logging on all critical systems. Logs include failed/successful logs, application access, administrator changes, and system changes. Logs are ingested by our observability and security incident event management (SIEM) solution for log ingestion and automated logging/alerting capabilities.

- **Backups enabled**: Notion is hosted by AWS and stores customer data using a combination of databases. By default, AWS provides durable infrastructure to store important data and is designed for durability of 99.9% of objects. Automated backups of all customer and system data is enabled, and data is backed up daily at minimum. The backups are encrypted in the same way as live production data, and are monitored and alerted.

- **Data erasure:** Notion customers are Controllers of their data. Each customer is responsible for the information they create, use, store, process and destroy. Notion customers have the ability to request data deletion or self-serve their own deletion, when data is not subject to regulatory or legal retention periodicity requirements. Please refer to our [Privacy Policy](https://www.notion.so/notion/Privacy-Policy-3468d120cf614d4c9014c09f6adc9091) and [Data Processing Addendum](https://www.notion.so/notion/Data-Processing-Addendum-361b540101274b1fa7e16b90402b0d99) for more information.

- **Encryption at rest:** Customer data is encrypted at rest using AES-256. Customer data is encrypted when on Notion’s internal networks, at rest in Cloud storage, database tables, and backups.

- **Encryption in transit:** Data sent in-transit is encrypted using TLS 1.2 or greater.

- **Physical security:** Notion leverages Amazon Web Services (AWS) to host our application, and defers all data center physical security controls to them. Please refer to [AWS’s physical security controls here](https://aws.amazon.com/compliance/data-center/controls/).


## [Application security](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#application-security)

- **Responsible disclosure:** Notion maintains a bug bounty program. Please refer to our [Responsible Disclosure Policy](https://www.notion.so/Responsible-Disclosure-Policy-5f18bb6b86804eaf989c006131778b9c).

- **Code analysis:** Notion security and development teams conduct threat modeling and secure design reviews for new releases and updates. After code completion for significant feature launches, we perform code audits, code reviews, and conduct security scans for our codebase.

- **Software Development Lifecycle (SDLC):** Notion uses a defined SDLC to ensure that code is written securely. During the design phase, security threat modeling and secure design reviews are performed for new releases and updates. After code completion for significant feature launches, we perform code audits, work with vendor companies or drive an internal penetration test, and conduct security scans for our codebase. After launch, we host bug bounties and have a vulnerability management program to address severe security issues.

- **Credential management:** Notion uses a third party Key Management Services (KMS) that automatically manages key generation, access control, secure storage, backup, and rotation of keys. Cryptographic keys are assigned to specific roles based on least privilege access and keys are automatically rotated yearly. Usage of keys is monitored and logged.

- **Vulnerability & patch management:** Notion performs vulnerability scanning and package monitoring on all infrastructure related hosts, and the company product continuously. Externally and internally-facing services are patched on a regular schedule. Any issues that are discovered are triaged and resolved according to the severity within Notion’s environment.

- **Web Application Firewall (WAF):** All public endpoints leverage a managed Web Application Firewall to deter attempts to exploit common vulnerabilities.


## [Security profile](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#security-profile)

- **Data Access Level:** Internal (i.e. Notion employees will only ever access your data for the purposes of troubleshooting problems or recovering content on your behalf.)

- **Third Party Dependence:** Yes - please refer to our list of subprocessors [here](https://www.notion.so/notion/Notion-s-List-of-Subprocessors-268fa5bcfa0f46b6bc29436b21676734).

- **Hosting:** Notion is hosted on one Amazon Web Services (AWS), one of the major cloud service providers.


## [Corporate security](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#corporate-security)

- **Employee training:** Security training is required during the employee onboarding process, and annually thereafter. Employees also must read and acknowledge Notion’s Code of Conduct and the Security policy. Developer training is also conducted on at least an annual basis.

- **HR security:** Notion performs background checks on employees when they are hired in accordance with local laws and regulations.

- **Incident response:** Notion has an incident management plan which contains steps for preparation, identification, containment, investigation, eradication, recovery, and follow-up/postmortem that is reviewed and tested annually at least.

- **Internal assessments:** Internal security audits are performed at least annually at Notion.

- **Internal SSO:** Multi-factor authentication (MFA) is required for all Notion employees to log into Notion’s identity provider.


## [Access control](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#access-control)

- **Data access:** Notion internally leverages the principle of Least Privilege for access. Access is granted based on job function, business requirements, and a need to know basis. Access reviews are conducted on a set frequency to ensure continued access to critical systems are still required.

- **Logging:** Notion leverages a SIEM solution for log ingestion and automated logging/alerting capabilities. Logs are ingested from critical systems and alerting rules are utilized to ensure security event alerts are generated where/when necessary.

- **Password Security:** Notion requires MFA to be enabled for any and all systems that provide the option for MFA). When such delegation is not possible, Notion maintains a stringent internal password management policy including complexity, and length.


## [Infrastructure](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#infrastructure)

- **Anti-DDoS:** Notion leverages third party applications for DDoS protection.

- **Data Center:** Notion is hosted on AWS, who handles physical security to data centers. Please refer to AWS’s security documentation [here](https://aws.amazon.com/security/).

- **Infrastructure Security:** Notion’s infrastructure is hosted in a fully redundant, secured environment. Notion’s customer data is hosted by AWS. AWS maintains a list of reports, certifications, and third party assessments to ensure best security practices. For more information on AWS compliance, please see [here](https://aws.amazon.com/compliance/programs/).

AWS infrastructure is housed in an Amazon controlled data centers throughout the world, and the data centers themselves are secured with a variety of physical controls to prevent unauthorized access. More information on AWS data centers and their security controls can be found [here](https://aws.amazon.com/compliance/data-center/data-centers/).

- **Separate Production Environment:** Customer data is never stored in non-production environments. Customer accounts are logically separated in our production environment. We have separate development, testing and production environments.


## [Endpoint security](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#endpoint-security)

- **Disk Encryption:** Employee laptops have disk encryption enabled for protection

- **Endpoint Detection & Response:** All endpoints have detection software installed. Additionally, Notion has implemented multiple security controls to ensure the security of customer data and solutions. These controls ensure we have ongoing visibility of what our end point is doing, that we can detect and react quickly to any tampering or threats as well as, logging and enforcement controls.

- **Mobile Device Management:** Employee devices and their software configuration are managed remotely by members of the IT and security team via MDM software.

- **Threat Detection:** Notion utilizes a third party endpoint protection software for dedicated threat detection. The endpoint software detects intrusions, malware, and malicious activities on endpoints and assists in rapid response to eliminate and mitigate the threats.


## [Network security](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#network-security)

- **Firewall:** Notion office networks are configured with a network firewall. WAN-accessible network services are not to be hosted within the office environment.

- **IDS/IPS:** Notion utilizes a mix of both network and host-based IDS/IPS type systems part of a broader defense-in-depth approach to securing the organization. This includes monitoring for suspicious activity through a combination of signature-based and anomaly-based detections.

- **Security Information and Event Management (SIEM):** Notion utilizes a SIEM solution for incident and event management. Event notifications are communicated to our security staff in real-time.

- **Wireless Security:** Notion offices use strong encryption for office wireless networks. Notion does not maintain any wireless networks with impacts on customer data or production systems.


## [Product security features](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#product-security-features)

- [Domain Management](https://www.notion.so/help/domain-management): Domain refers to the email address domain associated with a Notion account. Domain verification allows workspace owners to claim ownership over a domain, which will unlock domain management settings.

- [SAML Single Sign-On (SSO)](https://www.notion.so/help/saml-sso-configuration): Notion provides Single Sign-On (SSO) functionality for Business and Enterprise customers to access the app through a single authentication source.

- [SCIM Provisioning and Revoking](https://www.notion.so/help/provision-users-and-groups-with-scim): Notion workspace with the System for Cross-domain Identity Management (SCIM) API standard.

- [Audit Log](https://www.notion.so/help/audit-log): Notion gives Workspace owners access to detailed information about security and safety-related activity. This can include identifying potential security issues, investigating suspicious behavior, and troubleshooting access.

- [2FA (MFA)](https://www.notion.so/help/two-step-verification): Notion provides 2-step verification to add an extra layer of protection to your Notion account. This feature is available to all plan types and can be set up easily in your account settings.

- [Manage Permissions](https://www.notion.so/help/sharing-and-permissions): Notion allows owners to control their permission levels to ensure that users are viewing and interacting with your content exactly the way you want them to.

- [Manage Teamspaces](https://www.notion.so/help/manage-teamspaces): Workspace owners can get an overview of all teamspaces in the workspace, modify their settings, and access additional management tools.

- [SIEM and DLP Integrations:](https://www.notion.so/help/add-security-and-compliance-integrations) Notion can integrate with your DLP or SIEM of choice to detect events.


## [Compliance](https://www.notion.com/help/security-and-privacy?_ck=8e272447d87696b5cb66982b017e504adc755bb938c6c3527a59fa4cce8b2b7e\#compliance)

Notion maintains a comprehensive security and privacy program to provide advanced security features that are designed to protect your data in accordance with various regulatory and industry standards. To obtain Notion's independent audit reports (e.g., SOC 2 Type II report, ISO 27001 certificate), please visit our [Trust Center](https://trust.notion.com/).

- **SOC 2 Type 2**: The SOC 2 Type 2 is an audit reportperformed by an independent third-party certifiedby the American Institute of Certified Public Accountants (AICPA) to evaluate a service organization's controls related to the Trust Services Criteria (TSC). The SOC 2 Type 2 report assesses the effectiveness of these controls over a period of time and is intended to provide assurance to customers and stakeholders that the organization has implemented adequate controls to protect their data.

- **ISO:** ISO is an international standard development organization, and Notion has achieved certifications for four ISO standards: ISO 27001, ISO 27701, ISO 27017, and ISO 27018. The standards outline requirements for establishing, implementing, and continuously improving Notion’s Information Security Management System (ISMS) and Privacy Information Management System (PIMS).

- **HIPAA:** The Health Insurance Portability and Accountability Act (HIPAA) is a US federal law that was enacted in 1996 that requires the protection and confidential handling of protected health information (PHI) by covered entities such as healthcare providers, health plans, and healthcare clearinghouses, as well as their business associates. Provided businesses subject to HIPAA leverage the Notion Enterprise-grade security features described in our article [here](https://www.notion.so/help/hipaa) and sign Notion’s Business Associate Agreement they may process PHI within their Notion workspace.

- **BSI C5 (Cloud Computing Compliance Controls Catalogue):** BSI C5 is a security standard developed by the German Federal Office for Information Security. It outlines baseline security controls for cloud service providers. C5 includes additional control requirements relating to data location, service provisioning, place of jurisdiction, existing certifications, information disclosure obligations, and a full-service description.

- **PCI DSS:** The Payment Card Industry (PCI) Data Security Standards (DSS) is a global information security standard designed to prevent fraud through increased control of credit card data. Notion is compliant with PCI-DSS Merchant Level 2 requirements, ensuring secure handling of payment card data in our payment processing operations. However, our PCI-DSS compliance does not apply to Customer Data, and customers are prohibited from inputting or storing payment card information (PCI data) within their Notion workspaces, as explicitly outlined in our [Data Processing Addendum](https://notion.notion.site/Data-Processing-Addendum-361b540101274b1fa7e16b90402b0d99).

- **K-FSI:** Notion has successfully completed the Korean Financial Security Institute (K-FSI) Cloud Service Provider (CSP) Security and Safety Evaluation—demonstrating our commitment to meeting key regulatory requirements for cloud services in Korea’s financial sector. Financial institutions can review our K-FSI CSP audit results, which are scoped to SaaS service controls, to support their vendor risk assessments and internal compliance needs.


* * *

What data does Notion process?

Notion is committed to your safety and privacy. For detailed information on the data we process, please refer to our [Data Processing Addendum](https://www.notion.so/notion/Data-Processing-Addendum-361b540101274b1fa7e16b90402b0d99?pvs=4).

If I decide to leave Notion, what happens to my data?

For information around how long Notion will maintain data, please refer to the [Data Processing Addendum](https://www.notion.so/notion/Data-Processing-Addendum-361b540101274b1fa7e16b90402b0d99).

Follow the instructions [here](https://www.notion.so/help/delete-your-account) to delete your data.

If there was a disaster with Notions Systems and my Notion Instance was impacted, how does Notion restore itself?

Notion performs daily automated backups of all customer and system data to protect against loss due to unforeseen events across separate availability zones in AWS US West-2 and AWS US East-2.

We have a dedicated Business Continuity Plan and Disaster Recovery Plan for these circumstances, and our Disaster Recovery Plan is tested at least annually to ensure Notion will recover from a disruption resulting from a disaster.

Can Notion employees access our information?

Notion employees will only ever access your data for the purposes of troubleshooting problems or recovering content on your behalf. Please refer to our [Data Access Consent](https://www.notion.so/help/data-access-consent) for further information.

Will other people be able to see my pages?

Your data is safe in Notion! If someone tries to navigate to your workspace without having access, they’ll see a page that lets them know that they do not have the correct permission state to access that content.

If you enable `Share to web` in the `Share` menu at the top right of a page, it will publish that page to the web so that anyone with the link can access it. This is always turned off by default.

If you’re sharing a workspace with others, some pages will be visible to everyone in the workspace, or specific groups of people — this is based on the permissions you see in the `Share` menu at the top right of the page.

Please note, if you are using an account in an enterprise workspace, your content may be accessed by the workspace’s workspace owner. Learn more in [our Personal Use Terms of Service](https://notion.notion.site/Personal-Use-Terms-of-Service-00e4e5d0f2b9411cbee6493f15779500).

Can I opt out of Notion's tracking/analytics?

Yes you can! This will also disable in-app message support, but you can still reach out to us for help at [team@makenotion.com](mailto:team@makenotion.com).

Just send a message to our support team at that address and we'll opt you out.

My browser alerted me that Notion is using trackers. What do these trackers do?

We use tracking code in order to effectively run ads (for example, tracking a visit to our marketing site). We isolate this to a sandboxed iframe on a subdomain ( [aif.app.notion.com](https://aif.app.notion.com/)) — it's never activated on user pages.

No user content is exposed to any third-party service.

Does Notion review findings from Third Party Risk Assessment Platforms (i.e. Security Scorecard, Bitsight, Upguard)?

We understand that many organizations use third-party risk assessment platforms for security due diligence. However, we’ve noticed that these platforms often produce unreliable and incorrect results, and addressing these incorrect findings is costly and distracts from important cybersecurity work. Therefore, our policy is to not always respond to inquiries or findings from these platforms. This approach allows us to focus our cybersecurity resources on what truly matters for Notion and our customers.

* * *

Help Center Survey Iframe

* * *

[![](https://www.notion.com/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fspoqsaf9291f%2F4wnAiHwxmCXnmOVLPsh0tN%2F25ccda722bfa5d14bccdfd5969e341e8%2Fprivacy.png&w=3840&q=75)\\
\\
Up next\\
\\
Privacy is important to us — learn about how we handle privacy at Notion 🗝️\\
\\
Read more→](https://www.notion.com/help/privacy "Privacy practices")