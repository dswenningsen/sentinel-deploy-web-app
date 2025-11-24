"""Main application entry point for Sentinel Automation Web Interface.

Creates the Flask app, loads configuration, and registers blueprints.
"""

import os
import uuid
import atexit
import signal
from flask import Flask
from blueprints.workspace import workspace_bp
from blueprints.solution import solution_bp
from blueprints.rules_bp import deploy_rules_bp
from blueprints.auth_bp import auth_bp
from src.cache_cleanup import start_cache_cleanup_scheduler

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", str(uuid.uuid4()))

# Register blueprints
app.register_blueprint(workspace_bp)
app.register_blueprint(solution_bp)
app.register_blueprint(deploy_rules_bp)
app.register_blueprint(auth_bp)

# Start background cache cleanup scheduler (enabled via env)
if os.environ.get("ENABLE_CACHE_CLEANUP", "true").lower() in (
    "1",
    "true",
    "yes",
):
    stop_event = start_cache_cleanup_scheduler(
        interval_minutes=int(
            os.environ.get("CACHE_PURGE_INTERVAL_MINUTES", "15")
        ),
        max_age_minutes=int(os.environ.get("CACHE_MAX_AGE_MINUTES", "60")),
        secure_overwrite=os.environ.get(
            "CACHE_SECURE_OVERWRITE", "false"
        ).lower()
        in ("1", "true", "yes"),
    )
    app.config["CACHE_CLEANUP_STOP"] = stop_event

    # ensure the background thread is signaled on normal exit
    atexit.register(lambda: stop_event.set() if stop_event else None)

    # best-effort signal handlers for graceful shutdown
    def _on_exit(signum, frame):
        if app.config.get("CACHE_CLEANUP_STOP"):
            app.config["CACHE_CLEANUP_STOP"].set()

    try:
        signal.signal(signal.SIGINT, _on_exit)
        signal.signal(signal.SIGTERM, _on_exit)
    except Exception:
        app.logger.debug("Signal handlers for cache cleanup not installed.")


def main():
    """Run the Flask application."""
    app.run(debug=True)


if __name__ == "__main__":
    main()
