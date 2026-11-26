
import {
  Languages,
  FileText,
  Cpu
} from "lucide-react";

import { NavLink } from "react-router-dom";

export default function Navbar() {

  const navClass = ({ isActive }: { isActive: boolean }) =>

    `flex items-center gap-2 px-4 py-3 rounded-lg
    transition text-sm font-medium
    ${isActive
      ? "bg-blue-600 text-white"
      : "text-slate-400 hover:bg-slate-800 hover:text-white"
    }`;

  return (

    <header className="
      bg-slate-950 border-b border-slate-800
    ">

      <div className="
        max-w-7xl mx-auto px-6 py-5
      ">

        <div className="
          flex items-center justify-between
          flex-wrap gap-4
        ">

          <div className="flex items-center gap-3">

            <div className="bg-blue-600 p-3 rounded-xl">
              <Languages size={28} />
            </div>

            <div>

              <h1 className="text-xl font-bold">
                VietTranslate AI
              </h1>

              <p className="text-sm text-slate-400">
                Neural Machine Translation Platform
              </p>

            </div>

          </div>

          <div className="
            flex items-center gap-2
            text-blue-400
          ">

            <Cpu size={18} />

            MarianMT

          </div>

        </div>

        <nav className="flex flex-wrap gap-3 mt-6">

          <NavLink
            to="/"
            end
            className={navClass}
          >

            <Languages size={18} />

            Text Translation

          </NavLink>

          <NavLink
            to="/documents"
            className={navClass}
          >

            <FileText size={18} />

            Document Translation

          </NavLink>

        </nav>

      </div>

    </header>

  );
}
