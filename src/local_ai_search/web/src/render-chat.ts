import type { QueryResponse } from "./types";

export type ChatTurn = {
  query: string;
  response: QueryResponse;
};

export function renderChat(turns: ChatTurn[]): string {
  if (turns.length === 0) {
    return "";
  }

  return `
    <section class="chat">
      ${turns.map((turn) => renderTurn(turn)).join("")}
    </section>
  `;
}

function renderTurn(turn: ChatTurn): string {
  const sources = turn.response.evidence?.results ?? [];
  const accounting = turn.response.accounting;

  return `
    <section class="chat-turn">
      <article class="message user-message">
        <div class="avatar">●</div>
        <div>
          <div class="message-label">You</div>
          <p>${escapeHtml(turn.query)}</p>
        </div>
      </article>

      <article class="message assistant-message">
        <div class="avatar bot">◎</div>
        <div class="message-body">
          <div class="message-label assistant-label">Local AI Search</div>
          <div class="answer">${formatAnswer(turn.response.answer || "No answer returned.")}</div>
          ${
            sources.length > 0
              ? `
                <details class="sources" open>
                  <summary>Evidence</summary>
                  <ol>
                    ${sources
                      .map(
                        (source) => `
                          <li>
                            ${renderEvidenceTitle(source)}
                            ${
                              source.url
                                ? `<div class="result-url">${escapeHtml(source.url)}</div>`
                                : ""
                            }
                            ${
                              source.snippet
                                ? `<p>${escapeHtml(source.snippet)}</p>`
                                : ""
                            }
                          </li>
                        `,
                      )
                      .join("")}
                  </ol>
                </details>
              `
              : ""
          }
          ${
            accounting
              ? `
                <details class="sources evidence-details" open>
                  <summary>Evidence</summary>
                  <section class="evidence-summary">
                    <strong>Evidence summary</strong>
                    <p>
                      Found: ${accounting.available_count}
                      &nbsp; Used: ${accounting.evidence_count}
                      &nbsp; Shown: ${accounting.displayed_count}
                    </p>
                  </section>
                </details>
              `
              : ""
          }
          <details class="debug">
            <summary>Raw response</summary>
            <pre>${escapeHtml(JSON.stringify(turn.response, null, 2))}</pre>
          </details>
        </div>
      </article>
    </section>
  `;
}

function renderEvidenceTitle(result: {
  title?: string;
  url?: string;
  source_type?: string;
}): string {
  const label = result.source_type
    ? `<span class="source-type">${escapeHtml(result.source_type)}</span> `
    : "";
  const title = escapeHtml(result.title || "Untitled");

  if (result.url) {
    return `
      ${label}<a class="result-title" href="${escapeAttr(result.url)}" target="_blank" rel="noopener noreferrer">
        ${title}
      </a>
    `;
  }

  return `${label}<strong class="result-title">${title}</strong>`;
}

function formatAnswer(value: string): string {
  return escapeHtml(value)
    .split("\n\n")
    .map((paragraph) => `<p>${paragraph.replaceAll("\n", "<br>")}</p>`)
    .join("");
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
