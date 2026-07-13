import type {
  NavigationTree,
  QueryMode,
  QueryResponse,
  SessionHistory,
} from "./types";

export async function loadNavigation(): Promise<NavigationTree> {
  const response = await fetch("/api/v1/navigation");
  return response.json();
}

export async function runQuery(
  query: string,
  mode: QueryMode,
  session?: string,
  workspace?: string,
): Promise<QueryResponse> {
  const response = await fetch("/api/v1/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      mode,
      session: session || null,
      workspace: workspace || null,
      limit: 5,
      max_chars: 4000,
    }),
  });

  return response.json();
}

export async function loadSession(name: string): Promise<SessionHistory> {
  const response = await fetch(`/api/v1/sessions/${encodeURIComponent(name)}`);

  if (!response.ok) {
    throw new Error(`session request failed: ${response.status}`);
  }

  return response.json();
}