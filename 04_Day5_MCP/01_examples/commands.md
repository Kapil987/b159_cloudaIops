npx -y @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector uv run python e1_minimal_mcp_server.py

### stdio
```json
"mcpServers": {
     "servers": {
       "servicenow-minimal": {
         "type": "stdio",
         "command": "uv",
         "args": ["run", "--directory", "${workspaceFolder}/42_course_Sep/04_Day5_MCP",
                  "python", "e7_servicenow_minimal/server.py"]
       }
     }
   }
```

```json
"mcpServers": {
  "servicenow-minimal": {
    "type": "stdio",
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "C:/Users/Administrator/Documents/b159_cloudaIops/04_Day5_MCP/01_examples",
      "python",
      "e4_prompt_template.py"
    ]
  }
}
```
```bash
# these only works with claude code not claude desktop
claude mcp add --scope user servicenow-minimal -- uv run --directory "C:/Users/Administrator/Documents/b159_cloudaIops/04_Day5_MCP/01_examples" python e4_prompt_template.py
claude mcp remove servicenow-minimal
claude mcp list
```
### streamable transport layer
```json
"mcpServers": {
       "servicenow": {
         "command": "npx",
         "args": [
           "-y",
           "mcp-remote",
           "http://127.0.0.1:8004/mcp",
           "--allow-http",
           "--transport",
           "http-only"
         ]
       }
     }
```

