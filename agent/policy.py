from dataclasses import dataclass


@dataclass
class AgentPolicy:
    can_read_docs: bool = True
    can_write_reports: bool = True
    can_send_email: bool = False
    can_delete_files: bool = False
    max_files_per_run: int = 5


class PolicyViolationError(PermissionError):
    pass


ACTION_FLAGS = {
    "read_document": "can_read_docs",
    "write_report": "can_write_reports",
    "send_email": "can_send_email",
    "delete_file": "can_delete_files",
}


def check_permission(policy: AgentPolicy, action: str) -> None:
    flag = ACTION_FLAGS.get(action)
    if flag is None:
        raise PolicyViolationError(f"Unknown action: {action}")
    if not getattr(policy, flag):
        raise PolicyViolationError(f"Action not allowed by policy: {action}")
