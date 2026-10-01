import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import ChatArea from "./ChatArea";
import ChatInput from "./ChatInput";
import DatasetPanel from "./DatasetPanel";

export default function MainLayout() {
  const navigate = useNavigate();

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [datasetOpen, setDatasetOpen] = useState(true);

  const [sidebarWidth, setSidebarWidth] = useState(250);
  const [datasetWidth, setDatasetWidth] = useState(360);

  const [resizing, setResizing] = useState(null);

  const resizeState = useRef(null);

  const toggleSidebar = () => {
    setSidebarCollapsed((prev) => !prev);
  };

  const toggleDataset = () => {
    setDatasetOpen((prev) => !prev);
  };

  const goTo = (path) => {
    navigate(path);
  };

  /*
   * =========================================================
   * START RESIZE
   * =========================================================
   */

  const startResize = (type, event) => {
    event.preventDefault();
    event.stopPropagation();

    const startX = event.clientX;

    resizeState.current = {
      type,
      startX,
      startSidebarWidth: sidebarWidth,
      startDatasetWidth: datasetWidth,
    };

    setResizing(type);

    document.body.style.userSelect = "none";
    document.body.style.cursor = "col-resize";

    const handleMove = (moveEvent) => {
      const state = resizeState.current;

      if (!state) return;

      const delta = moveEvent.clientX - state.startX;

      if (state.type === "sidebar") {
        const nextWidth = Math.min(
          Math.max(state.startSidebarWidth + delta, 190),
          380
        );

        setSidebarWidth(nextWidth);
      }

      if (state.type === "dataset") {
        const nextWidth = Math.min(
          Math.max(state.startDatasetWidth - delta, 280),
          600
        );

        setDatasetWidth(nextWidth);
      }
    };

    const handleUp = () => {
      resizeState.current = null;
      setResizing(null);

      document.body.style.userSelect = "";
      document.body.style.cursor = "";

      window.removeEventListener("pointermove", handleMove);
      window.removeEventListener("pointerup", handleUp);
    };

    window.addEventListener("pointermove", handleMove);
    window.addEventListener("pointerup", handleUp);
  };

  /*
   * =========================================================
   * CLEANUP
   * =========================================================
   */

  useEffect(() => {
    return () => {
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    };
  }, []);

  /*
   * =========================================================
   * LAYOUT
   * =========================================================
   */

  const actualSidebarWidth = sidebarCollapsed ? 72 : sidebarWidth;

  return (
    <div
      className={`app-shell ${
        resizing ? `is-resizing is-resizing-${resizing}` : ""
      }`}
      style={{
        "--dn-sidebar-width": `${actualSidebarWidth}px`,
        "--dn-dataset-width": `${datasetWidth}px`,
      }}
    >
      {/* =====================================================
          LEFT SIDEBAR
      ===================================================== */}

      <aside
        className="sidebar-shell"
        style={{
          width: `${actualSidebarWidth}px`,
        }}
      >
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={toggleSidebar}
        />

        {!sidebarCollapsed && (
          <div
            className="sidebar-resize-handle"
            onPointerDown={(event) =>
              startResize("sidebar", event)
            }
            role="separator"
            aria-orientation="vertical"
            aria-label="Resize navigation sidebar"
          >
            <span />
          </div>
        )}
      </aside>

      {/* =====================================================
          MAIN APPLICATION
      ===================================================== */}

      <div className="app-main">
        <Navbar
          onToggleSidebar={toggleSidebar}
          datasetOpen={datasetOpen}
          onToggleDataset={toggleDataset}
        />

        <div
          className="workspace-grid"
          style={{
            gridTemplateColumns: datasetOpen
              ? `minmax(0, 1fr) 8px ${datasetWidth}px`
              : "minmax(0, 1fr)",
          }}
        >
          {/* =================================================
              CENTER WORKSPACE
          ================================================= */}

          <main className="chat-column">
            <ChatArea />
            <ChatInput />
          </main>

          {/* =================================================
              DATASET RESIZE HANDLE
          ================================================= */}

          {datasetOpen && (
            <div
              className="dataset-resize-handle"
              onPointerDown={(event) =>
                startResize("dataset", event)
              }
              role="separator"
              aria-orientation="vertical"
              aria-label="Resize dataset sidebar"
            >
              <span />
            </div>
          )}

          {/* =================================================
              DATASET SIDEBAR
          ================================================= */}

          {datasetOpen && <DatasetPanel />}
        </div>
      </div>

      {/* =====================================================
          MOBILE NAVIGATION
      ===================================================== */}

      <nav
        className="mobile-bottom-nav"
        aria-label="Mobile navigation"
      >
        <button
          type="button"
          onClick={() => goTo("/dashboard")}
          aria-label="Dashboard"
        >
          <span aria-hidden="true">⌂</span>
          <span>Dashboard</span>
        </button>

        <button
          type="button"
          onClick={() => goTo("/workspace")}
          aria-label="Analyze"
        >
          <span aria-hidden="true">✦</span>
          <span>Analyze</span>
        </button>

        <button
          type="button"
          onClick={() => goTo("/datasets")}
          aria-label="Datasets"
        >
          <span aria-hidden="true">▣</span>
          <span>Data</span>
        </button>

        <button
          type="button"
          onClick={() => goTo("/settings")}
          aria-label="Settings"
        >
          <span aria-hidden="true">⚙</span>
          <span>Settings</span>
        </button>
      </nav>
    </div>
  );
}