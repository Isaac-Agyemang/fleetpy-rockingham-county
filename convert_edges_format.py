import pandas as pd

net_dir = r"D:\PROJECT_RA\FleetPy\data\networks\rockingham_res7\base"

edges = pd.read_csv(net_dir + r"\edges.csv")

# FleetPy expects from/to node ids that match nodes.node_index,
# plus a travel time (seconds) and a distance (meters).
# We'll create the most common minimal schema used by NetworkBasic:
# from_node,to_node,travel_time,distance
# (If your FleetPy version expects different column names, the next error will tell us exactly.)

edges_out = pd.DataFrame({
    "from_node": edges["u"].astype(int),
    "to_node": edges["v"].astype(int),
    # OSMnx travel_time is usually seconds when created via add_edge_travel_times
    "travel_time": edges["travel_time"].astype(float),
    "distance": edges["length"].astype(float),
})

edges_out.to_csv(net_dir + r"\edges.csv", index=False)

print("✅ edges.csv converted. Columns:", edges_out.columns.tolist())
print(edges_out.head())
print("Rows:", len(edges_out))