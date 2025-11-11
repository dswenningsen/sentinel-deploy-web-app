"""
Pydantic model for Scheduled Alert Rule in Microsoft Sentinel
This model is used to define the properties and structure of a scheduled alert
rule in Microsoft Sentinel.
Reference: https://learn.microsoft.com/en-us/rest/api/securityinsights/
            alert-rules/create-or-update?view=rest-securityinsights-
            2024-01-01-preview&tabs=HTTP#nrtalertrule
"""

# pylint: disable=E0213, R0903
from typing import List
from pydantic import (
    BaseModel,
    Field,
    model_validator,
)
import scheduled_rule as sr


class NrtAlertRuleProperties(BaseModel):
    """Model"""

    displayName: str
    enabled: bool = Field(default=False)
    query: str
    severity: sr.AlertSeverity
    suppressionDuration: str
    suppressionEnabled: bool
    alertDetailsOverride: sr.AlertDetailsOverride | None = None
    alertRuleTemplateName: str | None = None
    customDetails: dict | None = None
    description: str | None = None
    entityMappings: List[sr.EntityMapping] | None = None
    eventGroupingSettings: sr.EventGroupingSettings | None
    incidentConfiguration: sr.IncidentConfiguration | None = None
    sentinelEntitiesMappings: List[sr.SentinelEntityMapping] | None
    subTechniques: str | None = None
    tactics: sr.AttackTactic | None = None
    techniques: str | None = None
    templateVersion: str | None

    @model_validator(mode="before")
    def alter_template_version(cls, values):
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


class NrtAlertRule(BaseModel):
    """Model"""

    kind: str = Field(default="NRT")
    properties: NrtAlertRuleProperties
    etag: str | None = None
