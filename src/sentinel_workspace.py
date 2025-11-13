"""
Main Sentinel Workspace class for creating and managing Sentinel workspaces
and alerts.
This class is used to create a new Sentinel workspace, onboard Microsoft Sentinel,
and create alerts in the workspace.
"""

import uuid
import requests
from azure.identity import DefaultAzureCredential, ClientSecretCredential
import azure.mgmt.securityinsight as si
import src.app_logging as al
import src.scheduled_rule as sr
import src.response_checker as rc
import src.deploy_solutions
import src.deploy_rules

# pylint: disable=W1203


class SentinelWorkspace:
    """
    Main Sentinel Workspace class for creating and managing Sentinel workspaces
    """

    def __init__(
        self,
        sub_id: str,
        rg_name: str,
        ws_name: str,
        tenant_id=None,
        client_id=None,
        client_secret=None,
    ):
        if tenant_id is None or client_id is None or client_secret is None:
            self.credential = DefaultAzureCredential()
        else:
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        self.rg_api_version = "?api-version=2021-04-01"
        self.ws_api_version = "?api-version=2025-02-01"
        self.sent_api_version = "?api-version=2025-03-01"
        self.subscription_id = sub_id
        self.resource_group_name = rg_name
        self.workspace_name = ws_name
        self.client = si.SecurityInsights(
            credential=self.credential, subscription_id=self.subscription_id
        )
        self.api_version = "?api-version=2025-07-01-preview"
        self.api_url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/"
            f"providers/Microsoft.OperationalInsights/workspaces/{self.workspace_name}"
            "/providers/Microsoft.SecurityInsights/"
        )
        self.headers = {
            "Authorization": "Bearer "
            + f"{self.get_access_token('https://management.azure.com/.default')}",
            "Content-Type": "application/json",
        }

    deploy_solutions = src.deploy_solutions.full_solution_deploy
    deploy_rules = src.deploy_rules.deploy_alert_rules

    def list_rule_content_templates(self):
        """Lists rule content templates in the workspace"""
        al.logger.info("Listing content templates")
        resource = (
            self.api_url + f"contentTemplates/{self.api_version}"
            "&%24filter=(properties%2FcontentKind%20eq%20'AnalyticsRule')"
            "&$expand=properties/mainTemplate"
        )
        al.logger.debug(f"GET {resource}")
        response = requests.get(
            url=resource,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(
            f"Error listing rule content templates in {self.workspace_name}",
            response,
        )

    def get_access_token(self, scope: str):
        """
        Retrieves access token for a specified scope using stored credentials.
        """
        token = self.credential.get_token(scope)
        return token.token

    def create_resoure_group(self, location: str, tags: dict = None):
        """Create a new resource group"""
        resource = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}{self.rg_api_version}"
        )
        body = {
            "location": location,
            "tags": tags,
        }
        response = requests.put(
            url=resource,
            json=body,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(
            f"Error creating {self.resource_group_name}", response
        )

    def create_log_analytics_workspace(
        self,
        location: str,
        tags: dict = None,
        sku_name: str = "PerGB2018",
        retention: int = 30,
    ):
        """Create a new log analytics workspace"""
        resource = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/providers/"
            f"Microsoft.OperationalInsights/workspaces/{self.workspace_name}"
            f"{self.ws_api_version}"
        )
        body = {
            "properties": {
                "sku": {"name": sku_name},
                "retentionInDays": retention,
            },
            "location": location,
            "tags": tags,
        }
        response = requests.put(
            url=resource,
            json=body,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(
            f"Error creating {self.workspace_name}", response
        )

    def onboard_sentinel(self):
        """Onboard Microsoft Sentinel"""
        resource = (
            self.api_url + f"onboardingStates/default{self.sent_api_version}"
        )
        body = {"properties": {"customerManagedKey": False}}
        response = requests.put(
            url=resource,
            json=body,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(
            f"Error onboarding sentinel to {self.workspace_name}", response
        )

    def delete_sentinel_solution(self):
        """Onboard Microsoft Sentinel"""
        resource = (
            self.api_url + f"onboardingStates/default{self.sent_api_version}"
        )
        response = requests.delete(
            url=resource,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(
            f"Error onboarding sentinel to {self.workspace_name}", response
        )

    def create_sentinel_workspace(self, region: str, tags: dict = None):
        """Create a new workspace"""
        return (
            self.create_resoure_group(region, tags=tags)
            and self.create_log_analytics_workspace(region, tags=tags)
            and self.onboard_sentinel()
        )

    def get_schedule_alerts(self):
        """Gets scheduled alerts in the workspace"""
        alerts = self.client.alert_rules.list(
            resource_group_name=self.resource_group_name,
            workspace_name=self.workspace_name,
        )
        return [x for x in alerts if x.kind == "Scheduled"]

    def get_fusion_alerts(self):
        """Gets fusion alerts in the workspace"""
        alerts = self.client.alert_rules.list(
            resource_group_name=self.resource_group_name,
            workspace_name=self.workspace_name,
        )
        return [x for x in alerts if x.kind == "Fusion"]

    def get_incident_creation_alerts(self):
        """Gets incident creation alerts in the workspace"""
        alerts = self.client.alert_rules.list(
            resource_group_name=self.resource_group_name,
            workspace_name=self.workspace_name,
        )
        return [
            x for x in alerts if x.kind == "MicrosoftSecurityIncidentCreation"
        ]

    def create_update_alert(
        self, alert: sr.ScheduledAlertRule, enabled: bool = False
    ):
        """Create alert in workspace"""
        al.logger.debug(f"Creating alert: {alert.properties.displayName}")
        if alert.name == alert.properties.alertRuleTemplateName:
            alert.name = str(uuid.uuid4())
        resource = self.api_url + f"alertRules/{alert.name}{self.api_version}"
        alert.properties.enabled = enabled
        body = alert.model_dump()
        body.pop("id", None)

        response = requests.put(
            url=resource,
            json=body,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(f"Error creating alert {alert.name}", response)

    def create_update_alerts(self, alerts: list, enabled: bool = False):
        """Create a list of alerts in the workspace"""
        responses = []
        for alert in alerts:
            response = self.create_update_alert(alert, enabled=enabled)
            if response is not None:
                responses.append(response)
        return responses

    def get_table(self, table_name: str):
        """Get a table from the workspace"""
        resource = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/providers/"
            f"Microsoft.OperationalInsights/workspaces/{self.workspace_name}/tables"
            f"/{table_name}{self.ws_api_version}"
        )
        response = requests.get(
            url=resource,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(
            f"Error creating {self.resource_group_name}", response
        )

    def create_table(self, table_properties: dict):
        """create a table in the workspace"""
        resource = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/providers/"
            f"Microsoft.OperationalInsights/workspaces/{self.workspace_name}/tables"
            f"/{table_properties['name']}{self.ws_api_version}"
        )
        response = requests.put(
            url=resource,
            json=table_properties,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(
            f"Error creating {table_properties['name']}", response
        )

    def create_dcr(self, dcr_name, dcr_properties):
        """create a data collection rule"""

        resource = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/providers/"
            f"Microsoft.Insights/dataCollectionRules/{dcr_name}?api-version=2023-03-11"
        )
        response = requests.put(
            url=resource,
            json=dcr_properties,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(f"Error creating {dcr_name}", response)

    def update_dcr(self, dcr_name, dcr_properties):
        """create a data collection rule"""

        resource = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}/"
            f"resourceGroups/{self.resource_group_name}/providers/"
            f"Microsoft.Insights/dataCollectionRules/{dcr_name}?api-version=2023-03-11"
        )
        response = requests.patch(
            url=resource,
            json=dcr_properties,
            headers=self.headers,
            timeout=300,
        )
        return rc.response_check(f"Error creating {dcr_name}", response)
