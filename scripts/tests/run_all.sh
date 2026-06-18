#!/usr/bin/env bash
set -euo pipefail

python -m pytest -q src/local_ai/test
python -m pytest -q src/local_search/test
python -m pytest -q src/local_ai_search/test

local-ai status >/dev/null
local-search status >/dev/null
local-ai-search status --self >/dev/null
