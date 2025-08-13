import requests
import response_checker as rc
from app_logging import logger


# pylint: disable=W1203
def list_content_product_packages(self):
    """List content product solutions available to the workspace"""
    logger.info(f"Listing all available content product packages")
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


def list_content_packages(self):
    """List content packages in the workspace"""
    logger.info(
        f"Listing installed content packages for workspace: {self.workspace_name}"
    )
    resource = self.api_url + f"contentPackages{self.api_version}"
    logger.debug(f"GET {resource}")
    response = requests.get(
        url=resource,
        headers=self.headers,
        timeout=300,
    )
    return rc.response_check(
        f"Error listing content packages in {self.workspace_name}", response
    )


def install_content_package(self, package_id: str, package_definition: dict):
    """Install content package in the workspace"""
    logger.info(f"Installing content package: {package_id}")
    resource = self.api_url + f"contentPackages/{package_id}{self.api_version}"
    response = requests.put(
        url=resource,
        headers=self.headers,
        json=package_definition,
        timeout=300,
    )
    return rc.response_check(
        f"Error listing content packages in {self.workspace_name}", response
    )


def prepare_package_body(package: dict):
    """Prepare the package body for installation"""
    logger.info(f"Preparing package body for: {package['name']}")
    return {
        "properties": {
            "contentId": package["properties"]["contentId"],
            "contentKind": package["properties"]["contentKind"],
            "contentProductId": package["properties"]["contentProductId"],
            "contentSchemaVersion": package["properties"][
                "contentSchemaVersion"
            ],
            "displayName": package["properties"]["displayName"],
            "version": package["properties"]["version"],
        }
    }


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


def full_solution_deploy(self, desired_solutions: list = None):
    logger.info(f"Starting full solution deployment")
    prod_packages = list_content_product_packages(self)
    prod_packages = [
        package
        for package in prod_packages["value"]
        if package["properties"]["displayName"] in desired_solutions
    ]
    logger.info(f"Filtered packages to deploy")
    for package in prod_packages:
        package_name = package["properties"]["displayName"]
        logger.info(f"Deploying package: {package_name}")
        package_body = prepare_package_body(package)
        installed_package = install_content_package(
            self, package["properties"]["contentId"], package_body
        )
        if not installed_package:
            logger.error(
                f"Failed to install package: {package_name}. Check logs for details."
            )
            continue
        logger.info(f"Installed {package_name} package successfully.")
        product_package = get_content_product_package(self, package["name"])
        if not product_package:
            logger.error(
                "Failed to get content product package details"
                f"for: {package_name}. Check logs for details."
            )
            continue
        full_resources = product_package["properties"]["packagedContent"][
            "resources"
        ]
        source = product_package["properties"]["source"]
        # TODO add in ability to deploy data connectors properly
        for resource in full_resources:
            if not resource["type"].endswith("contentTemplates"):
                continue
            resource_name = resource["properties"]["id"]
            logger.info(f"Deploying resource: {resource_name}")
            template_body = prepare_template_body(resource, source)
            install_result = install_content_template(
                self, resource["properties"]["contentProductId"], template_body
            )
            if not install_result:
                logger.error(
                    f"Failed to deploy resource: {resource_name}."
                    " Check logs for details."
                )
                continue
            logger.info(f"Resource {resource_name} deployed successfully.")
    return prod_packages
