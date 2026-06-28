import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import PatientLookup from "./pages/PatientLookup.jsx";
import NewConsultation from "./pages/NewConsultation.jsx";
import KnowledgeSearch from "./pages/KnowledgeSearch.jsx";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/patients" element={<PatientLookup />} />
        <Route path="/consultation/new" element={<NewConsultation />} />
        <Route path="/knowledge" element={<KnowledgeSearch />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}
