---
source_url: https://slack.com/help/articles/203772216-Set-up-SAML-based-SSO
source_site: slack
scraped_at_iso: 2026-06-26T11:13:45Z
---

[Skip to main content](https://slack.com/help/articles/203772216-Set-up-SAML-single-sign-on-for-Slack#main)

[![Help Center](https://a.slack-edge.com/9b5ded/helpcenter/img/slack_help_center_logo.svg)](https://slack.com/help)[close](https://slack.com/help/articles/203772216-Set-up-SAML-single-sign-on-for-Slack#)

Articles and guides

- [Getting started](https://slack.com/help/categories/360000049043 "Everything you need to know to get started and get to work in Slack.")
- [Using Slack](https://slack.com/help/categories/200111606 "From channels to search, learn how Slack works from top to bottom.")
- [Your profile & preferences](https://slack.com/help/categories/360000047906 "Adjust your profile and preferences to make Slack work just for you.")
- [Connect tools & automate tasks](https://slack.com/help/categories/360000047926 "Connect, simplify, and automate. Discover the power of apps and tools.")
- [Workspace administration](https://slack.com/help/categories/200122103 "Learn how to manage your Slack workspace or Enterprise org.")
- [Tutorials & videos](https://slack.com/help/categories/360000049063 "Learning Slack made simple: tutorials, videos, and tips to get up to speed and get work done.")
- [Slack Status](https://slack-status.com/)

[Sign Up](https://slack.com/get-started?entry_point=help_center)

# Workspace administration

Learn how to manage your Slack workspace or Enterprise org.

NextPrevious

Actions,activity,access logs,accessibility,add,add an app,Add members,Add to Slack,administrators,all passwords,analytics,android,announcement,announcements,App Directory,app icon,Apple Watch,approving apps,archive,Asana,Atlassian,Automation apps,badge,billing details,billing,Bitbucket,bot user,box,browse,calls,Calls:,cancel,changes,channels,channel instantly,channel management,channel notification,channel suggestions,claim domains,close,company culture,compliance exports,compose,computers,conversations,convert,connect,connected accounts,connection,connecting,copy messages,create,customization,customize,custom SAML,custom,customer support teams,data exports,data security,deactivate,default channels,delete,deletion,deploy slack,desktop,direct messages,directory,disable,discover and join,Discovery APIs,display name,DMs,Do Not Disturb,domain,domains,downgrade,dropbox,duplicate accounts,edit,editing,education,email address,email,emoji,emoticons,Enterprise Grid,Enterprise Mobility Management,executives,export,failed payments,Fair Billing,faqs,finding,format,formatting,framework for apps,free trials,general,getting started,giphy,github integration,github organization,github,glossary,google apps,google calendar,google drive,guests,highlights,hipchat,human resources,IFTTT,import,Incoming WebHooks,integrations,ios,invite,IT teams,JIRA,join,Keep up,keyboard layout,keyboard shortcuts,Keychain Access,keyword notifications,language,languages,leave,link previews,loading,limits,links,linux,mac,manage a workspace,manage apps,manage members,marketing,mention,merge,message actions,messages are displayed,message display,microsoft products,mobile,mobile push,move channels,moving workspaces,multiple,mute,name,names,noise,nonprofits,notify,OneDrive,onboard,owners,password,payment,payments,permissions,phones,pin,plan,plans,plus plan,polls,primary ownership,privacy policies,prioritize tasks,private,private channel,private notes and files,project management,public channel,purpose,Quick Switcher,quote,reactivate,read,recruitment,referrer information,reminder,remove,rename,retention,Request a new workspace,role,roles,RSS,sales,Salesforce,SAML,SCIM,SCIM provisioning,screen reader,search,send,session duration,share messages,share,shared channel,shared channels,sidebar,sign in,sign out,signup mode,single sign-on,Slack Day,Slack for Teams,Slack notifications,Save notes and files,Service Level Agreements,ServiceNow,sign up,slack status,slackbot,slash commands,snippet,snooze,software developers,star,statistics,Stride,sync,tablets,tax,threads,time zone,tips,to-do lists,topic,triage channels,Terms of Service,Trello,troubleshoot,trouble receiving,tour,twitter,two-factor authentication,unread messages,updates,upgrade,upload,username,user groups,URL,vacation,Vendor and remittance,video,voice call,voice,what is,what's important,whitelisting,windows phone,windows,working in,workspace apps,workspace creation requests,workspace discovery,workspace's settings,wunderlist,your actions,Zapier,zoom,features,#general,File storage,posts,dark mode,theme,Workflow Builder,Voice,video,screen sharing,workflows,Outlook Calendar,Invited members,Transfer ownership,Whitelist,Enterprise Key Management,Transport Layer Security,Strong customer authentication,CSV,text file,work hours,

Search for “\[term\]”See \[n\]+ more results →

# Set up SAML single sign-on for Slack

SAML-based [single sign-on (SSO)](https://slack.com/help/articles/220403548-Manage-single-sign-on-settings) gives members access to Slack through an identity provider (IDP) of your choice.

**Note:** If you're having trouble setting up SAML SSO, visit [Troubleshoot SAML authorization errors](https://slack.com/help/articles/360037402653-Troubleshoot-SAML-authorization-errors) for help.

**Tip:** Workspace Owners and Org Owners can bypass SSO authentication to [sign in with an email address and password](https://slack.com/signin). This guarantees access to Slack even if your IDP is having issues.

## **Step 1: Configure your identity provider**

To get started, you’ll need to set up a connection between your IDP and Slack. Many providers we work with have created content to guide you through enabling SAML for Slack:

- [Auth0](https://marketplace.auth0.com/integrations/slack-sso)
- [Google Workspace (SAML)](https://support.google.com/a/answer/6357481)
- [JumpCloud](https://jumpcloud.com/support/integrate-with-slack)
- [LastPass](https://support.lastpass.com/s/document-item?language=en_US&bundleId=lastpass&topicId=LastPass/c_lastpass_admins_toolkit_sso.html&_LANG=enus)

- [Microsoft Entra](https://learn.microsoft.com/en-us/entra/identity/saas-apps/slack-tutorial)
- [Okta](https://help.okta.com/en-us/content/topics/provisioning/slack/slck-integrate-slack.htm)
- [OneLogin](https://onelogin.service-now.com/support?id=kb_article&sys_id=ddb89c4d87428a50695f0f66cebb35f6&kb_category=d28aedf0db185340d5505eea4b9619e0)
- [PingFederate and PingOne](https://docs.pingidentity.com/configuration_guides/config_configuration_guides.html)

**Note**: We also offer guides to help you set up [custom SAML SSO](https://slack.com/help/articles/205168057-Custom-SAML-single-sign-on), [Google Workspace SSO](https://get.slack.help/hc/en-us/articles/204078066), or [ADFS SSO](https://slack.com/help/articles/230902028-ADFS-single-sign-on).

## **Step 2: Set up SAML SSO**

Free, Pro, and Business+ plans

Enterprise plans

Once you’ve configured your IDP, a Workspace Owner can enable SSO.

01. From your desktop, click **Admin** in the sidebar.
02. Select **Workspace settings** from the menu.
03. Click **Security,** then select **SSO & authentication**.
04. Next to **An identity provider or custom SAML**, click **Configure SAML**.
05. Enter your **SAML 2.0 Endpoint URL**. (This came from [setting up your connector earlier](https://slack.com/help/articles/203772216-Set-up-SAML-single-sign-on-for-Slack#h_01J2C9088ZGGSTYZPZ4P5397J0)). If Okta is your IDP, you can include the **IDP URL** instead if you’d like.
06. Enter your **Identity Provider Issuer URL**.
07. By default, the **Service Provider Issuer URL** is set to https://slack.com. This field should match what you've set in your IDP.
08. Copy the entire **x.509 Certificate** from your IDP.
09. Choose whether the SAML responses and assertions are signed. If you require an end-to-end encryption key for your IDP, select the checkbox next to **Sign** **AuthnRequest** to show the certificate. You can also select your preference for **AuthnContextClassRef** values.
10. Click **Test Configuration**. We'll let you know if the changes are successful or whether you need to make further changes.
11. Review your configuration, then select **Continue to Options** to proceed.
12. Choose whether SSO is required for all members, required for all members excluding guests, or optional. Below **Profile settings**, decide if members can edit their profile information (like their email or display name) after SSO is enabled.
13. Click **Turn on SSO** or **Add SSO**.

Once you’ve configured your IDP, an Org Owner can enable SSO.

01. From your desktop, click your **organization name** in the top left.

    ![](https://a.slack-edge.com/8e8e4/helpcenter/img/workspace-picker@2x.jpg)
02. Select **Tools & settings** from the menu, then click **Organization settings**.
03. From the sidebar, click **Security**, then click **SSO Settings**.
04. Enter your **SSO name**.
05. Enter your **SAML 2.0 Endpoint URL** (this came from [setting up your connector](https://slack.com/help/articles/203772216-Set-up-SAML-single-sign-on-for-Slack#h_01J2C9088ZGGSTYZPZ4P5397J0) earlier) to configure where authentication requests from Slack will be sent.
06. Enter your **Identity Provider Issuer URL**.
07. By default, the **Service Provider Issuer URL** is set to https://slack.com. This field should match what you've set in your IDP.
08. Copy the entire **x.509 Certificate** from your IDP.
09. Choose whether the SAML responses and assertions are signed. If you require an end-to-end encryption key for your IDP, select the checkbox next to **Sign** **AuthnRequest** to show the certificate. You can also select your preference for **AuthnContextClassRef** values.
10. Click **Test Configuration**. We'll let you know if the changes are successful or whether you need to make further changes.
11. Review your configuration, then select **Turn on SSO** or **Add SSO**.

**Tip:** Once setup is complete, you can [manage SSO settings](https://slack.com/help/articles/220403548-Manage-single-sign-on-settings) to require SSO for all members, control whether members can edit their profile information, and more.

### Set up additional SSO configurations

You can add up to 11 additional SSO configurations to allow people to log into Slack from IDPs of your choice.

1. From your desktop, click your organization name in the top left.

![](https://a.slack-edge.com/8e8e4/helpcenter/img/workspace-picker@2x.jpg)
2. Hover over **Tools & settings**, then click **Organization settings**.
3. From the left sidebar, click **Security**, then click **SSO Settings**.
4. Click **Add SSO Configuration** in the top right.

**Tip:** If you have [guests](https://slack.com/help/articles/202518103-Understand-guest-roles-in-Slack) in your workspace or organization, we recommend choosing the option where SSO is partially required so they can still sign in with their email address and password.

**Note:** After setting up SSO, you can [manage SSO settings](https://slack.com/help/articles/220403548-Manage-single-sign-on-settings#enterprise-grid-plan-1) and learn how to [connect IDP groups to workspaces](https://slack.com/help/articles/115001435788-Connect-identity-provider-groups-to-your-Enterprise-organization) in your organization.

## **What to expect after SSO is enabled**

Once you’ve set up SSO, members that are required to sign in with SSO will get an email. The email will prompt members to [bind their Slack accounts](https://get.slack.help/hc/en-us/articles/220766827) with your IDP. Members will have 72 hours to bind their account before their link expires.

Any members already signed in when SSO is enabled will remain signed in. Going forward, all members will sign in to Slack with their IDP account. If you chose to require SSO, your members will see a sign-in page before they can access Slack.

**Note:** To simplify member management, Slack supports the [SCIM provisioning standard](https://slack.com/help/articles/212572638-Manage-members-with-SCIM-provisioning).

**Who can use this feature?**

- **Workspace Owners** and **Org Owners**
- Available on the **Business+** and **Enterprise** plans
- Available on the **Free** and **Pro** plans if you've [connected a Salesforce org to Slack](https://slack.com/help/articles/30754346665747-Connect-Salesforce-and-Slack)

**Awesome!**

Thanks so much for your feedback!

If you’d like a member of our support team to respond to you, please send a note to [feedback@slack.com](mailto:feedback@slack.com).

**Got it!**

If you’d like a member of our support team to respond to you, please send a note to [feedback@slack.com](mailto:feedback@slack.com).

Was this article helpful?Yes, thanks!Not really

Sorry about that! What did you find most unhelpful?This article didn’t answer my questions or solve my problemI found this article confusing or difficult to readI don’t like how the feature worksOther

0/600

Submit article feedback

If you’d like a member of our support team to respond to you, please send a note to [feedback@slack.com](mailto:feedback@slack.com).

Oops! We're having trouble. Please try again later!

IN THIS ARTICLE

a11179690159.cdn.optimizely.com

# a11179690159.cdn.optimizely.com is blocked

This page has been blocked by an extension

- Try disabling your extensions.

ERR\_BLOCKED\_BY\_CLIENT

Reload


This page has been blocked by an extension

![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)