"""
Load testing script for QA Lab Task Management System.

This script tests the performance of the synchronous API under various load conditions.
It simulates realistic user behavior including authentication and CRUD operations.

Usage:
    locust -f tests/load_test.py --host=http://localhost:8000

For headless mode:
    locust -f tests/load_test.py --host=http://localhost:8000 --users 50 --spawn-rate 10 --run-time 1m --headless
"""

import random
import uuid

from locust import HttpUser, between, events, task


class TaskManagementUser(HttpUser):
    """Simulates a user interacting with the Task Management API."""

    # Wait 1-3 seconds between tasks to simulate real user behavior
    wait_time = between(1, 3)

    def on_start(self):
        """
        Called when a simulated user starts.
        Creates a unique user and logs in to get authentication token.
        """
        # Create unique credentials for this user
        self.username = f"loadtest_{uuid.uuid4().hex[:8]}"
        self.password = "TestPassword123!"
        self.task_ids = []

        # Register user
        register_response = self.client.post(
            "/api/users/",
            json={"username": self.username, "email": f"{self.username}@example.com", "password": self.password},
        )

        if register_response.status_code != 201:
            print(f"Registration failed: {register_response.status_code} - {register_response.text}")
            return

        # Login to get token
        login_response = self.client.post(
            "/api/auth/login", data={"username": self.username, "password": self.password}
        )

        if login_response.status_code == 200:
            token_data = login_response.json()
            self.token = token_data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            self.token = None
            self.headers = {}

    def on_stop(self):
        """
        Called when a simulated user stops.
        Cleans up by deleting all created tasks.
        """
        if hasattr(self, "headers") and self.headers:
            for task_id in self.task_ids:
                self.client.delete(f"/api/tasks/{task_id}", headers=self.headers)

    @task(5)
    def create_task(self):
        """Create a new task (weighted 5x - common operation)."""
        if not hasattr(self, "headers") or not self.headers:
            return

        task_data = {
            "title": f"Task {uuid.uuid4().hex[:8]}",
            "description": f"Description for load test task {random.randint(1, 1000)}",
            "status": random.choice(["pending", "in_progress", "completed"]),
        }

        with self.client.post("/api/tasks", json=task_data, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                task_id = response.json().get("id")
                if task_id:
                    self.task_ids.append(task_id)
                response.success()
            else:
                response.failure(f"Failed to create task: {response.status_code}")

    @task(10)
    def list_tasks(self):
        """List all tasks (weighted 10x - most common operation)."""
        if not hasattr(self, "headers") or not self.headers:
            return

        with self.client.get("/api/tasks", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to list tasks: {response.status_code}")

    @task(3)
    def update_task(self):
        """Update an existing task (weighted 3x - common operation)."""
        if not hasattr(self, "headers") or not self.headers or not self.task_ids:
            return

        task_id = random.choice(self.task_ids)
        update_data = {
            "title": f"Updated Task {uuid.uuid4().hex[:8]}",
            "description": "Updated description",
            "status": random.choice(["pending", "in_progress", "completed"]),
        }

        with self.client.put(
            f"/api/tasks/{task_id}", json=update_data, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to update task: {response.status_code}")

    @task(2)
    def get_single_task(self):
        """Get details of a single task (weighted 2x - moderate operation)."""
        if not hasattr(self, "headers") or not self.headers or not self.task_ids:
            return

        task_id = random.choice(self.task_ids)

        with self.client.get(f"/api/tasks/{task_id}", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get task: {response.status_code}")

    @task(1)
    def delete_task(self):
        """Delete a task (weighted 1x - least common operation)."""
        if not hasattr(self, "headers") or not self.headers or not self.task_ids:
            return

        task_id = self.task_ids.pop(random.randrange(len(self.task_ids)))

        with self.client.delete(f"/api/tasks/{task_id}", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to delete task: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print information when the test starts."""
    print("\n" + "=" * 80)
    print("🚀 LOAD TEST STARTING")
    print("=" * 80)
    print(f"Target: {environment.host}")
    print("=" * 80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary when the test stops."""
    print("\n" + "=" * 80)
    print("✅ LOAD TEST COMPLETED")
    print("=" * 80)
    print("\nKey metrics to evaluate:")
    print("  • Response times (avg, p95, p99)")
    print("  • Failure rate")
    print("  • Requests per second (RPS)")
    print("=" * 80 + "\n")
