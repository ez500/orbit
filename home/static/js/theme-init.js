(function () {
  // Load theme from localStorage or use system default
  const loadTheme = () => {
    const defaultTheme =
      document.documentElement.getAttribute("data-theme") || "dark";
    try {
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme) {
        const themeData = JSON.parse(savedTheme);
        console.log("[theme-init.js] Loading theme from localStorage:", themeData);
        applyTheme(themeData);
      } else {
        const serverTheme = {
          theme_color: defaultTheme,
          accent_color:
            getComputedStyle(document.documentElement)
              .getPropertyValue("--accent-color")
              .trim() || "#1E90FF",
          high_contrast:
            document.documentElement.classList.contains("high-contrast"),
          font_size:
            document.documentElement.getAttribute("data-font-size") || "medium",
          spacing:
            document.documentElement.getAttribute("data-spacing") || "normal",
        };
        console.log("[theme-init.js] No localStorage, using server defaults:", serverTheme);
        applyTheme(serverTheme);
      }
    } catch (e) {
      console.error("Failed to load theme:", e);
    }
  };

  // Apply theme settings to document
  const applyTheme = (settings) => {
    console.log("[theme-init.js] Applying theme:", settings);
    document.documentElement.setAttribute("data-theme", settings.theme_color);
    document.documentElement.setAttribute("data-font-size", settings.font_size);
    document.documentElement.setAttribute("data-spacing", settings.spacing);
    document.documentElement.style.setProperty(
      "--accent-color",
      settings.accent_color
    );
    document.documentElement.classList.toggle(
      "high-contrast",
      settings.high_contrast
    );
  };

  // Initialize theme
  loadTheme();

  // Listen for theme updates
  window.addEventListener("themeupdate", (e) => {
    const settings = e.detail;
    applyTheme(settings);
    localStorage.setItem("theme", JSON.stringify(settings));
  });

  // Watch for system theme changes
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  systemTheme.addEventListener("change", () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      const settings = JSON.parse(savedTheme);
      if (settings.theme_color === "system") {
        applyTheme(settings);
      }
    }
  });
})();
