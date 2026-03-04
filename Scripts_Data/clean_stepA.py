import pandas as pd
from pathlib import Path

# Paths adjusted to your folder structure
RAW = Path("data/raw/FY24_Geocode_FINAL_Rockingham for NCAT.xlsx")
OUT = Path("data/processed/demand_stepA_nonnull_nonzero.csv")

# Load
df = pd.read_excel(RAW)

coord_cols = ["OrigX", "OrigY", "DestX", "DestY"]

# Drop nulls
df0 = df.dropna(subset=coord_cols).copy()

# Drop zero coordinates
dfA = df0[
    (df0["OrigX"] != 0) & (df0["OrigY"] != 0) &
    (df0["DestX"] != 0) & (df0["DestY"] != 0)
].copy()

# Save
dfA.to_csv(OUT, index=False)

print("✅ Step A complete")
print("Rows before:", len(df))
print("After dropna:", len(df0))
print("After nonzero:", len(dfA))
print("Saved to:", OUT)