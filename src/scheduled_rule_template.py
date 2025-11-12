"""
Pydantic model for Scheduled Alert Rule in Microsoft Sentinel
This model is used to define the properties and structure of a scheduled alert
rule template in Microsoft Sentinel.
Reference:
    https://learn.microsoft.com/en-us/rest/api/securityinsights/
        alert-rule-templates/get?view=rest-securityinsights-2024-01-01-preview&
        tabs=HTTP#scheduledalertruletemplate
"""

# pylint: disable=C0103, R0903, E0401, E0213

from typing import List, Dict
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_serializer,
    field_validator,
    ValidationError,
)
import src.scheduled_rule as sr


class AlertRuleTemplateDataSources(BaseModel):
    """Model"""

    connectorId: str | None = None
    dataTypes: List[str] | None = None


class TemplateStatus(str, Enum):
    """Model"""

    Avaliable = "Available"
    Installed = "Installed"
    NotAvailable = "NotAvailable"


class ScheduledAlertRuleTemplateProperties(BaseModel):
    """Model"""

    alertDetailsOverride: sr.AlertDetailsOverride | None = None
    customDetails: Dict[str, str] | None = None
    description: str | None = None
    displayName: str | None = None
    entityMappings: List[sr.EntityMapping] | None = None
    eventGroupingSettings: sr.EventGroupingSettings | None = None
    query: str
    queryFrequency: str
    queryPeriod: str
    requiredDataConnectors: List[AlertRuleTemplateDataSources] | None = None
    severity: sr.AlertSeverity
    status: TemplateStatus | None = None
    subTechniques: List[str] | None = None
    tactics: List[sr.AttackTactic] | None = None
    techniques: List[str] | None = None
    triggerOperator: sr.TriggerOperator | None = None
    triggerThreshold: int | None = None
    version: str

    class Config:
        """Config"""

        use_enum_values = True

    @field_serializer("queryFrequency", "queryPeriod")
    def serialize_duration(self, v: str) -> str:
        """validate"""
        return sr.to_iso8601_duration(v)

    @model_validator(mode="before")
    def validate_techniques(self) -> list[str]:
        """validate"""
        validated_techniques = []
        sub_techniques = []
        if "techniques" in self and self["techniques"] is not None:
            for tech in self["techniques"]:
                if "." in tech:
                    sub_techniques.append(tech)
                    validated_techniques.append(tech.split(".")[0])
                else:
                    validated_techniques.append(tech)
            self["techniques"] = list(set(validated_techniques))
            if "subTechniques" in self and self["subTechniques"] is None:
                self["subTechniques"] = list(set(sub_techniques))
            if "subtechniques" in self and self["subtechniques"] is None:
                self["subTechniques"] = list(set(sub_techniques))
                self.pop("subtechniques")
        return self

    @field_validator("triggerOperator", mode="before")
    @classmethod
    def validate_trigger_operator(cls, value: str) -> str:
        """validate"""
        mapping = {
            "eq": "Equal",
            "ne": "NotEqual",
            "gt": "GreaterThan",
            "lt": "LessThan",
            "equals": "Equal",
            "notequals": "NotEqual",
            "greaterthan": "GreaterThan",
            "lessthan": "LessThan",
        }
        if value in mapping:
            return mapping[value]
        elif value in mapping.values():
            return value
        raise ValidationError(f"Invalid value for triggerOperator: {value}")


class ScheduledAlertRuleTemplate(BaseModel):
    """Model"""

    id: str | None = None
    name: str | None = None
    type: str | None = None
    systemData: sr.SystemData | None = None
    kind: str = Field(default="Scheduled")
    properties: ScheduledAlertRuleTemplateProperties
