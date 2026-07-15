import {
  Plus,
  Database,
  FileBarChart2,
  CheckSquare,
  Settings,
  MessageSquare,
} from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-72 bg-slate-900 text-white flex flex-col">

      {/* Logo */}
      <div className="border-b border-slate-700 p-6">
        <h1 className="text-2xl font-bold text-blue-400">
          DataNova AI
        </h1>
      </div>

      {/* New Chat */}
      <div className="p-4">
        <button className="flex w-full items-center gap-3 rounded-xl bg-blue-600 px-4 py-3 hover:bg-blue-700 transition">
          <Plus size={20} />
          New Chat
        </button>
      </div>

      {/* Recent Chats */}
      <div className="flex-1 px-4">
        <p className="mb-3 text-xs uppercase text-slate-400">
          Recent Chats
        </p>

        <div className="space-y-2">

          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800">
            <MessageSquare size={18} />
            Titanic Analysis
          </button>

          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800">
            <MessageSquare size={18} />
            Customer Churn
          </button>

          <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800">
            <MessageSquare size={18} />
            Sales Dashboard
          </button>

        </div>
      </div>

      {/* Bottom Menu */}
      <div className="border-t border-slate-700 p-4 space-y-2">

        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800">
          <Database size={18} />
          Workspace
        </button>

        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800">
          <FileBarChart2 size={18} />
          Reports
        </button>

        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800">
          <CheckSquare size={18} />
          Tasks
        </button>

        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800">
          <Settings size={18} />
          Settings
        </button>

      </div>
    </aside>
  );
}