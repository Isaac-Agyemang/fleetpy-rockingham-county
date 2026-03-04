import pandas as pd
from pathlib import Path

ZONES_IN = Path("data/processed/hex_zones_res7.csv")                 # zone_id (hex), lat, lon
OD_IN    = Path("data/processed/od_with_time_distance_res7.csv")     # o_hex, d_hex, trips, travel_time, distance_miles

OUT_LOOKUP = Path("data/processed/fleetpy_zone_lookup_res7.csv")
OUT_OD_LONG = Path("data/processed/fleetpy_od_long_res7.csv")
OUT_TRIPS_MAT = Path("data/processed/fleetpy_od_trips_matrix_res7.csv")

# ---------- 1) Zone lookup: hex -> integer zone_id_int ----------
zones = pd.read_csv(ZONES_IN)

# Ensure deterministic ordering
zones = zones.sort_values("zone_id").reset_index(drop=True)
zones["zone_int"] = range(1, len(zones) + 1)

# Save lookup
zones[["zone_int", "zone_id", "lat", "lon"]].to_csv(OUT_LOOKUP, index=False)

# Build dict for mapping
hex_to_int = dict(zip(zones["zone_id"], zones["zone_int"]))

# ---------- 2) OD long format with integer zone IDs ----------
od = pd.read_csv(OD_IN)

od["origin_zone"] = od["o_hex"].map(hex_to_int)
od["dest_zone"]   = od["d_hex"].map(hex_to_int)

# Basic sanity: make sure no missing mappings
if od["origin_zone"].isna().any() or od["dest_zone"].isna().any():
    raise ValueError("Some hex IDs in OD file were not found in hex_zones_res7.csv")

# FleetPy-friendly aggregated OD table
od_long = od[["origin_zone", "dest_zone", "trips", "travel_time", "distance_miles"]].copy()
od_long = od_long.sort_values(["origin_zone", "dest_zone"]).reset_index(drop=True)

od_long.to_csv(OUT_OD_LONG, index=False)

# ---------- 3) Trips matrix (wide 163x163) ----------
n = len(zones)
trips_mat = pd.DataFrame(0, index=range(1, n+1), columns=range(1, n+1))

for _, r in od_long.iterrows():
    trips_mat.loc[int(r["origin_zone"]), int(r["dest_zone"])] = int(r["trips"])

trips_mat.to_csv(OUT_TRIPS_MAT, index=True)

print("✅ Saved:")
print(" -", OUT_LOOKUP)
print(" -", OUT_OD_LONG)
print(" -", OUT_TRIPS_MAT)
print(f"Zones: {n} | OD pairs: {len(od_long)} | Total trips: {od_long['trips'].sum()}")