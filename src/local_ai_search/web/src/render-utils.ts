import type { EvidenceResult } from "./types";

export function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function escapeAttr(value: string): string {
  return escapeHtml(value);
}

export function formatText(value: string): string {
  return escapeHtml(value)
    .split("\n\n")
    .map((paragraph) => `<p>${paragraph.replaceAll("\n", "<br>")}</p>`)
    .join("");
}

export function formatTextWithEvidenceReferences(
  value: string,
  evidence: EvidenceResult[],
): string {
  const sourcesByRank = new Map(
    evidence.map((source) => [source.rank, source]),
  );

  const formattedText = escapeHtml(value)
    .split("\n\n")
    .map(
      (paragraph) =>
        `<p>${paragraph.replaceAll("\n", "<br>")}</p>`,
    )
    .join("");

  return formattedText.replace(
    /\[(\d+)\]/g,
    (reference, rankText: string) => {
      const rank = Number(rankText);
      const source = sourcesByRank.get(rank);

      if (!source?.url) {
        return reference;
      }

      return `<a class="evidence-reference" href="${escapeAttr(source.url)}" target="_blank" rel="noopener noreferrer" aria-label="Open evidence ${rank}">${reference}</a>`;
    },
  );
}