import pandas as pd
from pathlib import Path

INP = Path("data/processed/demand_stepA_nonnull_nonzero.csv")
OUT = Path("data/processed/demand_stepB_bbox.csv")

df = pd.read_csv(INP)

# Rockingham-ish bounding box (keeps only reasonable local points)
LAT_MIN, LAT_MAX = 35.9, 36.7
LON_MIN, LON_MAX = -80.3, -79.3

dfB = df[
    df["OrigX"].between(LAT_MIN, LAT_MAX) &
    df["OrigY"].between(LON_MIN, LON_MAX) &
    df["DestX"].between(LAT_MIN, LAT_MAX) &
    df["DestY"].between(LON_MIN, LON_MAX)
].copy()

dfB.to_csv(OUT, index=False)

print("✅ Step B complete")
print("Rows in:", len(df))
print("Rows out:", len(dfB))
print("Dropped:", len(df) - len(dfB))
print("Saved to:", OUT)