import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { patientAPI, apiErrorMessage } from "../services/api.js";
import { Spinner, ErrorBanner } from "../components/ui.jsx";

const inputClass =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500";

const emptyPatient = {
  name: "",
  date_of_birth: "",
  gender: "male",
};

export default function PatientLookup() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [patients, setPatients] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [listError, setListError] = useState("");

  const [form, setForm] = useState(emptyPatient);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");

  async function loadPatients(searchTerm = "") {
    setLoading(true);
    setListError("");
    try {
      const { data } = await patientAPI.list({ search: searchTerm || undefined, limit: 20 });
      setPatients(data.results);
      setTotal(data.total);
    } catch (err) {
      setListError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPatients();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setCreating(true);
    setCreateError("");
    try {
      const { data } = await patientAPI.create(form);
      setForm(emptyPatient);
      await loadPatients(search);
      // Surface the new patient id at the top by searching for it.
      setSearch(data.name);
    } catch (err) {
      setCreateError(apiErrorMessage(err));
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[360px_1fr]">
      {/* Create patient */}
      <div>
        <h2 className="text-xl font-semibold text-slate-800">New Patient</h2>
        <p className="mb-4 text-sm text-slate-500">Register a patient record.</p>
        <form onSubmit={handleCreate} className="space-y-3">
          <input
            className={inputClass}
            placeholder="Full name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <label className="block text-sm text-slate-600">
            Date of birth
            <input
              type="date"
              className={inputClass}
              value={form.date_of_birth}
              onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
              required
            />
          </label>
          <select
            className={inputClass}
            value={form.gender}
            onChange={(e) => setForm({ ...form, gender: e.target.value })}
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
            <option value="unknown">Unknown</option>
          </select>
          <button
            type="submit"
            disabled={creating}
            className="w-full rounded-lg bg-teal-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-700 disabled:opacity-50"
          >
            {creating ? "Creating…" : "Create patient"}
          </button>
          <ErrorBanner message={createError} />
        </form>
      </div>

      {/* Patient list */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-800">
            Patients <span className="text-sm font-normal text-slate-400">({total})</span>
          </h2>
          {loading && <Spinner />}
        </div>

        <div className="mb-4 flex gap-2">
          <input
            className={inputClass}
            placeholder="Search by name or ID…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && loadPatients(search)}
          />
          <button
            onClick={() => loadPatients(search)}
            className="rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
          >
            Search
          </button>
        </div>

        <ErrorBanner message={listError} />

        <div className="divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white">
          {patients.length === 0 && !loading && (
            <p className="p-6 text-center text-sm text-slate-400">No patients found.</p>
          )}
          {patients.map((p) => (
            <div key={p.patient_id} className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium text-slate-800">{p.name}</p>
                <p className="font-mono text-xs text-slate-400">{p.patient_id}</p>
              </div>
              <button
                onClick={() => navigate(`/consultation/new?patient=${p.patient_id}`)}
                className="rounded-lg border border-teal-200 bg-teal-50 px-3 py-1.5 text-xs font-medium text-teal-700 hover:bg-teal-100"
              >
                New consultation →
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
