import sentinel_workspace

sc = sentinel_workspace.SentinelWorkspace(
    tenant_id="8e64ba45-8728-476b-bf1f-84bb53f56ff7",
    client_id="f41b6ba9-813b-4096-b769-e3b03e4a0d4c",
    client_secret="",
    sub_id="25bce547-25db-47a6-a2bc-54e836303446",
    rg_name="rg-4",
    ws_name="ws-4",
)

sc.delete_sentinel_solution()
print("done")
