#!/usr/bin/env python3
"""
Test suite for SimpleMind parser
"""

import sys
import os
from pathlib import Path
import tempfile
import unittest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simplemind_parser import (
    SimpleMindMap,
    SimpleMindNode,
    SimpleMindParser,
    read_mindmap,
    write_mindmap,
    export_to_markdown,
    export_to_json
)


class TestSimpleMindParser(unittest.TestCase):
    """Test SimpleMind parser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.smmx")
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_mindmap(self):
        """Test creating a new mind map"""
        mindmap = SimpleMindMap("Test Map")
        self.assertEqual(mindmap.title, "Test Map")
        self.assertEqual(len(mindmap.nodes), 0)
    
    def test_add_node(self):
        """Test adding nodes to a mind map"""
        mindmap = SimpleMindMap("Test Map")
        
        # Add root node
        root = SimpleMindNode(
            id="0",
            text="Root",
            parent_id="-1",
            x=0,
            y=0,
            guid="ROOT"
        )
        mindmap.add_node(root)
        
        self.assertEqual(len(mindmap.nodes), 1)
        self.assertEqual(mindmap.root_node.text, "Root")
    
    def test_add_child_node(self):
        """Test adding child nodes"""
        mindmap = SimpleMindMap("Test Map")
        
        # Add root
        root = SimpleMindNode(
            id="0",
            text="Root",
            parent_id="-1",
            x=0,
            y=0
        )
        mindmap.add_node(root)
        
        # Add child
        child = SimpleMindNode(
            id="1",
            text="Child",
            parent_id="0",
            x=100,
            y=0
        )
        mindmap.add_node(child)
        
        self.assertEqual(len(mindmap.nodes), 2)
        self.assertEqual(len(mindmap.root_node.children), 1)
        self.assertEqual(mindmap.root_node.children[0].text, "Child")
    
    def test_search_nodes(self):
        """Test searching for nodes"""
        mindmap = SimpleMindMap("Test Map")
        
        # Add nodes
        root = SimpleMindNode(id="0", text="Root", parent_id="-1")
        mindmap.add_node(root)
        
        node1 = SimpleMindNode(id="1", text="Python Code", parent_id="0", notes="Python programming")
        mindmap.add_node(node1)
        
        node2 = SimpleMindNode(id="2", text="JavaScript", parent_id="0", notes="JS code")
        mindmap.add_node(node2)
        
        # Search
        results = mindmap.search_nodes("python", search_notes=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].text, "Python Code")
        
        results = mindmap.search_nodes("code", search_notes=True)
        self.assertEqual(len(results), 2)
    
    def test_to_markdown(self):
        """Test converting to markdown"""
        mindmap = SimpleMindMap("Test Map")
        
        root = SimpleMindNode(id="0", text="Root", parent_id="-1", notes="Root notes")
        mindmap.add_node(root)
        
        child = SimpleMindNode(id="1", text="Child", parent_id="0", notes="Child notes")
        mindmap.add_node(child)
        
        markdown = mindmap.to_markdown()
        self.assertIn("# Root", markdown)
        self.assertIn("Root notes", markdown)
        self.assertIn("## Child", markdown)
        self.assertIn("Child notes", markdown)
    
    def test_to_dict(self):
        """Test converting to dictionary"""
        mindmap = SimpleMindMap("Test Map")
        
        root = SimpleMindNode(id="0", text="Root", parent_id="-1")
        mindmap.add_node(root)
        
        data = mindmap.to_dict()
        self.assertEqual(data['title'], "Test Map")
        self.assertEqual(data['total_nodes'], 1)
        self.assertEqual(data['root']['text'], "Root")
    
    def test_write_and_read(self):
        """Test writing and reading a mind map"""
        # Create mind map
        mindmap = SimpleMindMap("Test Map")
        
        root = SimpleMindNode(
            id="0",
            text="Root",
            parent_id="-1",
            x=400,
            y=400,
            notes="Test notes",
            guid="ROOT_GUID"
        )
        mindmap.add_node(root)
        
        child = SimpleMindNode(
            id="1",
            text="Child",
            parent_id="0",
            x=500,
            y=400,
            guid="CHILD_GUID"
        )
        mindmap.add_node(child)
        
        # Write to file
        write_mindmap(mindmap, self.test_file)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Read it back
        loaded = read_mindmap(self.test_file)
        self.assertEqual(loaded.title, "Test Map")
        self.assertEqual(len(loaded.nodes), 2)
        self.assertEqual(loaded.root_node.text, "Root")
        self.assertEqual(loaded.root_node.notes, "Test notes")
        self.assertEqual(len(loaded.root_node.children), 1)
    
    def test_pro_features(self):
        """Test SimpleMind Pro features"""
        mindmap = SimpleMindMap("Pro Test")
        
        root = SimpleMindNode(
            id="0",
            text="Root",
            parent_id="-1",
            icon="star",
            url_link="https://example.com",
            layout_mode="horizontal",
            layout_direction="right",
            layout_flow="linear"
        )
        mindmap.add_node(root)
        
        # Check Pro features are preserved
        self.assertEqual(root.icon, "star")
        self.assertEqual(root.url_link, "https://example.com")
        self.assertEqual(root.layout_mode, "horizontal")
        
        # Convert to dict should include Pro features
        data = root.to_dict()
        self.assertEqual(data['icon'], "star")
        self.assertEqual(data['url_link'], "https://example.com")
        self.assertIn('layout', data)
        self.assertEqual(data['layout']['mode'], "horizontal")


if __name__ == '__main__':
    unittest.main()
