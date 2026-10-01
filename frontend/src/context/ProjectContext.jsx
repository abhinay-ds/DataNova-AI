import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  createProject as apiCreateProject,
  getActiveProject,
  getProjects,
  setActiveProject as saveActiveProject,
} from "../services/api";

import { useAuth } from "./AuthContext";

const ProjectContext = createContext(null);

export function ProjectProvider({ children }) {
  const { isAuthenticated, loading: authLoading } = useAuth();

  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProjectState] =
    useState(getActiveProject);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadProjects() {
    if (!isAuthenticated) {
      setProjects([]);
      setActiveProjectState(null);
      setLoading(false);
      setError("");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await getProjects();

      const projectList = Array.isArray(data)
        ? data
        : data?.projects || [];

      setProjects(projectList);

      const storedProject = getActiveProject();

      if (storedProject) {
        const stillExists = projectList.some(
          (project) => project.id === storedProject.id
        );

        if (stillExists) {
          const freshProject = projectList.find(
            (project) => project.id === storedProject.id
          );

          setActiveProjectState(freshProject);
          saveActiveProject(freshProject);
          return;
        }
      }

      if (projectList.length > 0) {
        setActiveProjectState(projectList[0]);
        saveActiveProject(projectList[0]);
      } else {
        setActiveProjectState(null);
        saveActiveProject(null);
      }
    } catch (err) {
      console.error("Failed to load projects:", err);

      setError(
        err?.message || "Unable to load your projects."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (authLoading) {
      return;
    }

    loadProjects();
  }, [authLoading, isAuthenticated]);

  function selectProject(project) {
    setActiveProjectState(project);
    saveActiveProject(project);
  }

  async function createProject(name, description = "") {
    const project = await apiCreateProject(
      name,
      description
    );

    setProjects((current) => [
      project,
      ...current,
    ]);

    setActiveProjectState(project);
    saveActiveProject(project);

    return project;
  }

  function clearProject() {
    setActiveProjectState(null);
    saveActiveProject(null);
  }

  return (
    <ProjectContext.Provider
      value={{
        projects,
        activeProject,
        loading,
        error,
        loadProjects,
        selectProject,
        createProject,
        clearProject,
      }}
    >
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  const context = useContext(ProjectContext);

  if (!context) {
    throw new Error(
      "useProject must be used inside ProjectProvider"
    );
  }

  return context;
}