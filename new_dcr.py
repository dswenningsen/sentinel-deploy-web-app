class dcr:
    """dcr"""

    def __init__(self, subscription_id, resource_group, ws_name, table_name):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.ws_name = ws_name
        self.table_name = table_name
        self.dcr_body = {
            "location": "westus",
            "kind": "Linux",
            "properties": {
                "dataSources": {
                    "syslog": [
                        {
                            "streams": ["Microsoft-Syslog"],
                            "facilityNames": ["local4"],
                            "logLevels": ["*"],
                            "name": "sysLogsDataSource-1039681476",
                        },
                        {
                            "streams": ["Microsoft-Syslog"],
                            "facilityNames": ["nopri"],
                            "logLevels": ["Emergency"],
                            "name": "sysLogsDataSource-1697966155",
                        },
                    ]
                },
                "destinations": {
                    "logAnalytics": [
                        {
                            "workspaceResourceId": (
                                f"/subscriptions/{self.subscription_id}/resourcegroups/"
                                f"{self.resource_group}/providers/"
                                f"microsoft.operationalinsights/workspaces/{self.ws_name}"
                            ),
                            "name": "DataCollectionEvent",
                        }
                    ]
                },
                "dataFlows": [
                    {
                        "streams": ["Microsoft-Syslog"],
                        "destinations": ["DataCollectionEvent"],
                        "transformKql": 'source\n| where SyslogMessage !startswith "FILTER:"\n',
                        "outputStream": "Microsoft-Syslog",
                    },
                    {
                        "streams": ["Microsoft-Syslog"],
                        "destinations": ["DataCollectionEvent"],
                        "transformKql": "source\n| where SyslogMessage startswith \"FILTER: Junos:\"\n",  # fmt: skip
                        "outputStream": f"Custom-{self.table_name}",
                    },
                ],
            },
        }
