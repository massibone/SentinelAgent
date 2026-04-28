Permission-aware Python agent for secure document and workflow automation. Designed for portfolio projects on GitHub and professional positioning on LinkedIn/Upwork.

Short description
Permission-aware Python AI agent with explicit identity, policy-driven access, limited toolset and JSONL audit logging; includes a FastAPI skeleton for extension.


Agent identity and profile (name, purpose, allowed tools, accessible data)
Policy engine enforcing allowed/forbidden actions
Tool registry with input validation and whitelisting
JSONL audit logging of prompts, tool calls, outputs and outcomes
Optional approval layer for sensitive actions
FastAPI skeleton for future integrations (webhooks, UI, local providers)

Project structure
secure-document-agent/
├─ agent/
│  ├─ identity.py        # agente: nome, scopo, tool consentiti, dati accessibili
│  ├─ policy.py          # regole di accesso e autorizzazioni
│  ├─ audit.py           # logger JSONL per audit (prompt, tool calls, output)
│  └─ tools/             # tool isolati con validazione input
├─ tests/
├─ examples/
├─ .github/workflows/ci.yml
├─ api.py                # FastAPI app (skeleton)
├─ main.py               # entrypoint CLI
├─ pyproject.toml
└─ README.md

Quick start

Sincronizza dipendenze:
bash


uv sync --all-groups
Esegui l’agente:
bash


uv run python main
Avvia l’API in hot-reload:
bash


uv run uvicorn api:app --
Architecture summary
Minimum blocks: agent profile, policy engine, tool registry, audit logger, approval layer. These enforce authority boundaries, typed inputs and narrow tool interfaces rather than relying on the model alone.

Three concrete example agents to showcase

Document extractor
Reads PDFs/folders and produces structured extractions.
Role separation, tool whitelist and per-action audit logs.
Email/workflow simulator
Classifies inbound requests and drafts responses.
Never sends emails without explicit human approval and permissions.
AI workflow security checker
Scans YAML/config/scripts for secret leakage, excess privileges or overly permissive tools and reports risks.
Recommended enhancements (roadmap)

Add PDF parsing with pypdf
Add manual approval steps for sensitive operations
Integrate local providers (e.g., Ollama) to reduce external dependencies
Tighten I/O validation with pydantic/JSON Schema
Add focused tests for allowed/denied tool behavior
Tests
Run the test suite:

bash


uv run pytest
