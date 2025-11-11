"""Input and output functions for Sentinel Automation rules."""

import time
from pathlib import Path
import glob
from pydantic import BaseModel
import yaml
import app_logging as al
import nrt_rule_template as nrt
import scheduled_rule_template as srt
import scheduled_rule as sr
import nrt_rule as nr

# pylint: disable=W1203


def write_rule_to_file(rule_2_write: BaseModel, out_dir: Path) -> None:
    """Write rule to file."""

    if rule_2_write.id is not None:
        file_name = out_dir / rule_2_write.id
        file_name = file_name.with_suffix(".yaml")
    else:
        file_name = out_dir / str(time.time())
        file_name = file_name.with_suffix(".yaml")

    data = rule_2_write.model_dump(mode="python")

    def represent_multiline_str(dumper, data):
        if "\n" in data:
            return dumper.represent_scalar(
                "tag:yaml.org,2002:str", data, style="|"
            )
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, represent_multiline_str)
    with open(file_name, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
        # YAML.dump(data, f)


def write_rules_to_file(rules_list: list[BaseModel], out_dir: Path) -> None:
    """Write rules to file."""
    for rule in rules_list:
        try:
            al.logger.debug(f"Writing rule {rule.name} to file")
            write_rule_to_file(rule, out_dir)
        except (
            FileNotFoundError,
            PermissionError,
            OSError,
            IOError,
            OSError,
        ) as e:
            al.logger.error(f"Error writing rule {rule.name} to file: {e}")
            continue


def read_templates_from_file(file_path: Path) -> list[BaseModel]:
    """Read rules from file."""
    modeled_rules = []
    rules = glob.glob(f"{file_path}/*.yaml") + glob.glob(f"{file_path}/*.yml")
    for rule in rules:
        with open(rule, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data.get("kind") == "Scheduled":
                modeled_rules.append(srt.ScheduledAlertRuleTemplate(**data))
            elif data.get("kind") == "NRT":
                modeled_rules.append(nrt.NrtRuleTemplate(**data))
            else:
                al.logger.warning(
                    f"Unknown rule type: {data.get('properties').get('kind')}"
                )
                continue
    return modeled_rules


def read_rules_from_file(file_path: Path) -> list[BaseModel]:
    """Read rules from file."""
    modeled_rules = []
    rules = glob.glob(f"{file_path}/*.yaml") + glob.glob(f"{file_path}/*.yml")
    for rule in rules:
        with open(rule, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data.get("kind") == "Scheduled":
                modeled_rules.append(sr.ScheduledAlertRule(**data))
            elif data.get("kind") == "NRT":
                modeled_rules.append(nr.NrtAlertRule(**data))
            else:
                al.logger.warning(
                    f"Unknown rule type: {data.get('properties').get('kind')}"
                )
                continue
    return modeled_rules


def write_content_packages_to_file(content_packages: list, out_dir: Path):
    for package in content_packages:
        first = str(package["properties"]["displayName"])
        trans_table = str.maketrans("", "", " \\/.")
        first = first.translate(trans_table)
        file_name = out_dir / first
        b = {"properties": package.pop("properties")}
        b["properties"].pop("id")
        file_name = file_name.with_suffix(".yaml")
        with open(file_name, "w", encoding="utf-8") as f:
            yaml.dump(b, f)


def read_content_packages_from_file(file_path: Path) -> list:
    """Read content packages from file."""
    content_packages = []
    packages = glob.glob(f"{file_path}/*.yaml") + glob.glob(
        f"{file_path}/*.yml"
    )
    for package in packages:
        with open(package, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            content_packages.append(data)
    return content_packages
