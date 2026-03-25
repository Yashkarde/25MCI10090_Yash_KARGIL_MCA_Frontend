let tasks = [];

function addTask() {
    let input = document.getElementById("taskInput");
    let taskText = input.value.trim();

    if (taskText === "") return;

    tasks.push({ text: taskText, completed: false });
    input.value = "";

    renderTasks(tasks);
}

function renderTasks(taskArray) {
    let list = document.getElementById("taskList");
    list.innerHTML = "";

    taskArray.forEach((task, index) => {
        let li = document.createElement("li");

        li.className = "list-group-item d-flex justify-content-between align-items-center";

        li.innerHTML = `
            <span class="${task.completed ? 'completed' : ''}" onclick="toggleTask(${index})">
                ${task.text}
            </span>
            <button class="btn btn-danger btn-sm" onclick="deleteTask(${index})">X</button>
        `;

        list.appendChild(li);
    });

    updateCounter(taskArray.length);
}

function toggleTask(index) {
    tasks[index].completed = !tasks[index].completed;
    renderTasks(tasks);
}

function deleteTask(index) {
    tasks.splice(index, 1);
    renderTasks(tasks);
}

function updateCounter(count) {
    document.getElementById("taskCounter").innerText = "Total Names :- " + count;
}

function debounce(func, delay) {
    let timer;

    return function (...args) {
        clearTimeout(timer);

        timer = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

function searchTask() {
    let value = document.getElementById("searchInput").value.toLowerCase();

    let filtered = tasks.filter(task =>
        task.text.toLowerCase().includes(value)
    );

    renderTasks(filtered);
}

document.getElementById("searchInput")
    .addEventListener("keyup", debounce(searchTask, 500));