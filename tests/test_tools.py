import pytest
from agent.registry import register, get_tool, REGISTRY
from agent.tools.list_documents import list_documents

def test_list_documents_registered():
    # ensure the tool function exists and returns an iterable
    assert callable(list_documents)
    docs = list_documents(path=".")  # adjust params if signature differs
    assert hasattr(docs, "__iter__")

def test_registry_register_and_get():
    def dummy_tool(**kwargs):
        return {"ok": True}
    register("dummy_tool", dummy_tool)
    fn = get_tool("dummy_tool")
    assert fn is dummy_tool
    assert REGISTRY["dummy_tool"] is dummy_tool

def test_tool_execution_via_registry():
    # register a simple tool and call through registry
    def echo_tool(params):
        return {"echo": params}
    register("echo", echo_tool)
    tool = get_tool("echo")
    assert tool({"x": 1}) == {"echo": {"x": 1}}
