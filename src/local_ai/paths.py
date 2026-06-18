from __future__ import annotations

"""
local_ai/paths.py

Filesystem path resolution for the application.

Responsibilities:
- Derive all runtime and repo paths from a small set of roots
- Keep path construction centralized and consistent
- Provide a single immutable AppPaths object via paths_get()

Design notes:
- Repo paths (repo_root, src_root, scripts_dir) are derived from the code location
- Runtime data paths are derived from CONFIG.ai_root and CONFIG.data_root
- App data is kept outside the repo under:
  ~/ai/data/<app_name>/
- No global state: paths are recomputed on each call to paths_get()
- Callers are responsible for creating directories when needed
"""

from dataclasses import dataclass
from pathlib import Path

from local_ai.config import CONFIG


@dataclass(frozen=True)
class AppPaths:
    """Resolved filesystem paths for repo code and runtime data."""
    repo_root: Path
    src_root: Path
    package_root: Path
    ai_root: Path
    scripts_dir: Path
    ai_start_script: Path
    ai_status_script: Path
    data_root: Path
    app_data_root: Path
    sessions_dir: Path
    web_dir: Path
    logs_dir: Path
    run_log_path: Path
    profile_path: Path


# WHY:
# All filesystem paths are derived from a small set of roots to keep layout
# consistent and avoid duplication across modules. Repo paths come from the
# code location, while runtime data paths come from CONFIG. This function
# only computes paths; it does not create directories or perform I/O.
def paths_get() -> AppPaths:
    """Compute and return the current set of application paths."""
    package_root = Path(__file__).resolve().parent
    src_root = package_root.parent
    repo_root = src_root.parent

    ai_root = CONFIG.ai_root
    data_root = CONFIG.data_root
    app_data_root = data_root / CONFIG.app_name
    sessions_dir = app_data_root / "sessions"

    scripts_dir = repo_root / "scripts"
    ai_start_script = scripts_dir / CONFIG.ai_start_script_name
    ai_status_script = scripts_dir / CONFIG.ai_status_script_name

    web_dir = app_data_root / "web"
    logs_dir = app_data_root / "logs"
    run_log_path = logs_dir / "run.log"
    profile_path = app_data_root / "profile.json"

    return AppPaths(
        repo_root=repo_root,
        src_root=src_root,
        package_root=package_root,
        ai_root=ai_root,
        scripts_dir=scripts_dir,
        ai_start_script=ai_start_script,
        ai_status_script=ai_status_script,
        data_root=data_root,
        app_data_root=app_data_root,
        sessions_dir=sessions_dir,
        web_dir=web_dir,
        logs_dir=logs_dir,
        run_log_path=run_log_path,
        profile_path=profile_path,
    )
