# local_ai_search TODO

## Bootstrap

[x] create `~/local_ai_search` repo
[x] add `pyproject.toml`
[x] add package directory `src/local_ai_search`
[x] add command entry point `local-ai-search`
[x] add `.gitignore`
[x] add `README.md`
[x] add `docs/decisions.md`
[x] add `docs/todo-list.md`

## Paths and runtime layout

[x] add `paths.py`
[x] define app data root
[x] define logs directory
[x] define run log path
[x] define evidence directory
[x] define exports directory
[x] ensure directories are created safely
[x] add path tests

## Logging

[x] add structured NDJSON logging
[x] write logs to `run.log`
[x] support verbose stdout logging
[x] include event names, timestamps, command, outcome, elapsed_ms, and errors
[x] preserve ELK-friendly event shape
[x] verify `local-ai-search` logs appear in ELK

## CLI foundation

[x] add `status` command
[x] add `doctor` command
[x] add `config-show` command
[x] add basic CLI tests
[x] add shell-safe human-readable output
[x] add no-dependency CLI color helpers
[x] color success markers
[x] color failure markers
[x] keep logs uncolored

## Configuration

[x] add config model
[x] default `search_provider = local_search`
[x] document supported providers
[x] keep DuckDuckGo supported but non-default
[x] reject unsupported providers
[x] add config tests

## Evidence contract

[x] add sample local_search evidence fixture
[x] add evidence loader
[x] validate `retrieval_version`
[x] validate required fields
[x] enforce bounded evidence chars
[x] add evidence formatter
[x] add malformed evidence tests
[x] add unsupported version test

## First integration

[x] add `inspect-evidence PATH`
[x] add explicit evidence consumption logging
[x] decide first AI handoff command
[x] avoid hidden retrieval
[x] avoid hidden prompt injection
[x] document evidence flow

## Startup and availability

[x] verify `local-ai-search` works from any directory
[x] document post-reboot startup steps
[x] document dependency expectations for `local-ai`
[x] document dependency expectations for `local-search`
[x] document status checks for all three tools
[x] make `status` check full ecosystem by default
[x] make `doctor` check full ecosystem by default
[x] add `--self` flag to `status`
[x] add `--self` flag to `doctor`
[x] check `local-ai status`
[x] check `local-search status`
[x] check `local-ai-search status --self`
[x] check `local-ai-search doctor --self`
[x] document that full ecosystem checks are the default
[x] add tests for `--self`
[x] add tests for ecosystem status/doctor behavior
[x] add `--help` coverage later

## Tests and CI

[x] add pytest tests
[x] add `scripts/tests/run_all.sh`
[x] add GitHub Actions workflow
[x] verify tests pass locally
[x] verify GitHub Actions pass

## Git

[x] initialize git repo
[x] make first commit
[x] create GitHub repo
[x] push main branch
[x] verify clean `git status`

## Phase 2 – Integration Strategy

[x] define first integrated query path
[x] define config ownership
[x] define shell ownership
[x] evaluate effort to combine `local_ai`, `local_search`, and `local_ai_search`
[x] decide subprocess vs import boundary
[x] decide repository ownership model

## Phase 2 – Implementation Candidates

[x] add subprocess adapter module for local-search
[x] add subprocess adapter module for local-ai
[x] implement pipeline.py query pipeline
[x] implement local-ai-search "QUERY"
[x] implement local-ai-search "QUERY" --ai-only
[x] implement local-ai-search "QUERY" --web-only
[x] defer runtime data migration plan

### Phase 2.1 – Monorepo

[x] draft monorepo migration plan
[x] design one user-facing monorepo config file
[x] combine repos into one monorepo
[x] combine config in monorepo
[x] move logs to centralized `data/logs/<package>/run.log`
[x] inventory package metadata and entry points
[x] draft combined pyproject.toml
[ ] preserve package names
[ ] preserve commands
[ ] preserve runtime data
[ ] merge tests/CI

### Phase 2.2 – GUI

[ ] decide GUI stack
[ ] expose local-ai-search query flow
[ ] expose ai-only/web-only modes
[ ] show search results and AI answer
[ ] keep CLI usable

### Phase 2.3 – Results quality

[ ] make default query mode evidence-aware
[ ] improve evidence prompt
[ ] compare local/search/AI output quality
[ ] add result quality test cases
[ ] decide DuckDuckGo/fallback role

## TBP / Later

[ ] decide --shell delegation
[ ] why is local_search not searxng in config
[ ] clean up tests
[ ] logs timestamp a day ahead?