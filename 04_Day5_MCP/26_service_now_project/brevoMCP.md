# Brevo MCP + GitHub Copilot Setup Guide

## Objective

Connect Brevo's official MCP (Model Context Protocol) server to GitHub Copilot in VS Code and send a test email using MCP tools.

---

# Prerequisites

## 1. Brevo Account

Create a Brevo account and log in.

Navigate to:

Settings → SMTP & API → API Keys & MCP

---

## 2. Generate MCP Token

Click:

Generate New API Key

Enter:

Brevo-Copilot

Enable:

Create MCP Server API Key

Copy the generated MCP token.

Important:

The token is shown only once.

Store it securely.

---

## 3. VS Code Requirements

Install:

* VS Code latest version
* GitHub Copilot extension
* GitHub Copilot Chat extension

Sign in to GitHub Copilot.

---

# Configure MCP in VS Code

Create:

```text
.vscode/mcp.json
```

Add:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "brevo-token",
      "description": "Brevo MCP Token",
      "password": true
    }
  ],
  "servers": {
    "brevo": {
      "type": "http",
      "url": "https://mcp.brevo.com/v1/brevo/mcp",
      "headers": {
        "Authorization": "Bearer ${input:brevo-token}"
      }
    }
  }
}
```

Save the file.

---

# Start MCP

Open:

Ctrl + Shift + P

Run:

MCP: List Servers

You should see:

brevo

Status should become:

Running

---

# Verify MCP Connection

Open:

View → Output

Select:

MCP

Expected log entries:

```text
Connection state: Running
Discovered xxx tools
```

If tools are discovered, MCP is working.

---

# Open GitHub Copilot Agent

Open:

GitHub Copilot Chat

Switch:

Ask → Agent

The MCP tools should now be available.

---

# Discover Brevo Tools

Ask:

```text
List all available Brevo MCP tools.
```

Copilot will return available endpoints.

---

# Important Discovery

In this setup the following email-related tools were available:

```text
mcp_mainbrevomcps_templates_send_test_template

mcp_mainbrevomcps_email_campaign_management_send_test_email

mcp_mainbrevomcps_email_campaign_management_create_email_campaig
```

No direct transactional send endpoint was exposed.

---

# Attempt 1 (Failed)

Tried:

```json
{
  "templateId": 1,
  "emailTo": [
    "example@gmail.com"
  ]
}
```

Result:

Failed because no templates existed.

---

# Verify Templates

Ask:

```text
List transactional templates.
```

Result:

```text
No templates found
```

Therefore template-based sending could not be used.

---

# Create Campaign Instead

Ask Copilot:

```text
Create a campaign using inline htmlContent.

Name: MCP Test

Subject: MCP Test Email

Sender: your-email@gmail.com

HTML:

<h1>Hello from Brevo MCP</h1>
<p>This is a test email generated via GitHub Copilot MCP.</p>
```

Copilot generated:

```json
{
  "htmlContent": "<h1>Hello from Brevo MCP</h1><p>This is a test email generated via GitHub Copilot MCP.</p>",
  "name": "MCP Test",
  "sender": {
    "email": "your-email@gmail.com"
  },
  "subject": "MCP Test Email"
}
```

Approve the tool call.

---

# Campaign Creation Result

Brevo returned:

```json
{
  "id": 1
}
```

Campaign ID:

```text
1
```

---

# Send Test Email

Ask:

```text
Send a test email for campaign ID 1 to your-email@gmail.com
```

Copilot executed:

```json
{
  "campaignId": 1,
  "emailTo": [
    "your-email@gmail.com"
  ]
}
```

Result:

```text
Test email sent successfully
```

---

# Final Architecture

```text
GitHub Copilot Agent
          │
          ▼
     Brevo MCP
          │
          ▼
     Brevo API
          │
          ▼
 Campaign Created
          │
          ▼
 Test Email Sent
```

---

# Useful Prompts

List tools:

```text
List all Brevo MCP tools.
```

List templates:

```text
List transactional email templates and IDs.
```

Create campaign:

```text
Create a campaign using inline htmlContent.
```

Get campaign ID:

```text
What campaign ID was created?
```

Send test email:

```text
Send a test email for campaign ID <id> to my email address.
```

---
### Prompt
Create a ServiceNow incident using the details provided.

Short Description: Database connection timeout

Description: Database connection is timing out affecting all users

Urgency: 1

Impact: 1

Workflow:

STEP 1

Create the ServiceNow incident.

STEP 2

Extract and store:

* incident_number
* sys_id
* instance_url

Construct:

incident_url

using:

https://<instance_name>.service-now.com/nav_to.do?uri=incident.do?sys_id=<sys_id>

STEP 3

Create a NEW Brevo email campaign.

Sender:
[shobhansingh431@gmail.com](mailto:shobhansingh431@gmail.com)

Campaign Name:
Incident Notification - <incident_number>

Subject:
ServiceNow Incident Created - <incident_number>

IMPORTANT:

Use htmlContent.

Do NOT escape HTML.

Do NOT include literal "\n" characters.

Pass valid HTML markup.

htmlContent:

<html>
<body>

<h2>🚨 ServiceNow Incident Created</h2>

<p>
<strong>Incident Number:</strong><br>
<incident_number>
</p>

<p>
<strong>Incident URL:</strong><br>
<incident_url>
</p>

<p>
<strong>Short Description:</strong><br>
<short_description>
</p>

<p>
<strong>Description:</strong><br>
<description>
</p>

<p>
<strong>Urgency:</strong><br>
<urgency>
</p>

<p>
<strong>Impact:</strong><br>
<impact>
</p>

<hr>

<p>
This notification was automatically generated by
ServiceNow MCP and Brevo MCP.
</p>

<p>
<strong>Open Incident:</strong><br>
<incident_url>
</p>

</body>
</html>

STEP 4

Capture the campaign ID returned by Brevo.

STEP 5

Send a test email using:

mcp_email_campaig_send_test_email

Recipients:

[shobhansingh431@gmail.com](mailto:shobhansingh431@gmail.com)

[kapilhsr9@gmail.com](mailto:kapilhsr9@gmail.com)

STEP 6

After successful delivery, delete the campaign.

STEP 7

Return:

* Incident Number
* Incident URL
* Campaign ID
* Email Recipients
* Delete Status

Rules:

Show the tool name before every MCP execution.

Show the payload before every MCP execution.

Use only:

* mcp_servicenow-in_create_incident
* mcp_email_campaig_create_email_campaign
* mcp_email_campaig_send_test_email
* mcp_email_campaig_delete_email_campaign

Always create a temporary campaign.

Never reuse an existing campaign.

Always delete the campaign after the test email is sent.


## Lessons Learned

1. MCP connectivity worked immediately.
2. Copilot initially generated invalid payloads.
3. Never approve tool calls using fake template IDs.
4. Verify payloads before execution.
5. Use htmlContent when templates do not exist.
6. Campaign creation can be used to validate MCP integrations quickly.
7. Brevo MCP exposes management tools more readily than direct SMTP send operations.
