import pandas as pd
from pathlib import Path
import numpy as np

# Inputs
LOOKUP = Path("data/processed/fleetpy_zone_lookup_res7.csv")
R5_MATRIX = Path("data/processed/travel_time_matrix_hex_res7_car.csv")

# Outputs
OUT_TT = Path("data/processed/fleetpy_tt_matrix_res7.csv")
OUT_DIST = Path("data/processed/fleetpy_dist_matrix_res7.csv")

AVG_SPEED_MPH = 35

# Load lookup and R5 matrix
zones = pd.read_csv(LOOKUP)
r5 = pd.read_csv(R5_MATRIX)

# Map hex → integer zone
hex_to_int = dict(zip(zones["zone_id"], zones["zone_int"]))

r5["origin_zone"] = r5["from_id"].map(hex_to_int)
r5["dest_zone"] = r5["to_id"].map(hex_to_int)

n = len(zones)
idx = list(range(1, n + 1))

# Initialize full matrices
tt_mat = pd.DataFrame(np.zeros((n, n)), index=idx, columns=idx)
dist_mat = pd.DataFrame(np.zeros((n, n)), index=idx, columns=idx)

# Fill matrices
for _, row in r5.iterrows():
    o = int(row["origin_zone"])
    d = int(row["dest_zone"])
    t = float(row["travel_time"])
    tt_mat.loc[o, d] = t
    dist_mat.loc[o, d] = round(t * (AVG_SPEED_MPH / 60), 3)

# Save
tt_mat.to_csv(OUT_TT, index=True)
dist_mat.to_csv(OUT_DIST, index=True)

print("✅ Full FleetPy matrices built")
print("Zones:", n)
print("Expected cells:", n * n)
print("Time matrix shape:", tt_mat.shape)
print("Distance matrix shape:", dist_mat.shape)