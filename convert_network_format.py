import pandas as pd

net_dir = r"D:\PROJECT_RA\FleetPy\data\networks\rockingham_res7\base"

# --- nodes ---
nodes = pd.read_csv(net_dir + r"\nodes.csv")
# expect columns: osmid,x,y
nodes_out = pd.DataFrame({
    "node_index": nodes["osmid"].astype(int),
    "is_stop_only": 0,
    "pos_x": nodes["x"].astype(float),
    "pos_y": nodes["y"].astype(float),
})
nodes_out.to_csv(net_dir + r"\nodes.csv", index=False)

print("✅ nodes.csv converted to FleetPy format:", nodes_out.columns.tolist())
print(nodes_out.head())

# --- edges ---
edges = pd.read_csv(net_dir + r"\edges.csv")
# If your edges file has columns u,v,travel_time,length etc, keep u/v but rename to what FleetPy expects later if needed.
print("ℹ️ edges.csv columns currently:", edges.columns.tolist())