import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

# Paths
zone_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\fleetpy_zone_lookup_res7.csv"
nodes_file = r"D:\PROJECT_RA\FleetPy\data\networks\rockingham_res7\nodes.csv"
output_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\fleetpy_zone_lookup_res7_with_nodes.csv"

# Load data
zones = pd.read_csv(zone_file)
nodes = pd.read_csv(nodes_file)

# Build KDTree using nodes (y = lat, x = lon)
node_coords = np.vstack((nodes["y"], nodes["x"])).T
tree = cKDTree(node_coords)

# Zone centroid coordinates
zone_coords = np.vstack((zones["lat"], zones["lon"])).T

# Find nearest node
dist, idx = tree.query(zone_coords, k=1)

# Assign osmid as node_id
zones["node_id"] = nodes.iloc[idx]["osmid"].values

# Save new file
zones.to_csv(output_file, index=False)

print("Zone-to-node mapping created successfully.")