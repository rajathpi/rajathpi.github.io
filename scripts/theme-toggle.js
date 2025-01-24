// Get the theme toggle button
const themeToggle = document.getElementById("theme-toggle");

// Check for saved theme in localStorage
const savedTheme = localStorage.getItem("theme");
if (savedTheme) {
  document.body.classList.add(savedTheme);
  updateButtonIcon(savedTheme);
}

// Toggle between light and dark mode
themeToggle.addEventListener("click", () => {
  if (document.body.classList.contains("light-mode")) {
    document.body.classList.remove("light-mode");
    localStorage.setItem("theme", "dark-mode");
    updateButtonIcon("dark-mode");
  } else {
    document.body.classList.add("light-mode");
    localStorage.setItem("theme", "light-mode");
    updateButtonIcon("light-mode");
  }
});

// Update the button icon based on the current theme
function updateButtonIcon(theme) {
  if (theme === "light-mode") {
    themeToggle.textContent = "🌙"; // Moon icon for dark mode
  } else {
    themeToggle.textContent = "☀️"; // Sun icon for light mode
  }
}