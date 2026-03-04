import pandas as pd
from pathlib import Path

INP = Path("data/processed/demand_hex_res7.csv")
OUT = Path("data/processed/od_hex_res7.csv")

df = pd.read_csv(INP)

# Count trips between each origin hex and destination hex
od = df.groupby(["o_hex", "d_hex"]).size().reset_index(name="trips")

od.to_csv(OUT, index=False)

print("✅ OD aggregation complete")
print("Saved to:", OUT)
print("OD pairs:", len(od))
print("Total trips (should match):", od["trips"].sum())