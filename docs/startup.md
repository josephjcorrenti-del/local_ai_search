# Startup and Availability

`local_ai_search` is the integration command for the local AI/search stack.

## Ecosystem checks

By default, `status` and `doctor` check the full ecosystem:

```bash
local-ai-search status
local-ai-search doctor
```

That means:

```text
local_ai_search
local_search
local_ai
```

To check only `local_ai_search`:

```bash
local-ai-search status --self
local-ai-search doctor --self
```

## Dependencies

The `local_ai_search` environment must have these commands available:

```bash
local-ai-search
local-search
local-ai
```

For local development, install dependencies into the `local_ai_search` virtual environment:

```bash
cd ~/local_ai_search
source .venv/bin/activate

pip install -e ~/local_search
pip install -e ~/ai/local_ai
```

Verify command availability:

```bash
which local-ai-search
which local-search
which local-ai
```

## Status verification

Verify the integrated stack:

```bash
local-ai-search status
```

Verify only `local_ai_search`:

```bash
local-ai-search status --self
```

## Doctor verification

Verify the integrated stack:

```bash
local-ai-search doctor
```

Verify only `local_ai_search`:

```bash
local-ai-search doctor --self
```

A healthy ecosystem should report:

```text
local_ai_search
local_search
local_ai
```

without errors.

## Post-reboot startup

Start Ollama before using AI-backed commands:

```bash
bash ~/scripts/ollama_start.sh
bash ~/scripts/ollama_status.sh
```

Verify the stack:

```bash
local-ai-search doctor
```

Expected healthy result:

```text
local_ai_search doctor passed
local_search doctor passed
local_ai doctor passed
```

If only search functionality is required, Ollama is not required.

## Design notes

`local_ai_search` is the orchestration layer.

Responsibilities:

```text
local_ai
  - model interaction
  - shell UX
  - profiles
  - workspaces

local_search
  - indexing
  - retrieval
  - artifacts
  - evidence generation

local_ai_search
  - integration
  - validation
  - orchestration
  - evidence consumption
```

The default status and doctor behavior reflects this architecture by checking the full stack rather than only the integration layer.

## Status Checks

### Full Ecosystem

```bash
local-ai-search status
```

Checks:

```text
local_ai_search
local_search
local_ai
```

This is the default behavior.

### Integration Layer Only

```bash
local-ai-search status --self
```

Checks:

```text
local_ai_search
```

only.

### Individual Components

```bash
local-search status
```

Checks the search subsystem.

```bash
local-ai status
```

Checks the AI subsystem.

### Doctor Checks

```bash
local-ai-search doctor
```

Runs health checks for:

```text
local_ai_search
local_search
local_ai
```

```bash
local-ai-search doctor --self
```

Runs health checks for:

```text
local_ai_search
``` 

only.

