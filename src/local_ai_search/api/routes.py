from __future__ import annotations

import time

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from local_ai_search import pipeline
from local_ai_search.adapters import local_ai, local_search
from local_ai_search.api.schemas import QueryRequest, QueryResponse
from local_ai_search.artifacts import latest_web_artifact_for_query
from local_ai_search.config import load_config
from local_ai_search.evidence import load_evidence_from_local_search

router = APIRouter()


@router.get("/status")
def status() -> dict:
    return {
        "ok": True,
        "service": "local_ai_search",
        "version": "0.1",
        "checks": {
            "local_ai_search": True,
            "local_ai": None,
            "local_search": None,
        },
    }


@router.get("/config")
def config() -> dict:
    return {
        "ok": True,
        "config": {},
    }


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    started = time.perf_counter()

    answer = None
    evidence = None

    if request.mode == "ai_only":
        answer = local_ai.ask(request.query)

    elif request.mode in ("web_only", "integrated"):
        local_search.search(request.query)

        config = load_config()
        artifact_path = latest_web_artifact_for_query(request.query)

        evidence = load_evidence_from_local_search(
            artifact_path,
            limit=request.limit or config.integration.evidence_limit,
            max_chars=request.max_chars or config.integration.evidence_max_chars,
        )

        if request.mode == "integrated":
            answer = pipeline.run_query(
                request.query,
                evidence,
            )

    return QueryResponse(
        ok=True,
        mode=request.mode,
        query=request.query,
        answer=answer,
        evidence=evidence,
        elapsed_ms=int((time.perf_counter() - started) * 1000),
    )


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>local_ai_search</title>
</head>
<body>
  <h1>local_ai_search</h1>

  <form id="query-form">
    <input id="query" name="query" size="60" placeholder="Ask something..." required>
    <select id="mode" name="mode">
      <option value="integrated">integrated</option>
      <option value="ai_only">ai only</option>
      <option value="web_only">web only</option>
    </select>
    <button type="submit">Run</button>
  </form>

  <h2>Answer</h2>
  <pre id="answer"></pre>

  <h2>Results</h2>
  <div id="results"></div>

  <h2>Raw Response</h2>
  <pre id="raw-response"></pre>

<script>
function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.getElementById("query-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = document.getElementById("query").value;
  const mode = document.getElementById("mode").value;

  const answerEl = document.getElementById("answer");
  const resultsEl = document.getElementById("results");
  const rawEl = document.getElementById("raw-response");

  answerEl.textContent = "Working...";
  resultsEl.innerHTML = "";
  rawEl.textContent = "";

  const response = await fetch("/api/v1/query", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      query,
      mode,
      limit: 5,
      max_chars: 4000
    })
  });

  const data = await response.json();

  rawEl.textContent = JSON.stringify(data, null, 2);

  if (!data.ok) {
    answerEl.textContent = data.error ? data.error.message : "Request failed";
    return;
  }

  answerEl.textContent = data.answer || "";

  if (data.evidence && data.evidence.results) {
    resultsEl.innerHTML = data.evidence.results.map((result) => `
      <article style="margin-bottom: 1rem;">
        <strong>${escapeHtml(result.rank)}. ${escapeHtml(result.title)}</strong><br>
        <a href="${escapeHtml(result.url)}" target="_blank" rel="noopener noreferrer">
          ${escapeHtml(result.url)}
        </a>
        <p>${escapeHtml(result.snippet)}</p>
      </article>
    `).join("");
  }
});
</script>
</body>
</html>
"""