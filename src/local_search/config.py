"""Configuration values for local_search."""

from __future__ import annotations

import configparser
from pathlib import Path


SCHEMA_VERSION = 1
RETRIEVAL_VERSION = 1


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _config_path() -> Path:
    return _repo_root() / "config.ini"


def _load_search_config() -> configparser.SectionProxy:
    parser = configparser.ConfigParser()
    parser.read(_config_path())

    if "search" not in parser:
        raise RuntimeError(f"missing [search] section in {_config_path()}")

    return parser["search"]


_SEARCH_CONFIG = _load_search_config()

APP_NAME = _SEARCH_CONFIG.get("app_name", "local_search")

DEFAULT_CHUNK_SIZE = _SEARCH_CONFIG.getint("chunk_size", 1200)
DEFAULT_CHUNK_OVERLAP = _SEARCH_CONFIG.getint("chunk_overlap", 200)

DEFAULT_SEARCH_LIMIT = _SEARCH_CONFIG.getint("default_limit", 10)

DEFAULT_SEARXNG_BASE_URL = _SEARCH_CONFIG.get(
    "provider_url",
    "http://localhost:8080",
)
DEFAULT_WEB_SEARCH_PROVIDER = _SEARCH_CONFIG.get("web_provider", "searxng")
WEB_SEARCH_TIMEOUT_SECONDS = _SEARCH_CONFIG.getint("timeout_seconds", 20)