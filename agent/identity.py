from dataclasses import dataclass, field
from typing import Sequence

@dataclass(frozen=True)
class AgentIdentity:
"""Profile that describes an agent's identity, allowed tools and approval rules."""
name: str
purpose: str
allowed_tools: Sequence[str] = field(default_factory=list)
accessible_data_domains: Sequence[str] = field(default_factory=list)
human_approval_required_for: Sequence[str] = field(default_factory=list)

def can\_use(self, tool: str) -> bool:
    return tool in self.allowed\_tools

def requires\_approval(self, action: str) -> bool:
    return action in self.human\_approval\_required\_for



DEFAULT_IDENTITY = AgentIdentity(
    name="DocGovAgent",
    purpose="Analyze document metadata and content with scoped permissions and audit logs.",
    allowed_tools=["list_documents", "read_document", "extract_metadata", "write_report"],
    accessible_data_domains=["local_documents", "generated_reports"],
    human_approval_required_for=["delete_file", "send_email", "external_upload"],
)

