from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_SEARCH_PROVIDER = "local_search"
SUPPORTED_SEARCH_PROVIDERS = ("local_search", "duckduckgo")


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class AppConfig:
    search_provider: str = DEFAULT_SEARCH_PROVIDER


def default_config_text() -> str:
    return "\n".join(
        [
            "search_provider = local_search",
            "",
            "# Supported:",
            "# - local_search",
            "# - duckduckgo",
            "",
        ]
    )


def validate_config(config: AppConfig) -> AppConfig:
    if config.search_provider not in SUPPORTED_SEARCH_PROVIDERS:
        supported = ", ".join(SUPPORTED_SEARCH_PROVIDERS)
        raise ConfigError(
            f"unsupported search_provider: {config.search_provider} "
            f"(supported: {supported})"
        )
    return config


def load_config(path: Path | None = None) -> AppConfig:
    if path is None:
        return validate_config(AppConfig())

    if not path.exists():
        return validate_config(AppConfig())

    values: dict[str, str] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in stripped:
            raise ConfigError(f"invalid config line: {line}")

        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()

    allowed_keys = {"search_provider"}
    unknown_keys = sorted(set(values) - allowed_keys)
    if unknown_keys:
        raise ConfigError(f"unknown config key: {unknown_keys[0]}")

    config = AppConfig(
        search_provider=values.get("search_provider", DEFAULT_SEARCH_PROVIDER)
    )
    return validate_config(config)
