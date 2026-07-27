import { escapeAttr, escapeHtml, formatText } from "./render-utils";
import type {
  NavigationTree,
  SessionMessage,
  SessionNode,
  WorkspaceNode,
} from "./types";

export function renderNavigation(tree: NavigationTree): string {
  return `
    <section class="navigation-group workspace-navigation">
      <section class="navigation-heading">
        <h2>Workspaces</h2>
        <button
          id="new-workspace"
          type="button"
          class="new-session-button"
        >
          +
        </button>
      </section>
      ${renderWorkspaceNodes(tree.workspaces)}
    </section>

    <section class="navigation-group session-navigation">
      <h2>Sessions</h2>
      ${renderSessionNodes(tree.sessions)}
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

export function renderSessionHistory(
  messages: SessionMessage[],
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
                <div class="answer">${formatText(message.content)}</div>
              </div>
            </article>
          `,
        )
        .join("")}
    </section>
  `;
}

export function renderLoading(): string {
  return `
    <section class="loading">
      <div class="spinner"></div>
      <p>Working...</p>
    </section>
  `;
}

export function renderError(message: string): string {
  return `
    <section class="error-card">
      <h2>Request failed</h2>
      <p>${escapeHtml(message)}</p>
    </section>
  `;
}

export function renderWorkspaceOverview(
  workspace: WorkspaceNode,
): string {
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
