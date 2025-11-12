"""Deploy and manage content product solutions in a workspace"""

import requests
import src.response_checker as rc
from src.app_logging import logger


# pylint: disable=W1203
def list_content_product_packages(self):
    """List content product solutions available to the workspace"""
    logger.info("Listing all available content product packages")
    query_filter = "$filter=properties/contentKind eq 'Solution'"
    resource = (
        self.api_url
        + f"contentProductPackages{self.api_version}&{query_filter}"
    )
    logger.debug(f"GET {resource}")
    response = requests.get(
        url=resource,
        headers=self.headers,
        timeout=300,
    )
    return rc.response_check(
        f"Error listing content packages in {self.workspace_name}", response
    )


def get_content_product_package(self, package_name: str):
    """Get details of a specific content product package"""
    logger.info(f"Getting content product package details for: {package_name}")
    resource = (
        self.api_url
        + f"contentProductPackages/{package_name}{self.api_version}"
    )
    logger.debug(f"GET {resource}")
    response = requests.get(
        url=resource,
        headers=self.headers,
        timeout=300,
    )
    return rc.response_check(
        f"Error getting content product package {package_name} in {self.workspace_name}",
        response,
    )


def prepare_template_body(template: dict, source: dict):
    """Prepare the template body for deployment"""
    logger.info(
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


def install_content_template(self, template_id: str, template_body: dict):
    """Install content template in the workspace"""
    logger.info(f"Installing content template: {template_id}")
    resource = (
        self.api_url + f"contentTemplates/{template_id}{self.api_version}"
    )
    logger.debug(f"PUT {resource}")
    response = requests.put(
        url=resource,
        headers=self.headers,
        json=template_body,
        timeout=300,
    )
    return rc.response_check(
        f"Error installing content template {template_id} in {self.workspace_name}",
        response,
    )


def deploy_solution_content(self, package_body: dict, deploy_name: str):
    """Deploy solution content to the workspace"""
    logger.info(
        f"Deploying solution content with deployment name: {deploy_name}"
    )
    resource = (
        f"https://management.azure.com/subscriptions/{self.subscription_id}/"
        f"resourceGroups/{self.resource_group_name}/"
        f"providers/Microsoft.Resources/deployments/{deploy_name}"
        "?api-version=2025-04-01"
    )
    logger.debug(f"PUT {resource}")
    response = requests.put(
        url=resource,
        headers=self.headers,
        json=package_body,
        timeout=300,
    )
    return rc.response_check(
        "Error deploying solution content with deployment name: "
        f"{deploy_name} in {self.workspace_name}",
        response,
    )


def full_solution_deploy(
    self, ws_location: str, desired_solutions: list = None
):
    """Deploy all desired solutions to the workspace"""
    logger.info("Starting full solution deployment")
    # Get all possible solutions that can be deployed
    prod_packages = list_content_product_packages(self)
    # Filter to only those we want to deploy
    prod_packages = [
        package
        for package in prod_packages["value"]
        if package["properties"]["displayName"] in desired_solutions
    ]
    logger.info("Filtered packages to deploy")
    for package in prod_packages:
        package_name = package["properties"]["displayName"]
        logger.info(f"Deploying package: {package_name}")
        # Get the solution and all of its content
        product_package = get_content_product_package(self, package["name"])
        if not product_package:
            logger.error(
                "Failed to get content product package details"
                f"for: {package_name}. Check logs for details."
            )
            continue

        # Remove invalid characters
        full_resources = product_package["properties"]["packagedContent"][
            "resources"
        ]
        for resource in full_resources:
            if (
                "mainTemplate" in resource["properties"].keys()
                and "metadata" in resource["properties"]["mainTemplate"].keys()
                and "postDeployment"
                in resource["properties"]["mainTemplate"]["metadata"].keys()
            ):
                resource["properties"]["mainTemplate"]["metadata"][
                    "postDeployment"
                ] = None
        # Prepare the body for deployment
        package_content_body = {
            "properties": {
                "parameters": {
                    "workspace": {"value": self.workspace_name},
                    "workspace-location": {"value": ws_location},
                },
                "template": product_package["properties"]["packagedContent"],
                "mode": "Incremental",
            }
        }
        # Create deployment name, max length is 64 characters
        deploy_name = f"deploy-{package_name.replace(' ', '-')}"
        if len(deploy_name) > 64:
            deploy_name = deploy_name[:64]
        # Deploy the solution and all of its contents
        install_result = deploy_solution_content(
            self, package_content_body, deploy_name
        )
        if not install_result:
            logger.error(
                f"Failed to deploy resource: {package_name}."
                " Check logs for details."
            )
            continue
        logger.info(f"Resource {package_name} deployed successfully.")
    return prod_packages


# Not currently used
# __________________________________________
# def list_content_packages(self):
#     """List content packages in the workspace"""
#     logger.info(
#         f"Listing installed content packages for workspace: {self.workspace_name}"
#     )
#     resource = self.api_url + f"contentPackages{self.api_version}"
#     logger.debug(f"GET {resource}")
#     response = requests.get(
#         url=resource,
#         headers=self.headers,
#         timeout=300,
#     )
#     return rc.response_check(
#         f"Error listing content packages in {self.workspace_name}", response
#     )

# def install_content_package(self, package_id: str, package_definition: dict):
#     """Install content package in the workspace"""
#     logger.info(f"Installing content package: {package_id}")
#     resource = self.api_url + f"contentPackages/{package_id}{self.api_version}"
#     response = requests.put(
#         url=resource,
#         headers=self.headers,
#         json=package_definition,
#         timeout=300,
#     )
#     return rc.response_check(
#         f"Error listing content packages in {self.workspace_name}", response
#     )

# def prepare_package_body(package: dict):
# """Prepare the package body for installation"""
# logger.info(f"Preparing package body for: {package['name']}")
# return {
#     "properties": {
#         "contentId": package["properties"]["contentId"],
#         "contentKind": package["properties"]["contentKind"],
#         "contentProductId": package["properties"]["contentProductId"],
#         "contentSchemaVersion": package["properties"][
#             "contentSchemaVersion"
#         ],
#         "displayName": package["properties"]["displayName"],
#         "version": package["properties"]["version"],
#     }
# }


# __________________________________________
