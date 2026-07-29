import "./styles.css";

import { createNavigationController } from "./navigation";
import { createQueryController } from "./query-lifecycle";
import type { ChatTurn } from "./render-chat";
import { createSessionController } from "./sessions";
import { createWorkspaceController } from "./workspaces";
import type {
  AppState,
  QueryMode,
  ResourceSelection,
} from "./types";

const app = document.querySelector<HTMLDivElement>("#app");

if (!app) {
  throw new Error("missing #app");
}

app.innerHTML = `
  <section class="app-shell">
      <aside id="navigation" class="navigation-panel">
        <section class="navigation-heading">
          <h2>Sessions</h2>
          <button id="new-session" type="button" class="new-session-button">+</button>
        </section>
        <p id="selected-session" class="selected-session">No session selected</p>
        <p id="selected-workspace" class="selected-workspace">No workspace selected</p>
        <div id="session-list" class="session-list"></div>
      </aside>

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
        <input id="query" class="query-input" name="query" placeholder="Search or ask..." required />
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
const sessionList = document.querySelector<HTMLElement>("#session-list");
const selectedSession =
  document.querySelector<HTMLElement>("#selected-session");
const selectedWorkspace =
  document.querySelector<HTMLElement>("#selected-workspace");
const newSessionButton =
  document.querySelector<HTMLButtonElement>("#new-session");
const queryInput = document.querySelector<HTMLInputElement>("#query");
const modeSelect = document.querySelector<HTMLSelectElement>("#mode");
const output = document.querySelector<HTMLElement>("#output");
const emptyState = document.querySelector<HTMLElement>("#empty-state");

if (
  !form ||
  !sessionList ||
  !selectedSession ||
  !selectedWorkspace ||
  !newSessionButton ||
  !queryInput ||
  !modeSelect ||
  !output ||
  !emptyState
) {
  throw new Error("missing UI elements");
}

const state: AppState = {
  selection: {
    session: null,
    workspace: null,
  },
  mode: "integrated",
};

const chatTurns: ChatTurn[] = [];
let loadedSessionHtml = "";

const initialParams = new URLSearchParams(window.location.search);
const initialQuery = initialParams.get("query");
const initialMode = initialParams.get("mode");

function setResourceSelection(selection: ResourceSelection): void {
  state.selection = {
    session: selection.session,
    workspace: selection.workspace,
  };

  navigationController.renderSelection(state.selection);
}

const sessionController = createSessionController({
  output,
  emptyState,
  queryInput,
  chatTurns,
  setResourceSelection,
  setLoadedSessionHtml: (html) => {
    loadedSessionHtml = html;
  },
});

const navigationController = createNavigationController({
  sessionList,
  selectedSession,
  selectedWorkspace,
  getResourceSelection: () => state.selection,
  createWorkspace: () => workspaceController.create(),
  openSession: (sessionName, workspaceName) =>
    sessionController.open(sessionName, workspaceName),
  openWorkspace: (workspace) => {
    workspaceController.open(workspace);
  },
});

const workspaceController = createWorkspaceController({
  output,
  emptyState,
  chatTurns,
  setResourceSelection,
  setLoadedSessionHtml: (html) => {
    loadedSessionHtml = html;
  },
  refreshNavigation: navigationController.refresh,
});

const queryController = createQueryController({
  output,
  emptyState,
  queryInput,
  chatTurns,
  state,
  setResourceSelection,
  getLoadedSessionHtml: () => loadedSessionHtml,
  refreshNavigation: navigationController.refresh,
});

navigationController.renderSelection(state.selection);
void navigationController.refresh();

newSessionButton.addEventListener("click", () => {
  const name = window.prompt("New session name:");
  const sessionName = name?.trim();

  if (!sessionName) {
    return;
  }

  setResourceSelection({
    session: sessionName,
    workspace: null,
  });

  chatTurns.length = 0;
  loadedSessionHtml = "";
  output.innerHTML = "";
  emptyState.hidden = false;
  queryInput.value = "";
  queryInput.focus();
});

if (initialQuery) {
  queryInput.value = initialQuery;
}

if (
  initialMode === "integrated" ||
  initialMode === "ai_only" ||
  initialMode === "web_only"
) {
  state.mode = initialMode;
  modeSelect.value = initialMode;
}

modeSelect.addEventListener("change", () => {
  state.mode = modeSelect.value as QueryMode;
});

form.addEventListener("submit", async (event) => {
  await queryController.submit(event);
});