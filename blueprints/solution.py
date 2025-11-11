"""Blueprint for solution selection and deployment monitoring routes."""

import uuid
import threading
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)
from src.app_logging import logger
from services.sentinel import process_solutions_task

# pylint: disable=W1203

solution_bp = Blueprint("solution", __name__)

deployments = {}


@solution_bp.route("/choose_solution", methods=["GET", "POST"])
def choose_solution():
    """Display solution selection form and handle solution deployment requests."""
    logger.info("Rendering choose_solution page.")
    solutions = [
        ("Azure Activity", "Azure Activity"),
        ("Microsoft Entra ID", "Microsoft Entra ID"),
        ("Microsoft 365", "Microsoft 365"),
        ("Security Threat Essentials", "Security Threat Essentials"),
        (
            "Cloud Identity Threat Protection Essentials",
            "Cloud Identity Threat Protection Essentials",
        ),
        ("Microsoft Defender for Cloud", "Microsoft Defender for Cloud"),
        ("Microsoft Defender XDR", "Microsoft Defender XDR"),
        ("Microsoft Entra ID Protection", "Microsoft Entra ID Protection"),
    ]

    if request.method == "POST":
        logger.info("Solution selection form submitted.")
        selected_solutions = request.form.getlist("solution")
        logger.info(f"Selected solutions: {selected_solutions}")
        workspace_form = session.get("workspace_form")
        client_secret = session.get("client_secret")
        deployment_id = str(uuid.uuid4())
        deployments[deployment_id] = {"status": "In Progress", "logs": []}
        logger.info(
            f"Starting solution deployment thread for deployment_id={deployment_id}"
        )
        thread = threading.Thread(
            target=process_solutions_task,
            args=(
                deployment_id,
                workspace_form,
                client_secret,
                selected_solutions,
                deployments,
            ),
        )
        thread.start()
        logger.info(
            f"Redirecting to monitor_solution for deployment_id={deployment_id}"
        )
        return redirect(
            url_for("solution.monitor_solution", deployment_id=deployment_id)
        )
    return render_template("choose_solution.html", solutions=solutions)


@solution_bp.route("/monitor_solution/<deployment_id>")
def monitor_solution(deployment_id):
    """Monitor the progress of a solution deployment and display status/results."""
    logger.info(
        f"Monitoring solution deployment for deployment_id={deployment_id}"
    )
    deployment = deployments.get(deployment_id)
    if not deployment:
        logger.error(f"Deployment not found: {deployment_id}")
        return "Deployment not found.", 404
    if deployment["status"] == "Completed":
        logger.info(f"Deployment {deployment_id} completed successfully.")
        return render_template(
            "solution_selected.html",
            solution=deployment["logs"],
            refresh=False,
            error=False,
        )
    elif deployment["status"] == "Error":
        logger.error(f"Deployment {deployment_id} failed with error.")
        return render_template(
            "logs.html",
            status="Error",
            logs=deployment["logs"],
            refresh=False,
            error=True,
        )
    logger.info(f"Deployment {deployment_id} in progress.")
    return render_template(
        "logs.html",
        status=deployment["status"],
        logs=deployment["logs"],
        refresh=True,
        error=False,
    )
