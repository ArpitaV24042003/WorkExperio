// // src/api.js
// const API_BASE_URL = import.meta.env.VITE_API_URL;

// export async function apiRequest(endpoint, method = 'GET', data = null) {
//   const options = {
//     method,
//     headers: {
//       'Content-Type': 'application/json',
//     },
//   };

//   if (data) {
//     options.body = JSON.stringify(data);
//   }

//   try {
//     const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
//     if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`);
//     }
//     return await response.json();
//   } catch (error) {
//     console.error('API request failed:', error);
//     throw error;
//   }
// }

// src/api.js

// Base URL: set VITE_API_URL in your .env, e.g. http://127.0.0.1:8000
const BASE_URL = (
  import.meta.env.VITE_API_URL || "https://workexperio.onrender.com"
).replace(/\/+$/, "");

// Safely join base + endpoint (accepts full URLs too)
function joinURL(base, endpoint) {
  if (!endpoint) return base;
  if (/^https?:\/\//i.test(endpoint)) return endpoint; // already absolute
  const ep = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  return `${base}${ep}`;
}

// Best-effort JSON parse
function parseJSONSafe(text) {
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    return { raw: text };
  }
}

/**
 * apiRequest
 * @param {string} endpoint - "/users/login" or full URL
 * @param {string} method - HTTP method, default "GET"
 * @param {object|FormData|null} body - data to send
 * @param {object} extra - { headers, credentials, timeoutMs }
 * @returns {Promise<any>}
 */
export async function apiRequest(
  endpoint,
  method = "GET",
  body = null,
  extra = {}
) {
  const url = joinURL(BASE_URL, endpoint);

  // Default headers; skip JSON header for FormData
  const isFormData =
    typeof FormData !== "undefined" && body instanceof FormData;
  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...(extra.headers || {}),
  };

  // Optional: attach Bearer token from localStorage if present
  try {
    const stored = localStorage.getItem("user");
    if (stored) {
      const parsed = JSON.parse(stored);
      const token = parsed?.token || parsed?.accessToken;
      if (token && !headers.Authorization) {
        headers.Authorization = `Bearer ${token}`;
      }
    }
  } catch {
    // ignore malformed storage
  }

  // Timeout support
  const timeoutMs = Number.isFinite(extra.timeoutMs) ? extra.timeoutMs : 15000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const options = {
    method,
    headers,
    signal: controller.signal,
    // If your backend uses cookies/sessions, enable this:
    // credentials: extra.credentials ?? "include",
  };

  if (body != null) {
    options.body = isFormData ? body : JSON.stringify(body);
  }

  try {
    const res = await fetch(url, options);
    const text = await res.text();
    const data = parseJSONSafe(text);

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
  } catch (err) {
    // Surface clearer messages for timeouts/aborts
    if (err.name === "AbortError") {
      throw new Error("Request timed out. Please try again.");
    }
    console.error("apiRequest failed:", err);
    throw err;
  } finally {
    clearTimeout(timer);
  }
}
