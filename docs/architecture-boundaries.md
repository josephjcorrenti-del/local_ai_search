# GUI / API Boundary

## Purpose

The GUI is a consumer of the local API.

The API is the stable integration boundary between frontend clients and existing Python behavior.

## User-facing routes

```text
/search
```

Future:

```text
/settings
/status
/artifacts
/logs
```

## API routes

```text
/api/v1/status
/api/v1/config
/api/v1/query
```

## Ownership

`local_ai` owns:

* model interaction
* prompt construction
* shell UX

`local_search` owns:

* retrieval
* search providers
* evidence generation

`local_ai_search` owns:

* orchestration
* API
* frontend hosting

The frontend owns presentation only.

The frontend must not perform retrieval, construct prompts, or bypass API contracts.

## Frontend

Current frontend:

```text
TypeScript
Vite
Static assets
```

Built assets are committed so:

```bash
local-ai-search serve
```

works without requiring a frontend build step.

## Principles

* CLI remains first-class
* API before GUI
* frontend is replaceable
* logs are the source of truth
* no hidden retrieval
* no hidden prompt injection
