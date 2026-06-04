# local_ai_search TODO

## Bootstrap

[ ] create `~/local_ai_search` repo
[ ] add `pyproject.toml`
[ ] add package directory `src/local_ai_search`
[ ] add command entry point `local-ai-search`
[ ] add `.gitignore`
[ ] add `README.md`
[ ] add `docs/decisions.md`
[ ] add `docs/todo-list.md`

## Paths and runtime layout

[ ] add `paths.py`
[ ] define app data root
[ ] define logs directory
[ ] define run log path
[ ] define evidence directory
[ ] define exports directory
[ ] ensure directories are created safely
[ ] add path tests

## Logging

[ ] add structured NDJSON logging
[ ] write logs to `run.log`
[ ] support verbose stdout logging
[ ] include event names, timestamps, command, outcome, elapsed_ms, and errors
[ ] preserve ELK-friendly event shape

## CLI foundation

[ ] add `status` command
[ ] add `doctor` command
[ ] add `config-show` command
[ ] add basic CLI tests
[ ] add shell-safe human-readable output

## Configuration

[ ] add config model
[ ] default `search_provider = local_search`
[ ] document supported providers
[ ] keep DuckDuckGo supported but non-default
[ ] reject unsupported providers
[ ] add config tests

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

## Tests and CI

[ ] add pytest tests
[ ] add `scripts/tests/run_all.sh`
[ ] add GitHub Actions workflow
[ ] verify tests pass locally
[ ] verify GitHub Actions pass

## Git

[ ] initialize git repo
[ ] make first commit
[ ] create GitHub repo
[ ] push main branch
[ ] verify clean `git status`

