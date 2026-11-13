winget install -e --id OpenJS.NodeJS.LTS
https://nodejs.org/en/download
Windows Installer (.msi)
npx -y @modelcontextprotocol/inspector
https://claude.com/download


Get your `claude_desktop_config.json` in the correct place, follow these exact steps:

1. Press **`Win + R`** to open the Run dialog.
2. Type **`%APPDATA%`** and press **Enter** (this opens your actual `AppData\Roaming` folder).
3. Inside that folder, check if a folder named **`Claude`** exists. If it doesn't, create a new folder and name it **`Claude`**.
4. Open that `Claude` folder and create a new text file inside it named **`claude_desktop_config.json`** (make sure Windows doesn't save it as `.txt`).
5. Paste the correct configuration below into that file and save it:

```json
{
  "mcpServers": {
    "day4-minimal-server": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/Administrator/Documents/b159_cloudaiops/04_Day5_MCP/01_examples",
        "run",
        "python",
        "e1_minimal_mcp_server.py"
      ]
    }
  }
}

```

*Verification:* Once saved, reopen Claude Desktop completely, and your server will appear under the tools/extensions menu.

## mcp inspector test
server --> connect --> tools -- select your tool -- fille the form and execute it

## prompt to test
for e2
```txt
Can you create a support ticket for me? The title is 'Login page crash' and the description is 'The user gets a white screen of death when clicking the sign-in button on mobile safari.' Please set the priority to high.
```