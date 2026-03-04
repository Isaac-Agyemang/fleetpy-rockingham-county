import pandas as pd
from pathlib import Path

# Paths
INP = Path("data/processed/od_with_travel_time_res7.csv")
OUT = Path("data/processed/od_with_time_distance_res7.csv")

# Load
df = pd.read_csv(INP)

# Parameters
AVG_SPEED_MPH = 35

# Compute distance (miles)
df["distance_miles"] = df["travel_time"] * (AVG_SPEED_MPH / 60)

# Optional: round for readability
df["distance_miles"] = df["distance_miles"].round(3)

# Save
df.to_csv(OUT, index=False)

print("✅ Distance column added")
print("Saved to:", OUT)
print(df.head())