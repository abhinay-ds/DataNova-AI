import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  Edit2,
  FolderOpen,
  LayoutDashboard,
  Plus,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";

import BrandLogo from "../components/BrandLogo";
import { useProject } from "../context/ProjectContext";

export default function Projects() {
  const navigate = useNavigate();
  const {
    projects,
    activeProject,
    loading,
    error,
    selectProject,
    createProject,
    updateProject,
    deleteProject,
    clearProject,
  } = useProject();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [actionError, setActionError] = useState("");

  const handleOpenCreate = () => {
    setName("");
    setDescription("");
    setActionError("");
    setShowCreateModal(true);
  };

  const handleOpenEdit = (project) => {
    setEditingProject(project);
    setName(project.name || "");
    setDescription(project.description || "");
    setActionError("");
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setActionError("Please provide a project name.");
      return;
    }

    try {
      setSubmitting(true);
      setActionError("");
      const created = await createProject(trimmed, description.trim());
      setShowCreateModal(false);
      selectProject(created);
      navigate("/workspace");
    } catch (err) {
      setActionError(err?.message || "Failed to create project.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!editingProject) return;
    const trimmed = name.trim();
    if (!trimmed) {
      setActionError("Please provide a project name.");
      return;
    }

    try {
      setSubmitting(true);
      setActionError("");
      await updateProject(editingProject.id, trimmed, description.trim());
      setEditingProject(null);
    } catch (err) {
      setActionError(err?.message || "Failed to update project.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (projectId, projectName) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${projectName}"? This will remove all associated datasets, chats, and reports in this project.`
    );
    if (!confirmed) return;

    try {
      setActionError("");
      await deleteProject(projectId);
    } catch (err) {
      setActionError(err?.message || "Failed to delete project.");
    }
  };

  const handleOpenProject = (project) => {
    selectProject(project);
    navigate("/workspace");
  };

  return (
    <div className="simple-page">
      {/* TOP NAVIGATION */}
      <div className="simple-top">
        <button
          type="button"
          onClick={() => navigate("/dashboard")}
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
          <BrandLogo size="md" />
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <button
            type="button"
            className="ghost-button"
            onClick={() => navigate("/dashboard")}
          >
            <LayoutDashboard size={15} style={{ marginRight: "6px" }} />
            Dashboard
          </button>

          {activeProject && (
            <button
              type="button"
              className="primary-button"
              onClick={() => navigate("/workspace")}
            >
              Open Workspace
              <ArrowRight size={15} style={{ marginLeft: "4px" }} />
            </button>
          )}
        </div>
      </div>

      {/* CONTENT */}
      <div className="simple-content wide">
        <div className="page-icon">
          <FolderOpen size={28} />
        </div>

        <span className="section-kicker">Project Management</span>
        <h1>Projects</h1>
        <p>
          Projects are optional containers for organizing your datasets, AI conversations,
          charts, and reports. Work within a project or return to the general dashboard anytime.
        </p>

        {/* CONTROLS BAR */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "12px",
            margin: "24px 0 16px",
            padding: "16px 20px",
            background: "var(--dn-surface, #ffffff)",
            border: "1px solid var(--dn-border, #e2e8f0)",
            borderRadius: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
            <button
              type="button"
              className="primary-button"
              onClick={handleOpenCreate}
            >
              <Plus size={16} style={{ marginRight: "4px" }} />
              New Project
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() => navigate("/dashboard")}
            >
              Return to Dashboard
            </button>
          </div>

          {activeProject ? (
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "4px 10px",
                  borderRadius: "999px",
                  background: "rgba(16, 185, 129, 0.12)",
                  color: "#10b981",
                  fontSize: "12px",
                  fontWeight: "600",
                }}
              >
                <CheckCircle2 size={13} />
                Active: {activeProject.name}
              </span>

              <button
                type="button"
                className="ghost-button"
                onClick={clearProject}
                title="Deselect this project and return to general mode"
                style={{ fontSize: "12px", padding: "4px 8px" }}
              >
                Deselect Project
              </button>
            </div>
          ) : (
            <span style={{ fontSize: "12px", color: "var(--dn-text-muted, #64748b)" }}>
              No project currently active (optional mode)
            </span>
          )}
        </div>

        {actionError && (
          <div
            className="auth-error"
            role="alert"
            style={{ marginBottom: "16px" }}
          >
            {actionError}
          </div>
        )}

        {error && (
          <div
            className="auth-error"
            role="alert"
            style={{ marginBottom: "16px" }}
          >
            {error}
          </div>
        )}

        {/* PROJECTS LIST */}
        {loading && projects.length === 0 ? (
          <div className="empty-card">
            <FolderOpen size={30} className="animate-pulse" />
            <strong>Loading projects...</strong>
            <span>Retrieving your saved projects.</span>
          </div>
        ) : projects.length === 0 ? (
          <div className="empty-card">
            <FolderOpen size={32} />
            <strong>No projects yet</strong>
            <span>
              Projects are optional containers. You can create a project to organize your
              analyses, datasets, and reports, or start directly from the dashboard.
            </span>
            <div style={{ display: "flex", gap: "10px", marginTop: "12px" }}>
              <button
                type="button"
                className="primary-button"
                onClick={handleOpenCreate}
              >
                <Plus size={16} style={{ marginRight: "4px" }} />
                Create First Project
              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={() => navigate("/dashboard")}
              >
                Return to Dashboard
              </button>
            </div>
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
              gap: "18px",
              marginTop: "8px",
            }}
          >
            {projects.map((project) => {
              const isActive = activeProject?.id === project.id;
              const dateStr = project.created_at
                ? new Date(project.created_at).toLocaleDateString()
                : null;

              return (
                <div
                  key={project.id}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    padding: "20px",
                    background: "var(--dn-surface, #ffffff)",
                    border: isActive
                      ? "2px solid #2563eb"
                      : "1px solid var(--dn-border, #e2e8f0)",
                    borderRadius: "14px",
                    boxShadow: isActive
                      ? "0 4px 20px rgba(37, 99, 235, 0.12)"
                      : "0 2px 8px rgba(15, 23, 42, 0.04)",
                    transition: "all 0.2s ease",
                  }}
                >
                  <div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        justifyContent: "space-between",
                        gap: "10px",
                        marginBottom: "8px",
                      }}
                    >
                      <strong
                        style={{
                          fontSize: "16px",
                          fontWeight: "700",
                          color: "var(--dn-text, #0f172a)",
                          lineHeight: "1.3",
                        }}
                      >
                        {project.name}
                      </strong>

                      {isActive && (
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "4px",
                            padding: "3px 8px",
                            borderRadius: "999px",
                            background: "rgba(16, 185, 129, 0.12)",
                            color: "#10b981",
                            fontSize: "11px",
                            fontWeight: "700",
                            flexShrink: 0,
                          }}
                        >
                          <CheckCircle2 size={12} />
                          Active
                        </span>
                      )}
                    </div>

                    <p
                      style={{
                        fontSize: "13px",
                        color: "var(--dn-text-muted, #64748b)",
                        lineHeight: "1.5",
                        margin: "0 0 16px 0",
                        minHeight: "38px",
                      }}
                    >
                      {project.description || "No description provided."}
                    </p>

                    {dateStr && (
                      <span
                        style={{
                          display: "block",
                          fontSize: "11px",
                          color: "var(--dn-text-muted, #94a3b8)",
                          marginBottom: "16px",
                        }}
                      >
                        Created on {dateStr}
                      </span>
                    )}
                  </div>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      paddingTop: "14px",
                      borderTop: "1px solid var(--dn-border, #f1f5f9)",
                      gap: "8px",
                    }}
                  >
                    <div style={{ display: "flex", gap: "6px" }}>
                      <button
                        type="button"
                        className="ghost-button"
                        onClick={() => handleOpenEdit(project)}
                        title="Rename project"
                        style={{ padding: "8px" }}
                      >
                        <Edit2 size={15} />
                      </button>

                      <button
                        type="button"
                        className="ghost-button"
                        onClick={() => handleDelete(project.id, project.name)}
                        title="Delete project"
                        style={{ padding: "8px", color: "#ef4444" }}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>

                    <div style={{ display: "flex", gap: "6px" }}>
                      {isActive ? (
                        <>
                          <button
                            type="button"
                            className="ghost-button"
                            onClick={clearProject}
                            style={{ fontSize: "12px", padding: "6px 10px" }}
                          >
                            Deselect
                          </button>
                          <button
                            type="button"
                            className="primary-button"
                            onClick={() => navigate("/workspace")}
                            style={{ fontSize: "12px", padding: "6px 12px" }}
                          >
                            Open
                            <ArrowRight size={13} style={{ marginLeft: "4px" }} />
                          </button>
                        </>
                      ) : (
                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => handleOpenProject(project)}
                          style={{ fontSize: "12px", padding: "6px 12px" }}
                        >
                          Open Project
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* CREATE PROJECT MODAL */}
      {showCreateModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            background: "rgba(15, 23, 42, 0.6)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
          }}
        >
          <div
            style={{
              width: "min(500px, 100%)",
              background: "var(--dn-surface, #ffffff)",
              border: "1px solid var(--dn-border, #e2e8f0)",
              borderRadius: "16px",
              padding: "28px",
              boxShadow: "0 20px 40px rgba(0, 0, 0, 0.2)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "16px",
              }}
            >
              <h3 style={{ margin: 0, fontSize: "18px", fontWeight: "700" }}>
                Create New Project
              </h3>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setShowCreateModal(false)}
                disabled={submitting}
                style={{ padding: "6px" }}
              >
                <X size={18} />
              </button>
            </div>

            {actionError && (
              <div
                className="auth-error"
                role="alert"
                style={{ marginBottom: "16px" }}
              >
                {actionError}
              </div>
            )}

            <form onSubmit={handleCreateSubmit}>
              <label style={{ display: "block", marginBottom: "14px" }}>
                <span
                  style={{
                    display: "block",
                    fontSize: "13px",
                    fontWeight: "600",
                    marginBottom: "6px",
                  }}
                >
                  Project Name
                </span>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Sales Forecast 2026"
                  required
                  autoFocus
                  disabled={submitting}
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "8px",
                    border: "1px solid var(--dn-border, #cbd5e1)",
                    fontSize: "14px",
                    background: "var(--dn-bg, #f8fafc)",
                    color: "var(--dn-text, #0f172a)",
                  }}
                />
              </label>

              <label style={{ display: "block", marginBottom: "20px" }}>
                <span
                  style={{
                    display: "block",
                    fontSize: "13px",
                    fontWeight: "600",
                    marginBottom: "6px",
                  }}
                >
                  Description (Optional)
                </span>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="What is the goal of this project?"
                  rows={3}
                  disabled={submitting}
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "8px",
                    border: "1px solid var(--dn-border, #cbd5e1)",
                    fontSize: "14px",
                    background: "var(--dn-bg, #f8fafc)",
                    color: "var(--dn-text, #0f172a)",
                    resize: "vertical",
                  }}
                />
              </label>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                }}
              >
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowCreateModal(false)}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={submitting}
                >
                  {submitting ? "Creating..." : "Create & Open Workspace"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT / RENAME PROJECT MODAL */}
      {editingProject && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 1000,
            background: "rgba(15, 23, 42, 0.6)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "20px",
          }}
        >
          <div
            style={{
              width: "min(500px, 100%)",
              background: "var(--dn-surface, #ffffff)",
              border: "1px solid var(--dn-border, #e2e8f0)",
              borderRadius: "16px",
              padding: "28px",
              boxShadow: "0 20px 40px rgba(0, 0, 0, 0.2)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "16px",
              }}
            >
              <h3 style={{ margin: 0, fontSize: "18px", fontWeight: "700" }}>
                Rename Project
              </h3>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setEditingProject(null)}
                disabled={submitting}
                style={{ padding: "6px" }}
              >
                <X size={18} />
              </button>
            </div>

            {actionError && (
              <div
                className="auth-error"
                role="alert"
                style={{ marginBottom: "16px" }}
              >
                {actionError}
              </div>
            )}

            <form onSubmit={handleEditSubmit}>
              <label style={{ display: "block", marginBottom: "14px" }}>
                <span
                  style={{
                    display: "block",
                    fontSize: "13px",
                    fontWeight: "600",
                    marginBottom: "6px",
                  }}
                >
                  Project Name
                </span>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  autoFocus
                  disabled={submitting}
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "8px",
                    border: "1px solid var(--dn-border, #cbd5e1)",
                    fontSize: "14px",
                    background: "var(--dn-bg, #f8fafc)",
                    color: "var(--dn-text, #0f172a)",
                  }}
                />
              </label>

              <label style={{ display: "block", marginBottom: "20px" }}>
                <span
                  style={{
                    display: "block",
                    fontSize: "13px",
                    fontWeight: "600",
                    marginBottom: "6px",
                  }}
                >
                  Description (Optional)
                </span>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  disabled={submitting}
                  style={{
                    width: "100%",
                    padding: "10px 14px",
                    borderRadius: "8px",
                    border: "1px solid var(--dn-border, #cbd5e1)",
                    fontSize: "14px",
                    background: "var(--dn-bg, #f8fafc)",
                    color: "var(--dn-text, #0f172a)",
                    resize: "vertical",
                  }}
                />
              </label>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "10px",
                }}
              >
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setEditingProject(null)}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={submitting}
                >
                  {submitting ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
