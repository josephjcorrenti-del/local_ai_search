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

[ ] add structured NDJSON logging
[ ] write logs to `run.log`
[ ] support verbose stdout logging
[ ] include event names, timestamps, command, outcome, elapsed_ms, and errors
[ ] preserve ELK-friendly event shape

## CLI foundation

[x] add `status` command
[x] add `doctor` command
[x] add `config-show` command
[x] add basic CLI tests
[x] add shell-safe human-readable output

## Configuration

[x] add config model
[x] default `search_provider = local_search`
[x] document supported providers
[x] keep DuckDuckGo supported but non-default
[x] reject unsupported providers
[x] add config tests

## Evidence contract

[ ] add sample local_search evidence fixture
[ ] add evidence loader
[ ] validate `retrieval_version`
[ ] validate required fields
[ ] enforce bounded evidence chars
[ ] add evidence formatter
[ ] add malformed evidence tests
[ ] add unsupported version tests

## First integration

[ ] add `inspect-evidence PATH`
[ ] add explicit evidence consumption logging
[ ] decide first AI handoff command
[ ] avoid hidden retrieval
[ ] avoid hidden prompt injection
[ ] document evidence flow

## Startup and availability

[ ] verify `local-ai-search` works from any directory
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

