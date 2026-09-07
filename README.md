# SentinelAgent

**Permission-aware Python AI agent** with explicit identity, policy-driven access control, a limited toolset, and JSONL audit logging. Includes a FastAPI skeleton for future extension.

Built as a portfolio project to demonstrate secure agentic design patterns: authority boundaries, typed inputs, narrow tool interfaces, and a human-approval layer — without relying on the model alone to enforce constraints.

---

## Features

- **Agent identity** — name, purpose, allowed tools, accessible data domains
- **Policy engine** — enforces allowed/forbidden actions per flag
- **Tool registry** — maps canonical names to callables; validates at registration
- **JSONL audit logging** — records prompts, tool calls, outputs, and outcomes
- **Approval layer** — blocks sensitive actions until a human explicitly decides
- **FastAPI skeleton** — ready for webhooks, UI, or local LLM providers

---

## Project structure

```
SentinelAgent/
├─ agent/
│  ├─ __init__.py
│  ├─ identity.py       # agent profile: name, purpose, allowed tools, data domains
│  ├─ policy.py         # access rules and permission flags
│  ├─ audit.py          # JSONL logger (timestamp, event_type, payload)
│  └─ registry.py       # tool registry: register / get / list_tools
├─ tools/
│  ├─ __init__.py       # imports and registers all tools
│  ├─ list_documents.py
│  ├─ read_document.py
│  ├─ extract_metadata.py
│  ├─ write_report.py
│  └─ request_approval.py
├─ tests/
│  ├─ test_identity.py
│  ├─ test_policy.py
│  └─ test_tools.py
├─ examples/            # sample .txt and .md files for demo runs
├─ .github/workflows/ci.yml
├─ api.py               # FastAPI app (skeleton)
├─ main.py              # CLI entrypoint
├─ pyproject.toml
└─ README.md
```

---

## Quick start

**Sync dependencies:**
```bash
uv sync --all-groups
```

**List available tools:**
```bash
uv run python main.py --list-tools
```

**Run a tool:**
```bash
uv run python main.py --tool list_documents
uv run python main.py --tool read_document --args '{"filename": "notes.txt"}'
```

**Start the API (hot reload):**
```bash
uv run uvicorn api:app --reload
```

**Run tests:**
```bash
uv run pytest
```

---

## Architecture

Every agent action passes through three sequential gates before execution:

```
CLI input
    │
    ▼
[1] Identity check     → is this tool in allowed_tools?
    │
    ▼
[2] Policy check       → does the policy flag permit this action?
    │
    ▼
[3] Approval check     → does this action require human sign-off?
    │
    ▼
Tool dispatch          → fn(**args) → result
    │
    ▼
Audit log              → JSONL record at every gate and outcome
```

This enforces authority boundaries structurally — a misconfigured or misbehaving model cannot bypass a gate by reasoning around it.

---

## Example agents (roadmap)

**Document extractor**
Reads folders of PDFs/text files and produces structured extractions. Demonstrates role separation, tool whitelisting, and per-action audit logs.

**Email/workflow simulator**
Classifies inbound requests and drafts responses. Never sends without explicit human approval.

**AI workflow security checker**
Scans YAML/config files for secret leakage, excess privileges, or overly permissive tool configs and reports risks.

---

## Recommended enhancements

- Add PDF parsing with `pypdf`
- Tighten I/O validation with `pydantic` / JSON Schema
- Integrate local LLM providers (e.g., Ollama) to reduce external dependencies
- Add focused tests for allowed/denied tool behavior at each gate
- Persist approval decisions to a queue for async workflows
