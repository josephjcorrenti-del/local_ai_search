import { loadNavigation, loadSession, runQuery } from "./api";
import { renderChat, type ChatTurn } from "./render-chat";
import { renderSearch } from "./render-search";
import type {
  NavigationTree,
  QueryMode,
  SessionNode,
  WorkspaceNode,
} from "./types";
import "./styles.css";

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
        <input id="session" name="session" type="hidden" />
        <input id="workspace" name="workspace" type="hidden" />
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
const sessionInput = document.querySelector<HTMLInputElement>("#session");
const workspaceInput =
  document.querySelector<HTMLInputElement>("#workspace");
const queryInput = document.querySelector<HTMLInputElement>("#query");
const modeSelect = document.querySelector<HTMLSelectElement>("#mode");
const output = document.querySelector<HTMLElement>("#output");
const emptyState = document.querySelector<HTMLElement>("#empty-state");

if (
  !form ||
  !sessionList ||
  !selectedSession ||
  !selectedWorkspace ||
  !workspaceInput ||
  !newSessionButton ||
  !sessionInput ||
  !queryInput ||
  !modeSelect ||
  !output ||
  !emptyState
) {
  throw new Error("missing UI elements");
}

const chatTurns: ChatTurn[] = [];
let loadedSessionHtml = "";

const initialParams = new URLSearchParams(window.location.search);
const initialQuery = initialParams.get("query");
const initialMode = initialParams.get("mode");

async function refreshNavigation(): Promise<void> {
  try {
    const tree = await loadNavigation();

    sessionList.innerHTML = renderNavigation(tree);

    sessionList
      .querySelectorAll<HTMLButtonElement>(".session-button")
      .forEach((button) => {
        button.addEventListener("click", async () => {
          const sessionName = button.dataset.session || "";

          if (!sessionName) {
            return;
          }

          await openSession(sessionName, null);
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

          await openSession(sessionName, workspaceName);
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

async function openSession(
  sessionName: string,
  workspaceName: string | null,
): Promise<void> {
  sessionInput.value = sessionName;
  selectedSession.textContent = `Selected: ${sessionName}`;

  if (workspaceName) {
    workspaceInput.value = workspaceName;
    selectedWorkspace.textContent = `Selected: ${workspaceName}`;
  } else {
    workspaceInput.value = "";
    selectedWorkspace.textContent = "No workspace selected";
  }

  output.innerHTML = "";
  emptyState.hidden = false;
  updateNavigationSelection();
  queryInput.value = "";

  try {
    const history = await loadSession(sessionName);

    chatTurns.length = 0;
    loadedSessionHtml = renderSessionHistory(history.messages);

    output.innerHTML = loadedSessionHtml;
    emptyState.hidden = true;
  } catch (error) {
    output.innerHTML = renderError(
      error instanceof Error
        ? error.message
        : "Unable to load session",
    );
  }
}

function openWorkspace(workspace: WorkspaceNode): void {
  workspaceInput.value = workspace.name;
  selectedWorkspace.textContent = `Selected: ${workspace.name}`;

  sessionInput.value = "";
  selectedSession.textContent = "No session selected";

  chatTurns.length = 0;
  loadedSessionHtml = "";

  output.innerHTML = renderWorkspaceOverview(workspace);
  emptyState.hidden = true;

  updateNavigationSelection();
}

function updateNavigationSelection(): void {
  const selectedSessionName = sessionInput.value;
  const selectedWorkspaceName = workspaceInput.value;

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

void refreshNavigation();

newSessionButton.addEventListener("click", () => {
  const name = window.prompt("New session name:");

  if (!name?.trim()) {
    return;
  }

  sessionInput.value = name.trim();
  workspaceInput.value = "";
  selectedWorkspace.textContent = "No workspace selected";
  selectedSession.textContent = `New session: ${name.trim()}`;
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

if (initialMode === "integrated" || initialMode === "ai_only" || initialMode === "web_only") {
  modeSelect.value = initialMode;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const session = sessionInput.value.trim();
  const workspace = workspaceInput.value.trim();
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

    if (!response.ok) {
      output.innerHTML = renderError(response.error?.message ?? "Unknown error");
      return;
    }

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
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  } catch (error) {
    output.innerHTML = renderError(
      error instanceof Error ? error.message : "Unknown error",
    );
  }
});

function renderNavigation(tree: NavigationTree): string {
  return `
    <section class="navigation-group">
      ${renderSessionNodes(tree.sessions)}
    </section>

    <section class="navigation-group workspace-navigation">
      <h2>Workspaces</h2>
      ${renderWorkspaceNodes(tree.workspaces)}
    </section>
  `;
}

function renderSessionNodes(sessions: SessionNode[]): string {
  if (sessions.length === 0) {
    return `
      <p class="navigation-empty">No sessions</p>
    `;
  }

  return sessions
    .map(
      (session) => `
        <button
          type="button"
          class="session-button"
          data-session="${escapeAttr(session.name)}"
        >
          ${escapeHtml(session.name)}
        </button>
      `,
    )
    .join("");
}

function renderWorkspaceNodes(workspaces: WorkspaceNode[]): string {
  if (workspaces.length === 0) {
    return `
      <p class="navigation-empty">No workspaces</p>
    `;
  }

  return workspaces
    .map(
      (workspace) => `
        <section class="workspace-node">
        <button
          type="button"
          class="workspace-button"
          data-workspace="${escapeAttr(workspace.name)}"
        >
          ${escapeHtml(workspace.name)}
        </button>

          <div class="workspace-children">
            ${workspace.sessions
              .map(
                (session) => `
                  <button
                    type="button"
                    class="workspace-session-button"
                    data-workspace="${escapeAttr(workspace.name)}"
                    data-session="${escapeAttr(session.name)}"
                  >
                    ${escapeHtml(session.name)}
                  </button>
                `,
              )
              .join("")}

            ${workspace.files
              .map(
                (file) => `
                  <div class="workspace-file">
                    ${escapeHtml(file.path)}
                  </div>
                `,
              )
              .join("")}
          </div>
        </section>
      `,
    )
    .join("");
}

function renderSessionHistory(
  messages: Array<{ role: string; content: string }>,
): string {
  if (messages.length === 0) {
    return `
      <section class="empty-state">
        <h2>Empty session</h2>
        <p>This session does not contain any messages yet.</p>
      </section>
    `;
  }

  return `
    <section class="chat">
      ${messages
        .map(
          (message) => `
            <article class="message ${
              message.role === "user" ? "user-message" : "assistant-message"
            }">
              <div class="avatar">${message.role === "user" ? "●" : "◎"}</div>
              <div class="message-body">
                <div class="message-label">
                  ${message.role === "user" ? "You" : "Local AI Search"}
                </div>
                <div class="answer">${formatSessionContent(message.content)}</div>
              </div>
            </article>
          `,
        )
        .join("")}
    </section>
  `;
}

function formatSessionContent(value: string): string {
  return escapeHtml(value)
    .split("\n\n")
    .map((paragraph) => `<p>${paragraph.replaceAll("\n", "<br>")}</p>`)
    .join("");
}

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

function renderWorkspaceOverview(workspace: WorkspaceNode): string {
  const sessions =
    workspace.sessions.length > 0
      ? `
        <section class="workspace-overview-section">
          <h2>Sessions</h2>
          <ul>
            ${workspace.sessions
              .map(
                (session) => `
                  <li>${escapeHtml(session.name)}</li>
                `,
              )
              .join("")}
          </ul>
        </section>
      `
      : "";

  const files =
    workspace.files.length > 0
      ? `
        <section class="workspace-overview-section">
          <h2>Files</h2>
          <ul class="workspace-file-list">
            ${workspace.files
              .map(
                (file) => `
                  <li>${escapeHtml(file.path)}</li>
                `,
              )
              .join("")}
          </ul>
        </section>
      `
      : "";

  const empty =
    workspace.sessions.length === 0 && workspace.files.length === 0
      ? `<p>This workspace does not contain any sessions or files.</p>`
      : "";

  return `
    <section class="workspace-overview">
      <h1>${escapeHtml(workspace.name)}</h1>
      ${sessions}
      ${files}
      ${empty}
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

function escapeAttr(value: string): string {
  return escapeHtml(value);
}