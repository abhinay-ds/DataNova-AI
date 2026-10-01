const API_BASE_URL = "http://127.0.0.1:8000";

const TOKEN_KEY = "datanova_access_token";
const USER_KEY = "datanova_user";
const PROJECT_KEY = "datanova_project";

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

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
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

  return data;
}

export async function getCurrentUser() {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: authHeaders(),
  });

  return handleResponse(response);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(PROJECT_KEY);
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
  const response = await fetch(`${API_BASE_URL}/projects`, {
    method: "GET",
    headers: authHeaders(),
  });

  return handleResponse(response);
}

export async function getProject(projectId) {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}`,
    {
      method: "GET",
      headers: authHeaders(),
    }
  );

  return handleResponse(response);
}

export async function createProject(name, description = "") {
  const response = await fetch(`${API_BASE_URL}/projects`, {
    method: "POST",
    headers: authHeaders({
      "Content-Type": "application/json",
    }),
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
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}`,
    {
      method: "PATCH",
      headers: authHeaders({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({
        name,
        description,
      }),
    }
  );

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

  const response = await fetch(
    `${API_BASE_URL}/upload/?session_id=${encodeURIComponent(
      sessionId
    )}&project_id=${encodeURIComponent(projectId)}`,
    {
      method: "POST",
      headers: authHeaders(),
      body: formData,
    }
  );

  return handleResponse(response);
}

export async function getProjectDatasets(projectId) {
  if (!projectId) {
    throw new Error("Project ID is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/datasets`,
    {
      method: "GET",
      headers: authHeaders(),
    }
  );

  return handleResponse(response);
}

export async function getDataset(
  projectId,
  datasetId
) {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/datasets/${datasetId}`,
    {
      method: "GET",
      headers: authHeaders(),
    }
  );

  return handleResponse(response);
}

export async function deleteDataset(
  projectId,
  datasetId
) {
  const response = await fetch(
    `${API_BASE_URL}/projects/${projectId}/datasets/${datasetId}`,
    {
      method: "DELETE",
      headers: authHeaders(),
    }
  );

  if (response.status === 204) {
    return true;
  }

  return handleResponse(response);
}

/* ---------------- CHAT ---------------- */

export async function sendMessage(
  message,
  sessionId
) {
  if (!message || !message.trim()) {
    throw new Error("Message cannot be empty.");
  }

  if (!sessionId) {
    throw new Error("Session ID is required.");
  }

  const response = await fetch(
    `${API_BASE_URL}/chat/`,
    {
      method: "POST",
      headers: authHeaders({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({
        message: message.trim(),
        session_id: sessionId,
      }),
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