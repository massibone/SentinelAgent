from typing import Dict, Any
from pydantic import BaseModel, Field, ValidationError
import os

class ExtractParams(BaseModel):
    path: str = Field(..., description="File path to read (PDF or text)")
    max_pages: int = Field(5, ge=1, le=100, description="Max pages to process")

def extract_metadata(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal metadata extractor:
    - validates input
    - returns dict with filename, size, and dummy text/length
    """
    try:
        p = ExtractParams(**params)
    except ValidationError as e:
        return {"ok": False, "error": "validation", "details": e.errors()}

    if not os.path.exists(p.path):
        return {"ok": False, "error": "not_found", "path": p.path}

    stat = os.stat(p.path)
    # Very simple extraction: for PDFs/text you would replace with pypdf/pdfplumber
    try:
        with open(p.path, "rb") as f:
            raw = f.read(2048)  # sample head bytes
    except Exception as e:
        return {"ok": False, "error": "read_error", "details": str(e)}

    metadata = {
        "ok": True,
        "file": os.path.basename(p.path),
        "bytes": stat.st_size,
        "sample_head_len": len(raw),
        "max_pages_considered": p.max_pages,
    }
    return metadata
