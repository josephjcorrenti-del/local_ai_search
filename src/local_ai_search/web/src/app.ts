import { runQuery } from "./api";
import { renderChat, type ChatTurn } from "./render-chat";
import { renderSearch } from "./render-search";
import type { QueryMode } from "./types";
import "./styles.css";

const app = document.querySelector<HTMLDivElement>("#app");

if (!app) {
  throw new Error("missing #app");
}

app.innerHTML = `
  <section class="app-shell">
    <main id="conversation" class="conversation">
      <section id="empty-state" class="empty-state">
        <p class="eyebrow">local first · LAN friendly · API backed</p>
        <h1>Local AI Search</h1>
        <p>Search the web/local evidence or ask your local AI with sources.</p>
      </section>

      <section id="output" class="output"></section>
    </main>

    <footer class="composer-shell">
      <section class="brand">
        <h2>Local AI Search</h2>
        <p>local first · LAN friendly · API backed</p>
      </section>

      <form id="query-form" class="query-form">
        <input id="query" name="query" placeholder="Search or ask..." required />
        <select id="mode" name="mode">
          <option value="integrated">integrated</option>
          <option value="ai_only">ai only</option>
          <option value="web_only">web only</option>
        </select>
        <button type="submit">Run</button>
      </form>

      <p class="privacy-note">Your data stays on your machine.</p>
    </footer>
  </section>
`;

const form = document.querySelector<HTMLFormElement>("#query-form");
const queryInput = document.querySelector<HTMLInputElement>("#query");
const modeSelect = document.querySelector<HTMLSelectElement>("#mode");
const output = document.querySelector<HTMLElement>("#output");
const emptyState = document.querySelector<HTMLElement>("#empty-state");

if (!form || !queryInput || !modeSelect || !output || !emptyState) {
  throw new Error("missing UI elements");
}

const chatTurns: ChatTurn[] = [];

const initialParams = new URLSearchParams(window.location.search);
const initialQuery = initialParams.get("query");
const initialMode = initialParams.get("mode");

if (initialQuery) {
  queryInput.value = initialQuery;
}

if (initialMode === "integrated" || initialMode === "ai_only" || initialMode === "web_only") {
  modeSelect.value = initialMode;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  const mode = modeSelect.value as QueryMode;

  if (!query) {
    return;
  }

  emptyState.hidden = true;

  if (mode === "web_only") {
    output.innerHTML = renderLoading();
  } else {
    output.innerHTML = `
      ${renderChat(chatTurns)}
      ${renderLoading()}
    `;
  }

  try {
    const response = await runQuery(query, mode);

    if (!response.ok) {
      output.innerHTML = renderError(response.error?.message ?? "Unknown error");
      return;
    }

    if (response.mode === "web_only") {
      output.innerHTML = renderSearch(response);
      return;
    }

    chatTurns.push({ query, response });
    output.innerHTML = renderChat(chatTurns);
    queryInput.value = "";
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  } catch (error) {
    output.innerHTML = renderError(
      error instanceof Error ? error.message : "Unknown error",
    );
  }
});

function renderLoading(): string {
  return `
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `;
}

function renderError(message: string): string {
  return `
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${escapeHtml(message)}</p>
    </section>
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
