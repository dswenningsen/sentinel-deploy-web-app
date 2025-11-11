"""Work with contents of the Azure Sentinel repo."""

import os
from github import Github, Auth
import yaml
import app_logging as al
import scheduled_rule_template as srt
import nrt_rule_template as nrt

# pylint: disable=W1203, W0718

SENTINEL_REPO = "Azure/Azure-Sentinel"
REPO_FOLDER = "Solutions"


def change_template_format(template_dict: dict) -> dict:
    """Change the template format to match the model."""
    property_field_list = [
        "displayName",
        "enabled",
        "query",
        "queryFrequency",
        "queryPeriod",
        "severity",
        "suppressionDuration",
        "suppressionEnabled",
        "triggerOperator",
        "triggerThreshold",
        "incidentConfiguration",
        "sentinelEntitiesMappings",
        "alertDetailsOverride",
        "entityMappings",
        "eventGroupingSettings",
        "customDetails",
        "description",
        "tactics",
        "techniques",
        "subTechniques",
        "alertRuleTemplateName",
        "version",
        "status",
    ]
    properites_fields = {
        k: template_dict.pop(k)
        for k in property_field_list
        if k in template_dict
    }
    template_dict["properties"] = properites_fields
    if "relevantTechniques" in template_dict:
        template_dict["properties"]["techniques"] = template_dict.pop(
            "relevantTechniques"
        )
    if (
        template_dict.get("properties").get("displayName") is None
        or template_dict.get("properties").get("displayName") == ""
    ):
        template_dict["properties"]["displayName"] = template_dict.get("name")
    return template_dict


def yaml_rules_2_dictionary(contents, reformat, repo) -> list[dict]:
    """Convert YAML rules from repo to dictionary format."""
    rules = []
    while contents:
        content = contents.pop(0)
        # for content in contents:
        if content.type == "file" and content.name.endswith((".yaml", ".yml")):
            try:
                yaml_data = yaml.safe_load(content.decoded_content.decode())
                if reformat:
                    yaml_data = change_template_format(yaml_data)
                rules.append(yaml_data)
            except yaml.YAMLError as e:
                al.logger.error(f"Error decoding YAML in {content.path}: {e}")
        if content.type == "dir":
            al.logger.info(f"Found sub-directory: {content.path}")
            contents.extend(repo.get_contents(content.path))
    return rules


def get_rules_for_solution(repo, solution_contents, reformat):
    """Get rules for a solution in the repo."""
    for content in solution_contents:
        if (
            "analytic" in content.name.lower() or "rule" in content.name.lower()
        ) and content.type == "dir":
            al.logger.info(f"Found Analytic folder in {content.path}")
            if content.name != "Analytic Rules":
                al.logger.warning(
                    f"Improperly formatted folder name: {content.path}"
                )
            solution_rules = yaml_rules_2_dictionary(
                repo.get_contents(content.path), reformat, repo
            )
            return solution_rules
    solution_name = solution_contents[0].path.split("/")[1]
    al.logger.info(f"No Analytic folder found for {solution_name}")
    return


def get_rules_from_repo(reformat=True, include: list = None) -> list[dict]:
    """Get rules from the Azure Sentinel repo Solutions."""
    token = os.getenv("GITHUB_TOKEN")
    if token is None:
        al.logger.error("GITHUB_TOKEN environment variable not set")
        return []
    auth = Auth.Token(token)
    g = Github(auth=auth)
    al.logger.info("Starting to process solutions...")
    repo = g.get_repo(SENTINEL_REPO)
    solutions = repo.get_contents(REPO_FOLDER)
    rules = []
    if include:
        al.logger.info(f"Filtering solutions to include: {include}")
        solutions = [
            solution for solution in solutions if solution.name in include
        ]
    for solution in solutions:
        al.logger.info(f"Processing {solution.name}...")
        try:
            rules.extend(
                get_rules_for_solution(
                    repo, repo.get_contents(solution.path), reformat
                )
            )
        except Exception as e:
            if "NoneType" not in str(e):
                al.logger.error(f"Error processing {solution.name}: {e}")

    al.logger.info(f"Total rules found: {len(rules)}")
    return rules


def model_rules_from_repo(reformat=True, include: list = None):
    """Get rules from repo and model them."""
    rules = get_rules_from_repo(reformat=reformat, include=include)
    modeled_rules = []
    for rule in rules:
        try:
            al.logger.debug(f"Modeling rule {rule['name']}")
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
