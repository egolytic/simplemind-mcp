#!/usr/bin/env python3
"""
SimpleMind MCP - Example Usage Scripts

Run these examples to see what the SimpleMind parser can do!
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from simplemind_parser import (
    read_mindmap,
    write_mindmap,
    export_to_markdown,
    export_to_json,
    SimpleMindMap,
    SimpleMindNode
)


def example_1_read_and_explore():
    """Example 1: Read a mind map and explore its structure"""
    print("=" * 60)
    print("EXAMPLE 1: Reading and Exploring a Mind Map")
    print("=" * 60)
    
    # Update this path to your actual .smmx file
    filepath = input("Enter path to your .smmx file: ").strip()
    
    try:
        # Load the mind map
        mindmap = read_mindmap(filepath)
        
        print(f"\n✓ Loaded: {mindmap.title}")
        print(f"  Total nodes: {len(mindmap.nodes)}")
        print(f"  Root node: {mindmap.root_node.text}")
        
        # Show top-level structure
        print(f"\n  Top-level branches:")
        for i, child in enumerate(mindmap.root_node.children, 1):
            print(f"    {i}. {child.text} ({len(child.children)} children)")
        
        return mindmap
    
    except Exception as e:
        print(f"Error: {e}")
        return None


def example_2_search_nodes(mindmap):
    """Example 2: Search for nodes"""
    if not mindmap:
        print("No mind map loaded!")
        return
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Searching Nodes")
    print("=" * 60)
    
    query = input("\nEnter search term: ").strip()
    
    results = mindmap.search_nodes(query, search_notes=True)
    
    if not results:
        print(f"No results found for '{query}'")
        return
    
    print(f"\n✓ Found {len(results)} nodes matching '{query}':")
    for i, node in enumerate(results, 1):
        has_notes = "📝" if node.notes else "📄"
        print(f"  {i}. {has_notes} {node.text} (ID: {node.id})")
        if node.notes and len(node.notes) < 100:
            print(f"     Notes: {node.notes}")
        elif node.notes:
            print(f"     Notes: {node.notes[:100]}...")


def example_3_find_incomplete(mindmap):
    """Example 3: Find nodes without notes"""
    if not mindmap:
        print("No mind map loaded!")
        return
    
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Finding Incomplete Topics")
    print("=" * 60)
    
    empty_nodes = [
        node for node in mindmap.nodes.values()
        if not node.notes and node.parent_id != "-1"
    ]
    
    if not empty_nodes:
        print("\n✓ All nodes have content! Great job!")
        return
    
    print(f"\n✓ Found {len(empty_nodes)} nodes without notes:")
    for i, node in enumerate(empty_nodes, 1):
        # Get parent for context
        parent = mindmap.get_node(node.parent_id)
        parent_text = parent.text if parent else "Unknown"
        print(f"  {i}. {node.text} (under '{parent_text}', ID: {node.id})")
    
    return empty_nodes


def example_4_add_node(mindmap, filepath):
    """Example 4: Add a new node"""
    if not mindmap:
        print("No mind map loaded!")
        return
    
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Adding a New Node")
    print("=" * 60)
    
    print("\nAvailable parent nodes:")
    for i, (node_id, node) in enumerate(list(mindmap.nodes.items())[:10], 1):
        print(f"  {i}. {node.text} (ID: {node_id})")
    
    parent_id = input("\nEnter parent node ID: ").strip()
    
    if parent_id not in mindmap.nodes:
        print(f"Error: Node ID '{parent_id}' not found")
        return
    
    text = input("Enter text for new node: ").strip()
    notes = input("Enter notes (optional): ").strip()
    
    # Generate new ID
    new_id = str(max([int(nid) for nid in mindmap.nodes.keys()]) + 1)
    
    # Get parent position
    parent = mindmap.get_node(parent_id)
    new_x = parent.x + 100
    new_y = parent.y + (len(parent.children) * 50)
    
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
    
    # Save
    output_path = filepath.replace('.smmx', '_modified.smmx')
    write_mindmap(mindmap, output_path)
    
    print(f"\n✓ Added node '{text}' with ID {new_id}")
    print(f"✓ Saved to: {output_path}")


def example_5_export(mindmap, filepath):
    """Example 5: Export to different formats"""
    if not mindmap:
        print("No mind map loaded!")
        return
    
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Exporting Mind Map")
    print("=" * 60)
    
    print("\nChoose export format:")
    print("  1. Markdown (hierarchical)")
    print("  2. JSON (structured data)")
    print("  3. Both")
    
    choice = input("\nYour choice (1-3): ").strip()
    
    base_path = filepath.replace('.smmx', '')
    
    if choice in ['1', '3']:
        md_path = f"{base_path}_export.md"
        markdown = export_to_markdown(filepath, md_path)
        print(f"\n✓ Exported to Markdown: {md_path}")
        print(f"  Preview (first 300 chars):")
        print(f"  {markdown[:300]}...")
    
    if choice in ['2', '3']:
        json_path = f"{base_path}_export.json"
        json_output = export_to_json(filepath, json_path)
        print(f"\n✓ Exported to JSON: {json_path}")
        print(f"  File size: {len(json_output)} characters")


def example_6_create_new():
    """Example 6: Create a brand new mind map"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Creating a New Mind Map")
    print("=" * 60)
    
    title = input("\nEnter mind map title: ").strip()
    
    # Create new mind map
    mindmap = SimpleMindMap(title=title)
    
    # Create root node
    root = SimpleMindNode(
        id="0",
        text=title,
        parent_id="-1",
        x=400,
        y=400,
        guid="ROOT_GUID_0"
    )
    mindmap.add_node(root)
    
    # Add a few child nodes
    print("\nAdd some initial topics (press Enter with empty text to finish):")
    
    for i in range(1, 100):
        topic = input(f"  Topic {i}: ").strip()
        if not topic:
            break
        
        child = SimpleMindNode(
            id=str(i),
            text=topic,
            parent_id="0",
            x=400 + (i % 4) * 150,
            y=300 + (i // 4) * 100,
            guid=f"GUID_{i}"
        )
        mindmap.add_node(child)
    
    # Save
    filename = f"{title.replace(' ', '_')}.smmx"
    write_mindmap(mindmap, filename)
    
    print(f"\n✓ Created new mind map: {filename}")
    print(f"  Title: {title}")
    print(f"  Nodes: {len(mindmap.nodes)}")


def main():
    """Run the examples"""
    print("\n" + "=" * 60)
    print("SimpleMind Parser - Example Scripts")
    print("=" * 60)
    
    while True:
        print("\n\nChoose an example:")
        print("  1. Read and explore a mind map")
        print("  2. Search for nodes")
        print("  3. Find incomplete topics (no notes)")
        print("  4. Add a new node")
        print("  5. Export to Markdown/JSON")
        print("  6. Create a brand new mind map")
        print("  0. Exit")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == '0':
            print("\nGoodbye! 👋")
            break
        
        # For examples 1-5, we need a mind map
        mindmap = None
        filepath = None
        
        if choice in ['1', '2', '3', '4', '5']:
            if choice == '1':
                mindmap = example_1_read_and_explore()
                if mindmap:
                    filepath = input("\nEnter the same path again for other examples: ").strip()
            else:
                filepath = input("Enter path to your .smmx file: ").strip()
                try:
                    mindmap = read_mindmap(filepath)
                    print(f"✓ Loaded: {mindmap.title}")
                except Exception as e:
                    print(f"Error loading file: {e}")
                    continue
        
        if choice == '2':
            example_2_search_nodes(mindmap)
        elif choice == '3':
            example_3_find_incomplete(mindmap)
        elif choice == '4':
            example_4_add_node(mindmap, filepath)
        elif choice == '5':
            example_5_export(mindmap, filepath)
        elif choice == '6':
            example_6_create_new()
        elif choice != '1':
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
