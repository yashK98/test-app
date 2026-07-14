import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Dashboard from "./pages/Dashboard";
import AppDetail from "./pages/AppDetail";

export default function App() {
  return (
    <div className="min-h-screen bg-base-900 scanline">
      <NavBar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/app/:app" element={<AppDetail />} />
      </Routes>
    </div>
  );
}
