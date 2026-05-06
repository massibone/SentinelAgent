from typing import Dict, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
import os
import json

REPORT_DIR = os.environ.get("SENTINEL_REPORT_DIR", "generated_reports")

class ReportParams(BaseModel):
    title: str = Field(..., description="Report title")
    content: Dict[str, Any] = Field(..., description="Structured report body")
    author: str | None = None

def write_report(params: Dict[str, Any], audit_hook=None) -> Dict[str, Any]:
    """
    Writes a JSON report to REPORT_DIR. Calls audit_hook(event_dict) if provided.
    Returns metadata about the created report.
    """
    try:
        p = ReportParams(**params)
    except ValidationError as e:
        return {"ok": False, "error": "validation", "details": e.errors()}

    os.makedirs(REPORT_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in p.title).strip()
    filename = f"{timestamp}_{safe_title[:50].replace(' ', '_')}.json"
    path = os.path.join(REPORT_DIR, filename)

    payload = {
        "title": p.title,
        "author": p.author,
        "created_at": timestamp,
        "content": p.content,
    }

    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        result = {"ok": False, "error": "write_failed", "details": str(e)}
        if audit_hook:
            audit_hook({"action": "write_report", "result": result})
        return result

    result = {"ok": True, "path": path, "filename": filename}
    if audit_hook:
        audit_hook({"action": "write_report", "result": result})
    return result
