import pandas as pd

# ----------------------------
# PATHS (your project)
# ----------------------------
net_dir = r"D:\PROJECT_RA\FleetPy\data\networks\rockingham_res7\base"
demand_dir = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7"

nodes_path = net_dir + r"\nodes.csv"
edges_path = net_dir + r"\edges.csv"

req_path = demand_dir + r"\requests_res7.csv"
zone_nodes_path = demand_dir + r"\fleetpy_zone_lookup_res7_with_nodes.csv"  # if present

# ----------------------------
# 1) Load nodes + build mapping old_id -> new_id (0..N-1)
# ----------------------------
nodes = pd.read_csv(nodes_path)

# old node ids are currently in node_index (OSM IDs)
old_ids = nodes["node_index"].astype(int).tolist()
mapping = {old_id: new_id for new_id, old_id in enumerate(old_ids)}

# write nodes with sequential ids
nodes_out = nodes.copy()
nodes_out["node_index"] = nodes_out["node_index"].astype(int).map(mapping).astype(int)
nodes_out.to_csv(nodes_path, index=False)
print(f"✅ nodes remapped to sequential IDs. N={len(nodes_out):,}")

# ----------------------------
# 2) Remap edges
# ----------------------------
edges = pd.read_csv(edges_path)

edges_out = edges.copy()
edges_out["from_node"] = edges_out["from_node"].astype(int).map(mapping)
edges_out["to_node"]   = edges_out["to_node"].astype(int).map(mapping)

before = len(edges_out)
edges_out = edges_out.dropna(subset=["from_node", "to_node"]).copy()
edges_out["from_node"] = edges_out["from_node"].astype(int)
edges_out["to_node"]   = edges_out["to_node"].astype(int)

edges_out.to_csv(edges_path, index=False)
print(f"✅ edges remapped. kept {len(edges_out):,}/{before:,} edges")

# ----------------------------
# 3) Remap requests origin/destination nodes
# ----------------------------
req = pd.read_csv(req_path)

req["origin_node"] = req["origin_node"].astype(int).map(mapping)
req["destination_node"] = req["destination_node"].astype(int).map(mapping)

missing_o = req["origin_node"].isna().sum()
missing_d = req["destination_node"].isna().sum()

# If anything is missing, drop those rows (should be ~0 if snapping was correct)
req_out = req.dropna(subset=["origin_node", "destination_node"]).copy()
req_out["origin_node"] = req_out["origin_node"].astype(int)
req_out["destination_node"] = req_out["destination_node"].astype(int)

req_out.to_csv(req_path, index=False)
print(f"✅ requests remapped. dropped {len(req)-len(req_out):,} rows "
      f"(missing origin={missing_o:,}, missing dest={missing_d:,})")

# ----------------------------
# 4) Optional: remap zone lookup file that stores node IDs
# ----------------------------
import os
if os.path.exists(zone_nodes_path):
    zn = pd.read_csv(zone_nodes_path)
    for col in zn.columns:
        if "node" in col.lower():
            zn[col] = zn[col].astype(int).map(mapping)
    zn = zn.dropna().copy()
    for col in zn.columns:
        if "node" in col.lower():
            zn[col] = zn[col].astype(int)
    zn.to_csv(zone_nodes_path, index=False)
    print("✅ zone lookup with nodes remapped")
else:
    print("ℹ️ zone lookup with nodes not found (skipped)")

print("DONE.")