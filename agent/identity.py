from dataclasses import dataclass, field
from typing import Sequence

@dataclass(frozen=True)
class AgentIdentity:
    """
    Profilo che definisce l'identità dell'agente, i tool consentiti 
    e le regole di approvazione.
    """
    name: str
    purpose: str
    allowed_tools: Sequence[str] = field(default_factory=list)
    accessible_data_domains: Sequence[str] = field(default_factory=list)
    human_approval_required_for: Sequence[str] = field(default_factory=list)

    def can_use(self, tool: str) -> bool:
        """Verifica se l'agente è autorizzato a utilizzare un determinato tool."""
        return tool in self.allowed_tools

    def requires_approval(self, action: str) -> bool:
        """Verifica se un'azione specifica richiede l'autorizzazione umana."""
        return action in self.human_approval_required_for

# Istanza predefinita per il progetto SentinelAgent
DEFAULT_IDENTITY = AgentIdentity(
    name="SentinelAgent",
    purpose="Analyze document metadata and content with scoped permissions and audit logs.",
    allowed_tools=["list_documents", "read_document", "extract_metadata", "write_report"],
    accessible_data_domains=["local_documents", "generated_reports"],
    human_approval_required_for=["delete_file", "send_email", "external_upload"],
)
