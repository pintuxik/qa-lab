import os

import requests
from flask import flash, redirect, render_template, request, session, url_for

# Backend API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")


def get_auth_headers():
    """Get authorization headers for API requests"""
    token = session.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def make_api_request(method, endpoint, data=None, params=None, use_form_data=False):
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = get_auth_headers()

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            if use_form_data:
                response = requests.post(url, headers=headers, data=data)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

        return response
    except requests.exceptions.ConnectionError:
        flash("Backend service is not available", "error")
        return None


def register_routes(app):
    """Register all routes with the Flask app"""

    @app.route("/")
    def index():
        if "access_token" not in session:
            return redirect(url_for("login"))
        return redirect(url_for("dashboard"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            # OAuth2 requires form data, not JSON
            response = make_api_request(
                "POST", "/api/auth/login", {"username": username, "password": password}, use_form_data=True
            )

            if response and response.status_code == 200:
                data = response.json()
                session["access_token"] = data["access_token"]
                session["username"] = username
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username or password", "error")

        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            response = make_api_request(
                "POST", "/api/auth/register", {"username": username, "email": email, "password": password}
            )

            if response and response.status_code == 200:
                flash("Registration successful! Please login.", "success")
                return redirect(url_for("login"))
            else:
                error_msg = "Registration failed"
                if response:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                flash(error_msg, "error")

        return render_template("register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out", "info")
        return redirect(url_for("login"))

    @app.route("/dashboard")
    def dashboard():
        if "access_token" not in session:
            return redirect(url_for("login"))

        # Get user's tasks
        response = make_api_request("GET", "/api/tasks")
        tasks = []
        if response and response.status_code == 200:
            tasks = response.json()

        return render_template("dashboard.html", tasks=tasks, username=session.get("username"))

    @app.route("/tasks", methods=["POST"])
    def create_task():
        if "access_token" not in session:
            return redirect(url_for("login"))

        title = request.form["title"]
        description = request.form.get("description", "")
        priority = request.form.get("priority", "medium")
        category = request.form.get("category", "")

        response = make_api_request(
            "POST",
            "/api/tasks",
            {"title": title, "description": description, "priority": priority, "category": category},
        )

        if response and response.status_code == 200:
            flash("Task created successfully!", "success")
        else:
            flash("Failed to create task", "error")

        return redirect(url_for("dashboard"))

    @app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
    def toggle_task(task_id):
        if "access_token" not in session:
            return redirect(url_for("login"))

        # Get current task
        response = make_api_request("GET", f"/api/tasks/{task_id}")
        if response and response.status_code == 200:
            task = response.json()
            new_status = not task["is_completed"]

            # Update task
            update_response = make_api_request("PUT", f"/api/tasks/{task_id}", {"is_completed": new_status})

            if update_response and update_response.status_code == 200:
                flash("Task updated successfully!", "success")
            else:
                flash("Failed to update task", "error")

        return redirect(url_for("dashboard"))

    @app.route("/tasks/<int:task_id>/delete", methods=["POST"])
    def delete_task(task_id):
        if "access_token" not in session:
            return redirect(url_for("login"))

        response = make_api_request("DELETE", f"/api/tasks/{task_id}")
        if response and response.status_code == 200:
            flash("Task deleted successfully!", "success")
        else:
            flash("Failed to delete task", "error")

        return redirect(url_for("dashboard"))

    @app.route("/health")
    def health_check():
        """Health check endpoint for Kubernetes liveness probe."""
        return {"status": "healthy", "service": "frontend"}, 200

    @app.route("/ready")
    def readiness_check():
        """
        Readiness check endpoint for Kubernetes readiness probe.
        Checks backend connectivity.
        """
        try:
            # Test backend connection
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return {"status": "ready", "backend": "connected", "service": "frontend"}, 200
            else:
                return (
                    {"status": "not ready", "backend": "unhealthy", "service": "frontend"},
                    503,
                )
        except requests.exceptions.RequestException as e:
            return (
                {"status": "not ready", "backend": "disconnected", "error": str(e), "service": "frontend"},
                503,
            )
