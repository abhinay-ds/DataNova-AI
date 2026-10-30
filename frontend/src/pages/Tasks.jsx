import {
  AlertCircle,
  CheckCircle2,
  CheckSquare,
  Clock,
  Code2,
  Cpu,
  LineChart,
  Loader2,
  MessageSquare,
  RefreshCw,
  Sparkles,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useProject } from "../context/ProjectContext";
import { getProjectTasks } from "../services/api";
import BrandLogo from "../components/BrandLogo";

const CAPABILITY_ICONS = {
  data_analysis: Cpu,
  analyze_dataset: Cpu,
  chart: LineChart,
  visualization: LineChart,
  code: Code2,
  code_generation: Code2,
  ml: Zap,
  machine_learning: Zap,
};

function formatCapabilityName(cap) {
  if (!cap) return "AI Task";
  return cap
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export default function Tasks() {
  const navigate = useNavigate();
  const { activeProject } = useProject();

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadTasks = async () => {
    if (!activeProject?.id) {
      setTasks([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getProjectTasks(activeProject.id);
      setTasks(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load tasks:", err);
      setError(err?.message || "Failed to load task history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [activeProject?.id]);

  return (
    <div className="simple-page">
      <div className="simple-top">
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
          aria-label="DataNova AI"
          style={{ background: "transparent", border: "none", padding: 0, cursor: "pointer", display: "flex", alignItems: "center" }}
        >
          <BrandLogo size="md" />
        </button>

        <button
          className="ghost-button"
          onClick={() => navigate("/workspace")}
        >
          Back to workspace
        </button>
      </div>

      <div className="simple-content wide">
        <div className="page-icon">
          <CheckSquare size={28} />
        </div>

        <span className="section-kicker">Tasks</span>
        <h1>AI Task History</h1>
        <p>
          {activeProject
            ? `Execution history of capabilities and routines dispatched for "${activeProject.name}".`
            : "Select a project to view AI task history."}
        </p>

        {/* Action Header */}
        {activeProject && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              margin: "20px 0 16px 0",
              padding: "12px 16px",
              background: "var(--dn-surface, #ffffff)",
              border: "1px solid var(--dn-border, #e5e7eb)",
              borderRadius: "10px",
            }}
          >
            <div style={{ fontSize: "13px", color: "var(--dn-text-muted)" }}>
              Total tasks recorded: <strong>{tasks.length}</strong>
            </div>

            <button
              className="ghost-button"
              onClick={loadTasks}
              disabled={loading}
              title="Refresh task history"
              style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              Refresh
            </button>
          </div>
        )}

        {error && (
          <div
            style={{
              padding: "12px 16px",
              marginBottom: "16px",
              borderRadius: "8px",
              background: "rgba(239, 68, 68, 0.1)",
              color: "#ef4444",
              fontSize: "13px",
            }}
          >
            {error}
          </div>
        )}

        {/* Loading state */}
        {loading && tasks.length === 0 ? (
          <div className="empty-card">
            <Loader2 size={28} className="animate-spin" />
            <strong>Loading task history...</strong>
            <span>Fetching executed routines from project conversations.</span>
          </div>
        ) : tasks.length > 0 ? (
          <div className="tasks-list">
            {tasks.map((task) => {
              const IconComponent =
                CAPABILITY_ICONS[task.capability.toLowerCase()] || Zap;
              const isCompleted = task.status === "completed";
              const dateStr = task.created_at
                ? new Date(task.created_at).toLocaleString()
                : "Recently";

              return (
                <div
                  key={task.id}
                  className="dataset-list-card"
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    justifyContent: "space-between",
                    padding: "16px",
                    marginBottom: "12px",
                    border: "1px solid var(--dn-border, #e5e7eb)",
                    borderRadius: "10px",
                    background: "var(--dn-surface, #ffffff)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "flex-start", gap: "14px", flex: 1 }}>
                    <div
                      style={{
                        padding: "8px",
                        borderRadius: "8px",
                        background: isCompleted
                          ? "rgba(16, 185, 129, 0.1)"
                          : "rgba(239, 68, 68, 0.1)",
                        color: isCompleted ? "#10b981" : "#ef4444",
                        marginTop: "2px",
                      }}
                    >
                      <IconComponent size={20} />
                    </div>

                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "8px",
                          marginBottom: "4px",
                          flexWrap: "wrap",
                        }}
                      >
                        <strong>{formatCapabilityName(task.capability)}</strong>

                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            fontSize: "11px",
                            fontWeight: "600",
                            background: isCompleted
                              ? "rgba(16, 185, 129, 0.12)"
                              : "rgba(239, 68, 68, 0.12)",
                            color: isCompleted ? "#10b981" : "#ef4444",
                          }}
                        >
                          {isCompleted ? (
                            <>
                              <CheckCircle2 size={12} /> Completed
                            </>
                          ) : (
                            <>
                              <AlertCircle size={12} /> Failed
                            </>
                          )}
                        </span>
                      </div>

                      {task.prompt && (
                        <div
                          style={{
                            fontSize: "13px",
                            color: "var(--dn-text-main)",
                            margin: "4px 0",
                            fontStyle: "italic",
                          }}
                        >
                          "{task.prompt}"
                        </div>
                      )}

                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "12px",
                          fontSize: "12px",
                          color: "var(--dn-text-muted)",
                          marginTop: "6px",
                        }}
                      >
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                          <Clock size={12} />
                          {dateStr}
                        </span>

                        <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                          <MessageSquare size={12} />
                          Conversation #{task.conversation_id}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="empty-card">
            <CheckSquare size={32} />
            <strong>No tasks recorded yet</strong>
            <span>
              When you prompt DataNova AI to analyze datasets, create charts, or train models, executed tasks will automatically appear here.
            </span>
            <button
              className="primary-button"
              onClick={() => navigate(activeProject ? "/workspace" : "/projects")}
              style={{ marginTop: "12px" }}
            >
              {activeProject ? "Open AI Workspace" : "View Projects"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
