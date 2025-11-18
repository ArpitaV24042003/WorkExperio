import axios from "axios";
import { useAuthStore } from "../store/auth";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
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
  const message = error?.response?.data?.detail || error.message || "Something went wrong";
  return Promise.reject(new Error(message));
};

