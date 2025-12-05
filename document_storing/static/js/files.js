let url = null;

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const upload_files = (files) => {
    let formdata = new FormData();

    for (let i = 0; i < files.length; i++) {
        formdata.append("files", files[i].file)
    }

    console.log(formdata);

    fetch("/files/handle/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: formdata
    }).then(res => res.json())
    .then(result => {
        console.log(result);

        url = `http://127.0.0.1:8000/files/download/${result.data.folder}`

        console.log(url);
        //document.getElementById("btn").style.display = ""df -h
    })
}