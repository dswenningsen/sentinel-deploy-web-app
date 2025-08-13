"""
Pydantic model for Scheduled Alert Rule in Microsoft Sentinel
This model is used to define the properties and structure of a scheduled alert
rule in Microsoft Sentinel.
Reference:
    https://learn.microsoft.com/en-us/rest/api/securityinsights/
        alert-rule-templates/get?view=rest-securityinsights-2024-01-01-preview&
        tabs=HTTP#scheduledalertruletemplate
"""

# pylint: disable=C0103, R0903, E0401, E0213

from typing import List
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
import scheduled_rule as sr


class AlertRuleTemplateDataSources(BaseModel):
    """Model"""

    connectorId: str | None = None
    dataTypes: List[str] | None = None


class TemplateStatus(str, Enum):
    """Model"""

    Avaliable = "Available"
    Installed = "Installed"
    NotAvailable = "NotAvailable"


class ScheduledAlertRuleTemplateProperties(sr.ScheduledAlertRuleProperties):
    """Model"""

    enabled: SkipJsonSchema[bool] = Field(default=False)
    suppressionEnabled: SkipJsonSchema[bool] = Field(default=False)
    suppressionDuration: SkipJsonSchema[str] = Field(default="PT5M")
    requiredDataConnectors: List[AlertRuleTemplateDataSources] | None = None
    status: TemplateStatus | None = None
    version: SkipJsonSchema[str | None] = Field(default=None, exclude=True)

    @model_validator(mode="before")
    def alter_template_version(cls, values):
        """Alter templateVersion to version."""
        # TODO: Fix problem Here
        try:
            if values["version"] is not None and (
                "templateVersion" not in values
                or values["templateVersion"] is None
            ):
                values["templateVersion"] = values["version"]
            return values
        except KeyError:
            return values


class ScheduledAlertRuleTemplate(sr.ScheduledAlertRule):
    """Model"""

    properties: ScheduledAlertRuleTemplateProperties
