# SourceCompact

**SourceCompact** is a utility tool that collapses an entire codebase into a single file. This is especially useful for feeding source code into AI models or LLMs that require full context in a linear, compact format.

## Features

- Recursively reads project directories
- Concatenates all source files into one unified file
- Preserves relative file paths and boundaries as comments
- Supports multiple programming languages
- Ignores unnecessary files and folders (e.g., `.git`, `node_modules`, `__pycache__`, etc.)

## Use Cases

- Feed complete codebase context to AI/LLM
- Analyze project structure in a single glance
- Archive source code in a simplified format
- Assist in static code analysis pipelines

## Installation

```bash
git clone https://github.com/yourusername/sourcecompact.git
cd sourcecompact
pip install -r requirements.txt
