from typing import Callable
from agent.registry import register

# Import tool functions so they get registered below.
from .list_documents import list_documents  # noqa: F401
from .read_document import read_document    # noqa: F401
from .extract_metadata import extract_metadata  # noqa: F401
from .write_report import write_report      # noqa: F401
from .request_approval import request_approval, get_approval, decide_approval  # noqa: F401

# Register tools with canonical names used by AgentIdentity.allowed_tools / policy
register("list_documents", list_documents)
register("read_document", read_document)
register("extract_metadata", extract_metadata)
register("write_report", write_report)
register("request_approval", request_approval)
# expose public API
__all__ = [
    "list_documents",
    "read_document",
    "extract_metadata",
    "write_report",
    "request_approval",
    "get_approval",
    "decide_approval",
]

