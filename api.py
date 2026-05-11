from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
import uvicorn

from agent.identity import DEFAULT_IDENTITY
from agent.registry import REGISTRY, get_tool
from agent.policy import PolicyEngine  # assume PolicyEngine(rules: dict) or adapt
from agent.audit import AuditLogger     # assume AuditLogger.write(event: dict)
from agent.tools import request_approval

app = FastAPI(title="SentinelAgent API", version="0.1")

# --- Simple in-memory policy + audit for the skeleton ---
# Replace with your actual policy loader/engine
_DEFAULT_RULES = {
    "list_documents": {"allow": True},
    "read_document": {"allow": True},
    "extract_metadata": {"allow": True},
    "write_report": {"allow": True},
    "request_approval": {"allow": True},
}
_policy = PolicyEngine(rules=_DEFAULT_RULES)
_audit = AuditLogger()  # adapt constructor if different

# --- Pydantic models ---
class ToolCall(BaseModel):
    tool_name: str
    params: Dict[str, Any] = {}
    requester: Optional[str] = None

class ToolListResponse(BaseModel):
    tools: Dict[str, str]

# --- Endpoints ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/agent/info")
def agent_info():
    return {"name": DEFAULT_IDENTITY.name, "purpose": DEFAULT_IDENTITY.purpose}

@app.get("/tools")
def list_tools():
    return {"tools": list(REGISTRY.keys())}

@app.post("/tools/run")
def run_tool(call: ToolCall):
    tool_name = call.tool_name
    params = call.params or {}
    requester = call.requester or "unknown"

    # audit: record request
    _audit.write({"event": "tool_call.request", "tool": tool_name, "params": params, "requester": requester})

    # policy: check allowed
    if not _policy.is_allowed(tool_name):
        _audit.write({"event": "tool_call.denied", "tool": tool_name, "reason": "policy_denied", "requester": requester})
        raise HTTPException(status_code=403, detail="Tool not allowed by policy")

    # identity: check agent allowed_tools
    if tool_name not in DEFAULT_IDENTITY.allowed_tools:
        _audit.write({"event": "tool_call.denied", "tool": tool_name, "reason": "identity_disallowed", "requester": requester})
        raise HTTPException(status_code=403, detail="Tool not allowed by agent identity")

    # approval: if action requires human approval, create request and return pending
    if tool_name in DEFAULT_IDENTITY.human_approval_required_for:
        app_resp = request_approval({"action": tool_name, "actor": requester, "metadata": params}, audit_hook=_audit.write)
        return {"status": "pending_approval", "approval": app_resp}

    # find tool
    fn = get_tool(tool_name)
    if fn is None:
        _audit.write({"event": "tool_call.failed", "tool": tool_name, "reason": "not_registered", "requester": requester})
        raise HTTPException(status_code=404, detail="Tool not found")

    # execute tool (pass audit_hook if accepted signature)
    try:
        # many tools accept (params) or (params, audit_hook)
        try:
            result = fn(params)
        except TypeError:
            # try call with audit_hook
            result = fn(params, audit_hook=_audit.write)
    except Exception as e:
        _audit.write({"event": "tool_call.error", "tool": tool_name, "error": str(e), "requester": requester})
        raise HTTPException(status_code=500, detail=f"Tool execution error: {e}")

    _audit.write({"event": "tool_call.completed", "tool": tool_name, "result": getattr(result, "__dict__", result), "requester": requester})
    return {"status": "ok", "result": result}

# Run server with uvicorn when executed directly
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
