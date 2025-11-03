const removeElementById = (id) => {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
};

function fadeOut(el) {
    el.style.opacity = 1;

    (function fade() {
        if ((el.style.opacity -= 0.1) < 0) {
            el.style.display = "none";
        }
        else {
            requestAnimationFrame(fade);
        }
    })();
}

function fadeIn(el, display) {
    el.style.opacity = 0;
    el.style.display = display || "block";

    (function fade() {
        var val = parseFloat(el.style.opacity);
        if (!((val += 0.1) > 1)) {
            el.style.opacity = val;
            requestAnimationFrame(fade);
        }
    })();
}

function isRequired(value) {
    return value.trim() !== "";
}

function isValidEmail(value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
}

function validateForm() {
    let isValid = true;
    removeElementById("name-error");
    removeElementById("email-error");
    removeElementById("subject-error");
    removeElementById("message-error");

    if (!isRequired(document.getElementById("name").value)) {
        const nameError = document.createElement("label");
        nameError.setAttribute("id", "name-error");
        nameError.setAttribute("class", "error");
        nameError.setAttribute("for", "name");
        nameError.innerText = "Please enter your name";
        document.getElementById("name").after(nameError);
        isValid = false;
    }

    if (!isRequired(document.getElementById("email").value) || !isValidEmail(document.getElementById("email").value)) {
        const emailError = document.createElement("label");
        emailError.setAttribute("id", "email-error");
        emailError.setAttribute("class", "error");
        emailError.setAttribute("for", "email");
        emailError.innerText = "Please enter a valid email address";
        document.getElementById("email").after(emailError);
        isValid = false;
    }

    if (!isRequired(document.getElementById("subject").value)) {
        const subjectError = document.createElement("label");
        subjectError.setAttribute("id", "subject-error");
        subjectError.setAttribute("class", "error");
        subjectError.setAttribute("for", "subject");
        subjectError.innerText = "Please enter a subject";
        document.getElementById("subject").after(subjectError);
        isValid = false;
    }

    if (!isRequired(document.getElementById("message").value) || document.getElementById("message").value.length < 5) {
        const msgError = document.createElement("label");
        msgError.setAttribute("id", "message-error");
        msgError.setAttribute("class", "error");
        msgError.setAttribute("for", "message");
        msgError.innerText = "Please enter a message";
        document.getElementById("message").after(msgError);
        isValid = false;
    }

    return isValid;
}

const contactForm = document.getElementById("contactForm");
contactForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    if (contactForm.childElementCount > 0) {
        if (validateForm()) {
            const submit = document.getElementsByClassName("submitting")[0];

            submit.setAttribute("style", "display: block");
            submit.innerText = "Submitting...";

            const formData = new FormData(contactForm);
            const csrfToken = formData.get("csrfmiddlewaretoken");

            try {
                const response = await fetch("/contact/", {
                    method: "POST",
                    headers: { "X-CSRFToken": csrfToken },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log("Success:", data);
                document.getElementById("form-message-warning").style.display = "none";
                setTimeout(function () {
                    fadeOut(contactForm);
                }, 1000);
                setTimeout(function () {
                    fadeIn(document.getElementById("form-message-success"));
                }, 1400);
            }
            catch (error) {
                console.error("Error:", error);
                document.getElementById("form-message-warning").innerHTML = "Something went wrong. Please try again.";
                fadeIn(document.getElementById("form-message-warning"), "block");
                submit.setAttribute("display", "none");
            }
        }
    }
});