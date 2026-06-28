import { useState } from "react";

const emptyForm = {
  patient_id: "",
  chief_complaint: "",
  blood_pressure: "",
  heart_rate: "",
  temperature_celsius: "",
  respiratory_rate: "",
  oxygen_saturation: "",
  additional_symptoms: "",
};

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-600">
        {label}
      </span>
      {children}
    </label>
  );
}

const inputClass =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500";

// Phase 1: full input/output UI in place. The consultation API call is
// activated in Phase 2 — for now submit shows the assembled payload.
export default function NewConsultation() {
  const [form, setForm] = useState(emptyForm);
  const [preview, setPreview] = useState(null);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      patient_id: form.patient_id,
      chief_complaint: form.chief_complaint,
      vital_signs: {
        blood_pressure: form.blood_pressure,
        heart_rate: Number(form.heart_rate),
        temperature_celsius: Number(form.temperature_celsius),
        respiratory_rate: Number(form.respiratory_rate),
        oxygen_saturation: Number(form.oxygen_saturation),
      },
      additional_symptoms: form.additional_symptoms
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    };
    setPreview(payload);
  };

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div>
        <h2 className="text-xl font-semibold text-slate-800">New Consultation</h2>
        <p className="mb-6 text-sm text-slate-500">
          Enter the clinical presentation to request an AI-assisted assessment.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Patient ID">
            <input
              className={inputClass}
              value={form.patient_id}
              onChange={update("patient_id")}
              placeholder="P-20260628-001"
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

          <div className="grid grid-cols-2 gap-4">
            <Field label="Blood pressure">
              <input
                className={inputClass}
                value={form.blood_pressure}
                onChange={update("blood_pressure")}
                placeholder="140/90"
              />
            </Field>
            <Field label="Heart rate (bpm)">
              <input
                type="number"
                className={inputClass}
                value={form.heart_rate}
                onChange={update("heart_rate")}
                placeholder="95"
              />
            </Field>
            <Field label="Temperature (°C)">
              <input
                type="number"
                step="0.1"
                className={inputClass}
                value={form.temperature_celsius}
                onChange={update("temperature_celsius")}
                placeholder="38.5"
              />
            </Field>
            <Field label="Respiratory rate">
              <input
                type="number"
                className={inputClass}
                value={form.respiratory_rate}
                onChange={update("respiratory_rate")}
                placeholder="18"
              />
            </Field>
            <Field label="O₂ saturation (%)">
              <input
                type="number"
                className={inputClass}
                value={form.oxygen_saturation}
                onChange={update("oxygen_saturation")}
                placeholder="98"
              />
            </Field>
          </div>

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
            className="w-full rounded-lg bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-700"
          >
            Build request
          </button>
        </form>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-600">
          Request payload (FHIR-style)
        </h3>
        <pre className="min-h-[12rem] overflow-auto rounded-xl border border-slate-200 bg-slate-900 p-4 text-xs text-emerald-300">
{preview
  ? JSON.stringify(preview, null, 2)
  : "// Fill the form and click \"Build request\" to preview the\n// payload that will be POSTed to /consultations in Phase 2."}
        </pre>
      </div>
    </div>
  );
}
