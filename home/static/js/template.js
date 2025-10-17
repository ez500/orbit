function toggleSidebar() {
    const sidebar = document.querySelector(".sidebar");
    sidebar.classList.toggle("collapsed");
}

function logout() {
    const logoutForm = document.getElementById("logout-form");
    HTMLFormElement.prototype.submit.call(logoutForm);
}