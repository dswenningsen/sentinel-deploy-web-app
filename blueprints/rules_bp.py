"""Blueprint for deploying analytic rules and monitoring progress."""

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
from services.sentinel import deploy_rules_task

# pylint: disable=W1203

deploy_rules_bp = Blueprint("deploy_rules", __name__)

# deployment tracking for this blueprint
rule_deployments = {}


@deploy_rules_bp.route("/deploy_rules", methods=["GET", "POST"])
def deploy_rules():
    """Display a page to trigger rule deployment and start background task."""
    logger.info("Rendering deploy_rules page.")

    if request.method == "POST":
        logger.info("Deploy rules form submitted.")
        workspace_form = session.get("workspace_form")
        client_secret = session.get("client_secret")
        deployment_id = str(uuid.uuid4())
        rule_deployments[deployment_id] = {"status": "In Progress", "logs": []}

        logger.info(
            f"Starting rule deployment thread for deployment_id={deployment_id}"
        )
        thread = threading.Thread(
            target=deploy_rules_task,
            args=(
                deployment_id,
                workspace_form,
                client_secret,
                rule_deployments,
            ),
        )
        thread.start()
        logger.info(
            f"Redirecting to monitor_rules for deployment_id={deployment_id}"
        )
        return redirect(
            url_for("deploy_rules.monitor_rules", deployment_id=deployment_id)
        )

    return render_template("deploy_rules.html")


@deploy_rules_bp.route(
    "/deploy_rules_prompt/<source_deployment_id>", methods=["GET", "POST"]
)
def prompt_deploy_rules(source_deployment_id):
    """Prompt the user to confirm deploying rules after a solution deploy."""
    logger.info(
        f"Rendering deploy rules prompt for source_deployment_id={source_deployment_id}"
    )

    if request.method == "POST":
        workspace_form = session.get("workspace_form")
        client_secret = session.get("client_secret")
        deployment_id = str(uuid.uuid4())
        rule_deployments[deployment_id] = {"status": "In Progress", "logs": []}

        logger.info(
            "Starting rule deployment thread (triggered from "
            f"{source_deployment_id}) for deployment_id={deployment_id}"
        )
        thread = threading.Thread(
            target=deploy_rules_task,
            args=(
                deployment_id,
                workspace_form,
                client_secret,
                rule_deployments,
            ),
        )
        thread.start()
        return redirect(
            url_for("deploy_rules.monitor_rules", deployment_id=deployment_id)
        )

    # GET: render confirmation template
    return render_template(
        "deploy_rules_prompt.html", source_deployment_id=source_deployment_id
    )


@deploy_rules_bp.route("/monitor_rules/<deployment_id>")
def monitor_rules(deployment_id):
    """Monitor the progress of a rule deployment and display status/results."""
    logger.info(f"Monitoring rule deployment for deployment_id={deployment_id}")
    deployment = rule_deployments.get(deployment_id)
    if not deployment:
        logger.error(f"Deployment not found: {deployment_id}")
        return "Deployment not found.", 404

    if deployment["status"] == "Completed":
        logger.info(f"Rule deployment {deployment_id} completed successfully.")
        return render_template(
            "solution_selected.html",
            solution=deployment["logs"],
            refresh=False,
            error=False,
        )
    elif deployment["status"] == "Error":
        logger.error(f"Rule deployment {deployment_id} failed with error.")
        return render_template(
            "logs.html",
            status="Error",
            logs=deployment["logs"],
            refresh=False,
            error=True,
        )

    logger.info(f"Rule deployment {deployment_id} in progress.")
    return render_template(
        "logs.html",
        status=deployment["status"],
        logs=deployment["logs"],
        refresh=True,
        error=False,
    )
