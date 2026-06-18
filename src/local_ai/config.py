from __future__ import annotations

"""
local_ai/config.py

Central configuration for the application.

Responsibilities:
- Define all runtime configuration values in one place
- Provide a single immutable config object (CONFIG)
- Keep configuration explicit and inspectable (no env-driven overrides yet)

Design notes:
- Uses a frozen dataclass to prevent mutation at runtime
- Separates "roles" of models:
  - lightweight_model_name: cheaper / smaller tasks (summarization)
  - large_model_name: primary chat / reasoning model
- Paths are defined relative to a single ai_root to keep runtime data separate from repo code
- Defaults favor local, explicit behavior over flexibility
"""

import configparser
from dataclasses import dataclass
from pathlib import Path
import os


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _config_path() -> Path:
    return _repo_root() / "config.ini"


def _load_ai_config() -> configparser.SectionProxy:
    parser = configparser.ConfigParser()
    parser.read(_config_path())

    if "ai" not in parser:
        raise RuntimeError(f"missing [ai] section in {_config_path()}")

    return parser["ai"]

def _model_role_resolve(role_value: str) -> str:
    model_map = {
        "small_model": _AI_CONFIG.get("small_model", "phi3:mini"),
        "lightweight_model": _AI_CONFIG.get("lightweight_model", "phi3:mini"),
        "large_model": _AI_CONFIG.get("large_model", "qwen2.5-coder:3b"),
    }

    return model_map.get(role_value, role_value)


_AI_CONFIG = _load_ai_config()


def _model_role_resolve(role_value: str) -> str:
    model_map = {
        "small_model": _AI_CONFIG.get("small_model", "phi3:mini"),
        "lightweight_model": _AI_CONFIG.get("lightweight_model", "phi3:mini"),
        "large_model": _AI_CONFIG.get("large_model", "qwen2.5-coder:3b"),
    }

    return model_map.get(role_value, role_value)


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration values used across modules."""
    app_name: str = _AI_CONFIG.get("app_name", "local_ai")

    ollama_base_url: str = _AI_CONFIG.get("ollama_base_url", "http://127.0.0.1:11434")
    request_timeout_s: int = _AI_CONFIG.getint("request_timeout_seconds", 120)

    lightweight_model_name: str = _AI_CONFIG.get("lightweight_model", "phi3:mini")
    large_model_name: str = _AI_CONFIG.get("large_model", "qwen2.5-coder:3b")
    small_model_name: str = _AI_CONFIG.get("small_model", "phi3:mini")

    chat_model_name: str = _model_role_resolve(_AI_CONFIG.get("chat_model", "large_model"))
    summary_model_name: str = _model_role_resolve(
        _AI_CONFIG.get("summary_model", "lightweight_model")
    )

    ai_start_script_name: str = "ai_start.sh"
    ai_status_script_name: str = "ai_status.sh"

    ai_root: Path = Path.home() / "ai"

    default_session_name: str = _AI_CONFIG.get("default_session_name", "default")
    memory_turn_limit: int = _AI_CONFIG.getint("memory_turn_limit", 8)

    summary_keep_recent_messages: int = _AI_CONFIG.getint("summary_keep_recent_messages", 8)
    summary_max_input_messages: int = _AI_CONFIG.getint("summary_max_input_messages", 12)
    summary_inactive_minutes: int = _AI_CONFIG.getint("summary_inactive_minutes", 30)
    summary_max_input_chars: int = _AI_CONFIG.getint("summary_max_input_chars", 600)

    web_chat_max_source_chars: int = _AI_CONFIG.getint("web_chat_max_source_chars", 6000)

    @property
    def data_root(self) -> Path:
        """Resolve the active data root from an explicit CLI/env selection."""
        data_dir = os.environ.get("OWB_DATA_DIR", "data")
        return self.ai_root / data_dir

CONFIG = AppConfig()
