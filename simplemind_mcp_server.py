#!/usr/bin/env python3
"""
SimpleMind MCP Server

A Model Context Protocol server that provides tools for reading and manipulating
SimpleMind (.smmx) mind map files.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional, List, Dict
import json

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

from simplemind_parser import (
    SimpleMindParser,
    SimpleMindMap,
    SimpleMindNode,
    read_mindmap,
    write_mindmap,
    export_to_markdown,
    export_to_json
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simplemind-mcp")

# Initialize MCP server
server = Server("simplemind-mcp")


# Helper functions
def find_smmx_files(directory: str) -> List[str]:
    """Find all .smmx files in a directory"""
    path = Path(directory)
    if not path.exists():
        return []
    
    if path.is_file() and path.suffix == '.smmx':
        return [str(path)]
    
    return [str(f) for f in path.rglob('*.smmx')]


def format_node_info(node: SimpleMindNode, include_children: bool = True) -> Dict[str, Any]:
    """Format a node for JSON output"""
    info = {
        'id': node.id,
        'text': node.text,
        'notes': node.notes,
        'parent_id': node.parent_id,
        'guid': node.guid,
        'position': {'x': node.x, 'y': node.y},
        'child_count': len(node.children)
    }
    
    if include_children:
        info['children'] = [
            {'id': child.id, 'text': child.text}
            for child in node.children
        ]
    
    return info


# MCP Tool Implementations

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available SimpleMind tools"""
    return [
        Tool(
            name="list_mindmaps",
            description="Find all SimpleMind (.smmx) files in a directory or get info about a specific file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory to search, or path to specific .smmx file"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="read_mindmap",
            description="Read and parse a SimpleMind file, returning its structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["structured", "markdown", "json", "summary"],
                        "description": "Output format: structured (full tree), markdown (hierarchical), json (raw data), or summary (overview only)",
                        "default": "structured"
                    }
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="get_node",
            description="Get detailed information about a specific node by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "node_id": {
                        "type": "string",
                        "description": "ID of the node to retrieve"
                    }
                },
                "required": ["filepath", "node_id"]
            }
        ),
        Tool(
            name="search_nodes",
            description="Search for nodes containing specific text in their title or notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query text"
                    },
                    "search_notes": {
                        "type": "boolean",
                        "description": "Whether to search in notes as well as titles",
                        "default": True
                    }
                },
                "required": ["filepath", "query"]
            }
        ),
        Tool(
            name="export_mindmap",
            description="Export a mind map to Markdown or JSON format",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["markdown", "json"],
                        "description": "Export format"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional: path to save the exported file"
                    }
                },
                "required": ["filepath", "format"]
            }
        ),
        Tool(
            name="add_node",
            description="Add a new node to a mind map",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "ID of the parent node"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text/title for the new node"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes/content for the node",
                        "default": ""
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional: path to save modified mind map (defaults to overwriting original)"
                    }
                },
                "required": ["filepath", "parent_id", "text"]
            }
        ),
        Tool(
            name="update_node",
            description="Update the text or notes of an existing node",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "node_id": {
                        "type": "string",
                        "description": "ID of the node to update"
                    },
                    "text": {
                        "type": "string",
                        "description": "New text/title for the node (leave empty to keep current)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "New notes for the node (leave empty to keep current)"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional: path to save modified mind map (defaults to overwriting original)"
                    }
                },
                "required": ["filepath", "node_id"]
            }
        ),
        Tool(
            name="delete_node",
            description="Delete a node and all its children from a mind map",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "node_id": {
                        "type": "string",
                        "description": "ID of the node to delete"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional: path to save modified mind map (defaults to overwriting original)"
                    }
                },
                "required": ["filepath", "node_id"]
            }
        ),
        Tool(
            name="get_node_path",
            description="Get the full path from root to a specific node (breadcrumb trail)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    },
                    "node_id": {
                        "type": "string",
                        "description": "ID of the node"
                    }
                },
                "required": ["filepath", "node_id"]
            }
        ),
        Tool(
            name="find_nodes_without_notes",
            description="Find all nodes that don't have any notes/content (useful for finding incomplete topics)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the .smmx file"
                    }
                },
                "required": ["filepath"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool execution requests"""
    
    try:
        if name == "list_mindmaps":
            path = arguments["path"]
            files = find_smmx_files(path)
            
            if not files:
                return [types.TextContent(
                    type="text",
                    text=f"No .smmx files found in: {path}"
                )]
            
            result = {
                "count": len(files),
                "files": []
            }
            
            for filepath in files:
                try:
                    mindmap = read_mindmap(filepath)
                    result["files"].append({
                        "path": filepath,
                        "title": mindmap.title,
                        "node_count": len(mindmap.nodes)
                    })
                except Exception as e:
                    result["files"].append({
                        "path": filepath,
                        "error": str(e)
                    })
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "read_mindmap":
            filepath = arguments["filepath"]
            format_type = arguments.get("format", "structured")
            
            mindmap = read_mindmap(filepath)
            
            if format_type == "markdown":
                content = mindmap.to_markdown()
            elif format_type == "json":
                content = json.dumps(mindmap.to_dict(), indent=2)
            elif format_type == "summary":
                content = json.dumps({
                    "title": mindmap.title,
                    "total_nodes": len(mindmap.nodes),
                    "root_node": mindmap.root_node.text if mindmap.root_node else None,
                    "top_level_branches": [
                        {"id": child.id, "text": child.text, "child_count": len(child.children)}
                        for child in (mindmap.root_node.children if mindmap.root_node else [])
                    ]
                }, indent=2)
            else:  # structured
                content = json.dumps(mindmap.to_dict(), indent=2)
            
            return [types.TextContent(type="text", text=content)]
        
        elif name == "get_node":
            filepath = arguments["filepath"]
            node_id = arguments["node_id"]
            
            mindmap = read_mindmap(filepath)
            node = mindmap.get_node(node_id)
            
            if not node:
                return [types.TextContent(
                    type="text",
                    text=f"Node with ID '{node_id}' not found"
                )]
            
            result = format_node_info(node, include_children=True)
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "search_nodes":
            filepath = arguments["filepath"]
            query = arguments["query"]
            search_notes = arguments.get("search_notes", True)
            
            mindmap = read_mindmap(filepath)
            results = mindmap.search_nodes(query, search_notes=search_notes)
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No nodes found matching '{query}'"
                )]
            
            output = {
                "query": query,
                "count": len(results),
                "results": [format_node_info(node, include_children=False) for node in results]
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(output, indent=2)
            )]
        
        elif name == "export_mindmap":
            filepath = arguments["filepath"]
            format_type = arguments["format"]
            output_path = arguments.get("output_path")
            
            if format_type == "markdown":
                content = export_to_markdown(filepath, output_path)
                message = "Exported to Markdown"
            else:  # json
                content = export_to_json(filepath, output_path)
                message = "Exported to JSON"
            
            if output_path:
                message += f" at: {output_path}"
            
            return [types.TextContent(
                type="text",
                text=f"{message}\n\nPreview:\n{content[:500]}..."
            )]
        
        elif name == "add_node":
            filepath = arguments["filepath"]
            parent_id = arguments["parent_id"]
            text = arguments["text"]
            notes = arguments.get("notes", "")
            output_path = arguments.get("output_path", filepath)
            
            mindmap = read_mindmap(filepath)
            
            # Check if parent exists
            parent = mindmap.get_node(parent_id)
            if not parent:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Parent node with ID '{parent_id}' not found"
                )]
            
            # Generate new ID
            new_id = str(max([int(nid) for nid in mindmap.nodes.keys()]) + 1)
            
            # Calculate position intelligently based on grandparent direction
            grandparent = mindmap.get_node(parent.parent_id) if parent.parent_id != "-1" else None
            
            if grandparent:
                # Calculate direction from grandparent to parent
                dx = parent.x - grandparent.x
                dy = parent.y - grandparent.y
                
                # Continue in the same direction for the child
                # Base position: continue the line
                base_x = parent.x + dx
                base_y = parent.y + dy
                
                # If there are multiple children, offset them perpendicular to the main direction
                if len(parent.children) > 0:
                    # Calculate perpendicular direction (rotate 90 degrees)
                    perp_dx = -dy
                    perp_dy = dx
                    
                    # Normalize and scale the perpendicular offset
                    import math
                    perp_length = math.sqrt(perp_dx**2 + perp_dy**2)
                    if perp_length > 0:
                        perp_dx = (perp_dx / perp_length) * 80  # 80 pixels perpendicular spacing
                        perp_dy = (perp_dy / perp_length) * 80
                    
                    # Offset based on child index (alternating above/below the line)
                    child_index = len(parent.children)
                    if child_index % 2 == 0:
                        # Even: offset in positive perpendicular direction
                        offset_mult = (child_index // 2)
                    else:
                        # Odd: offset in negative perpendicular direction
                        offset_mult = -((child_index + 1) // 2)
                    
                    new_x = base_x + (perp_dx * offset_mult)
                    new_y = base_y + (perp_dy * offset_mult)
                else:
                    # First child: just continue the line
                    new_x = base_x
                    new_y = base_y
            else:
                # Parent is root or no grandparent - use simple offset
                new_x = parent.x + 200
                new_y = parent.y + (len(parent.children) * 100)
            
            # Create new node
            new_node = SimpleMindNode(
                id=new_id,
                text=text,
                parent_id=parent_id,
                x=new_x,
                y=new_y,
                notes=notes,
                guid=f"GENERATED_{new_id}"
            )
            
            mindmap.add_node(new_node)
            write_mindmap(mindmap, output_path)
            
            return [types.TextContent(
                type="text",
                text=f"✓ Added node '{text}' with ID {new_id} under parent {parent_id}\n✓ Saved to: {output_path}"
            )]
        
        elif name == "update_node":
            filepath = arguments["filepath"]
            node_id = arguments["node_id"]
            new_text = arguments.get("text")
            new_notes = arguments.get("notes")
            output_path = arguments.get("output_path", filepath)
            
            if not new_text and not new_notes:
                return [types.TextContent(
                    type="text",
                    text="Error: Must provide either text or notes to update"
                )]
            
            mindmap = read_mindmap(filepath)
            node = mindmap.get_node(node_id)
            
            if not node:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Node with ID '{node_id}' not found"
                )]
            
            changes = []
            if new_text:
                node.text = new_text
                changes.append(f"text → '{new_text}'")
            if new_notes is not None:  # Allow empty string to clear notes
                node.notes = new_notes
                changes.append(f"notes → {len(new_notes)} characters")
            
            write_mindmap(mindmap, output_path)
            
            return [types.TextContent(
                type="text",
                text=f"✓ Updated node {node_id}: {', '.join(changes)}\n✓ Saved to: {output_path}"
            )]
        
        elif name == "delete_node":
            filepath = arguments["filepath"]
            node_id = arguments["node_id"]
            output_path = arguments.get("output_path", filepath)
            
            mindmap = read_mindmap(filepath)
            node = mindmap.get_node(node_id)
            
            if not node:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Node with ID '{node_id}' not found"
                )]
            
            if node.parent_id == "-1":
                return [types.TextContent(
                    type="text",
                    text="Error: Cannot delete the root node"
                )]
            
            # Count children to be deleted
            def count_descendants(n):
                count = 1
                for child in n.children:
                    count += count_descendants(child)
                return count
            
            deleted_count = count_descendants(node)
            
            # Remove from parent's children list
            parent = mindmap.get_node(node.parent_id)
            if parent:
                parent.children = [c for c in parent.children if c.id != node_id]
            
            # Remove from nodes dict (and all descendants)
            def remove_node_and_children(n):
                for child in n.children:
                    remove_node_and_children(child)
                if n.id in mindmap.nodes:
                    del mindmap.nodes[n.id]
            
            remove_node_and_children(node)
            
            write_mindmap(mindmap, output_path)
            
            return [types.TextContent(
                type="text",
                text=f"✓ Deleted node '{node.text}' and {deleted_count - 1} descendants\n✓ Saved to: {output_path}"
            )]
        
        elif name == "get_node_path":
            filepath = arguments["filepath"]
            node_id = arguments["node_id"]
            
            mindmap = read_mindmap(filepath)
            node = mindmap.get_node(node_id)
            
            if not node:
                return [types.TextContent(
                    type="text",
                    text=f"Node with ID '{node_id}' not found"
                )]
            
            # Build path from root to node
            path = []
            current = node
            while current:
                path.insert(0, {"id": current.id, "text": current.text})
                if current.parent_id == "-1":
                    break
                current = mindmap.get_node(current.parent_id)
            
            result = {
                "node_id": node_id,
                "path": path,
                "breadcrumb": " > ".join([p["text"] for p in path])
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "find_nodes_without_notes":
            filepath = arguments["filepath"]
            
            mindmap = read_mindmap(filepath)
            
            empty_nodes = [
                format_node_info(node, include_children=False)
                for node in mindmap.nodes.values()
                if not node.notes and node.parent_id != "-1"  # Exclude root
            ]
            
            result = {
                "count": len(empty_nodes),
                "nodes": empty_nodes
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simplemind-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
