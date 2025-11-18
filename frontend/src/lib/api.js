import axios from "axios";
import { useAuthStore } from "../store/auth";

// Determine API URL: use env var, or detect Render deployment, or fallback to localhost
const getApiUrl = () => {
  // If explicitly set in env, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // If we're on Render frontend, use Render backend
  if (window.location.hostname.includes("onrender.com")) {
    return "https://workexperio-backend.onrender.com";
  }
  
  // Default to localhost for local development
  return "http://localhost:8000";
};

export const apiClient = axios.create({
  baseURL: getApiUrl(),
  timeout: 30000, // 30 seconds timeout
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors - ONLY redirect to login on 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // ONLY handle 401 Unauthorized - this means token is invalid/expired
    // Do NOT redirect on 400/403/404/422/500 - these are business logic errors
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname;
      const authStore = useAuthStore.getState();
      
      // Only logout and redirect if:
      // 1. We have a token (meaning we thought we were logged in)
      // 2. We're not on login/signup pages
      // 3. The error is not from a public/auth endpoint (might be expected)
      const isPublicEndpoint = error.config?.url?.includes("/auth/") || 
                               error.config?.url?.includes("/public/") ||
                               error.config?.url?.includes("/signup") ||
                               error.config?.url?.includes("/login");
      
      if (authStore.token && 
          !currentPath.includes("/login") && 
          !currentPath.includes("/signup") &&
          !isPublicEndpoint) {
        // Token is invalid/expired, logout
        authStore.logout();
        // Redirect to login after a short delay to prevent flash
        setTimeout(() => {
          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
        }, 100);
      }
    }
    // For all other errors (400/403/404/422/500), just reject the promise
    // Components will handle these errors appropriately (show toast, error message, etc.)
    return Promise.reject(error);
  }
);

export const handleApiError = (error) => {
  // Handle network errors (no response from server)
  if (!error.response) {
    if (error.code === "ECONNABORTED" || error.message?.includes("timeout")) {
      return Promise.reject(new Error("Request timed out. Please check your connection and try again."));
    }
    if (error.message === "Network Error" || error.code === "ERR_NETWORK") {
      const apiUrl = getApiUrl();
      return Promise.reject(new Error(`Cannot connect to server. Please ensure the backend is running at ${apiUrl}`));
    }
    return Promise.reject(new Error("Network error. Please check your internet connection and try again."));
  }
  
  // Handle HTTP errors (server responded with error status)
  const message = error?.response?.data?.detail || error.message || "Something went wrong";
  return Promise.reject(new Error(message));
};

