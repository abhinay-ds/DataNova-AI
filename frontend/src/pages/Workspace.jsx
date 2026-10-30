import { Navigate } from "react-router-dom";
import MainLayout from "../components/layout/MainLayout";
import { useProject } from "../context/ProjectContext";

export default function Workspace() {
  const { activeProject, loading } = useProject();

  if (loading) {
    return (
      <div className="app-loading">
        <div className="app-loading-spinner" />
        <span>Restoring your workspace...</span>
      </div>
    );
  }

  // Workspace is entered only when the user chooses to open or create a project
  if (!activeProject) {
    return <Navigate to="/dashboard" replace />;
  }

  return <MainLayout />;
}
