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
          loadTeamMembers(this.value, 'team');
        } else {
          resetUserSelect();
        }
      });
    }

    if (projectSelect) {
      projectSelect.addEventListener('change', function() {
        if (this.value) {
          loadProjectMembers(this.value, 'project');
        } else {
          resetUserSelect();
        }
      });
    }

    // Handle add task button click
    addTaskBtn.addEventListener('click', async function() {
      const taskData = {
        title: document.getElementById('taskTitle').value.trim(),
        content: document.getElementById('taskContent').value.trim(),
        deadline: document.getElementById('taskDeadline').value || null,
        status: document.getElementById('taskStatus').value,
        team: teamSelect.value || null,
        project: projectSelect.value || null,
        users: Array.from(usersSelect.selectedOptions).map(opt => parseInt(opt.value))
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
      addTaskBtn.disabled = true;
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
          const result = await response.json();
          showNotification('Task created successfully!', 'success');

          // Reset form
          addTaskForm.reset();

          // Close modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('addTaskModal'));
          if (modal) {
            modal.hide();
          }

          // Reload page to show new task
          setTimeout(() => {
            window.location.reload();
          }, 500);
        } else {
          const error = await response.json();
          showNotification('Error creating task: ' + (error.message || 'Unknown error'), 'danger');
        }
      } catch (error) {
        console.error('[AddTask] Error:', error);
        showNotification('Failed to create task. Please try again.', 'danger');
      } finally {
        // Re-enable button
        addTaskBtn.disabled = false;
        addTaskBtn.innerHTML = 'Add Task';
      }
    });

    // Load team members
    async function loadTeamMembers(teamId, type) {
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

    // Load project members
    async function loadProjectMembers(projectId, type) {
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
      usersSelect.innerHTML = '';

      Object.values(members).forEach(member => {
        const option = document.createElement('option');
        option.value = member.id;
        option.textContent = member.username || `${member.first_name} ${member.last_name}`;
        usersSelect.appendChild(option);
      });

      // Auto-select all members
      Array.from(usersSelect.options).forEach(opt => opt.selected = true);
    }

    // Reset user select to current user only
    function resetUserSelect() {
      const currentUserId = usersSelect.options[0]?.value;
      const currentUsername = usersSelect.options[0]?.textContent;

      usersSelect.innerHTML = '';

      if (currentUserId) {
        const option = document.createElement('option');
        option.value = currentUserId;
        option.textContent = currentUsername;
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
  });
})();
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(data),
        }).then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        }).then(() => {
            alert('Task added successfully!');
            document.getElementById('addTaskForm').reset();
            const modalEl = document.getElementById('addTaskModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
            window.location.reload();
        }).catch(error => {
            console.error('Error:', error);
            alert('Failed to add task. Please try again.');
        });
    }

    document.getElementById('addTaskBtn').addEventListener("click", () => {
        addNewTask();
    })

    const deleteButton = document.getElementById('deleteTaskBtn');
    if (deleteButton) {
        deleteButton.addEventListener("click", event => event.preventDefault());
    }
});
>>>>>>> origin
