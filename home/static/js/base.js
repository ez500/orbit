(function () {
  function applyTheme() {
    const theme = localStorage.getItem("theme")
      ? JSON.parse(localStorage.getItem("theme"))
      : {
          theme_color: "dark",
          accent_color: "#1E90FF",
          high_contrast: false,
          font_size: "medium",
          spacing: "normal",
        };

    // Apply theme to root
    document.documentElement.style.setProperty(
      "--accent-color",
      theme.accent_color
    );
    document.documentElement.style.setProperty(
      "--theme-mode",
      theme.theme_color
    );

    // Apply classes
    document.documentElement.classList.remove("theme-dark", "theme-light");
    document.documentElement.classList.add(`theme-${theme.theme_color}`);
    document.documentElement.classList.toggle(
      "high-contrast",
      theme.high_contrast
    );

    // Calculate text color for accent
    const rgb = parseInt(theme.accent_color.slice(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = rgb & 0xff;
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    const textColor = luminance > 0.5 ? "#000000" : "#ffffff";
    document.documentElement.style.setProperty("--accent-text", textColor);

    // Apply font size and spacing
    const FONT_MAP = { small: "14px", medium: "16px", large: "18px" };
    const SPACING_MAP = { compact: "1", normal: "1.5", relaxed: "1.8" };

    if (theme.font_size && FONT_MAP[theme.font_size]) {
      document.documentElement.style.setProperty(
        "--user-font-size",
        FONT_MAP[theme.font_size]
      );
      document.body.style.fontSize = FONT_MAP[theme.font_size];
    }

    if (theme.spacing && SPACING_MAP[theme.spacing]) {
      document.body.style.lineHeight = SPACING_MAP[theme.spacing];
    }
  }

  // Apply theme on page load
  document.addEventListener("DOMContentLoaded", applyTheme);

  // Listen for theme changes from settings page
  window.addEventListener("storage", function (e) {
    if (e.key === "theme") {
      applyTheme();
    }
  });
})();
