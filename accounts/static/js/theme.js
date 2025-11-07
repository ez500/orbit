// Constants for theme settings
const FONT_MAP = { small: "14px", medium: "16px", large: "18px" };
const SPACING_MAP = { compact: "1", normal: "1.5", relaxed: "1.8" };

// Apply theme settings to the page
function applyTheme(themeData) {
  if (!themeData) return;

  // Theme mode
  document.documentElement.setAttribute("data-theme", themeData.theme_color);
  document.documentElement.classList.toggle(
    "theme-dark",
    themeData.theme_color === "dark"
  );
  document.documentElement.classList.toggle(
    "theme-light",
    themeData.theme_color === "light"
  );

  // Accent color
  document.documentElement.style.setProperty(
    "--accent-color",
    themeData.accent_color
  );

  // Calculate text color based on accent color
  const rgb = parseInt(themeData.accent_color.slice(1), 16);
  const r = (rgb >> 16) & 0xff;
  const g = (rgb >> 8) & 0xff;
  const b = rgb & 0xff;
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  const textColor = luminance > 0.5 ? "#000000" : "#ffffff";
  document.documentElement.style.setProperty("--accent-text", textColor);

  // High contrast
  document.documentElement.classList.toggle(
    "high-contrast",
    themeData.high_contrast
  );

  // Font size
  if (themeData.font_size && FONT_MAP[themeData.font_size]) {
    document.documentElement.style.setProperty(
      "--user-font-size",
      FONT_MAP[themeData.font_size]
    );
    document.body.style.fontSize = FONT_MAP[themeData.font_size];
  }

  // Spacing
  if (themeData.spacing && SPACING_MAP[themeData.spacing]) {
    document.body.style.lineHeight = SPACING_MAP[themeData.spacing];
  }
}

// Initialize theme from localStorage
function initTheme() {
  try {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      const themeData = JSON.parse(savedTheme);
      applyTheme(themeData);
    }
  } catch (e) {
    console.error("Failed to load theme from localStorage:", e);
  }
}

// Call initialize after DOM is loaded
document.addEventListener("DOMContentLoaded", initTheme);
