import pandas as pd
from pathlib import Path
import h3

INP = Path("data/processed/demand_hex_res7.csv")
OUT = Path("data/processed/hex_zones_res7.csv")

df = pd.read_csv(INP)

# all unique hexes used in origins or destinations
hex_ids = pd.Index(pd.unique(pd.concat([df["o_hex"], df["d_hex"]], ignore_index=True)))

# centroids (lat, lon)
centroids = [h3.cell_to_latlng(h) for h in hex_ids]

zones = pd.DataFrame({
    "zone_id": hex_ids,
    "lat": [c[0] for c in centroids],
    "lon": [c[1] for c in centroids],
})

zones.to_csv(OUT, index=False)

print("✅ Hex centroid table created")
print("Saved to:", OUT)
print("Total zones:", len(zones))