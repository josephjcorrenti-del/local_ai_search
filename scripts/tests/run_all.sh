#!/usr/bin/env bash
set -euo pipefail

python -m pytest -q src/local_ai_search/test
local-ai-search status >/dev/null
