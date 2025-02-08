// Select the checkbox input
const themeCheckbox = document.querySelector(".theme-controller") as HTMLInputElement

// Function to set the theme
function setTheme(theme: string): void {
  document.documentElement.setAttribute("data-theme", theme) // Set the `data-theme` attribute
  localStorage.setItem("theme", theme) // Save the theme to localStorage

  // Update the checkbox state based on the selected theme
  if (themeCheckbox) {
    themeCheckbox.checked = theme === "dark"
  }
}

// Function to handle theme change when the checkbox is toggled
function handleThemeChange(): void {
  const newTheme = themeCheckbox.checked ? "dark" : "light" // Determine the theme based on checkbox state
  setTheme(newTheme)
}

// Initialize the theme on page load
function initializeTheme(): void {
  const savedTheme = localStorage.getItem("theme") || "light" // Default to "light"
  setTheme(savedTheme) // Apply the saved or default theme
}

// Add event listener for the checkbox
if (themeCheckbox) {
  themeCheckbox.addEventListener("change", handleThemeChange)
}

// Initialize the theme when the script loads
initializeTheme()