"""Service logic for Sentinel workspace and solution deployment tasks."""

from src.app_logging import logger
from src.sentinel_workspace import SentinelWorkspace

# pylint: disable=W1203, W0718


def create_workspace_task(
    deployment_id,
    subscription_id,
    resource_group,
    workspace_name,
    region,
    client_id,
    client_secret,
    tenant_id,
    deployments,
    create_rg=False,
    create_law=False,
):
    """Background task to create a Sentinel workspace in a separate thread.
    Args:
        create_rg (bool): Whether to create the resource group.
        create_law (bool): Whether to create the log analytics workspace.
    """
    logs = []
    try:
        logger.info(
            f"[create_workspace_task] Starting workspace creation for "
            f"{workspace_name} in {resource_group} (create_rg={create_rg}, "
            f"create_law={create_law})"
        )
        logs.append("Initializing Sentinel Workspace creation...")
        workspace = SentinelWorkspace(
            sub_id=subscription_id,
            rg_name=resource_group,
            ws_name=workspace_name,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        if create_rg and create_law:
            # Pass create_rg and create_law to your workspace creation logic as needed
            a = workspace.create_sentinel_workspace(region=region)
            if a:
                logs.append("Sentinel Workspace created successfully!")
                deployments[deployment_id]["logs"] = logs
                deployments[deployment_id]["status"] = "Completed"
                logger.info(
                    f"[create_workspace_task] Workspace {workspace_name} created successfully."
                )
            else:
                logs.append("Error: Workspace creation failed.")
                deployments[deployment_id]["logs"] = logs
                deployments[deployment_id]["status"] = "Error"
                logger.error(
                    f"[create_workspace_task] Workspace creation failed for {workspace_name}."
                )
        elif create_law and not create_rg:
            # If only log analytics workspace is to be created
            a = workspace.create_log_analytics_workspace(location=region)
            if a:
                logs.append("Log Analytics Workspace created successfully!")
                deployments[deployment_id]["logs"] = logs
                deployments[deployment_id]["status"] = "Completed"
                logger.info(
                    f"[create_workspace_task] Log Analytics Workspace "
                    f"{workspace_name} created successfully."
                )
            else:
                logs.append("Error: Log Analytics Workspace creation failed.")
                deployments[deployment_id]["logs"] = logs
                deployments[deployment_id]["status"] = "Error"
                logger.error(
                    "[create_workspace_task] Log Analytics Workspace creation"
                    f"failed for {workspace_name}."
                )
            b = workspace.onboard_sentinel()
            if b:
                logs.append("Sentinel onboarded successfully!")
                deployments[deployment_id]["logs"] = logs
                deployments[deployment_id]["status"] = "Completed"
                logger.info(
                    f"[create_workspace_task] Sentinel onboarded successfully for {workspace_name}."
                )
            else:
                logs.append("Error: Sentinel onboarding failed.")
                deployments[deployment_id]["logs"] = logs
                deployments[deployment_id]["status"] = "Error"
                logger.error(
                    f"[create_workspace_task] Sentinel onboarding failed for {workspace_name}."
                )
    except Exception as e:
        logs.append(f"Error: {str(e)}")
        deployments[deployment_id]["logs"] = logs
        deployments[deployment_id]["status"] = "Error"
        logger.error(f"[create_workspace_task] Exception: {e}")


def process_solutions_task(
    deployment_id,
    workspace_form,
    client_secret,
    selected_solutions,
    deployments,
):
    """Background task to deploy selected solutions to the Sentinel workspace."""
    logs = []
    try:
        logger.info(
            f"[process_solutions_task] Deploying solutions: {selected_solutions}"
        )
        logs.append("Deploying Solutions...")
        sent_client = SentinelWorkspace(
            sub_id=workspace_form["subscription_id"],
            rg_name=workspace_form["resource_group"],
            ws_name=workspace_form["workspace_name"],
            tenant_id=workspace_form["tenant_id"],
            client_id=workspace_form["client_id"],
            client_secret=client_secret,
        )
        sent_client.deploy_solutions(
            workspace_form["region"], selected_solutions
        )
        logs.append("All selected solutions deployed successfully.")
        deployments[deployment_id]["logs"] = logs
        deployments[deployment_id]["status"] = "Completed"
        logger.info(
            f"{process_solutions_task} All selected solutions deployed."
        )
    except Exception as e:
        logs.append(f"Error: {str(e)}")
        deployments[deployment_id]["logs"] = logs
        deployments[deployment_id]["status"] = "Error"
        logger.error(f"[process_solutions_task] Exception: {e}")


def deploy_rules_task(
    deployment_id,
    workspace_form,
    client_secret,
    deployments,
):
    """Background task to deploy analytic alert rules to the Sentinel workspace."""
    logs = []
    try:
        logger.info(
            "[deploy_rules_task] Deploying rules to workspace: "
            f"{workspace_form.get('workspace_name')}"
        )
        logs.append("Deploying rules to workspace...")
        sent_client = SentinelWorkspace(
            sub_id=workspace_form["subscription_id"],
            rg_name=workspace_form["resource_group"],
            ws_name=workspace_form["workspace_name"],
            tenant_id=workspace_form.get("tenant_id"),
            client_id=workspace_form.get("client_id"),
            client_secret=client_secret,
        )
        responses = sent_client.deploy_rules()
        if False not in responses:
            logs.append("All rules deployed successfully.")
            deployments[deployment_id]["logs"] = logs
            deployments[deployment_id]["status"] = "Completed"
            logger.info(
                f"[deploy_rules_task] All rules deployed for {workspace_form.get('workspace_name')}"
            )
        else:
            logs.append("Error: Some rules failed to deploy.")
            logs.append("Check logs for details.")
            deployments[deployment_id]["logs"] = logs
            deployments[deployment_id]["status"] = "Error"
            logger.error(
                f"[deploy_rules_task] Some rules failed to deploy for {workspace_form.get('workspace_name')}"
            )
    except Exception as e:
        logs.append(f"Error: {str(e)}")
        deployments[deployment_id]["logs"] = logs
        deployments[deployment_id]["status"] = "Error"
        logger.error(f"[deploy_rules_task] Exception: {e}")
