import pandas as pd
from pathlib import Path

# FILE PATHS (Permanent)

RAW_DEMAND = Path("data/raw/rockingham_microtransit_demand.csv")
OUT_DIR = Path("data/processed")

OUT_DIR.mkdir(parents=True, exist_ok=True)


# LOAD DEMAND
df = pd.read_csv(RAW_DEMAND)


# CREATE UNIQUE ORIGINS
origins = (
    df[["Pick-up Latitude", "Pick-up Longitude"]]
    .drop_duplicates()
    .reset_index(drop=True)
    .rename(columns={
        "Pick-up Latitude": "lat",
        "Pick-up Longitude": "lon"
    })
)

origins["origin_id"] = range(1, len(origins) + 1)


# CREATE UNIQUE DESTINATIONS
destinations = (
    df[["Drop-off Latitude", "Drop-off Longitude"]]
    .drop_duplicates()
    .reset_index(drop=True)
    .rename(columns={
        "Drop-off Latitude": "lat",
        "Drop-off Longitude": "lon"
    })
)

destinations["destination_id"] = range(1, len(destinations) + 1)


# MERGE IDs BACK INTO DEMAND

df = df.merge(
    origins,
    left_on=["Pick-up Latitude", "Pick-up Longitude"],
    right_on=["lat", "lon"],
    how="left"
).drop(columns=["lat", "lon"])

df = df.merge(
    destinations,
    left_on=["Drop-off Latitude", "Drop-off Longitude"],
    right_on=["lat", "lon"],
    how="left"
).drop(columns=["lat", "lon"])

# SAVE OUTPUTS

origins.to_csv(OUT_DIR / "origins.csv", index=False)
destinations.to_csv(OUT_DIR / "destinations.csv", index=False)
df.to_csv(OUT_DIR / "demand_od_clean.csv", index=False)

print("✅ Saved:")
print(" - data/processed/origins.csv")
print(" - data/processed/destinations.csv")
print(" - data/processed/demand_od_clean.csv")
