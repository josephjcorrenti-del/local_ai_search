from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


APP_NAME = "local_ai_search"


@dataclass(frozen=True)
class AppPaths:
    repo_root: Path
    data_root: Path
    log_dir: Path
    run_log: Path
    evidence_dir: Path
    exports_dir: Path


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_paths() -> AppPaths:
    repo_root = get_repo_root()
    data_root = repo_root / "data" / APP_NAME

    return AppPaths(
        repo_root=repo_root,
        data_root=data_root,
        log_dir=data_root / "logs",
        run_log=data_root / "logs" / "run.log",
        evidence_dir=data_root / "evidence",
        exports_dir=data_root / "exports",
    )


def ensure_runtime_dirs() -> AppPaths:
    paths = get_paths()
    paths.log_dir.mkdir(parents=True, exist_ok=True)
    paths.evidence_dir.mkdir(parents=True, exist_ok=True)
    paths.exports_dir.mkdir(parents=True, exist_ok=True)
    return paths
