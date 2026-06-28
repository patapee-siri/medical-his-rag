import { NavLink } from "react-router-dom";
import ApiStatus from "./ApiStatus.jsx";

const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/patients", label: "Patients" },
  { to: "/consultation/new", label: "New Consultation" },
];

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🏥</span>
            <div>
              <h1 className="text-lg font-semibold leading-tight">
                Medical HIS
              </h1>
              <p className="text-xs text-slate-500">
                Clinical Decision Support · RAG
              </p>
            </div>
          </div>
          <ApiStatus />
        </div>
        <nav className="mx-auto max-w-6xl px-6">
          <ul className="flex gap-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `inline-block border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
                      isActive
                        ? "border-teal-600 text-teal-700"
                        : "border-transparent text-slate-500 hover:text-slate-800"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>

      <footer className="mx-auto max-w-6xl px-6 py-6 text-center text-xs text-slate-400">
        AI-assisted decision support only — not a substitute for professional
        medical judgment.
      </footer>
    </div>
  );
}
