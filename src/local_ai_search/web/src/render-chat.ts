import type { QueryResponse } from "./types";

export function renderChat(response: QueryResponse): string {
  const sources = response.evidence?.results ?? [];

  return `
    <section class="chat">
      <article class="message user-message">
        <div class="message-label">You</div>
        <p>${escapeHtml(response.query)}</p>
      </article>

      <article class="message assistant-message">
        <div class="message-label">local_ai_search</div>
        <div class="answer">${formatAnswer(response.answer || "No answer returned.")}</div>
      </article>

      ${
        sources.length > 0
          ? `
            <details class="sources" open>
              <summary>Sources</summary>
              ${sources
                .map(
                  (source) => `
                    <article class="source">
                      <a href="${escapeAttr(source.url)}" target="_blank" rel="noopener noreferrer">
                        ${escapeHtml(source.title || "Untitled")}
                      </a>
                      <p>${escapeHtml(source.snippet || "")}</p>
                    </article>
                  `,
                )
                .join("")}
            </details>
          `
          : ""
      }

      <details class="debug">
        <summary>Raw response</summary>
        <pre>${escapeHtml(JSON.stringify(response, null, 2))}</pre>
      </details>
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
