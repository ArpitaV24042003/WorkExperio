import { create } from "zustand";

// Initialize from localStorage
const getPersistedToken = () => {
  try {
    return localStorage.getItem("token") || "";
  } catch {
    return "";
  }
};

const getPersistedUser = () => {
  try {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
};

export const useAuthStore = create((set, get) => ({
  token: getPersistedToken(),
  user: getPersistedUser(),
  isAuthenticated: Boolean(getPersistedToken()),
  
  // Initialize auth state on mount (for page refresh)
  initialize: () => {
    const token = getPersistedToken();
    const user = getPersistedUser();
    if (token && !get().isAuthenticated) {
      set({
        token,
        user,
        isAuthenticated: true,
      });
    }
  },
  
  setCredentials: ({ token, user }) =>
    set(() => {
      if (token) {
        localStorage.setItem("token", token);
      }
      if (user) {
        localStorage.setItem("user", JSON.stringify(user));
      }
      return {
        token,
        user,
        isAuthenticated: Boolean(token),
      };
    }),
  logout: () =>
    set(() => {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      return {
        token: "",
        user: null,
        isAuthenticated: false,
      };
    }),
}));

