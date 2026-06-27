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
                  <summary>Sources</summary>
                  <ol>
                    ${sources
                      .map(
                        (source) => `
                          <li>
                            <a href="${escapeAttr(source.url)}" target="_blank" rel="noopener noreferrer">
                              ${escapeHtml(source.title || "Untitled")}
                            </a>
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
                    <strong>Web</strong>
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
