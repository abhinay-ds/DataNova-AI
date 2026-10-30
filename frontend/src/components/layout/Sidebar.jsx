import { useState } from "react";
import {
  CheckSquare,
  Database,
  FileBarChart2,
  FolderOpen,
  LayoutDashboard,
  MessageSquare,
  PanelLeft,
  Plus,
  Settings,
  Sparkles,
  X,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

import BrandLogo from "../BrandLogo";
import { useAuth } from "../../context/AuthContext";
import { useProject } from "../../context/ProjectContext";
import { useChat } from "../../context/ChatContext";

const primary = [
  {
    to: "/dashboard",
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    to: "/projects",
    label: "Projects",
    icon: FolderOpen,
  },
  {
    to: "/workspace",
    label: "AI Workspace",
    icon: Sparkles,
  },
  {
    to: "/datasets",
    label: "Datasets",
    icon: Database,
  },
  {
    to: "/reports",
    label: "Reports",
    icon: FileBarChart2,
  },
  {
    to: "/tasks",
    label: "Tasks",
    icon: CheckSquare,
  },
];

const DEFAULT_RECENT_CHATS = [
  { id: "titanic", title: "Titanic Analysis" },
  { id: "churn", title: "Customer Churn" },
  { id: "sales", title: "Sales Dashboard" },
];

export default function Sidebar({
  collapsed = false,
  isExpanded: parentExpanded = false,
  onToggle,
}) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { activeProject } = useProject();
  const chatContext = useChat();

  const [touchExpanded, setTouchExpanded] = useState(false);

  // If pinned open (!collapsed) or parent expanded (hover/focus), sidebar is expanded.
  // On mobile touch devices, touchExpanded toggles drawer overlay.
  const isExpanded = parentExpanded || touchExpanded;

  const conversations = chatContext?.conversations || [];
  const activeConversationId = chatContext?.activeConversationId;
  const selectConversation = chatContext?.selectConversation;

  const recentChats =
    conversations && conversations.length > 0
      ? conversations.slice(0, 6)
      : DEFAULT_RECENT_CHATS;

  const mobileClose = () => {
    setTouchExpanded(false);
    if (
      typeof window !== "undefined" &&
      window.innerWidth <= 768 &&
      onToggle
    ) {
      onToggle();
    }
  };

  const goTo = (path) => {
    navigate(path);
    mobileClose();
  };

  const handleNewAnalysis = () => {
    if (activeProject) {
      goTo("/workspace");
    } else {
      goTo("/dashboard?action=quick-start");
    }
  };

  const handleSelectRecentChat = (item) => {
    if (
      item &&
      item.id &&
      selectConversation &&
      item.id !== "titanic" &&
      item.id !== "churn" &&
      item.id !== "sales"
    ) {
      selectConversation(item.id);
    }
    goTo("/workspace");
  };

  const userInitial =
    user?.full_name?.[0]?.toUpperCase() ||
    user?.email?.[0]?.toUpperCase() ||
    "U";
  const userDisplayName =
    user?.full_name ||
    user?.email ||
    "DataNova User";
  const projectStatus =
    activeProject?.name || "Optional mode";

  return (
    <>
      {/* Mobile Drawer Backdrop */}
      {!collapsed && (
        <button
          type="button"
          className="sidebar-mobile-overlay"
          onClick={onToggle}
          aria-label="Close navigation"
        />
      )}

      {/* Touch Backdrop for touch-expanded compact sidebar */}
      {collapsed && touchExpanded && (
        <button
          type="button"
          className="sidebar-touch-backdrop"
          onClick={() => setTouchExpanded(false)}
          aria-label="Close sidebar overlay"
        />
      )}

      <aside
        className={`sidebar ${
          isExpanded ? "is-expanded" : "is-collapsed"
        }`}
        aria-expanded={isExpanded}
      >
        {/* BRAND & HEADER CONTROLS */}
        <div className="sidebar-brand">
          {isExpanded ? (
            <div className="sidebar-brand-expanded">
              <button
                type="button"
                className="sidebar-logo-button"
                onClick={() => goTo("/dashboard")}
                aria-label="DataNova AI"
                style={{
                  background: "transparent",
                  border: "none",
                  padding: 0,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <BrandLogo variant="full" size="sm" />
              </button>

              <div className="sidebar-brand-actions">
                {/* Desktop Collapse/Pin Button */}
                <button
                  type="button"
                  className="sidebar-toggle-btn icon-button desktop-only-btn"
                  onClick={onToggle}
                  aria-label={collapsed ? "Pin sidebar open" : "Collapse sidebar"}
                  title={collapsed ? "Pin sidebar open" : "Collapse sidebar"}
                >
                  <PanelLeft size={18} />
                </button>

                {/* Mobile Drawer Close Button */}
                <button
                  type="button"
                  className="sidebar-mobile-close mobile-only-btn"
                  onClick={mobileClose}
                  aria-label="Close navigation"
                >
                  <X size={18} />
                </button>
              </div>
            </div>
          ) : (
            <button
              type="button"
              className="brand-mark-collapsed"
              onClick={() => goTo("/dashboard")}
              aria-label="DataNova AI"
              title="DataNova AI - Click for Dashboard"
              style={{
                background: "transparent",
                border: "none",
                padding: 0,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "100%",
                height: "100%",
              }}
            >
              <BrandLogo variant="icon" size="sm" />
            </button>
          )}
        </div>

        {/* NEW ANALYSIS BUTTON */}
        <button
          type="button"
          className="new-chat"
          onClick={handleNewAnalysis}
          title={
            !isExpanded
              ? activeProject
                ? "New analysis in active project"
                : "Start a new analysis"
              : undefined
          }
        >
          <Plus size={18} style={{ flexShrink: 0 }} />
          {isExpanded && <span className="nav-text">New analysis</span>}
        </button>

        {/* MAIN NAVIGATION */}
        <nav
          className="sidebar-nav"
          aria-label="Main navigation"
        >
          {isExpanded && (
            <p className="nav-label">
              Workspace
            </p>
          )}

          {primary.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={mobileClose}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
              title={!isExpanded ? label : undefined}
            >
              <Icon size={18} style={{ flexShrink: 0 }} />
              {isExpanded && <span className="nav-text">{label}</span>}
            </NavLink>
          ))}

          {/* RECENT CHATS (Shows actual conversation titles when available) */}
          {isExpanded && (
            <>
              <p className="nav-label recent-label">
                Recent chats
              </p>

              {recentChats.map((item) => {
                const title = item.title || item;
                const id = item.id || title;
                const isActive =
                  activeConversationId && activeConversationId === item.id;

                return (
                  <button
                    key={id}
                    type="button"
                    className={`recent-item ${
                      isActive ? "active-recent" : ""
                    }`}
                    onClick={() => handleSelectRecentChat(item)}
                    title={title}
                  >
                    <MessageSquare size={16} style={{ flexShrink: 0 }} />
                    <span className="nav-text">{title}</span>
                  </button>
                );
              })}
            </>
          )}
        </nav>

        {/* BOTTOM AREA (Settings & User Profile) */}
        <div className="sidebar-bottom">
          <NavLink
            to="/settings"
            onClick={mobileClose}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
            title={!isExpanded ? "Settings" : undefined}
          >
            <Settings size={18} style={{ flexShrink: 0 }} />
            {isExpanded && <span className="nav-text">Settings</span>}
          </NavLink>

          {isExpanded ? (
            <div className="profile-card">
              <div className="avatar">
                {userInitial}
              </div>

              <div className="profile-info">
                <strong>{userDisplayName}</strong>
                <span>{projectStatus}</span>
              </div>
            </div>
          ) : (
            <div
              className="profile-card-collapsed"
              title={`${userDisplayName} (${projectStatus})`}
            >
              <div className="avatar">
                {userInitial}
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
