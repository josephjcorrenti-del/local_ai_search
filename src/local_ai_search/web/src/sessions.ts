import { loadSession } from "./api";
import {
  renderError,
  renderSessionHistory,
} from "./render-app";
import type { ChatTurn } from "./render-chat";
import type { ResourceSelection } from "./types";

export interface SessionControllerOptions {
  output: HTMLElement;
  emptyState: HTMLElement;
  queryInput: HTMLInputElement;
  chatTurns: ChatTurn[];
  setResourceSelection: (selection: ResourceSelection) => void;
  setLoadedSessionHtml: (html: string) => void;
}

export interface SessionController {
  startNew(): void;
  open(
    sessionName: string,
    workspaceName: string | null,
  ): Promise<void>;
}

export function createSessionController(
  options: SessionControllerOptions,
): SessionController {
  const {
    output,
    emptyState,
    queryInput,
    chatTurns,
    setResourceSelection,
    setLoadedSessionHtml,
  } = options;

  function startNew(): void {
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
    setLoadedSessionHtml("");
    output.innerHTML = "";
    emptyState.hidden = false;
    queryInput.value = "";
    queryInput.focus();
  }

  async function open(
    sessionName: string,
    workspaceName: string | null,
  ): Promise<void> {
    setResourceSelection({
      session: sessionName,
      workspace: workspaceName,
    });

    output.innerHTML = "";
    emptyState.hidden = false;
    queryInput.value = "";

    try {
      const history = await loadSession(sessionName);

      chatTurns.length = 0;

      const loadedSessionHtml = renderSessionHistory(history.messages);

      setLoadedSessionHtml(loadedSessionHtml);
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

  return {
    startNew,
    open,
  };
}