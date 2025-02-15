const themeCheckbox = document.querySelector(".theme-controller") as HTMLInputElement

function setTheme(theme: string): void {
  document.documentElement.setAttribute("data-theme", theme)
  localStorage.setItem("theme", theme)

  if (themeCheckbox) {
    themeCheckbox.checked = theme === "dark"
  }
}

function handleThemeChange(): void {
  const newTheme = themeCheckbox.checked ? "dark" : "light"
  setTheme(newTheme)
}

function initializeTheme(): void {
  const savedTheme = localStorage.getItem("theme") || "light"
  setTheme(savedTheme)
  const label = themeCheckbox.closest("label")
  label?.classList.remove("hidden")
}

if (themeCheckbox) {
  themeCheckbox.addEventListener("change", handleThemeChange)
}

initializeTheme()