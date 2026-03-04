import pandas as pd

# INPUT FILE (your original demand)
infile = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\_old_requests\requests_res7.csv"

# OUTPUT FILE (where FleetPy expects it)
outfile = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\requests_res7_clean.csv"

df = pd.read_csv(infile)

print("Original rows:", len(df))

# remove trips where start == end
df = df[df["start"] != df["end"]].copy()

# sort requests
df = df.sort_values(["rq_time", "request_id"]).reset_index(drop=True)

# recreate request ids sequentially
df["request_id"] = range(1, len(df)+1)

df.to_csv(outfile, index=False)

print("Clean rows:", len(df))
print("Saved to:", outfile)