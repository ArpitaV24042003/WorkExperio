import { create } from "zustand";

const persistedToken = localStorage.getItem("token");
const persistedUser = localStorage.getItem("user");

export const useAuthStore = create((set) => ({
  token: persistedToken || "",
  user: persistedUser ? JSON.parse(persistedUser) : null,
  isAuthenticated: Boolean(persistedToken),
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

