document.addEventListener("DOMContentLoaded", () => {
    function addNewTask(event) {
        // form data
        const title = document.getElementById('taskTitle').value;
        const description = document.getElementById('taskDescription').value;
        const dueDate = document.getElementById('taskDueDate').value;
        const status = document.getElementById('taskStatus').value;
        const assigneesSelect = document.getElementById('taskAssignees');
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        const selectedOptions = Array.from(assigneesSelect.selectedOptions);
        const assignees = selectedOptions.map(option => option.value);

        const data = {
            title: title,
            content: description,
            deadline: dueDate,
            users: assignees,
        };

        // Send POST request to your backend API
        fetch('/api/tasks/', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(data),
        }).then(response => {
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            alert('Task added successfully!');
            document.getElementById('addTaskForm').reset();
            var modalEl = document.getElementById('addTaskModal');
            var modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
            window.location.reload();
        }).catch(error => {
            console.error('Error:', error);
            alert('Failed to add task. Please try again.');
        });
    }

    function deleteTask(event) {
        event.preventDefault();
    }


    document.getElementById('addTaskBtn').addEventListener("click", () => {
        addNewTask(2);
    })

    const deleteButton = document.getElementById('deleteTaskBtn');
    if (deleteButton) {
        deleteButton.addEventListener('click', deleteTask);
    }
});
