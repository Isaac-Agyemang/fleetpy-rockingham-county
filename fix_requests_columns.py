import pandas as pd

demand_dir = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7"
in_path  = demand_dir + r"\requests_res7.csv"
out_path = demand_dir + r"\requests_fleetpy.csv"

df = pd.read_csv(in_path)

# required by FleetPy demand module in your version:
# rq_id, rq_time, start, end, nr_pax
rename_map = {
    "origin_node": "start",
    "destination_node": "end",
}
df = df.rename(columns=rename_map)

needed = ["rq_id", "rq_time", "start", "end", "nr_pax"]
missing = [c for c in needed if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns after rename: {missing}. Columns now: {df.columns.tolist()}")

df = df[needed].copy()

# ensure correct dtypes
df["rq_id"] = df["rq_id"].astype(int)
df["rq_time"] = df["rq_time"].astype(float)
df["start"] = df["start"].astype(int)
df["end"] = df["end"].astype(int)
df["nr_pax"] = df["nr_pax"].astype(int)

df.to_csv(out_path, index=False)
print("✅ wrote:", out_path)
print(df.head())