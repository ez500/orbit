(function() {
  'use strict';

  // Get CSRF token
  function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.querySelector('meta[name="csrf-token"]')?.content ||
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
  }

  // Make loadEditFormData globally accessible
  window.loadEditFormData = function() {
    const teamSelect = document.getElementById('editTaskTeam');
    const projectSelect = document.getElementById('editTaskProject');
    const usersSelect = document.getElementById('editTaskUsers');

    if (!window.currentTaskData) {
      console.error('[EditTask] Current task data not available, retrying...');
      // Retry after a short delay
      setTimeout(() => {
        if (window.currentTaskData) {
          console.log('[EditTask] Task data now available, loading...');
          window.loadEditFormData();
        } else {
          console.error('[EditTask] Task data still not available after retry');
        }
      }, 200);
      return;
    }

    console.log('[EditTask] Loading edit form data with:', window.currentTaskData);

    // Load available teams and projects from the page
    loadTeamsAndProjects();

    // Load users based on current team or project
    if (window.currentTaskData.team) {
      loadTeamMembers(window.currentTaskData.team, usersSelect);
    } else if (window.currentTaskData.project) {
      loadProjectMembers(window.currentTaskData.project, usersSelect);
    } else {
      // No team or project - load the current task's assigned users directly
      loadCurrentTaskUsers(usersSelect);
    }
  };

  // Make toggleEditMode globally accessible (overriding the one in template)
  window.toggleEditMode = function() {
    const viewMode = document.getElementById('viewMode');
    const editMode = document.getElementById('editMode');

    if (!viewMode || !editMode) {
      console.error('[EditTask] View or Edit mode elements not found');
      return;
    }

    if (viewMode.style.display === 'none') {
      viewMode.style.display = 'block';
      editMode.style.display = 'none';
    } else {
      viewMode.style.display = 'none';
      editMode.style.display = 'block';

      // Give a small delay to ensure DOM is ready and scripts have executed
      setTimeout(() => {
        // Load teams, projects, and users for the edit form
        if (typeof loadEditFormData === 'function') {
          loadEditFormData();
        }

        // Setup handlers after switching to edit mode
        setupEditTaskHandlers();
      }, 100);
    }
  };

  // Initialize edit task functionality
  document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners for when modal content is loaded
    const viewTaskModal = document.getElementById('viewTaskModal');
    if (viewTaskModal) {
      // Listen for when the modal content is loaded
      const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
            // Modal content was added, setup handlers
            const saveBtn = document.getElementById('saveTaskBtn');
            if (saveBtn && !saveBtn.hasAttribute('data-handler-attached')) {
              setupEditTaskHandlers();
            }
          }
        });
      });

      // Observe the modal content container
      const modalContent = document.getElementById('viewTaskModalContent');
      if (modalContent) {
        observer.observe(modalContent, { childList: true, subtree: true });
      }
    }
  });

  function setupEditTaskHandlers() {
    const saveTaskBtn = document.getElementById('saveTaskBtn');
    const editTaskForm = document.getElementById('editTaskForm');
    const teamSelect = document.getElementById('editTaskTeam');
    const projectSelect = document.getElementById('editTaskProject');
    const usersSelect = document.getElementById('editTaskUsers');

    if (!saveTaskBtn || !editTaskForm) {
      return; // Elements not in DOM yet
    }

    // Mark handler as attached to prevent duplicate setup
    if (saveTaskBtn.hasAttribute('data-handler-attached')) {
      return;
    }
    saveTaskBtn.setAttribute('data-handler-attached', 'true');

    // Load team/project members when selection changes
    if (teamSelect) {
      teamSelect.addEventListener('change', function() {
        if (this.value) {
          loadTeamMembers(this.value, usersSelect);
          // Clear project selection
          if (projectSelect) projectSelect.value = '';
        }
      });
    }

    if (projectSelect) {
      projectSelect.addEventListener('change', function() {
        if (this.value) {
          loadProjectMembers(this.value, usersSelect);
          // Clear team selection
          if (teamSelect) teamSelect.value = '';
        }
      });
    }

    // Handle save task button click
    saveTaskBtn.addEventListener('click', async function() {
      const taskId = editTaskForm.dataset.taskId;

      const taskData = {
        title: document.getElementById('editTaskTitle').value.trim(),
        content: document.getElementById('editTaskContent').value.trim(),
        deadline: document.getElementById('editTaskDeadline').value || null,
        status: document.getElementById('editTaskStatus').value,
        team: teamSelect?.value || null,
        project: projectSelect?.value || null,
        users: Array.from(usersSelect?.selectedOptions || []).map(opt => parseInt(opt.value))
      };

      // Validate required fields
      if (!taskData.title) {
        showNotification('Please enter a task title', 'danger');
        return;
      }

      if (!taskData.users || taskData.users.length === 0) {
        showNotification('Please select at least one assignee', 'danger');
        return;
      }

      // Disable button during submission
      saveTaskBtn.disabled = true;
      const originalText = saveTaskBtn.innerHTML;
      saveTaskBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';

      try {
        const response = await fetch(`/dashboard/api/tasks/${taskId}/update/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify(taskData)
        });

        if (response.ok) {
          const result = await response.json();
          showNotification('Task updated successfully!', 'success');

          // Close modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('viewTaskModal'));
          if (modal) {
            modal.hide();
          }

          // Reload page to show updated task
          setTimeout(() => {
            window.location.reload();
          }, 500);
        } else {
          const error = await response.json();
          showNotification('Error updating task: ' + (error.error || error.message || 'Unknown error'), 'danger');
        }
      } catch (error) {
        console.error('[EditTask] Error:', error);
        showNotification('Failed to update task. Please try again.', 'danger');
      } finally {
        // Re-enable button
        saveTaskBtn.disabled = false;
        saveTaskBtn.innerHTML = originalText;
      }
    });
  }

  // Load teams and projects from the main form
  function loadTeamsAndProjects() {
    const mainTeamSelect = document.getElementById('taskTeam');
    const mainProjectSelect = document.getElementById('taskProject');
    const editTeamSelect = document.getElementById('editTaskTeam');
    const editProjectSelect = document.getElementById('editTaskProject');

    if (mainTeamSelect && editTeamSelect) {
      // Copy teams from main form to edit form
      editTeamSelect.innerHTML = '<option value="">None</option>';
      Array.from(mainTeamSelect.options).forEach(opt => {
        if (opt.value) {
          const newOpt = opt.cloneNode(true);
          if (window.currentTaskData.team && parseInt(opt.value) === window.currentTaskData.team) {
            newOpt.selected = true;
          }
          editTeamSelect.appendChild(newOpt);
        }
      });
    }

    if (mainProjectSelect && editProjectSelect) {
      // Copy projects from main form to edit form
      editProjectSelect.innerHTML = '<option value="">None</option>';
      Array.from(mainProjectSelect.options).forEach(opt => {
        if (opt.value) {
          const newOpt = opt.cloneNode(true);
          if (window.currentTaskData.project && parseInt(opt.value) === window.currentTaskData.project) {
            newOpt.selected = true;
          }
          editProjectSelect.appendChild(newOpt);
        }
      });
    }
  }

  // Load team members
  async function loadTeamMembers(teamId, usersSelect) {
    try {
      const response = await fetch('/dashboard/api/project-team-members/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ team: teamId })
      });

      if (response.ok) {
        const members = await response.json();
        populateUserSelect(members, usersSelect);
      }
    } catch (error) {
      console.error('[EditTask] Error loading team members:', error);
    }
  }

  // Load project members
  async function loadProjectMembers(projectId, usersSelect) {
    try {
      const response = await fetch('/dashboard/api/project-team-members/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ project: projectId })
      });

      if (response.ok) {
        const members = await response.json();
        populateUserSelect(members, usersSelect);
      }
    } catch (error) {
      console.error('[EditTask] Error loading project members:', error);
    }
  }

  // Load current task's assigned users
  function loadCurrentTaskUsers(usersSelect) {
    if (!usersSelect) {
      console.error('[EditTask] usersSelect element not found');
      return;
    }

    console.log('[EditTask] Loading current task users', window.currentTaskData);

    // Clear the select
    usersSelect.innerHTML = '';

    // Populate with users from currentTaskData
    if (window.currentTaskData.userDetails && window.currentTaskData.userDetails.length > 0) {
      console.log('[EditTask] Found user details:', window.currentTaskData.userDetails);
      window.currentTaskData.userDetails.forEach(user => {
        const option = document.createElement('option');
        option.value = user.id;
        // Use fullName if available and not empty, otherwise use username
        const displayName = (user.fullName && user.fullName.trim()) ? user.fullName : user.username;
        option.textContent = displayName;
        option.selected = true; // Select all current users
        usersSelect.appendChild(option);
        console.log('[EditTask] Added user option:', displayName);
      });
    } else {
      console.log('[EditTask] No user details found, falling back to API');
      // Fallback: if no user details, try to load current user from API
      loadCurrentUserFromAPI(usersSelect);
    }
  }

  // Load current user only (fallback)
  async function loadCurrentUserFromAPI(usersSelect) {
    try {
      const response = await fetch('/dashboard/api/project-team-members/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        const members = await response.json();
        populateUserSelect(members, usersSelect);
      }
    } catch (error) {
      console.error('[EditTask] Error loading current user:', error);
    }
  }

  // Populate user select with members
  function populateUserSelect(members, usersSelect) {
    if (!usersSelect) return;

    usersSelect.innerHTML = '';

    Object.values(members).forEach(member => {
      const option = document.createElement('option');
      option.value = member.id;
      option.textContent = member.username || `${member.first_name} ${member.last_name}`;

      // Select if user was previously assigned to this task
      if (window.currentTaskData.users && window.currentTaskData.users.includes(member.id)) {
        option.selected = true;
      }

      usersSelect.appendChild(option);
    });
  }

  // Show notification
  function showNotification(message, type = 'info') {
    const container = document.querySelector('.container-fluid') || document.querySelector('.container');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.insertBefore(alert, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      alert.remove();
    }, 5000);
  }
})();
