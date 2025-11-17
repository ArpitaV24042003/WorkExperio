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
    if (error.response?.status === 401 || error.response?.status === 403) {
      // Only logout if we're not already on login/signup page
      const currentPath = window.location.pathname;
      if (!currentPath.includes("/login") && !currentPath.includes("/signup")) {
        useAuthStore.getState().logout();
        // Don't redirect immediately - let the component handle it
        // This prevents "not found" flash on refresh
      }
    }
    return Promise.reject(error);
  }
);

export const handleApiError = (error) => {
  const message = error?.response?.data?.detail || error.message || "Something went wrong";
  return Promise.reject(new Error(message));
};

