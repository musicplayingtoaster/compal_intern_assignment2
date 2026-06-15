const form = document.getElementById('todo_form')

form.addEventListener('submit', function(event) {
    console.log("hit");
    event.preventDefault();
    const formData = new FormData(this);
    
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }
    
    fetch('/submit/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => {
        console.error("Error: error")
    });
});
