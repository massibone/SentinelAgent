from dataclasses import dataclass, field


@dataclass
class AgentIdentity:
    name: str
    purpose: str
    allowed_tools: list[str] = field(default_factory=list)
    accessible_data_domains: list[str] = field(default_factory=list)
    human_approval_required_for: list[str] = field(default_factory=list)


DEFAULT_IDENTITY = AgentIdentity(
    name="DocGovAgent",
    purpose="Analyze document metadata and content with scoped permissions and audit logs.",
    allowed_tools=["list_documents", "read_document", "extract_metadata", "write_report"],
    accessible_data_domains=["local_documents", "generated_reports"],
    human_approval_required_for=["delete_file", "send_email", "external_upload"],
)

