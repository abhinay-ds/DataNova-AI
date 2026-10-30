import {
  Download,
  ExternalLink,
  FileBarChart2,
  FileSpreadsheet,
  Loader2,
  Plus,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useDataset } from "../context/DatasetContext";
import { useProject } from "../context/ProjectContext";
import {
  fetchProjectReportBlob,
  fetchProjectReportHtml,
  generateReport,
  getProjectReports,
} from "../services/api";
import BrandLogo from "../components/BrandLogo";

export default function Reports() {
  const navigate = useNavigate();
  const { activeProject } = useProject();
  const { datasets = [], dataset, activeDatasetId } = useDataset();

  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [error, setError] = useState(null);
  const [actionLoadingId, setActionLoadingId] = useState(null);

  // Initialize selected dataset id when datasets or active dataset change
  useEffect(() => {
    if (activeDatasetId) {
      setSelectedDatasetId(String(activeDatasetId));
    } else if (dataset?.id) {
      setSelectedDatasetId(String(dataset.id));
    } else if (datasets.length > 0) {
      setSelectedDatasetId(String(datasets[0].id));
    }
  }, [activeDatasetId, dataset, datasets]);

  const loadReports = async () => {
    if (!activeProject?.id) {
      setReports([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getProjectReports(activeProject.id);
      setReports(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load reports:", err);
      setError(err?.message || "Failed to load project reports.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, [activeProject?.id]);

  const handleGenerate = async () => {
    if (!activeProject?.id) {
      alert("Please select a project first.");
      return;
    }

    try {
      setGenerating(true);
      setError(null);
      const dId = selectedDatasetId ? Number(selectedDatasetId) : null;
      await generateReport(activeProject.id, dId);
      await loadReports();
    } catch (err) {
      console.error("Failed to generate report:", err);
      setError(err?.message || "Failed to generate report.");
    } finally {
      setGenerating(false);
    }
  };

  // Safe, authenticated report viewing using blob/object-URL
  const handleViewReport = async (reportId) => {
    if (!activeProject?.id) return;
    try {
      setActionLoadingId(`view_${reportId}`);
      setError(null);
      const htmlContent = await fetchProjectReportHtml(activeProject.id, reportId);
      const blob = new Blob([htmlContent], { type: "text/html" });
      const objectUrl = URL.createObjectURL(blob);

      // Open object URL in a new tab
      const newTab = window.open(objectUrl, "_blank");
      if (!newTab) {
        // Pop-up blocked fallback
        window.location.href = objectUrl;
      }

      // Revoke the object URL after allowing the browser to load it
      setTimeout(() => {
        URL.revokeObjectURL(objectUrl);
      }, 60000);
    } catch (err) {
      console.error("Failed to view report:", err);
      setError(err?.message || "Failed to open report.");
    } finally {
      setActionLoadingId(null);
    }
  };

  // Safe, authenticated report downloading using blob/object-URL
  const handleDownloadReport = async (reportId, filename) => {
    if (!activeProject?.id) return;
    try {
      setActionLoadingId(`dl_${reportId}`);
      setError(null);
      const blob = await fetchProjectReportBlob(activeProject.id, reportId);
      const objectUrl = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = filename || "datanova_report.html";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Revoke the object URL
      setTimeout(() => {
        URL.revokeObjectURL(objectUrl);
      }, 10000);
    } catch (err) {
      console.error("Failed to download report:", err);
      setError(err?.message || "Failed to download report.");
    } finally {
      setActionLoadingId(null);
    }
  };

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
          <FileBarChart2 size={28} />
        </div>

        <span className="section-kicker">Reports</span>
        <h1>Analysis Reports</h1>
        <p>
          {activeProject
            ? `Generated comprehensive reports for project "${activeProject.name}".`
            : "Select a project to view and generate reports."}
        </p>

        {/* Action Bar */}
        {activeProject && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "12px",
              margin: "20px 0",
              padding: "16px",
              background: "var(--dn-surface, #ffffff)",
              border: "1px solid var(--dn-border, #e5e7eb)",
              borderRadius: "10px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
              <span style={{ fontSize: "13px", fontWeight: "600", color: "var(--dn-text-muted)" }}>
                Dataset:
              </span>
              {datasets.length > 0 ? (
                <select
                  value={selectedDatasetId}
                  onChange={(e) => setSelectedDatasetId(e.target.value)}
                  style={{
                    padding: "6px 12px",
                    borderRadius: "6px",
                    border: "1px solid var(--dn-border, #e5e7eb)",
                    background: "var(--dn-bg, #f8fafc)",
                    fontSize: "13px",
                  }}
                >
                  {datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.filename} ({d.rows || 0} rows)
                    </option>
                  ))}
                </select>
              ) : (
                <span style={{ fontSize: "13px", color: "var(--dn-text-muted)" }}>
                  No datasets uploaded yet
                </span>
              )}
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <button
                className="ghost-button"
                onClick={loadReports}
                disabled={loading || generating}
                title="Refresh reports"
                style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
              >
                <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
                Refresh
              </button>

              <button
                className="primary-button"
                onClick={handleGenerate}
                disabled={generating || datasets.length === 0}
                style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}
              >
                {generating ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <Plus size={16} />
                    Generate Report
                  </>
                )}
              </button>
            </div>
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

        {/* Content list or empty state */}
        {loading && reports.length === 0 ? (
          <div className="empty-card">
            <Loader2 size={28} className="animate-spin" />
            <strong>Loading reports...</strong>
            <span>Fetching generated reports for this project.</span>
          </div>
        ) : reports.length > 0 ? (
          <div className="reports-list" style={{ marginTop: "16px" }}>
            {reports.map((r) => {
              const isViewing = actionLoadingId === `view_${r.id}`;
              const isDownloading = actionLoadingId === `dl_${r.id}`;
              const dateStr = r.created_at
                ? new Date(r.created_at).toLocaleString()
                : "Recently";

              return (
                <div
                  key={r.id}
                  className="dataset-list-card"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "16px",
                    marginBottom: "12px",
                    border: "1px solid var(--dn-border, #e5e7eb)",
                    borderRadius: "10px",
                    background: "var(--dn-surface, #ffffff)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                    <div style={{ color: "#2563eb" }}>
                      <FileBarChart2 size={26} />
                    </div>

                    <div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "8px",
                          marginBottom: "4px",
                        }}
                      >
                        <strong>{r.title}</strong>
                        <span
                          style={{
                            padding: "2px 6px",
                            borderRadius: "4px",
                            fontSize: "10px",
                            fontWeight: "600",
                            background: "rgba(37, 99, 235, 0.1)",
                            color: "#2563eb",
                          }}
                        >
                          HTML
                        </span>
                      </div>

                      <div style={{ fontSize: "12px", color: "var(--dn-text-muted)" }}>
                        Generated {dateStr}
                        {r.dataset_name ? ` • Dataset: ${r.dataset_name}` : ""}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <button
                      className="ghost-button"
                      disabled={isViewing || isDownloading}
                      onClick={() => handleViewReport(r.id)}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      {isViewing ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <ExternalLink size={14} />
                      )}
                      View
                    </button>

                    <button
                      className="primary-button"
                      disabled={isViewing || isDownloading}
                      onClick={() => handleDownloadReport(r.id, r.filename)}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      {isDownloading ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Download size={14} />
                      )}
                      Download
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="empty-card">
            <FileBarChart2 size={32} />
            <strong>No reports generated yet</strong>
            <span>
              {datasets.length > 0
                ? "Click 'Generate Report' above to profile and analyze your dataset into an executive HTML report."
                : "Upload a dataset first from the workspace or Datasets page to generate reports."}
            </span>
            {datasets.length === 0 && (
              <button
                className="primary-button"
                onClick={() => navigate(activeProject ? "/workspace" : "/projects")}
                style={{ marginTop: "12px" }}
              >
                <Plus size={16} /> {activeProject ? "Go to Workspace" : "View Projects"}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
