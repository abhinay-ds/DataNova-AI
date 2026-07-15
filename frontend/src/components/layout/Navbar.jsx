import {
  Bell,
  Moon,
  ChevronDown,
  CircleUserRound,
} from "lucide-react";

export default function Navbar() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between">

      {/* Workspace */}
      <div className="flex items-center gap-2">

        <h2 className="font-semibold text-lg">
          Workspace
        </h2>

        <ChevronDown size={18} />

      </div>

      {/* Right Side */}

      <div className="flex items-center gap-6">

        <button className="hover:text-blue-600 transition">
          <Moon size={20} />
        </button>

        <button className="hover:text-blue-600 transition">
          <Bell size={20} />
        </button>

        <div className="flex items-center gap-2">

          <CircleUserRound size={30} />

          <span className="font-medium">
            Guest
          </span>

        </div>

      </div>

    </header>
  );
}