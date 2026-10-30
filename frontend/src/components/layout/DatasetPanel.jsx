import {
  AlertCircle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Copy,
  Database,
  Eye,
  FileSpreadsheet,
  HardDrive,
  Lightbulb,
  MessageCircle,
  PanelBottom,
  PanelRight,
  Rows3,
  Sparkles,
  Table2,
  Upload,
  X,
} from "lucide-react";

import { useState } from "react";
import { useDataset } from "../../context/DatasetContext";

export default function DatasetPanel({
  layoutMode = "side",
  onToggleLayout,
  onClose,
}) {
  const {
    dataset,
    datasets = [],
    activeDatasetId,
    selectDataset,
    loading,
    error,
  } = useDataset();

  const [activeTab, setActiveTab] = useState("overview");

  /* =========================================================
     LOADING STATE
     ========================================================= */

  if (loading && !dataset) {
    return (
      <aside className="dataset-panel">
        <div className="dataset-panel-header">
          <div className="dataset-title-group">
            <div className="dataset-header-icon">
              <Database size={17} />
            </div>

            <div>
              <h2>Dataset</h2>
              <p>Loading active data...</p>
            </div>
          </div>
        </div>

        <div className="dataset-empty-state">
          <div className="dataset-empty-icon animate-pulse">
            <FileSpreadsheet size={34} />
          </div>

          <h3>Restoring dataset...</h3>

          <p>
            Profiling rows, columns and data quality.
          </p>
        </div>
      </aside>
    );
  }

  /* =========================================================
     EMPTY STATE
     ========================================================= */

  if (!dataset) {
    return (
      <aside className="dataset-panel">
        <div className="dataset-panel-header">
          <div className="dataset-title-group">
            <div className="dataset-header-icon">
              <Database size={17} />
            </div>

            <div>
              <h2>Dataset</h2>
              <p>{error ? "Error" : "Your active data"}</p>
            </div>
          </div>
        </div>

        <div className="dataset-empty-state">
          <div className="dataset-empty-icon">
            {error ? (
              <AlertCircle size={34} className="text-red-500" />
            ) : (
              <FileSpreadsheet size={34} />
            )}
          </div>

          <h3>{error ? "Failed to load dataset" : "No dataset uploaded"}</h3>

          <p>
            {error
              ? error
              : "Upload a CSV, Excel or JSON file to start analyzing your data with DataNova AI."}
          </p>

          {!error && (
            <div className="dataset-upload-hint">
              <Upload size={14} />
              <span>Upload from the workspace</span>
            </div>
          )}
        </div>
      </aside>
    );
  }

  /* =========================================================
     DATA
     ========================================================= */

  const profile = dataset.profile || {};
  const shape = profile.shape || {};

  const rows =
    shape.rows ??
    dataset.rows ??
    0;

  const columns =
    shape.columns ??
    dataset.columns ??
    0;

  const missingValues =
    profile.missing_values ??
    dataset.missing_values ??
    {};

  const totalMissingValues =
    typeof missingValues === "object" &&
    missingValues !== null
      ? Object.values(missingValues).reduce(
          (total, value) =>
            total + Number(value || 0),
          0
        )
      : Number(missingValues || 0);

  const duplicateRows =
    profile.duplicates ??
    profile.duplicate_rows ??
    dataset.duplicate_rows ??
    0;

  const filename =
    dataset.filename ||
    dataset.file_name ||
    "Uploaded Dataset";

  const extension = filename.includes(".")
    ? filename.split(".").pop().toUpperCase()
    : "DATA";

  const memoryUsage =
    profile.memory_usage ??
    dataset.memory_usage ??
    {};

  let memoryDisplay = "N/A";

  if (
    typeof memoryUsage === "object" &&
    memoryUsage !== null
  ) {
    if (memoryUsage.mb !== undefined) {
      memoryDisplay = `${memoryUsage.mb} MB`;
    } else if (memoryUsage.kb !== undefined) {
      memoryDisplay = `${memoryUsage.kb} KB`;
    } else if (memoryUsage.bytes !== undefined) {
      memoryDisplay = `${memoryUsage.bytes} bytes`;
    }
  } else if (memoryUsage) {
    memoryDisplay = String(memoryUsage);
  }

  const preview =
    dataset.preview ||
    dataset.summary?.preview ||
    dataset.summary?.data?.preview ||
    [];

  const columnNames =
    profile.columns ||
    profile.column_names ||
    dataset.column_names ||
    (preview.length > 0
      ? Object.keys(preview[0])
      : []);

  const qualityScore =
    dataset.quality?.score ??
    dataset.quality?.data?.score;

  const qualityRating =
    dataset.quality?.rating ??
    dataset.quality?.data?.rating;

  const recommendations =
    dataset.recommendations ||
    dataset.quality?.recommendations ||
    [];

  const formatNumber = (value) => {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "0";
    }

    return number.toLocaleString();
  };

  const getValuePreview = (value) => {
    if (value === null || value === undefined) {
      return "";
    }

    if (typeof value === "object") {
      return JSON.stringify(value);
    }

    return String(value);
  };

  /* =========================================================
     QUICK ACTIONS
     ========================================================= */

  const sendPrompt = (prompt) => {
    window.dispatchEvent(
      new CustomEvent("datanova:prompt", {
        detail: prompt,
      })
    );
  };

  const quickActions = [
    {
      label: "Preview data",
      icon: Eye,
      prompt: "Show me a preview of my dataset",
    },
    {
      label: "Generate summary",
      icon: Sparkles,
      prompt: "Give me an overview of my dataset",
    },
    {
      label: "Create a visualization",
      icon: BarChart3,
      prompt: "Create a useful visualization of my dataset",
    },
    {
      label: "Ask a question",
      icon: MessageCircle,
      prompt: "",
    },
  ];

  /* =========================================================
     RENDER
     ========================================================= */

  return (
    <aside className="dataset-panel">

      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="dataset-panel-header">

        <div className="dataset-title-group">

          <div className="dataset-header-icon">
            <Database size={17} />
          </div>

          <div>
            <h2>Dataset</h2>
            <p>Active data source</p>
          </div>

        </div>

        <div className="dataset-header-actions" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <div className="dataset-ready">
            <CheckCircle2 size={12} />
            Ready
          </div>

          {onToggleLayout && (
            <button
              type="button"
              className="icon-button"
              onClick={onToggleLayout}
              title={
                layoutMode === "bottom"
                  ? "Dock dataset panel to right"
                  : "Dock dataset panel to bottom"
              }
              aria-label="Toggle panel docking position"
              style={{ width: "26px", height: "26px", padding: 0 }}
            >
              {layoutMode === "bottom" ? (
                <PanelRight size={14} />
              ) : (
                <PanelBottom size={14} />
              )}
            </button>
          )}

          {onClose && (
            <button
              type="button"
              className="icon-button"
              onClick={onClose}
              title="Close dataset panel"
              aria-label="Close dataset panel"
              style={{ width: "26px", height: "26px", padding: 0 }}
            >
              <X size={14} />
            </button>
          )}
        </div>
      </div>


      {/* =====================================================
          CONTENT
          ===================================================== */}

      <div className="dataset-panel-content">

        {/* Switcher if multiple datasets exist */}
        {datasets.length > 1 && (
          <div className="dataset-switcher mb-3 px-1">
            <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider block mb-1">
              Select Dataset:
            </label>
            <select
              className="w-full text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-2.5 py-1.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
              value={activeDatasetId || dataset.id || ""}
              onChange={(e) => selectDataset(Number(e.target.value))}
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename} ({d.rows != null ? Number(d.rows).toLocaleString() : 0} rows)
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Dataset card */}

        <div className="active-dataset-card">

          <div className="active-dataset-main">

            <div className="active-dataset-icon">
              <FileSpreadsheet size={21} />
            </div>

            <div className="active-dataset-info">

              <span className="dataset-label">
                ACTIVE DATASET
              </span>

              <strong title={filename}>
                {filename}
              </strong>

              <div className="dataset-meta">

                <span className="file-badge">
                  {extension}
                </span>

                <span>
                  {formatNumber(rows)} rows
                </span>

                <span>•</span>

                <span>
                  {formatNumber(columns)} columns
                </span>

              </div>

              <small>
                {dataset.created_at
                  ? `Uploaded ${new Date(dataset.created_at).toLocaleDateString()}`
                  : "Uploaded just now"}
              </small>

            </div>

          </div>


          <button
            type="button"
            className="dataset-details-button"
            onClick={() =>
              setActiveTab("columns")
            }
          >
            View details
            <ArrowRight size={14} />
          </button>

        </div>


        {/* =================================================
            TABS
            ================================================= */}

        <div className="dataset-tabs">

          <button
            type="button"
            className={
              activeTab === "overview"
                ? "active"
                : ""
            }
            onClick={() =>
              setActiveTab("overview")
            }
          >
            Overview
          </button>

          <button
            type="button"
            className={
              activeTab === "columns"
                ? "active"
                : ""
            }
            onClick={() =>
              setActiveTab("columns")
            }
          >
            Columns
          </button>

          <button
            type="button"
            className={
              activeTab === "insights"
                ? "active"
                : ""
            }
            onClick={() =>
              setActiveTab("insights")
            }
          >
            Insights
          </button>

        </div>


        {/* =================================================
            OVERVIEW
            ================================================= */}

        {activeTab === "overview" && (
          <>

            <div className="dataset-stat-grid">

              <div className="dataset-stat-card rows-stat">
                <div className="dataset-stat-top">
                  <Rows3 size={15} />
                </div>

                <strong>
                  {formatNumber(rows)}
                </strong>

                <span>Rows</span>
              </div>


              <div className="dataset-stat-card columns-stat">
                <div className="dataset-stat-top">
                  <Table2 size={15} />
                </div>

                <strong>
                  {formatNumber(columns)}
                </strong>

                <span>Columns</span>
              </div>


              <div className="dataset-stat-card missing-stat">
                <div className="dataset-stat-top">
                  <AlertCircle size={15} />
                </div>

                <strong>
                  {formatNumber(totalMissingValues)}
                </strong>

                <span>Missing</span>
              </div>


              <div className="dataset-stat-card duplicate-stat">
                <div className="dataset-stat-top">
                  <Copy size={15} />
                </div>

                <strong>
                  {formatNumber(duplicateRows)}
                </strong>

                <span>Duplicates</span>
              </div>

            </div>


            {/* Quick actions */}

            <section className="dataset-section">

              <div className="dataset-section-heading">
                <h3>Quick actions</h3>
              </div>


              <div className="quick-actions">

                {quickActions.map(
                  ({
                    label,
                    icon: Icon,
                    prompt,
                  }) => (
                    <button
                      key={label}
                      type="button"
                      className="quick-action"
                      onClick={() => {
                        if (prompt) {
                          sendPrompt(prompt);
                        }
                      }}
                    >
                      <span className="quick-action-icon">
                        <Icon size={15} />
                      </span>

                      <span>
                        {label}
                      </span>

                      <ArrowRight
                        size={14}
                        className="quick-action-arrow"
                      />
                    </button>
                  )
                )}

              </div>

            </section>


            {/* Memory */}

            <div className="dataset-memory">

              <div className="dataset-memory-icon">
                <HardDrive size={15} />
              </div>

              <div>
                <span>
                  MEMORY USAGE
                </span>

                <strong>
                  {memoryDisplay}
                </strong>
              </div>

            </div>

          </>
        )}


        {/* =================================================
            COLUMNS
            ================================================= */}

        {activeTab === "columns" && (
          <section className="dataset-section">

            <div className="dataset-section-heading">
              <h3>Dataset columns</h3>

              <span>
                {columnNames.length} fields
              </span>
            </div>


            {columnNames.length > 0 ? (
              <div className="dataset-column-list">

                {columnNames.map(
                  (column, index) => (
                    <div
                      key={column}
                      className="dataset-column-item"
                    >
                      <span className="column-number">
                        {String(index + 1).padStart(
                          2,
                          "0"
                        )}
                      </span>

                      <span title={column}>
                        {column}
                      </span>
                    </div>
                  )
                )}

              </div>
            ) : (
              <div className="dataset-empty-mini">
                No column information available.
              </div>
            )}

          </section>
        )}


        {/* =================================================
            INSIGHTS
            ================================================= */}

        {activeTab === "insights" && (
          <section className="dataset-section">

            <div className="dataset-section-heading">
              <h3>Dataset insights</h3>
              <Lightbulb size={15} />
            </div>


            {qualityScore !== undefined && (
              <div className="quality-card">

                <div className="quality-top">

                  <span>
                    Data quality
                  </span>

                  <strong>
                    {qualityScore}
                  </strong>

                </div>

                <div className="quality-bar">
                  <div
                    style={{
                      width: `${Math.max(
                        0,
                        Math.min(
                          100,
                          Number(qualityScore) || 0
                        )
                      )}%`,
                    }}
                  />
                </div>

                {qualityRating && (
                  <span className="quality-rating">
                    {qualityRating}
                  </span>
                )}

              </div>
            )}


            {recommendations.length > 0 ? (
              <div className="insight-list">

                {recommendations
                  .slice(0, 5)
                  .map((item, index) => (
                    <div
                      key={index}
                      className="insight-item"
                    >
                      <Sparkles size={13} />
                      <span>{item}</span>
                    </div>
                  ))}

              </div>
            ) : (
              <div className="dataset-empty-mini">
                No additional insights available yet.
              </div>
            )}

          </section>
        )}


        {/* =================================================
            PREVIEW
            ================================================= */}

        {preview.length > 0 && (
          <section className="dataset-section preview-section">

            <div className="dataset-section-heading">
              <h3>Data preview</h3>

              <span>
                First {Math.min(preview.length, 5)} rows
              </span>
            </div>

            <div className="dataset-preview-table">

              <table>

                <thead>
                  <tr>
                    {Object.keys(preview[0]).map(
                      (column) => (
                        <th
                          key={column}
                          title={column}
                        >
                          {column}
                        </th>
                      )
                    )}
                  </tr>
                </thead>

                <tbody>

                  {preview
                    .slice(0, 5)
                    .map((row, rowIndex) => (
                      <tr key={rowIndex}>

                        {Object.values(row).map(
                          (
                            value,
                            columnIndex
                          ) => (
                            <td
                              key={columnIndex}
                              title={getValuePreview(
                                value
                              )}
                            >
                              {getValuePreview(
                                value
                              )}
                            </td>
                          )
                        )}

                      </tr>
                    ))}

                </tbody>

              </table>

            </div>

          </section>
        )}

      </div>

    </aside>
  );
}