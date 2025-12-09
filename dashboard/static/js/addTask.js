 (function() {
  'use strict';

  // Get CSRF token
  function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
  }

  // Initialize add task functionality
  document.addEventListener('DOMContentLoaded', function() {
    const addTaskBtn = document.getElementById('addTaskBtn');
    const addTaskForm = document.getElementById('addTaskForm');
    const teamSelect = document.getElementById('taskTeam');
    const projectSelect = document.getElementById('taskProject');
    const usersSelect = document.getElementById('taskUsers');

    if (!addTaskBtn || !addTaskForm) {
      console.error('[AddTask] Required elements not found');
      return;
    // HEAD implementation kept: feature-rich Add Task script
    (function() {
      'use strict';

      // Get CSRF token
      function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
      }

      // Initialize add task functionality
      document.addEventListener('DOMContentLoaded', function() {
        const addTaskBtn = document.getElementById('addTaskBtn');
        const addTaskForm = document.getElementById('addTaskForm');
        const teamSelect = document.getElementById('taskTeam');
        const projectSelect = document.getElementById('taskProject');
        const usersSelect = document.getElementById('taskUsers');

        if (!addTaskBtn || !addTaskForm) {
          console.error('[AddTask] Required elements not found');
          return;
        }

        // Load team/project members when selection changes
        if (teamSelect) {
          teamSelect.addEventListener('change', function() {
            if (this.value) {
             (function() {
              'use strict';

              // Get CSRF token from cookie or hidden input
              function getCSRFToken() {
                return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                       document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
              }

              document.addEventListener('DOMContentLoaded', function() {
                const addTaskBtn = document.getElementById('addTaskBtn');
                const addTaskForm = document.getElementById('addTaskForm');
                const teamSelect = document.getElementById('taskTeam');
                const projectSelect = document.getElementById('taskProject');
                const usersSelect = document.getElementById('taskUsers');

                if (!addTaskBtn || !addTaskForm) {
                  console.error('[AddTask] Required elements not found');
                  return;
                }

                // Load team/project members when selection changes
                if (teamSelect) {
                  teamSelect.addEventListener('change', function() {
                    if (this.value) loadTeamMembers(this.value);
                    else resetUserSelect();
                  });
                }

                if (projectSelect) {
                  projectSelect.addEventListener('change', function() {
                    if (this.value) loadProjectMembers(this.value);
                    else resetUserSelect();
                  });
                }

                // Handle add task button click
                addTaskBtn.addEventListener('click', async function() {
                  const titleEl = document.getElementById('taskTitle');
                  const contentEl = document.getElementById('taskContent');
                  const deadlineEl = document.getElementById('taskDeadline');
                  const statusEl = document.getElementById('taskStatus');

                  const taskData = {
                    title: titleEl ? titleEl.value.trim() : '',
                    content: contentEl ? contentEl.value.trim() : '',
                    deadline: deadlineEl ? (deadlineEl.value || null) : null,
                    status: statusEl ? statusEl.value : null,
                    team: teamSelect ? (teamSelect.value || null) : null,
                    project: projectSelect ? (projectSelect.value || null) : null,
                    users: usersSelect ? Array.from(usersSelect.selectedOptions).map(opt => parseInt(opt.value)) : []
                  };

                  if (!taskData.title) {
                    showNotification('Please enter a task title', 'danger');
                    return;
                  }

                  if (!taskData.users || taskData.users.length === 0) {
                    showNotification('Please select at least one assignee', 'danger');
                    return;
                  }

                  // Disable button during submission
                  addTaskBtn.disabled = true;
                  const originalHtml = addTaskBtn.innerHTML;
                  addTaskBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';

                  try {
                    const response = await fetch('/dashboard/api/tasks/', {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                      },
                      body: JSON.stringify(taskData)
                    });

                    if (response.ok) {
                      showNotification('Task created successfully!', 'success');
                      addTaskForm.reset();
                      const modalEl = document.getElementById('addTaskModal');
                      const modal = modalEl ? bootstrap.Modal.getInstance(modalEl) : null;
                      if (modal) modal.hide();
                      setTimeout(() => window.location.reload(), 500);
                    } else {
                      let errorText = 'Unknown error';
                      try { const err = await response.json(); errorText = err.message || JSON.stringify(err); } catch(e){}
                      showNotification('Error creating task: ' + errorText, 'danger');
                    }
                  } catch (error) {
                    console.error('[AddTask] Error:', error);
                    showNotification('Failed to create task. Please try again.', 'danger');
                  } finally {
                    addTaskBtn.disabled = false;
                    addTaskBtn.innerHTML = originalHtml;
                  }
                });

                // Load team members
                async function loadTeamMembers(teamId) {
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
                      populateUserSelect(members);
                    }
                  } catch (error) {
                    console.error('[AddTask] Error loading team members:', error);
                  }
                }

                // Load project members (same endpoint)
                async function loadProjectMembers(projectId) {
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
                      populateUserSelect(members);
                    }
                  } catch (error) {
                    console.error('[AddTask] Error loading project members:', error);
                  }
                }

                // Populate user select with members
                function populateUserSelect(members) {
                  if (!usersSelect) return;
                  usersSelect.innerHTML = '';

                  Object.values(members || {}).forEach(member => {
                    const option = document.createElement('option');
                    option.value = member.id;
                    option.textContent = member.username || `${member.first_name || ''} ${member.last_name || ''}`.trim();
                    usersSelect.appendChild(option);
                  });

                  // Auto-select all members
                  Array.from(usersSelect.options).forEach(opt => opt.selected = true);
                }

                // Reset user select to first available option (if any)
                function resetUserSelect() {
                  if (!usersSelect) return;
                  const firstOption = usersSelect.options[0];
                  const currentUserId = firstOption ? firstOption.value : null;
                  const currentUsername = firstOption ? firstOption.textContent : '';

                  usersSelect.innerHTML = '';
                  if (currentUserId) {
                    const option = document.createElement('option');
                    option.value = currentUserId;
                    option.textContent = currentUsername || 'You';
                    option.selected = true;
                    usersSelect.appendChild(option);
                  }
                }

                // Show notification
                function showNotification(message, type = 'info') {
                  const container = document.querySelector('.container-fluid') || document.querySelector('.container');
                  if (!container) return;

                  const alert = document.createElement('div');
                  alert.className = `alert alert-${type} alert-dismissible fade show`;
                  alert.role = 'alert';
                  alert.innerHTML = `\n        ${message}\n        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>\n      `;

                  container.insertBefore(alert, container.firstChild);
                  setTimeout(() => alert.remove(), 5000);
                }
              });
            })();
