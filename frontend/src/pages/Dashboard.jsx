import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Compass,
  Database,
  FileBarChart2,
  FolderOpen,
  LayoutDashboard,
  MessageSquare,
  Plus,
  Sparkles,
  Upload,
  UserCheck,
  X,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useDataset } from "../context/DatasetContext";
import { useProject } from "../context/ProjectContext";
import BrandLogo from "../components/BrandLogo";

const FEATURES = [
  {
    icon: BarChart3,
    title: "Visualize",
    text: "Turn columns into clear charts and discover patterns.",
  },
  {
    icon: BrainCircuit,
    title: "Predict",
    text: "Build and evaluate machine learning models.",
  },
  {
    icon: Database,
    title: "Explore",
    text: "Profile, query and understand your dataset.",
  },
  {
    icon: FileBarChart2,
    title: "Report",
    text: "Turn your findings into polished reports.",
  },
];

const DATASET_QUESTIONS = [
  "Give me an overview of my dataset",
  "Show me the missing values in my dataset",
  "Show me the distribution of my data",
];

const GENERAL_QUESTIONS = [
  "How does DataNova analyze data?",
  "What can I ask DataNova?",
  "What types of files can I upload?",
];

export default function Dashboard() {
  const navigate = useNavigate();

  const { isGuest, demoLogin } = useAuth();
  const { dataset } = useDataset();

  const {
    projects,
    activeProject,
    loading: projectsLoading,
    error: projectError,
    selectProject,
    createProject,
    clearProject,
  } = useProject();

  const [showProjectMenu, setShowProjectMenu] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showQuickStart, setShowQuickStart] = useState(false);
  const [showGuestAuthModal, setShowGuestAuthModal] = useState(false);

  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDescription, setNewProjectDescription] = useState("");

  const [quickStartName, setQuickStartName] = useState(() => {
    const today = new Date().toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
    return `Analysis — ${today}`;
  });

  const [creatingProject, setCreatingProject] = useState(false);
  const [projectActionError, setProjectActionError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (
      params.get("action") === "quick-start" ||
      params.get("action") === "new-analysis"
    ) {
      if (isGuest) {
        setShowGuestAuthModal(true);
      } else {
        setShowQuickStart(true);
      }
    }
  }, [isGuest]);

  /* =========================================================
     DATASET INFORMATION
  ========================================================= */

  const profile = dataset?.profile || {};
  const shape = profile?.shape || {};

  const rows =
    (typeof shape.rows === "number"
      ? shape.rows
      : Array.isArray(shape)
      ? shape[0]
      : null) ??
    profile?.rows ??
    dataset?.rows ??
    0;

  const columns =
    (typeof shape.columns === "number"
      ? shape.columns
      : Array.isArray(shape)
      ? shape[1]
      : null) ??
    (Array.isArray(profile?.columns) ? profile.columns.length : null) ??
    (Array.isArray(profile?.column_names) ? profile.column_names.length : null) ??
    dataset?.columns ??
    0;

  const rawMissing =
    profile?.missing_values ??
    profile?.missing ??
    dataset?.missing_values ??
    0;

  const missingValues =
    typeof rawMissing === "object" && rawMissing !== null
      ? Object.values(rawMissing).reduce(
          (total, value) => total + Number(value || 0),
          0
        )
      : Number(rawMissing || 0);

  const formatMetric = (val) => {
    const num = Number(val);
    return Number.isFinite(num) ? num.toLocaleString() : "0";
  };

  const filename =
    dataset?.filename ||
    dataset?.name ||
    "No dataset uploaded";

  const hasDataset = Boolean(dataset && activeProject);

  /* =========================================================
     FEATURES
  ========================================================= */

  const features = FEATURES;
  const quickQuestions = hasDataset ? DATASET_QUESTIONS : GENERAL_QUESTIONS;

  /* =========================================================
     WORKFLOW ACTIONS
  ========================================================= */

  const openWorkspace = (question = "") => {
    navigate("/workspace");

    if (question) {
      setTimeout(() => {
        window.dispatchEvent(
          new CustomEvent("datanova:prompt", {
            detail: question,
          })
        );
      }, 150);
    }
  };

  const handleStartAnalysis = (question = "") => {
    if (isGuest) {
      setShowGuestAuthModal(true);
      return;
    }

    if (activeProject) {
      openWorkspace(question);
      return;
    }

    setShowQuickStart(true);
  };

  const handleOpenExistingProject = () => {
    if (projects.length > 0) {
      openProjectSelector();
    } else {
      navigate("/projects");
    }
  };

  const handleQuickStartSubmit = async (event) => {
    event.preventDefault();
    const name = quickStartName.trim();

    if (!name) {
      setProjectActionError("Please enter an analysis project name.");
      return;
    }

    try {
      setCreatingProject(true);
      setProjectActionError("");

      const project = await createProject(
        name,
        "Created via Quick Start Analysis"
      );

      setShowQuickStart(false);
      selectProject(project);
      navigate("/workspace");
    } catch (err) {
      setProjectActionError(
        err?.message || "Unable to start analysis. Please try again."
      );
    } finally {
      setCreatingProject(false);
    }
  };

  const handleCreateProject = async (event) => {
    event.preventDefault();

    if (isGuest) {
      setShowGuestAuthModal(true);
      return;
    }

    const name = newProjectName.trim();

    if (!name) {
      setProjectActionError("Please enter a project name.");
      return;
    }

    try {
      setCreatingProject(true);
      setProjectActionError("");

      const project = await createProject(
        name,
        newProjectDescription.trim()
      );

      setNewProjectName("");
      setNewProjectDescription("");
      setShowCreateProject(false);
      setShowProjectMenu(false);
      selectProject(project);
      navigate("/workspace");
    } catch (err) {
      setProjectActionError(
        err?.message || "Unable to create project. Please try again."
      );
    } finally {
      setCreatingProject(false);
    }
  };

  const openProjectSelector = () => {
    setShowProjectMenu((current) => !current);
    setShowCreateProject(false);
    setProjectActionError("");
  };

  const openCreateProjectModal = () => {
    if (isGuest) {
      setShowGuestAuthModal(true);
      return;
    }
    setShowCreateProject(true);
    setShowProjectMenu(false);
    setProjectActionError("");
  };

  const closeProjectPanels = () => {
    setShowCreateProject(false);
    setShowProjectMenu(false);
    setProjectActionError("");
  };

  return (
    <div className="dashboard-page">
      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}
      <header className="landing-nav">
        <button
          type="button"
          className="brand-logo-button"
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

        <div className="landing-actions">
          <button
            type="button"
            className="ghost-button"
            onClick={() => navigate("/projects")}
          >
            <FolderOpen size={15} style={{ marginRight: "6px" }} />
            Projects
          </button>

          {isGuest ? (
            <>
              <button
                type="button"
                className="secondary-button"
                onClick={() => navigate("/login")}
              >
                Sign in
              </button>
              <button
                type="button"
                className="primary-button"
                onClick={async () => {
                  await demoLogin();
                  navigate("/dashboard");
                }}
              >
                <Sparkles size={14} style={{ marginRight: "4px" }} />
                Try Demo
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                className="ghost-button"
                onClick={() => navigate("/settings")}
              >
                Settings
              </button>

              {activeProject ? (
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => openWorkspace()}
                >
                  Open workspace
                  <ArrowRight size={16} />
                </button>
              ) : (
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => handleStartAnalysis()}
                >
                  <Plus size={15} style={{ marginRight: "4px" }} />
                  Start analysis
                </button>
              )}
            </>
          )}
        </div>
      </header>

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}
      <main className="dashboard-content">

        {/* GUEST MODE BANNER */}
        {isGuest && (
          <div className="guest-banner" role="status">
            <div>
              <strong>Guest Explorer Mode</strong>
              <span style={{ marginLeft: "8px" }}>
                You have temporary access to explore DataNova AI. No data is stored permanently.
              </span>
            </div>
            <div style={{ display: "flex", gap: "8px", flexShrink: 0 }}>
              <button
                type="button"
                className="secondary-button"
                onClick={() => navigate("/login")}
                style={{ padding: "5px 12px", fontSize: "12px" }}
              >
                Sign In
              </button>
              <button
                type="button"
                className="primary-button"
                onClick={async () => {
                  await demoLogin();
                  navigate("/dashboard");
                }}
                style={{ padding: "5px 12px", fontSize: "12px" }}
              >
                Try Demo Account
              </button>
            </div>
          </div>
        )}

        {/* ===================================================
            WELCOME SECTION
        =================================================== */}
        <motion.section
          className="dashboard-welcome"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div>
            <div className="eyebrow">
              <Sparkles size={14} />
              AI-powered data workspace
            </div>

            <h1>
              Turn your data into
              <br />
              <span>meaningful insights.</span>
            </h1>

            <p>
              Upload CSV, Excel, or JSON datasets, ask questions in plain
              English, and let DataNova AI profile, visualize, and model your data.
            </p>
          </div>

          <div
            className="dashboard-welcome-actions"
            style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}
          >
            {/* 1. START NEW ANALYSIS */}
            <button
              type="button"
              className="primary-button large"
              onClick={() => handleStartAnalysis()}
            >
              <Sparkles size={18} />
              Start New Analysis
            </button>

            {/* 2. OPEN EXISTING PROJECT */}
            <button
              type="button"
              className="secondary-button large"
              onClick={handleOpenExistingProject}
            >
              <FolderOpen size={18} />
              Open Existing Project
            </button>

            {/* 3. CREATE PROJECT */}
            <button
              type="button"
              className="secondary-button large"
              onClick={openCreateProjectModal}
            >
              <Plus size={18} />
              Create Project
            </button>
          </div>
        </motion.section>

        {/* ===================================================
            ACTIVE PROJECT (IF SELECTED)
        =================================================== */}
        {activeProject && (
          <motion.section
            className="dashboard-section"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              padding: "20px 24px",
              background: "var(--dn-surface, #ffffff)",
              border: "1px solid #bfdbfe",
              borderRadius: "16px",
              boxShadow: "0 4px 18px rgba(37, 99, 235, 0.08)",
              marginBottom: "32px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "16px",
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <span className="section-kicker">Active Project</span>
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px",
                      padding: "2px 8px",
                      borderRadius: "999px",
                      background: "rgba(16, 185, 129, 0.12)",
                      color: "#10b981",
                      fontSize: "11px",
                      fontWeight: "700",
                    }}
                  >
                    <CheckCircle2 size={12} />
                    Active
                  </span>
                </div>

                <h2 style={{ margin: "0 0 4px 0", fontSize: "20px", fontWeight: "700" }}>
                  {activeProject.name}
                </h2>

                <p style={{ margin: 0, fontSize: "13px", color: "var(--dn-text-muted, #64748b)" }}>
                  {activeProject.description || "Active analysis workspace"}
                </p>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                <button
                  type="button"
                  className="ghost-button"
                  onClick={clearProject}
                  title="Return to general dashboard without an active project"
                >
                  Deselect project
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={openProjectSelector}
                >
                  Switch project
                </button>

                <button
                  type="button"
                  className="primary-button"
                  onClick={() => openWorkspace()}
                >
                  Open in workspace
                  <ArrowRight size={15} style={{ marginLeft: "4px" }} />
                </button>
              </div>
            </div>
          </motion.section>
        )}

        {/* ===================================================
            ACCURATE OVERVIEW METRICS
        =================================================== */}
        <motion.section
          className="dashboard-section"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="section-heading">
            <div>
              <span className="section-kicker">
                {hasDataset ? "Active Dataset Metrics" : "Platform Overview"}
              </span>

              <h2>
                {hasDataset
                  ? `Metrics: ${filename}`
                  : "Workspace Overview & Status"}
              </h2>
            </div>
          </div>

          {hasDataset ? (
            <div className="dataset-overview-card">
              <div className="dataset-overview-header">
                <div className="dataset-file-icon">
                  <Database size={22} />
                </div>

                <div className="dataset-overview-name">
                  <strong>{filename}</strong>
                  <span>Active dataset for {activeProject.name}</span>
                </div>

                <div className="dataset-ready-pill">
                  <span />
                  Ready
                </div>
              </div>

              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span>Rows</span>
                  <strong>{formatMetric(rows)}</strong>
                </div>

                <div className="dashboard-stat">
                  <span>Columns</span>
                  <strong>{formatMetric(columns)}</strong>
                </div>

                <div className="dashboard-stat">
                  <span>Missing values</span>
                  <strong>{formatMetric(missingValues)}</strong>
                </div>

                <div className="dashboard-stat">
                  <span>Status</span>
                  <strong className="status-ready">Ready</strong>
                </div>
              </div>
            </div>
          ) : (
            <div className="dataset-overview-card">
              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span>Saved Projects</span>
                  <strong>{projects.length}</strong>
                </div>

                <div className="dashboard-stat">
                  <span>Active Selection</span>
                  <strong style={{ fontSize: "16px", fontWeight: "600" }}>
                    {activeProject ? activeProject.name : "Optional mode"}
                  </strong>
                </div>

                <div className="dashboard-stat">
                  <span>AI Capabilities</span>
                  <strong style={{ fontSize: "16px", fontWeight: "600" }}>
                    4 Modules
                  </strong>
                </div>

                <div className="dashboard-stat">
                  <span>Session Environment</span>
                  <strong className="status-ready" style={{ fontSize: "16px" }}>
                    {isGuest ? "Guest Access" : "Operational"}
                  </strong>
                </div>
              </div>
            </div>
          )}
        </motion.section>

        {/* ===================================================
            RECENT PROJECTS SECTION
        =================================================== */}
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <span className="section-kicker">Project Organization</span>
              <h2>Your Projects</h2>
            </div>

            {projects.length > 0 && (
              <button
                type="button"
                className="text-button"
                onClick={() => navigate("/projects")}
              >
                View all ({projects.length})
                <ArrowRight size={15} />
              </button>
            )}
          </div>

          {projectsLoading && projects.length === 0 ? (
            <div className="empty-card">
              <FolderOpen size={28} className="animate-pulse" />
              <strong>Loading projects...</strong>
            </div>
          ) : projects.length === 0 ? (
            /* HELPFUL EMPTY STATE WHEN ZERO PROJECTS EXIST */
            <div className="dashboard-empty-card">
              <div className="dashboard-empty-icon">
                <FolderOpen size={25} />
              </div>

              <div>
                <strong>Projects are optional</strong>
                <p>
                  You don't need a project to explore DataNova AI. You can start an analysis right away,
                  or create a project whenever you want to organize multiple datasets, chats, and reports.
                </p>
              </div>

              <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => handleStartAnalysis()}
                >
                  <Sparkles size={16} style={{ marginRight: "4px" }} />
                  Start New Analysis
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={openCreateProjectModal}
                >
                  <Plus size={16} style={{ marginRight: "4px" }} />
                  Create First Project
                </button>
              </div>
            </div>
          ) : (
            /* RECENT PROJECTS CARDS */
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
                gap: "16px",
              }}
            >
              {projects.slice(0, 3).map((project) => {
                const isActive = activeProject?.id === project.id;
                return (
                  <div
                    key={project.id}
                    style={{
                      padding: "18px 20px",
                      background: "var(--dn-surface, #ffffff)",
                      border: isActive
                        ? "2px solid #2563eb"
                        : "1px solid var(--dn-border, #e2e8f0)",
                      borderRadius: "14px",
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                      boxShadow: "0 2px 8px rgba(15, 23, 42, 0.04)",
                    }}
                  >
                    <div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "flex-start",
                          justifyContent: "space-between",
                          gap: "8px",
                          marginBottom: "6px",
                        }}
                      >
                        <strong
                          style={{
                            fontSize: "15px",
                            fontWeight: "700",
                            color: "var(--dn-text, #0f172a)",
                          }}
                        >
                          {project.name}
                        </strong>

                        {isActive && (
                          <span
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "3px",
                              padding: "2px 6px",
                              borderRadius: "999px",
                              background: "rgba(16, 185, 129, 0.12)",
                              color: "#10b981",
                              fontSize: "10px",
                              fontWeight: "700",
                              flexShrink: 0,
                            }}
                          >
                            <CheckCircle2 size={11} />
                            Active
                          </span>
                        )}
                      </div>

                      <p
                        style={{
                          fontSize: "12px",
                          color: "var(--dn-text-muted, #64748b)",
                          margin: "0 0 14px 0",
                          lineHeight: "1.4",
                          minHeight: "34px",
                        }}
                      >
                        {project.description || "No description provided."}
                      </p>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        paddingTop: "12px",
                        borderTop: "1px solid var(--dn-border, #f1f5f9)",
                      }}
                    >
                      <button
                        type="button"
                        className="text-button"
                        onClick={() => {
                          selectProject(project);
                          navigate("/projects");
                        }}
                        style={{ fontSize: "12px" }}
                      >
                        Manage
                      </button>

                      <button
                        type="button"
                        className={isActive ? "primary-button" : "secondary-button"}
                        onClick={() => {
                          selectProject(project);
                          navigate("/workspace");
                        }}
                        style={{ fontSize: "12px", padding: "6px 12px" }}
                      >
                        {isActive ? "Open Workspace" : "Open Project"}
                        <ArrowRight size={13} style={{ marginLeft: "4px" }} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* PROJECT SELECTOR DROPDOWN (IF TOGGLED) */}
        {showProjectMenu && (
          <div className="project-selector" style={{ marginTop: "16px" }}>
            <div className="project-selector-header">
              <strong>Select a project</strong>
              <span>
                {projects.length} project{projects.length === 1 ? "" : "s"}
              </span>
            </div>

            {projects.length === 0 ? (
              <div className="project-selector-empty">
                <FolderOpen size={20} />
                <span>No projects yet. Create your first project or start an analysis.</span>
              </div>
            ) : (
              <div className="project-list">
                {projects.map((project) => (
                  <button
                    key={project.id}
                    type="button"
                    className={
                      activeProject?.id === project.id
                        ? "project-option active"
                        : "project-option"
                    }
                    onClick={() => {
                      selectProject(project);
                      setShowProjectMenu(false);
                      setProjectActionError("");
                    }}
                  >
                    <div>
                      <strong>{project.name}</strong>
                      {project.description && (
                        <span>{project.description}</span>
                      )}
                    </div>

                    {activeProject?.id === project.id && (
                      <span className="project-active-dot" />
                    )}
                  </button>
                ))}
              </div>
            )}

            <div
              style={{
                marginTop: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <button
                type="button"
                className="text-button"
                onClick={() => {
                  setShowProjectMenu(false);
                  navigate("/projects");
                }}
              >
                Manage all projects →
              </button>

              <button
                type="button"
                className="ghost-button"
                onClick={closeProjectPanels}
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* CREATE PROJECT FORM (IF TOGGLED) */}
        {showCreateProject && (
          <div className="project-create-card" style={{ marginTop: "16px" }}>
            <div className="project-create-heading">
              <div>
                <span className="section-kicker">New project</span>
                <h3>Create a new analysis project</h3>
              </div>

              <button
                type="button"
                className="ghost-button"
                onClick={closeProjectPanels}
                disabled={creatingProject}
              >
                Cancel
              </button>
            </div>

            {projectActionError && (
              <div className="auth-error" role="alert">
                {projectActionError}
              </div>
            )}

            <form
              className="project-create-form"
              onSubmit={handleCreateProject}
            >
              <label>
                <span>Project name</span>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(event) =>
                    setNewProjectName(event.target.value)
                  }
                  placeholder="e.g. Customer Churn Analysis"
                  disabled={creatingProject}
                  autoFocus
                  required
                />
              </label>

              <label>
                <span>Description</span>
                <textarea
                  value={newProjectDescription}
                  onChange={(event) =>
                    setNewProjectDescription(event.target.value)
                  }
                  placeholder="What will you analyze in this project?"
                  rows={3}
                  disabled={creatingProject}
                />
              </label>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "8px",
                }}
              >
                <button
                  type="button"
                  className="secondary-button"
                  onClick={closeProjectPanels}
                  disabled={creatingProject}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={creatingProject}
                >
                  {creatingProject ? "Creating..." : "Create & Open Workspace"}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* ===================================================
            QUICK ACTIONS
        =================================================== */}
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <span className="section-kicker">Quick actions</span>
              <h2>What do you want to do?</h2>
            </div>
          </div>

          <div className="dashboard-action-grid">
            <button
              type="button"
              className="dashboard-action-card"
              onClick={() => handleStartAnalysis()}
            >
              <div className="action-card-icon blue">
                <MessageSquare size={20} />
              </div>

              <div>
                <strong>Analyze with AI</strong>
                <p>Ask questions about your dataset in plain English.</p>
              </div>

              <ArrowRight size={17} />
            </button>

            <button
              type="button"
              className="dashboard-action-card"
              onClick={() => handleStartAnalysis("Create a visualization")}
            >
              <div className="action-card-icon purple">
                <BarChart3 size={20} />
              </div>

              <div>
                <strong>Create visualizations</strong>
                <p>Generate charts and explore relationships in your data.</p>
              </div>

              <ArrowRight size={17} />
            </button>

            <button
              type="button"
              className="dashboard-action-card"
              onClick={() => navigate("/reports")}
            >
              <div className="action-card-icon green">
                <FileBarChart2 size={20} />
              </div>

              <div>
                <strong>Generate reports</strong>
                <p>Turn your findings into a structured report.</p>
              </div>

              <ArrowRight size={17} />
            </button>
          </div>
        </section>

        {/* ===================================================
            CAPABILITIES
        =================================================== */}
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <span className="section-kicker">DataNova capabilities</span>
              <h2>Everything in one workspace</h2>
            </div>
          </div>

          <div className="feature-grid">
            {features.map(({ icon: Icon, title, text }, index) => (
              <motion.button
                key={title}
                type="button"
                className="feature-card"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.08 * index }}
                onClick={() => handleStartAnalysis()}
              >
                <div className="feature-icon">
                  <Icon size={20} />
                </div>

                <h3>{title}</h3>
                <p>{text}</p>
                <ArrowRight size={16} className="feature-arrow" />
              </motion.button>
            ))}
          </div>
        </section>

        {/* ===================================================
            QUICK QUESTIONS
        =================================================== */}
        <section className="quick-start">
          <div>
            <span className="section-kicker">Quick start</span>
            <h2>
              {hasDataset
                ? "Ask DataNova something"
                : "Start exploring your data"}
            </h2>

            <p>
              {hasDataset
                ? "Choose a question or open the workspace to ask anything about your dataset."
                : "Upload a dataset and start analyzing it with natural language."}
            </p>
          </div>

          <div className="prompt-examples">
            {quickQuestions.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => handleStartAnalysis(prompt)}
              >
                <Sparkles size={15} />
                {prompt}
                <ArrowRight size={14} />
              </button>
            ))}
          </div>
        </section>

        {/* ===================================================
            NEW ANALYSIS CALLOUT
        =================================================== */}
        <section className="dashboard-new-project">
          <div className="new-project-icon">
            <Plus size={22} />
          </div>

          <div>
            <strong>Start a new analysis</strong>
            <p>Upload another dataset and begin a fresh analysis.</p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={() => handleStartAnalysis()}
          >
            Start analysis
            <ArrowRight size={15} />
          </button>
        </section>
      </main>

      {/* =====================================================
          QUICK START ANALYSIS MODAL
      ===================================================== */}
      {showQuickStart && (
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
              width: "min(480px, 100%)",
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
                Start New Analysis
              </h3>
              <button
                type="button"
                className="ghost-button"
                onClick={() => setShowQuickStart(false)}
                disabled={creatingProject}
                style={{ padding: "6px" }}
              >
                <X size={18} />
              </button>
            </div>

            <p
              style={{
                fontSize: "13px",
                color: "var(--dn-text-muted, #64748b)",
                margin: "0 0 18px 0",
                lineHeight: "1.5",
              }}
            >
              A project container will be created to organize your datasets,
              conversations, and charts. Enter a name for your analysis, or use the recommended default.
            </p>

            {projectActionError && (
              <div
                className="auth-error"
                role="alert"
                style={{ marginBottom: "16px" }}
              >
                {projectActionError}
              </div>
            )}

            <form onSubmit={handleQuickStartSubmit}>
              <label style={{ display: "block", marginBottom: "16px" }}>
                <span
                  style={{
                    display: "block",
                    fontSize: "13px",
                    fontWeight: "600",
                    marginBottom: "6px",
                  }}
                >
                  Analysis Project Name
                </span>
                <input
                  type="text"
                  value={quickStartName}
                  onChange={(e) => setQuickStartName(e.target.value)}
                  placeholder="e.g. Sales Analysis"
                  required
                  autoFocus
                  disabled={creatingProject}
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
                  onClick={() => setShowQuickStart(false)}
                  disabled={creatingProject}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="primary-button"
                  disabled={creatingProject}
                >
                  {creatingProject
                    ? "Preparing Workspace..."
                    : "Start Analysis & Open Workspace"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================
          GUEST RESTRICTION MODAL
      ===================================================== */}
      {showGuestAuthModal && (
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
              width: "min(460px, 100%)",
              background: "var(--dn-surface, #ffffff)",
              border: "1px solid var(--dn-border, #e2e8f0)",
              borderRadius: "16px",
              padding: "28px",
              boxShadow: "0 20px 40px rgba(0, 0, 0, 0.2)",
              textAlign: "center",
            }}
          >
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "#eff6ff",
                color: "#2563eb",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 16px",
              }}
            >
              <Sparkles size={24} />
            </div>

            <h3
              style={{
                margin: "0 0 8px 0",
                fontSize: "18px",
                fontWeight: "700",
              }}
            >
              Sign In or Try Demo Account
            </h3>

            <p
              style={{
                fontSize: "13px",
                color: "var(--dn-text-muted, #64748b)",
                margin: "0 0 20px 0",
                lineHeight: "1.5",
              }}
            >
              Creating projects and uploading datasets is reserved for registered
              and demo accounts. Guest access is temporary and data is not retained.
            </p>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "10px",
              }}
            >
              <button
                type="button"
                className="primary-button"
                onClick={() => navigate("/login")}
                style={{
                  width: "100%",
                  justifyContent: "center",
                  padding: "10px",
                }}
              >
                Sign In / Create Account
              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={async () => {
                  setShowGuestAuthModal(false);
                  await demoLogin();
                  navigate("/dashboard");
                }}
                style={{
                  width: "100%",
                  justifyContent: "center",
                  padding: "10px",
                }}
              >
                Switch to Demo Account
              </button>

              <button
                type="button"
                className="ghost-button"
                onClick={() => setShowGuestAuthModal(false)}
                style={{ width: "100%", justifyContent: "center" }}
              >
                Continue Browsing as Guest
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
