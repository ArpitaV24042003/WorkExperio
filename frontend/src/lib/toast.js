/**
 * Simple toast notification system
 */

let toastContainer = null;

const createToastContainer = () => {
  if (toastContainer) return toastContainer;
  
  const container = document.createElement("div");
  container.id = "toast-container";
  container.className = "fixed top-4 right-4 z-50 space-y-2";
  document.body.appendChild(container);
  toastContainer = container;
  return container;
};

const showToast = (message, type = "info") => {
  const container = createToastContainer();
  const toast = document.createElement("div");
  
  const bgColors = {
    success: "bg-green-500",
    error: "bg-red-500",
    warning: "bg-yellow-500",
    info: "bg-blue-500",
  };
  
  toast.className = `${bgColors[type] || bgColors.info} text-white px-4 py-3 rounded-md shadow-lg min-w-[300px] flex items-center justify-between`;
  toast.innerHTML = `
    <span>${message}</span>
    <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.remove()">×</button>
  `;
  
  container.appendChild(toast);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.remove();
    }
  }, 5000);
};

export const toast = {
  success: (message) => showToast(message, "success"),
  error: (message) => showToast(message, "error"),
  warning: (message) => showToast(message, "warning"),
  info: (message) => showToast(message, "info"),
};

