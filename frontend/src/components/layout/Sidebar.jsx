import { motion } from "framer-motion";

import {
  CheckSquare,
  Database,
  FileBarChart2,
  LayoutDashboard,
  MessageSquare,
  Plus,
  Settings,
  Sparkles,
  X,
} from "lucide-react";

import {
  NavLink,
  useNavigate,
} from "react-router-dom";

import BrandLogo from "../BrandLogo";


const primary = [
  {
    to: "/dashboard",
    label: "Dashboard",
    icon: LayoutDashboard,
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


const recent = [
  "Titanic Analysis",
  "Customer Churn",
  "Sales Dashboard",
];


export default function Sidebar({
  collapsed = false,
  onToggle,
}) {
  const navigate = useNavigate();

  const mobileClose = () => {
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


  return (
    <>
      {!collapsed && (
        <button
          type="button"
          className="sidebar-mobile-overlay"
          onClick={onToggle}
          aria-label="Close navigation"
        />
      )}

      <motion.aside
        animate={{
          width: collapsed ? 72 : 250,
        }}
        transition={{
          duration: 0.2,
          ease: "easeOut",
        }}
        className={`sidebar ${
          collapsed
            ? "is-collapsed"
            : "is-expanded"
        }`}
      >

        {/* BRAND */}

        <div className="sidebar-brand">

          {!collapsed ? (
            <>
              <button
                type="button"
                className="sidebar-logo-button"
                onClick={() =>
                  goTo("/workspace")
                }
                aria-label="DataNova AI"
              >
                <BrandLogo />
              </button>

              <button
                type="button"
                className="sidebar-mobile-close"
                onClick={onToggle}
                aria-label="Close navigation"
              >
                <X size={18} />
              </button>
            </>
          ) : (
            <button
              type="button"
              className="brand-mark"
              onClick={() =>
                goTo("/workspace")
              }
              aria-label="DataNova AI"
            >
              <Sparkles size={19} />
            </button>
          )}

        </div>


        {/* NEW ANALYSIS */}

        <button
          type="button"
          className="new-chat"
          onClick={() =>
            goTo("/workspace")
          }
        >
          <Plus size={18} />

          {!collapsed && (
            <span>
              New analysis
            </span>
          )}
        </button>


        {/* NAVIGATION */}

        <nav
          className="sidebar-nav"
          aria-label="Main navigation"
        >

          {!collapsed && (
            <p className="nav-label">
              Workspace
            </p>
          )}

          {primary.map(
            ({
              to,
              label,
              icon: Icon,
            }) => (
              <NavLink
                key={to}
                to={to}
                onClick={mobileClose}
                className={({ isActive }) =>
                  `nav-item ${
                    isActive
                      ? "active"
                      : ""
                  }`
                }
                title={
                  collapsed
                    ? label
                    : undefined
                }
              >
                <Icon size={18} />

                {!collapsed && (
                  <span>
                    {label}
                  </span>
                )}
              </NavLink>
            )
          )}


          {!collapsed && (
            <p className="nav-label recent-label">
              Recent chats
            </p>
          )}

          {recent.map((item) => (
            <button
              key={item}
              type="button"
              className="recent-item"
              onClick={() =>
                goTo("/workspace")
              }
            >
              <MessageSquare size={16} />

              {!collapsed && (
                <span>
                  {item}
                </span>
              )}
            </button>
          ))}

        </nav>


        {/* BOTTOM */}

        <div className="sidebar-bottom">

          <NavLink
            to="/settings"
            onClick={mobileClose}
            className={({ isActive }) =>
              `nav-item ${
                isActive
                  ? "active"
                  : ""
              }`
            }
          >
            <Settings size={18} />

            {!collapsed && (
              <span>
                Settings
              </span>
            )}
          </NavLink>


          {!collapsed && (
            <div className="profile-card">

              <div className="avatar">
                G
              </div>

              <div>
                <strong>
                  Guest workspace
                </strong>

                <span>
                  Free session
                </span>
              </div>

            </div>
          )}

        </div>

      </motion.aside>
    </>
  );
}