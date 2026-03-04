import pandas as pd
from pathlib import Path
import h3

INP = Path("data/processed/demand_stepC_in_county.csv")
OUT = Path("data/processed/demand_hex_res7.csv")

df = pd.read_csv(INP)

RES = 7  # recommended for Rockingham County

# Assign hex IDs
df["o_hex"] = df.apply(lambda r: h3.latlng_to_cell(r["OrigX"], r["OrigY"], RES), axis=1)
df["d_hex"] = df.apply(lambda r: h3.latlng_to_cell(r["DestX"], r["DestY"], RES), axis=1)

df.to_csv(OUT, index=False)

print("✅ Hex assignment complete")
print("Saved to:", OUT)
print("Unique origin hexes:", df["o_hex"].nunique())
print("Unique destination hexes:", df["d_hex"].nunique())
print("Total rows:", len(df))