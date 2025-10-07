"""
NRT Rule Template Model
This module defines the NRT Rule Template model for Microsoft Sentinel.
Reference: https://learn.microsoft.com/en-us/rest/api/securityinsights/
            alert-rules/create-or-update?view=rest-securityinsights-
            2024-01-01-preview&tabs=HTTP#nrtalertrule
"""

from typing import List, Dict
from pydantic import Field, BaseModel
from pydantic.json_schema import SkipJsonSchema
import scheduled_rule as sr
import scheduled_rule_template as srt


class NrtRuleTemplateProperties(BaseModel):
    """Model"""

    alertDetailsOverride: sr.AlertDetailsOverride | None = None
    customDetails: Dict[str, str] | None = None
    entityMappings: List[sr.EntityMapping] | None = None
    eventGroupingSettings: sr.EventGroupingSettings | None = None
    query: str
    sentinelEntitiesMappings: List[sr.SentinelEntityMapping] | None = None
    severity: sr.AlertSeverity
    tactics: List[sr.AttackTactic] | None = None
    techniques: List[str] | None = None
    version: str
    requiredDataConnectors: List[srt.AlertRuleTemplateDataSources] | None = None
    status: srt.TemplateStatus | None = None


class NrtRuleTemplate(BaseModel):
    """Model"""

    kind: str = Field(default="NRT")
    displayName: str
    description: str | None = None
    properties: NrtRuleTemplateProperties
