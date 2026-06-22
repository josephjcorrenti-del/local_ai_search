import { runQuery } from "./api";
import { renderChat } from "./render-chat";
import { renderSearch } from "./render-search";
import type { QueryMode } from "./types";
import "./styles.css";

const app = document.querySelector<HTMLDivElement>("#app");

if (!app) {
  throw new Error("missing #app");
}

app.innerHTML = `
  <section class="shell">
    <header class="hero">
      <p class="eyebrow">local first · LAN friendly · API backed</p>
      <h1>local_ai_search</h1>
      <p>Search the web/local evidence or ask your local AI with sources.</p>
    </header>

    <form id="query-form" class="query-form">
      <input id="query" name="query" placeholder="Search or ask..." required />
      <select id="mode" name="mode">
        <option value="integrated">integrated</option>
        <option value="ai_only">ai only</option>
        <option value="web_only">web only</option>
      </select>
      <button type="submit">Run</button>
    </form>

    <section id="output" class="output"></section>
  </section>
`;

const form = document.querySelector<HTMLFormElement>("#query-form");
const queryInput = document.querySelector<HTMLInputElement>("#query");
const modeSelect = document.querySelector<HTMLSelectElement>("#mode");
const output = document.querySelector<HTMLElement>("#output");

if (!form || !queryInput || !modeSelect || !output) {
  throw new Error("missing UI elements");
}

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

  output.innerHTML = `
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `;

  try {
    const response = await runQuery(query, mode);

    if (!response.ok) {
      output.innerHTML = `
        <section class="error-card">
          <h2>Request failed</h2>
          <p>${response.error?.message ?? "Unknown error"}</p>
        </section>
      `;
      return;
    }

    output.innerHTML =
      response.mode === "web_only"
        ? renderSearch(response)
        : renderChat(response);
  } catch (error) {
    output.innerHTML = `
      <section class="error-card">
        <h2>Request failed</h2>
        <p>${error instanceof Error ? error.message : "Unknown error"}</p>
      </section>
    `;
  }
});
