"""
Tool registry: maps canonical tool names to callable functions.
Used by tools/__init__.py to register tools and by main.py to dispatch calls.
"""
from __future__ import annotations

from typing import Callable, Any

_REGISTRY: dict[str, Callable[..., Any]] = {}


def register(name: str, fn: Callable[..., Any]) -> None:
    """Register a tool function under a canonical name."""
    if name in _REGISTRY:
        raise ValueError(f"Tool '{name}' is already registered.")
    _REGISTRY[name] = fn


def get(name: str) -> Callable[..., Any]:
    """Retrieve a registered tool by name. Raises KeyError if not found."""
    if name not in _REGISTRY:
        raise KeyError(f"Tool '{name}' is not registered.")
    return _REGISTRY[name]


def list_tools() -> list[str]:
    """Return all registered tool names."""
    return sorted(_REGISTRY.keys())
