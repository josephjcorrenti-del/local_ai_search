import type { QueryResponse } from "./types";

export function renderSearch(response: QueryResponse): string {
  const results = response.evidence?.results ?? [];

  if (results.length === 0) {
    return `
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${renderDebug(response)}
      </section>
    `;
  }

  return `
    <section class="search-results">
      <p class="result-count">${results.length} results · ${response.elapsed_ms} ms</p>
      ${results
        .map(
          (result) => `
            <article class="search-result">
              <a class="result-title" href="${escapeAttr(result.url)}" target="_blank" rel="noopener noreferrer">
                ${escapeHtml(result.title || "Untitled")}
              </a>
              <div class="result-url">${escapeHtml(result.url || "")}</div>
              <p>${escapeHtml(result.snippet || "")}</p>
            </article>
          `,
        )
        .join("")}
      ${renderDebug(response)}
    </section>
  `;
}

function renderDebug(response: QueryResponse): string {
  return `
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${escapeHtml(JSON.stringify(response, null, 2))}</pre>
    </details>
  `;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value: string): string {
  return escapeHtml(value);
}
