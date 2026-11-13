# ServiceNow FastMCP Server

FastAPI-hosted FastMCP server that lets Azure agents discover ServiceNow incident capabilities and create incidents from structured payloads.

## Configure

Create or update `.env`:

```env
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_USERNAME=your-user
SERVICENOW_PASSWORD=your-password
```

`SERVICENOW_INSTANCE` can also be just `your-instance.service-now.com`; the app will add `https://`.

## Run

FastAPI-hosted MCP server:

```powershell
uv run python main.py
```

FastMCP directly, without the FastAPI wrapper:

```powershell
uv run python servicenow_fastmcp.py
```

The MCP endpoint for Azure agents is:

```text
http://localhost:8000/mcp
```

Useful HTTP checks:

```text
GET  http://localhost:8000/health
GET  http://localhost:8000/capabilities
POST http://localhost:8000/incidents
```

## Use With GitHub Copilot In VS Code

This repo includes `.vscode/mcp.json`:

```json
{
  "servers": {
    "servicenow-incident-mcp": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Start the server first:

```powershell
uv run python main.py
```

Then in VS Code:

1. Open this folder.
2. Open Copilot Chat in Agent mode.
3. Run `MCP: List Servers` from the Command Palette if the server is not already visible.
4. Start `servicenow-incident-mcp`.
5. Ask Copilot: `What ServiceNow tools are available?`

Copilot should discover `discover_capabilities`, `get_recent_incident_solutions`, `search_incident_solutions`, and `create_incident`.

## MCP Tools

`discover_capabilities`

Returns the ServiceNow operation this server exposes and the expected incident fields.

`create_incident`

Creates a ServiceNow incident using this structured payload:

```json
{
  "short_description": "Cannot access payroll portal",
  "description": "User cannot sign in to the payroll portal. Error says access denied. Issue started this morning and blocks payroll submission.",
  "urgency": "2",
  "impact": "2",
  "caller_id": "user@example.com",
  "category": "software",
  "subcategory": "access",
  "assignment_group": "Service Desk",
  "contact_type": "self-service",
  "business_service": "Payroll",
  "cmdb_ci": "Payroll Portal",
  "additional_fields": {
    "u_source": "azure-agent"
  }
}
```

Required fields are `short_description` and `description`. `urgency` and `impact` default to `"2"` when the agent does not have enough context.

`get_recent_incident_solutions`

Returns the latest incidents that have `close_notes`, defaulting to 5 records. Use this before creating a new incident so the caller LLM can suggest prior resolutions to the user.

HTTP check:

```text
GET http://localhost:8000/incident-solutions?limit=5
```

`search_incident_solutions`

Searches incidents that have `close_notes` using a query against `short_description`, `description`, and `close_notes`. Use this when the user has a specific issue such as `database timeout`, `VPN outage`, or `PostgreSQL 5432`.

HTTP check:

```text
GET http://localhost:8000/incident-solutions/search?query=database%20timeout&limit=5
```

## Files

`servicenow_fastmcp.py` contains only the FastMCP server, tools, and resources.

`fastapi_app.py` contains the FastAPI app, health endpoints, and MCP ASGI mounting.

`models.py`, `config.py`, and `servicenow_client.py` contain the shared schema, settings, and ServiceNow Table API client.

## Sample incidents
INC0000060 - Unable to connect to email
INC0009002 - My computer is not detecting the headphone device
INC0000009 - Reset my password
INC0000010 - Need Oracle 10GR2 installed
INC0000011 - Need new Blackberry set up
INC0000012 - Customer didn't receive eFax
INC0000013 - EMAIL is slow when an attachment is involved
INC0000014 - Missing my home directory
INC0000021 - New employee hire
INC0000024 - Issue with a web page on wiki
INC0000026 - Seem to have an issue with my hard drive...
INC0000028 - My disk is still having issues. Can't delete a file
INC0000030 - Lost connection to the wireless network
INC0000032 - EMAIL Server Down Again
INC0000033 - File Server is 80% full - Needs upgrade
INC0000034 - Does not look like a backup occurred last night
INC0000035 - Reset my password
INC0000036 - Issue with networking
INC0000038 - my PDF docs are all locked from editing
INC0000006 - Hangs when trying to print VISIO document
INC0000008 - Printer in my office is out of toner
INC0000001 - Can't read email
INC0000004 - Forgot email password
INC0000601 - The USB port on my PC stopped working
INC0009003 - Cannot sign into the company portal app
INC0009004 - Defect tracking tool is down.
INC0000005 - CPU load high for over 10 minutes
INC0010007 - Chander unable to access GIAM portal
INC0008001 - ATF:TEST2
INC0010017 - Multiple users experiencing VPN outages in AWS us-east-1
INC0010005 - Unable to login to ServiceNow
INC0000015 - I can't launch my VPN client since the last software update
INC0000016 - Rain is leaking on main DNS Server
INC0000017 - How do I create a sub-folder
INC0000018 - Sales forecast spreadsheet is READ ONLY
INC0000019 - Can't launch 64-bit Windows 7 virtual machine
INC0000020 - I need a replacement iPhone, please
INC0000025 - Need to add more memory to laptop
INC0000027 - Please remove the latest hotfix from my PC
INC0000029 - I can't get my weather report
INC0000031 - Need help with Remedy. Can we configure UI?
INC0000037 - Request for a new service
INC0000039 - Trouble getting to Oregon mail server
INC0000040 - JavaScript error on hiring page of corporate website
INC0000041 - My desk phone does not work
INC0000044 - Can't log into SAP from my laptop today
INC0008112 - Assessment :  ATF Assessor
INC0009009 - Unable to access the shared folder.
INC0010008 - Cannot sign in to payroll portal
INC0010009 - Cannot sign in to payroll portal
INC0000057 - Performance problems with wifi
INC0010012 - User cannot sign in to the payroll portal
INC0000059 - Unable to access team file share
INC0000007 - Need access to sales DB for the West
INC0000058 - Performance problems with email
INC0010013 - Database connection timeout
INC0000002 - Network file shares access issue
INC0010006 - User unable to authenticate to ABC corporate portal
INC0010014 - Database connection timeout
INC0001990 - Unable to access the personal details section in payroll portal
INC0009001 - Unable to post content on a Wiki page
INC0008111 - ATF : Test1
INC0000047 - Issue with email
INC0000046 - Can't access SFA software
INC0000048 - Having problems with Sales Tools performance
INC0010001 - Azure Foundry Test Incident
INC0010010 - Create ServiceNow incident for Brevo test email
INC0000051 - Manager can't access SAP Controlling application
INC0000052 - SAP Financial Accounting application appears to be down
INC0000053 - The SAP HR application is not accessible
INC0000054 - SAP Materials Management is slow or there is an outage
INC0000055 - SAP Sales app is not accessible
INC0010004 - Payroll portal inaccessible, blocking payroll submission
INC0000003 - Wireless access is down in my area
INC0009005 - Email server is down.
INC0010016 - Multiple users experiencing VPN outages in AWS us-east-1
INC0000049 - Network storage unavailable
INC0000050 - Can't access Exchange server - is it down?
INC0007001 - Employee payroll application server is down.
INC0010015 - Database connection timeout
INC0010018 - VPN connectivity issues from AWS US-East-1
INC0010011 - User cannot sign in to the payroll portal
INC0007002 - Need access to the common drive.
