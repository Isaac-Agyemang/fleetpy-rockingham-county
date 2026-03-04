import pandas as pd
from pathlib import Path

# Paths
OD_FILE = Path("data/processed/od_hex_res7.csv")
TT_FILE = Path("data/processed/travel_time_matrix_hex_res7_car.csv")
OUT_FILE = Path("data/processed/od_with_travel_time_res7.csv")

# Load
od = pd.read_csv(OD_FILE)
tt = pd.read_csv(TT_FILE)

# Rename columns so they match
tt = tt.rename(columns={
    "from_id": "o_hex",
    "to_id": "d_hex"
})

# Merge
merged = od.merge(
    tt[["o_hex", "d_hex", "travel_time"]],
    on=["o_hex", "d_hex"],
    how="left"
)

# Save
merged.to_csv(OUT_FILE, index=False)

print("✅ Merge complete")
print("Saved to:", OUT_FILE)
print("Rows:", len(merged))
print("Missing travel times:", merged["travel_time"].isna().sum())