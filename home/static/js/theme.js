// Theme management for all pages
(function () {
  const FONT_SIZES = {
    small: "14px",
    medium: "16px",
    large: "18px",
  };

  const SPACING = {
    compact: "1",
    normal: "1.5",
    relaxed: "1.8",
  };

  function calculateTextColor(bgColor) {
    const rgb = parseInt(bgColor.slice(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = rgb & 0xff;
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.5 ? "#000000" : "#ffffff";
  }

  function applyTheme(themeData) {
    console.log("[theme.js] Applying theme:", themeData);

    // Clean up existing classes
    document.documentElement.classList.remove('theme-dark', 'theme-light', 'theme-system', 'high-contrast');

    // Apply theme mode
    const isDark = themeData.theme_color === 'dark' ||
                  (themeData.theme_color === 'system' &&
                   window.matchMedia('(prefers-color-scheme: dark)').matches);

    // Set theme attributes
    document.documentElement.setAttribute('data-theme', themeData.theme_color);
    document.documentElement.classList.add(`theme-${themeData.theme_color}`);
    
    // Force light/dark mode based on system preference if system theme is selected
    if (themeData.theme_color === 'system') {
      document.documentElement.classList.add(`theme-${isDark ? 'dark' : 'light'}`);
    }

    // Apply accent color
    document.documentElement.style.setProperty('--accent-color', themeData.accent_color);
    const textColor = calculateTextColor(themeData.accent_color);
    document.documentElement.style.setProperty('--accent-text', textColor);

    // Update CSS variables based on theme
    document.documentElement.style.setProperty('--bg-color', isDark ? '#1a1a1a' : '#ffffff');
    document.documentElement.style.setProperty('--text-color', isDark ? '#ffffff' : '#000000');
    document.documentElement.style.setProperty('--border-color', isDark ? '#404040' : '#dee2e6');
    document.documentElement.style.setProperty('--sidebar-bg', isDark ? '#2d2d2d' : '#f8f9fa');
    document.documentElement.style.setProperty('--card-bg', isDark ? '#2d2d2d' : '#ffffff');
    document.documentElement.style.setProperty('--input-bg', isDark ? '#333333' : '#ffffff');
    document.documentElement.style.setProperty('--hover-bg', isDark ? '#404040' : '#e9ecef');

    // Apply high contrast mode
    if (themeData.high_contrast) {
      document.documentElement.classList.add('high-contrast');
      // Override some variables for high contrast
      document.documentElement.style.setProperty('--bg-color', '#000000');
      document.documentElement.style.setProperty('--text-color', '#ffffff');
      document.documentElement.style.setProperty('--border-color', '#ffffff');
    }

    // Apply font size
    if (themeData.font_size && FONT_SIZES[themeData.font_size]) {
      document.documentElement.style.setProperty('--user-font-size', FONT_SIZES[themeData.font_size]);
      document.documentElement.setAttribute('data-font-size', themeData.font_size);
      document.documentElement.style.fontSize = FONT_SIZES[themeData.font_size];
    }

    // Apply spacing
    if (themeData.spacing && SPACING[themeData.spacing]) {
      document.documentElement.setAttribute('data-spacing', themeData.spacing);
      document.documentElement.style.setProperty('--line-height', SPACING[themeData.spacing]);
    }

    // Force a repaint to ensure all changes are applied
    document.body.style.display = 'none';
    document.body.offsetHeight;
    document.body.style.display = '';

    // Store theme in localStorage
    localStorage.setItem('theme', JSON.stringify(themeData));
  }

  // Update UI elements to reflect current theme
  function updateThemeUI(themeData) {
    // Update theme option buttons
    document.querySelectorAll(".theme-option").forEach((option) => {
      const input = option.querySelector('input[type="radio"]');
      option.classList.toggle("active", input.value === themeData.theme_color);
    });

    // Update color scheme options
    document
      .querySelectorAll('.color-option input[type="radio"]')
      .forEach((input) => {
        const swatch = input.nextElementSibling;
        if (swatch) {
          swatch.classList.toggle(
            "active",
            input.value === themeData.accent_color
          );
        }
      });

    // Update preview section
    const preview = document.querySelector(".preview-section");
    if (preview) {
      preview.style.setProperty("--preview-accent", themeData.accent_color);
    }
  }

  // Initialize theme from localStorage or server-side data
  function initializeTheme() {
    let themeData;
    try {
      // Try to get theme from localStorage first
      const savedTheme = localStorage.getItem("theme");
      if (savedTheme) {
        themeData = JSON.parse(savedTheme);
        console.log("[theme.js] Initializing from localStorage:", themeData);
      } else {
        console.log("[theme.js] No localStorage, using server defaults");
        // Fall back to server-side data embedded in the page
        themeData = {
          theme_color:
            document.documentElement.getAttribute("data-theme") || "dark",
          accent_color:
            getComputedStyle(document.documentElement)
              .getPropertyValue("--accent-color")
              .trim() || "#1E90FF",
          high_contrast:
            document.documentElement.classList.contains("high-contrast"),
          font_size: "medium",
          spacing: "normal",
        };
      }
      applyTheme(themeData);
    } catch (e) {
      console.error("Failed to initialize theme:", e);
    }
  }

  // Listen for theme changes
  window.addEventListener("themeupdate", (event) => {
    try {
      const themeData = event.detail;
      console.log("[theme.js] Received themeupdate event:", themeData);
      applyTheme(themeData);
      localStorage.setItem("theme", JSON.stringify(themeData));
    } catch (e) {
      console.error("Failed to update theme:", e);
    }
  });

  // Watch for system theme changes if using system theme
  const systemThemeQuery = window.matchMedia("(prefers-color-scheme: dark)");
  systemThemeQuery.addListener((e) => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      const themeData = JSON.parse(savedTheme);
      if (themeData.theme_color === "system") {
        applyTheme(themeData);
      }
    }
  });

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeTheme);
  } else {
    initializeTheme();
  }
})();
