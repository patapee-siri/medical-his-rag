import { useState } from "react";

// Phase 1 placeholder: UI is in place; the patient API is wired in Phase 2.
export default function PatientLookup() {
  const [query, setQuery] = useState("");

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-800">Patients</h2>
        <p className="text-sm text-slate-500">
          Search and manage patient records.
        </p>
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name or patient ID…"
          className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
        />
        <button
          type="button"
          disabled
          className="cursor-not-allowed rounded-lg bg-slate-200 px-5 py-2.5 text-sm font-medium text-slate-400"
        >
          Search
        </button>
      </div>

      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
        <p className="text-sm text-slate-400">
          Patient list will appear here once the API is connected (Phase 2).
        </p>
      </div>
    </div>
  );
}
