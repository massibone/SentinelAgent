from pathlib import Path

from agent.audit import AuditLogger
from agent.policy import AgentPolicy, check_permission


BASE_DIR = Path("examples")


def list_documents(policy: AgentPolicy, logger: AuditLogger) -> list[str]:
    files = sorted([p.name for p in BASE_DIR.glob("*.txt")])
    limited = files[: policy.max_files_per_run]
    logger.log("tool_call", {"tool": "list_documents", "result_count": len(limited)})
    return limited


def read_document(filename: str, policy: AgentPolicy, logger: AuditLogger) -> str:
    check_permission(policy, "read_document")
    path = BASE_DIR / filename
    content = path.read_text(encoding="utf-8")
    logger.log("tool_call", {"tool": "read_document", "filename": filename})
    return content


def write_report(filename: str, content: str, policy: AgentPolicy, logger: AuditLogger) -> str:
    check_permission(policy, "write_report")
    reports_dir = Path("logs") / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / filename
    path.write_text(content, encoding="utf-8")
    logger.log("tool_call", {"tool": "write_report", "filename": filename})
    return str(path)
