const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "datanova_access_token";
const USER_KEY = "datanova_user";
const PROJECT_KEY = "datanova_project";

let refreshPromise = null;

async function handleResponse(response) {
  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(`Server returned ${response.status}`);
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.message ||
      `Request failed with status ${response.status}`
    );
  }

  return data;
}

export function getToken() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token || token === "null" || token === "undefined" || !token.trim()) {
    return null;
  }
  return token.trim();
}

function authHeaders(extraHeaders = {}) {
  const token = getToken();

  return {
    ...extraHeaders,
    ...(token
      ? {
          Authorization: `Bearer ${token}`,
        }
      : {}),
  };
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(PROJECT_KEY);
}

export async function refreshToken() {
  const token = getToken();
  if (!token) {
    throw new Error("No token available to refresh.");
  }

  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Token refresh rejected with status ${response.status}`);
      }

      const data = await response.json();
      if (!data?.access_token) {
        throw new Error("No access token in refresh response.");
      }

      localStorage.setItem(TOKEN_KEY, data.access_token);
      if (data.user) {
        localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      }

      return data;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function authFetch(url, options = {}, isRetry = false) {
  const mergedHeaders = authHeaders(options.headers || {});
  const response = await fetch(url, {
    ...options,
    headers: mergedHeaders,
  });

  if (response.status === 401) {
    if (!isRetry && getToken()) {
      try {
        await refreshToken();
        return await authFetch(url, options, true);
      } catch {
        // Refresh failed
      }
    }

    logout();
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent("datanova:auth-expired"));
      if (window.location && window.location.pathname !== "/login") {
        window.location.href = "/login?expired=1";
      }
    }
    throw new Error("Invalid or expired authentication token. Please sign in again.");
  }

  return response;
}

/* ---------------- AUTH ---------------- */

export async function signup(email, password, fullName = null) {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName,
    }),
  });

  const data = await handleResponse(response);

  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  localStorage.removeItem(PROJECT_KEY);

  return data;
}

export async function login(email, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await handleResponse(response);

  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  localStorage.removeItem(PROJECT_KEY);

  return data;
}

export async function demoLogin() {
  const response = await fetch(`${API_BASE_URL}/auth/demo`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await handleResponse(response);

  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  localStorage.removeItem(PROJECT_KEY);

  return data;
}

export async function guestLogin() {
  const response = await fetch(`${API_BASE_URL}/auth/guest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  const data = await handleResponse(response);

  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  localStorage.removeItem(PROJECT_KEY);

  return data;
}

export async function getCurrentUser() {
  const response = await authFetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
  });

  return handleResponse(response);
}

export function getStoredUser() {
  try {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  return Boolean(getToken());
}

/* ---------------- PROJECTS ---------------- */

export async function getProjects() {
  const response = await authFetch(`${API_BASE_URL}/projects`, {
    method: "GET",
  });

  return handleResponse(response);
}

export async function getProject(projectId) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function createProject(name, description = "") {
  const response = await authFetch(`${API_BASE_URL}/projects`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      description,
    }),
  });

  const data = await handleResponse(response);

  localStorage.setItem(PROJECT_KEY, JSON.stringify(data));

  return data;
}

export async function updateProject(
  projectId,
  name,
  description = ""
) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
        description,
      }),
    }
  );

  return handleResponse(response);
}

export async function deleteProject(projectId) {
  const response = await authFetch(`${API_BASE_URL}/projects/${projectId}`, {
    method: "DELETE",
  });

  if (response.status === 204) {
    const current = getActiveProject();
    if (current && current.id === projectId) {
      setActiveProject(null);
    }
    return true;
  }

  return handleResponse(response);
}

export function setActiveProject(project) {
  if (!project) {
    localStorage.removeItem(PROJECT_KEY);
    return;
  }

  localStorage.setItem(
    PROJECT_KEY,
    JSON.stringify(project)
  );
}

export function getActiveProject() {
  try {
    const project = localStorage.getItem(PROJECT_KEY);
    return project ? JSON.parse(project) : null;
  } catch {
    return null;
  }
}

/* ---------------- DATASETS ---------------- */

export async function uploadDataset(
  file,
  sessionId,
  projectId
) {
  if (!file) {
    throw new Error("No file selected.");
  }

  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  const formData = new FormData();

  formData.append("file", file);

  const response = await authFetch(
    `${API_BASE_URL}/upload/?session_id=${encodeURIComponent(
      sessionId
    )}&project_id=${encodeURIComponent(projectId)}`,
    {
      method: "POST",
      body: formData,
    }
  );

  return handleResponse(response);
}

export async function getProjectDatasets(projectId) {
  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/datasets`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function getDataset(
  projectId,
  datasetId
) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/datasets/${datasetId}`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function getDatasetAnalysis(
  projectId,
  datasetId,
  sessionId = null
) {
  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  if (!datasetId) {
    throw new Error("Dataset ID is required.");
  }

  const query = sessionId
    ? `?session_id=${encodeURIComponent(sessionId)}`
    : "";

  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/datasets/${datasetId}/analysis${query}`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function deleteDataset(
  projectId,
  datasetId
) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/datasets/${datasetId}`,
    {
      method: "DELETE",
    }
  );

  if (response.status === 204) {
    return true;
  }

  return handleResponse(response);
}

/* ---------------- CONVERSATIONS ---------------- */

export async function getProjectConversations(projectId) {
  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/conversations`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function getConversationMessages(projectId, conversationId) {
  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  if (!conversationId) {
    throw new Error("Conversation ID is required.");
  }

  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/conversations/${conversationId}/messages`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

/* ---------------- CHAT ---------------- */

export async function sendMessage(
  message,
  sessionId,
  projectId = null,
  conversationId = null
) {
  if (!message || !message.trim()) {
    throw new Error("Message cannot be empty.");
  }

  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  const payload = {
    message: message.trim(),
    session_id: sessionId,
  };

  if (projectId != null) {
    payload.project_id = Number(projectId);
  }

  if (conversationId != null) {
    payload.conversation_id = Number(conversationId);
  }

  const response = await authFetch(
    `${API_BASE_URL}/chat/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  return handleResponse(response);
}

/* ---------------- REPORTS & TASKS ---------------- */

export async function generateReport(projectId, datasetId = null) {
  const payload = datasetId ? { dataset_id: Number(datasetId) } : {};

  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/reports/generate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  return handleResponse(response);
}

export async function getProjectReports(projectId) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/reports`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function fetchProjectReportHtml(projectId, reportId) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/reports/${reportId}/view`,
    {
      method: "GET",
    }
  );

  if (!response.ok) {
    let errorMsg = `Server returned ${response.status}`;
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errData.message || errorMsg;
    } catch {
      // not json
    }
    throw new Error(errorMsg);
  }

  return response.text();
}

export async function fetchProjectReportBlob(projectId, reportId) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/reports/${reportId}/download`,
    {
      method: "GET",
    }
  );

  if (!response.ok) {
    let errorMsg = `Server returned ${response.status}`;
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errData.message || errorMsg;
    } catch {
      // not json
    }
    throw new Error(errorMsg);
  }

  return response.blob();
}

export async function getProjectTasks(projectId) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/tasks`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function getProjectAnalyses(projectId) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/analyses`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

export async function getProjectCharts(projectId) {
  const response = await authFetch(
    `${API_BASE_URL}/projects/${projectId}/charts`,
    {
      method: "GET",
    }
  );

  return handleResponse(response);
}

/* ---------------- SYSTEM ---------------- */

export async function checkBackend() {
  const response = await fetch(
    `${API_BASE_URL}/health`
  );

  return handleResponse(response);
}

export async function testLLM() {
  const response = await fetch(
    `${API_BASE_URL}/test-llm`
  );

  return handleResponse(response);
}

export async function getBackendInfo() {
  const response = await fetch(API_BASE_URL);

  return handleResponse(response);
}

export { API_BASE_URL };
