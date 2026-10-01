import {
  Moon,
  Palette,
  Settings as SettingsIcon,
  Sparkles,
  Sun,
} from "lucide-react";

import { useNavigate } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";
import BrandLogo from "../components/BrandLogo";

export default function Settings() {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="simple-page">
      <div className="simple-top">
        <div className="brand-inline">
          
            <BrandLogo className="settings-logo" />
        </div>

        <button
          className="ghost-button"
          onClick={() => navigate("/workspace")}
        >
          Back to workspace
        </button>
      </div>

      <div className="simple-content wide">
        <div className="page-icon">
          <SettingsIcon />
        </div>

        <span className="section-kicker">Settings</span>

        <h1>Workspace preferences</h1>

        <p>
          Configure how your DataNova workspace looks and behaves.
        </p>

        {/* Appearance */}
        <div className="settings-card">
          <div>
            {theme === "dark" ? (
              <Moon size={20} />
            ) : (
              <Sun size={20} />
            )}

            <div>
              <strong>Appearance</strong>

              <span>
                {theme === "dark"
                  ? "Dark mode is enabled"
                  : "Light mode is enabled"}
              </span>
            </div>
          </div>

          <button
            type="button"
            className="theme-switch"
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            <span
              className={
                theme === "dark"
                  ? "theme-switch-thumb dark"
                  : "theme-switch-thumb"
              }
            />
          </button>
        </div>

        {/* AI Workspace */}
        <div className="settings-card">
          <div>
            <Sparkles size={19} />

            <div>
              <strong>AI workspace</strong>

              <span>
                Session-based analysis and conversation memory enabled
              </span>
            </div>
          </div>

          <span className="status-pill">Active</span>
        </div>
      </div>
    </div>
  );
}