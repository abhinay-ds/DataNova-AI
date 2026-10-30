import {
  Bell,
  ChevronDown,
  ChevronRight,
  LayoutDashboard,
  Moon,
  PanelBottom,
  PanelLeft,
  PanelRight,
  RotateCcw,
  Search,
  Sun,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import { useTheme } from "../../context/ThemeContext";
import { useProject } from "../../context/ProjectContext";


export default function Navbar({
  sidebarCollapsed = false,
  onToggleSidebar,
  datasetOpen,
  onToggleDataset,
  panelLayout = "side",
  onTogglePanelLayout,
  onResetLayout,
}) {
  const navigate = useNavigate();

  const {
    theme,
    setTheme,
  } = useTheme();
  const { activeProject } = useProject();


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
          className={`icon-button navbar-sidebar-toggle ${
            !sidebarCollapsed ? "is-pinned" : ""
          }`}
          onClick={onToggleSidebar}
          aria-label={sidebarCollapsed ? "Pin sidebar open" : "Collapse sidebar"}
          title={sidebarCollapsed ? "Pin sidebar open" : "Collapse sidebar"}
        >
          <PanelLeft size={18} />
        </button>


        <div className="breadcrumb">

          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            title="Return to Dashboard"
            style={{
              background: "transparent",
              border: "none",
              padding: 0,
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
              color: "var(--dn-text-muted, #64748b)",
              fontSize: "13px",
              fontWeight: "500",
            }}
          >
            <LayoutDashboard size={14} />
            <span>Dashboard</span>
          </button>

          <ChevronRight size={13} style={{ color: "var(--dn-text-muted, #94a3b8)" }} />

          <strong>
            {activeProject?.name || "Data analysis"}
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

        {datasetOpen && onTogglePanelLayout && (
          <button
            type="button"
            className="icon-button"
            onClick={onTogglePanelLayout}
            title={
              panelLayout === "bottom"
                ? "Dock dataset panel to right"
                : "Dock dataset panel to bottom"
            }
            aria-label="Toggle panel docking position"
          >
            {panelLayout === "bottom" ? (
              <PanelRight size={17} />
            ) : (
              <PanelBottom size={17} />
            )}
          </button>
        )}

        {onResetLayout && (
          <button
            type="button"
            className="icon-button"
            onClick={onResetLayout}
            title="Reset workspace panel sizes to default"
            aria-label="Reset workspace layout"
          >
            <RotateCcw size={16} />
          </button>
        )}

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