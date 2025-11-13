"""Deploy Analytic Rules to Workspace"""

import src.app_logging as al
import src.nrt_rule_template as nrt
import src.scheduled_rule_template as srt
import src.template_to_rule as ttr

# import src.sentinel_workspace as sw

# pylint: disable=W1203, W1201, W0718


def prepare_template_body(template: dict, source: dict):
    """Prepare the template body for deployment"""
    al.logger.info(
        f"Preparing template body for: {template["properties"]["contentId"]}"
    )
    return {
        "properties": {
            "contentId": template["properties"]["contentId"],
            "contentKind": template["properties"]["contentKind"],
            "contentProductId": template["properties"]["contentProductId"],
            "displayName": template["properties"]["displayName"],
            "packageId": template["properties"]["packageId"],
            "packageVersion": template["properties"]["packageVersion"],
            "source": source,
            "version": template["properties"]["version"],
            "contentSchemaVersion": template["properties"][
                "contentSchemaVersion"
            ],
            "mainTemplate": template["properties"]["mainTemplate"],
        }
    }


def model_templates_for_deployment(templates: list[dict]):
    """Model rules for deployment"""
    modeled_rules = []
    for rule in templates:
        try:
            al.logger.debug(
                f"Modeling rule {rule['name']}: "
                + f"{rule['properties']['displayName']}"
            )
            if rule["kind"] == "NRT":
                modeled_rules.append(nrt.NrtRuleTemplate(**rule))
            elif rule["kind"] == "Scheduled":
                modeled_rules.append(srt.ScheduledAlertRuleTemplate(**rule))
            else:
                al.logger.warning(f"{rule['kind']} for rule {rule['name']}")
        except Exception as e:
            al.logger.error(
                f"Error creating ScheduledAlertRuleTemplate {rule['name']}: {e}"
            )
            continue
    return modeled_rules


def deploy_alert_rules(self):
    """Deploy alert rules to the workspace"""
    templates_to_deploy = []
    al.logger.info(f"Deploying alert rules to workspace: {self.workspace_name}")

    content_templates_from_ws = self.list_rule_content_templates()["value"]
    for content_template in content_templates_from_ws:
        content_rule_template = content_template["properties"]["mainTemplate"][
            "resources"
        ][0]
        content_rule_template["properties"]["version"] = content_template[
            "properties"
        ]["version"]
        templates_to_deploy.append(content_rule_template)
    modeled_templates = model_templates_for_deployment(templates_to_deploy)
    modeled_rules = ttr.translate_templates_to_rules(modeled_templates, False)
    return self.create_update_alerts(modeled_rules, enabled=False)
