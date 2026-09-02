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
[x] preserve package names
[x] preserve commands
[x] preserve runtime data
[x] consolidate test execution
[x] consolidate CI workflow
[x] remove duplicated test helpers
[x] document package test ownership

### Phase 2.2 – GUI / Local API

[x] decide local API stack
[x] define API contract before frontend
[x] expose status endpoint
[x] expose config endpoint
[x] expose query endpoint
[x] expose ai-only mode
[x] expose web-only mode
[x] open from browser
[x] ai_only works
[x] web_only works
[x] access FE on local network
[x] integrated works
[x] test CLI usability
[x] create minimal TypeScript frontend
[x] render web_only as search
[x] render ai_only/integrated as conversation
[x] make raw response optional
[x] remove old inline HTML
[x] remove results
[x] add minimal styling
[x] document GUI/API boundary

### Phase 2.3 – Results quality

[x] add answer quality rubric
[x] improve evidence prompt
[x] unify CLI and API integrated pipeline
[x] define evidence source types
[x] expose retrieved/used/displayed counts
[x] inspect local_ai workspace contract

#### Session and intent foundation

[x] support local_ai sessions in integrated queries
[x] add deterministic intent gate before retrieval
[x] support session evidence source
[x] classify insufficient conversational context

#### Workspace and filesystem evidence

[x] support workspace evidence source
[x] support explicit filesystem evidence roots
[x] support automatic filesystem traversal for approved project roots
[x] use r/o filesystem for evidence

#### Update Front end to use new evidence source types

[x] add session to FE
[x] order sessions by last message date
[x] add workspace to FE
[ ] add filesystem to FE
[ ] verify the all results quality results are available in FE
[ ] workspace first screen needs to be able to access files and sessions

#### Search independence

[x] guarantee deterministic pytest does not call live web providers
[ ] search fresh cached evidence before external retrieval
[ ] reuse relevant cached evidence across differently worded queries
[ ] refresh relevant known source URLs before general web search
[ ] build a context-resolved external retrieval query when needed
[ ] distinguish results, genuine zero results, degraded provider, and unavailable provider
[ ] cache exact-query successes, zero results, and provider failures
[ ] add provider cooldown and circuit-breaker behavior
[ ] use SearXNG only when healthy
[ ] support an optional authenticated fallback provider
[ ] cache successful fallback results through the existing artifact system
[ ] fail safely when every provider is unavailable

[ ] support preferred and blocked website domains
[ ] exclude blocked domains from cached and newly retrieved evidence
[ ] record explicit source visits locally
[ ] apply preferred-domain boosts only to already-relevant results
[ ] apply a smaller capped previous-visit boost only to already-relevant results
[ ] keep topical relevance, freshness, and authority above stored preferences
[ ] expose domain and visit-ranking policy through config before adding frontend controls

#### Answer quality behavior

[x] make default query mode evidence-aware
[x] support uncertainty/competing-evidence language
[x] verify local_ai uses the current monorepo runtime data directory
[x] render evidence references as clickable source links
[ ] render deterministic evidence summary after answer

#### Inline evidence references

[x] update the evidence prompt to require exact references such as `[1]` and `[1][3]`
[x] fixed bug where bold was not displaying correctly
[x] add a concise citation example to the prompt
[x] validate citations against the supplied evidence ranks
[x] detect evidence-backed answers with missing or invalid citations
[x] make one bounded citation-repair attempt when validation fails
[x] add tests for single, multiple, missing, malformed, and nonexistent references

#### Quality validation

[x] add deterministic integrated prompt_builder quality tests
[ ] compare local/search/AI output quality
[ ] prevent duplicate query submission
[ ] detect standalone topic changes and exclude unrelated session context
[ ] add an integrated regression test proving Python/Go context does not contaminate a new art question
[ ] separate session persistence from session-context inclusion
[ ] add regression coverage proving excluded session context does not prevent the current turn from being persisted
[ ] define precedence between selected workspace/filesystem context and automatic retrieval
[ ] evaluate citation-to-claim alignment and uncited evidence-backed claims
[ ] fail safely when required freshness retrieval returns no usable evidence
[ ] distinguish genuine zero-result searches from upstream web-provider failure

#### Conversational context and retrieval

[ ] load the selected session's recent history before interpreting each query
[ ] use session history to resolve corrections, refinements, and referential follow-ups
[ ] build a temporary context-resolved retrieval query when a follow-up needs search
[ ] decide whether retrieval is needed after resolving the follow-up's meaning
[ ] give the answer model both session context and any retrieved evidence
[ ] persist only the original user message and final answer in session history
[ ] avoid attaching short follow-ups to stale or unrelated session context
[ ] add integrated regression tests for multi-turn conversational queries

### Phase 2.3.0.1 – Frontend and Client Boundary Refactor

#### Documentation

[x] document frontend, middleware, and backend ownership
[x] document API consistency philosophy
[x] document frontend interaction-state ownership
[x] document backend ownership of defaults and validation
[x] document client-independent behavior
[x] document planning roles (Decisions / Phases / TBP)

#### API consistency

[x] inventory all /api/v1 endpoint contracts
[x] normalize HTTP status behavior
[x] define one structured API error contract
[x] make frontend API request handling consistent
[x] prepare API routes for shared request logging
[ ] define bounded API request logging
[ ] reuse structured backend logging for API requests
[x] add API consistency contract tests

#### Backend / middleware ownership

[x] remove duplicated backend defaults from frontend requests
[x] define canonical session/workspace query behavior
[x] define canonical default-session behavior
[x] verify browser behavior is client-independent
[x] move session creation policy into the backend
[x] verify browser behavior is client-independent

#### Frontend state

[x] introduce explicit resource-selection model
[x] stop using hidden DOM inputs as application state
[x] define application state ownership
[x] prepare state model for future filesystem integration

#### Duplication review

[x] inventory duplicated frontend behavior
[x] consolidate shared rendering primitives
[x] consolidate evidence rendering
[x] consolidate HTML escaping
[x] consolidate debug/status rendering

#### Responsibility extraction

[x] extract rendering ownership from app.ts
[x] extract navigation ownership from app.ts
[x] extract session ownership from app.ts
[x] extract workspace ownership from app.ts
[x] extract query lifecycle from app.ts
[x] reduce app.ts to application composition

#### local_ai_search should not be doing local_ai's job

[x] review local_ai_search session, workspace, prompt, CLI, and API ownership
[x] verify local_ai owns canonical session and workspace persistence
[x] verify local_ai owns session normalization, timestamps, bounded history, and summarization policy
[x] verify local_ai_search does not read or write session/workspace files directly
[x] keep retrieval, intent routing, evidence shaping, and evidence-aware prompt policy in local_ai_search
[x] keep navigation ordering and API response shaping in local_ai_search
[x] define one reusable local_ai chat operation that returns an answer without printing
[x] allow the local_ai chat operation to accept orchestrator-supplied instructions or evidence context
[x] keep session-history loading inside the canonical local_ai chat operation
[x] keep user and assistant message persistence inside the canonical local_ai operation
[x] expose usable session context through local_ai without requiring local_ai_search to interpret stored summary shape
[x] bug: session_summarize() returns before saving its generated summary, making the persistence block unreachable
[x] route integrated CLI and API queries through the canonical local_ai chat operation
[x] route ai_only CLI and API queries through the same canonical local_ai chat operation
[x] remove direct session_append ownership from local_ai_search
[x] remove direct session_turns_get use from local_ai_search prompt execution
[x] treat current local_ai_search query behavior as authoritative when package behavior conflicts
[x] preserve current integrated, ai_only, web_only, and insufficient-context behavior during ownership changes
[x] preserve current workspace/session association behavior during ownership changes
[x] verify default and named sessions behave identically through CLI and API
[x] add boundary tests proving local_ai_search delegates session lifecycle to local_ai
[x] audit local_ai_search AI model configuration for duplicated or unused local_ai runtime settings
[x] verify local_ai is the canonical owner of session lifecycle

#### Validation

[ ] verify CLI behavior remains unchanged
[ ] verify API contracts remain stable
[ ] verify frontend behavior is unchanged
[ ] verify future clients can rely solely on the API

### Phase 2.3.0.2 – Backend Package Ownership Refactor

#### Confirm ownership

[ ] update decisions to state that `local_ai` owns all model-facing AI logic
[ ] update decisions to state that `local_search` owns retrieval and evidence production
[ ] update decisions to limit `local_ai_search` to orchestration and the client/API boundary


#### Move AI responsibilities to local_ai

[ ] define a structured evidence input accepted by the canonical `local_ai` chat operation
[ ] move evidence-aware prompt construction from `local_ai_search` to `local_ai`
[ ] move uncertainty and competing-evidence instructions to `local_ai`
[ ] move inline-reference generation, validation, and bounded repair to `local_ai`
[ ] move session-context and workspace-context composition to `local_ai`
[ ] move conversational follow-up interpretation and temporary query resolution to `local_ai`
[ ] ensure `local_ai` persists only the original user message and final answer
[ ] remove obsolete session, workspace, and prompt builders from `local_ai_search`

#### Move retrieval responsibilities to local_search

[ ] make `local_search` return evidence without `local_ai_search` inspecting artifact directories
[ ] move web-artifact discovery and query-slug handling to `local_search`
[ ] move filesystem traversal, inclusion policy, and filesystem evidence construction to `local_search`
[ ] move filesystem retrieval configuration to the search-owned config section
[ ] keep evidence bounding and shaping owned by `local_search`

#### Reduce local_ai_search to orchestration

[ ] keep mode selection and package-call sequencing in `local_ai_search`
[ ] keep evidence contract validation at the integration boundary
[ ] keep evidence accounting and API response shaping in `local_ai_search`
[ ] replace direct `local_ai` and `local_search` internal imports with adapter operations
[ ] remove duplicate or obsolete intent and evidence paths
[ ] ensure selected session, workspace, filesystem, and web inputs reach the correct owner
[ ] preserve the existing public CLI, API, and frontend contracts

#### Validate the boundary

[ ] add tests proving `local_ai_search` delegates AI behavior to `local_ai`
[ ] add tests proving `local_ai_search` delegates retrieval behavior to `local_search`
[ ] add tests proving `local_ai_search` does not read package-owned runtime storage directly
[ ] add multi-turn regression tests for corrections and referential follow-ups
[ ] add integrated tests for evidence, uncertainty, and inline references
[ ] verify integrated, `ai_only`, and `web_only` behavior through CLI and API
[ ] verify session, workspace, filesystem, and frontend behavior remain stable
[ ] run all Python tests and the frontend production build

### Phase 2.3.1 – Results quality in GUI

[x] expose session selection/input in GUI
[ ] apply intent gate behavior to GUI queries
[ ] display when retrieval was skipped
[ ] display insufficient conversational context clearly
[x] expose workspace selection/input in GUI
[ ] display workspace/session evidence in evidence summary
[ ] display more search results
[x] keep full search/debug evidence available behind verbose/raw/details

### Phase 2.4 geek tabs
[ ] adjustable config
[ ] logs
[ ] status
[ ] doctor
[ ] evidence/artifacts
[ ] ollama serve output
[ ] web gui serve output
[ ] toggle on and off in settings

#### 2.4.1 Inline evidence references
[ ] add an integrated regression test proving Qwen produces valid inline references
[ ] measure citation-repair frequency and added latency

### Phase 2.5 Easy start update
[ ] start tools
[ ] upgrade tools
[ ] see status of tools

### Other enhancements
[ ] make code copyable
[ ] add a viewable history
[ ] delete history
[ ] decide DuckDuckGo/fallback role
[ ] add intent gate before retrieval
[ ] change http://192.168.1.60:8765/search/ to something that can be remembered
[ ] test_api.py has duplicate test_api_query_contract names
[ ] test_prompt_builder.py appears to have nested tests under test_run_query_uses_build_prompt

## TBP / Later

[ ] decide --shell delegation
[ ] why is local_search not searxng in config
[x] clean up tests
[ ] logs timestamp a day ahead?
[ ] decide whether local_ai, local_search, and local_ai_search should expose package APIs for GUI/API use
[ ] create docker container
[ ] make sure ELK still works correctly.
[ ] create/use chat summary for performance
[x] verify local_ai uses the current monorepo runtime data directory
[ ] verify local ai search uses default session
[ ] verify local ai acts like local ai search 
[ ] improve frontend navigation editing and resource organization
[ ] support assigning or moving sessions into workspaces through an intuitive UI
[ ] define initial chat behavior when the app opens without a selected session
[ ] decide whether the first message uses the default session, creates a new session, or prompts for a session
[ ] improve session and workspace creation UX
[ ] make it clear where a newly created session or workspace appears
[ ] replace bulky prompt-based creation flows with an integrated frontend interaction
[ ] need to be able to stop an ai search 
[ ] add easy startup and installation for Docker, SearXNG, Ollama, and the web server
[ ] get Hermes working with config-backed partial GPU offload

### Session lifecycle and explicit creation

- [ ] add a first-class `session_create()` operation to `local_ai`
- [ ] keep session-name normalization and storage validation owned by `local_ai`
- [ ] inspect supported filesystem constraints before defining invalid characters
- [ ] trim session names before validation and duplicate checks
- [ ] preserve case-sensitive, globally unique session names
- [ ] reserve only the exact configured default-session name
- [ ] persist explicitly created empty sessions with existing session metadata
- [ ] add `POST /api/v1/sessions` to expose explicit empty-session creation
- [ ] return `201` with the canonical trimmed session name
- [ ] make query-created sessions use the same lifecycle rules
- [ ] return consistent structured errors for invalid or duplicate session names
- [ ] keep workspace references separate from session ownership
- [ ] define recoverable behavior when session creation succeeds but workspace association fails
- [ ] add lifecycle tests in `local_ai` and API contract tests in `local_ai_search`

#### Runtime performance and troubleshooting

[ ] define a system-agnostic runtime diagnostics contract
[ ] report the effective AI-runtime configuration using supported platform mechanisms
[ ] detect settings that disable or restrict available hardware acceleration
[ ] detect whether the configured acceleration backend is available and healthy
[ ] report model placement, context size, loaded-model count, memory use, and accelerator utilization when available
[ ] report CPU and system-memory utilization when accelerator metrics are unavailable
[ ] warn when model loading, concurrency, context, or batch settings exceed detected system capacity
[ ] diagnose model-runner failures and identify the relevant application, runtime, or service logs
[ ] distinguish retrieval, model load, prompt evaluation, and response generation time
[ ] add a repeatable representative model benchmark that records accuracy, citation behavior, and timing
[ ] verify configured models can start using their effective placement, context, batch, and parallelism settings
[ ] make unsupported diagnostic capabilities explicit rather than treating them as failures
[ ] isolate platform-specific inspection behind replaceable diagnostic adapters
[ ] expose diagnostics through CLI first and make the results available to future status and doctor interfaces
[ ] add deterministic tests using platform-independent fixtures and mocked diagnostic adapters

#### Deterministic context composition

[ ] implement the context-source priority and conflict-resolution decision
[ ] include active project decisions as relevant model context
[ ] include session-associated files separately from session message history
[ ] consider selected workspace files and linked sessions when composing context
[ ] select relevant local/filesystem and web evidence according to the resolved question
[ ] preserve the current message and recent ordinary turns verbatim
[ ] summarize oversized or older terminal output and conversation history
[ ] retain original session messages and files so omitted details remain retrievable
[ ] allocate context by measured size or tokens instead of message count alone
[ ] keep the configured 4,000-character retrieved-evidence budget separate from conversation-history limits
[ ] reserve context capacity for the current question and generated answer
[ ] report which sources were included verbatim, summarized, retrieved, or omitted
[ ] add deterministic tests for priority, budgeting, conflict resolution, and oversized session content