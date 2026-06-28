import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="py-20 text-center">
      <p className="text-5xl">🔍</p>
      <h2 className="mt-4 text-xl font-semibold text-slate-800">
        Page not found
      </h2>
      <Link
        to="/"
        className="mt-4 inline-block text-sm font-medium text-teal-600 hover:text-teal-700"
      >
        ← Back to dashboard
      </Link>
    </div>
  );
}
