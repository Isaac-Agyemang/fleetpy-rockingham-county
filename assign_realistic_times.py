import numpy as np
import pandas as pd

# INPUT FILE
infile = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\requests_res7_clean.csv"

# OUTPUT FILE
outfile = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\requests_res7_realistic.csv"

df = pd.read_csv(infile)

print("Original rows:", len(df))

# remove invalid trips
df = df[df["start"] != df["end"]].copy()

# ----- realistic demand distribution -----

rng = np.random.default_rng(42)

n = len(df)

# mixture weights
weights = [0.05, 0.35, 0.30, 0.30]

# means in seconds from 6am
means = [
    1800,   # 6:30 AM
    7200,   # 8:00 AM
    21600,  # 12:00 PM
    36000   # 4:00 PM
]

std = [
    1200,
    2400,
    3600,
    2400
]

choices = rng.choice(len(weights), size=n, p=weights)

times = np.zeros(n)

for i in range(len(weights)):
    idx = choices == i
    times[idx] = rng.normal(means[i], std[i], idx.sum())

times = np.clip(times, 0, 39600)

df["rq_time"] = times.astype(int)

# sort
df = df.sort_values("rq_time").reset_index(drop=True)

# reassign IDs starting from 0
df["request_id"] = range(len(df))

# keep only FleetPy columns
df = df[["rq_time", "start", "end", "request_id"]]

df.to_csv(outfile, index=False)

print("Saved:", outfile)
print("Rows:", len(df))
print("Min rq_time:", df["rq_time"].min())
print("Max rq_time:", df["rq_time"].max())