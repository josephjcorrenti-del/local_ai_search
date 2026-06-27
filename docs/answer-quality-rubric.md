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

The application owns provenance.

Good:

- evidence counts are shown by the UI/API
- sources are visible and inspectable
- raw/debug response remains available

Bad:

- model invents vague provenance
- model claims it used sources without clear mapping
- provenance is hidden unless raw JSON is opened

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

## Current quality targets

### Simple coding request

Example:

```text
make a simple python program that says hello world
