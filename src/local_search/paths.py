"""Filesystem paths for local_search."""

from __future__ import annotations

from pathlib import Path

APP_NAME = "local_search"

REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = REPO_ROOT / "data" / APP_NAME

LOG_DIR = DATA_ROOT / "logs"
ARTIFACTS_DIR = DATA_ROOT / "artifacts"
EXPORTS_DIR = DATA_ROOT / "exports"

DB_PATH = DATA_ROOT / "search.db"
RUN_LOG = LOG_DIR / "run.log"
WEB_ARTIFACTS_DIR = ARTIFACTS_DIR / "web"


def ensure_app_dirs() -> None:
    """Create required runtime directories."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    WEB_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
