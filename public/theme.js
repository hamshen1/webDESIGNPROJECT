// DOM Elements
const darkModeToggle = document.querySelector(".dark-mode-toggle");
const html = document.documentElement;

// Check for saved theme preference or system preference
function initializeTheme() {
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  // Only enable dark mode if explicitly saved as dark or if system prefers dark and no saved preference
  if (savedTheme === "dark") {
    enableDarkMode();
  } else if (savedTheme === "light") {
    disableDarkMode();
  } else if (prefersDark) {
    enableDarkMode();
  } else {
    disableDarkMode(); // Default to light mode if no preference
  }

  // Make toggle visible after theme is initialized
  darkModeToggle.style.opacity = "1";
}

function enableDarkMode() {
  html.classList.add("dark-mode");
  localStorage.setItem("theme", "dark");
}

function disableDarkMode() {
  html.classList.remove("dark-mode");
  localStorage.setItem("theme", "light");
}

// Toggle dark mode
darkModeToggle.addEventListener("click", () => {
  if (html.classList.contains("dark-mode")) {
    disableDarkMode();
  } else {
    enableDarkMode();
  }
});

// Initialize theme when DOM is loaded
document.addEventListener("DOMContentLoaded", initializeTheme);

// Listen for system theme changes
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    const savedTheme = localStorage.getItem("theme");
    // Only react to system changes if user hasn't set a preference
    if (!savedTheme) {
      if (e.matches) {
        enableDarkMode();
      } else {
        disableDarkMode();
      }
    }
  });
