import { escapeAttr, escapeHtml } from "./render-utils";
import type {
  EvidenceAccounting,
  EvidenceResult,
  QueryResponse,
} from "./types";

export function renderEvidenceTitle(result: EvidenceResult): string {
  const label = result.source_type
    ? `<span class="source-type">${escapeHtml(result.source_type)}</span> `
    : "";

  const title = escapeHtml(result.title || "Untitled");

  if (result.url) {
    return `
      ${label}<a
        class="result-title"
        href="${escapeAttr(result.url)}"
        target="_blank"
        rel="noopener noreferrer"
      >
        ${title}
      </a>
    `;
  }

  return `${label}<strong class="result-title">${title}</strong>`;
}

export function renderEvidenceUrl(result: EvidenceResult): string {
  if (!result.url) {
    return "";
  }

  return `
    <div class="result-url">${escapeHtml(result.url)}</div>
  `;
}

export function renderEvidenceSnippet(result: EvidenceResult): string {
  if (!result.snippet) {
    return "";
  }

  return `<p>${escapeHtml(result.snippet)}</p>`;
}

export function renderEvidenceAccountingText(
  accounting: EvidenceAccounting,
): string {
  return `Found: ${accounting.available_count} · Used: ${accounting.evidence_count} · Shown: ${accounting.displayed_count}`;
}

export function renderDebugResponse(response: QueryResponse): string {
  return `
    <details class="debug">
      <summary>Raw response</summary>
      <pre>${escapeHtml(JSON.stringify(response, null, 2))}</pre>
    </details>
  `;
}
