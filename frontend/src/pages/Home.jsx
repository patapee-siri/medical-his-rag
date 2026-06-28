import { Link } from "react-router-dom";

const features = [
  {
    icon: "🩺",
    title: "AI Consultation",
    desc: "Enter symptoms & vitals, get an evidence-grounded assessment with citations.",
    to: "/consultation/new",
    cta: "Start consultation",
  },
  {
    icon: "👤",
    title: "Patient Records",
    desc: "Create and look up patient records with medical history and allergies.",
    to: "/patients",
    cta: "Manage patients",
  },
  {
    icon: "📚",
    title: "Knowledge Base",
    desc: "Medical literature indexed for semantic search with two-stage retrieval.",
    to: "/consultation/new",
    cta: "Query knowledge",
  },
];

export default function Home() {
  return (
    <div className="space-y-8">
      <section className="rounded-2xl bg-gradient-to-br from-teal-600 to-emerald-600 px-8 py-10 text-white">
        <h2 className="text-2xl font-semibold">
          Healthcare Information System with RAG
        </h2>
        <p className="mt-2 max-w-2xl text-teal-50">
          A production-grade clinical decision support system. Backend powered by
          FastAPI, vector search via Qdrant, and LLM inference grounded in
          medical literature — every answer comes with sources and a confidence
          score.
        </p>
        <Link
          to="/consultation/new"
          className="mt-6 inline-block rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-teal-700 transition hover:bg-teal-50"
        >
          New consultation →
        </Link>
      </section>

      <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <div
            key={f.title}
            className="flex flex-col rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <span className="text-3xl">{f.icon}</span>
            <h3 className="mt-3 font-semibold text-slate-800">{f.title}</h3>
            <p className="mt-1 flex-1 text-sm text-slate-500">{f.desc}</p>
            <Link
              to={f.to}
              className="mt-4 text-sm font-medium text-teal-600 hover:text-teal-700"
            >
              {f.cta} →
            </Link>
          </div>
        ))}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="font-semibold text-slate-800">Project status</h3>
        <p className="mt-1 text-sm text-slate-500">
          Phase 1 (Foundation) — scaffold complete. AI consultation & patient
          endpoints are wired in Phase 2.
        </p>
      </section>
    </div>
  );
}
