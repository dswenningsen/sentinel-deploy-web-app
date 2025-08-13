"""
Pydantic model for Scheduled Alert Rule in Microsoft Sentinel
This model is used to define the properties and structure of a scheduled alert
rule in Microsoft Sentinel.
Reference: https://learn.microsoft.com/en-us/rest/api/securityinsights/
            alert-rules/create-or-update?view=rest-securityinsights-
            2024-01-01-preview&tabs=HTTP#nrtalertrule
"""

# pylint: disable=C0103, R0903, E0401, E0213
from pydantic import Field, model_validator
from pydantic.json_schema import SkipJsonSchema
import nrt_rule_template as nrt
import scheduled_rule_template as srt


class NrtAlertRuleProperties(nrt.NrtRuleTemplateProperties):
    """Model"""

    displayName: str
    templateVersion: str | None
    version: SkipJsonSchema[str | None] = Field(default=None, exclude=True)

    @model_validator(mode="before")
    def alter_templateVersion(cls, values):
        """Alter templateVersion to version."""
        try:
            if (
                values["version"] is not None
                and values["templateVersion"] is None
            ):
                values["templateVersion"] = values["version"]
            return values
        except KeyError:
            return values


class NrtAlertRule(nrt.NrtRuleTemplate):
    """Model"""

    kind: str = Field(default="NRT")
    properties: NrtAlertRuleProperties
    displayName: SkipJsonSchema[str | None] = Field(default=None, exclude=True)
    alertRulesCreatedByTemplateCount: SkipJsonSchema[int | None] = Field(
        default=None, exclude=True
    )
    createdDateUTC: SkipJsonSchema[str | None] = Field(
        default=None, exclude=True
    )
    description: SkipJsonSchema[str | None] = Field(default=None, exclude=True)
    lastUpdatedDateUTC: SkipJsonSchema[str | None] = Field(
        default=None, exclude=True
    )
    name: SkipJsonSchema[str] = Field(default=None, exclude=True)
    status: SkipJsonSchema[srt.TemplateStatus | None] = Field(
        default=None, exclude=True
    )
