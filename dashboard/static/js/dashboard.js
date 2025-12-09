(function() {
  'use strict';

  class Dashboard {
    constructor() {
      this.widgets = [];
      this.updateIntervals = {};
      this.init();
    }

    init() {
      this.loadWidgets();
      this.setupEventListeners();
      console.log('[Dashboard] Initialized');
    }

    setupEventListeners() {
      // Auto-save on window unload
      window.addEventListener('beforeunload', () => {
        this.saveLayout(false);
      });
    }

    async loadWidgets() {
      try {
        const response = await fetch('/dashboard/api/widgets/');
        if (response.ok) {
          const data = await response.json();
          this.widgets = data.widgets || [];
          this.renderWidgets();
        } else {
          console.log('[Dashboard] No saved widgets, starting fresh');
        }
      } catch (error) {
        console.error('[Dashboard] Error loading widgets:', error);
      }
    }

    renderWidgets() {
      const container = document.getElementById('dashboard-widgets');
      container.innerHTML = '';

      if (this.widgets.length === 0) {
        return;
      }

      this.widgets.forEach(widget => {
        this.renderWidget(widget);
      });
    }

    renderWidget(widgetConfig) {
      const container = document.getElementById('dashboard-widgets');
      const widgetEl = this.createWidgetElement(widgetConfig);
      container.appendChild(widgetEl);

      // Load widget data
      this.loadWidgetData(widgetConfig.type, widgetEl.id);

      // Setup auto-refresh
      if (widgetConfig.autoRefresh !== false) {
        this.setupAutoRefresh(widgetConfig.type, widgetEl.id);
      }
    }

    createWidgetElement(config) {
      const col = document.createElement('div');
      col.className = config.size || 'col-md-6';

      const widgetId = `widget-${config.type}-${Date.now()}`;
      col.id = widgetId;

      const card = document.createElement('div');
      card.className = 'card dashboard-widget';

      const header = this.createWidgetHeader(config, widgetId);
      const body = this.createWidgetBody(config);

      card.appendChild(header);
      card.appendChild(body);
      col.appendChild(card);

      return col;
    }

    createWidgetHeader(config, widgetId) {
      const header = document.createElement('div');
      header.className = 'card-header';

      const title = document.createElement('h6');
      title.className = 'mb-0';
      title.innerHTML = `<i class="${config.icon || 'fas fa-chart-bar'} me-2"></i>${config.title}`;

      const actions = document.createElement('div');
      actions.className = 'widget-actions';

      // Refresh button
      const refreshBtn = document.createElement('button');
      refreshBtn.className = 'btn btn-sm';
      refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
      refreshBtn.onclick = () => this.refreshWidget(config.type, widgetId);

      // Remove button
      const removeBtn = document.createElement('span');
      removeBtn.className = 'widget-remove';
      removeBtn.innerHTML = '<i class="fas fa-times"></i>';
      removeBtn.onclick = () => this.removeWidget(widgetId);

      actions.appendChild(refreshBtn);
      actions.appendChild(removeBtn);

      header.appendChild(title);
      header.appendChild(actions);

      return header;
    }

    createWidgetBody(config) {
      const body = document.createElement('div');
      body.className = 'card-body';
      body.innerHTML = '<div class="widget-loading"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
      return body;
    }

    async loadWidgetData(type, widgetId) {
      const widget = document.getElementById(widgetId);
      if (!widget) return;

      const body = widget.querySelector('.card-body');

      try {
        const response = await fetch(`/dashboard/api/widget-data/${type}/`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        body.innerHTML = this.renderWidgetContent(type, data);
      } catch (error) {
        console.error(`[Dashboard] Error loading ${type} widget:`, error);
        body.innerHTML = `<div class="alert alert-danger m-3">Error loading widget data</div>`;
      }
    }

    renderWidgetContent(type, data) {
      switch(type) {
        case 'tasks':
          return this.renderTasksWidget(data);
        case 'stats':
          return this.renderStatsWidget(data);
        case 'team':
          return this.renderTeamWidget(data);
        case 'calendar':
          return this.renderCalendarWidget(data);
        case 'analytics':
          return this.renderAnalyticsWidget(data);
        case 'projectTimeline':
          return this.renderProjectTimelineWidget(data);
        case 'teamBoard':
          return this.renderTeamBoardWidget(data);
        default:
          return `<p class="text-muted p-3">Widget type "${type}" not implemented yet</p>`;
      }
    }

    renderTasksWidget(data) {
      if (!data.tasks || data.tasks.length === 0) {
        return '<p class="text-muted p-3 mb-0">No tasks found</p>';
      }

      let html = '<div class="task-list">';
      data.tasks.forEach(task => {
        html += `
          <div class="task-list-item">
            <div>
              <div class="task-title">${this.escapeHtml(task.title)}</div>
              <div class="task-meta">
                ${task.deadline ? `Due: ${new Date(task.deadline).toLocaleDateString()}` : 'No deadline'}
                ${task.project ? ` • ${this.escapeHtml(task.project)}` : ''}
                ${task.team ? ` • ${this.escapeHtml(task.team)}` : ''}
              </div>
            </div>
            <span class="task-status ${task.status}">${task.status.replace('_', ' ')}</span>
          </div>
        `;
      });
      html += '</div>';
      return html;
    }

    renderStatsWidget(data) {
      return `
        <div class="row g-3 p-3">
          <div class="col-md-6">
            <div class="widget-stat">
              <div class="widget-stat-value">${data.total_tasks || 0}</div>
              <div class="widget-stat-label">Total Tasks</div>
              ${data.tasks_change ? `<div class="widget-stat-change ${data.tasks_change > 0 ? 'positive' : 'negative'}">
                <i class="fas fa-${data.tasks_change > 0 ? 'arrow-up' : 'arrow-down'}"></i> ${Math.abs(data.tasks_change)}% this week
              </div>` : ''}
            </div>
          </div>
          <div class="col-md-6">
            <div class="widget-stat">
              <div class="widget-stat-value">${data.completed_tasks || 0}</div>
              <div class="widget-stat-label">Completed</div>
              ${data.completion_rate ? `<div class="widget-stat-change positive">
                ${data.completion_rate}% completion rate
              </div>` : ''}
            </div>
          </div>
          <div class="col-md-6">
            <div class="widget-stat">
              <div class="widget-stat-value">${data.active_projects || 0}</div>
              <div class="widget-stat-label">Active Projects</div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="widget-stat">
              <div class="widget-stat-value">${data.team_members || 0}</div>
              <div class="widget-stat-label">Team Members</div>
            </div>
          </div>
        </div>
      `;
    }

    renderTeamWidget(data) {
      if (!data.activities || data.activities.length === 0) {
        return '<p class="text-muted p-3 mb-0">No recent activity</p>';
      }

      let html = '<div class="activity-list">';
      data.activities.forEach(activity => {
        html += `
          <div class="activity-item">
            <div class="activity-icon">
              <i class="fas fa-${activity.icon || 'circle'}"></i>
            </div>
            <div class="activity-content">
              <div class="activity-title">${this.escapeHtml(activity.title)}</div>
              <div class="activity-time">${this.formatTimeAgo(activity.timestamp)}</div>
            </div>
          </div>
        `;
      });
      html += '</div>';
      return html;
    }

    renderCalendarWidget(data) {
      const calendarId = `calendar-${Date.now()}`;
      setTimeout(() => {
        if (typeof FullCalendar !== 'undefined') {
          const calendarEl = document.getElementById(calendarId);
          if (calendarEl) {
            const calendar = new FullCalendar.Calendar(calendarEl, {
              initialView: 'dayGridMonth',
              height: 400,
              events: data.events || []
            });
            calendar.render();
          }
        }
      }, 100);

      return `<div class="widget-calendar" id="${calendarId}"></div>`;
    }

    renderAnalyticsWidget(data) {
      return `
        <div class="widget-chart p-3">
          <canvas id="analytics-chart-${Date.now()}"></canvas>
        </div>
      `;
    }

    renderProjectTimelineWidget(data) {
      if (!data.projects || data.projects.length === 0) {
        return '<p class="text-muted p-3 mb-0">No active projects</p>';
      }

      let html = '<div class="p-3">';
      data.projects.forEach(project => {
        const progress = project.progress || 0;
        html += `
          <div class="mb-3">
            <div class="d-flex justify-content-between mb-2">
              <span class="fw-medium">${this.escapeHtml(project.name)}</span>
              <span class="text-muted">${progress}%</span>
            </div>
            <div class="progress">
              <div class="progress-bar" role="progressbar" style="width: ${progress}%" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            ${project.deadline ? `<small class="text-muted">Due: ${new Date(project.deadline).toLocaleDateString()}</small>` : ''}
          </div>
        `;
      });
      html += '</div>';
      return html;
    }

    renderTeamBoardWidget(data) {
      return `
        <div class="p-3">
          <div class="row g-3">
            <div class="col-md-4">
              <h6 class="mb-2">To Do</h6>
              <div class="bg-light p-2 rounded">
                ${data.todo ? data.todo.map(task => `
                  <div class="bg-white p-2 mb-2 rounded shadow-sm">
                    <small>${this.escapeHtml(task.title)}</small>
                  </div>
                `).join('') : '<p class="text-muted small mb-0">No tasks</p>'}
              </div>
            </div>
            <div class="col-md-4">
              <h6 class="mb-2">In Progress</h6>
              <div class="bg-light p-2 rounded">
                ${data.in_progress ? data.in_progress.map(task => `
                  <div class="bg-white p-2 mb-2 rounded shadow-sm">
                    <small>${this.escapeHtml(task.title)}</small>
                  </div>
                `).join('') : '<p class="text-muted small mb-0">No tasks</p>'}
              </div>
            </div>
            <div class="col-md-4">
              <h6 class="mb-2">Done</h6>
              <div class="bg-light p-2 rounded">
                ${data.completed ? data.completed.map(task => `
                  <div class="bg-white p-2 mb-2 rounded shadow-sm">
                    <small>${this.escapeHtml(task.title)}</small>
                  </div>
                `).join('') : '<p class="text-muted small mb-0">No tasks</p>'}
              </div>
            </div>
          </div>
        </div>
      `;
    }

    setupAutoRefresh(type, widgetId) {
      // Clear existing interval if any
      if (this.updateIntervals[widgetId]) {
        clearInterval(this.updateIntervals[widgetId]);
      }

      // Refresh every 30 seconds
      this.updateIntervals[widgetId] = setInterval(() => {
        this.refreshWidget(type, widgetId);
      }, 30000);
    }

    async refreshWidget(type, widgetId) {
      const widget = document.getElementById(widgetId);
      if (!widget) return;

      const card = widget.querySelector('.card');
      card.classList.add('widget-refreshing');

      await this.loadWidgetData(type, widgetId);

      setTimeout(() => {
        card.classList.remove('widget-refreshing');
      }, 500);
    }

    removeWidget(widgetId) {
      const widget = document.getElementById(widgetId);
      if (!widget) return;

      // Clear auto-refresh interval
      if (this.updateIntervals[widgetId]) {
        clearInterval(this.updateIntervals[widgetId]);
        delete this.updateIntervals[widgetId];
      }

      // Remove from widgets array
      const widgetType = widgetId.split('-')[1];
      this.widgets = this.widgets.filter(w => w.type !== widgetType);

      // Remove from DOM
      widget.remove();

      // Save layout
      this.saveLayout();
    }

    async saveLayout(showMessage = true) {
      const widgets = this.widgets.map(w => ({
        type: w.type,
        title: w.title,
        icon: w.icon,
        size: w.size,
        autoRefresh: w.autoRefresh
      }));

      try {
        const response = await fetch('/dashboard/api/widgets/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken()
          },
          body: JSON.stringify({ widgets })
        });

        if (response.ok && showMessage) {
          this.showNotification('Dashboard layout saved successfully', 'success');
        }
      } catch (error) {
        console.error('[Dashboard] Error saving layout:', error);
        if (showMessage) {
          this.showNotification('Error saving dashboard layout', 'danger');
        }
      }
    }

    getCSRFToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
             document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }

    showNotification(message, type = 'info') {
      const container = document.querySelector('.container-fluid');
      const alert = document.createElement('div');
      alert.className = `alert alert-${type} alert-dismissible fade show`;
      alert.role = 'alert';
      alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
      container.insertBefore(alert, container.firstChild);

      // Auto-dismiss after 3 seconds
      setTimeout(() => {
        alert.remove();
      }, 3000);
    }

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    formatTimeAgo(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      const seconds = Math.floor((now - date) / 1000);

      if (seconds < 60) return 'just now';
      if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
      if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
      return `${Math.floor(seconds / 86400)} days ago`;
    }
  }

  // Widget configurations
  const WIDGET_CONFIGS = {
    tasks: {
      type: 'tasks',
      title: 'My Tasks',
      icon: 'fas fa-tasks',
      size: 'col-md-6',
      autoRefresh: true
    },
    calendar: {
      type: 'calendar',
      title: 'Calendar',
      icon: 'fas fa-calendar',
      size: 'col-md-12',
      autoRefresh: false
    },
    stats: {
      type: 'stats',
      title: 'Statistics',
      icon: 'fas fa-chart-bar',
      size: 'col-md-6',
      autoRefresh: true
    },
    team: {
      type: 'team',
      title: 'Team Activity',
      icon: 'fas fa-users',
      size: 'col-md-6',
      autoRefresh: true
    },
    projectTimeline: {
      type: 'projectTimeline',
      title: 'Project Timeline',
      icon: 'fas fa-stream',
      size: 'col-md-12',
      autoRefresh: true
    },
    teamBoard: {
      type: 'teamBoard',
      title: 'Team Board',
      icon: 'fas fa-columns',
      size: 'col-md-12',
      autoRefresh: true
    },
    analytics: {
      type: 'analytics',
      title: 'Analytics',
      icon: 'fas fa-chart-line',
      size: 'col-md-12',
      autoRefresh: true
    }
  };

  // Global addWidget function
  window.addWidget = function(type) {
    if (!window.dashboard) {
      console.error('[Dashboard] Dashboard not initialized');
      return;
    }

    const config = WIDGET_CONFIGS[type];
    if (!config) {
      console.error(`[Dashboard] Unknown widget type: ${type}`);
      return;
    }

    // Check if widget already exists
    if (window.dashboard.widgets.some(w => w.type === type)) {
      window.dashboard.showNotification('Widget already added', 'warning');
      return;
    }

    window.dashboard.widgets.push(config);
    window.dashboard.renderWidget(config);
    window.dashboard.saveLayout();
  };

  // Initialize dashboard when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new Dashboard();
  });
})();
