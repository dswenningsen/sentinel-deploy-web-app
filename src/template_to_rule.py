"""Turns templates into rules"""

import src.app_logging as al
import src.scheduled_rule as sr
import src.nrt_rule as nr

# pylint: disable=W1203, W0718


def translate_template_to_rule(template, enabled: bool = False):
    """Translates a template to a rule"""
    rule = template.model_dump(mode="python")
    rule["properties"]["alertRuleTemplateName"] = template.name
    rule["properties"]["templateVersion"] = template.properties.version
    rule["properties"]["enabled"] = enabled
    if template.kind == "Scheduled":
        rule = sr.ScheduledAlertRule(**rule)
    elif template.kind == "NRT":
        rule = nr.NrtAlertRule(**rule)
    return rule


def translate_templates_to_rules(templates, enabled: bool = False):
    """Translate a list of templates to rules"""
    rules = []
    for template in templates:
        try:
            rule = translate_template_to_rule(template, enabled=enabled)
            rules.append(rule)
        except Exception as e:
            al.logger.error(
                f"Error translating template {template.properties.displayName} to rule: {e}"
            )
            continue
    return rules
