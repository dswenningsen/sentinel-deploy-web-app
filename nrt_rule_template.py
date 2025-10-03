"""
NRT Rule Template Model
This module defines the NRT Rule Template model for Microsoft Sentinel.
Reference: https://learn.microsoft.com/en-us/rest/api/securityinsights/
            alert-rules/create-or-update?view=rest-securityinsights-
            2024-01-01-preview&tabs=HTTP#nrtalertrule
"""

from typing import List
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema
import scheduled_rule_template as srt


class NrtRuleTemplateProperties(srt.ScheduledAlertRuleTemplateProperties):
    """Model"""

    # TODO: Rewrite to not inherit from scheduled rule template
    queryFrequency: SkipJsonSchema[str] = Field(default=None, exclude=True)
    queryPeriod: SkipJsonSchema[str] = Field(default=None, exclude=True)
    displayName: SkipJsonSchema[str] = Field(default=None, exclude=True)
    status: SkipJsonSchema[srt.TemplateStatus] = Field(
        default=None, exclude=True
    )
    triggerOperator: SkipJsonSchema[str] = Field(default=None, exclude=True)
    triggerThreshold: SkipJsonSchema[int] = Field(default=None, exclude=True)


class NrtRuleTemplate(srt.ScheduledAlertRuleTemplate):
    """Model"""

    # TODO: Rewrite to not inherit from scheduled rule template
    alertRulesCreatedByTemplateCount: int | None = None
    createdDateUTC: str | None = None
    description: str | None = None
    displayName: str | None = None
    lastUpdatedDateUTC: str | None = None
    status: srt.TemplateStatus | None = None
    properties: NrtRuleTemplateProperties
    requiredDataConnectors: List[srt.AlertRuleTemplateDataSources] | None = None
