"""Blueprint for workspace creation and monitoring routes."""

# pylint: disable=W1203
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
from services.sentinel import create_workspace_task

workspace_bp = Blueprint("workspace", __name__)

deployments = {}


@workspace_bp.route("/registered-app", methods=["GET", "POST"])
def collect_workspace_info():
    """Display workspace information form and handle user input for
    workspace/solution deployment."""
    logger.info("Rendering workspace information collection page.")
    if request.method == "POST":
        logger.info("Workspace information form submitted.")
        subscription_id = request.form["subscription_id"]
        resource_group = request.form["resource_group"]
        workspace_name = request.form["workspace_name"]
        region = request.form["region"]
        # client_id/client_secret may be omitted for logged-in users
        client_id = request.form.get("client_id")
        client_secret = request.form.get("client_secret")
        tenant_id = request.form["tenant_id"]
        session["workspace_form"] = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "workspace_name": workspace_name,
            "region": region,
            "client_id": client_id,
            "tenant_id": tenant_id,
        }
        session["client_secret"] = client_secret
        # Do not start workspace creation here; go to RG/LAW creation page
        return redirect(url_for("workspace.create_rg_law"))
    return render_template("form.html")


@workspace_bp.route("/form_no_creds", methods=["GET"])
def form_no_creds():
    """Render the same form but hide client id/secret fields for logged-in users."""
    return render_template("form.html", hide_creds=True)


@workspace_bp.route("/create_rg_law", methods=["GET", "POST"])
def create_rg_law():
    """Ask if resource group and log analytics workspace need to be created.
    If neither, skip to choose_solution."""
    if request.method == "POST":
        create_rg = request.form.get("create_rg") == "yes"
        create_law = request.form.get("create_law") == "yes"
        session["create_rg"] = create_rg
        session["create_law"] = create_law
        if not create_rg and not create_law:
            # Skip workspace creation, go directly to choose_solution
            return redirect(url_for("solution.choose_solution"))
        # Otherwise, start workspace creation as before
        workspace_form = session.get("workspace_form")
        client_secret = session.get("client_secret")
        # pass user id (UID) to worker; worker will read cache from MSAL_CACHE_DIR
        user = session.get("user") or {}
        user_id = user.get("sub") or user.get("oid")

        deployment_id = str(uuid.uuid4())
        deployments[deployment_id] = {"status": "In Progress", "logs": []}
        logger.info(
            f"Starting workspace creation thread for deployment_id={deployment_id}"
        )
        thread = threading.Thread(
            target=create_workspace_task,
            args=(
                deployment_id,
                workspace_form["subscription_id"],
                workspace_form["resource_group"],
                workspace_form["workspace_name"],
                workspace_form["region"],
                workspace_form["client_id"],
                client_secret,
                workspace_form["tenant_id"],
                deployments,
                user_id,
                create_rg,
                create_law,
            ),
        )
        thread.start()
        logger.info(f"Redirecting to monitor for deployment_id={deployment_id}")
        return redirect(
            url_for("workspace.monitor", deployment_id=deployment_id)
        )
    return render_template("create_rg_law.html")


@workspace_bp.route("/monitor/<deployment_id>")
def monitor(deployment_id):
    """Monitor the progress of a workspace deployment and display status/results."""
    logger.info(
        f"Monitoring workspace deployment for deployment_id={deployment_id}"
    )
    deployment = deployments.get(deployment_id)
    if not deployment:
        logger.error(f"Deployment not found: {deployment_id}")
        return "Deployment not found.", 404
    if deployment["status"] == "Completed":
        logger.info(f"Deployment {deployment_id} completed successfully.")
        return redirect(url_for("solution.choose_solution"))
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
