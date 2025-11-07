document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("settings-form");
  const themeInputs = document.querySelectorAll('input[name="theme_color"]');
  const accentInputs = document.querySelectorAll('input[name="accent_color"]');
  const highContrastInput = document.getElementById("id_high_contrast");
  const fontSizeSelect = document.getElementById("id_font_size");
  const spacingSelect = document.getElementById("id_spacing");
  const resetButton = document.getElementById("reset-theme-btn");

  // Auto-dismiss success messages after 5 seconds
  const messagesContainer = document.getElementById("messages-container");
  if (messagesContainer) {
    const alerts = messagesContainer.querySelectorAll(".alert");
    alerts.forEach((alert) => {
      // Only auto-dismiss success messages, not errors
      if (alert.classList.contains("alert-success")) {
        setTimeout(() => {
          const bsAlert = new bootstrap.Alert(alert);
          bsAlert.close();
        }, 5000);
      }
    });

    // Smooth scroll to messages
    messagesContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Function to preview theme changes
  function previewTheme(settings) {
    window.dispatchEvent(
      new CustomEvent("themeupdate", {
        detail: {
          theme_color: settings.theme_color,
          accent_color: settings.accent_color,
          high_contrast: settings.high_contrast,
          font_size: settings.font_size,
          spacing: settings.spacing,
        },
      })
    );
  }

  // Handle theme selection
  themeInputs.forEach((input) => {
    input.addEventListener("change", (e) => {
      previewTheme({
        theme_color: e.target.value,
        accent_color: document.querySelector(
          'input[name="accent_color"]:checked'
        ).value,
        high_contrast: highContrastInput.checked,
        font_size: fontSizeSelect.value,
        spacing: spacingSelect.value,
      });
    });
  });

  // Handle accent color selection
  accentInputs.forEach((input) => {
    input.addEventListener("change", (e) => {
      previewTheme({
        theme_color: document.querySelector('input[name="theme_color"]:checked')
          .value,
        accent_color: e.target.value,
        high_contrast: highContrastInput.checked,
        font_size: fontSizeSelect.value,
        spacing: spacingSelect.value,
      });
    });
  });

  // Handle high contrast toggle
  highContrastInput.addEventListener("change", (e) => {
    previewTheme({
      theme_color: document.querySelector('input[name="theme_color"]:checked')
        .value,
      accent_color: document.querySelector('input[name="accent_color"]:checked')
        .value,
      high_contrast: e.target.checked,
      font_size: fontSizeSelect.value,
      spacing: spacingSelect.value,
    });
  });

  // Handle font size changes
  fontSizeSelect.addEventListener("change", (e) => {
    previewTheme({
      theme_color: document.querySelector('input[name="theme_color"]:checked')
        .value,
      accent_color: document.querySelector('input[name="accent_color"]:checked')
        .value,
      high_contrast: highContrastInput.checked,
      font_size: e.target.value,
      spacing: spacingSelect.value,
    });
  });

  // Handle spacing changes
  spacingSelect.addEventListener("change", (e) => {
    previewTheme({
      theme_color: document.querySelector('input[name="theme_color"]:checked')
        .value,
      accent_color: document.querySelector('input[name="accent_color"]:checked')
        .value,
      high_contrast: highContrastInput.checked,
      font_size: fontSizeSelect.value,
      spacing: e.target.value,
    });
  });

  // Reset to defaults
  resetButton.addEventListener("click", () => {
    previewTheme({
      theme_color: "system",
      accent_color: "#1E90FF",
      high_contrast: false,
      font_size: "medium",
      spacing: "normal",
    });

    // Update form elements
    document.querySelector(
      'input[name="theme_color"][value="system"]'
    ).checked = true;
    document.querySelector(
      'input[name="accent_color"][value="#1E90FF"]'
    ).checked = true;
    highContrastInput.checked = false;
    fontSizeSelect.value = "medium";
    spacingSelect.value = "normal";
  });

  // Form submission
  form.addEventListener("submit", function (e) {
    // The form will submit normally, and the server will handle the update
    // The page will reload with new settings
  });
});
