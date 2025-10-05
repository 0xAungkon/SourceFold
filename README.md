# SourceFold - The Ultimate Tool For Vibe Coders to Utilize AI

**SourceFold** is a utility tool that collapses an entire codebase into a single file. This is especially useful for feeding source code into AI models or LLMs that require full context in a linear, compact format.

<img src="static/images/gui.png" alt="GUI Preview" width="600"/>  
<img src="static/images/output1.png" alt="Output Example" width="600"/>  

## How To Use It

* Upload your codebase and get all the files combined into a single markdown file.
* Upload it to [Qwen](https://chat.qwen.ai/) or any other AI model.
* The AI now understands your entire codebase context.

## Features

* Recursively reads project directories
* Concatenates all source files into one unified file
* Preserves relative file paths and boundaries as comments
* Supports multiple programming languages
* Ignores unnecessary files and folders (e.g., `.git`, `node_modules`, `__pycache__`, etc.)
* **Now includes CLI support for direct terminal usage**

## Use Cases

* Feed complete codebase context to AI/LLM
* Analyze project structure in a single glance
* Archive source code in a simplified format
* Assist in static code analysis pipelines
* Generate unified markdown files directly via CLI

## Installation

```bash
git clone https://github.com/0xAungkon/SourceFold.git
cd SourceFold
pip install -r requirements.txt
make start
```

Or use Docker:

```bash
docker compose up -d
```

**Access the app at:** [http://localhost:8000](http://localhost:8000)

---

## CLI Usage

You can now use SourceFold directly from the command line.

### Example 1 — Install CLI System-Wide (Root Access Required)

```bash
sudo wget -O /bin/sourcefold-cli https://raw.githubusercontent.com/0xAungkon/SourceFold/refs/heads/main/sourcefold-cli.py
sudo chmod +x /bin/sourcefold-cli
```

### Example 2 — Run CLI

```bash
sourcefold-cli --output .docs/combined_code.md --folders src,test --extensions .jsx,.js
```

### Example 3 — Run Without Installation

```bash
curl -s https://raw.githubusercontent.com/0xAungkon/SourceFold/refs/heads/main/sourcefold-cli.py | python3 - --output /tmp/combined_codebase.md --folders src,test --extensions .py,.html
```

---

## License

MIT License © 2025 0xAungkon
