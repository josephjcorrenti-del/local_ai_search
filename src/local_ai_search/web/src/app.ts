import "./styles.css";

import {
  createWorkspace,
  loadNavigation,
  runQuery,
} from "./api";
import {
  renderError,
  renderLoading,
  renderNavigation,
  renderWorkspaceOverview,
} from "./render-app";
import { renderChat, type ChatTurn } from "./render-chat";
import { escapeHtml } from "./render-utils";
import { renderSearch } from "./render-search";
import { createSessionController } from "./sessions";
import type {
  AppState,
  QueryMode,
  ResourceSelection,
  WorkspaceNode,
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

  renderResourceSelection();
}

function renderResourceSelection(): void {
  const { session, workspace } = state.selection;

  selectedSession.textContent = session
    ? `Selected: ${session}`
    : "No session selected";

  selectedWorkspace.textContent = workspace
    ? `Selected: ${workspace}`
    : "No workspace selected";

  updateNavigationSelection();
}

async function refreshNavigation(): Promise<void> {
  try {
    const tree = await loadNavigation();

    sessionList.innerHTML = renderNavigation(tree);

    const newWorkspaceButton =
      sessionList.querySelector<HTMLButtonElement>("#new-workspace");

    newWorkspaceButton?.addEventListener("click", async () => {
      const name = window.prompt("New workspace name:");

      if (!name?.trim()) {
        return;
      }

      try {
        const workspace = await createWorkspace(name.trim());

        await refreshNavigation();
        openWorkspace(workspace);
      } catch (error) {
        output.innerHTML = renderError(
          error instanceof Error
            ? error.message
            : "Unable to create workspace",
        );
        emptyState.hidden = true;
      }
    });

    sessionList
      .querySelectorAll<HTMLButtonElement>(".session-button")
      .forEach((button) => {
        button.addEventListener("click", async () => {
          const sessionName = button.dataset.session || "";

          if (!sessionName) {
            return;
          }

          await sessionController.open(sessionName, null);
        });
      });

    sessionList
      .querySelectorAll<HTMLButtonElement>(".workspace-button")
      .forEach((button) => {
        button.addEventListener("click", () => {
          const workspaceName = button.dataset.workspace || "";
          const workspace = tree.workspaces.find(
            (item) => item.name === workspaceName,
          );

          if (!workspace) {
            return;
          }

          openWorkspace(workspace);
        });
      });

    sessionList
      .querySelectorAll<HTMLButtonElement>(".workspace-session-button")
      .forEach((button) => {
        button.addEventListener("click", async () => {
          const sessionName = button.dataset.session || "";
          const workspaceName = button.dataset.workspace || "";

          if (!sessionName || !workspaceName) {
            return;
          }

          await sessionController.open(
            sessionName,
            workspaceName,
          );
        });
      });

    updateNavigationSelection();
  } catch (error) {
    sessionList.innerHTML = `
      <p class="navigation-empty">
        Unable to load navigation: ${escapeHtml(String(error))}
      </p>
    `;
  }
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

function openWorkspace(workspace: WorkspaceNode): void {
  setResourceSelection({
    session: null,
    workspace: workspace.name,
  });

  chatTurns.length = 0;
  loadedSessionHtml = "";

  output.innerHTML = renderWorkspaceOverview(workspace);
  emptyState.hidden = true;
}

function updateNavigationSelection(): void {
  const {
    session: selectedSessionName,
    workspace: selectedWorkspaceName,
  } = state.selection;

  sessionList
    .querySelectorAll<HTMLButtonElement>(".session-button")
    .forEach((button) => {
      button.classList.toggle(
        "selected",
        !selectedWorkspaceName &&
          button.dataset.session === selectedSessionName,
      );
    });

  sessionList
    .querySelectorAll<HTMLButtonElement>(".workspace-button")
    .forEach((button) => {
      button.classList.toggle(
        "selected",
        button.dataset.workspace === selectedWorkspaceName,
      );
    });

  sessionList
    .querySelectorAll<HTMLButtonElement>(".workspace-session-button")
    .forEach((button) => {
      button.classList.toggle(
        "selected",
        button.dataset.workspace === selectedWorkspaceName &&
          button.dataset.session === selectedSessionName,
      );
    });
}

renderResourceSelection();
void refreshNavigation();

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
  event.preventDefault();

  const session = state.selection.session;
  const workspace = state.selection.workspace;
  const query = queryInput.value.trim();
  const mode = state.mode;

  if (!query) {
    return;
  }

  emptyState.hidden = true;

  if (mode === "web_only") {
    output.innerHTML = renderLoading();
  } else {
    output.innerHTML = `
      ${loadedSessionHtml}
      ${renderChat(chatTurns)}
      ${renderLoading()}
    `;
  }

  try {
    const response = await runQuery(
      query,
      mode,
      session,
      workspace,
    );

    setResourceSelection({
      session: response.session,
      workspace: response.workspace,
    });

    if (response.mode === "web_only") {
      output.innerHTML = renderSearch(response);
      return;
    }

    chatTurns.push({ query, response });
    output.innerHTML = `
      ${loadedSessionHtml}
      ${renderChat(chatTurns)}
    `;

    await refreshNavigation();

    queryInput.value = "";
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: "smooth",
    });
  } catch (error) {
    output.innerHTML = renderError(
      error instanceof Error ? error.message : "Unknown error",
    );
  }
});