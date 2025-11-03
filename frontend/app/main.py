import os
import sys

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

    # Register routes - handle both relative and absolute imports
    try:
        from .routes import register_routes
    except ImportError:
        # When run directly, add parent dir to path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.routes import register_routes

    register_routes(app)

    return app


# For backwards compatibility and direct execution
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
