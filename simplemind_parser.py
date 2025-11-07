"""
SimpleMind Parser - Core functionality for reading and writing .smmx files

SimpleMind files (.smmx) are ZIP archives containing an XML file at document/mindmap.xml
This module provides clean Python interfaces for working with mind maps.
"""

import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class SimpleMindNode:
    """Represents a single node/topic in a mind map"""
    
    def __init__(self, id: str, text: str, parent_id: str = None, 
                 x: float = 0, y: float = 0, notes: str = "", 
                 guid: str = "", palette: str = "", colorinfo: str = "",
                 icon: str = "", url_link: str = "", layout_mode: str = "",
                 layout_direction: str = "", layout_flow: str = ""):
        self.id = id
        self.text = text
        self.parent_id = parent_id
        self.x = x
        self.y = y
        self.notes = notes
        self.guid = guid
        self.palette = palette
        self.colorinfo = colorinfo
        self.icon = icon  # SimpleMind Pro: icon reference
        self.url_link = url_link  # SimpleMind Pro: external URL
        self.layout_mode = layout_mode  # SimpleMind Pro: layout mode
        self.layout_direction = layout_direction  # SimpleMind Pro: layout direction
        self.layout_flow = layout_flow  # SimpleMind Pro: layout flow
        self.children = []
        self.parent_relation_guid = ""  # SimpleMind Pro: parent relation styling
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        result = {
            'id': self.id,
            'text': self.text,
            'parent_id': self.parent_id,
            'x': self.x,
            'y': self.y,
            'notes': self.notes,
            'guid': self.guid,
            'palette': self.palette,
            'colorinfo': self.colorinfo,
            'children': [child.to_dict() for child in self.children]
        }
        
        # Include Pro features if present
        if self.icon:
            result['icon'] = self.icon
        if self.url_link:
            result['url_link'] = self.url_link
        if self.layout_mode:
            result['layout'] = {
                'mode': self.layout_mode,
                'direction': self.layout_direction,
                'flow': self.layout_flow
            }
        
        return result
    
    def __repr__(self):
        return f"SimpleMindNode(id={self.id}, text={self.text}, children={len(self.children)})"


class SimpleMindMap:
    """Represents a complete SimpleMind mind map"""
    
    def __init__(self, title: str = "New Mind Map"):
        self.title = title
        self.nodes = {}  # id -> SimpleMindNode
        self.root_node = None
        self.guid = ""
        self.style = "system.bright-palette"
        self.zoom = 100
        self.scroll_x = 0
        self.scroll_y = 0
        self.contains_images = False  # SimpleMind Pro
        self.relations = []  # SimpleMind Pro: cross-links
        self.images = {}  # SimpleMind Pro: image hash -> binary data
    
    def add_node(self, node: SimpleMindNode):
        """Add a node to the mind map"""
        self.nodes[node.id] = node
        if node.parent_id == "-1":
            self.root_node = node
        elif node.parent_id in self.nodes:
            self.nodes[node.parent_id].children.append(node)
    
    def get_node(self, node_id: str) -> Optional[SimpleMindNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def search_nodes(self, query: str, search_notes: bool = True) -> List[SimpleMindNode]:
        """Search for nodes containing the query text"""
        query_lower = query.lower()
        results = []
        
        for node in self.nodes.values():
            if query_lower in node.text.lower():
                results.append(node)
            elif search_notes and query_lower in node.notes.lower():
                results.append(node)
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mind map to dictionary"""
        return {
            'title': self.title,
            'root': self.root_node.to_dict() if self.root_node else None,
            'total_nodes': len(self.nodes)
        }
    
    def to_markdown(self, max_depth: int = 10) -> str:
        """Convert mind map to hierarchical Markdown"""
        if not self.root_node:
            return ""
        
        lines = [f"# {self.root_node.text}\n"]
        if self.root_node.notes:
            lines.append(f"{self.root_node.notes}\n")
        
        def process_children(node: SimpleMindNode, depth: int):
            if depth > max_depth:
                return
            
            for child in node.children:
                # Add header
                lines.append(f"{'#' * (depth + 1)} {child.text}\n")
                
                # Add notes if present
                if child.notes:
                    lines.append(f"{child.notes}\n")
                
                # Process grandchildren
                process_children(child, depth + 1)
        
        process_children(self.root_node, 1)
        return "\n".join(lines)
    
    def __repr__(self):
        return f"SimpleMindMap(title={self.title}, nodes={len(self.nodes)})"


class SimpleMindParser:
    """Parser for SimpleMind .smmx files"""
    
    @staticmethod
    def read(filepath: str) -> SimpleMindMap:
        """
        Read a SimpleMind .smmx file and return a SimpleMindMap object
        
        Args:
            filepath: Path to the .smmx file
            
        Returns:
            SimpleMindMap object
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not filepath.suffix == '.smmx':
            raise ValueError(f"File must be .smmx format, got: {filepath.suffix}")
        
        # Extract XML from ZIP
        with zipfile.ZipFile(filepath, 'r') as z:
            xml_content = z.read('document/mindmap.xml')
        
        # Parse XML
        tree = ET.fromstring(xml_content)
        
        # Create mind map object
        mindmap = SimpleMindMap()
        
        # SimpleMind Pro: Extract images if present
        with zipfile.ZipFile(filepath, 'r') as z:
            for file_info in z.filelist:
                if file_info.filename.startswith('images/') and file_info.filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_hash = Path(file_info.filename).stem
                    mindmap.images[image_hash] = z.read(file_info.filename)
        
        # Parse metadata
        meta = tree.find('.//meta')
        if meta is not None:
            title_elem = meta.find('title')
            if title_elem is not None:
                mindmap.title = title_elem.get('text', 'Untitled')
            
            guid_elem = meta.find('guid')
            if guid_elem is not None:
                mindmap.guid = guid_elem.get('guid', '')
            
            style_elem = meta.find('style')
            if style_elem is not None:
                mindmap.style = style_elem.get('key', 'system.bright-palette')
            
            scroll_elem = meta.find('scrollstate')
            if scroll_elem is not None:
                mindmap.zoom = int(scroll_elem.get('zoom', '100'))
                mindmap.scroll_x = float(scroll_elem.get('x', '0'))
                mindmap.scroll_y = float(scroll_elem.get('y', '0'))
            
            # SimpleMind Pro: check for images
            images_elem = meta.find('images')
            if images_elem is not None:
                mindmap.contains_images = images_elem.get('containsImages', 'false').lower() == 'true'
        
        # Parse topics (nodes)
        topics = tree.findall('.//topic')
        
        # First pass: create all nodes
        for topic in topics:
            node_id = topic.get('id')
            parent_id = topic.get('parent')
            text = topic.get('text', '')
            x = float(topic.get('x', '0'))
            y = float(topic.get('y', '0'))
            guid = topic.get('guid', '')
            palette = topic.get('palette', '')
            colorinfo = topic.get('colorinfo', '')
            
            # SimpleMind Pro: icon reference
            icon = topic.get('icon', '')
            
            # Get notes if present
            notes = ""
            note_elem = topic.find('note')
            if note_elem is not None:
                notes = note_elem.text or ""
            
            # SimpleMind Pro: URL link
            url_link = ""
            link_elem = topic.find('link')
            if link_elem is not None:
                url_link = link_elem.get('urllink', '')
            
            # SimpleMind Pro: layout
            layout_mode = ""
            layout_direction = ""
            layout_flow = ""
            layout_elem = topic.find('layout')
            if layout_elem is not None:
                layout_mode = layout_elem.get('mode', '')
                layout_direction = layout_elem.get('direction', '')
                layout_flow = layout_elem.get('flow', '')
            
            node = SimpleMindNode(
                id=node_id,
                text=text,
                parent_id=parent_id,
                x=x,
                y=y,
                notes=notes,
                guid=guid,
                palette=palette,
                colorinfo=colorinfo,
                icon=icon,
                url_link=url_link,
                layout_mode=layout_mode,
                layout_direction=layout_direction,
                layout_flow=layout_flow
            )
            
            # SimpleMind Pro: parent relation styling
            parent_rel_elem = topic.find('parent-relation')
            if parent_rel_elem is not None:
                node.parent_relation_guid = parent_rel_elem.get('guid', '')
            
            mindmap.add_node(node)
        
        # SimpleMind Pro: Parse relations (cross-links)
        relations = tree.find('.//relations')
        if relations is not None:
            for relation in relations.findall('relation'):
                mindmap.relations.append({
                    'guid': relation.get('guid', ''),
                    'source': relation.get('source', ''),
                    'target': relation.get('target', '')
                })
        
        return mindmap
    
    @staticmethod
    def write(mindmap: SimpleMindMap, filepath: str):
        """
        Write a SimpleMindMap object to a .smmx file
        
        Args:
            mindmap: SimpleMindMap object to write
            filepath: Output path for the .smmx file
        """
        filepath = Path(filepath)
        
        # Build XML structure
        root = ET.Element('simplemind-mindmaps')
        root.set('doc-version', '3')
        root.set('generator', 'SimpleMindMCP')
        root.set('gen-version', '1.0.0')
        
        mindmap_elem = ET.SubElement(root, 'mindmap')
        
        # Meta section
        meta = ET.SubElement(mindmap_elem, 'meta')
        
        guid_elem = ET.SubElement(meta, 'guid')
        guid_elem.set('guid', mindmap.guid or 'GENERATED_GUID')
        
        title_elem = ET.SubElement(meta, 'title')
        title_elem.set('text', mindmap.title)
        
        # SimpleMind Pro: images metadata
        if mindmap.contains_images or mindmap.images:
            images_elem = ET.SubElement(meta, 'images')
            images_elem.set('containsImages', 'true')
        
        style_elem = ET.SubElement(meta, 'style')
        style_elem.set('key', mindmap.style)
        
        numbering_elem = ET.SubElement(meta, 'auto-numbering')
        numbering_elem.set('style', 'disabled')
        
        scroll_elem = ET.SubElement(meta, 'scrollstate')
        scroll_elem.set('zoom', str(mindmap.zoom))
        scroll_elem.set('x', f"{mindmap.scroll_x:.2f}")
        scroll_elem.set('y', f"{mindmap.scroll_y:.2f}")
        
        if mindmap.root_node:
            selection_elem = ET.SubElement(meta, 'selection')
            selection_elem.set('guid', mindmap.root_node.guid)
            selection_elem.set('type', 'node')
            selection_elem.set('id', mindmap.root_node.id)
            
            main_elem = ET.SubElement(meta, 'main-centraltheme')
            main_elem.set('id', mindmap.root_node.id)
        
        # Topics section
        topics_elem = ET.SubElement(mindmap_elem, 'topics')
        
        def add_topic_element(node: SimpleMindNode):
            topic = ET.SubElement(topics_elem, 'topic')
            topic.set('id', node.id)
            topic.set('parent', node.parent_id)
            topic.set('guid', node.guid)
            topic.set('x', f"{node.x:.2f}")
            topic.set('y', f"{node.y:.2f}")
            
            if node.palette:
                topic.set('palette', node.palette)
            if node.colorinfo:
                topic.set('colorinfo', node.colorinfo)
            
            # SimpleMind Pro: icon
            if node.icon:
                topic.set('icon', node.icon)
            
            topic.set('text', node.text)
            topic.set('textfmt', 'plain')
            
            # SimpleMind Pro: parent relation
            if node.parent_relation_guid:
                parent_rel = ET.SubElement(topic, 'parent-relation')
                parent_rel.set('guid', node.parent_relation_guid)
            
            # SimpleMind Pro: URL link
            if node.url_link:
                link = ET.SubElement(topic, 'link')
                link.set('urllink', node.url_link)
            
            if node.notes:
                note = ET.SubElement(topic, 'note')
                note.text = node.notes
            
            # SimpleMind Pro: layout
            if node.layout_mode:
                layout = ET.SubElement(topic, 'layout')
                layout.set('mode', node.layout_mode)
                if node.layout_direction:
                    layout.set('direction', node.layout_direction)
                if node.layout_flow:
                    layout.set('flow', node.layout_flow)
            
            # Recursively add children
            for child in node.children:
                add_topic_element(child)
        
        # Add all nodes starting from root(s)
        # SimpleMind Pro allows multiple root nodes (floating nodes)
        root_nodes = [node for node in mindmap.nodes.values() if node.parent_id == "-1"]
        for root_node in root_nodes:
            add_topic_element(root_node)
        
        # SimpleMind Pro: Add relations (cross-links)
        if mindmap.relations:
            relations_elem = ET.SubElement(mindmap_elem, 'relations')
            for rel in mindmap.relations:
                relation = ET.SubElement(relations_elem, 'relation')
                relation.set('guid', rel['guid'])
                relation.set('source', rel['source'])
                relation.set('target', rel['target'])
        
        # Add node-groups (empty for now)
        ET.SubElement(mindmap_elem, 'node-groups')
        
        # Convert to string with XML declaration
        xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        
        # Pretty print (optional but nice)
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(encoding='utf-8')
        
        # Write to ZIP file
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('document/mindmap.xml', pretty_xml)
            
            # SimpleMind Pro: Write images
            for image_hash, image_data in mindmap.images.items():
                z.writestr(f'images/{image_hash}.png', image_data)


# Convenience functions
def read_mindmap(filepath: str) -> SimpleMindMap:
    """Read a SimpleMind file"""
    return SimpleMindParser.read(filepath)


def write_mindmap(mindmap: SimpleMindMap, filepath: str):
    """Write a SimpleMind file"""
    SimpleMindParser.write(mindmap, filepath)


def export_to_markdown(filepath: str, output_path: Optional[str] = None) -> str:
    """
    Export a SimpleMind file to Markdown
    
    Args:
        filepath: Path to .smmx file
        output_path: Optional path to save markdown file
        
    Returns:
        Markdown content as string
    """
    mindmap = read_mindmap(filepath)
    markdown = mindmap.to_markdown()
    
    if output_path:
        Path(output_path).write_text(markdown, encoding='utf-8')
    
    return markdown


def export_to_json(filepath: str, output_path: Optional[str] = None) -> str:
    """
    Export a SimpleMind file to JSON
    
    Args:
        filepath: Path to .smmx file
        output_path: Optional path to save JSON file
        
    Returns:
        JSON content as string
    """
    mindmap = read_mindmap(filepath)
    data = mindmap.to_dict()
    json_str = json.dumps(data, indent=2)
    
    if output_path:
        Path(output_path).write_text(json_str, encoding='utf-8')
    
    return json_str
