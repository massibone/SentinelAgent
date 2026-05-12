"""
api.py — FastAPI skeleton for SentinelAgent.

Endpoints:
    GET  /health          → liveness check
    GET  /agent/info      → agent name and purpose
    GET  /tools           → list registered tools
    POST /tools/run       → execute a tool through identity → policy → approval gates
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.identity import DEFAULT_IDENTITY
from agent.policy import AgentPolicy, check_permission, PolicyViolationError
from agent.audit import AuditLogger
import agent.registry as registry

# Importing tools triggers registration via tools/__init__.py
import tools  # noqa: F401

app = FastAPI(title="SentinelAgent API", version="0.1")

_policy = AgentPolicy()
_audit = AuditLogger()


# --- Pydantic models ---

class ToolCallRequest(BaseModel):
    tool_name: str
    params: dict[str, Any] = {}
    requester: str = "anonymous"


# --- Endpoints ---

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/agent/info")
def agent_info() -> dict:
    return {
        "name": DEFAULT_IDENTITY.name,
        "purpose": DEFAULT_IDENTITY.purpose,
        "allowed_tools": list(DEFAULT_IDENTITY.allowed_tools),
    }


@app.get("/tools")
def list_tools() -> dict:
    return {"tools": registry.list_tools()}


@app.post("/tools/run")
def run_tool(call: ToolCallRequest) -> dict:
    tool_name = call.tool_name
    params = call.params
    requester = call.requester

    _audit.log("TOOL_REQUEST", {"tool": tool_name, "params": params, "requester": requester})

    # Gate 1 — Identity
    if not DEFAULT_IDENTITY.can_use(tool_name):
        _audit.log("IDENTITY_DENIED", {"tool": tool_name, "requester": requester})
        raise HTTPException(status_code=403, detail=f"Tool '{tool_name}' not in agent allowed_tools.")

    # Gate 2 — Policy
    try:
        check_permission(_policy, tool_name)
    except PolicyViolationError as exc:
        _audit.log("POLICY_DENIED", {"tool": tool_name, "reason": str(exc), "requester": requester})
        raise HTTPException(status_code=403, detail=str(exc))

    # Gate 3 — Approval
    if DEFAULT_IDENTITY.requires_approval(tool_name):
        _audit.log("APPROVAL_REQUIRED", {"tool": tool_name, "requester": requester})
        raise HTTPException(
            status_code=202,
            detail=f"Tool '{tool_name}' requires human approval. Submit via request_approval.",
        )

    # Dispatch
    try:
        fn = registry.get(tool_name)
    except KeyError:
        _audit.log("TOOL_NOT_FOUND", {"tool": tool_name})
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not registered.")

    try:
        result = fn(**params)
    except TypeError as exc:
        _audit.log("TOOL_CALL_ERROR", {"tool": tool_name, "error": str(exc)})
        raise HTTPException(status_code=422, detail=f"Invalid params for '{tool_name}': {exc}")
    except Exception as exc:
        _audit.log("TOOL_CALL_ERROR", {"tool": tool_name, "error": str(exc)})
        raise HTTPException(status_code=500, detail=f"Tool execution error: {exc}")

    _audit.log("TOOL_RESULT", {"tool": tool_name, "result": result})
    return {"status": "ok", "result": result}
