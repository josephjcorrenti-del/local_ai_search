import { loadNavigation } from "./api";
import { renderNavigation } from "./render-app";
import { escapeHtml } from "./render-utils";
import type {
  ResourceSelection,
  WorkspaceNode,
} from "./types";

export interface NavigationControllerOptions {
  sessionList: HTMLElement;
  selectedSession: HTMLElement;
  selectedWorkspace: HTMLElement;
  getResourceSelection: () => ResourceSelection;
  createWorkspace: () => Promise<void>;
  openSession: (
    sessionName: string,
    workspaceName: string | null,
  ) => Promise<void>;
  openWorkspace: (workspace: WorkspaceNode) => void;
}

export interface NavigationController {
  refresh(): Promise<void>;
  renderSelection(selection: ResourceSelection): void;
}

export function createNavigationController(
  options: NavigationControllerOptions,
): NavigationController {
  const {
    sessionList,
    selectedSession,
    selectedWorkspace,
    getResourceSelection,
    createWorkspace,
    openSession,
    openWorkspace,
  } = options;

  function updateSelection(selection: ResourceSelection): void {
    const {
      session: selectedSessionName,
      workspace: selectedWorkspaceName,
    } = selection;

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

  function renderSelection(selection: ResourceSelection): void {
    const { session, workspace } = selection;

    selectedSession.textContent = session
      ? `Selected: ${session}`
      : "No session selected";

    selectedWorkspace.textContent = workspace
      ? `Selected: ${workspace}`
      : "No workspace selected";

    updateSelection(selection);
  }

  async function refresh(): Promise<void> {
    try {
      const tree = await loadNavigation();

      sessionList.innerHTML = renderNavigation(tree);

      const newWorkspaceButton =
        sessionList.querySelector<HTMLButtonElement>("#new-workspace");

      newWorkspaceButton?.addEventListener("click", async () => {
        await createWorkspace();
      });

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

      updateSelection(getResourceSelection());
    } catch (error) {
      sessionList.innerHTML = `
        <p class="navigation-empty">
          Unable to load navigation: ${escapeHtml(String(error))}
        </p>
      `;
    }
  }

  return {
    refresh,
    renderSelection,
  };
}
