document.addEventListener("DOMContentLoaded", function () {
  // Calendar initialization
  const tasks = [
    {
      title: "Update dashboard analytics",
      date: "2025-10-15",
      status: "success",
    },
    {
      title: "Design new onboarding flow",
      date: "2025-10-18",
      status: "warning",
    },
    {
      title: "Implement user feedback system",
      date: "2025-10-20",
      status: "info",
    },
  ];

  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  let currentDate = new Date();

  function renderCalendar() {
    const firstDay = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      1
    );
    const lastDay = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth() + 1,
      0
    );
    const startingDay = firstDay.getDay();
    const totalDays = lastDay.getDate();

    document.getElementById("currentMonth").textContent = `${
      months[currentDate.getMonth()]
    } ${currentDate.getFullYear()}`;

    const calendarGrid = document.getElementById("calendarGrid");
    calendarGrid.innerHTML = "";

    let currentRow = document.createElement("div");
    currentRow.className = "row g-0";

    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDay; i++) {
      currentRow.appendChild(createDayCell("", true));
    }

    // Add cells for each day of the month
    for (let day = 1; day <= totalDays; day++) {
      const date = new Date(
        currentDate.getFullYear(),
        currentDate.getMonth(),
        day
      );
      if ((day + startingDay - 1) % 7 === 0 && day !== 1) {
        calendarGrid.appendChild(currentRow);
        currentRow = document.createElement("div");
        currentRow.className = "row g-0";
      }
      currentRow.appendChild(createDayCell(day, false, date));
    }

    // Add empty cells for remaining days
    const remainingCells = 7 - currentRow.children.length;
    for (let i = 0; i < remainingCells; i++) {
      currentRow.appendChild(createDayCell("", true));
    }
    calendarGrid.appendChild(currentRow);
  }

  function createDayCell(day, inactive, date) {
    const cell = document.createElement("div");
    cell.className = `col border calendar-day${inactive ? " inactive" : ""}`;
    if (!inactive) {
      const dateStr = date.toISOString().split("T")[0];
      const today = new Date();
      const isToday = date.toDateString() === today.toDateString();

      const dayTasks = tasks.filter((task) => task.date === dateStr);

      cell.innerHTML = `
                <div class="p-2">
                    <div class="calendar-date${
                      isToday ? " today" : ""
                    }">${day}</div>
                    ${dayTasks
                      .map(
                        (task) => `
                        <div class="calendar-task badge bg-${task.status}-subtle text-${task.status} w-100 text-start p-2">
                            ${task.title}
                        </div>
                    `
                      )
                      .join("")}
                </div>
            `;

      cell.addEventListener("click", () => {
        document.getElementById("taskDueDate").value = dateStr;
        new bootstrap.Modal(document.getElementById("addTaskModal")).show();
      });
    }
    return cell;
  }

  // Event listeners for month navigation
  document.getElementById("prevMonth").addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
  });

  document.getElementById("nextMonth").addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
  });

  // Initial render
  renderCalendar();

  // View toggle functionality
  const viewToggleButtons = document.querySelectorAll(".view-toggle .btn");
  const listView = document.querySelector(".card:not(#calendarView)");
  const calendarView = document.querySelector("#calendarView");

  viewToggleButtons.forEach((button) => {
    button.addEventListener("click", function () {
      viewToggleButtons.forEach((btn) => btn.classList.remove("active"));
      this.classList.add("active");

      if (this.dataset.view === "calendar") {
        listView.classList.add("d-none");
        calendarView.classList.remove("d-none");
      } else {
        listView.classList.remove("d-none");
        calendarView.classList.add("d-none");
      }
    });
  });

  // Search functionality
  const searchInput = document.querySelector(
    'input[placeholder="Search Tasks"]'
  );
  const taskItems = document.querySelectorAll(".task-item");

  searchInput.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    taskItems.forEach((item) => {
      const taskTitle = item.querySelector("h6").textContent.toLowerCase();
      if (taskTitle.includes(searchTerm)) {
        item.style.display = "";
      } else {
        item.style.display = "none";
      }
    });
  });

  // Add task functionality
  window.addNewTask = function (event) {
    event.preventDefault();
    const form = document.getElementById("addTaskForm");
    const title = document.getElementById("taskTitle").value;
    const description = document.getElementById("taskDescription").value;
    const dueDate = document.getElementById("taskDueDate").value;
    const status = document.getElementById("taskStatus").value;
    const assignees = Array.from(
      document.getElementById("taskAssignees").selectedOptions
    ).map((option) => option.text);

    if (!title || !dueDate) {
      alert("Please fill in all required fields");
      return;
    }

    // Create new task item in list view
    const taskList = document.querySelector(".card-body.p-0");
    const newTask = document.createElement("div");
    newTask.className = "task-item p-3 border-bottom";
    newTask.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="task-${Date.now()}">
                </div>
                <div class="ms-3 flex-grow-1">
                    <h6 class="mb-1">${title}</h6>
                    <div class="d-flex align-items-center gap-3">
                        <span class="badge bg-info-subtle text-info">To Do</span>
                        <small class="text-muted">Due ${new Date(
                          dueDate
                        ).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                        })}</small>
                        <div class="avatar-group">
                            ${assignees
                              .map(
                                (assignee) => `
                                <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(
                                  assignee
                                )}" alt="${assignee}" class="avatar">
                            `
                              )
                              .join("")}
                        </div>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="btn btn-light btn-sm">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                </div>
            </div>
        `;
    taskList.insertBefore(newTask, taskList.firstChild);

    // Add task to calendar view
    tasks.push({
      title: title,
      date: dueDate,
      status: "info",
    });
    renderCalendar();

    // Close modal and reset form
    bootstrap.Modal.getInstance(document.getElementById("addTaskModal")).hide();
    form.reset();
  };
});
