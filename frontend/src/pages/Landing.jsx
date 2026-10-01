import { motion } from "framer-motion";

import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Database,
  FileBarChart2,
  FileCode2,
  Sparkles,
  Upload,
  Zap,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import BrandLogo from "../components/BrandLogo";


// ============================================================
// CAPABILITIES
// ============================================================

const capabilities = [
  {
    icon: Database,
    title: "Explore your data",
    text: "Automatically understand rows, columns, missing values and dataset structure.",
  },
  {
    icon: BarChart3,
    title: "Visualize instantly",
    text: "Generate useful charts and uncover relationships without writing plotting code.",
  },
  {
    icon: BrainCircuit,
    title: "Ask AI questions",
    text: "Use natural language to query your dataset and get understandable answers.",
  },
  {
    icon: FileCode2,
    title: "Generate code",
    text: "Get reproducible Python analysis code for the work DataNova performs.",
  },
  {
    icon: FileBarChart2,
    title: "Create reports",
    text: "Turn your analysis into structured reports ready to share.",
  },
  {
    icon: Zap,
    title: "Work faster",
    text: "Keep analysis, visualizations and conversations together in one workspace.",
  },
];


// ============================================================
// LANDING PAGE
// ============================================================

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">

      {/* =====================================================
          NAVBAR
          ===================================================== */}

      <nav className="landing-main-nav">

        <button
          className="landing-brand"
          onClick={() => navigate("/")}
          type="button"
          aria-label="DataNova AI home"
        >
          <BrandLogo className="landing-logo" />
        </button>


        <div className="landing-nav-links">

          <button
            onClick={() => navigate("/dashboard")}
            type="button"
          >
            Dashboard
          </button>

          <button
            onClick={() => navigate("/workspace")}
            type="button"
          >
            Workspace
          </button>

          <button
            onClick={() => navigate("/datasets")}
            type="button"
          >
            Datasets
          </button>

        </div>


        <button
          className="primary-button"
          onClick={() => navigate("/workspace")}
          type="button"
        >
          Start analyzing
          <ArrowRight size={16} />
        </button>

      </nav>


      {/* =====================================================
          HERO
          ===================================================== */}

      <main>

        <section className="landing-hero">

          <motion.div
            className="landing-hero-content"
            initial={{
              opacity: 0,
              y: 25,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              duration: 0.5,
            }}
          >

            {/* Eyebrow */}

            <div className="landing-eyebrow">
              <Sparkles size={14} />
              AI-powered data workspace
            </div>


            {/* Heading */}

            <h1>
              From raw data to
              <br />
              <span>clear decisions.</span>
            </h1>


            {/* Description */}

            <p>
              Upload a dataset, ask questions in plain English,
              generate visualizations, train models and turn your
              analysis into polished reports.
            </p>


            {/* Hero buttons */}

            <div className="landing-hero-actions">

              <button
                className="primary-button large"
                onClick={() => navigate("/workspace")}
                type="button"
              >
                <Upload size={18} />
                Analyze your data
              </button>


              <button
                className="secondary-button large"
                onClick={() => navigate("/dashboard")}
                type="button"
              >
                Explore DataNova
                <ArrowRight size={17} />
              </button>

            </div>


            {/* Supported formats */}

            <div className="landing-supported">
              <span>Supports</span>
              <b>CSV</b>
              <b>Excel</b>
              <b>JSON</b>
              <b>SQL</b>
            </div>

          </motion.div>


          {/* =================================================
              HERO PRODUCT PREVIEW
              ================================================= */}

          <motion.div
            className="landing-preview"
            initial={{
              opacity: 0,
              x: 35,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
            transition={{
              duration: 0.6,
              delay: 0.15,
            }}
          >

            <div className="preview-window">

              {/* Top bar */}

              <div className="preview-topbar">

                <div className="preview-dots">
                  <span />
                  <span />
                  <span />
                </div>

                <span>
                  DataNova Workspace
                </span>

                <div />

              </div>


              {/* Preview body */}

              <div className="preview-body">

                {/* Preview sidebar */}

                <aside className="preview-sidebar">

                  <div className="preview-sidebar-logo">
                    <Sparkles size={13} />
                    DataNova
                  </div>


                  <div className="preview-nav active">
                    <BarChart3 size={13} />
                    Workspace
                  </div>


                  <div className="preview-nav">
                    <Database size={13} />
                    Datasets
                  </div>


                  <div className="preview-nav">
                    <FileBarChart2 size={13} />
                    Reports
                  </div>

                </aside>


                {/* Preview content */}

                <div className="preview-content">

                  {/* Heading */}

                  <div className="preview-heading">

                    <div>

                      <small>
                        AI DATA ANALYST
                      </small>

                      <h3>
                        Analyze your dataset
                      </h3>

                    </div>


                    <div className="preview-status">
                      <span />
                      Dataset ready
                    </div>

                  </div>


                  {/* Statistics */}

                  <div className="preview-stats">

                    <div>
                      <span>Rows</span>
                      <strong>891</strong>
                    </div>


                    <div>
                      <span>Columns</span>
                      <strong>12</strong>
                    </div>


                    <div>
                      <span>Missing</span>
                      <strong>866</strong>
                    </div>

                  </div>


                  {/* Analysis cards */}

                  <div className="preview-analysis">

                    {/* Chart */}

                    <div className="preview-chart">

                      <div className="preview-card-title">
                        Survival by passenger class
                      </div>


                      <div className="fake-bars">
                        <span style={{ height: "42%" }} />
                        <span style={{ height: "67%" }} />
                        <span style={{ height: "88%" }} />
                      </div>


                      <div className="fake-labels">
                        <span>1st</span>
                        <span>2nd</span>
                        <span>3rd</span>
                      </div>

                    </div>


                    {/* Chat */}

                    <div className="preview-chat">

                      <div className="preview-card-title">
                        Ask DataNova
                      </div>


                      <div className="preview-user-message">
                        Show survival across passenger classes
                      </div>


                      <div className="preview-ai-message">
                        <Sparkles size={12} />

                        First-class passengers had the highest
                        survival rate in this dataset.
                      </div>

                    </div>

                  </div>

                </div>

              </div>

            </div>

          </motion.div>

        </section>


        {/* =====================================================
            CAPABILITIES
            ===================================================== */}

        <section className="landing-section">

          <div className="landing-section-heading">

            <span>
              CAPABILITIES
            </span>


            <h2>
              Everything you need to
              <br />
              understand your data.
            </h2>


            <p>
              From the first upload to the final insight,
              DataNova brings your analysis workflow together.
            </p>

          </div>


          <div className="landing-capability-grid">

            {capabilities.map(
              ({ icon: Icon, title, text }, index) => (

                <motion.div
                  key={title}
                  className="landing-capability"
                  initial={{
                    opacity: 0,
                    y: 15,
                  }}
                  whileInView={{
                    opacity: 1,
                    y: 0,
                  }}
                  viewport={{
                    once: true,
                  }}
                  transition={{
                    delay: index * 0.05,
                  }}
                >

                  <div className="landing-capability-icon">
                    <Icon size={20} />
                  </div>


                  <h3>
                    {title}
                  </h3>


                  <p>
                    {text}
                  </p>

                </motion.div>

              )
            )}

          </div>

        </section>


        {/* =====================================================
            CTA
            ===================================================== */}

        <section className="landing-cta">

          <div className="landing-cta-icon">
            <Sparkles size={23} />
          </div>


          <h2>
            Ready to understand
            <br />
            your data?
          </h2>


          <p>
            Upload a dataset and start asking questions.
          </p>


          <button
            className="primary-button large"
            onClick={() => navigate("/workspace")}
            type="button"
          >
            Open DataNova
            <ArrowRight size={17} />
          </button>

        </section>

      </main>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="landing-footer">

        <div className="landing-brand">

          <BrandLogo className="landing-footer-logo" />

        </div>


        <span>
          AI-powered data analysis workspace
        </span>

      </footer>

    </div>
  );
}