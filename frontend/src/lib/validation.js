/**
 * Form validation utilities
 */

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password) => {
  if (!password) return "Password is required";
  if (password.length < 6) return "Password must be at least 6 characters";
  return null;
};

export const validateRequired = (value, fieldName) => {
  if (!value || (typeof value === "string" && !value.trim())) {
    return `${fieldName} is required`;
  }
  return null;
};

export const validateMinLength = (value, minLength, fieldName) => {
  if (value && value.length < minLength) {
    return `${fieldName} must be at least ${minLength} characters`;
  }
  return null;
};

export const validateMaxLength = (value, maxLength, fieldName) => {
  if (value && value.length > maxLength) {
    return `${fieldName} must be at most ${maxLength} characters`;
  }
  return null;
};

export const validateForm = (formData, rules) => {
  const errors = {};
  
  for (const [field, fieldRules] of Object.entries(rules)) {
    const value = formData[field];
    
    for (const rule of fieldRules) {
      const error = rule(value, field);
      if (error) {
        errors[field] = error;
        break; // Stop at first error for this field
      }
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Common validation rules
export const commonRules = {
  email: [
    (v) => validateRequired(v, "Email"),
    (v) => (v && !validateEmail(v) ? "Invalid email address" : null),
  ],
  password: [
    (v) => validateRequired(v, "Password"),
    (v) => validatePassword(v),
  ],
  name: [
    (v) => validateRequired(v, "Name"),
    (v) => validateMinLength(v, 2, "Name"),
  ],
  title: [
    (v) => validateRequired(v, "Title"),
    (v) => validateMinLength(v, 3, "Title"),
  ],
  description: [
    (v) => validateRequired(v, "Description"),
    (v) => validateMinLength(v, 10, "Description"),
  ],
};

