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

        document.getElementById("currentMonth").textContent = `${months[currentDate.getMonth()]
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

            dayTasks.forEach((task) => { console.log(task) })

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

    // Calendar Import/Export functions and event listeners
    function createIcsContent(eventData) {
        // Format dates to format (YYYYMMDDTHHMMSSZ for UTC)
        const formatIcsDate = (date) => {
            return date.toISOString().replace(/[-:]|\.\d{3}/g, "");
        };

        let eventStrings = [];
        for (let i = 0; i < eventData.length; i++) {
            const { title, description, start, end, location } = eventData[i];

            eventStrings.push(`BEGIN:VEVENT
UID:${Date.now()}@veralign.com
DTSTAMP:${formatIcsDate(new Date())}
DTSTART:${formatIcsDate(start)}
DTEND:${formatIcsDate(end)}
SUMMARY:${title}
DESCRIPTION:${description}
LOCATION:${location}
END:VEVENT`);
        }

        const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Company//VerAlign//EN
${eventStrings.join("\n")}
END:VCALENDAR`;

        return icsContent;
    }

    function downloadIcsFile(eventData) {
        const icsContent = createIcsContent(eventData);
        const filename = "VerAlign Calendar.ics";

        const blob = new Blob([icsContent], { type: "text/calendar; charset=utf-8" });
        const url = URL.createObjectURL(blob);

        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = filename;
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
        URL.revokeObjectURL(url);
    }

    function parseIcsContent(icsContent) {
        const lines = icsContent.split(/\r\n|\n|\r/);
        const events = [];
        let currentEvent = null;

        for (const line of lines) {
            if (line.startsWith("BEGIN:VEVENT")) {
                currentEvent = {};
            }
            else if (line.startsWith("END:VEVENT")) {
                if (currentEvent) {
                    events.push(currentEvent);
                    currentEvent = null;
                }
            }
            else if (currentEvent) {
                const parts = line.split(":");
                if (parts.length >= 2) {
                    const key = parts[0].trim();
                    const value = parts.slice(1).join(":").trim();

                    if (key === "SUMMARY") {
                        currentEvent.summary = value;
                    }
                    else if (key === "DTSTART") {
                        currentEvent.dtstart = `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;
                    }
                    else if (key === "DTEND") {
                        currentEvent.dtend = `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;
                    }
                    else if (key === "LOCATION") {
                        currentEvent.location = value;
                    }
                    else if (key === "DESCRIPTION") {
                        currentEvent.description = value;
                    }
                }
            }
        }
        return events;
    }

    async function fetchAndParseIcs(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const icsText = await response.text();
            console.log(response);
            return icsText;
        }
        catch (error) {
            console.error("Error fetching or parsing ICS:", error);
        }
    }

    document.getElementById("calExport").addEventListener("click", () => {
        let evenList = [];
        for (let i = 0; i < tasks.length; i++) {
            console.log(tasks[i].deadline);
            evenList.push({
                title: tasks[i].title,
                description: tasks[i].content,
                start: new Date(tasks[i].deadline + "T14:00:00Z"),
                end: new Date(tasks[i].deadline + "T15:00:00Z"),
                location: ""
            });
        }

        downloadIcsFile(evenList);
    });

    document.getElementById("calImport").addEventListener("click", () => {
        document.getElementById("fileInput").click();
    });

    document.getElementById("fileInput").addEventListener("change", (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const fileContents = e.target.result;
                //console.log("File content:", fileContents);

                const calendarEvents = parseIcsContent(fileContents);
                //console.log("Parsed Calendar Events:", calendarEvents);

                const users = Array.from(document.getElementById('taskUsers').options).map(option => option.value);
                const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                for (let i = 0; i < calendarEvents.length; i++) {
                    const data = {
                        title: calendarEvents[i].summary,
                        content: calendarEvents[i].description,
                        status: "todo",
                        deadline: calendarEvents[i].dtend,
                        team: null,
                        project: null,
                        users: users,
                    };

                    // Send POST request to your backend API
                    fetch('../api/tasks/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                        body: JSON.stringify(data),
                    }).then(response => {
                        if (!response.ok) throw new Error('Network response was not ok');
                        return response.json();
                    }).then(() => {
                        window.location.reload();
                    }).catch(error => {
                        console.error('Error:', error);
                        //alert('Failed to add task. Please try again.');
                    });
                }
            };
            reader.readAsText(file);
        }
    });

    document.getElementById("urlImport").addEventListener("click", async () => {
        const icsUrl = document.getElementById("calUrl").value;
        const test = document.getElementById("calUrl").name;
        if (!icsUrl) {
            return;
        }

        let fileContents = null;
        if (icsUrl === "https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics") {
            fileContents = await fetchAndParseIcs(test);
        }
        else {
            fileContents = await fetchAndParseIcs(icsUrl);
        }
        //console.log(fileContents);

        const calendarEvents = parseIcsContent(fileContents);
        //console.log("Parsed Calendar Events:", calendarEvents);

        const users = Array.from(document.getElementById('taskUsers').options).map(option => option.value);
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        for (let i = 0; i < calendarEvents.length; i++) {
            const data = {
                title: calendarEvents[i].summary,
                content: calendarEvents[i].description,
                status: "todo",
                deadline: calendarEvents[i].dtend,
                team: null,
                project: null,
                users: users,
            };

            // Send POST request to your backend API
            fetch('../api/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify(data),
            }).then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            }).then(() => {
                window.location.reload();
            }).catch(error => {
                console.error('Error:', error);
                //alert('Failed to add task. Please try again.');
            });
        }
    });
});
