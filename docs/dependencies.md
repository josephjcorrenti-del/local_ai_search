# Dependencies

## Philosophy

`local_ai_search` integrates existing tools.

It does not replace them.

The project assumes:

```text
local_ai_search
    depends on
        local_search
        local_ai
```

The first integration boundary is command-based.

No direct Python imports are required between projects.

## Required Commands

The following commands must be available:

```bash
local-ai-search
local-search
local-ai
```

Verify:

```bash
which local-ai-search
which local-search
which local-ai
```

## local_search Dependency

`local_search` is responsible for:

```text
- indexing
- retrieval
- search providers
- artifact persistence
- artifact cleanup
- evidence generation
```

`local_ai_search` consumes evidence through:

```bash
local-search evidence PATH
```

Example:

```bash
local-search evidence artifact.json
```

`local_ai_search` should not parse raw artifacts directly at the first integration boundary.

## local_ai Dependency

`local_ai` is responsible for:

```text
- model interaction
- prompt construction
- shell UX
- profiles
- workspaces
```

`local_ai_search` may delegate AI operations to `local_ai`.

## Installation

For development:

```bash
cd ~/local_ai_search
source .venv/bin/activate

pip install -e ~/local_search
pip install -e ~/ai/local_ai
```

Verify:

```bash
local-search status
local-ai status
local-ai-search status
```

## Runtime Dependency

AI-backed commands require Ollama.

Verify:

```bash
bash ~/scripts/ollama_status.sh
```

or:

```bash
local-ai doctor
```

Search-only operations do not require Ollama.

## Ecosystem Verification

Verify the complete stack:

```bash
local-ai-search doctor
```

Verify only the integration layer:

```bash
local-ai-search doctor --self
```

