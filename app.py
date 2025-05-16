from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Initialize the database
def init_db():
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, complete BOOLEAN)")
    conn.commit()
    conn.close()

# Homepage (task list)
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],))
    tasks = cur.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

# Add a new task
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title")
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (user_id, title, complete) VALUES (?, ?, ?)", (session["user_id"], title, False))
    conn.commit()
    conn.close()
    return redirect("/")
# Delete a task (only if it belongs to user)
@app.route("/delete/<int:task_id>")
def delete(task_id):
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect("/")

# Mark a task as complete
@app.route("/complete/<int:task_id>")
def complete(task_id):
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("tasks.db")
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET complete = 1 WHERE id=? AND user_id=?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect("/")
# User registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password, method="sha256")

        conn = sqlite3.connect("tasks.db")
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Registered successfully! Please log in.", "success")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")
        finally:
            conn.close()
    return render_template("register.html")

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("tasks.db")
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["username"] = username
            return redirect("/")
        else:
            flash("Login failed. Check username and password.", "danger")
    return render_template("login.html")
# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Start app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)