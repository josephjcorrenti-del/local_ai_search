# local_ai_search Decisions

## 2026-07-26 - Documentation roles

Project documentation has three distinct planning roles:

- Decisions answer: “Why have we chosen this direction?”
- Numbered phases answer: “What are we intentionally working on now?”
- TBP / Later answers: “What should we remember even if it is not the right time?”

TBP is intentionally informal.

It is a capture area for:

- ideas discovered while coding
- questions that need later investigation
- possible defects
- usability observations
- work that was previously planned but has been deprioritized
- tasks that may return to an active phase as the project evolves

TBP items do not need the same structure or polish as active phase tasks.

Ideas may move:

- from TBP into an active phase
- from an active phase back into TBP
- between phases as architecture and priorities change
- out of the plan when they are no longer relevant

TBP should not be removed merely because it is unstructured or because its items are not currently scheduled.

When a TBP item becomes active work, it should be reviewed and rewritten as needed before or during promotion into a numbered phase.

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
* 
## 2026-06-29 - Session ownership

`local_ai` owns session storage.

`local_ai_search` does not implement a separate session system. It reuses the existing `local_ai` session APIs and storage so the same conversation can continue across CLI, shell, API, and web UI.

Both `local_ai` and `local_ai_search` can have complete conversations using the same session.

The difference is capability: `local_ai_search` can augment a session-backed conversation with retrieved evidence or web search when needed, while `local_ai` answers from the model/session context alone.

## 2026-06-30 Resource selection rule

If a flag points to an existing resource, `local_ai_search` should reuse the owning system rather than duplicate storage or parsing.

Examples:

- `--session` selects an existing `local_ai` session.
- `--workspace` selects an existing `local_ai` workspace.

However, existing resources are not automatically sufficient evidence.

When an answer depends on facts that may have changed, `local_ai_search` should consider the age and relevance of local evidence before relying on it. Older local evidence may be useful as context, but the prompt_builder should be able to seek newer or more relevant evidence when freshness matters.

## 2026-07-15 - Frontend responsibility boundary

The frontend owns browser presentation and interaction state.

The frontend may:

- render navigation and content
- track the currently selected resource
- collect user input
- display loading and errors
- call versioned API endpoints

The frontend must not:

- perform retrieval
- construct evidence
- construct AI prompts
- own session or workspace persistence
- define canonical resource-validity rules
- duplicate backend configuration defaults

The API must validate all request context independently of the frontend.

## 2026-07-15 - Frontend state model

Session, workspace, and future file selection should use one explicit resource-selection model.

DOM inputs may mirror selection for form submission, but they are not the source of truth.

Reason:

- prevents contradictory session/workspace state
- centralizes selection transitions
- prepares for filesystem navigation
- keeps rendering contexts independent from resource behavior

## 2026-07-15 - Frontend module ownership

The frontend remains plain TypeScript without a framework.

Target responsibilities:

- app.ts: composition and startup
- navigation.ts: navigation rendering and navigation events
- session.ts: session-specific presentation and transitions
- workspace.ts: workspace-specific presentation and transitions
- query.ts: query form lifecycle
- api.ts: HTTP boundary only

Modules should remain small and behavior-preserving.
A framework or state library requires a separate decision.

## 2026-07-15 - Middleware owns canonical defaults

Frontend requests should omit configurable values unless the user explicitly overrides them.

Defaults such as evidence limits, character limits, default mode, and default session are resolved by backend configuration.

The API may expose optional override fields for advanced clients.

## 2026-07-15 - Resource creation and selection rules

The owning backend defines canonical session and workspace creation behavior.

The frontend may prompt for names and present choices, but it must use API behavior rather than invent persistence semantics.

All frontend-only validation must also be validated by the API.

### 2026-07-16 - API logging and diagnostics

The API should reuse the existing structured NDJSON logging infrastructure.

API requests should follow the existing start, done, and error event pattern
and include a request or run identifier, route, method, outcome, status code,
and elapsed time.

Client-facing errors must remain stable and safe. Internal exception details,
tracebacks, and diagnostic context belong in structured logs rather than API
responses.

Request logging must be bounded and must not blindly record raw request bodies,
evidence packages, file contents, secrets, or other large or sensitive values.

A request identifier may later be included in structured API errors so a client
failure can be matched to backend logs.

## 2026-07-16 - Client-independent API behavior

The versioned local API must provide complete client-independent behavior.

Any rule required for a valid query or resource operation must be defined and
enforced by the API middleware rather than existing only in frontend code.

Browser, native, desktop, command-line, and future clients may present different
interaction flows, but clients using the API must receive consistent:

- request validation
- configured defaults
- session and workspace rules
- resource operation semantics
- orchestration behavior
- HTTP status behavior
- structured errors

A client must not need to inspect or reproduce the TypeScript frontend to use
the API correctly.

The CLI may continue to call shared Python behavior directly, but its observable
domain behavior should remain aligned with the API.

Reason:

- keeps the frontend replaceable
- supports future native clients
- prevents conflicting client implementations
- keeps canonical behavior in one inspectable layer