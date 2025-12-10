document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    function addNewTask() {
        // form data
        const title = document.getElementById('taskTitle').value;
        const content = document.getElementById('taskContent').value;
        const status = document.getElementById('taskStatus').value;
        const rawDeadline = document.getElementById('taskDeadline').value;
        const deadline = rawDeadline ? rawDeadline : null;

        const team = document.getElementById('taskTeam').value;
        const project = document.getElementById('taskProject').value;
        const users =
            Array.from(document.getElementById('taskUsers').selectedOptions)
                .map(option => option.value);

        const data = {
            title: title,
            content: content,
            status: status,
            deadline: deadline,
            team: team,
            project: project,
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
