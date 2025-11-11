import sentinel_workspace

sc = sentinel_workspace.SentinelWorkspace(
    "25bce547-25db-47a6-a2bc-54e836303446", "rg-testallinone", "ws-testallinone"
)

print("Done")

import json

a = sc.list_rule_content_templates()
json.dump(a, open("templates.json", "w"), indent=4)
