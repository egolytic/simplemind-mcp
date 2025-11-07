from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simplemind-mcp",
    version="1.0.0",
    author="SimpleMind MCP Contributors",
    description="A Model Context Protocol server for SimpleMind mind map files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/egolytic/simplemind-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.7",
    install_requires=[
        "mcp>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "simplemind-mcp=simplemind_mcp_server:main",
        ],
    },
)
