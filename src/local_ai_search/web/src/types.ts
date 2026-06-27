export type QueryMode = "integrated" | "ai_only" | "web_only";

export type EvidenceResult = {
  rank: number;
  title: string;
  url: string;
  snippet: string;
};

export type Evidence = {
  provider?: string;
  query?: string;
  results?: EvidenceResult[];
};

export type EvidenceAccounting = {
  available_count: number;
  evidence_count: number;
  displayed_count: number;
};

export type QueryResponse = {
  ok: boolean;
  mode: QueryMode;
  query: string;
  answer: string | null;
  evidence: Evidence | null;
  accounting: EvidenceAccounting | null;
  elapsed_ms: number;
  error: { type: string; message: string } | null;
};

