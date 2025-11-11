// src/api.js
// Enhanced fetch wrapper for WorkExperio frontend
// - Uses process.env.VITE_API_URL (fallback to render URL)
// - Automatic Bearer token attachment (from localStorage.token or localStorage.user token fields)
// - Timeout, retries with exponential backoff (good for Render cold starts)
// - JSON & FormData handling
// - Normalized errors

// ---- BASE URL ----
const RAW_BASE = process.env.VITE_API_URL || "https://workexperio.onrender.com";
// normalize (strip trailing slashes)
const BASE_URL = RAW_BASE.replace(/\/+$/, "");

// ---- UTILS ----
function joinURL(base, endpoint) {
  if (!endpoint) return base;
  if (/^https?:\/\//i.test(endpoint)) return endpoint; // already absolute
  const ep = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${base}${ep}`;
}

function parseJSONSafe(text) {
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function fetchWithTimeout(resource, options = {}, timeoutMs = 45000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(resource, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}

// Exponential backoff wrapper (good for Render cold starts)
async function withRetries(fn, { retries = 2, baseDelay = 1000 } = {}) {
  let lastErr;
  for (let i = 0; i <= retries; i++) {
    try {
      return await fn();
    } catch (err) {
      lastErr = err;
      // If last attempt, break
      if (i === retries) break;
      // Wait with jitter
      const delay = baseDelay * Math.pow(2, i) + Math.random() * 250;
      await sleep(delay);
    }
  }
  throw lastErr;
}

// ---- AUTH HELPERS ----
export function clearAuth() {
  try {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  } catch (e) {
    // ignore
  }
}

/** Return token from storage (primary token or inside user object) */
export function getToken() {
  try {
    // Primary: token stored directly
    let token = localStorage.getItem("token");
    if (token) return token;

    // Fallback: token inside stored user object (some backends return token there)
    const stored = localStorage.getItem("user");
    if (!stored) return null;
    const parsed = JSON.parse(stored);
    return parsed?.token || parsed?.accessToken || null;
  } catch {
    return null;
  }
}

function readStoredTokenFallback() {
  // small internal alias for legacy usage
  return getToken();
}

// ---- MAIN FUNCTION ----
/**
 * apiRequest
 * @param {string} endpoint - "/users/login" or full URL
 * @param {string} method - HTTP method, default "GET"
 * @param {object|FormData|null} body - data to send
 * @param {object} extra - { headers, credentials, timeoutMs, retries, baseDelay }
 * @returns {Promise<any>}
 */
export async function apiRequest(
  endpoint,
  method = "GET",
  body = null,
  extra = {}
) {
  const url = joinURL(BASE_URL, endpoint);

  const isFormData =
    typeof FormData !== "undefined" && body instanceof FormData;

  // Build headers: only set Content-Type for JSON when there is a non-null body
  const headers = {
    ...(isFormData
      ? {}
      : body != null
      ? { "Content-Type": "application/json" }
      : {}),
    ...(extra.headers || {}),
  };

  // --- Attach Bearer token from localStorage (stable logic) ---
  try {
    let token = readStoredTokenFallback();
    if (token && !headers.Authorization) {
      headers.Authorization = `Bearer ${token}`;
    }
  } catch {
    // ignore malformed storage
  }
  // --- End token attach ---

  const timeoutMs = Number.isFinite(extra.timeoutMs) ? extra.timeoutMs : 45000; // 45s
  const retries = Number.isFinite(extra.retries) ? extra.retries : 2;
  const baseDelay = Number.isFinite(extra.baseDelay) ? extra.baseDelay : 1000;

  const options = {
    method,
    headers,
    // default to same-origin for cookies; set extra.credentials="include" if you need cross-site cookies
    credentials: extra.credentials ?? "same-origin",
  };

  if (body != null) {
    options.body = isFormData ? body : JSON.stringify(body);
  }

  const exec = async () => {
    const res = await fetchWithTimeout(url, options, timeoutMs);

    // No content
    if (res.status === 204) return null;

    const ct = res.headers.get("content-type") || "";
    const text = await res.text(); // read once
    const data = ct.includes("application/json")
      ? parseJSONSafe(text)
      : text || null;

    if (!res.ok) {
      // Normalize message shape
      const msg =
        (data && (data.message || data.error || data.detail)) ||
        `HTTP ${res.status} ${res.statusText}`;
      const err = new Error(msg);
      err.status = res.status;
      err.data = data;

      // On auth errors, clear local auth to prevent loops
      if (res.status === 401 || res.status === 403) {
        try {
          clearAuth();
        } catch {}
      }

      throw err;
    }
    return data;
  };

  try {
    return await withRetries(exec, { retries, baseDelay });
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    // Network error message normalization
    if (err?.message?.includes("Failed to fetch")) {
      throw new Error("Network error: could not reach the server.");
    }
    throw err;
  }
}

// ---- Convenience helpers ----

/**
 * Upload a file using multipart/form-data. Returns parsed JSON.
 * Example: await uploadFile('/resumes/parse', file, { userId: 1 })
 */
export async function uploadFile(endpoint, file, fields = {}, extra = {}) {
  const fd = new FormData();
  if (file) fd.append("file", file);
  Object.keys(fields || {}).forEach((k) => {
    const v = fields[k];
    if (v !== undefined && v !== null) fd.append(k, v);
  });

  // ensure we don't send Content-Type header for multipart
  return await apiRequest(endpoint, "POST", fd, { ...extra, headers: {} });
}

/**
 * Fetch canonical current user via GET /users/me
 */
export async function fetchCurrentUser() {
  return await apiRequest("/users/me", "GET");
}

/**
 * Optional helper to programmatically set the token (e.g. after login)
 */
export function setToken(token) {
  try {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  } catch {}
}

export default {
  apiRequest,
  uploadFile,
  fetchCurrentUser,
  setToken,
  clearAuth,
  getToken,
};
