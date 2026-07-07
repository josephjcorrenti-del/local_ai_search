export type QueryMode = "integrated" | "ai_only" | "web_only";

export type EvidenceResult = {
  rank: number;
  title: string;
  snippet: string;
  url?: string;
  source_type?: string;
  provider?: string;
  path?: string;
  workspace?: string;
  session?: string;
};

export type Evidence = {
  retrieval_version?: number;
  artifact_type?: string;
  provider?: string;
  query?: string;
  fetched_at?: string;
  session?: string;
  workspace?: string;
  root?: string;
  results?: EvidenceResult[];
};

export type EvidenceAccounting = {
  available_count: number;
  evidence_count: number;
  displayed_count: number;
};

export type IntentInfo = {
  route: string;
  reason: string;
};

export type RetrievalInfo = {
  status: string;
  reason: string | null;
};

export type QueryResponse = {
  ok: boolean;
  mode: QueryMode;
  query: string;
  answer: string | null;
  evidence: Evidence | null;
  accounting: EvidenceAccounting | null;
  intent: IntentInfo | null;
  retrieval: RetrievalInfo | null;
  elapsed_ms: number;
  error: { type: string; message: string } | null;
};
