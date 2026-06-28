import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { consultationAPI, apiErrorMessage } from "../services/api.js";
import { Spinner, ErrorBanner } from "../components/ui.jsx";
import ConsultationResult from "../components/ConsultationResult.jsx";

const inputClass =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500";

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-600">{label}</span>
      {children}
    </label>
  );
}

export default function NewConsultation() {
  const [searchParams] = useSearchParams();
  const [form, setForm] = useState({
    patient_id: searchParams.get("patient") || "",
    chief_complaint: "",
    blood_pressure: "",
    heart_rate: "",
    temperature_celsius: "",
    respiratory_rate: "",
    oxygen_saturation: "",
    additional_symptoms: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  function buildPayload() {
    const payload = {
      patient_id: form.patient_id.trim(),
      chief_complaint: form.chief_complaint.trim(),
      additional_symptoms: form.additional_symptoms
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    };
    // Only include vital_signs if all fields are filled (schema requires all).
    const vitals = [
      form.blood_pressure,
      form.heart_rate,
      form.temperature_celsius,
      form.respiratory_rate,
      form.oxygen_saturation,
    ];
    if (vitals.every((v) => String(v).trim() !== "")) {
      payload.vital_signs = {
        blood_pressure: form.blood_pressure,
        heart_rate: Number(form.heart_rate),
        temperature_celsius: Number(form.temperature_celsius),
        respiratory_rate: Number(form.respiratory_rate),
        oxygen_saturation: Number(form.oxygen_saturation),
      };
    }
    return payload;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const { data } = await consultationAPI.create(buildPayload());
      setResult(data);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      {/* Form */}
      <div>
        <h2 className="text-xl font-semibold text-slate-800">New Consultation</h2>
        <p className="mb-6 text-sm text-slate-500">
          Enter the clinical presentation to request an AI-assisted, evidence-grounded
          assessment.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Patient ID">
            <input
              className={inputClass}
              value={form.patient_id}
              onChange={update("patient_id")}
              placeholder="P-20260628-XXXXXX"
              required
            />
          </Field>

          <Field label="Chief complaint">
            <textarea
              className={inputClass}
              rows={3}
              value={form.chief_complaint}
              onChange={update("chief_complaint")}
              placeholder="Persistent headache and fever for 3 days…"
              required
            />
          </Field>

          <fieldset className="rounded-lg border border-slate-200 p-3">
            <legend className="px-1 text-xs font-medium text-slate-500">
              Vital signs (optional — fill all or none)
            </legend>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Blood pressure">
                <input className={inputClass} value={form.blood_pressure} onChange={update("blood_pressure")} placeholder="140/90" />
              </Field>
              <Field label="Heart rate (bpm)">
                <input type="number" className={inputClass} value={form.heart_rate} onChange={update("heart_rate")} placeholder="95" />
              </Field>
              <Field label="Temperature (°C)">
                <input type="number" step="0.1" className={inputClass} value={form.temperature_celsius} onChange={update("temperature_celsius")} placeholder="38.5" />
              </Field>
              <Field label="Respiratory rate">
                <input type="number" className={inputClass} value={form.respiratory_rate} onChange={update("respiratory_rate")} placeholder="18" />
              </Field>
              <Field label="O₂ saturation (%)">
                <input type="number" className={inputClass} value={form.oxygen_saturation} onChange={update("oxygen_saturation")} placeholder="98" />
              </Field>
            </div>
          </fieldset>

          <Field label="Additional symptoms (comma-separated)">
            <input
              className={inputClass}
              value={form.additional_symptoms}
              onChange={update("additional_symptoms")}
              placeholder="nausea, photophobia, neck stiffness"
            />
          </Field>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-700 disabled:opacity-50"
          >
            {loading ? "Analyzing…" : "Request assessment"}
          </button>
          <ErrorBanner message={error} />
        </form>
      </div>

      {/* Result */}
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-600">Assessment</h3>
        {loading && (
          <div className="rounded-xl border border-slate-200 bg-white p-10 text-center">
            <Spinner label="Retrieving evidence and generating assessment…" />
          </div>
        )}
        {!loading && !result && (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-400">
            Submit the form to see the AI-assisted assessment, sources, and confidence.
          </div>
        )}
        {!loading && result && <ConsultationResult result={result} />}
      </div>
    </div>
  );
}
