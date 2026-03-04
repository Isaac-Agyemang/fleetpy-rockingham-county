import pandas as pd
import numpy as np

# INPUTS
demand_file = r"D:\PROJECT_RA\fleetpy_rockingham\data\processed\demand_hex_res7.csv"
zone_node_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\fleetpy_zone_lookup_res7_with_nodes.csv"

# OUTPUT (FleetPy reads from this exact folder)
out_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\requests_res7.csv"

# -------------------------
# Load data
# -------------------------
demand = pd.read_csv(demand_file)
zn = pd.read_csv(zone_node_file)

# Build mapping: zone_id (hex string) -> node_id
z2n = dict(zip(zn["zone_id"].astype(str), zn["node_id"]))

# Map hex to nodes
demand["origin_node"] = demand["o_hex"].astype(str).map(z2n)
demand["destination_node"] = demand["d_hex"].astype(str).map(z2n)

# Drop unmapped
demand = demand.dropna(subset=["origin_node", "destination_node"]).copy()

# =========================
# REALISTIC TIME MODEL (NO CLIPPING SPIKE)
# =========================
N = len(demand)
TMAX = 39600  # 11 hours (6am–5pm), seconds since 6am

# Morning, Midday, Afternoon peaks
period = np.random.choice([0, 1, 2], size=N, p=[0.45, 0.15, 0.40])

means = np.array([7200, 21600, 36000])  # 8am, 12pm, 4pm (since 6am)
stds  = np.array([3600, 5400, 3600])

# Re-sample out-of-range values instead of clipping them to 0/TMAX
rq_time = np.empty(N, dtype=int)
for i in range(N):
    mu = means[period[i]]
    sigma = stds[period[i]]
    t = int(round(np.random.normal(mu, sigma)))
    while t < 0 or t > TMAX:
        t = int(round(np.random.normal(mu, sigma)))
    rq_time[i] = t

# =========================
# CREATE REQUEST FILE
# =========================
requests = pd.DataFrame({
    "rq_id": np.arange(1, N + 1),
    "rq_time": rq_time,
    "origin_node": demand["origin_node"].astype(int),
    "destination_node": demand["destination_node"].astype(int),
    "nr_pax": 1
})

# Optional: sort by time (cleaner)
requests = requests.sort_values("rq_time").reset_index(drop=True)

# Save
requests.to_csv(out_file, index=False)

print(f"Saved {len(requests)} requests to: {out_file}")
print("rq_time range:", requests["rq_time"].min(), requests["rq_time"].max())
print("Requests at TMAX:", (requests["rq_time"] == TMAX).sum())
print("Requests at 0:", (requests["rq_time"] == 0).sum())