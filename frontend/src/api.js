// src/api.js

// ---- BASE URL ----
// FIX: Replaced import.meta.env with process.env to avoid es2015 build warning
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
      // AbortError or network error => retry (up to retries)
      if (i === retries) break;
      const delay = baseDelay * Math.pow(2, i) + Math.random() * 250;
      await sleep(delay);
    }
  }
  throw lastErr;
}

// ---- MAIN ----
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

  // Build headers (don't set JSON header for FormData)
  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(extra.headers || {}),
  };

  // --- LOGIC FIX BLOCK ---
  // Attach Bearer token from localStorage
  try {
    // First, check for the standalone token (from LoginSignupPage.jsx)
    let token = localStorage.getItem("token");

    // If not found, check inside the user object as a fallback
    if (!token) {
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        token = parsedUser?.token || parsedUser?.accessToken;
      }
    }

    // If we found a token one way or another, add it to the header
    if (token && !headers.Authorization) {
      headers.Authorization = `Bearer ${token}`;
    }
  } catch {
    // ignore malformed storage
  }
  // --- END OF LOGIC FIX BLOCK ---

  const timeoutMs = Number.isFinite(extra.timeoutMs) ? extra.timeoutMs : 45000; // 45s (cold start friendly)
  const retries = Number.isFinite(extra.retries) ? extra.retries : 2;
  const baseDelay = Number.isFinite(extra.baseDelay) ? extra.baseDelay : 1000;

  const options = {
    method,
    headers,
    // enable cookies if your backend uses sessions; otherwise remove/override with extra.credentials
    credentials: extra.credentials ?? "include",
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
      const msg =
        (data && (data.message || data.error || data.detail)) ||
        `HTTP ${res.status} ${res.statusText}`;
      const err = new Error(msg);
      err.status = res.status;
      err.data = data;
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
