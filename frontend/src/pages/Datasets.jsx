import {
  CheckCircle2,
  Database,
  FileSpreadsheet,
  Plus,
  Sparkles,
  Trash2,
  Upload,
} from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useDataset } from "../context/DatasetContext";
import { useProject } from "../context/ProjectContext";
import { deleteDataset } from "../services/api";
import BrandLogo from "../components/BrandLogo";

export default function Datasets() {
  const navigate = useNavigate();
  const { activeProject } = useProject();
  const {
    datasets = [],
    dataset,
    activeDatasetId,
    selectDataset,
    loadProjectDatasets,
    loading,
  } = useDataset();

  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (datasetId, filename) => {
    if (!activeProject?.id) return;
    const confirmed = window.confirm(
      `Are you sure you want to delete dataset "${filename}"?`
    );
    if (!confirmed) return;

    try {
      setDeletingId(datasetId);
      await deleteDataset(activeProject.id, datasetId);
      await loadProjectDatasets(activeProject.id);
    } catch (err) {
      console.error("Failed to delete dataset:", err);
      alert(err?.message || "Failed to delete dataset.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleSelectAndAnalyze = async (datasetId) => {
    await selectDataset(datasetId);
    navigate("/workspace");
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
          <Database size={28} />
        </div>

        <span className="section-kicker">Datasets</span>
        <h1>Project Datasets</h1>
        <p>
          {activeProject
            ? `Datasets for "${activeProject.name}". Select a dataset to activate it in the AI workspace.`
            : "Select a project to view and manage datasets."}
        </p>

        {loading && datasets.length === 0 ? (
          <div className="empty-card">
            <FileSpreadsheet size={28} className="animate-pulse" />
            <strong>Loading datasets...</strong>
            <span>Fetching datasets for the active project.</span>
          </div>
        ) : datasets.length > 0 ? (
          <div className="datasets-list" style={{ marginTop: "24px" }}>
            {datasets.map((d) => {
              const isActive =
                dataset?.id === d.id ||
                activeDatasetId === d.id ||
                dataset?.dataset_id === d.id;

              const fileType = d.file_type
                ? d.file_type.toUpperCase()
                : d.filename?.includes(".")
                ? d.filename.split(".").pop().toUpperCase()
                : "DATA";

              const rows =
                d.rows != null ? Number(d.rows).toLocaleString() : "—";
              const cols =
                d.columns != null ? Number(d.columns).toLocaleString() : "—";
              const dateStr = d.created_at
                ? new Date(d.created_at).toLocaleDateString()
                : "Recently";

              return (
                <div
                  key={d.id}
                  className="dataset-list-card"
                  style={{
                    borderLeft: isActive
                      ? "3px solid var(--dn-primary)"
                      : "1px solid var(--dn-border)",
                    marginBottom: "12px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <div style={{ color: "var(--dn-primary)" }}>
                      <FileSpreadsheet size={24} />
                    </div>

                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "8px",
                          marginBottom: "4px",
                        }}
                      >
                        <strong>{d.filename}</strong>
                        <span
                          style={{
                            padding: "2px 6px",
                            borderRadius: "4px",
                            fontSize: "10px",
                            fontWeight: "600",
                            background: "var(--dn-primary-soft)",
                            color: "var(--dn-primary)",
                          }}
                        >
                          {fileType}
                        </span>

                        {isActive && (
                          <span
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "3px",
                              padding: "2px 6px",
                              borderRadius: "4px",
                              fontSize: "10px",
                              fontWeight: "600",
                              background: "rgba(16, 185, 129, 0.12)",
                              color: "#10b981",
                            }}
                          >
                            <CheckCircle2 size={11} />
                            Active
                          </span>
                        )}
                      </div>

                      <span style={{ fontSize: "12px", color: "var(--dn-text-muted)" }}>
                        {rows} rows • {cols} columns • Uploaded {dateStr}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    {isActive ? (
                      <button
                        className="primary-button"
                        onClick={() => navigate("/workspace")}
                      >
                        Analyze
                      </button>
                    ) : (
                      <button
                        className="ghost-button"
                        onClick={() => handleSelectAndAnalyze(d.id)}
                      >
                        Make Active
                      </button>
                    )}

                    <button
                      className="ghost-button"
                      style={{ padding: "8px", color: "#ef4444" }}
                      disabled={deletingId === d.id}
                      onClick={() => handleDelete(d.id, d.filename)}
                      title="Delete dataset"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="empty-card">
            <Upload size={28} />
            <strong>No datasets uploaded</strong>
            <span>
              Upload a CSV, Excel or JSON dataset from the workspace to get started.
            </span>
            <button
              className="primary-button"
              onClick={() => navigate(activeProject ? "/workspace" : "/projects")}
            >
              {activeProject ? "Go to Workspace" : "View Projects"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
