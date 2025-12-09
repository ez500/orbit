/**
 * Edit Task Functionality
 * Handles editing tasks from the task modal
 */

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
  async function loadTeamsAndProjects() {
    const mainTeamSelect = document.getElementById('taskTeam');
    const mainProjectSelect = document.getElementById('taskProject');
    const editTeamSelect = document.getElementById('editTaskTeam');
    const editProjectSelect = document.getElementById('editTaskProject');
    const taskData = window.currentTaskData || {};

    // If main selects exist on the page, copy their options into the edit form
    if (mainTeamSelect && mainProjectSelect && editTeamSelect && editProjectSelect) {
      // Copy teams
      editTeamSelect.innerHTML = '<option value="">None</option>';
      Array.from(mainTeamSelect.options).forEach(opt => {
        const newOpt = opt.cloneNode(true);
        if (opt.value && taskData.team && parseInt(opt.value, 10) === taskData.team) {
          newOpt.selected = true;
        }
        editTeamSelect.appendChild(newOpt);
      });

      // Copy projects
      editProjectSelect.innerHTML = '<option value="">None</option>';
      Array.from(mainProjectSelect.options).forEach(opt => {
        const newOpt = opt.cloneNode(true);
        if (opt.value && taskData.project && parseInt(opt.value, 10) === taskData.project) {
          newOpt.selected = true;
        }
        editProjectSelect.appendChild(newOpt);
      });

      return;
    }

    // Otherwise fetch via API
    await fetchTeamsAndProjects();
  }

  // Fetch teams and projects from API
  async function fetchTeamsAndProjects() {
    const editTeamSelect = document.getElementById('editTaskTeam');
    const editProjectSelect = document.getElementById('editTaskProject');
    const taskData = window.currentTaskData;

    try {
      // Fetch user's teams and projects
      const response = await fetch('/dashboard/api/user-teams-projects/', {
        headers: {
          'X-CSRFToken': getCSRFToken()
        }
      });

      if (response.ok) {
        const data = await response.json();

        // Populate teams
        if (editTeamSelect && data.teams) {
          editTeamSelect.innerHTML = '<option value="">None</option>';
          data.teams.forEach(team => {
            const option = document.createElement('option');
            option.value = team.id;
            option.textContent = team.name;
            if (taskData.team && team.id === taskData.team) {
              option.selected = true;
            }
            editTeamSelect.appendChild(option);
          });
        }

        // Populate projects
        if (editProjectSelect && data.projects) {
          editProjectSelect.innerHTML = '<option value="">None</option>';
          data.projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            if (taskData.project && project.id === taskData.project) {
              option.selected = true;
            }
            editProjectSelect.appendChild(option);
          });
        }
      }
    } catch (error) {
      console.error('[EditTask] Error fetching teams/projects:', error);
      // Fallback: just set None option
      if (editTeamSelect) editTeamSelect.innerHTML = '<option value="">None</option>';
      if (editProjectSelect) editProjectSelect.innerHTML = '<option value="">None</option>';
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

  // Initialize when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    // Setup event listeners for save button
    document.addEventListener('click', function(e) {
      if (e.target && e.target.id === 'saveTaskBtn') {
        handleSaveTask();
      }
    });

    // Team selection change
    document.addEventListener('change', function(e) {
      if (e.target && e.target.id === 'editTaskTeam') {
        const teamId = e.target.value;
        if (teamId) {
          loadTeamMembers(teamId);
          // Clear project selection
          const projectSelect = document.getElementById('editTaskProject');
          if (projectSelect) projectSelect.value = '';
        }
      }
    });

    // Project selection change
    document.addEventListener('change', function(e) {
      if (e.target && e.target.id === 'editTaskProject') {
        const projectId = e.target.value;
        if (projectId) {
          loadProjectMembers(projectId);
          // Clear team selection
          const teamSelect = document.getElementById('editTaskTeam');
          if (teamSelect) teamSelect.value = '';
        }
      }
    });
  });

  // Handle save task
  async function handleSaveTask() {
    const editTaskForm = document.getElementById('editTaskForm');
    if (!editTaskForm) return;

    const taskId = editTaskForm.dataset.taskId;
    const teamSelect = document.getElementById('editTaskTeam');
    const projectSelect = document.getElementById('editTaskProject');
    const usersSelect = document.getElementById('editTaskUsers');

    // Get deadline and convert from local timezone to UTC
    const deadlineValue = document.getElementById('editTaskDeadline').value;
    const deadlineUTC = deadlineValue && window.TimezoneUtils ?
      window.TimezoneUtils.localToUtc(deadlineValue) : deadlineValue;

    const taskData = {
      title: document.getElementById('editTaskTitle').value.trim(),
      content: document.getElementById('editTaskContent').value.trim(),
      deadline: deadlineUTC || null,
      status: document.getElementById('editTaskStatus').value,
      team: teamSelect?.value || null,
      project: projectSelect?.value || null,
      users: Array.from(usersSelect?.selectedOptions || []).map(opt => parseInt(opt.value))
    };

    // Validate
    if (!taskData.title) {
      showNotification('Please enter a task title', 'danger');
      return;
    }

    if (!taskData.users || taskData.users.length === 0) {
      showNotification('Please select at least one assignee', 'danger');
      return;
    }

    // Disable button
    const saveBtn = document.getElementById('saveTaskBtn');
    saveBtn.disabled = true;
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';

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
        showNotification('Task updated successfully!', 'success');

        // Close modal properly
        const modalElement = document.getElementById('viewTaskModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
          modal.hide();
          // Remove backdrop and restore body
          setTimeout(() => {
            document.body.classList.remove('modal-open');
            document.body.style.removeProperty('padding-right');
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
          }, 150);
        }

        // Reload page
        setTimeout(() => {
          window.location.reload();
        }, 500);
      } else {
        const error = await response.json();
        showNotification('Error: ' + (error.error || error.message || 'Unknown error'), 'danger');
      }
    } catch (error) {
      console.error('[EditTask] Error:', error);
      showNotification('Failed to update task. Please try again.', 'danger');
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerHTML = originalText;
    }
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
