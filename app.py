from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Connect to the existing database
def get_connection():
    connection = sqlite3.connect("tasks.db")
    connection.row_factory = sqlite3.Row
    return connection


# Create the table if it does not exist
with get_connection() as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            due_date TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)


# Display the home page and all tasks
@app.route("/")
def home():
    with get_connection() as connection:
        tasks = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    total_tasks = len(tasks)
    completed_tasks = sum(task["completed"] for task in tasks)
    pending_tasks = total_tasks - completed_tasks

    return render_template(
        "index.html",
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )


# Add a new task
@app.route("/add", methods=["POST"])
def add_task():
    name = request.form.get("task_name", "").strip()
    subject = request.form.get("subject", "").strip()
    due_date = request.form.get("due_date", "").strip()

    if name and subject and due_date:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO tasks (name, subject, due_date) VALUES (?, ?, ?)",
                (name, subject, due_date)
            )

    return redirect(url_for("home"))


# Mark a task as completed
@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    with get_connection() as connection:
        connection.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )

    return redirect(url_for("home"))


# Delete a task
@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)