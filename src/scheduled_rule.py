"""
Pydantic model for Scheduled Alert Rule in Microsoft Sentinel
This model is used to define the properties and structure of a scheduled alert
rule in Microsoft Sentinel.

***NOTE: Most other models in this codebase inherit from this model.***

Reference:
    https://learn.microsoft.com/en-us/rest/api/securityinsights/alert-rules/
        create-or-update?view=rest-securityinsights-2024-01-01-preview&
        tabs=HTTP#scheduledalertrule
"""

# pylint: disable=C0103, R0903
from typing import List, Dict
from enum import Enum
import re
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer,
    model_validator,
    ValidationError,
)


# ISO8601 conversion function
def to_iso8601_duration(value: str) -> str:
    """
    Converts a given duration string into ISO8601 format and validates
    that it falls within a specified range.

    Args:
      value (str): duration in days, hours, minutes, and seconds to convert

    Returns:
      String representing a duration in ISO8601 format
    """
    value = value.strip().lower()

    # Already ISO8601?
    iso8601_regex = r"^P(T(?=\d+[HMS])(\d+H)?(\d+M)?(\d+S)?|(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?)$"
    if re.fullmatch(iso8601_regex, value, re.IGNORECASE):
        return value.upper()

    pattern = r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
    match = re.fullmatch(pattern, value)
    if not match:
        raise ValueError(f"Invalid duration format: '{value}'")

    days, hours, minutes, seconds = match.groups()
    duration = "P"
    if days:
        duration += f"{int(days)}D"
    if any([hours, minutes, seconds]):
        duration += "T"
        if hours:
            duration += f"{int(hours)}H"
        if minutes:
            duration += f"{int(minutes)}M"
        if seconds:
            duration += f"{int(seconds)}S"

    # Check range: 5 minutes to 14 days
    total_minutes = (
        (int(days) if days else 0) * 1440
        + (int(hours) if hours else 0) * 60
        + (int(minutes) if minutes else 0)
    )
    if total_minutes < 5 or total_minutes > 14 * 1440:
        raise ValueError("Duration must be between 5 minutes and 14 days")

    return duration


class AlertSeverity(str, Enum):
    """Model"""

    High = "High"
    Medium = "Medium"
    Low = "Low"
    Informational = "Informational"


class TriggerOperator(str, Enum):
    """Model"""

    Equal = "Equal"
    NotEqual = "NotEqual"
    GreaterThan = "GreaterThan"
    LessThan = "LessThan"


class AlertProperty(str, Enum):
    """Model"""

    AlertLink = "AlertLink"
    ConfidenceLevel = "ConfidenceLevel"
    ConfidenceScore = "ConfidenceScore"
    ExtendedLinks = "ExtendedLinks"
    ProductComponentName = "ProductComponentName"
    ProductName = "ProductName"
    ProviderName = "ProviderName"
    RemediationSteps = "RemediationSteps"
    SubTechniques = "SubTechniques"
    Techniques = "Techniques"


class AlertPropertyMapping(BaseModel):
    """Model"""

    alertProperty: AlertProperty
    value: str

    class Config:
        """Config"""

        use_enum_values = True


class AlertDetailsOverride(BaseModel):
    """Model"""

    alertDisplayNameFormat: str | None = None
    alertDescriptionFormat: str | None = None
    alertSeverityColumnName: str | None = None
    alertTacticsColumnName: str | None = None
    alertDynamicProperties: List[AlertPropertyMapping] | None = None


class EntityType(str, Enum):
    """Model"""

    Account = "Account"
    AzureResource = "AzureResource"
    CloudApplication = "CloudApplication"
    DNS = "DNS"
    File = "File"
    FileHash = "FileHash"
    Host = "Host"
    IP = "IP"
    MailCluster = "MailCluster"
    MailMessage = "MailMessage"
    Mailbox = "Mailbox"
    Malware = "Malware"
    Process = "Process"
    RegistryKey = "RegistryKey"
    RegistryValue = "RegistryValue"
    SecurityGroup = "SecurityGroup"
    SubmissionMail = "SubmissionMail"
    URL = "URL"


class FieldMapping(BaseModel):
    """Model"""

    columnName: str
    identifier: str


class EntityMapping(BaseModel):
    """Model"""

    entityType: EntityType
    fieldMappings: List[FieldMapping]

    class Config:
        """Config"""

        use_enum_values = True


class EventGroupingAggregationKind(str, Enum):
    """Model"""

    SingleAlert = "SingleAlert"
    AlertPerResult = "AlertPerResult"


class EventGroupingSettings(BaseModel):
    """Model"""

    aggregationKind: EventGroupingAggregationKind

    class Config:
        """Config"""

        use_enum_values = True


class MatchingMethod(str, Enum):
    """Model"""

    AllEntities = "AllEntities"
    Selected = "Selected"
    AnyAlert = "AnyAlert"


class AlertDetail(str, Enum):
    """Model"""

    DisplayName = "DisplayName"
    Severity = "Severity"


class GroupingConfiguration(BaseModel):
    """Model"""

    enabled: bool
    groupByAlertDetails: List[AlertDetail] | None = None
    groupByCustomDetails: List[str] | None = None
    groupByEntities: List[EntityType] | None = None
    lookbackDuration: str
    matchingMethod: MatchingMethod
    reopenClosedIncident: bool

    class Config:
        """Config"""

        use_enum_values = True

    @field_validator("lookbackDuration")
    @classmethod
    def validate_duration(cls, v: str) -> str:
        """validate"""
        return v.strip().lower()

    @field_serializer("lookbackDuration")
    def serialize_duration(self, v: str) -> str:
        """validate"""
        return to_iso8601_duration(v)

    @model_validator(mode="before")
    def check_match_data_present(self) -> "GroupingConfiguration":
        """
        validate when matchingMethod is "Selected", groupByAlertDetails,
        groupByCustomDetails, or groupByEntities must be set
        """
        if self["matchingMethod"] == "Selected" and not (
            self["groupByAlertDetails"]
            or self["groupByCustomDetails"]
            or self["groupByEntities"]
        ):
            raise ValidationError(
                "groupByAlertDetails, groupByEntities, or groupByCustomDetails "
                "must be set when matchingMethod is 'Selected'"
            )
        return self


class IncidentConfiguration(BaseModel):
    """Model"""

    createIncident: bool
    groupingConfiguration: GroupingConfiguration | None = None

    @model_validator(mode="before")
    def check_grouping_config(self) -> "IncidentConfiguration":
        """
        validate when createIncident is True, groupingConfiguration must be set
        """
        if self["createIncident"] and self["groupingConfiguration"] is None:
            raise ValidationError(
                "groupingConfiguration must be set when createIncident is True"
            )
        if (
            not self["createIncident"]
            and self["groupingConfiguration"] is not None
        ):
            raise ValidationError(
                "groupingConfiguration must not be set when createIncident is False"
            )
        return self


class SentinelEntityMapping(BaseModel):
    """Model"""

    columnName: str


class AttackTactic(str, Enum):
    """Model"""

    Collection = "Collection"
    CommandAndControl = "CommandAndControl"
    CredentialAccess = "CredentialAccess"
    DefenseEvasion = "DefenseEvasion"
    Discovery = "Discovery"
    Execution = "Execution"
    Exfiltration = "Exfiltration"
    Impact = "Impact"
    ImpairProcessControl = "ImpairProcessControl"
    InhibitResponseFunction = "InhibitResponseFunction"
    InitialAccess = "InitialAccess"
    LateralMovement = "LateralMovement"
    Persistence = "Persistence"
    PreAttack = "PreAttack"
    PrivilegeEscalation = "PrivilegeEscalation"
    Reconnaissance = "Reconnaissance"
    ResourceDevelopment = "ResourceDevelopment"


class ScheduledAlertRuleProperties(BaseModel):
    """Model"""

    displayName: str
    enabled: bool
    query: str
    queryFrequency: str
    queryPeriod: str
    severity: AlertSeverity
    suppressionDuration: str = "PT5M"
    suppressionEnabled: bool
    triggerOperator: TriggerOperator
    triggerThreshold: int
    incidentConfiguration: IncidentConfiguration | None = None
    sentinelEntitiesMappings: List[SentinelEntityMapping] | None = None
    alertDetailsOverride: AlertDetailsOverride | None = None
    entityMappings: List[EntityMapping] | None = None
    eventGroupingSettings: EventGroupingSettings | None = None
    customDetails: Dict[str, str] | None = None
    description: str | None = None
    tactics: List[AttackTactic] | None = None
    techniques: List[str] | None = None
    subTechniques: List[str] | None = None
    alertRuleTemplateName: str | None = None
    templateVersion: str | None = None

    class Config:
        """Config"""

        use_enum_values = True

    @field_serializer("queryFrequency", "queryPeriod", "suppressionDuration")
    def serialize_duration(self, v: str) -> str:
        """validate"""
        return to_iso8601_duration(v)

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


class CreatedByType(str, Enum):
    """Model"""

    Application = "Application"
    Key = "Key"
    ManagedIdentity = "ManagedIdentity"
    User = "User"


class SystemData(BaseModel):
    """Model"""

    createdBy: str | None = None
    createdByType: CreatedByType | None = None
    createdAt: str | None = None
    lastModifiedBy: str | None = None
    lastModifiedByType: CreatedByType | None = None
    lastModifiedAt: str | None = None

    class Config:
        """Config"""

        use_enum_values = True


class ScheduledAlertRule(BaseModel):
    """Model"""

    kind: str = Field(default="Scheduled")
    properties: ScheduledAlertRuleProperties
    etag: str | None = None
    id: str | None = None
    name: str | None = None
    type: str | None = None
    systemData: SystemData | None = None

    class Config:
        """Config"""

        use_enum_values = True
