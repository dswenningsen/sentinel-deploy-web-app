"""tester"""

import src.sentinel_workspace
import src.deploy_rules as dr

sc = src.sentinel_workspace.SentinelWorkspace(
    "25bce547-25db-47a6-a2bc-54e836303446",
    "rg-1",
    "ws-1",
    "8e64ba45-8728-476b-bf1f-84bb53f56ff7",
    "f41b6ba9-813b-4096-b769-e3b03e4a0d4c",
    "",
)

a = sc.deploy_rules()

print("Done")
