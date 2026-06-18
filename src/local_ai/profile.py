from __future__ import annotations

"""
local_ai/profile.py

Explicit, inspectable user profile storage.

Responsibilities:
- Store optional profile preferences under app data root
- Keep profile disabled by default
- Normalize human-readable keys to stable internal keys
- Avoid hidden personalization or automatic memory injection

Design notes:
- The default profile key is "default"
- A profile being enabled means shell may auto-load it
- Profile values are explicit key/value preferences, not chat memory
"""

import json
from pathlib import Path
from typing import Any

from local_ai.log import log_event
from local_ai.paths import paths_get

DEFAULT_PROFILE_KEY = "default"

KEY_ALIASES = {
    "display name": "display_name",
    "display_name": "display_name",
    "preferred model": "preferred_model",
    "preferred_model": "preferred_model",
    "preferred session": "preferred_session",
    "preferred_session": "preferred_session",
    "preferred workspace": "preferred_workspace",
    "preferred_workspace": "preferred_workspace",
}


def profile_key_normalize(profile_key: str | None = None) -> str:
    """Normalize a profile identity key."""
    value = (profile_key or DEFAULT_PROFILE_KEY).strip()
    if not value:
        raise ValueError("profile key cannot be empty")
    return value


def profile_value_key_normalize(key: str) -> str:
    """Normalize a human-readable profile value key."""
    normalized = " ".join(key.strip().lower().replace("-", " ").split())
    if not normalized:
        raise ValueError("profile value key cannot be empty")

    if normalized in KEY_ALIASES:
        return KEY_ALIASES[normalized]

    underscored = normalized.replace(" ", "_")
    if underscored in KEY_ALIASES:
        return KEY_ALIASES[underscored]

    raise ValueError(f"unknown profile key: {key}")


def profile_path_get() -> Path:
    """Return the profile storage path."""
    return paths_get().profile_path


def profile_default_get(profile_key: str | None = None) -> dict[str, Any]:
    """Return a default disabled profile object."""
    return {
        "profile_key": profile_key_normalize(profile_key),
        "enabled": False,
        "values": {},
    }


def profile_load(profile_key: str | None = None) -> dict[str, Any]:
    """Load profile data, returning a disabled default if missing."""
    expected_key = profile_key_normalize(profile_key)
    path = profile_path_get()

    log_event("profile.read.start", path=str(path))

    if not path.exists():
        profile = profile_default_get(expected_key)
        log_event(
            "profile.read.ready",
            path=str(path)
        )
        return profile

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("profile file must contain a JSON object")

    stored_key = profile_key_normalize(data.get("profile_key") or expected_key)
    values = data.get("values", {})
    if not isinstance(values, dict):
        raise ValueError("profile values must be a JSON object")

    profile = {
        "profile_key": stored_key,
        "enabled": bool(data.get("enabled", False)),
        "values": values,
    }

    log_event(
        "profile.read.ready",
        path=str(path)
    )
    return profile


def profile_save(profile: dict[str, Any]) -> dict[str, Any]:
    """Write profile data to disk."""
    path = profile_path_get()
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "profile_key": profile_key_normalize(profile.get("profile_key")),
        "enabled": bool(profile.get("enabled", False)),
        "values": profile.get("values", {}),
    }

    if not isinstance(data["values"], dict):
        raise ValueError("profile values must be a JSON object")

    log_event(
        "profile.write.start",
        path=str(path),
    )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")

    log_event(
        "profile.write.ready",
        path=str(path),
    )
    return data


def profile_enable(profile_key: str | None = None) -> dict[str, Any]:
    """Enable a profile."""
    profile = profile_load(profile_key)
    profile["profile_key"] = profile_key_normalize(profile_key)
    profile["enabled"] = True
    return profile_save(profile)


def profile_disable(profile_key: str | None = None) -> dict[str, Any]:
    """Disable a profile but keep stored values."""
    profile = profile_load(profile_key)
    profile["profile_key"] = profile_key_normalize(profile_key)
    profile["enabled"] = False
    return profile_save(profile)


def profile_delete() -> bool:
    """Delete the stored profile file."""
    path = profile_path_get()

    log_event("profile.delete.start", path=str(path))

    if not path.exists():
        log_event("profile.delete.ready", path=str(path))
        return False

    path.unlink()
    log_event("profile.delete.ready", path=str(path))
    return True


def profile_set(
    key: str,
    value: str,
    profile_key: str | None = None,
) -> dict[str, Any]:
    """Set one profile value using a human-readable key."""
    profile = profile_load(profile_key)
    normalized_key = profile_value_key_normalize(key)
    profile["values"][normalized_key] = value
    return profile_save(profile)


def profile_clear(
    key: str,
    profile_key: str | None = None,
) -> dict[str, Any]:
    """Clear one profile value using a human-readable key."""
    profile = profile_load(profile_key)
    normalized_key = profile_value_key_normalize(key)
    profile["values"].pop(normalized_key, None)
    return profile_save(profile)
