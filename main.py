# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse , Response
from fastapi.middleware.cors import CORSMiddleware
import os
import zipfile
import shutil
import uuid
import re
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel
import tempfile
import logging
import magic


app = FastAPI(title="Source Fold API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to store uploaded files temporarily
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class FilterRequest(BaseModel):
    uuid: str
    include_extensions: Optional[List[str]] = None
    exclude_extensions: Optional[List[str]] = None
    include_files: Optional[List[str]] = None
    exclude_files: Optional[List[str]] = None
    include_folders: Optional[List[str]] = None
    exclude_folders: Optional[List[str]] = None
    include_regex: Optional[str] = None
    exclude_regex: Optional[str] = None

def get_folder_structure(directory: Path) -> Dict:
    """Recursively build folder structure as nested JSON."""
    structure = {"name": directory.name, "type": "folder", "children": []}
    try:
        for item in directory.iterdir():
            if item.is_dir():
                structure["children"].append(get_folder_structure(item))
            else:
                mime_type = magic.from_file(item, mime=True)

                textual_application_mimetypes = [
                    "inode/x-empty", 
                    'application/json',
                    "application/json",
                    "application/javascript",
                    "application/xml",
                    "application/x-www-form-urlencoded",
                    # "application/sql",
                    # "application/graphql",
                    "application/ld+json",
                    "application/vnd.api+json",
                    "application/x-sh",
                    "application/x-python",
                    "application/x-httpd-php",
                    "application/x-yaml",
                    "application/x-markdown",
                    "application/x-perl",
                    "application/x-latex",
                    "application/x-c",
                    "application/x-java",
                    "application/x-tcl",
                    "application/x-ruby",
                    "application/x-shellscript",
                    "application/x-ksh",
                    "application/x-bash",
                    "application/x-zsh",
                    "application/x-csh",
                    "application/x-scala",
                    "application/x-lisp",
                    "application/x-haskell",
                    "application/x-sql",
                    "application/x-php",  # sometimes used interchangeably
                    "application/x-aspx",
                    "application/x-typescript",
                    "application/x-jsonlines",
                    "application/vnd.curl",
                ]


                if mime_type.startswith("text/") or mime_type in textual_application_mimetypes:
                    is_text = True
                else:
                    is_text = False

                structure["children"].append({"name": item.name, "type": "file", "mime_type": mime_type, "is_text": is_text})
    except Exception as e:
        logger.error(f"Error reading directory {directory}: {e}")
    return structure

def read_file_content(file_path: Path) -> str:
    """Read file content with proper encoding handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return f"Error: Could not read file content ({e})"
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"Error: Could not read file content ({e})"

def generate_markdown(directory: Path, filters: FilterRequest) -> str:
    """Generate markdown content based on filters."""
    markdown = []
    
    def should_include_file(file_path: Path) -> bool:
        """Check if file should be included based on filters."""
        file_name = file_path.name
        file_ext = file_path.suffix.lower()
        relative_path = str(file_path.relative_to(directory))

        # Extension filters
        if filters.include_extensions and file_ext[1:] not in [ext.lower() for ext in filters.include_extensions]:
            return False
        if filters.exclude_extensions and file_ext[1:] in [ext.lower() for ext in filters.exclude_extensions]:
            return False

        # File name filters
        if filters.include_files and file_name not in filters.include_files:
            return False
        if filters.exclude_files and file_name in filters.exclude_files:
            return False

        # Folder filters
        folder_path = str(file_path.parent.relative_to(directory))
        if filters.include_folders and folder_path not in filters.include_folders:
            return False
        if filters.exclude_folders and folder_path in filters.exclude_folders:
            return False

        # Regex filters
        if filters.include_regex and not re.search(filters.include_regex, relative_path):
            return False
        if filters.exclude_regex and re.search(filters.exclude_regex, relative_path):
            return False

        return True

    def process_directory(current_dir: Path):
        """Recursively process directory and generate markdown."""
        try:
            for item in sorted(current_dir.iterdir()):  # Sort for consistent output
                if item.is_dir():
                    process_directory(item)
                else:
                    if should_include_file(item):
                        content = read_file_content(item)
                        relative_path = item.relative_to(directory)
                        markdown.append(f"----\n`{relative_path}`\n```\n{content}\n```")
        except Exception as e:
            logger.error(f"Error processing directory {current_dir}: {e}")

    process_directory(directory)
    return "\n".join(markdown)

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.post("/upload/")
async def upload_zip(file: UploadFile = File(...)):
    """Handle zip file upload and return UUID and folder structure."""
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only zip files are allowed")

    file_uuid = str(uuid.uuid4())
    extract_path = UPLOAD_DIR / file_uuid
    
    try:
        # Create temporary directory
        extract_path.mkdir(parents=True, exist_ok=True)
        
        # Save and extract zip file
        zip_path = extract_path / file.filename
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Remove the zip file after extraction
        zip_path.unlink()

        # Get folder structure
        structure = get_folder_structure(extract_path)
        
        return JSONResponse(content={"uuid": file_uuid, "structure": structure})
    
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        shutil.rmtree(extract_path, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error processing upload: {e}")

@app.post("/markdown/")
async def create_markdown(filters: FilterRequest):
    """Generate markdown file based on filters and return it."""
    extract_path = UPLOAD_DIR / filters.uuid
    
    if not extract_path.exists():
        raise HTTPException(status_code=404, detail="UUID not found")

    try:
        markdown_content = generate_markdown(extract_path, filters)
        
        # Check file size (in bytes, 65KB = 65 * 1024)
        # content_size = len(markdown_content.encode("utf-8"))
        output_file = extract_path / "output.md"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        
        
        return Response(content=markdown_content)
    
    except Exception as e:
        logger.error(f"Error generating markdown: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating markdown: {e}")

@app.get("/download/{uuid}/{filename}")
async def download_markdown(uuid: str, filename: str):
    """Download the generated markdown file."""
    file_path = UPLOAD_DIR / uuid / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/markdown"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
