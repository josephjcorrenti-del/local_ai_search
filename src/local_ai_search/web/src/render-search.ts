import {
  renderDebugResponse,
  renderEvidenceAccountingText,
  renderEvidenceSnippet,
  renderEvidenceTitle,
  renderEvidenceUrl,
} from "./render-evidence";
import type { QueryResponse } from "./types";

export function renderSearch(response: QueryResponse): string {
  const results = response.evidence?.results ?? [];
  const accounting = response.accounting;

  if (results.length === 0) {
    return `
      <section class="empty-state">
        <h2>No results</h2>
        <p>No search evidence was returned for this query.</p>
        ${renderDebugResponse(response)}
      </section>
    `;
  }

  return `
    <section class="search-results">
      <p class="result-count">
        ${
          accounting
            ? renderEvidenceAccountingText(accounting)
            : `${results.length} results`
        }
        · ${response.elapsed_ms} ms
      </p>
      ${results
        .map(
          (result) => `
            <article class="search-result">
              ${renderEvidenceTitle(result)}
              ${renderEvidenceUrl(result)}
              ${renderEvidenceSnippet(result)}
            </article>
          `,
        )
        .join("")}
      ${renderDebugResponse(response)}
    </section>
  `;
}
