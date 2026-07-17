import type {
  NavigationTree,
  QueryMode,
  QueryResponse,
  SessionHistory,
  WorkspaceNode,
} from "./types";

type ApiErrorBody = {
  ok: false;
  error: {
    type: string;
    message: string;
  };
};

type WorkspaceCreateResponse = {
  ok: true;
  workspace: WorkspaceNode;
};

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as {
    ok?: unknown;
    error?: {
      type?: unknown;
      message?: unknown;
    };
  };

  return (
    candidate.ok === false &&
    typeof candidate.error === "object" &&
    candidate.error !== null &&
    typeof candidate.error.type === "string" &&
    typeof candidate.error.message === "string"
  );
}

async function requestJson<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(url, options);

  let data: unknown;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      response.ok
        ? "The server returned an invalid response."
        : `Request failed with status ${response.status}.`,
    );
  }

  if (!response.ok) {
    if (isApiErrorBody(data)) {
      throw new Error(data.error.message);
    }

    throw new Error(`Request failed with status ${response.status}.`);
  }

  return data as T;
}

export function loadNavigation(): Promise<NavigationTree> {
  return requestJson<NavigationTree>("/api/v1/navigation");
}

export function runQuery(
  query: string,
  mode: QueryMode,
  session?: string,
  workspace?: string,
): Promise<QueryResponse> {
  return requestJson<QueryResponse>("/api/v1/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      mode,
      session: session || null,
      workspace: workspace || null,
    }),
  });
}

export function loadSession(name: string): Promise<SessionHistory> {
  return requestJson<SessionHistory>(
    `/api/v1/sessions/${encodeURIComponent(name)}`,
  );
}

export async function createWorkspace(
  name: string,
): Promise<WorkspaceNode> {
  const response = await requestJson<WorkspaceCreateResponse>(
    "/api/v1/workspaces",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name }),
    },
  );

  return response.workspace;
}