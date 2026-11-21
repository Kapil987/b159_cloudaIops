# e7 — Smallest ServiceNow MCP server

File: [server.py](server.py) (the whole thing, one file)

## What it is
- One file, one tool: `create_incident`
- Plain typed arguments, no Pydantic models, no config class
- Credentials come from a `.env` file next to `server.py` (loaded with `python-dotenv`) or from real environment variables. Real env vars win.
- stdio transport, so any Host (VS Code, Claude Desktop, Inspector) can launch it

## Flow

```mermaid
flowchart LR
    U["User"] -->|"VPN is down, raise an incident"| H["Host + LLM<br/>(VS Code / Inspector)"]
    H <-->|"MCP over stdio"| S["server.py<br/>create_incident"]
    ENV[".env or env vars<br/>INSTANCE / USERNAME / PASSWORD"] --> S
    S -->|"POST /api/now/table/incident<br/>Basic auth"| SN[("ServiceNow")]
    SN -->|"JSON result"| S
    S -->|"number, sys_id, url"| H
    H -->|"Created INC0010001"| U
```

```mermaid
sequenceDiagram
    participant H as Host + LLM
    participant S as server.py
    participant SN as ServiceNow

    H->>S: list tools
    S-->>H: create_incident (schema built from the function signature)
    H->>S: create_incident(short_description, description, urgency)
    S->>S: read env vars, build URL
    S->>SN: POST /api/now/table/incident
    alt success
        SN-->>S: 201 + result
        S-->>H: {number, sys_id, url}
    else error (bad password, wrong URL)
        SN-->>S: 401 / 4xx
        S-->>H: ToolError with the status and body
    end
```

The tool's input schema comes straight from the function signature: argument names, types, and `Literal["1","2","3"]` for urgency and impact. The docstring and `description=` tell the LLM when to use it. No model class is involved, which is why this is the smallest version.

## Tool
| Argument | Required | Notes |
|---|---|---|
| `short_description` | yes | incident title |
| `description` | yes | details |
| `urgency` | no | `"1"` high, `"2"` medium (default), `"3"` low |
| `impact` | no | same scale |

Returns `number`, `sys_id`, and a `url` to open the incident.

## Setup
From `04_Day5_MCP/`:

```powershell
uv sync
copy e7_servicenow_minimal\.env.example e7_servicenow_minimal\.env
```

Edit `.env` and fill in your values (use the full host, no auto-expansion):

```
SERVICENOW_INSTANCE=dev12345.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your-password
```

`.env` is git-ignored, `.env.example` is not. You can still skip the file and set the variables in your shell or in the Host's `env` block; those override `.env`.

A free ServiceNow Personal Developer Instance works fine for testing.

## Test it
1. **MCP Inspector** (easiest)
```powershell
npx @modelcontextprotocol/inspector uv run python e7_server.py
```
Open Tools, then `create_incident`, fill the fields, Run. Check the incident exists in ServiceNow.

2. **VS Code** — add `.vscode/mcp.json`:
   ```json
   {
     "mcpServers": {
       "servicenow-minimal": {
         "type": "stdio",
         "command": "uv",
         "args": ["run", "--directory", "${workspaceFolder}/42_course_Sep/04_Day5_MCP",
                  "python", "e7_servicenow_minimal/server.py"]
       }
     }
   }
   ```
   Then in Copilot chat (agent mode): "Raise an incident, VPN is down for the whole Pune office, high urgency."
   No secrets needed here: the server reads them from `.env`.

## Things that will bite you
- **Never `print()` in a stdio server.** stdout is the protocol. Use `print(..., file=sys.stderr)`.
- **Bare instance name isn't expanded.** `dev12345` fails; use `dev12345.service-now.com`.
- **Only `ToolError` text reaches the LLM (mcp 2.x).** A wrong password raises `ToolError("ServiceNow returned 401: ...")` so the model can tell the user. Any other exception (a `KeyError` for a missing env var, a network error) shows up only as `Error executing tool create_incident`; the details are in the server's stderr log.
- **`.env` is read once at startup.** Edit it, then restart the server in the Host.
- Needs `mcp>=2.3` (it imports `mcp.server.mcpserver`, not the old `fastmcp` module), `httpx` and `python-dotenv`.


```json
{
  "result": {
    "number": "INC0010006",
    "sys_id": "cb8ae84283281710173fa4d0deaad3c2",
    "short_description": "Test incident from Python",
    "description": "Created using ServiceNow REST API",

    "state": "1",
    "incident_state": "1",
    "active": "true",
    "priority": "3",
    "impact": "2",
    "urgency": "2",
    "severity": "3",
    "category": "inquiry",
    "subcategory": "",

    "caller_id": "",
    "opened_by": {
      "link": "https://dev443316.service-now.com/api/now/table/sys_user/6816f79cc0a8016401c5a33be04be441",
      "value": "6816f79cc0a8016401c5a33be04be441"
    },
    "assigned_to": "",
    "assignment_group": "",

    "approval": "not requested",
    "approval_history": "",
    "approval_set": "",
    "upon_approval": "proceed",
    "upon_reject": "cancel",

    "made_sla": "true",
    "sla_due": "",
    "business_duration": "",
    "business_stc": "",
    "calendar_duration": "",
    "calendar_stc": "",

    "sys_created_on": "2026-11-15 14:08:35",
    "sys_created_by": "admin",
    "sys_updated_on": "2026-11-15 14:08:35",
    "sys_updated_by": "admin",
    "sys_mod_count": "0",
    "sys_class_name": "incident",

    "opened_at": "2026-11-15 14:08:35",
    "resolved_at": "",
    "resolved_by": "",
    "closed_at": "",
    "closed_by": "",
    "closed_code": "",
    "close_notes": "",

    "reopen_count": "0",
    "reopened_time": "",
    "reopened_by": "",
    "reassignment_count": "0",

    "parent": "",
    "parent_incident": "",
    "child_incidents": "0",
    "universal_request": "",

    "cmdb_ci": "",
    "business_service": "",
    "service_offering": "",
    "company": "",
    "location": "",
    "contract": "",
    "delivery_plan": "",
    "delivery_task": "",

    "watch_list": "",
    "additional_assignee_list": "",
    "group_list": "",
    "work_notes_list": "",
    "comments": "",
    "work_notes": "",
    "comments_and_work_notes": "",

    "work_start": "",
    "work_end": "",
    "time_worked": "",
    "expected_start": "",
    "due_date": "",
    "follow_up": "",
    "activity_due": "",

    "business_impact": "",
    "cause": "",
    "hold_reason": "",
    "route_reason": "",
    "contact_type": "",
    "notify": "1",
    "knowledge": "false",
    "order": "",
    "origin_table": "",
    "origin_id": "",
    "task_effective_number": "INC0010006",
    "correlation_display": "",
    "correlation_id": "",
    "sys_domain": {
      "link": "https://dev443316.service-now.com/api/now/table/sys_user_group/global",
      "value": "global"
    },
    "sys_domain_path": "/",
    "sys_tags": "",
    "user_input": "",
    "escalation": "0"
  }
}
```
## Next
[e8](../e8_servicenow_with_settings/README.md) adds a settings class, Pydantic input/output models, a read tool, and runs over streamable-http instead of stdio.
