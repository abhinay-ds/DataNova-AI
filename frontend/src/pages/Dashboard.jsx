import { useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Database,
  FileBarChart2,
  FolderOpen,
  MessageSquare,
  Plus,
  Sparkles,
  Upload,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useDataset } from "../context/DatasetContext";
import { useProject } from "../context/ProjectContext";

export default function Dashboard() {
  const navigate = useNavigate();

  const { dataset } = useDataset();

  const {
    projects,
    activeProject,
    loading: projectsLoading,
    error: projectError,
    selectProject,
    createProject,
  } = useProject();

  const [showProjectMenu, setShowProjectMenu] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);

  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectDescription, setNewProjectDescription] =
    useState("");

  const [creatingProject, setCreatingProject] = useState(false);
  const [projectActionError, setProjectActionError] =
    useState("");

  /* =========================================================
     DATASET INFORMATION
  ========================================================= */

  const profile = dataset?.profile || {};

  const rows =
    profile?.shape?.[0] ??
    profile?.rows ??
    dataset?.rows ??
    0;

  const columns =
    profile?.shape?.[1] ??
    profile?.columns ??
    dataset?.columns ??
    0;

  const missingValues =
    profile?.missing_values ??
    profile?.missing ??
    dataset?.missing_values ??
    0;

  const filename =
    dataset?.filename ||
    dataset?.name ||
    "No dataset uploaded";

  const hasDataset = Boolean(dataset);

  /* =========================================================
     FEATURES
  ========================================================= */

  const features = [
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

  /* =========================================================
     QUICK QUESTIONS
  ========================================================= */

  const quickQuestions = hasDataset
    ? [
        "Give me an overview of my dataset",
        "Show me the missing values in my dataset",
        "Show me the distribution of my data",
      ]
    : [
        "How does DataNova analyze data?",
        "What can I ask DataNova?",
        "What types of files can I upload?",
      ];

  /* =========================================================
     OPEN WORKSPACE
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

  /* =========================================================
     CREATE PROJECT
  ========================================================= */

  const handleCreateProject = async (event) => {
    event.preventDefault();

    const name = newProjectName.trim();

    if (!name) {
      setProjectActionError(
        "Please enter a project name."
      );
      return;
    }

    try {
      setCreatingProject(true);
      setProjectActionError("");

      await createProject(
        name,
        newProjectDescription.trim()
      );

      setNewProjectName("");
      setNewProjectDescription("");
      setShowCreateProject(false);
      setShowProjectMenu(false);
    } catch (err) {
      setProjectActionError(
        err?.message ||
          "Unable to create project. Please try again."
      );
    } finally {
      setCreatingProject(false);
    }
  };

  /* =========================================================
     PROJECT MENU
  ========================================================= */

  const openProjectSelector = () => {
    setShowProjectMenu((current) => !current);
    setShowCreateProject(false);
    setProjectActionError("");
  };

  const openCreateProject = () => {
    setShowCreateProject(true);
    setShowProjectMenu(false);
    setProjectActionError("");
  };

  const closeProjectPanels = () => {
    setShowCreateProject(false);
    setShowProjectMenu(false);
    setProjectActionError("");
  };

  /* =========================================================
     RENDER
  ========================================================= */

  return (
    <div className="dashboard-page">

      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <header className="landing-nav">
        <div className="brand-inline">
          <span className="brand-mark">
            <Sparkles size={17} />
          </span>

          <div>
            <strong>DataNova AI</strong>
            <small>Analyze • Visualize • Predict</small>
          </div>
        </div>

        <div className="landing-actions">
          <button
            type="button"
            className="ghost-button"
            onClick={() => navigate("/settings")}
          >
            Settings
          </button>

          <button
            type="button"
            className="primary-button"
            onClick={() => openWorkspace()}
          >
            Open workspace
            <ArrowRight size={16} />
          </button>
        </div>
      </header>

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <main className="dashboard-content">

        {/* ===================================================
            WELCOME
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
              Upload your dataset, ask questions in plain
              English, generate visualizations and let
              DataNova AI help you understand your data.
            </p>
          </div>

          <div className="dashboard-welcome-actions">
            <button
              type="button"
              className="primary-button large"
              onClick={() => openWorkspace()}
            >
              <Upload size={18} />
              Start analyzing
            </button>

            <button
              type="button"
              className="secondary-button large"
              onClick={() => navigate("/datasets")}
            >
              <FolderOpen size={18} />
              My datasets
            </button>
          </div>
        </motion.section>

        {/* ===================================================
            CURRENT PROJECT
        =================================================== */}

        <motion.section
          className="dashboard-section"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >

          <div className="dashboard-project-heading">

            <div>
              <span className="section-kicker">
                Current project
              </span>

              <h2>
                {projectsLoading
                  ? "Loading projects..."
                  : activeProject?.name ||
                    "No project selected"}
              </h2>

              {activeProject?.description && (
                <p className="dashboard-project-description">
                  {activeProject.description}
                </p>
              )}
            </div>

            <div className="dashboard-project-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={openProjectSelector}
                disabled={projectsLoading}
              >
                {activeProject
                  ? "Switch project"
                  : "Select project"}
              </button>

              <button
                type="button"
                className="primary-button"
                onClick={openCreateProject}
              >
                <Plus size={15} />
                New project
              </button>

            </div>
          </div>

          {/* =================================================
              PROJECT ERROR
          ================================================= */}

          {projectError && !showCreateProject && (
            <div
              className="auth-error"
              role="alert"
              style={{ marginTop: "16px" }}
            >
              {projectError}
            </div>
          )}

          {/* =================================================
              PROJECT SELECTOR
          ================================================= */}

          {showProjectMenu && (
            <div className="project-selector">

              <div className="project-selector-header">
                <strong>Your projects</strong>

                <span>
                  {projects.length} project
                  {projects.length === 1
                    ? ""
                    : "s"}
                </span>
              </div>

              {projects.length === 0 ? (
                <div className="project-selector-empty">
                  <FolderOpen size={20} />
                  <span>
                    No projects yet. Create your first
                    project.
                  </span>
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
                        <strong>
                          {project.name}
                        </strong>

                        {project.description && (
                          <span>
                            {project.description}
                          </span>
                        )}
                      </div>

                      {activeProject?.id ===
                        project.id && (
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
                  justifyContent: "flex-end",
                }}
              >
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

          {/* =================================================
              CREATE PROJECT
          ================================================= */}

          {showCreateProject && (
            <div className="project-create-card">

              <div className="project-create-heading">

                <div>
                  <span className="section-kicker">
                    New project
                  </span>

                  <h3>
                    Create a new analysis project
                  </h3>
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
                <div
                  className="auth-error"
                  role="alert"
                >
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
                      setNewProjectName(
                        event.target.value
                      )
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
                      setNewProjectDescription(
                        event.target.value
                      )
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
                    {creatingProject
                      ? "Creating..."
                      : "Create project"}
                  </button>
                </div>

              </form>
            </div>
          )}

          {/* =================================================
              DATASET STATUS
          ================================================= */}

          <div
            className="section-heading"
            style={{ marginTop: "28px" }}
          >
            <div>
              <span className="section-kicker">
                Active dataset
              </span>

              <h2>
                {hasDataset
                  ? "Your active dataset"
                  : "Ready for your first dataset"}
              </h2>
            </div>

            {hasDataset && (
              <button
                type="button"
                className="text-button"
                onClick={() => navigate("/workspace")}
              >
                Open workspace
                <ArrowRight size={15} />
              </button>
            )}
          </div>

          {hasDataset ? (
            <div className="dataset-overview-card">

              <div className="dataset-overview-header">

                <div className="dataset-file-icon">
                  <Database size={22} />
                </div>

                <div className="dataset-overview-name">
                  <strong>{filename}</strong>
                  <span>
                    Active dataset
                  </span>
                </div>

                <div className="dataset-ready-pill">
                  <span />
                  Ready
                </div>

              </div>

              <div className="dashboard-stat-grid">

                <div className="dashboard-stat">
                  <span>Rows</span>
                  <strong>
                    {Number(rows).toLocaleString()}
                  </strong>
                </div>

                <div className="dashboard-stat">
                  <span>Columns</span>
                  <strong>
                    {Number(columns).toLocaleString()}
                  </strong>
                </div>

                <div className="dashboard-stat">
                  <span>Missing values</span>
                  <strong>
                    {Number(
                      missingValues
                    ).toLocaleString()}
                  </strong>
                </div>

                <div className="dashboard-stat">
                  <span>Status</span>
                  <strong className="status-ready">
                    Ready
                  </strong>
                </div>

              </div>
            </div>
          ) : (
            <div className="dashboard-empty-card">

              <div className="dashboard-empty-icon">
                <Upload size={25} />
              </div>

              <div>
                <strong>
                  Upload a dataset to get started
                </strong>

                <p>
                  DataNova supports CSV, Excel and JSON
                  datasets. Once uploaded, you can
                  immediately start asking questions.
                </p>
              </div>

              <button
                type="button"
                className="primary-button"
                onClick={() => openWorkspace()}
              >
                Upload dataset
                <ArrowRight size={16} />
              </button>

            </div>
          )}

        </motion.section>

        {/* ===================================================
            QUICK ACTIONS
        =================================================== */}

        <section className="dashboard-section">

          <div className="section-heading">
            <div>
              <span className="section-kicker">
                Quick actions
              </span>

              <h2>
                What do you want to do?
              </h2>
            </div>
          </div>

          <div className="dashboard-action-grid">

            <button
              type="button"
              className="dashboard-action-card"
              onClick={() => openWorkspace()}
            >
              <div className="action-card-icon blue">
                <MessageSquare size={20} />
              </div>

              <div>
                <strong>
                  Analyze with AI
                </strong>

                <p>
                  Ask questions about your dataset in
                  plain English.
                </p>
              </div>

              <ArrowRight size={17} />
            </button>

            <button
              type="button"
              className="dashboard-action-card"
              onClick={() => openWorkspace()}
            >
              <div className="action-card-icon purple">
                <BarChart3 size={20} />
              </div>

              <div>
                <strong>
                  Create visualizations
                </strong>

                <p>
                  Generate charts and explore
                  relationships in your data.
                </p>
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
                <strong>
                  Generate reports
                </strong>

                <p>
                  Turn your analysis into a structured
                  report.
                </p>
              </div>

              <ArrowRight size={17} />
            </button>

          </div>
        </section>

        {/* ===================================================
            FEATURES
        =================================================== */}

        <section className="dashboard-section">

          <div className="section-heading">
            <div>
              <span className="section-kicker">
                DataNova capabilities
              </span>

              <h2>
                Everything in one workspace
              </h2>
            </div>
          </div>

          <div className="feature-grid">

            {features.map(
              (
                { icon: Icon, title, text },
                index
              ) => (
                <motion.button
                  key={title}
                  type="button"
                  className="feature-card"
                  initial={{
                    opacity: 0,
                    y: 15,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  transition={{
                    delay: 0.08 * index,
                  }}
                  onClick={() => openWorkspace()}
                >
                  <div className="feature-icon">
                    <Icon size={20} />
                  </div>

                  <h3>{title}</h3>

                  <p>{text}</p>

                  <ArrowRight
                    size={16}
                    className="feature-arrow"
                  />
                </motion.button>
              )
            )}

          </div>
        </section>

        {/* ===================================================
            QUICK QUESTIONS
        =================================================== */}

        <section className="quick-start">

          <div>
            <span className="section-kicker">
              Quick start
            </span>

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
                onClick={() =>
                  openWorkspace(prompt)
                }
              >
                <Sparkles size={15} />
                {prompt}
                <ArrowRight size={14} />
              </button>
            ))}

          </div>

        </section>

        {/* ===================================================
            NEW ANALYSIS
        =================================================== */}

        <section className="dashboard-new-project">

          <div className="new-project-icon">
            <Plus size={22} />
          </div>

          <div>
            <strong>
              Start a new analysis
            </strong>

            <p>
              Upload another dataset and begin a fresh
              analysis.
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={() => openWorkspace()}
          >
            Open workspace
            <ArrowRight size={15} />
          </button>

        </section>

      </main>
    </div>
  );
}