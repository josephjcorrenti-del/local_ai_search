from __future__ import annotations

"""
local_ai/schemas.py

Small JSON schema definitions used for structured model outputs.

Responsibilities:
- Keep schema definitions separate from CLI/runtime flow
- Provide simple, inspectable contracts for structured responses

Design notes:
- Schemas are intentionally minimal
- Current scope is limited to lightweight local validation/use cases
- This module is a container for shared schema constants, not schema logic
"""


PING_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "model": {"type": "string"},
        "summary": {"type": "string"},
    },
    "required": ["status", "model", "summary"],
    "additionalProperties": False,
}
