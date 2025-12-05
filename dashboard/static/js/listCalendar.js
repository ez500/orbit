document.addEventListener("DOMContentLoaded", function () {
    const tasks = JSON.parse(document.getElementById("tasks-data").textContent);

    // View toggle functionality
    const viewToggleButtons = document.querySelectorAll(".view-toggle .btn");
    const listViews = document.querySelectorAll(".card:not(#calendarView)");
    const calendarView = document.querySelector("#calendarView");

    viewToggleButtons.forEach((button) => {
        button.addEventListener("click", function () {
            viewToggleButtons.forEach((btn) => btn.classList.remove("active"));
            this.classList.add("active");

            if (this.dataset.view === "calendar") {
                listViews.forEach((listView) => listView.classList.add("d-none"));
                calendarView.classList.remove("d-none");
            } else {
                listViews.forEach((listView) => listView.classList.remove("d-none"));
                calendarView.classList.add("d-none");
            }
        });
    });

    const form = document.getElementById("taskFilterForm");
    form.querySelectorAll("select").forEach(sel => {
        sel.addEventListener("change", () => form.submit());
    })

    // Calendar initialization
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
        cell.className = `col border calendar-day${inactive ? " inactive" : ""} position-relative`;
        if (!inactive) {
            const dateStr = date.toISOString().split("T")[0];
            const today = new Date();
            const isToday = date.toDateString() === today.toDateString();

            const dayTasks = tasks.filter((task) => task.deadline === dateStr);

            dayTasks.forEach((task) => {console.log(task)})

            cell.innerHTML = `
                <div class="p-2">
                    <div class="appendButtonHere d-flex align-items-center">
                        <div class="me-auto text-start calendar-date${isToday ? " today" : ""}">${day}</div>    
                    </div>
                    ${dayTasks.map(
                        (task) => {
                            const mode = task.status === "completed" ? "success"
                                : task.status === "in_progress" ? "warning" 
                                    : task.status === "review" ? "info" : "danger";
                            
                            return `
                                <div class="calendar-task badge bg-${mode}-subtle text-${mode} w-100 text-start p-2"
                                    data-task-id="${task.id}" role="button" aria-label="View Task {{ task.title }}">
                                    ${task.title}
                                </div>
                            `;
                        }
                    ).join("")}
                </div>
            `;

            cell.addEventListener("mouseenter", () => {
                if (cell.querySelector(".add-task-btn")) return;
                const elementToAddButton = cell.querySelector(".appendButtonHere");

                const addTaskButton = document.createElement("button");
                addTaskButton.type = "button";
                addTaskButton.className = "btn btn-sm btn-outline-primary add-task-btn";
                addTaskButton.setAttribute("aria-label", "Add task");
                addTaskButton.dataset.bsToggle = "modal";
                addTaskButton.dataset.bsTarget = "#addTaskEventModal";
                addTaskButton.innerHTML = `<i class="fas fa-plus fa-sm"></i>`;
                elementToAddButton.appendChild(addTaskButton);

                addTaskButton.addEventListener("click", () => {
                    document.getElementById("id_deadline").value = dateStr;
                })
            });

            cell.addEventListener("mouseleave", () => {
                const addTaskButton = cell.querySelector(".add-task-btn");
                if (addTaskButton) {
                    addTaskButton.remove();
                }
            })
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
});
