"""Delete multiple Sentinel workspaces for testing purposes"""

import src.sentinel_workspace as sw

# For numbered in sequence
# for i in range(9):
#     print(f"Deleting attempt {i}")
#     sc = sw.SentinelWorkspace(
#         tenant_id="8e64ba45-8728-476b-bf1f-84bb53f56ff7",
#         client_id="f41b6ba9-813b-4096-b769-e3b03e4a0d4c",
#         client_secret="",
#         sub_id="25bce547-25db-47a6-a2bc-54e836303446",
#         rg_name=f"rg-{i}",
#         ws_name=f"ws-{i}",
#     )
#     sc.delete_sentinel_solution()

# For single ws
sc = sw.SentinelWorkspace(
    tenant_id="8e64ba45-8728-476b-bf1f-84bb53f56ff7",
    client_id="f41b6ba9-813b-4096-b769-e3b03e4a0d4c",
    client_secret="",
    sub_id="25bce547-25db-47a6-a2bc-54e836303446",
    rg_name=f"rg-revert",
    ws_name=f"ws-revert",
)
sc.delete_sentinel_solution()

print("done")
