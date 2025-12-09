(function() {
  'use strict';

  let calendar = null;

  document.addEventListener('DOMContentLoaded', function() {
    // Initialize task list and calendar view
    console.log('[ListCalendar] Initialized');

    // View toggle functionality
    const viewToggleButtons = document.querySelectorAll('.view-toggle button');
    const listView = document.getElementById('listView');
    const calendarView = document.getElementById('calendarView');

    viewToggleButtons.forEach(button => {
      button.addEventListener('click', function() {
        const view = this.dataset.view;

        // Update active button
        viewToggleButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');

        // Toggle views
        if (view === 'list') {
          listView.classList.remove('d-none');
          calendarView.classList.add('d-none');
        } else if (view === 'calendar') {
          listView.classList.add('d-none');
          calendarView.classList.remove('d-none');
          // Initialize calendar if not already done
          if (!calendar) {
            initializeCalendar();
          }
        }
      });
    });

    // Initialize FullCalendar
    function initializeCalendar() {
      const calendarEl = document.getElementById('calendarView');
      if (!calendarEl) return;

      // Get tasks data from the template
      const tasksData = document.getElementById('tasks-data');
      let tasks = [];

      if (tasksData) {
        try {
          tasks = JSON.parse(tasksData.textContent);
        } catch (e) {
          console.error('[ListCalendar] Error parsing tasks data:', e);
        }
      }

      // Convert tasks to calendar events
      const events = tasks.map(task => {
        let color = '#6c757d'; // default gray

        switch(task.status) {
          case 'todo':
            color = '#6c757d';
            break;
          case 'in_progress':
            color = '#007bff';
            break;
          case 'review':
            color = '#ffc107';
            break;
          case 'completed':
            color = '#28a745';
            break;
        }

        return {
          title: task.title,
          start: task.deadline || new Date().toISOString().split('T')[0],
          backgroundColor: color,
          borderColor: color,
          extendedProps: {
            id: task.id,
            status: task.status,
            content: task.content
          }
        };
      });

      // Clear and recreate calendar container
      const cardBody = calendarEl.querySelector('.card-body');
      cardBody.innerHTML = '<div id="fullcalendar"></div>';

      const fullcalendarEl = document.getElementById('fullcalendar');

      // Initialize FullCalendar
      if (typeof FullCalendar !== 'undefined') {
        calendar = new FullCalendar.Calendar(fullcalendarEl, {
          initialView: 'dayGridMonth',
          headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
          },
          events: events,
          height: 'auto',
          eventClick: function(info) {
            const taskId = info.event.extendedProps.id;
            if (taskId) {
              loadTaskModal(taskId);
            }
          },
          eventDidMount: function(info) {
            // Add tooltip
            info.el.title = info.event.extendedProps.content || info.event.title;
          }
        });

        calendar.render();
      } else {
        console.error('[ListCalendar] FullCalendar not loaded');
        cardBody.innerHTML = '<div class="alert alert-warning m-3">Calendar library not loaded. Please refresh the page.</div>';
      }
    }

    // Handle task modal views
    const viewTaskLinks = document.querySelectorAll('[data-task-id]');
    viewTaskLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        const taskId = this.dataset.taskId;
        if (taskId) {
          loadTaskModal(taskId);
        }
      });
    });

    // Load task details in modal
    async function loadTaskModal(taskId) {
      try {
        const response = await fetch(`/dashboard/tasks/${taskId}/view/`);
        if (response.ok) {
          const html = await response.text();
          const modalContent = document.getElementById('viewTaskModalContent');
          if (modalContent) {
            modalContent.innerHTML = html;

            // Execute inline scripts (innerHTML doesn't execute them automatically)
            const scripts = modalContent.querySelectorAll('script');
            scripts.forEach(script => {
              const newScript = document.createElement('script');
              if (script.src) {
                newScript.src = script.src;
              } else {
                newScript.textContent = script.textContent;
              }
              document.body.appendChild(newScript);
              document.body.removeChild(newScript);
            });

            const modal = new bootstrap.Modal(document.getElementById('viewTaskModal'));
            modal.show();
          }
        }
      } catch (error) {
        console.error('[ListCalendar] Error loading task:', error);
      }
    }

    // Handle filter changes
    const filterInputs = document.querySelectorAll('.filter-input, .filter-select');
    filterInputs.forEach(input => {
      input.addEventListener('change', function() {
        this.form.submit();
      });
    });

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
      const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
      tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });
    }
  });
})();
