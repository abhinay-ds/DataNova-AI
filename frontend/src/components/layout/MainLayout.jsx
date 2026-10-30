import { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import ChatArea from "./ChatArea";
import ChatInput from "./ChatInput";
import DatasetPanel from "./DatasetPanel";

/* =========================================================
   STORAGE & LAYOUT CONFIGURATION
   ========================================================= */

const STORAGE_KEYS = {
  SIDEBAR_WIDTH: "datanova_sidebar_width",
  DATASET_WIDTH: "datanova_dataset_width",
  DATASET_HEIGHT: "datanova_dataset_height",
  PANEL_LAYOUT: "datanova_panel_layout",
  SIDEBAR_COLLAPSED: "datanova_sidebar_collapsed",
  DATASET_OPEN: "datanova_dataset_open",
};

const DEFAULTS = {
  SIDEBAR_WIDTH: 250,
  DATASET_WIDTH: 360,
  DATASET_HEIGHT: 320,
  PANEL_LAYOUT: "side", // "side" | "bottom"
};

const LIMITS = {
  SIDEBAR_MIN: 180,
  SIDEBAR_MAX: 400,
  DATASET_WIDTH_MIN: 280,
  DATASET_WIDTH_MAX: 750,
  DATASET_HEIGHT_MIN: 180,
  DATASET_HEIGHT_MAX: 650,
  CHAT_WIDTH_MIN: 320,
  CHAT_HEIGHT_MIN: 200,
};

function getStoredNumber(key, fallback, min, max) {
  try {
    const val = localStorage.getItem(key);
    if (val !== null) {
      const parsed = Number(val);
      if (Number.isFinite(parsed)) {
        return Math.min(Math.max(parsed, min), max);
      }
    }
  } catch (err) {
    // ignore
  }
  return fallback;
}

function getStoredString(key, fallback, validValues) {
  try {
    const val = localStorage.getItem(key);
    if (val && validValues.includes(val)) {
      return val;
    }
  } catch (err) {
    // ignore
  }
  return fallback;
}

function getStoredBoolean(key, fallback) {
  try {
    const val = localStorage.getItem(key);
    if (val !== null) {
      return val === "true";
    }
  } catch (err) {
    // ignore
  }
  return fallback;
}

export default function MainLayout() {
  const navigate = useNavigate();

  // Panel sizing & layout states initialized from localStorage (compact by default)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() =>
    getStoredBoolean(STORAGE_KEYS.SIDEBAR_COLLAPSED, true)
  );
  const [sidebarHovered, setSidebarHovered] = useState(false);

  const [sidebarWidth, setSidebarWidth] = useState(() =>
    getStoredNumber(
      STORAGE_KEYS.SIDEBAR_WIDTH,
      DEFAULTS.SIDEBAR_WIDTH,
      LIMITS.SIDEBAR_MIN,
      LIMITS.SIDEBAR_MAX
    )
  );

  const [datasetOpen, setDatasetOpen] = useState(() =>
    getStoredBoolean(STORAGE_KEYS.DATASET_OPEN, true)
  );

  const [panelLayout, setPanelLayout] = useState(() =>
    getStoredString(
      STORAGE_KEYS.PANEL_LAYOUT,
      DEFAULTS.PANEL_LAYOUT,
      ["side", "bottom"]
    )
  );

  const [datasetWidth, setDatasetWidth] = useState(() =>
    getStoredNumber(
      STORAGE_KEYS.DATASET_WIDTH,
      DEFAULTS.DATASET_WIDTH,
      LIMITS.DATASET_WIDTH_MIN,
      LIMITS.DATASET_WIDTH_MAX
    )
  );

  const [datasetHeight, setDatasetHeight] = useState(() =>
    getStoredNumber(
      STORAGE_KEYS.DATASET_HEIGHT,
      DEFAULTS.DATASET_HEIGHT,
      LIMITS.DATASET_HEIGHT_MIN,
      LIMITS.DATASET_HEIGHT_MAX
    )
  );

  const [resizing, setResizing] = useState(null); // null | "sidebar" | "dataset-width" | "dataset-height"

  const resizeState = useRef(null);

  // ChatGPT-style in-flow sidebar state:
  // If pinned open (!sidebarCollapsed), stays expanded.
  // When collapsed (compact 72px), hovering over the sidebar temporarily expands it in-flow, shifting main content.
  const isSidebarExpanded = !sidebarCollapsed || sidebarHovered;
  const actualSidebarWidth = isSidebarExpanded ? sidebarWidth : 72;

  /* =========================================================
     PERSIST TO LOCALSTORAGE
     ========================================================= */

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.SIDEBAR_WIDTH, String(sidebarWidth));
    } catch (e) {}
  }, [sidebarWidth]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.DATASET_WIDTH, String(datasetWidth));
    } catch (e) {}
  }, [datasetWidth]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.DATASET_HEIGHT, String(datasetHeight));
    } catch (e) {}
  }, [datasetHeight]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.PANEL_LAYOUT, panelLayout);
    } catch (e) {}
  }, [panelLayout]);

  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEYS.SIDEBAR_COLLAPSED,
        String(sidebarCollapsed)
      );
    } catch (e) {}
  }, [sidebarCollapsed]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.DATASET_OPEN, String(datasetOpen));
    } catch (e) {}
  }, [datasetOpen]);

  /* =========================================================
     WINDOW RESIZE ADAPTATION (PREVENT OVERFLOW)
     ========================================================= */

  useEffect(() => {
    const handleResize = () => {
      const w = window.innerWidth;
      const h = window.innerHeight;

      // Clamp sidebar width if window got small
      const maxSidebar = Math.min(LIMITS.SIDEBAR_MAX, Math.floor(w * 0.4));
      if (sidebarWidth > maxSidebar && maxSidebar >= LIMITS.SIDEBAR_MIN) {
        setSidebarWidth(maxSidebar);
      }

      // Clamp dataset width
      const effectiveSidebar = actualSidebarWidth;
      const maxDatasetW = Math.min(
        LIMITS.DATASET_WIDTH_MAX,
        Math.max(
          LIMITS.DATASET_WIDTH_MIN,
          w - effectiveSidebar - LIMITS.CHAT_WIDTH_MIN
        )
      );
      if (datasetWidth > maxDatasetW) {
        setDatasetWidth(maxDatasetW);
      }

      // Clamp dataset height
      const maxDatasetH = Math.min(
        LIMITS.DATASET_HEIGHT_MAX,
        Math.max(LIMITS.DATASET_HEIGHT_MIN, h - 60 - LIMITS.CHAT_HEIGHT_MIN)
      );
      if (datasetHeight > maxDatasetH) {
        setDatasetHeight(maxDatasetH);
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [sidebarWidth, datasetWidth, datasetHeight, actualSidebarWidth]);

  /* =========================================================
     TOGGLE ACTIONS
     ========================================================= */

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed((prev) => !prev);
    setSidebarHovered(false);
  }, []);

  const toggleDataset = useCallback(() => {
    setDatasetOpen((prev) => !prev);
  }, []);

  const togglePanelLayout = useCallback(() => {
    setPanelLayout((prev) => (prev === "side" ? "bottom" : "side"));
  }, []);

  const resetLayout = useCallback(() => {
    setSidebarWidth(DEFAULTS.SIDEBAR_WIDTH);
    setDatasetWidth(DEFAULTS.DATASET_WIDTH);
    setDatasetHeight(DEFAULTS.DATASET_HEIGHT);
    setPanelLayout(DEFAULTS.PANEL_LAYOUT);
    setSidebarCollapsed(false);
    setDatasetOpen(true);
  }, []);

  const handleDoubleClickHandle = useCallback((type) => {
    if (type === "sidebar") {
      setSidebarWidth(DEFAULTS.SIDEBAR_WIDTH);
    } else if (type === "dataset-width") {
      setDatasetWidth(DEFAULTS.DATASET_WIDTH);
    } else if (type === "dataset-height") {
      setDatasetHeight(DEFAULTS.DATASET_HEIGHT);
    }
  }, []);

  /* =========================================================
     KEYBOARD RESIZING (ACCESSIBILITY)
     ========================================================= */

  const handleKeyDownDivider = useCallback(
    (type, event) => {
      const step = event.shiftKey ? 40 : 10;
      const w = window.innerWidth;
      const h = window.innerHeight;
      const effectiveSidebar = actualSidebarWidth;

      if (type === "sidebar") {
        const maxSidebar = Math.min(LIMITS.SIDEBAR_MAX, Math.floor(w * 0.4));
        if (event.key === "ArrowLeft") {
          event.preventDefault();
          setSidebarWidth((prev) => Math.max(prev - step, LIMITS.SIDEBAR_MIN));
        } else if (event.key === "ArrowRight") {
          event.preventDefault();
          setSidebarWidth((prev) => Math.min(prev + step, maxSidebar));
        } else if (event.key === "Home") {
          event.preventDefault();
          setSidebarWidth(LIMITS.SIDEBAR_MIN);
        } else if (event.key === "End") {
          event.preventDefault();
          setSidebarWidth(maxSidebar);
        } else if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          setSidebarWidth(DEFAULTS.SIDEBAR_WIDTH);
        }
      } else if (type === "dataset-width") {
        const maxDatasetW = Math.min(
          LIMITS.DATASET_WIDTH_MAX,
          Math.max(
            LIMITS.DATASET_WIDTH_MIN,
            w - effectiveSidebar - LIMITS.CHAT_WIDTH_MIN
          )
        );
        if (event.key === "ArrowLeft") {
          // Dragging left makes dataset wider
          event.preventDefault();
          setDatasetWidth((prev) => Math.min(prev + step, maxDatasetW));
        } else if (event.key === "ArrowRight") {
          // Dragging right makes dataset narrower
          event.preventDefault();
          setDatasetWidth((prev) =>
            Math.max(prev - step, LIMITS.DATASET_WIDTH_MIN)
          );
        } else if (event.key === "Home") {
          event.preventDefault();
          setDatasetWidth(LIMITS.DATASET_WIDTH_MIN);
        } else if (event.key === "End") {
          event.preventDefault();
          setDatasetWidth(maxDatasetW);
        } else if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          setDatasetWidth(DEFAULTS.DATASET_WIDTH);
        }
      } else if (type === "dataset-height") {
        const maxDatasetH = Math.min(
          LIMITS.DATASET_HEIGHT_MAX,
          Math.max(LIMITS.DATASET_HEIGHT_MIN, h - 60 - LIMITS.CHAT_HEIGHT_MIN)
        );
        if (event.key === "ArrowUp") {
          // Dragging up makes dataset taller
          event.preventDefault();
          setDatasetHeight((prev) => Math.min(prev + step, maxDatasetH));
        } else if (event.key === "ArrowDown") {
          // Dragging down makes dataset shorter
          event.preventDefault();
          setDatasetHeight((prev) =>
            Math.max(prev - step, LIMITS.DATASET_HEIGHT_MIN)
          );
        } else if (event.key === "Home") {
          event.preventDefault();
          setDatasetHeight(LIMITS.DATASET_HEIGHT_MIN);
        } else if (event.key === "End") {
          event.preventDefault();
          setDatasetHeight(maxDatasetH);
        } else if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          setDatasetHeight(DEFAULTS.DATASET_HEIGHT);
        }
      }
    },
    [sidebarCollapsed, sidebarWidth, actualSidebarWidth]
  );

  /* =========================================================
     DRAGGING / RESIZING LOGIC
     ========================================================= */

  const startResize = useCallback(
    (type, event) => {
      event.preventDefault();
      event.stopPropagation();

      const startX = event.clientX;
      const startY = event.clientY;

      resizeState.current = {
        type,
        startX,
        startY,
        startSidebarWidth: sidebarWidth,
        startDatasetWidth: datasetWidth,
        startDatasetHeight: datasetHeight,
      };

      setResizing(type);

      document.body.style.userSelect = "none";
      document.body.style.cursor =
        type === "dataset-height" ? "row-resize" : "col-resize";

      const target = event.currentTarget;
      if (
        target &&
        target.setPointerCapture &&
        event.pointerId !== undefined
      ) {
        try {
          target.setPointerCapture(event.pointerId);
        } catch (err) {}
      }

      const handlePointerMove = (moveEvent) => {
        const state = resizeState.current;
        if (!state) return;

        const w = window.innerWidth;
        const h = window.innerHeight;

        if (state.type === "sidebar") {
          const delta = moveEvent.clientX - state.startX;
          const maxSidebar = Math.min(LIMITS.SIDEBAR_MAX, Math.floor(w * 0.4));
          const nextWidth = Math.min(
            Math.max(state.startSidebarWidth + delta, LIMITS.SIDEBAR_MIN),
            maxSidebar
          );
          setSidebarWidth(nextWidth);
        } else if (state.type === "dataset-width") {
          const delta = moveEvent.clientX - state.startX;
          const effectiveSidebar = actualSidebarWidth;
          const maxDataset = Math.min(
            LIMITS.DATASET_WIDTH_MAX,
            Math.max(
              LIMITS.DATASET_WIDTH_MIN,
              w - effectiveSidebar - LIMITS.CHAT_WIDTH_MIN
            )
          );
          const nextWidth = Math.min(
            Math.max(state.startDatasetWidth - delta, LIMITS.DATASET_WIDTH_MIN),
            maxDataset
          );
          setDatasetWidth(nextWidth);
        } else if (state.type === "dataset-height") {
          const delta = moveEvent.clientY - state.startY;
          const maxDatasetH = Math.min(
            LIMITS.DATASET_HEIGHT_MAX,
            Math.max(LIMITS.DATASET_HEIGHT_MIN, h - 60 - LIMITS.CHAT_HEIGHT_MIN)
          );
          const nextHeight = Math.min(
            Math.max(
              state.startDatasetHeight - delta,
              LIMITS.DATASET_HEIGHT_MIN
            ),
            maxDatasetH
          );
          setDatasetHeight(nextHeight);
        }
      };

      const handlePointerUp = (upEvent) => {
        if (
          target &&
          target.releasePointerCapture &&
          upEvent.pointerId !== undefined
        ) {
          try {
            target.releasePointerCapture(upEvent.pointerId);
          } catch (err) {}
        }

        resizeState.current = null;
        setResizing(null);

        document.body.style.userSelect = "";
        document.body.style.cursor = "";

        window.removeEventListener("pointermove", handlePointerMove);
        window.removeEventListener("pointerup", handlePointerUp);
        window.removeEventListener("pointercancel", handlePointerUp);
      };

      window.addEventListener("pointermove", handlePointerMove);
      window.addEventListener("pointerup", handlePointerUp);
      window.addEventListener("pointercancel", handlePointerUp);
    },
    [sidebarWidth, datasetWidth, datasetHeight, sidebarCollapsed, actualSidebarWidth]
  );

  /* Clean up body cursor on unmount */
  useEffect(() => {
    return () => {
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    };
  }, []);

  const goTo = (path) => {
    navigate(path);
  };

  /* =========================================================
     RENDER
     ========================================================= */

  return (
    <div
      className={`app-shell ${
        resizing ? `is-resizing is-resizing-${resizing}` : ""
      }`}
      style={{
        "--dn-sidebar-width": `${actualSidebarWidth}px`,
        "--dn-dataset-width": `${datasetWidth}px`,
        "--dn-dataset-height": `${datasetHeight}px`,
      }}
    >
      {/* =====================================================
          LEFT SIDEBAR (ChatGPT-style in-flow layout)
      ===================================================== */}

      <aside
        className={`sidebar-shell ${
          isSidebarExpanded ? "is-expanded-shell" : "is-collapsed-shell"
        }`}
        style={{
          width: `${actualSidebarWidth}px`,
        }}
        onMouseEnter={() => {
          if (
            typeof window !== "undefined" &&
            window.matchMedia("(hover: hover)").matches
          ) {
            setSidebarHovered(true);
          }
        }}
        onMouseLeave={() => {
          if (
            typeof window !== "undefined" &&
            window.matchMedia("(hover: hover)").matches
          ) {
            setSidebarHovered(false);
          }
        }}
        onFocus={() => {
          setSidebarHovered(true);
        }}
        onBlur={(e) => {
          if (!e.currentTarget.contains(e.relatedTarget)) {
            setSidebarHovered(false);
          }
        }}
      >
        <Sidebar
          collapsed={sidebarCollapsed}
          isExpanded={isSidebarExpanded}
          onToggle={toggleSidebar}
        />

        {!sidebarCollapsed && (
          <div
            className="sidebar-resize-handle"
            role="separator"
            tabIndex={0}
            aria-orientation="vertical"
            aria-label="Resize navigation sidebar"
            aria-valuenow={sidebarWidth}
            aria-valuemin={LIMITS.SIDEBAR_MIN}
            aria-valuemax={LIMITS.SIDEBAR_MAX}
            title="Drag to resize sidebar, double-click to reset"
            onPointerDown={(event) => startResize("sidebar", event)}
            onDoubleClick={() => handleDoubleClickHandle("sidebar")}
            onKeyDown={(event) => handleKeyDownDivider("sidebar", event)}
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
          sidebarCollapsed={sidebarCollapsed}
          onToggleSidebar={toggleSidebar}
          datasetOpen={datasetOpen}
          onToggleDataset={toggleDataset}
          panelLayout={panelLayout}
          onTogglePanelLayout={togglePanelLayout}
          onResetLayout={resetLayout}
        />

        {panelLayout === "side" ? (
          /* =================================================
              SIDE-BY-SIDE (HORIZONTAL 3-COLUMN) LAYOUT
             ================================================= */
          <div
            className="workspace-grid workspace-layout-side"
            style={{
              gridTemplateColumns: datasetOpen
                ? `minmax(0, 1fr) 8px ${datasetWidth}px`
                : "minmax(0, 1fr)",
            }}
          >
            {/* CENTER WORKSPACE */}
            <main className="chat-column">
              <ChatArea />
              <ChatInput />
            </main>

            {/* DATASET HORIZONTAL RESIZE HANDLE */}
            {datasetOpen && (
              <div
                className="dataset-resize-handle"
                role="separator"
                tabIndex={0}
                aria-orientation="vertical"
                aria-label="Resize dataset panel width"
                aria-valuenow={datasetWidth}
                aria-valuemin={LIMITS.DATASET_WIDTH_MIN}
                aria-valuemax={LIMITS.DATASET_WIDTH_MAX}
                title="Drag to resize panel width, double-click to reset"
                onPointerDown={(event) =>
                  startResize("dataset-width", event)
                }
                onDoubleClick={() =>
                  handleDoubleClickHandle("dataset-width")
                }
                onKeyDown={(event) =>
                  handleKeyDownDivider("dataset-width", event)
                }
              >
                <span />
              </div>
            )}

            {/* DATASET SIDEBAR */}
            {datasetOpen && (
              <DatasetPanel
                layoutMode="side"
                onToggleLayout={togglePanelLayout}
                onClose={toggleDataset}
              />
            )}
          </div>
        ) : (
          /* =================================================
              STACKED (VERTICAL SPLIT) LAYOUT
             ================================================= */
          <div className="workspace-grid workspace-layout-bottom">
            {/* TOP CHAT WORKSPACE */}
            <main className="chat-column">
              <ChatArea />
              <ChatInput />
            </main>

            {/* VERTICAL DIVIDER / ROW RESIZE HANDLE */}
            {datasetOpen && (
              <div
                className="workspace-horizontal-resize-handle"
                role="separator"
                tabIndex={0}
                aria-orientation="horizontal"
                aria-label="Resize dataset panel height"
                aria-valuenow={datasetHeight}
                aria-valuemin={LIMITS.DATASET_HEIGHT_MIN}
                aria-valuemax={LIMITS.DATASET_HEIGHT_MAX}
                title="Drag to resize panel height, double-click to reset"
                onPointerDown={(event) =>
                  startResize("dataset-height", event)
                }
                onDoubleClick={() =>
                  handleDoubleClickHandle("dataset-height")
                }
                onKeyDown={(event) =>
                  handleKeyDownDivider("dataset-height", event)
                }
              >
                <span />
              </div>
            )}

            {/* BOTTOM DATASET CONTAINER */}
            {datasetOpen && (
              <div
                className="dataset-bottom-container"
                style={{
                  height: `${datasetHeight}px`,
                  minHeight: `${LIMITS.DATASET_HEIGHT_MIN}px`,
                  maxHeight: `${LIMITS.DATASET_HEIGHT_MAX}px`,
                }}
              >
                <DatasetPanel
                  layoutMode="bottom"
                  onToggleLayout={togglePanelLayout}
                  onClose={toggleDataset}
                />
              </div>
            )}
          </div>
        )}
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