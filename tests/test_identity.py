import pytest
from agent.identity import DEFAULT_IDENTITY, AgentIdentity

def test_default_identity_fields():
    assert isinstance(DEFAULT_IDENTITY, AgentIdentity)
    assert DEFAULT_IDENTITY.name != ""
    assert "read_document" in DEFAULT_IDENTITY.allowed_tools

def test_can_use_method():
    assert DEFAULT_IDENTITY.can_use("read_document")
    assert not DEFAULT_IDENTITY.can_use("nonexistent_tool")

def test_requires_approval_method():
    assert DEFAULT_IDENTITY.requires_approval("delete_file")
    assert not DEFAULT_IDENTITY.requires_approval("read_document")

