class DashboardManager {
  constructor() {
    this.widgets = [];
    this.draggedItem = null;

    this.widgetTemplates = {
      tasks: {
        title: "Recent Tasks",
        template: `
          <div class="col-md-6 col-xl-4 mb-4 dashboard-widget" draggable="true">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="card-title mb-0">Recent Tasks</h6>
                <button class="btn btn-link text-muted p-0" onclick="dashboard.removeWidget('tasks')">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="card-body">
                <div class="task-list">
                  <div class="task-item d-flex align-items-center mb-3">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox">
                    </div>
                    <div class="ms-3">
                      <p class="mb-0">Update dashboard layout</p>
                      <small class="text-muted">Due today</small>
                    </div>
                  </div>
                  <div class="task-item d-flex align-items-center">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox">
                    </div>
                    <div class="ms-3">
                      <p class="mb-0">Review pull requests</p>
                      <small class="text-muted">Due tomorrow</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      large: {
        wrapper: (id, content) => `
                    <div class="dashboard-widget col-12" data-widget-id="${id}" draggable="true">
                        <div class="card border-0 shadow-sm h-100">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <div class="d-flex align-items-center">
                                        <h6 class="card-title mb-0">${content.title}</h6>
                                        <span class="badge bg-light text-dark ms-2">Full Width</span>
                                    </div>
                                    <div class="widget-actions">
                                        <button class="btn btn-link text-muted p-0" onclick="window.dashboard.removeWidget('${id}', event)">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="widget-content">
                                    ${content.body}
                                </div>
                            </div>
                        </div>
                    </div>
                `,
      },
    };

    // Widget definitions with content generators
    this.widgetTypes = {
      // Large Widgets
      projectTimeline: {
        title: "Project Timeline",
        size: "large",
        template: `
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="card-title mb-0">Project Timeline</h6>
                <div class="dropdown">
                  <button class="btn btn-link btn-sm p-0 text-muted" data-bs-toggle="dropdown">
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                  <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" onclick="dashboard.removeWidget(event, 'projectTimeline')">Remove Widget</a></li>
                  </ul>
                </div>
              </div>
              <div class="timeline-container" style="height: 400px; overflow-y: auto;">
                <div class="timeline">
                  <div class="timeline-item">
                    <div class="timeline-point bg-success"></div>
                    <div class="timeline-content">
                      <h6 class="mb-1">Project Kickoff</h6>
                      <p class="mb-0 text-muted">Initial planning and team assignment completed</p>
                      <small class="text-muted">October 1, 2025</small>
                    </div>
                  </div>
                  <div class="timeline-item">
                    <div class="timeline-point bg-primary"></div>
                    <div class="timeline-content">
                      <h6 class="mb-1">Design Phase</h6>
                      <p class="mb-0 text-muted">UI/UX design and prototyping</p>
                      <small class="text-muted">October 5 - October 15</small>
                    </div>
                  </div>
                  <div class="timeline-item">
                    <div class="timeline-point bg-warning"></div>
                    <div class="timeline-content">
                      <h6 class="mb-1">Development Sprint 1</h6>
                      <p class="mb-0 text-muted">Core functionality implementation</p>
                      <small class="text-muted">October 15 - October 30</small>
                    </div>
                  </div>
                  <div class="timeline-item">
                    <div class="timeline-point bg-info"></div>
                    <div class="timeline-content">
                      <h6 class="mb-1">Testing Phase</h6>
                      <p class="mb-0 text-muted">Quality assurance and bug fixes</p>
                      <small class="text-muted">November 1 - November 10</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      teamBoard: {
        title: "Team Board",
        size: "large",
        template: `
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="card-title mb-0">Team Board</h6>
                <div class="dropdown">
                  <button class="btn btn-link btn-sm p-0 text-muted" data-bs-toggle="dropdown">
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                  <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" onclick="dashboard.removeWidget(event, 'teamBoard')">Remove Widget</a></li>
                  </ul>
                </div>
              </div>
              <div class="team-board">
                <div class="row g-3">
                  <div class="col-md-3">
                    <div class="board-column bg-light p-2 rounded">
                      <h6 class="column-title mb-3">To Do</h6>
                      <div class="task-card p-2 bg-white rounded mb-2 shadow-sm">
                        <h6 class="mb-1">Update API Documentation</h6>
                        <small class="text-muted d-block mb-2">High Priority</small>
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="badge bg-danger">Backend</span>
                          <img src="https://ui-avatars.com/api/?name=John+Doe" alt="John D." class="rounded-circle" width="24" height="24">
                        </div>
                      </div>
                      <div class="task-card p-2 bg-white rounded mb-2 shadow-sm">
                        <h6 class="mb-1">Design System Updates</h6>
                        <small class="text-muted d-block mb-2">Medium Priority</small>
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="badge bg-primary">Design</span>
                          <img src="https://ui-avatars.com/api/?name=Jane+Smith" alt="Jane S." class="rounded-circle" width="24" height="24">
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="board-column bg-light p-2 rounded">
                      <h6 class="column-title mb-3">In Progress</h6>
                      <div class="task-card p-2 bg-white rounded mb-2 shadow-sm">
                        <h6 class="mb-1">User Authentication</h6>
                        <small class="text-muted d-block mb-2">High Priority</small>
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="badge bg-danger">Backend</span>
                          <img src="https://ui-avatars.com/api/?name=Mike+Johnson" alt="Mike J." class="rounded-circle" width="24" height="24">
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="board-column bg-light p-2 rounded">
                      <h6 class="column-title mb-3">Review</h6>
                      <div class="task-card p-2 bg-white rounded mb-2 shadow-sm">
                        <h6 class="mb-1">Homepage Redesign</h6>
                        <small class="text-muted d-block mb-2">Medium Priority</small>
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="badge bg-primary">Design</span>
                          <img src="https://ui-avatars.com/api/?name=Sarah+Wilson" alt="Sarah W." class="rounded-circle" width="24" height="24">
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-3">
                    <div class="board-column bg-light p-2 rounded">
                      <h6 class="column-title mb-3">Done</h6>
                      <div class="task-card p-2 bg-white rounded mb-2 shadow-sm">
                        <h6 class="mb-1">Initial Setup</h6>
                        <small class="text-muted d-block mb-2">Completed</small>
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="badge bg-success">Infrastructure</span>
                          <img src="https://ui-avatars.com/api/?name=Team+Lead" alt="Team Lead" class="rounded-circle" width="24" height="24">
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      analytics: {
        title: "Detailed Analytics",
        size: "large",
        template: `
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="card-title mb-0">Detailed Analytics</h6>
                <div class="dropdown">
                  <button class="btn btn-link btn-sm p-0 text-muted" data-bs-toggle="dropdown">
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                  <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" onclick="dashboard.removeWidget(event, 'analytics')">Remove Widget</a></li>
                  </ul>
                </div>
              </div>
              <div class="analytics-container">
                <div class="row g-3">
                  <div class="col-md-8">
                    <div class="chart-container" style="height: 300px; background: #f8f9fa; border-radius: 8px;">
                      <!-- Placeholder for chart -->
                      <div class="d-flex align-items-center justify-content-center h-100">
                        <p class="text-muted mb-0">Project Progress Chart</p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="metrics-grid">
                      <div class="metric-card p-3 bg-light rounded mb-2">
                        <h3 class="mb-1">85%</h3>
                        <small class="text-muted">Task Completion Rate</small>
                      </div>
                      <div class="metric-card p-3 bg-light rounded mb-2">
                        <h3 class="mb-1">12</h3>
                        <small class="text-muted">Active Sprints</small>
                      </div>
                      <div class="metric-card p-3 bg-light rounded">
                        <h3 class="mb-1">94%</h3>
                        <small class="text-muted">Team Efficiency</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      tasks: {
        title: "Recent Tasks",
        template: `
          <div class="col-md-6 col-xl-4 mb-4 dashboard-widget" draggable="true">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="card-title mb-0">Recent Tasks</h6>
                <button class="btn btn-link text-muted p-0" onclick="dashboard.removeWidget('tasks')">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="card-body">
                <div class="tasks-list">
                  <div class="task-item d-flex align-items-center mb-2">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox">
                    </div>
                    <div class="ms-2">
                      <p class="mb-0 text-truncate">Update dashboard analytics</p>
                      <small class="text-muted">Due today</small>
                    </div>
                  </div>
                  <div class="task-item d-flex align-items-center mb-2">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox">
                    </div>
                    <div class="ms-2">
                      <p class="mb-0 text-truncate">Design new onboarding flow</p>
                      <small class="text-muted">Due tomorrow</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      calendarSmall: {
        title: "Calendar",
        template: `
          <div class="col-md-6 col-xl-4 mb-4 dashboard-widget" data-widget-id="calendarSmall" draggable="true">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="card-title mb-0">Calendar</h6>
                <div class="d-flex align-items-center gap-2">
                  <button class="btn btn-link text-muted p-0" onclick="window.dashboard.addWidget('calendarLarge'); window.dashboard.removeWidget('calendarSmall')">
                    <i class="fas fa-expand"></i>
                  </button>
                  <button class="btn btn-link text-muted p-0" onclick="window.dashboard.removeWidget('calendarSmall')">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="mb-0">October 2025</h5>
                  <div>
                    <button class="btn btn-sm btn-outline-secondary"><i class="fas fa-chevron-left"></i></button>
                    <button class="btn btn-sm btn-outline-secondary"><i class="fas fa-chevron-right"></i></button>
                  </div>
                </div>
                <div class="calendar-grid">
                  <table class="table table-sm calendar-table">
                    <thead>
                      <tr>
                        <th>Su</th><th>Mo</th><th>Tu</th><th>We</th><th>Th</th><th>Fr</th><th>Sa</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td>
                      </tr>
                      <tr>
                        <td>8</td><td>9</td><td>10</td><td>11</td><td>12</td><td>13</td><td>14</td>
                      </tr>
                      <tr>
                        <td>15</td><td class="text-primary fw-bold">16</td><td>17</td><td>18</td><td>19</td><td>20</td><td>21</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      calendarLarge: {
        title: "Calendar",
        size: "large",
        template: `
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h6 class="card-title mb-0">Calendar</h6>
                <div class="d-flex align-items-center gap-2">
                  <button class="btn btn-link text-muted p-0" onclick="window.dashboard.addWidget('calendarSmall'); window.dashboard.removeWidget('calendarLarge')">
                    <i class="fas fa-compress"></i>
                  </button>
                  <button class="btn btn-link text-muted p-0" onclick="window.dashboard.removeWidget('calendarLarge')">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
              <div class="row">
                <div class="col-md-8">
                  <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4 class="mb-0">October 2025</h4>
                    <div>
                      <button class="btn btn-outline-secondary"><i class="fas fa-chevron-left"></i></button>
                      <button class="btn btn-outline-secondary ms-2"><i class="fas fa-chevron-right"></i></button>
                    </div>
                  </div>
                  <div class="calendar-grid large">
                    <table class="table calendar-table">
                      <thead>
                        <tr>
                          <th>Sunday</th>
                          <th>Monday</th>
                          <th>Tuesday</th>
                          <th>Wednesday</th>
                          <th>Thursday</th>
                          <th>Friday</th>
                          <th>Saturday</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">1</div>
                              <div class="events">
                                <div class="event bg-primary">Project Start</div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">2</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">3</div>
                              <div class="events">
                                <div class="event bg-success">Team Meeting</div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">4</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">5</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">6</div>
                              <div class="events">
                                <div class="event bg-info">Design Review</div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">7</div>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">8</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">9</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">10</div>
                              <div class="events">
                                <div class="event bg-warning">Deadline</div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">11</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">12</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">13</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">14</div>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">15</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date fw-bold text-primary">16</div>
                              <div class="events">
                                <div class="event bg-primary">Review</div>
                                <div class="event bg-success">Meeting</div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">17</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">18</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">19</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">20</div>
                            </div>
                          </td>
                          <td>
                            <div class="calendar-cell">
                              <div class="date">21</div>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="upcoming-events">
                    <h5 class="mb-3">Upcoming Events</h5>
                    <div class="event-list">
                      <div class="event-item p-2 bg-light rounded mb-2">
                        <div class="d-flex align-items-center">
                          <div class="event-dot bg-primary me-2"></div>
                          <div>
                            <h6 class="mb-0">Project Review</h6>
                            <small class="text-muted">Today at 2:00 PM</small>
                          </div>
                        </div>
                      </div>
                      <div class="event-item p-2 bg-light rounded mb-2">
                        <div class="d-flex align-items-center">
                          <div class="event-dot bg-success me-2"></div>
                          <div>
                            <h6 class="mb-0">Team Meeting</h6>
                            <small class="text-muted">Today at 4:00 PM</small>
                          </div>
                        </div>
                      </div>
                      <div class="event-item p-2 bg-light rounded">
                        <div class="d-flex align-items-center">
                          <div class="event-dot bg-warning me-2"></div>
                          <div>
                            <h6 class="mb-0">Project Deadline</h6>
                            <small class="text-muted">Oct 20, 2025</small>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      stats: {
        title: "Statistics",
        template: `
          <div class="col-md-6 col-xl-4 mb-4 dashboard-widget" draggable="true">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="card-title mb-0">Statistics</h6>
                <button class="btn btn-link text-muted p-0" onclick="dashboard.removeWidget('stats')">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="card-body">
                <div class="row g-2">
                  <div class="col-6">
                    <div class="p-3 bg-light rounded">
                      <h3 class="mb-0">12</h3>
                      <small class="text-muted">Tasks Due</small>
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="p-3 bg-light rounded">
                      <h3 class="mb-0">5</h3>
                      <small class="text-muted">Completed</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
      team: {
        title: "Team Activity",
        template: `
          <div class="col-md-6 col-xl-4 mb-4 dashboard-widget" draggable="true">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="card-title mb-0">Team Activity</h6>
                <button class="btn btn-link text-muted p-0" onclick="dashboard.removeWidget('team')">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="card-body">
                <div class="activity-feed">
                  <div class="activity-item d-flex mb-2">
                    <div class="activity-icon me-2">
                      <img src="https://ui-avatars.com/api/?name=John+Doe" alt="John D." class="rounded-circle" width="32" height="32">
                    </div>
                    <div>
                      <p class="mb-0"><strong>John Doe</strong> completed a task</p>
                      <small class="text-muted">2 hours ago</small>
                    </div>
                  </div>
                  <div class="activity-item d-flex mb-2">
                    <div class="activity-icon me-2">
                      <img src="https://ui-avatars.com/api/?name=Jane+Smith" alt="Jane S." class="rounded-circle" width="32" height="32">
                    </div>
                    <div>
                      <p class="mb-0"><strong>Jane Smith</strong> added a new task</p>
                      <small class="text-muted">4 hours ago</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `,
      },
    };

    this.init();
  }

  init() {
    // Load saved layout or start empty
    this.widgets = JSON.parse(localStorage.getItem("dashboardWidgets")) || [];
    this.renderDashboard();
    this.initializeDragAndDrop();
    this.updateEmptyState();
  }

  renderDashboard() {
    const container = document.getElementById("dashboard-widgets");
    container.innerHTML = ""; // Clear existing widgets

    this.widgets.forEach((widgetId) => {
      const widgetConfig =
        this.widgetTypes[widgetId] || this.widgetTemplates[widgetId];
      if (widgetConfig) {
        const template =
          widgetConfig.size === "large"
            ? this.widgetTemplates.large.wrapper(widgetId, {
                title: widgetConfig.title,
                body: widgetConfig.template,
                detailsUrl: widgetConfig.detailsUrl || "#",
              })
            : widgetConfig.template;
        container.insertAdjacentHTML("beforeend", template);
      }
    });

    this.updateEmptyState();
    this.saveLayout();
  }

  addWidget(widgetId) {
    console.log("Adding widget:", widgetId);

    // Convert 'calendar' to 'calendarSmall' for better UX
    if (widgetId === "calendar") {
      widgetId = "calendarSmall";
    }

    const widgetConfig =
      this.widgetTypes[widgetId] || this.widgetTemplates[widgetId];

    if (!widgetConfig) {
      console.log("Widget not found:", widgetId);
      console.log(
        "Available widgets:",
        Object.keys(this.widgetTypes).concat(Object.keys(this.widgetTemplates))
      );
      return;
    }

    if (this.widgets.includes(widgetId)) {
      console.log("Widget already exists:", widgetId);
      return;
    }

    // Remove conflicting calendar type if it exists
    if (
      widgetId === "calendarSmall" &&
      this.widgets.includes("calendarLarge")
    ) {
      this.removeWidget("calendarLarge");
    } else if (
      widgetId === "calendarLarge" &&
      this.widgets.includes("calendarSmall")
    ) {
      this.removeWidget("calendarSmall");
    }

    this.widgets.push(widgetId);
    this.renderDashboard();
    this.saveLayout();
  }

  removeWidget(widgetId, event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    console.log("Removing widget:", widgetId);
    const index = this.widgets.indexOf(widgetId);
    if (index !== -1) {
      this.widgets.splice(index, 1);
      this.renderDashboard();
      this.saveLayout();
    }
  }

  updateEmptyState() {
    const emptyDashboard = document.getElementById("empty-dashboard");
    if (emptyDashboard) {
      emptyDashboard.classList.toggle("d-none", this.widgets.length > 0);
    }
  }

  saveLayout() {
    localStorage.setItem("dashboardWidgets", JSON.stringify(this.widgets));
  }

  initializeDragAndDrop() {
    const container = document.getElementById("dashboard-widgets");

    container.addEventListener("dragstart", (e) => {
      const widget = e.target.closest(".dashboard-widget");
      if (widget) {
        this.draggedItem = widget;
        e.dataTransfer.effectAllowed = "move";
        widget.classList.add("dragging");
      }
    });

    container.addEventListener("dragend", (e) => {
      if (this.draggedItem) {
        this.draggedItem.classList.remove("dragging");
        this.draggedItem = null;
        this.updateLayoutFromDOM();
      }
    });

    container.addEventListener("dragover", (e) => {
      e.preventDefault();
      if (!this.draggedItem) return;

      const widget = e.target.closest(".dashboard-widget");
      if (widget && widget !== this.draggedItem) {
        const rect = widget.getBoundingClientRect();
        const midpoint = rect.y + rect.height / 2;

        if (e.clientY < midpoint) {
          widget.parentNode.insertBefore(this.draggedItem, widget);
        } else {
          widget.parentNode.insertBefore(this.draggedItem, widget.nextSibling);
        }
      }
    });

    container.addEventListener("drop", (e) => {
      e.preventDefault();
      if (this.draggedItem) {
        this.updateLayoutFromDOM();
      }
    });
  }

  updateLayoutFromDOM() {
    const widgets = document.querySelectorAll(".dashboard-widget");
    this.widgets = Array.from(widgets)
      .map((widget) => widget.getAttribute("data-widget-id") || widget.id)
      .filter((id) => id);
    this.saveLayout();
  }
}

// Global function for adding widgets
function addWidget(widgetId) {
  console.log("Global addWidget called with:", widgetId);
  if (!window.dashboard) {
    console.error("Dashboard not initialized");
    return;
  }
  window.dashboard.addWidget(widgetId);
}

// Initialize dashboard when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing dashboard");
  window.dashboard = new DashboardManager();
});
