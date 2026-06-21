from __future__ import annotations

from pathlib import Path
import re

from local_ai_search.adapters.local_search import LocalSearchAdapterError
from local_search.paths import ARTIFACTS_DIR


def query_slug(query: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", query.strip().lower())
    return slug.strip("_")


def latest_web_artifact_for_query(query: str) -> Path:
    pattern = f"search_{query_slug(query)}_*.json"
    web_artifacts_dir = ARTIFACTS_DIR / "web"
    matches = sorted(web_artifacts_dir.glob(pattern))

    if not matches:
        raise LocalSearchAdapterError(f"no web artifact found for query: {query}")

    return matches[-1]
