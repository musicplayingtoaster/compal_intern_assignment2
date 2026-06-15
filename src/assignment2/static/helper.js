const form = document.getElementById('todo_form')
const todo_list = document.querySelector('.todo_list')

form.addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    fetch('/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => createTodo(data))
    .catch(error => {
        console.error("Error: error")
    });

    form.reset()
});

window.addEventListener("load", () => {
    console.log("page loaded! attempting to get database stuff...")
    fetch('/load', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        data.forEach(element => {
            createTodo(element)
        });
    })
})

todo_list.addEventListener('change', function(event){
    if (event.target && event.target.type === 'checkbox') {
        const checkbox = event.target;

        if (checkbox.checked) {
            fetch('/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"id":checkbox.parentElement.id, "todo":"", "resolved":1}),
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error("Error:", error));
        } else {
            fetch('/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({"id":checkbox.parentElement.id, "todo":"", "resolved":0}),
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error("Error:", error));
        }
    }
});


function createTodo(data) {
    const todoDiv = document.createElement('div');
    console.log(data);

    // note: 0=primarykey,1=todostring,2=resolved
    todoDiv.className = "todo_item";
    todoDiv.id = data[0].toString();
    todoDiv.innerHTML = `
    <input id="todo" name="resolve" type="checkbox">
    <label for="todo">${data[1]}</label>
    <button id="delete" onclick="deleteSelf(${data[0]})" type="button">Delete</button>
    `;
    todo_list.appendChild(todoDiv);
    if (data[2] == 1){
        todoDiv.querySelector('input').checked = true;
    }
}

function deleteSelf(id){
    console.log("self removal.", id)
    fetch('/delete', {
        method: 'DELETE',
        body: id,
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        if (data == "deleted") {
            document.getElementById(id.toString()).remove();
        }
    })
}