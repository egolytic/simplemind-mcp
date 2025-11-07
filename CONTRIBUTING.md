# Contributing to SimpleMind MCP

Thank you for your interest in contributing to SimpleMind MCP! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub with:

1. A clear, descriptive title
2. Steps to reproduce (for bugs)
3. Expected behavior
4. Actual behavior
5. Your environment (OS, Python version, SimpleMind version)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes
4. Add tests if applicable
5. Run the test suite (`python -m unittest`)
6. Commit your changes (`git commit -m "Add feature"`)
7. Push to your fork (`git push origin feature-name`)
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_FORK/simplemind-mcp.git
cd simplemind-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Run tests
python -m unittest discover tests
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Comment complex logic

## Areas for Contribution

### High Priority

- **Batch Operations**: Add tools for bulk node updates
- **Merge/Split Tools**: Combine or split mind maps
- **Advanced Search**: Regular expression support, filter by attributes
- **Export Formats**: Add HTML, OPML, or other formats

### Medium Priority

- **Node Styling**: Support for colors, fonts, and shapes
- **Templates**: Pre-built mind map templates
- **Import Tools**: Import from other mind mapping formats
- **Performance**: Optimize for large mind maps (1000+ nodes)

### Nice to Have

- **Visualization**: Generate visual previews
- **Collaboration Features**: Merge changes from multiple users
- **Version Control**: Track changes over time
- **AI Integration**: Auto-generate content for nodes

## Testing

All new features should include tests:

```python
# tests/test_new_feature.py
import unittest
from simplemind_parser import YourNewFeature

class TestNewFeature(unittest.TestCase):
    def test_feature_works(self):
        # Your test here
        pass
```

## Documentation

- Update README.md if adding new tools
- Include docstrings in your code
- Add examples to examples.py if relevant

## Questions?

Feel free to open an issue for any questions about contributing!
