import { useEffect, useState } from "react";
import { knowledgeAPI, apiErrorMessage } from "../services/api.js";
import { Spinner, ErrorBanner, Badge } from "../components/ui.jsx";

const inputClass =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500";

export default function KnowledgeSearch() {
  const [query, setQuery] = useState("");
  const [rerank, setRerank] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    knowledgeAPI
      .stats()
      .then(({ data }) => setStats(data))
      .catch(() => {});
  }, []);

  async function handleSearch(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const { data } = await knowledgeAPI.search({ query, top_k: 5, rerank });
      setResults(data);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-800">Knowledge Base</h2>
          <p className="text-sm text-slate-500">
            Semantic search over indexed medical literature (PubMed).
          </p>
        </div>
        {stats && (
          <Badge tone="teal">
            {stats.total_documents} docs · {stats.embedding_model}
          </Badge>
        )}
      </div>

      <form onSubmit={handleSearch} className="space-y-3">
        <div className="flex gap-2">
          <input
            className={inputClass}
            placeholder="e.g. fever, headache, neck stiffness…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-teal-600 px-5 py-2 text-sm font-semibold text-white hover:bg-teal-700 disabled:opacity-50"
          >
            Search
          </button>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={rerank}
            onChange={(e) => setRerank(e.target.checked)}
          />
          Two-stage retrieval (BM25 re-ranking)
        </label>
      </form>

      {loading && <Spinner label="Searching…" />}
      <ErrorBanner message={error} />

      {results && (
        <div className="space-y-2">
          <p className="text-sm text-slate-500">
            {results.total_returned} results {results.reranked && "· re-ranked"}
            {results.augmented && " · 🔄 augmented with live sources"}
          </p>
          {results.documents.map((d, i) => (
            <div key={d.doc_id} className="rounded-xl border border-slate-200 bg-white p-4 text-sm">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span className="mr-1 font-semibold text-teal-700">[{i + 1}]</span>
                  {d.url ? (
                    <a href={d.url} target="_blank" rel="noopener noreferrer" className="font-medium text-slate-800 underline decoration-slate-300 hover:decoration-teal-500">
                      {d.title}
                    </a>
                  ) : (
                    <span className="font-medium text-slate-800">{d.title}</span>
                  )}
                  <p className="mt-1 text-xs text-slate-500">{d.excerpt}</p>
                  <div className="mt-1.5 flex flex-wrap gap-2">
                    <Badge tone="slate">{d.source_type.replace(/_/g, " ")}</Badge>
                    {d.year && <Badge tone="slate">{d.year}</Badge>}
                    {d.provider && d.provider !== "curated" && (
                      <Badge tone="teal">{d.provider}</Badge>
                    )}
                    {d.credibility && (
                      <Badge tone={d.credibility === "peer_reviewed" ? "teal" : "amber"}>
                        {d.credibility.replace(/_/g, " ")}
                      </Badge>
                    )}
                  </div>
                </div>
                <span className="shrink-0 text-xs font-medium text-slate-400">
                  {Math.round(d.relevance_score * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
