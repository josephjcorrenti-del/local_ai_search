from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_SEARCH_PROVIDERS = ("local_search", "duckduckgo")


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class SearchConfig:
    provider: str
    provider_url: str
    default_limit: int
    timeout_seconds: int


@dataclass(frozen=True)
class AIConfig:
    ollama_base_url: str
    request_timeout_seconds: int
    small_model: str
    lightweight_model: str
    large_model: str
    chat_model: str
    summary_model: str


@dataclass(frozen=True)
class IntegrationConfig:
    default_mode: str
    evidence_limit: int
    evidence_max_chars: int


@dataclass(frozen=True)
class AppConfig:
    search: SearchConfig
    ai: AIConfig
    integration: IntegrationConfig

    @property
    def search_provider(self) -> str:
        return self.search.provider


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config.ini"


def default_config_text() -> str:
    return "\n".join(
        [
            "[search]",
            "app_name = local_search",
            "provider = local_search",
            "web_provider = searxng",
            "",
            "# Supported integration providers:",
            "# - local_search",
            "# - duckduckgo",
            "",
            "provider_url = http://localhost:8080",
            "default_limit = 10",
            "timeout_seconds = 20",
            "chunk_size = 1200",
            "chunk_overlap = 200",
            "",
            "[ai]",
            "ollama_base_url = http://127.0.0.1:11434",
            "request_timeout_seconds = 120",
            "",
            "small_model = phi3:mini",
            "lightweight_model = phi3:mini",
            "large_model = qwen2.5-coder:3b",
            "",
            "chat_model = large_model",
            "summary_model = lightweight_model",
            "",
            "[integration]",
            "default_mode = integrated",
            "evidence_limit = 5",
            "evidence_max_chars = 4000",
            "",
        ]
    )


def _parser_load(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    read_paths = parser.read(path)

    if not read_paths:
        raise ConfigError(f"config file not found: {path}")

    return parser


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or default_config_path()
    parser = _parser_load(config_path)

    try:
        config = AppConfig(
            search=SearchConfig(
                provider=parser.get("search", "provider"),
                provider_url=parser.get("search", "provider_url"),
                default_limit=parser.getint("search", "default_limit"),
                timeout_seconds=parser.getint("search", "timeout_seconds"),
            ),
            ai=AIConfig(
                ollama_base_url=parser.get("ai", "ollama_base_url"),
                request_timeout_seconds=parser.getint("ai", "request_timeout_seconds"),
                small_model=parser.get("ai", "small_model"),
                lightweight_model=parser.get("ai", "lightweight_model"),
                large_model=parser.get("ai", "large_model"),
                chat_model=parser.get("ai", "chat_model"),
                summary_model=parser.get("ai", "summary_model"),
            ),
            integration=IntegrationConfig(
                default_mode=parser.get("integration", "default_mode"),
                evidence_limit=parser.getint("integration", "evidence_limit"),
                evidence_max_chars=parser.getint("integration", "evidence_max_chars"),
            ),
        )
    except (configparser.Error, ValueError) as exc:
        raise ConfigError(str(exc)) from exc

    return validate_config(config)


def validate_config(config: AppConfig) -> AppConfig:
    if config.search.provider not in SUPPORTED_SEARCH_PROVIDERS:
        supported = ", ".join(SUPPORTED_SEARCH_PROVIDERS)
        raise ConfigError(
            f"unsupported search provider: {config.search.provider} "
            f"(supported: {supported})"
        )

    return config


_CONFIG = load_config()

DEFAULT_SEARCH_PROVIDER = _CONFIG.search.provider
EVIDENCE_LIMIT = _CONFIG.integration.evidence_limit
EVIDENCE_MAX_CHARS = _CONFIG.integration.evidence_max_chars