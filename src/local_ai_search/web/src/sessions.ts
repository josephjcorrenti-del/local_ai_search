import { loadSession } from "./api";
import { renderError, renderSessionHistory } from "./render-app";
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
    open,
  };
}
