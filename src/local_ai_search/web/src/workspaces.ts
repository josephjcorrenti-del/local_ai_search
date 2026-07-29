import { createWorkspace } from "./api";
import {
  renderError,
  renderWorkspaceOverview,
} from "./render-app";
import type { ChatTurn } from "./render-chat";
import type {
  ResourceSelection,
  WorkspaceNode,
} from "./types";

export interface WorkspaceControllerOptions {
  output: HTMLElement;
  emptyState: HTMLElement;
  chatTurns: ChatTurn[];
  setResourceSelection: (selection: ResourceSelection) => void;
  setLoadedSessionHtml: (html: string) => void;
  refreshNavigation: () => Promise<void>;
}

export interface WorkspaceController {
  create(): Promise<void>;
  open(workspace: WorkspaceNode): void;
}

export function createWorkspaceController(
  options: WorkspaceControllerOptions,
): WorkspaceController {
  const {
    output,
    emptyState,
    chatTurns,
    setResourceSelection,
    setLoadedSessionHtml,
    refreshNavigation,
  } = options;

  function open(workspace: WorkspaceNode): void {
    setResourceSelection({
      session: null,
      workspace: workspace.name,
    });

    chatTurns.length = 0;
    setLoadedSessionHtml("");

    output.innerHTML = renderWorkspaceOverview(workspace);
    emptyState.hidden = true;
  }

  async function create(): Promise<void> {
    const name = window.prompt("New workspace name:");
    const workspaceName = name?.trim();

    if (!workspaceName) {
      return;
    }

    try {
      const workspace = await createWorkspace(workspaceName);

      await refreshNavigation();
      open(workspace);
    } catch (error) {
      output.innerHTML = renderError(
        error instanceof Error
          ? error.message
          : "Unable to create workspace",
      );
      emptyState.hidden = true;
    }
  }

  return {
    create,
    open,
  };
}
