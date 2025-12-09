(function () {
  // Utility maps for preview
  const FONT_MAP = { small: "14px", medium: "16px", large: "18px" };
  const SPACING_MAP = { compact: "1", normal: "1.5", relaxed: "1.8" };

  const form = document.getElementById("settings-form");
  let initialValues = null;
  let unsavedChangesAlert = null;

  // Function to show unsaved changes alert
  function showUnsavedChangesAlert() {
    // Remove existing alert if present
    if (unsavedChangesAlert) {
      unsavedChangesAlert.remove();
    }

    // Get or create messages container
    let messagesContainer = document.getElementById("messages-container");
    if (!messagesContainer) {
      messagesContainer = document.createElement("div");
      messagesContainer.id = "messages-container";
      const settingsContainer = document.querySelector(".settings-container");
      if (settingsContainer) {
        settingsContainer.insertBefore(messagesContainer, settingsContainer.firstChild);
      }
    }

    // Create alert element
    unsavedChangesAlert = document.createElement("div");
    unsavedChangesAlert.className = "alert alert-warning alert-dismissible fade show";
    unsavedChangesAlert.setAttribute("role", "alert");
    unsavedChangesAlert.innerHTML = `
      <i class="fas fa-exclamation-triangle me-2"></i>
      <strong>Unsaved changes:</strong> You have unsaved changes. Don't forget to click "Save Changes" to apply them.
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    messagesContainer.appendChild(unsavedChangesAlert);
  }

  // Function to hide unsaved changes alert
  function hideUnsavedChangesAlert() {
    if (unsavedChangesAlert) {
      unsavedChangesAlert.remove();
      unsavedChangesAlert = null;
    }
  }

  // Function to check if form has unsaved changes
  function hasUnsavedChanges() {
    if (!initialValues) return false;
    const currentValues = getCurrentValues();
    return JSON.stringify(currentValues) !== JSON.stringify(initialValues);
  }

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
    // Calculate theme-specific values
    const isDark = values.theme_color === "dark";
    const accentColor = values.accent_color;

    // Calculate if we should use black or white text on accent color
    const rgb = parseInt(accentColor.slice(1), 16);
    const r = (rgb >> 16) & 0xff;
    const g = (rgb >> 8) & 0xff;
    const b = rgb & 0xff;
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    const textColor = luminance > 0.5 ? "#000000" : "#ffffff";

    // Update CSS variables for theme colors
    document.documentElement.style.setProperty("--accent-color", accentColor);
    document.documentElement.style.setProperty("--accent-color-rgb", `${r}, ${g}, ${b}`);
    document.documentElement.style.setProperty("--accent-text", textColor);
    document.documentElement.style.setProperty("--bg-color", isDark ? "#1a1a1a" : "#ffffff");
    document.documentElement.style.setProperty("--text-color", isDark ? "#ffffff" : "#000000");
    document.documentElement.style.setProperty("--card-bg", isDark ? "#2d2d2d" : "#ffffff");
    document.documentElement.style.setProperty("--border-color", isDark ? "#404040" : "#dee2e6");
    document.documentElement.style.setProperty("--hover-bg", isDark ? "#404040" : "#f8f9fa");
    document.documentElement.style.setProperty("--input-bg", isDark ? "#333333" : "#ffffff");

    // Update theme classes
    document.documentElement.classList.toggle("theme-dark", isDark);
    document.documentElement.classList.toggle("theme-light", !isDark);
    document.documentElement.classList.toggle("high-contrast", values.high_contrast);

    // Update data attributes
    document.documentElement.setAttribute("data-theme", values.theme_color);

    // Font size
    if (values.font_size && FONT_MAP[values.font_size]) {
      document.documentElement.style.setProperty("--user-font-size", FONT_MAP[values.font_size]);
      document.documentElement.setAttribute("data-font-size", values.font_size);
    }

    // Spacing
    if (values.spacing && SPACING_MAP[values.spacing]) {
      document.documentElement.style.setProperty("--line-height", SPACING_MAP[values.spacing]);
      document.documentElement.setAttribute("data-spacing", values.spacing);
    }

    // Dispatch a custom event so other scripts can respond
    window.dispatchEvent(new CustomEvent("themeupdate", { detail: values }));
  }

  // Handle live preview on form changes
  form.querySelectorAll("input, select").forEach((input) => {
    input.addEventListener("change", () => {
      applyPreview(getCurrentValues());
      // Show alert if there are unsaved changes
      if (hasUnsavedChanges()) {
        showUnsavedChangesAlert();
      }
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

      // Apply preview
      applyPreview(defaults);
      
      // Show alert if there are unsaved changes
      if (hasUnsavedChanges()) {
        showUnsavedChangesAlert();
      }
    });
  }

  // Initialize with current values
  function initializeUI() {
    const values = getCurrentValues();
    applyPreview(values);

    // Store initial values for comparison
    initialValues = JSON.parse(JSON.stringify(values));

    // Ensure theme options are correctly set up on page load
    // Remove any stray 'selected' classes and ensure 'active' is on the saved option
    document.querySelectorAll('.theme-option').forEach(option => {
      option.classList.remove('selected');
      const radio = option.querySelector('input[type="radio"]');
      if (radio && radio.checked) {
        // This is the saved theme - ensure it has 'active' class
        option.classList.add('active');
      } else {
        // Remove active from non-saved themes
        option.classList.remove('active');
      }
    });

    // Ensure color options are correctly set up on page load
    // Remove any stray 'selected' classes from color options
    document.querySelectorAll('.color-option').forEach(option => {
      option.classList.remove('selected');
    });

    // Highlight active accent color
    const activeAccent = values.accent_color;
    document.querySelectorAll(".accent-color-option").forEach((option) => {
      const radio = option.querySelector('input[type="radio"]');
      if (radio && radio.value === activeAccent) {
        radio.checked = true;
      }
    });
  }

  // Auto-dismiss success messages after 5 seconds
  function autoDismissMessages() {
    const messagesContainer = document.getElementById("messages-container");
    if (messagesContainer) {
      // Scroll to top to show messages
      window.scrollTo({ top: 0, behavior: 'smooth' });

      const successAlerts = messagesContainer.querySelectorAll(".alert-success");
      successAlerts.forEach((alert) => {
        setTimeout(() => {
          const bsAlert = new bootstrap.Alert(alert);
          bsAlert.close();
        }, 5000); // 5 seconds
      });

      // Error messages stay visible (don't auto-dismiss)
      // but we still want to scroll to them
      const errorAlerts = messagesContainer.querySelectorAll(".alert-danger");
      if (errorAlerts.length > 0) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }
  }

  // Call initialize after DOM is loaded and when form values change
  document.addEventListener("DOMContentLoaded", () => {
    // Auto-dismiss success messages
    autoDismissMessages();

    initializeUI();

    // Add click handlers for theme and accent color options
    document.querySelectorAll('.theme-option').forEach(option => {
      option.addEventListener('click', function() {
        // Find the radio button within this option
        const radio = this.querySelector('input[type="radio"]');
        if (radio) {
          const wasChecked = radio.checked;

          // Check the radio button
          radio.checked = true;

          // Update selected state on all theme options (for unsaved selection)
          // Remove both 'active' and 'selected' from all options
          document.querySelectorAll('.theme-option').forEach(opt => {
            opt.classList.remove('active', 'selected');
          });
          // Add 'selected' to the clicked option (highlighted state)
          this.classList.add('selected');

          // Only trigger change event if it wasn't already checked
          if (!wasChecked) {
            // Trigger change event to update preview
            radio.dispatchEvent(new Event('change', { bubbles: true }));
          }

          // Show alert if there are unsaved changes
          if (hasUnsavedChanges()) {
            showUnsavedChangesAlert();
          }
        }
      });
    });

    document.querySelectorAll('.color-option').forEach(option => {
      option.addEventListener('click', function() {
        const radio = this.querySelector('input[type="radio"]');
        if (radio) {
          const wasChecked = radio.checked;

          // Check the radio button
          radio.checked = true;

          // Update selected state on all color options
          // Remove 'selected' class from all (color options don't use 'active' class)
          document.querySelectorAll('.color-option').forEach(opt => {
            opt.classList.remove('selected');
          });
          // Add 'selected' to the clicked option (highlighted state)
          this.classList.add('selected');

          // Only trigger change event if it wasn't already checked
          if (!wasChecked) {
            // Trigger change event
            radio.dispatchEvent(new Event('change', { bubbles: true }));
          }

          // Show alert if there are unsaved changes
          if (hasUnsavedChanges()) {
            showUnsavedChangesAlert();
          }
        }
      });
    });
  });

  // Handle form submission - save to localStorage before submitting
  form.addEventListener("submit", function () {
    // Get current theme values and save to localStorage
    const themeValues = getCurrentValues();
    localStorage.setItem("theme", JSON.stringify(themeValues));

    // Hide unsaved changes alert
    hideUnsavedChangesAlert();
    
    // Update initial values to current values
    initialValues = JSON.parse(JSON.stringify(themeValues));

    // The form will submit normally to the server
    // Django will save to database and reload the page
  });
})();
