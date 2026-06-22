import type { QueryMode, QueryResponse } from "./types";

export async function runQuery(
  query: string,
  mode: QueryMode,
): Promise<QueryResponse> {
  const response = await fetch("/api/v1/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      mode,
      limit: 5,
      max_chars: 4000,
    }),
  });

  return response.json();
}
