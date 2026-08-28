# Answer Quality Rubric

Phase 2.3 defines a good `local_ai_search` answer as conversational, accurate, fast, and evidence-aware.

## Goals

A good integrated answer should:

- answer the user's question directly
- stay conversational and readable
- use supplied evidence when relevant
- avoid unsupported claims
- distinguish certainty from uncertainty
- acknowledge conflicting evidence when present
- keep provenance visible through application-owned evidence summaries
- avoid making the model responsible for inventing provenance
- remain fast enough for local interactive use

## Scoring rubric

Use this rubric when comparing `ai_only`, `web_only`, and `integrated` output quality.

### 1. Directness

The answer should address the user's actual request first.

Good:

- gives the requested code, answer, or explanation immediately
- avoids unnecessary preamble

Bad:

- starts with retrieval commentary
- repeats the question
- answers a related but different question

### 2. Conversational quality

The answer should feel like a helpful assistant in a chat window.

Good:

- natural language
- clear structure
- concise unless detail is needed

Bad:

- raw search-summary style
- overly formal report style
- unnecessary verbosity

### 3. Accuracy

The answer should be factually correct and technically sound.

Good:

- uses correct syntax, dates, names, and facts
- avoids overgeneralization
- does not hallucinate details

Bad:

- makes unsupported claims
- gives broken code
- treats weak evidence as certain

### 4. Evidence use

The answer should use supplied evidence when it is relevant.

Good:

- aligns with the evidence package
- explains uncertainty when evidence is weak
- avoids claiming more than the evidence supports

Bad:

- ignores relevant evidence
- overfits to a bad search result
- cites or describes evidence that was not supplied

### 5. Provenance

The model places inline evidence references. The application validates those
references and owns their presentation.

Good:

- evidence-backed claims use exact references such as `[1]` or `[1][3]`
- references use only ranks supplied with the selected evidence
- the application validates references before returning the answer
- the frontend links valid references to their corresponding sources
- evidence remains visible and inspectable

Bad:

- references are missing from evidence-backed claims
- references identify nonexistent evidence ranks
- the model invents vague or unmapped provenance
- sources are hidden unless raw JSON is opened

### 6. Competing evidence and uncertainty

When evidence disagrees, the answer should surface that clearly.

Good:

- says when sources differ
- gives the most likely answer with appropriate confidence
- identifies what would be needed to be more certain

Bad:

- picks one side without explanation
- presents disagreement as settled fact
- refuses useful synthesis when evidence is merely incomplete

### 7. Speed

The answer should remain usable interactively on local hardware.

Good:

- avoids unnecessary retrieval
- avoids unnecessary prompt bloat
- returns in an acceptable time for the task

Bad:

- searches when conversation history is sufficient
- sends excessive evidence to the model
- makes simple tasks feel slow

## Scoring

Score each applicable category using:

- `2` — meets the target
- `1` — partially meets the target
- `0` — fails the target
- `N/A` — not applicable to this mode or scenario

Record both the score and a short observation. Compare percentages using only
applicable categories rather than treating `N/A` as zero.

## Current quality targets

### Simple coding request

Example:

```text
Make a simple Python program that says hello world.
```

Expected:

- `ai_only` returns runnable Python directly.
- `web_only` returns relevant results if retrieval is requested.
- `integrated` returns runnable Python without allowing incidental evidence to
  distort common syntax.
- The answer does not cite ordinary language syntax unless a factual claim
  depends on supplied evidence.

### Stable factual question

Example:

```text
What is SQLite?
```

Expected:

- The answer defines SQLite directly and accurately.
- Integrated output uses relevant evidence.
- Evidence-backed factual claims contain valid inline references.
- The answer does not describe the retrieval process.

### Freshness-sensitive question

Example:

```text
What is the latest stable Python release?
```

Expected:

- `ai_only` may acknowledge that its knowledge could be outdated.
- `web_only` returns current, relevant results.
- `integrated` uses current evidence and does not substitute stale model
  knowledge for supplied facts.
- Dates and version numbers are qualified when evidence is incomplete.

### Weak or insufficient evidence

Use a controlled evidence package that does not establish the requested fact.

Expected:

- The answer does not treat unrelated evidence as support.
- Missing information is identified clearly.
- General model knowledge is distinguished from evidence-backed information.
- The answer prefers uncertainty over invention.

### Competing evidence

Use a controlled evidence package containing two incompatible claims.

Expected:

- Both claims remain visible to the answer model.
- The answer states that the sources disagree.
- The answer does not silently select one claim.
- Any conclusion is appropriately qualified.
- References identify the evidence supporting each competing claim.

### Conversational follow-up

Example session:

```text
User: I prefer SQLite for small local applications.
User: What database did I just tell you I prefer?
```

Expected:

- The second message is resolved from session context.
- Unnecessary web retrieval is skipped.
- The response identifies SQLite directly.
- The original user message and final answer are persisted.

### Standalone topic change

Example session:

```text
User: What IDEs are good for Python and Go?
User: What LLMs are used for art?
```

Expected:

- The second message is treated as a standalone topic.
- Retrieval concerns art or image-generation models.
- Unrelated Python, Go, and IDE context is excluded from the answer context.
- The answer does not discuss Python or Go unless the user connects the topics.
- Both turns remain persisted in the same session.

## Comparison record

For every scenario, record:

| Field | Value |
| --- | --- |
| Date and time | |
| Mode or command | |
| Model | |
| Query | |
| Session | |
| Evidence provider | |
| Evidence relevance | |
| Directness | |
| Conversational quality | |
| Accuracy | |
| Evidence use | |
| Provenance | |
| Competing evidence and uncertainty | |
| Elapsed time | |
| Notes | |

Keep live-model comparison results out of deterministic pytest. Runtime output
may vary by model, available evidence, index contents, and execution environment.
