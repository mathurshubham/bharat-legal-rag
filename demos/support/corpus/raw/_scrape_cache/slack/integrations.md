---
source_url: https://slack.com/help/articles/115005265703-Manage-apps-on-Slack
source_site: slack
scraped_at_iso: 2026-06-26T11:13:51Z
---

guide

[Skip to main content](https://docs.slack.dev/quickstart/#__docusaurus_skipToContent_fallback)

On this page

We recommend using the CLI and the Slack Bolt framework for simplicity in creating an app. Pick your flavor of Bolt below and get started!

Would you rather create an app from the [app settings](https://api.slack.com/apps) in a browser? Head over to [Creating an app with app settings](https://docs.slack.dev/app-management/quickstart-app-settings) to learn how to create a basic Slack app that can send messages using webhooks.

- Python
- JavaScript

This quickstart guide aims to help you get a Slack app using Bolt for Python up and running as soon as possible!

When complete, you'll have a local environment configured with a customized [app](https://github.com/slack-samples/bolt-python-getting-started-app) running to modify and make your own.

Reference for readers

In search of the complete guide to building an app from scratch? Check out the [building an app](https://docs.slack.dev/tools/bolt-python/creating-an-app) guide.

#### Prerequisites [​](https://docs.slack.dev/quickstart/\#prerequisites "Direct link to Prerequisites")

A few tools are needed for the following steps. We recommend using the [**Slack CLI**](https://docs.slack.dev/tools/slack-cli/) for the smoothest experience, but other options remain available.

You can also begin by installing git and downloading [Python 3.7 or later](https://www.python.org/downloads/), or the latest stable version of Python. Refer to [Python's setup and building guide](https://devguide.python.org/getting-started/setup-building/) for more details.

Install the latest version of the Slack CLI to get started:

- [Slack CLI for macOS & Linux](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-mac-and-linux)
- [Slack CLI for Windows](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-windows)

Then confirm a successful installation with the following command:

```sh
$ slack version
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

An authenticated login is also required if this hasn't been done before:

```sh
$ slack login
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

A place to belong

A workspace where development can happen is also needed.

We recommend using [developer sandboxes](https://docs.slack.dev/tools/developer-sandboxes) to avoid disruptions where real work gets done.

## Creating a project [​](https://docs.slack.dev/quickstart/\#creating-a-project "Direct link to Creating a project")

With the toolchain configured, it's time to set up a new Bolt project. This contains the code that handles logic for your app.

If you don’t already have a project, let’s create a new one!

- Slack CLI
- Terminal

A starter template can be used to start with project scaffolding:

```sh
$ slack create first-bolt-app --template slack-samples/bolt-python-getting-started-app

$ cd first-bolt-app
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After a project is created you'll have a `requirements.txt` file for app dependencies and a `.slack` directory for Slack CLI configuration.

A few other files exist too, but we'll visit these later.

A starter template can be cloned to start with project scaffolding:

```sh
$ git clone https://github.com/slack-samples/bolt-python-getting-started-app first-bolt-app

$ cd first-bolt-app
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

Outlines of a project are taking shape, so we can move on to running the app!

We recommend using a [Python virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) to manage your project's dependencies. This is a great way to prevent conflicts with your system's Python packages. Let's create and activate a new virtual environment with [Python 3.7 or later](https://www.python.org/downloads/):

```sh
$ python3 -m venv .venv

$ source .venv/bin/activate

$ pip install -r requirements.txt
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

Confirm the virtual environment is active by checking that the path to `python3` is _inside_ your project ( [a similar command is available on Windows](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#activating-a-virtual-environment)):

```sh
$ which python3

# Output: /path/to/first-bolt-app/.venv/bin/python3
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

## Running the app [​](https://docs.slack.dev/quickstart/\#running-the-app "Direct link to Running the app")

Before you can start developing with Bolt, you will want a running Slack app.

- Slack CLI
- Browser

The getting started app template contains a `manifest.json` file with details about an app that we will use to get started. Use the following command and select "Create a new app" to install the app to the team of choice:

```sh
$ slack run

...

⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

With the app running, you can test it out with the following steps in Slack:

1. Open a direct message with your app or invite the bot `@first-bolt-app (local)` to a public channel.
2. Send "hello" to the current conversation and wait for a response.
3. Click the attached button labelled "Click Me" to post another reply.

After confirming the app responds, celebrate, then interrupt the process by pressing `CTRL+C` in the terminal to stop your app from running.

Navigate to your list of apps and [create a new Slack app](https://api.slack.com/apps/new) using the "from a manifest" option:

1. Select the workspace to develop your app in.
2. Copy and paste the `manifest.json` file contents to create your app.
3. Confirm the app features and click "Create".

You'll then land on your app's **Basic Information** page, which is an overview of your app and which contains important credentials:

![Basic Information page](https://docs.slack.dev/assets/images/basic-information-page-e7d531fe4721830376d61a91de5d933e.png)

To listen for events happening in Slack (such as a new posted message) without opening a port or exposing an endpoint, we will use [Socket Mode](https://docs.slack.dev/tools/bolt-python/concepts/socket-mode). This connection requires a specific app token:

1. On the **Basic Information** page, scroll to the **App-Level Tokens** section and click **Generate Token and Scopes**.
2. Name the token "Development" or something similar and add the `connections:write` scope, then click **Generate**.
3. Save the generated `xapp` token as an environment variable within your project:

```sh
$ export SLACK_APP_TOKEN=<your-app-level-token>
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

The above command works on Linux and macOS but [similar commands are available on Windows](https://superuser.com/questions/212150/how-to-set-env-variable-in-windows-cmd-line/212153#212153).

Keep it secret. Keep it safe.

Treat your tokens like a password and [keep it safe](https://docs.slack.dev/concepts/security). Your app uses these to retrieve and send information to Slack.

A bot token is also needed to interact with the Web API methods as your app's bot user. We can gather this as follows:

1. Navigate to the **OAuth & Permissions** on the left sidebar and install your app to your workspace to generate a token.
2. After authorizing the installation, you'll return to the **OAuth & Permissions** page and find a **Bot User OAuth Token**:

![OAuth Tokens](https://docs.slack.dev/assets/images/bot-token-3d6c761238c7a66557fd08d00a2a1b0c.png)

3. Copy the bot token beginning with `xoxb` from the **OAuth & Permissions page** and then store it in a new environment variable:

```sh
$ export SLACK_BOT_TOKEN=xoxb-<your-bot-token>
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After saving tokens for the app you created, it is time to run it:

```sh
$ python3 app.py

...

⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

With the app running, you can test it out with the following steps in Slack:

1. Open a direct message with your app or invite the bot `@BoltApp` to a public channel.
2. Send "hello" to the current conversation and wait for a response.
3. Click the attached button labelled "Click Me" to post another reply.

After confirming the app responds, celebrate, then interrupt the process by pressing `CTRL+C` in the terminal to stop your app from running.

## Updating the app [​](https://docs.slack.dev/quickstart/\#updating-the-app "Direct link to Updating the app")

At this point, you've successfully run the getting started Bolt for Python [app](https://github.com/slack-samples/bolt-python-getting-started-app)!

The defaults included leave opportunities abound, so to personalize this app let's now edit the code to respond with a kind farewell.

#### Responding to a farewell [​](https://docs.slack.dev/quickstart/\#responding-to-a-farewell "Direct link to Responding to a farewell")

Chat is a common thing apps do and responding to various types of messages can make conversations more interesting.

Using an editor of choice, open the `app.py` file and add the following import to the top of the file, and message listener after the "hello" handler:

```python
import random

@app.message("goodbye")

def message_goodbye(say):

    responses = ["Adios", "Au revoir", "Farewell"]

    parting = random.choice(responses)

    say(f"{parting}!")
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

Once the file is updated, save the changes and then we'll make sure those changes are being used.

- Slack CLI
- Terminal

Run the following command and select the app created earlier to start, or restart, your app with the latest changes:

```sh
$ slack run

...

⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After finding the above output appears, open Slack to perform these steps:

1. Return to the direct message or public channel with your bot.
2. Send "goodbye" to the conversation.
3. Receive a parting response from before and repeat "goodbye" to find another one.

Your app can be stopped again by pressing `CTRL+C` in the terminal to end these chats.

Run the following command to start, or restart, your app with the latest changes:

```sh
$ python3 app.py

...

⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After finding the above output appears, open Slack to perform these steps:

1. Return to the direct message or public channel with your bot.
2. Send "goodbye" to the conversation.
3. Receive a parting response from before and repeat "goodbye" to find another one.

Your app can be stopped again by pressing `CTRL+C` in the terminal to end these chats.

#### Customizing app settings [​](https://docs.slack.dev/quickstart/\#customizing-app-settings "Direct link to Customizing app settings")

The created app will have some placeholder values and a small set of [scopes](https://docs.slack.dev/reference/scopes) to start, but we recommend exploring the customizations possible on app settings.

- Slack CLI
- Browser

Open app settings for your app with the following command:

```sh
$ slack app settings
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

This will open the following page in a web browser:

![Basic Information page](https://docs.slack.dev/assets/images/basic-information-page-e7d531fe4721830376d61a91de5d933e.png)

Browse to [https://api.slack.com/apps](https://api.slack.com/apps) and select your app "Getting Started Bolt App" from the list.

This will open the following page:

![Basic Information page](https://docs.slack.dev/assets/images/basic-information-page-e7d531fe4721830376d61a91de5d933e.png)

On these pages you're free to make changes such as updating your app icon, configuring app features, and perhaps even distributing your app!

## Next steps [​](https://docs.slack.dev/quickstart/\#next-steps "Direct link to Next steps")

You can now continue customizing your app with various features to make it right for whatever job's at hand. Here are some ideas about what to explore next:

- Follow along with the steps that went into making this app on the [creating an app](https://docs.slack.dev/tools/bolt-python/creating-an-app) guide for an educational overview.
- Check out the [Agent quickstart](https://docs.slack.dev/ai/agent-quickstart) to get up and running with an agent.
- Browse our [curated catalog of samples](https://docs.slack.dev/samples) for more apps to use as a starting point for development.

This quickstart guide aims to help you get a Slack app using Bolt for JavaScript up and running as soon as possible!

When complete, you'll have a local environment configured with a customized [app](https://github.com/slack-samples/bolt-js-getting-started-app) running that responds to a simple greeting.

Reference for readers

In search of the complete guide to building an app from scratch? Check out the [building an app](https://docs.slack.dev/tools/bolt-js/creating-an-app) guide.

#### Prerequisites [​](https://docs.slack.dev/quickstart/\#prerequisites "Direct link to Prerequisites")

A few tools are needed for the following steps. We recommend using the [**Slack CLI**](https://docs.slack.dev/tools/slack-cli/) for the smoothest experience, but other options remain available.

- Slack CLI
- Terminal

Install the latest version of the Slack CLI to get started:

- [Slack CLI for macOS & Linux](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-mac-and-linux)
- [Slack CLI for Windows](https://docs.slack.dev/tools/slack-cli/guides/installing-the-slack-cli-for-windows)

Then confirm a successful installation with the following command:

```sh
$ slack version
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

An authenticated login is also required if this hasn't been done before:

```sh
$ slack login
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

Tooling for the terminal can also be used to follow along:

- [Git](https://git-scm.com/downloads)
- [Node.js](https://nodejs.org/en/download)

Once installed, make sure recent versions are being used:

```sh
$ git --version

$ node --version
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

A workspace where development can happen is also needed.

We recommend using [developer sandboxes](https://docs.slack.dev/tools/developer-sandboxes) to avoid disruptions where real work gets done.

## Creating a project [​](https://docs.slack.dev/quickstart/\#creating-a-project "Direct link to Creating a project")

With the toolchain configured, it's time to set up a new Bolt project. This contains the code that handles logic for your app.

If you don’t already have a project, let’s create a new one!

- Slack CLI
- Terminal

A starter template can be used to start with project scaffolding:

```sh
$ slack create first-bolt-app --template slack-samples/bolt-js-getting-started-app

$ cd first-bolt-app
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After a project is created you'll have a `package.json` file for app dependencies and a `.slack` directory for Slack CLI configuration.

A few other files exist too, but we'll visit these later.

A starter template can be cloned to start with project scaffolding:

```sh
$ git clone https://github.com/slack-samples/bolt-js-getting-started-app first-bolt-app

$ cd first-bolt-app

$ npm install
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

Outlines of a project are taking shape, so we can move on to running the app!

## Running the app [​](https://docs.slack.dev/quickstart/\#running-the-app "Direct link to Running the app")

Before you can start developing with Bolt, you will want a running Slack app.

- Slack CLI
- Browser

The getting started app template contains a `manifest.json` file with details about an app that we will use to get started. Use the following command and select "Create a new app" to install the app to the team of choice:

```sh
$ slack run

...

[INFO]  bolt-app ⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

With the app running, you can test it out with the following steps in Slack:

1. Open a direct message with your app or invite the bot `@first-bolt-app (local)` to a public channel.
2. Send "hello" to the current conversation and wait for a response.
3. Click the attached button labelled "Click Me" to post another reply.

After confirming the app responds, celebrate, then interrupt the process by pressing `CTRL+C` in the terminal to stop your app from running.

Navigate to your list of apps and [create a new Slack app](https://api.slack.com/apps/new) using the "from a manifest" option:

1. Select the workspace to develop your app in.
2. Copy and paste the `manifest.json` file contents to create your app.
3. Confirm the app features and click "Create".

You'll then land on your app's **Basic Information** page, which is an overview of your app and which contains important credentials:

![Basic Information page](https://docs.slack.dev/assets/images/basic-information-page-e7d531fe4721830376d61a91de5d933e.png)

To listen for events happening in Slack (such as a new posted message) without opening a port or exposing an endpoint, we will use [Socket Mode](https://docs.slack.dev/tools/bolt-js/concepts/socket-mode). This connection requires a specific app token:

1. On the **Basic Information** page, scroll to the **App-Level Tokens** section and click **Generate Token and Scopes**.
2. Name the token "Development" or something similar and add the `connections:write` scope, then click **Generate**.
3. Save the generated `xapp` token as an environment variable within your project:

```sh
$ export SLACK_APP_TOKEN=xapp-1-A0123456789-example
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

The above command works on Linux and macOS but [similar commands are available on Windows](https://superuser.com/questions/212150/how-to-set-env-variable-in-windows-cmd-line/212153#212153).

Keep it secret. Keep it safe

Treat your tokens like a password and [keep it safe](https://docs.slack.dev/concepts/security). Your app uses these to retrieve and send information to Slack.

A bot token is also needed to interact with the Web API methods as your app's bot user. We can gather this as follows:

1. Navigate to the **OAuth & Permissions** on the left sidebar and install your app to your workspace to generate a token.
2. After authorizing the installation, you'll return to the **OAuth & Permissions** page and find a **Bot User OAuth Token**:

![OAuth Tokens](https://docs.slack.dev/assets/images/bot-token-3d6c761238c7a66557fd08d00a2a1b0c.png)

3. Copy the bot token beginning with `xoxb` from the **OAuth & Permissions page** and then store it in a new environment variable:

```sh
$ export SLACK_BOT_TOKEN=xoxb-example
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After saving tokens for the app you created, it is time to run it:

```sh
$ npm run start

...

[INFO]  bolt-app ⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

With the app running, you can test it out with the following steps in Slack:

1. Open a direct message with your app or invite the bot `@BoltApp` to a public channel.
2. Send "hello" to the current conversation and wait for a response.
3. Click the attached button labelled "Click Me" to post another reply.

After confirming the app responds, celebrate, then interrupt the process by pressing `CTRL+C` in the terminal to stop your app from running.

## Updating the app [​](https://docs.slack.dev/quickstart/\#updating-the-app "Direct link to Updating the app")

At this point, you've successfully run the getting started Bolt for JavaScript [app](https://github.com/slack-samples/bolt-js-getting-started-app)!

The defaults included leave opportunities abound, so to personalize this app let's now edit the code to respond with a kind farewell.

#### Responding to a farewell [​](https://docs.slack.dev/quickstart/\#responding-to-a-farewell "Direct link to Responding to a farewell")

Chat is a common thing apps do and responding to various types of messages can make conversations more interesting.

Using an editor of choice, open the `app.js` file and add the following message listener after the "hello" handler:

```js
app.message('goodbye', async ({ say }) => {

  const responses = ['Adios', 'Au revoir', 'Farewell'];

  const parting = responses[Math.floor(Math.random() * responses.length)];

  await say(`${parting}!`);

});
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

Once the file is updated, save the changes and then we'll make sure those changes are being used.

- Slack CLI
- Terminal

Run the following command and select the app created earlier to start, or restart, your app with the latest changes:

```sh
$ slack run

...

[INFO]  bolt-app ⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After finding the above output appears, open Slack to perform these steps:

1. Return to the direct message or public channel with your bot.
2. Send "goodbye" to the conversation.
3. Receive a parting response from before and repeat "goodbye" to find another one.

Your app can be stopped again by pressing `CTRL+C` in the terminal to end these chats.

Run the following command to start, or restart, your app with the latest changes:

```sh
$ npm run start

...

[INFO]  bolt-app ⚡️ Bolt app is running!
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

After finding the above output appears, open Slack to perform these steps:

1. Return to the direct message or public channel with your bot.
2. Send "goodbye" to the conversation.
3. Receive a parting response from before and repeat "goodbye" to find another one.

Your app can be stopped again by pressing `CTRL+C` in the terminal to end these chats.

#### Customizing app settings [​](https://docs.slack.dev/quickstart/\#customizing-app-settings "Direct link to Customizing app settings")

The created app will have some placeholder values and a small set of [scopes](https://docs.slack.dev/reference/scopes) to start, but we recommend exploring the customizations possible on app settings.

- Slack CLI
- Browser

Open app settings for your app with the following command:

```sh
$ slack app settings
```

![](https://docs.slack.dev/img/devhub-icons/copy.svg)

This will open the following page in a web browser:

![Basic Information page](https://docs.slack.dev/assets/images/basic-information-page-e7d531fe4721830376d61a91de5d933e.png)

Browse to [https://api.slack.com/apps](https://api.slack.com/apps) and select your app "Getting Started Bolt App" from the list.

This will open the following page:

![Basic Information page](https://docs.slack.dev/assets/images/basic-information-page-e7d531fe4721830376d61a91de5d933e.png)

On these pages you're free to make changes such as updating your app icon, configuring app features, and perhaps even distributing your app!

## Next steps [​](https://docs.slack.dev/quickstart/\#next-steps "Direct link to Next steps")

You can now continue customizing your app with various features to make it right for whatever job's at hand. Here are some ideas about what to explore next:

- Follow along with the steps that went into making this app on the [creating an app](https://docs.slack.dev/tools/bolt-js/creating-an-app) guide for an educational overview.
- Check out the [Agent quickstart](https://docs.slack.dev/ai/agent-quickstart) to get up and running with an agent.
- Browse our [curated catalog of samples](https://docs.slack.dev/samples) for more apps to use as a starting point for development.

Copy as markdown

- [Creating a project](https://docs.slack.dev/quickstart/#creating-a-project)
- [Running the app](https://docs.slack.dev/quickstart/#running-the-app)
- [Updating the app](https://docs.slack.dev/quickstart/#updating-the-app)
- [Next steps](https://docs.slack.dev/quickstart/#next-steps)

 [Search](https://docs.slack.dev/search)