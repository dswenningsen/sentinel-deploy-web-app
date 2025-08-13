"""Main application entry point for Sentinel Automation Web Interface.

Creates the Flask app, loads configuration, and registers blueprints.
"""

import os
import uuid
from flask import Flask
from blueprints.workspace import workspace_bp
from blueprints.solution import solution_bp

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", str(uuid.uuid4()))

# Register blueprints
app.register_blueprint(workspace_bp)
app.register_blueprint(solution_bp)


def main():
    """Run the Flask application."""
    app.run(debug=True)


if __name__ == "__main__":
    main()
