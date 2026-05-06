from typing import Dict, Any
from pydantic import BaseModel, Field, ValidationError
from uuid import uuid4
from datetime import datetime
import threading

# In-memory simple approval store (replace with DB/queue in prod)
_APPROVAL_STORE: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()

class ApprovalParams(BaseModel):
    action: str = Field(..., description="Action that requires approval")
    actor: str = Field(..., description="Requesting agent or user id")
    reason: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

def request_approval(params: Dict[str, Any], audit_hook=None) -> Dict[str, Any]:
    """
    Creates an approval request record and returns a token.
    Use external process to set status -> approved/denied.
    audit_hook(event_dict) is called with creation event.
    """
    try:
        p = ApprovalParams(**params)
    except ValidationError as e:
        return {"ok": False, "error": "validation", "details": e.errors()}

    token = str(uuid4())
    record = {
        "token": token,
        "action": p.action,
        "actor": p.actor,
        "reason": p.reason,
        "metadata": p.metadata,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "decided_at": None,
        "decision": None,
        "decider": None,
    }
    with _LOCK:
        _APPROVAL_STORE[token] = record

    if audit_hook:
        audit_hook({"action": "request_approval", "token": token, "record": record})

    return {"ok": True, "token": token, "status": "pending"}

def get_approval(token: str) -> Dict[str, Any] | None:
    return _APPROVAL_STORE.get(token)

def decide_approval(token: str, approve: bool, decider: str, note: str | None = None, audit_hook=None) -> Dict[str, Any]:
    with _LOCK:
        rec = _APPROVAL_STORE.get(token)
        if not rec:
            return {"ok": False, "error": "not_found", "token": token}
        if rec["status"] != "pending":
            return {"ok": False, "error": "already_decided", "status": rec["status"]}

        rec["status"] = "approved" if approve else "denied"
        rec["decision"] = {"by": decider, "note": note}
        rec["decided_at"] = datetime.utcnow().isoformat() + "Z"

    if audit_hook:
        audit_hook({"action": "decide_approval", "token": token, "result": rec})
    return {"ok": True, "token": token, "status": rec["status"]}
