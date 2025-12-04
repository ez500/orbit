document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    document.getElementById('id_team').addEventListener("change", event => {
        const selectedTeam = event.target.value;
        const projectSelector = document.getElementById('id_project');
        const userSelector = document.getElementById('id_users');
        projectSelector.disabled = selectedTeam !== '';

        userSelector.options.length = 0;

        fetch('../api/project-team-members/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({team: selectedTeam}),
        }).then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        }).then(data => {
            console.log(data);
            Object.values(data).forEach(member => {
                console.log(member);
                const option = document.createElement('option');
                option.value = member.id;
                option.textContent = member.username;
                userSelector.appendChild(option);
            })
        }).catch(error => {
            console.error('Error:', error);
            alert('Something weird happened.');
        });
    });

    document.getElementById('id_project').addEventListener("change", event => {
        const selectedProject = event.target.value;
        const teamSelector = document.getElementById('id_team');
        teamSelector.disabled = selectedProject !== '';

        const userSelector = document.getElementById('id_users');
        userSelector.options.length = 0;

        fetch('../api/project-team-members/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({project: selectedProject}),
        }).then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        }).then(data => {
            Object.values(data).forEach(member => {
                console.log(member);
                const option = document.createElement('option');
                option.value = member.id;
                option.textContent = member.username;
                userSelector.appendChild(option);
            })
        }).catch(error => {
            console.error('Error:', error);
            alert('Something weird happened.');
        });
    });
});