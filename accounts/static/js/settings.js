(function () {
  // Utility maps for preview
  const FONT_MAP = { small: "14px", medium: "16px", large: "18px" };
  const SPACING_MAP = { compact: "1", normal: "1.5", relaxed: "1.8" };

  const form = document.getElementById("settings-form");

  function getCurrentValues() {
    return {
      high_contrast: form.querySelector('[name="high_contrast"]').checked,
      font_size: form.querySelector('[name="font_size"]').value,
      spacing: form.querySelector('[name="spacing"]').value,
      theme_color:
        form.querySelector('input[name="theme_color"]:checked')?.value ||
        "dark",
      accent_color:
        form.querySelector('[name="accent_color"]:checked')?.value || "#1E90FF",
    };
  }

  function applyPreview(values) {
    // Set CSS variables for the entire UI
    document.documentElement.style.setProperty(
      "--accent-color",
      values.accent_color
    );
    document.documentElement.style.setProperty(
      "--theme-mode",
      values.theme_color
    );
    document.documentElement.classList.toggle(
      "theme-dark",
      values.theme_color === "dark"
    );
    document.documentElement.classList.toggle(
      "theme-light",
      values.theme_color === "light"
    );

    // High contrast
    document.documentElement.classList.toggle(
      "high-contrast",
      values.high_contrast
    );

    // Font size
    if (values.font_size && FONT_MAP[values.font_size]) {
      document.documentElement.style.setProperty(
        "--user-font-size",
        FONT_MAP[values.font_size]
      );
      document.body.style.fontSize = FONT_MAP[values.font_size];
    }

    // Spacing
    if (values.spacing && SPACING_MAP[values.spacing]) {
      document.body.style.lineHeight = SPACING_MAP[values.spacing];
    }

    // Apply accent color to UI elements
    const accentColor = values.accent_color;
    // Calculate if we should use black or white text
    const rgb = parseInt(accentColor.slice(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = rgb & 0xff;
    // Calculate relative luminance
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    const textColor = luminance > 0.5 ? "#000000" : "#ffffff";

    document.documentElement.style.setProperty("--accent-text", textColor);

    document.querySelectorAll(".btn-primary").forEach((btn) => {
      btn.style.backgroundColor = accentColor;
      btn.style.borderColor = accentColor;
      btn.style.color = textColor;
    });

    document.querySelectorAll(".nav-pills .nav-link.active").forEach((nav) => {
      nav.style.backgroundColor = accentColor;
      nav.style.color = textColor;
    });

    // Apply theme colors
    const isDark = values.theme_color === "dark";
    document.body.style.backgroundColor = isDark ? "#1a1a1a" : "#ffffff";
    document.body.style.color = isDark ? "#ffffff" : "#000000";

    document.querySelectorAll(".card").forEach((card) => {
      card.style.backgroundColor = isDark ? "#2d2d2d" : "#ffffff";
      card.style.borderColor = isDark ? "#404040" : "#dee2e6";
    });

    // Update all mockups
    document.querySelectorAll(".color-mockup .mockup-card").forEach((card) => {
      card.classList.toggle("dark-mock", isDark);
      card.classList.toggle("light-mock", !isDark);
      card.classList.toggle("high-contrast-mock", values.high_contrast);

      // Update button colors
      const btn = card.querySelector(".mockup-btn");
      if (btn) {
        const accent =
          getComputedStyle(card).getPropertyValue("--accent") || accentColor;
        btn.style.background = accent;
        btn.style.boxShadow = values.high_contrast
          ? "0 0 0 3px #fff inset"
          : "";
      }

      // Update input styling
      const input = card.querySelector(".mockup-input");
      if (input) {
        input.style.background = isDark ? "#222" : "#fff";
        input.style.color = isDark ? "#fff" : "#000";
        input.style.border = values.high_contrast ? "2px solid #fff" : "";
      }
    });

    // Update form controls
    document.querySelectorAll(".form-control").forEach((input) => {
      input.style.backgroundColor = isDark ? "#333" : "#fff";
      input.style.color = isDark ? "#fff" : "#000";
      input.style.borderColor = isDark ? "#404040" : "#ced4da";
    });

    document.querySelectorAll(".form-select").forEach((select) => {
      select.style.backgroundColor = isDark ? "#333" : "#fff";
      select.style.color = isDark ? "#fff" : "#000";
      select.style.borderColor = isDark ? "#404040" : "#ced4da";
    });
  }

  // Handle live preview on form changes
  form.querySelectorAll("input, select").forEach((input) => {
    input.addEventListener("change", () => {
      applyPreview(getCurrentValues());
    });
  });

  // Reset button handler
  const resetBtn = document.getElementById("reset-theme-btn");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (!confirm("Reset theme and accent to defaults?")) return;

      const defaults = {
        theme_color: "dark",
        accent_color: "#1E90FF",
        high_contrast: false,
        font_size: "medium",
        spacing: "normal",
      };

      // Update form values
      form.querySelector(`#theme_${defaults.theme_color}`).checked = true;
      form.querySelector(
        `[name="accent_color"][value="${defaults.accent_color}"]`
      ).checked = true;
      form.querySelector('[name="high_contrast"]').checked =
        defaults.high_contrast;
      form.querySelector('[name="font_size"]').value = defaults.font_size;
      form.querySelector('[name="spacing"]').value = defaults.spacing;

      // Apply preview and dispatch event
      applyPreview(defaults);
      window.dispatchEvent(new CustomEvent("themeupdate", { detail: defaults }));
    });
  }

  // Regular form submission
  form.addEventListener("submit", function (e) {
    if (!confirm("Save changes to your settings?")) {
      e.preventDefault();
    }
  });

  // Initialize with current values
  function initializeUI() {
    const values = getCurrentValues();
    applyPreview(values);

    // Highlight active accent color
    const activeAccent = values.accent_color;
    document.querySelectorAll(".accent-color-option").forEach((option) => {
      const radio = option.querySelector('input[type="radio"]');
      if (radio.value === activeAccent) {
        radio.checked = true;
      }
    });
  }

  // Call initialize after DOM is loaded and when form values change
  document.addEventListener("DOMContentLoaded", initializeUI);

  // Save settings with visual feedback
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // Show saving indicator
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = "Saving...";
    submitBtn.disabled = true;

    // Get form data
    const formData = new FormData(form);

    // Filter formData to only include appearance-related fields for AJAX
    const appearanceData = new FormData();
    appearanceData.append(
      "csrfmiddlewaretoken",
      formData.get("csrfmiddlewaretoken")
    );

    // Get current values properly
    const themeValues = getCurrentValues();

    // Append each field
    appearanceData.append("theme_color", themeValues.theme_color);
    appearanceData.append("accent_color", themeValues.accent_color);
    appearanceData.append("high_contrast", themeValues.high_contrast);
    appearanceData.append("font_size", themeValues.font_size);
    appearanceData.append("spacing", themeValues.spacing);

    // Log the data being sent for debugging
    console.log("=== Saving theme settings ===");
    for (let pair of appearanceData.entries()) {
      console.log(pair[0] + ": " + pair[1]);
    }

    // Save via AJAX
    fetch(form.action, {
      method: "POST",
      body: appearanceData,
      headers: {
        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => {
        // Log the response for debugging
        console.log("Response status:", response.status);
        return response.json().then((data) => {
          console.log("Response data:", data);
          if (!response.ok) throw data;
          return data;
        });
      })
      .then((data) => {
        // Save theme to localStorage
        const themeValues = getCurrentValues();
        console.log("=== Theme saved successfully ===");
        console.log("Saved values:", themeValues);
        localStorage.setItem("theme", JSON.stringify(themeValues));

        // Dispatch themeupdate event to notify other pages/tabs
        console.log("Dispatching themeupdate event...");
        window.dispatchEvent(new CustomEvent("themeupdate", { detail: themeValues }));

        // Show success message
        const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          Settings saved successfully! Theme changes will apply across all pages.
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      `;
        form.insertAdjacentHTML("afterbegin", alertHtml);

        // Update UI with saved values
        initializeUI();
      })
      .catch((error) => {
        // Show error message with details if available
        const errorMessage =
          error.message || "Failed to save settings. Please try again.";
        let errorDetails = "";

        // If we have form validation errors, show them
        if (error.errors) {
          const allErrors = [
            ...Object.values(error.errors.user || {}),
            ...Object.values(error.errors.profile || {}),
          ];
          if (allErrors.length > 0) {
            errorDetails = `<ul class="mb-0 mt-2">
              ${allErrors.map((err) => `<li>${err}</li>`).join("")}
            </ul>`;
          }
        }

        const alertHtml = `
          <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${errorMessage}
            ${errorDetails}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        `;
        form.insertAdjacentHTML("afterbegin", alertHtml);
      })
      .finally(() => {
        // Restore submit button
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;

        // Auto-dismiss alerts after 5 seconds
        setTimeout(() => {
          document.querySelectorAll(".alert").forEach((alert) => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
          });
        }, 5000);
      });
  });
})();
