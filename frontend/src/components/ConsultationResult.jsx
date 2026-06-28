import { ConfidenceBar, Badge } from "./ui.jsx";

export default function ConsultationResult({ result }) {
  if (!result) return null;

  const isMock = result.model_used === "mock";

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="teal">{result.consultation_id}</Badge>
        <Badge tone={isMock ? "amber" : "slate"}>
          {result.model_used || "unknown"}
        </Badge>
        <Badge tone="slate">{result.processing_time_ms} ms</Badge>
      </div>

      {/* Confidence */}
      <div>
        <p className="mb-1 text-sm font-medium text-slate-600">Confidence</p>
        <ConfidenceBar value={result.confidence} />
      </div>

      {/* Assessment */}
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">AI Assessment</h3>
        <div className="whitespace-pre-wrap rounded-xl border border-slate-200 bg-white p-4 text-sm leading-relaxed text-slate-700">
          {result.ai_assessment}
        </div>
      </div>

      {/* Sources */}
      {result.sources?.length > 0 && (
        <div>
          <h3 className="mb-2 text-sm font-semibold text-slate-700">
            Evidence ({result.sources.length})
          </h3>
          <ol className="space-y-2">
            {result.sources.map((s, i) => (
              <li
                key={s.doc_id}
                className="rounded-xl border border-slate-200 bg-white p-3 text-sm"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <span className="mr-1 font-semibold text-teal-700">[{i + 1}]</span>
                    {s.url ? (
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-slate-800 underline decoration-slate-300 hover:decoration-teal-500"
                      >
                        {s.title}
                      </a>
                    ) : (
                      <span className="font-medium text-slate-800">{s.title}</span>
                    )}
                    <p className="mt-1 text-xs text-slate-500">{s.excerpt}</p>
                  </div>
                  <span className="shrink-0 text-xs font-medium text-slate-400">
                    {Math.round(s.relevance_score * 100)}%
                  </span>
                </div>
                <div className="mt-1.5 flex gap-2">
                  <Badge tone="slate">{s.source_type.replace(/_/g, " ")}</Badge>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Uncertainty */}
      {result.uncertainty_notes?.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
          <h3 className="mb-1 text-sm font-semibold text-amber-800">
            Uncertainty &amp; limitations
          </h3>
          <ul className="list-inside list-disc text-sm text-amber-700">
            {result.uncertainty_notes.map((n, i) => (
              <li key={i}>{n}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-xs italic text-slate-400">{result.disclaimer}</p>
    </div>
  );
}
