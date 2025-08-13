import sentinel_workspace

sc = sentinel_workspace.SentinelWorkspace(
    "25bce547-25db-47a6-a2bc-54e836303446", "rg-2", "ws-2"
)

a = sc.deploy_solutions()
print("Done")
