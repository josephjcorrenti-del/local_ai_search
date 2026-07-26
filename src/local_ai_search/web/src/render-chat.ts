import {
  renderDebugResponse,
  renderEvidenceAccountingText,
  renderEvidenceSnippet,
  renderEvidenceTitle,
  renderEvidenceUrl,
} from "./render-evidence";
import { escapeHtml, formatText } from "./render-utils";
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
          <div class="answer">${formatText(turn.response.answer || "No answer returned.")}</div>
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
                            ${renderEvidenceUrl(source)}
                            ${renderEvidenceSnippet(source)}
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
                    <p>${renderEvidenceAccountingText(accounting)}</p>
                  </section>
                </details>
              `
              : ""
          }
          ${renderDebugResponse(turn.response)}
        </div>
      </article>
    </section>
  `;
}
