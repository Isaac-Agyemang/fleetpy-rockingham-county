import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, LineString
import h3

# -------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------
lookup_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\fleetpy_zone_lookup_res7.csv"

requests_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\requests.csv"
user_stats_file = r"D:\PROJECT_RA\FleetPy\studies\rockingham_study\results\rockingham_res7\1_user-stats.csv"

od_file = r"D:\PROJECT_RA\fleetpy_rockingham\data\processed\od_hex_res7.csv"

output_file = r"D:\PROJECT_RA\FleetPy\studies\rockingham_study\results\rockingham_res7\rockingham_analysis.gpkg"

# -------------------------------------------------------
# H3 API COMPAT
# -------------------------------------------------------
def h3_boundary_latlon(h):
    if hasattr(h3, "cell_to_boundary"):
        return list(h3.cell_to_boundary(h))  # (lat, lon)
    return list(h3.h3_to_geo_boundary(h, geo_json=True))  # (lat, lon)

def h3_center_latlon(h):
    if hasattr(h3, "cell_to_latlng"):
        return h3.cell_to_latlng(h)
    return h3.h3_to_geo(h)

def h3_to_polygon_lonlat(h):
    boundary = h3_boundary_latlon(h)  # (lat, lon)
    return Polygon([(lon, lat) for lat, lon in boundary])  # shapely wants (lon, lat)

# -------------------------------------------------------
# ZONE LOOKUP (authoritative mapping)
# zone_int (1..163) -> zone_id (H3)
# -------------------------------------------------------
lk = pd.read_csv(lookup_file)

needed = {"zone_int", "zone_id"}
missing = needed - set(lk.columns)
if missing:
    raise ValueError(f"lookup file missing columns {missing}. Found: {list(lk.columns)}")

lk["zone_int"] = pd.to_numeric(lk["zone_int"], errors="coerce").astype("Int64")
lk["zone_id"] = lk["zone_id"].astype(str)

# Build hex geometry from H3
lk["geometry"] = lk["zone_id"].apply(h3_to_polygon_lonlat)
hex_gdf = gpd.GeoDataFrame(lk, geometry="geometry", crs="EPSG:4326")

# -------------------------------------------------------
# REQUEST DEMAND (requests start/end are zone_int)
# -------------------------------------------------------
req = pd.read_csv(requests_file)

if "start" not in req.columns or "end" not in req.columns:
    raise ValueError(f"Expected 'start' and 'end' in requests file. Found columns: {list(req.columns)}")

req["start"] = pd.to_numeric(req["start"], errors="coerce").astype("Int64")
req["end"] = pd.to_numeric(req["end"], errors="coerce").astype("Int64")

origin = req.groupby("start").size().reset_index(name="origin_trips")
dest = req.groupby("end").size().reset_index(name="dest_trips")

hex_gdf = hex_gdf.merge(origin, left_on="zone_int", right_on="start", how="left")
hex_gdf = hex_gdf.merge(dest, left_on="zone_int", right_on="end", how="left")

hex_gdf["origin_trips"] = hex_gdf["origin_trips"].fillna(0).astype(int)
hex_gdf["dest_trips"] = hex_gdf["dest_trips"].fillna(0).astype(int)

# -------------------------------------------------------
# SERVED / MISSED / SERVICE RATE (user-stats start is also zone_int)
# -------------------------------------------------------
users = pd.read_csv(user_stats_file)

if "dropoff_time" not in users.columns:
    raise ValueError(f"'dropoff_time' not found in {user_stats_file}. Columns: {list(users.columns)}")
if "start" not in users.columns:
    raise ValueError(f"'start' not found in {user_stats_file}. Columns: {list(users.columns)}")

users["start"] = pd.to_numeric(users["start"], errors="coerce").astype("Int64")

served = users[users["dropoff_time"].notna()]
served_hex = served.groupby("start").size().reset_index(name="served_trips")

hex_gdf = hex_gdf.merge(served_hex, left_on="zone_int", right_on="start", how="left")
hex_gdf["served_trips"] = hex_gdf["served_trips"].fillna(0).astype(int)

hex_gdf["missed_trips"] = (hex_gdf["origin_trips"] - hex_gdf["served_trips"]).clip(lower=0)

hex_gdf["service_rate"] = 0.0
mask = hex_gdf["origin_trips"] > 0
hex_gdf.loc[mask, "service_rate"] = hex_gdf.loc[mask, "served_trips"] / hex_gdf.loc[mask, "origin_trips"]

# -------------------------------------------------------
# OD FLOW LINES (your OD file uses H3: o_hex/d_hex)
# -------------------------------------------------------
od = pd.read_csv(od_file)

if {"o_hex", "d_hex", "trips"}.issubset(od.columns):
    o_col, d_col = "o_hex", "d_hex"
elif {"origin", "destination", "trips"}.issubset(od.columns):
    o_col, d_col = "origin", "destination"
else:
    raise ValueError(
        "od file must have either (o_hex, d_hex, trips) or (origin, destination, trips). "
        f"Found: {list(od.columns)}"
    )

od[o_col] = od[o_col].astype(str)
od[d_col] = od[d_col].astype(str)

flow_lines = []
for _, r in od.iterrows():
    o_hex = r[o_col]
    d_hex = r[d_col]

    o_lat, o_lon = h3_center_latlon(o_hex)
    d_lat, d_lon = h3_center_latlon(d_hex)

    flow_lines.append({
        "origin": o_hex,
        "destination": d_hex,
        "trips": r["trips"],
        "geometry": LineString([(o_lon, o_lat), (d_lon, d_lat)])
    })

flows_gdf = gpd.GeoDataFrame(flow_lines, geometry="geometry", crs="EPSG:4326")

# -------------------------------------------------------
# SAVE
# -------------------------------------------------------
hex_gdf.to_file(output_file, layer="hex_zones", driver="GPKG")
flows_gdf.to_file(output_file, layer="od_flows", driver="GPKG")

print("✅ Created:", output_file)
print("✅ Now hex_zones should have non-zero origin_trips / served_trips where demand exists.")