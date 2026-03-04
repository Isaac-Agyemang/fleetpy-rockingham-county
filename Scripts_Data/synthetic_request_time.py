import pandas as pd
import numpy as np

# INPUTS
demand_file = r"D:\PROJECT_RA\fleetpy_rockingham\data\processed\demand_hex_res7.csv"
zone_node_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\fleetpy_zone_lookup_res7_with_nodes.csv"

# OUTPUT (FleetPy reads from this exact folder)
out_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\requests_res7.csv"

# Load
demand = pd.read_csv(demand_file)
zn = pd.read_csv(zone_node_file)

# Build mapping: zone_id (hex string) -> node_id (osmid)
z2n = dict(zip(zn["zone_id"].astype(str), zn["node_id"]))

# Map hex to nodes
demand["origin_node"] = demand["o_hex"].astype(str).map(z2n)
demand["destination_node"] = demand["d_hex"].astype(str).map(z2n)

# Drop any unmapped (should be near zero)
demand = demand.dropna(subset=["origin_node", "destination_node"]).copy()

# Create FleetPy requests
N = len(demand)
requests = pd.DataFrame({
    "rq_id": np.arange(1, N+1),
    # Synthetic request times within your sim window (0..7200 seconds)
    "rq_time": np.random.randint(0, 7200, size=N),
    "origin_node": demand["origin_node"].astype(int),
    "destination_node": demand["destination_node"].astype(int),
    "nr_pax": 1
})

# Optional: sort by time (cleaner)
requests = requests.sort_values("rq_time").reset_index(drop=True)

requests.to_csv(out_file, index=False)
print(f"Saved {len(requests)} requests to: {out_file}")