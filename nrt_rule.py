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
from typing import List
from enum import Enum


# TODO: class AlertDetailsOverride
class AlertDetailsOverride:
    a = 1


# TODO: EntityMapping
class EntityMapping:
    a = 1


# TODO: EventGroupingSettings
class EventGroupingSettings:
    a = 1


# TODO: IncidentConfiguration
class IncidentConfiguration:
    a = 1


# TODO: SentinelEntityMapping
class SentinelEntityMapping:
    a = 1


# TODO: AttackTactic
class AttackTactic:
    a = 1


class NrtAlertRuleProperties:
    """Model"""

    displayName: str
    enabled: bool = Field(default=False)
    query: str
    severity: str
    suppressionDuration: str
    suppressionEnabled: bool
    alertDetailsOverride: AlertDetailsOverride | None = None
    alertRuleTemplateName: str | None = None
    customDetails: dict | None = None
    description: str | None = None
    entityMappings: List[EntityMapping] | None = None
    eventGroupingSettings: EventGroupingSettings | None
    incidentConfiguration: IncidentConfiguration | None = None
    sentinelEntitiesMappings: List[SentinelEntityMapping] | None
    subTechniques: str | None = None
    tactics: AttackTactic | None = None
    techniques: str | None = None
    templateVersion: str | None

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


class NrtAlertRule:
    """Model"""

    kind: str = Field(default="NRT")
    properties: NrtAlertRuleProperties
    etag: str | None = None
