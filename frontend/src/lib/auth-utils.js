/**
 * Auth utility functions for token validation and state management
 */

/**
 * Validates if a token exists and is not empty
 * @param {string} token - The token to validate
 * @returns {boolean} - True if token is valid
 */
export const isValidToken = (token) => {
  return token && typeof token === "string" && token.trim().length > 0;
};

/**
 * Gets the stored token from localStorage
 * @returns {string|null} - The token or null if not found
 */
export const getStoredToken = () => {
  try {
    const token = localStorage.getItem("token");
    return isValidToken(token) ? token : null;
  } catch {
    return null;
  }
};

/**
 * Checks if user is authenticated by validating token in localStorage
 * @returns {boolean} - True if authenticated
 */
export const isAuthenticated = () => {
  return getStoredToken() !== null;
};

/**
 * Rehydrates auth state from localStorage
 * @returns {{token: string|null, user: object|null}} - Auth state
 */
export const rehydrateAuthState = () => {
  try {
    const token = getStoredToken();
    const userStr = localStorage.getItem("user");
    const user = userStr ? JSON.parse(userStr) : null;
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
};

