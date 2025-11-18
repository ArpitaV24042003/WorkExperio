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

// Handle 401/403 errors - redirect to login if token is invalid
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only handle auth errors for actual authentication failures
    // Don't logout on expected 401s (like checking if user exists)
    if (error.response?.status === 401 || error.response?.status === 403) {
      const currentPath = window.location.pathname;
      const authStore = useAuthStore.getState();
      
      // Only logout if:
      // 1. We have a token (meaning we thought we were logged in)
      // 2. We're not on login/signup pages
      // 3. The error is not from a public endpoint
      // 4. The error is not from a project-specific endpoint (might be permission issue, not auth)
      const isPublicEndpoint = error.config?.url?.includes("/auth/") || 
                               error.config?.url?.includes("/public/");
      const isProjectEndpoint = error.config?.url?.includes("/projects/");
      
      // For project endpoints, don't auto-logout - let the component handle it
      // This prevents redirects when user has valid token but no project access
      if (authStore.token && 
          !currentPath.includes("/login") && 
          !currentPath.includes("/signup") &&
          !isPublicEndpoint &&
          !isProjectEndpoint) {
        // Token is invalid, logout
        authStore.logout();
        // Redirect to login after a short delay to prevent flash
        setTimeout(() => {
          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
        }, 100);
      }
    }
    return Promise.reject(error);
  }
);

export const handleApiError = (error) => {
  const message = error?.response?.data?.detail || error.message || "Something went wrong";
  return Promise.reject(new Error(message));
};

