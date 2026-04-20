// Thin fetch wrapper for the OpenShelf backend.
//
// Base URL is empty in dev — we rely on Vite's proxy (see vite.config.js)
// to forward /auth, /listings, /conversations, etc. to FastAPI on :8000.
// In a built deploy where frontend and backend share an origin, empty
// base URL still works. Override via VITE_API_URL if they're split.

const BASE_URL = import.meta.env.VITE_API_URL ?? "";

const TOKEN_KEY = "openshelf.token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  // 204 No Content
  if (res.status === 204) return null;

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail = (data && data.detail) || res.statusText;
    throw new ApiError(
      typeof detail === "string" ? detail : "Request failed",
      res.status,
      detail,
    );
  }
  return data;
}

export const api = {
  get: (path, opts) => request(path, { ...opts, method: "GET" }),
  post: (path, body, opts) => request(path, { ...opts, method: "POST", body }),
  put: (path, body, opts) => request(path, { ...opts, method: "PUT", body }),
  delete: (path, opts) => request(path, { ...opts, method: "DELETE" }),
};

// ============================================================
//  Typed endpoint helpers
//  Group by resource; mirrors the FastAPI router layout.
// ============================================================

export const authApi = {
  login: (email, password) =>
    api.post("/auth/login", { email, password }, { auth: false }),
  register: (payload) => api.post("/auth/register", payload, { auth: false }),
  me: () => api.get("/auth/me"),
};

export const coursesApi = {
  list: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api.get(`/courses/${q ? `?${q}` : ""}`);
  },
  get: (id) => api.get(`/courses/${id}`),
  withTextbooks: (id) => api.get(`/courses/${id}/textbooks`),
  enrollments: (userId) => api.get(`/courses/user/${userId}/enrollments`),
  search: (q, universityId) => {
    const params = new URLSearchParams({ q });
    if (universityId) params.set("university_id", String(universityId));
    return api.get(`/courses/?${params}`);
  },
};

export const textbooksApi = {
  list: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return api.get(`/textbooks/${q ? `?${q}` : ""}`);
  },
  get: (id) => api.get(`/textbooks/${id}`),
  byIsbn: (isbn) => api.get(`/textbooks/isbn/${isbn}`),
};

export const listingsApi = {
  list: (params = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).filter(([, v]) => v !== undefined && v !== "")
      ),
    ).toString();
    return api.get(`/listings/${q ? `?${q}` : ""}`);
  },
  get: (id) => api.get(`/listings/${id}`),
  create: (payload) => api.post("/listings/", payload),
  update: (id, payload) => api.put(`/listings/${id}`, payload),
  remove: (id) => api.delete(`/listings/${id}`),
  aiPrice: (textbookId, condition) =>
    api.post("/listings/ai-price", { textbook_id: textbookId, condition }),
};

export const matchesApi = {
  generate: (userId) => api.post(`/matches/generate/${userId}`),
  get: (userId) => api.get(`/matches/${userId}`),
};

export const conversationsApi = {
  list: () => api.get("/conversations/"),
  get: (id) => api.get(`/conversations/${id}`),
  start: (listingId, initialMessage) =>
    api.post("/conversations/", {
      listing_id: listingId,
      initial_message: initialMessage,
      is_agentic: !initialMessage,
    }),
  sendMessage: (id, content) =>
    api.post(`/conversations/${id}/messages`, { content, is_agentic: false }),
};

export const reviewsApi = {
  forUser: (userId) => api.get(`/reviews/user/${userId}`),
  profile: (userId) => api.get(`/reviews/user/${userId}/profile`),
  create: (payload) => api.post("/reviews/", payload),
};

export const notificationsApi = {
  list: (userId, unreadOnly = false) =>
    api.get(`/notifications/${userId}${unreadOnly ? "?unread_only=true" : ""}`),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: (userId) => api.put(`/notifications/user/${userId}/read-all`),
};

export const chatApi = {
  send: (message, history = []) =>
    api.post("/chat/", { message, history }),
};

export const uploadsApi = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const token = getToken();
    const res = await fetch(`${BASE_URL}/uploads/`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      const detail = await res.text();
      throw new ApiError("Upload failed", res.status, detail);
    }
    return res.json();
  },
};
