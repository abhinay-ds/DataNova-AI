import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getDatasetAnalysis,
  getProjectDatasets,
} from "../services/api";
import { useProject } from "./ProjectContext";

const DatasetContext = createContext(null);

export function DatasetProvider({ children }) {
  const { activeProject } = useProject();

  const [dataset, setDatasetState] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [activeDatasetId, setActiveDatasetId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const activeProjectIdRef = useRef(activeProject?.id);

  useEffect(() => {
    activeProjectIdRef.current = activeProject?.id;
  }, [activeProject?.id]);

  // =====================================================
  // LOAD PROJECT DATASETS & RESTORE ACTIVE DATASET
  // =====================================================
  const loadProjectDatasets = useCallback(
    async (projectId, preferredDatasetId = null) => {
      if (!projectId) {
        setDatasetState(null);
        setDatasets([]);
        setActiveDatasetId(null);
        setError(null);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        // Clear active dataset while switching projects to avoid cross-project contamination
        setDatasetState(null);

        const datasetList = await getProjectDatasets(projectId);

        // Guard against race conditions if project changed mid-request
        if (activeProjectIdRef.current !== projectId) return;

        const list = Array.isArray(datasetList)
          ? datasetList
          : datasetList?.datasets || [];

        setDatasets(list);

        if (list.length === 0) {
          setActiveDatasetId(null);
          setDatasetState(null);
          setLoading(false);
          return;
        }

        // Determine target dataset: preferred or latest (list is ordered by created_at DESC)
        let target = null;
        if (preferredDatasetId) {
          target = list.find((d) => d.id === preferredDatasetId);
        }
        if (!target) {
          target = list[0];
        }

        setActiveDatasetId(target.id);

        const sessionId = localStorage.getItem("datanova_session_id") || "default";
        const analysisData = await getDatasetAnalysis(
          projectId,
          target.id,
          sessionId
        );

        if (activeProjectIdRef.current !== projectId) return;

        setDatasetState(analysisData);
      } catch (err) {
        if (activeProjectIdRef.current !== projectId) return;
        console.error("Failed to load project datasets:", err);
        setError(err?.message || "Failed to load project datasets.");
        setDatasetState(null);
      } finally {
        if (activeProjectIdRef.current === projectId) {
          setLoading(false);
        }
      }
    },
    []
  );

  // Reload datasets when active project changes or page refreshes
  useEffect(() => {
    let isCancelled = false;

    if (!activeProject?.id) {
      setDatasetState(null);
      setDatasets([]);
      setActiveDatasetId(null);
      setError(null);
      return;
    }

    loadProjectDatasets(activeProject.id);

    return () => {
      isCancelled = true;
    };
  }, [activeProject?.id, loadProjectDatasets]);

  // =====================================================
  // SELECT SPECIFIC DATASET
  // =====================================================
  const selectDataset = useCallback(
    async (datasetId) => {
      if (!activeProject?.id || !datasetId) return;

      try {
        setLoading(true);
        setError(null);

        const sessionId = localStorage.getItem("datanova_session_id") || "default";
        const analysisData = await getDatasetAnalysis(
          activeProject.id,
          datasetId,
          sessionId
        );

        setActiveDatasetId(datasetId);
        setDatasetState(analysisData);
      } catch (err) {
        console.error("Failed to select dataset:", err);
        setError(err?.message || "Failed to load selected dataset.");
      } finally {
        setLoading(false);
      }
    },
    [activeProject?.id]
  );

  // =====================================================
  // MANUAL SET DATASET (e.g. from file upload)
  // =====================================================
  const setDataset = useCallback(
    (newDataset) => {
      setDatasetState(newDataset);
      if (newDataset?.id || newDataset?.dataset_id) {
        const id = newDataset.id || newDataset.dataset_id;
        setActiveDatasetId(id);
      }
      // Re-fetch project datasets list to include newly uploaded file
      if (activeProject?.id) {
        getProjectDatasets(activeProject.id)
          .then((list) => {
            if (Array.isArray(list)) {
              setDatasets(list);
            }
          })
          .catch((err) => {
            console.warn("Could not refresh dataset list after upload:", err);
          });
      }
    },
    [activeProject?.id]
  );

  const clearDataset = useCallback(() => {
    setDatasetState(null);
    setActiveDatasetId(null);
  }, []);

  return (
    <DatasetContext.Provider
      value={{
        dataset,
        setDataset,
        datasets,
        setDatasets,
        activeDatasetId,
        setActiveDatasetId,
        loading,
        error,
        loadProjectDatasets,
        selectDataset,
        clearDataset,
      }}
    >
      {children}
    </DatasetContext.Provider>
  );
}

export function useDataset() {
  const context = useContext(DatasetContext);

  if (!context) {
    throw new Error("useDataset must be used inside DatasetProvider");
  }

  return context;
}