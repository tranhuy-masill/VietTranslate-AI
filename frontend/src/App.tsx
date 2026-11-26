
import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Navbar from "./components/Navbar";

import TranslatorPage from "./pages/TranslatorPage";

import DocumentPage from "./pages/DocumentPage";


function App() {

  return (

    <BrowserRouter>

      <div className="
        min-h-screen bg-slate-950 text-slate-100
      ">

        <Navbar />

        <Routes>

          <Route
            path="/"
            element={<TranslatorPage />}
          />

          <Route
            path="/documents"
            element={<DocumentPage />}
          />

        </Routes>

        <footer className="
          border-t border-slate-800
          text-center text-slate-500
          py-6 mt-10
        ">

          VietTranslate AI — MarianMT SwitchOut p = 0.02

        </footer>

      </div>

    </BrowserRouter>

  );
}

export default App;
