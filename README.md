# SimpleMind MCP Server

A Model Context Protocol (MCP) server that provides tools for reading, writing, and manipulating SimpleMind (.smmx) mind map files directly from Claude Desktop.

## Features

### Read Operations
- 📂 **list_mindmaps** - Find all .smmx files in a directory
- 📖 **read_mindmap** - Load and parse mind maps (structured, markdown, json, or summary format)
- 🔍 **search_nodes** - Search for nodes by text in titles or notes
- 📌 **get_node** - Get detailed info about a specific node
- 🗺️ **get_node_path** - Get the breadcrumb trail from root to any node
- 🎯 **find_nodes_without_notes** - Find incomplete topics (nodes without content)

### Write Operations
- ➕ **add_node** - Add new nodes to a mind map
- ✏️ **update_node** - Modify node text or notes
- 🗑️ **delete_node** - Remove nodes and their children
- 💾 **export_mindmap** - Export to Markdown or JSON

## Installation

### Step 1: Install Dependencies

```bash
pip install mcp
```

That's it! The parser uses only Python standard library.

### Step 2: Add to Claude Desktop Configuration

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this to the `mcpServers` section:

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

**Important:** Replace `/path/to/simplemind-mcp/` with the actual path where you saved these files!

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop for the changes to take effect.

## Usage Examples

### List All Mind Maps in a Directory

```
Claude: Use the list_mindmaps tool to find all SimpleMind files in ~/Documents
```

### Read and Summarize a Mind Map

```
You: What's in my project mind map?
Claude: [Uses read_mindmap with format="summary"]

Summary of project.smmx:
- Title: Project Planning
- Total nodes: 43
- Top-level branches:
  • Overview (5 children)
  • Research (4 children)
  • Development (2 children)
  • Testing (3 children)
  • Documentation (7 children)
```

### Search for Specific Topics

```
You: Find all nodes in my mind map related to "API"
Claude: [Uses search_nodes]

Found 3 nodes:
1. API Design (ID: 17)
2. API Documentation (ID: 8)
3. API Testing Strategy (ID: 22)
```

### Find Incomplete Topics

```
You: Which topics in my project mind map don't have content yet?
Claude: [Uses find_nodes_without_notes]

Found 8 nodes without notes:
- Security Considerations
- Performance Metrics
- User Authentication
- Database Schema
- Error Handling
...

Would you like me to help create content for any of these?
```

### Add a New Topic

```
You: Add a new node under "Development" called "Code Review Process"
Claude: [Uses get_node to find Development ID, then add_node]

✓ Added node 'Code Review Process' with ID 44
✓ Saved to: project.smmx
```

### Update Node Content

```
You: Update the notes for node 17 with information about REST API design
Claude: [Uses update_node]

✓ Updated node 17: notes → 532 characters
✓ Saved to: project.smmx
```

### Export to Markdown

```
You: Export my project mind map to Markdown
Claude: [Uses export_mindmap with format="markdown"]

✓ Exported to: project_export.md

Preview:
# Project Planning

## Overview

### Introduction
...
```

## Real-World Workflow Examples

### 1. **Morning Planning**

```
You: What topics in my project mind map need content?
Claude: [Finds nodes without notes]

You: Let's tackle "Database Schema" today
Claude: [Retrieves node, generates content, updates the mind map]
```

### 2. **Content Creation Pipeline**

```
You: For each empty node under "Documentation", create a 300-word explanation and update the mind map
Claude: [Iterates through nodes, generates content, updates each one]
```

### 3. **Review and Organization**

```
You: Show me the breadcrumb path for node 22
Claude: [Uses get_node_path]

Path: Project Planning > Research > User Studies > Interview Results
```

### 4. **Export for Different Uses**

```
You: Export to Markdown for my knowledge base
Claude: [Exports hierarchical Markdown]

You: Now export to JSON for my automation workflow
Claude: [Exports structured JSON]
```

## Integration with Automation Tools

You can use SimpleMind as your planning tool and sync it with automation workflows:

1. **Plan in SimpleMind** - Visual mind mapping of all your content
2. **Claude reads SimpleMind** - Uses this MCP to find incomplete topics
3. **Generate content** - Claude creates documentation, reports, etc.
4. **Update SimpleMind** - Marks nodes as complete with timestamps
5. **Sync to knowledge base** - Export to Markdown for your documentation system
6. **Automate distribution** - Automation tools process content based on mind map structure

## File Structure

```
simplemind-mcp/
├── simplemind_parser.py        # Core parsing library
├── simplemind_mcp_server.py    # MCP server implementation  
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
├── examples.py                 # Example scripts
└── tests/                      # Test files
    └── test_parser.py
```

## Technical Details

### SimpleMind File Format

SimpleMind (.smmx) files are ZIP archives containing:
- `document/mindmap.xml` - XML structure with all nodes and metadata
- `images/` - (Pro version) Embedded images

### Node Structure

Each node contains:
- **id** - Unique identifier
- **text** - Node title/label
- **notes** - Long-form content
- **parent_id** - Parent node ID
- **position** - X/Y coordinates
- **children** - Child nodes

### SimpleMind Pro Support

This MCP supports SimpleMind Pro features including:
- Icons
- URL links
- Layout modes
- Cross-links (relations)
- Embedded images

### Tool Response Formats

All tools return JSON for structured data:

```json
{
  "id": "17",
  "text": "API Design",
  "notes": "REST API best practices...",
  "parent_id": "14",
  "child_count": 3,
  "children": [
    {"id": "18", "text": "Authentication"},
    {"id": "19", "text": "Rate Limiting"},
    {"id": "20", "text": "Error Handling"}
  ]
}
```

## Troubleshooting

### MCP Server Not Showing Up

1. Check the config file path is correct
2. Verify Python path: `which python` or `where python`
3. Check Claude Desktop logs (Help → View Logs)
4. Restart Claude Desktop

### File Not Found Errors

- Use absolute paths, not relative: `/Users/you/Documents/map.smmx`
- Check file permissions: `ls -la /path/to/file.smmx`

### Import Errors

```bash
# Make sure MCP SDK is installed
pip install --upgrade mcp

# Verify installation
python -c "import mcp; print('MCP installed successfully')"
```

## Limitations

- Cannot edit visual styling (colors, fonts, etc.) - only content and structure
- Cannot modify images or attachments in nodes (read-only for Pro features)
- Position calculations are basic (new nodes placed near parent)

## Contributing

Contributions are welcome! Feel free to:

- Add support for node styling (colors, shapes)
- Implement batch operations
- Create merge/split tools for mind maps
- Improve position calculations for new nodes
- Add support for more export formats

## License

MIT License - See LICENSE file for details

## Support

Having issues? Please open an issue on GitHub with:
- Your operating system and Python version
- The error message you're seeing
- Steps to reproduce the problem

## Version History

- **1.0.0** (2024-11) - Initial release
  - Full read/write support for .smmx files
  - 10 core tools for mind map manipulation
  - Export to Markdown and JSON
  - SimpleMind Pro feature support

---

**Happy Mind Mapping! 🧠✨**
