import {
  Bell,
  ChevronDown,
  Moon,
  PanelLeft,
  PanelRight,
  Search,
  Sun,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import { useTheme } from "../../context/ThemeContext";


export default function Navbar({
  onToggleSidebar,
  datasetOpen,
  onToggleDataset,
}) {
  const navigate = useNavigate();

  const {
    theme,
    setTheme,
  } = useTheme();


  const toggleTheme = () => {
    setTheme(
      theme === "dark"
        ? "light"
        : "dark"
    );
  };


  return (
    <header className="topbar">

      <div className="topbar-left">

        <button
          type="button"
          className="icon-button navbar-sidebar-toggle"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          <PanelLeft size={18} />
        </button>


        <div className="breadcrumb">

          <span className="muted">
            Workspace
          </span>

          <ChevronDown size={13} />

          <strong>
            Data analysis
          </strong>

        </div>

      </div>


      <div className="topbar-actions">

        <button
          type="button"
          className="search-pill"
          onClick={() =>
            navigate("/workspace")
          }
        >
          <Search size={15} />

          <span>
            Ask DataNova
          </span>

          <kbd>
            ⌘ K
          </kbd>
        </button>


        <button
          type="button"
          className="icon-button"
          onClick={toggleTheme}
          aria-label="Toggle theme"
          title="Toggle theme"
        >
          {theme === "dark" ? (
            <Moon size={18} />
          ) : (
            <Sun size={18} />
          )}
        </button>


        <button
          type="button"
          className="icon-button"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>


        <button
          type="button"
          className="dataset-toggle"
          onClick={onToggleDataset}
        >
          {datasetOpen ? (
            <PanelRight size={16} />
          ) : (
            <PanelLeft size={16} />
          )}

          <span>
            {datasetOpen
              ? "Hide data"
              : "Show data"}
          </span>
        </button>


        <button
          type="button"
          className="avatar-button"
          onClick={() =>
            navigate("/settings")
          }
        >
          G
        </button>

      </div>

    </header>
  );
}