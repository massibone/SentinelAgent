"""
main.py — CLI entrypoint for SentinelAgent.

Usage:
    uv run python main.py
    uv run python main.py --tool list_documents
    uv run python main.py --tool read_document --args '{"filename": "notes.txt"}'
    uv run python main.py --list-tools
"""
from __future__ import annotations

import argparse
import json
import sys

from agent.identity import DEFAULT_IDENTITY
from agent.policy import AgentPolicy, check_permission, PolicyViolationError
from agent.audit import AuditLogger
import agent.registry as registry

# Importing tools triggers registration via tools/__init__.py
import tools  # noqa: F401


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="SentinelAgent",
        description="Permission-aware agent for secure document automation.",
    )
    parser.add_argument(
        "--tool",
        metavar="TOOL_NAME",
        help="Name of the tool to run (e.g. list_documents, read_document).",
    )
    parser.add_argument(
        "--args",
        metavar="JSON",
        default="{}",
        help='Tool arguments as a JSON string (e.g. \'{"filename": "notes.txt"}\').',
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Print all registered tools and exit.",
    )
    return parser


def run(tool_name: str, tool_args: dict, policy: AgentPolicy, logger: AuditLogger) -> None:
    identity = DEFAULT_IDENTITY

    # 1. Identity check
    if not identity.can_use(tool_name):
        logger.log("IDENTITY_DENIED", {"tool": tool_name, "reason": "not in allowed_tools"})
        print(f"[DENIED] '{tool_name}' is not in the agent's allowed_tools.")
        sys.exit(1)

    # 2. Policy check
    try:
        check_permission(policy, tool_name)
    except PolicyViolationError as exc:
        logger.log("POLICY_DENIED", {"tool": tool_name, "reason": str(exc)})
        print(f"[DENIED] Policy violation: {exc}")
        sys.exit(1)

    # 3. Approval check
    if identity.requires_approval(tool_name):
        logger.log("APPROVAL_REQUIRED", {"tool": tool_name, "args": tool_args})
        print(f"[BLOCKED] '{tool_name}' requires human approval. Use request_approval tool.")
        sys.exit(1)

    # 4. Dispatch
    fn = registry.get(tool_name)
    logger.log("TOOL_CALL", {"tool": tool_name, "args": tool_args})

    try:
        result = fn(**tool_args)
        logger.log("TOOL_RESULT", {"tool": tool_name, "result": result})
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    except Exception as exc:
        logger.log("TOOL_ERROR", {"tool": tool_name, "error": str(exc)})
        print(f"[ERROR] {exc}")
        sys.exit(1)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger = AuditLogger()
    policy = AgentPolicy()

    if args.list_tools:
        print("Registered tools:")
        for name in registry.list_tools():
            marker = "✓" if DEFAULT_IDENTITY.can_use(name) else "✗"
            print(f"  {marker} {name}")
        sys.exit(0)

    if not args.tool:
        parser.print_help()
        sys.exit(0)

    try:
        tool_args = json.loads(args.args)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid JSON in --args: {exc}")
        sys.exit(1)

    run(args.tool, tool_args, policy, logger)


if __name__ == "__main__":
    main()
