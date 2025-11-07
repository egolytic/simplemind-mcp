# SimpleMind MCP Quick Start Guide

Get up and running with SimpleMind MCP in 5 minutes!

## Installation

### 1. Download the Code

```bash
git clone https://github.com/egolytic/simplemind-mcp.git
cd simplemind-mcp
```

Or download the ZIP file and extract it.

### 2. Install Dependencies

```bash
pip install mcp
```

That's it! No other dependencies needed.

### 3. Configure Claude Desktop

Find your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration (replace the path with your actual path):

```json
{
  "mcpServers": {
    "simplemind": {
      "command": "python",
      "args": ["/path/to/simplemind-mcp/simplemind_mcp_server.py"]
    }
  }
}
```

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

## Test It Works

Ask Claude:

```
Can you list all SimpleMind files in my Documents folder?
```

Claude should use the `list_mindmaps` tool and show you any .smmx files found.

## Basic Usage

### Read a Mind Map

```
Claude: Read my project planning mind map at ~/Documents/project.smmx
```

### Search for Topics

```
You: Find all nodes about "API" in my mind map
Claude: [Uses search_nodes tool]
```

### Add Content

```
You: Add a new node called "Security Review" under the "Development" branch
Claude: [Uses add_node tool]
```

### Export

```
You: Export my mind map to Markdown
Claude: [Uses export_mindmap tool]
```

## Common Issues

### "MCP server not found"

- Check the path in your config file is correct
- Make sure you restarted Claude Desktop
- Verify Python is installed: `python --version`

### "No module named mcp"

Run: `pip install mcp`

### "Permission denied"

Make sure the script has execute permissions:
```bash
chmod +x simplemind_mcp_server.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Try the [examples.py](examples.py) script to explore features
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to help improve the tool

## Need Help?

Open an issue on GitHub with:
- Your operating system
- Python version (`python --version`)
- The error message you're seeing
- What you were trying to do
