document.addEventListener('DOMContentLoaded', () => {
    // View task functionality
    document.addEventListener("click", async(e) => {
        const el = e.target.closest(".calendar-task, .task-item");
        if (!el) return;

        const taskId = el.getAttribute("data-task-id");
        if (!taskId) return;

        const url = `/dashboard/tasks/${taskId}/view/`;

        try {
            const response = await fetch(url, {headers: {'X-Requested-With': 'XMLHttpRequest'}});
            if (!response.ok) throw new Error('Load failed.');
            document.getElementById("viewTaskModalContent").innerHTML = await response.text();

            // Load task data from the hidden element
            const taskDataElement = document.getElementById('taskData');
            if (taskDataElement) {
                const taskInfo = taskDataElement.getAttribute('data-task-info');
                if (taskInfo) {
                    try {
                        window.currentTaskData = JSON.parse(taskInfo);
                        console.log('[ViewTaskModal] Loaded task data:', window.currentTaskData);
                    } catch (error) {
                        console.error('[ViewTaskModal] Error parsing task data:', error);
                    }
                }
            }

            new bootstrap.Modal(document.getElementById("viewTaskModal")).show();
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Keyboard accessibility for task viewing
    document.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
            const el = e.target.closest(".calendar-task, .task-item");
            if (el) {
                e.preventDefault();
                el.click();
            }
        }
    })
});