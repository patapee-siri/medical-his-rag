import { useEffect, useState } from "react";
import { healthAPI } from "../services/api.js";

// Polls the backend /health endpoint so the user can see, at a glance,
// whether the API is reachable. Proves frontend<->backend integration.
export default function ApiStatus() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    let cancelled = false;

    async function ping() {
      try {
        const res = await healthAPI.check();
        if (!cancelled) setStatus(res.data?.status === "healthy" ? "online" : "degraded");
      } catch {
        if (!cancelled) setStatus("offline");
      }
    }

    ping();
    const id = setInterval(ping, 15000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  const config = {
    checking: { color: "bg-amber-400", label: "Checking API…" },
    online: { color: "bg-emerald-500", label: "API online" },
    degraded: { color: "bg-amber-500", label: "API degraded" },
    offline: { color: "bg-rose-500", label: "API offline" },
  }[status];

  return (
    <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5">
      <span className={`h-2.5 w-2.5 rounded-full ${config.color}`} />
      <span className="text-xs font-medium text-slate-600">{config.label}</span>
    </div>
  );
}
