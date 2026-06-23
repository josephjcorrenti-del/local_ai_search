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


local_ai_search status and doctor should default to checking the full AI/search ecosystem.

That means:
- local_ai_search
- local_ai
- local_search

A `--self` flag may limit checks to local_ai_search only.

Reason:
local_ai_search exists to integrate AI and search. A healthy integration project is not useful if the underlying AI or search commands are unavailable.


## 2026-06-04 - No hidden retrieval

`local_ai_search` must not perform hidden background retrieval.

Search must be explicit.

Evidence loading must be explicit.

Prompt construction must use bounded evidence windows.

Logs remain the source of truth.


## 2026-06-06 - CLI output colors

`local_ai_search` uses the same no-dependency CLI color pattern as `local_search`.

Human CLI output may be colored unless `NO_COLOR` is set.

Structured logs must never contain ANSI color codes.

## 2026-06-06 - Evidence flow and default command shape

The user-facing command shape should match the existing `local-search` and `local-ai` CLIs:

```bash
local-search "secure web browsers"
local-ai "when should i move out of my parents house?"
local-ai-search "how many legs do a cat have?"
local-ai-search "how many legs do a cat have?" --web-only
local-ai-search "how many legs do a cat have?" --ai-only

## 2026-06-08 - Config ownership

Configuration should have one user-facing config file with separate ownership sections.

Target shape:

```ini
[search]
provider = local_search
fallback_provider = duckduckgo
provider_url = http://localhost:8080

[ai]
chat_model = qwen2.5-coder:3b
summary_model = phi3:mini
ollama_base_url = http://127.0.0.1:11434

[integration]
default_mode = integrated
evidence_limit = 5
evidence_max_chars = 4000
```

Decision:

There should be one user-facing config file, but each domain keeps its own config ownership.

Ownership:

* `[search]` is owned by search behavior
* `[ai]` is owned by AI behavior
* `[integration]` is owned by orchestration behavior

The code may continue to use separate `config.py` modules for:

* `local_ai`
* `local_search`
* `local_ai_search`

Shared settings must not be duplicated ambiguously.

When commands are run through `local-ai-search`, the resolved top-level configuration should be treated as canonical for integrated behavior.

---

## 2026-06-08 - Shell ownership

Decision:

`local_ai` owns shell implementation.

`local_ai_search` should not implement a second shell.

If `local-ai-search --shell` is implemented, it should be a delegating entry point to:

```bash
local-ai --shell
```

Future search-aware shell behavior should extend the existing `local_ai` shell or use an explicit integration mode rather than duplicating shell UX in `local_ai_search`.

---

## 2026-06-08 - Subprocess vs import boundary

Decision:

Keep subprocess as the first-class integration boundary for now.

Direct Python imports are deferred until:

* user-facing behavior is stable
* config ownership is stable
* repository ownership is stable

Subprocess calls should be wrapped in adapter/helper functions so the implementation can later switch from subprocess to direct imports without changing CLI behavior.

Subprocess boundaries must respect config ownership.

Shared settings should come from the canonical user-facing configuration and be passed explicitly through adapters wherever possible.

---

## 2026-06-08 - Repository ownership model

Decision:

Move toward a monorepo with separate packages and separate command surfaces.

Target source layout:

```text
src/
  local_ai/
  local_search/
  local_ai_search/
```

Commands should remain:

```text
local-ai
local-search
local-ai-search
```

Do not fully merge packages.

Do not remove the `local-ai` or `local-search` command surfaces.

During initial consolidation:

* keep `paths.py` separate
* keep `logging.py` separate
* keep runtime data roots separate
* keep run logs separate

Runtime data migration should be explicit, tested, and deferred until after code consolidation.

```text
~/local_ai_search/data/
  local_ai/
  local_search/
  local_ai_search/
```

Runtime data migration should be:

* explicit
* tested
* deferred until after code consolidation

---

## 2026-06-08 - Effort to combine projects

Evaluation:

Combining `local_ai`, `local_search`, and `local_ai_search` into one monorepo is reasonable if packages remain separate.

A full package merge is not recommended at this time.

Estimated effort:

Medium.

Expected work:

* move packages into one repository
* preserve package names
* preserve command names
* merge pyproject entry points
* merge test commands
* update CI
* keep imports stable
* keep runtime data stable

Primary risks:

* packaging conflicts
* test path assumptions
* duplicate dependency declarations
* console script conflicts
* CI changes
* accidental runtime data migration

Decision:

Monorepo consolidation is the preferred long-term repository direction.

Actual migration should be deferred until the first integrated query behavior is implemented and tested.

## 2026-06-15 - Monorepo runtime layout

Target runtime layout:

```text
data/
  local_ai/
  local_search/
  local_ai_search/

  logs/
    local_ai/
      run.log
    local_search/
      run.log
    local_ai_search/
      run.log
```

## 2026-06-18 - Test ownership

Tests remain package-local.

src/local_ai/test
src/local_search/test
src/local_ai_search/test

Reason:

* preserves package boundaries
* preserves ownership
* keeps behavior inspectable

The monorepo uses a shared test runner and shared CI workflow,
but test organization remains package-specific.

## 2026-06-18 - Phase 2.2 GUI/API direction

The first GUI should use a solid local API middle layer.

The frontend should be intentionally simple and replaceable.

`local_ai_search` should expose existing Python behavior through a local-only API,
then place a minimal web UI on top of that API.

Reason:

* keeps CLI first-class
* avoids frontend lock-in
* makes future desktop/web/mobile UI possible
* preserves inspectable backend behavior

## 2026-06-19 - API contract

The local API is the middle layer between frontend clients and existing Python behavior.

The API is versioned under `/api/v1`.

The API must bind to localhost by default.

The frontend is replaceable and should only depend on the API contract.

The CLI remains first-class and must not depend on the GUI.

Query modes are explicit:

- integrated
- ai_only
- web_only

Responses use a stable JSON envelope:

- ok
- mode
- query
- answer
- evidence
- elapsed_ms
- error

## 2026-06-22 - GUI/API boundary

Decision:

The GUI is a consumer of the local API.

The API is the stable integration boundary.

The frontend owns presentation only and must not perform retrieval, evidence generation, or prompt construction.

Reason:

* keeps CLI first-class
* avoids frontend lock-in
* preserves inspectable behavior
* enables future clients