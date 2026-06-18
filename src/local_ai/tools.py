from __future__ import annotations

"""
local_ai/tools.py

Local tool definitions for model tool-calling.

Responsibilities:
- Define small, explicit tools callable by the model
- Provide a registry (TOOL_REGISTRY) for execution
- Provide tool schemas (TOOL_DEFS) for model-side function calling

Design notes:
- Tools are intentionally minimal and local-only
- No hidden behavior: tools perform one explicit action and return structured output
- Tool definitions (TOOL_DEFS) must stay in sync with callable functions
- Output is bounded and simple to keep responses inspectable
- This module does not handle tool orchestration (handled in cli.py)
"""

from pathlib import Path


def directory_list(path: str) -> dict[str, object]:
    """Return a shallow listing of files and directories for a local path."""
    base = Path(path).expanduser().resolve()

    if not base.exists():
        return {"ok": False, "error": f"path does not exist: {base}"}

    if not base.is_dir():
        return {"ok": False, "error": f"path is not a directory: {base}"}

    entries = []
    for child in sorted(base.iterdir(), key=lambda p: p.name.lower()):
        entries.append(
            {
                "name": child.name,
                "type": "dir" if child.is_dir() else "file",
            }
        )

    return {
        "ok": True,
        "path": str(base),
        "entries": entries[:50],
    }


TOOL_REGISTRY = {
    "directory_list": directory_list,
}


TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "directory_list",
            "description": "List files and directories at a local path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or home-relative directory path",
                    }
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    }
]
