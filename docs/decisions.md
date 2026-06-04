# local_ai_search Decisions

## 2026-06-04 - Project name and purpose

`local_ai_search` is a new integration project that combines `local_ai` and `local_search` into an explicit AI + search workflow.

It is not phase 2 of either existing project.

`local_ai` remains responsible for AI orchestration, shell UX, profiles, workspaces, prompt construction, and model interaction.

`local_search` remains responsible for indexing, retrieval, search providers, artifact persistence, artifact cleanup, and evidence shaping.

`local_ai_search` owns the integration boundary between the two.

## 2026-06-04 - Command name

The command will be:

```bash
local-ai-search
```

This keeps naming consistent with:

```bash
local-ai
local-search
```

## 2026-06-04 - Repository

`local_ai_search` will be a new repository.

Reason:

* the integration layer is a new project
* neither `local_ai` nor `local_search` should absorb the other
* both existing tools must remain independently useful
* the combined workflow should be explicit and inspectable

## 2026-06-04 - Search provider configuration

Search provider configuration should look like:

```ini
search_provider = local_search

# Supported:
# - local_search
# - duckduckgo
```

DuckDuckGo remains supported but is not the default.

The default search provider should be `local_search`.

## 2026-06-04 - Integration boundary

The first integration boundary should use versioned JSON evidence packages.

`local_search` produces evidence.

`local_ai_search` validates, bounds, logs, and passes evidence to `local_ai`.

Direct Python imports are not the first boundary.

Subprocess and JSON contracts are preferred first because they preserve project independence and make behavior inspectable.

## 2026-06-04 - No hidden retrieval

`local_ai_search` must not perform hidden background retrieval.

Search must be explicit.

Evidence loading must be explicit.

Prompt construction must use bounded evidence windows.

Logs remain the source of truth.

## 2026-06-04 - Runtime data

Runtime data should live under:

```text
~/local_ai_search/data/local_ai_search/
```

Logs should live under:

```text
~/local_ai_search/data/local_ai_search/logs/run.log
```

This mirrors the layout used by `local_ai` and `local_search`.

