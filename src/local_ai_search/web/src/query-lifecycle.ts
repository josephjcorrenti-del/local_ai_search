import { runQuery } from "./api";
import {
  renderError,
  renderLoading,
} from "./render-app";
import {
  renderChat,
  type ChatTurn,
} from "./render-chat";
import { renderSearch } from "./render-search";
import type {
  AppState,
  ResourceSelection,
} from "./types";

export interface QueryControllerOptions {
  output: HTMLElement;
  emptyState: HTMLElement;
  queryInput: HTMLInputElement;
  chatTurns: ChatTurn[];
  state: AppState;
  setResourceSelection: (selection: ResourceSelection) => void;
  getLoadedSessionHtml: () => string;
  refreshNavigation: () => Promise<void>;
}

export interface QueryController {
  submit(event: SubmitEvent): Promise<void>;
}

export function createQueryController(
  options: QueryControllerOptions,
): QueryController {
  const {
    output,
    emptyState,
    queryInput,
    chatTurns,
    state,
    setResourceSelection,
    getLoadedSessionHtml,
    refreshNavigation,
  } = options;

  async function submit(event: SubmitEvent): Promise<void> {
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
        ${getLoadedSessionHtml()}
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
        ${getLoadedSessionHtml()}
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
  }

  return {
    submit,
  };
}
