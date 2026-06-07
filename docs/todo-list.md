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
[ ] document post-reboot startup steps
[ ] document dependency expectations for `local-ai`
[ ] document dependency expectations for `local-search`
[ ] document status checks for all three tools
[ ] make `status` check full ecosystem by default
[ ] make `doctor` check full ecosystem by default
[ ] add `--self` flag to `status`
[ ] add `--self` flag to `doctor`
[ ] check `local-ai status`
[ ] check `local-search status`
[ ] check `local-ai-search status --self`
[ ] check `local-ai-search doctor --self`
[ ] document that full ecosystem checks are the default
[ ] add tests for `--self`
[ ] add tests for ecosystem status/doctor behavior
[ ] add `--help` coverage later

## Other
[ ] populate README
[ ] local-ai-search --shell should go to local-search --shell
[ ] verify duck duck go works in local-search, local-ai, and local-ai-search

## Tests and CI

[x] add pytest tests
[x] add `scripts/tests/run_all.sh`
[x] add GitHub Actions workflow
[x] verify tests pass locally
[ ] verify GitHub Actions pass

## Git

[x] initialize git repo
[x] make first commit
[ ] create GitHub repo
[ ] push main branch
[x] verify clean `git status`

