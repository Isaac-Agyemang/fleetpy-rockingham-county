import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, LineString
import h3

# -------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------
hex_file = r"D:\PROJECT_RA\fleetpy_rockingham\data\processed\hex_zones_res7.csv"
od_file = r"D:\PROJECT_RA\fleetpy_rockingham\data\processed\od_hex_res7.csv"

requests_file = r"D:\PROJECT_RA\FleetPy\data\demand\skat_fy24_res7\matched\rockingham_res7\requests.csv"
user_stats_file = r"D:\PROJECT_RA\FleetPy\studies\rockingham_study\results\rockingham_res7\1_user-stats.csv"

output_file = r"D:\PROJECT_RA\FleetPy\studies\rockingham_study\results\rockingham_res7\rockingham_analysis.gpkg"

# -------------------------------------------------------
# HELPERS: H3 API COMPAT (works for old + new python-h3)
# -------------------------------------------------------
def h3_boundary_latlon(h):
    """Return list of (lat, lon) tuples for the hex boundary."""
    if hasattr(h3, "cell_to_boundary"):
        # Newer h3 API
        return list(h3.cell_to_boundary(h))
    # Older h3 API
    return list(h3.h3_to_geo_boundary(h, geo_json=True))

def h3_center_latlon(h):
    """Return (lat, lon) center for the hex."""
    if hasattr(h3, "cell_to_latlng"):
        # Newer h3 API
        return h3.cell_to_latlng(h)
    # Older h3 API
    return h3.h3_to_geo(h)

def h3_to_polygon_lonlat(h):
    # shapely needs (lon, lat)
    boundary = h3_boundary_latlon(h)  # (lat, lon)
    return Polygon([(lon, lat) for lat, lon in boundary])

# -------------------------------------------------------
# BUILD HEX GEOMETRY (zone_id column)
# -------------------------------------------------------
hex_df = pd.read_csv(hex_file)

# your columns are: zone_id, lat, lon
if "zone_id" not in hex_df.columns:
    raise ValueError(f"Expected 'zone_id' in hex file. Found columns: {list(hex_df.columns)}")

hex_df["geometry"] = hex_df["zone_id"].apply(h3_to_polygon_lonlat)
hex_gdf = gpd.GeoDataFrame(hex_df, geometry="geometry", crs="EPSG:4326")

# -------------------------------------------------------
# REQUEST DEMAND (start/end are zone ids)
# -------------------------------------------------------
req = pd.read_csv(requests_file)

if "start" not in req.columns or "end" not in req.columns:
    raise ValueError(f"Expected 'start' and 'end' in requests file. Found columns: {list(req.columns)}")

origin = req.groupby("start").size().reset_index(name="origin_trips")
dest = req.groupby("end").size().reset_index(name="dest_trips")

hex_gdf = hex_gdf.merge(origin, left_on="zone_id", right_on="start", how="left")
hex_gdf = hex_gdf.merge(dest, left_on="zone_id", right_on="end", how="left")

hex_gdf["origin_trips"] = hex_gdf["origin_trips"].fillna(0).astype(int)
hex_gdf["dest_trips"] = hex_gdf["dest_trips"].fillna(0).astype(int)

# -------------------------------------------------------
# SERVED / MISSED / SERVICE RATE
# -------------------------------------------------------
users = pd.read_csv(user_stats_file)

if "dropoff_time" not in users.columns:
    raise ValueError(f"'dropoff_time' not found in {user_stats_file}. Columns: {list(users.columns)}")

if "start" not in users.columns:
    raise ValueError(f"'start' not found in {user_stats_file}. Columns: {list(users.columns)}")

served = users[users["dropoff_time"].notna()]
served_hex = served.groupby("start").size().reset_index(name="served_trips")

hex_gdf = hex_gdf.merge(served_hex, left_on="zone_id", right_on="start", how="left")
hex_gdf["served_trips"] = hex_gdf["served_trips"].fillna(0).astype(int)

hex_gdf["missed_trips"] = (hex_gdf["origin_trips"] - hex_gdf["served_trips"]).clip(lower=0)

hex_gdf["service_rate"] = 0.0
mask = hex_gdf["origin_trips"] > 0
hex_gdf.loc[mask, "service_rate"] = (
    hex_gdf.loc[mask, "served_trips"] / hex_gdf.loc[mask, "origin_trips"]
)

# -------------------------------------------------------
# OD FLOW LINES
# -------------------------------------------------------
od = pd.read_csv(od_file)

needed = {"origin", "destination", "trips"}
missing = needed - set(od.columns)
if missing:
    raise ValueError(f"od file missing columns {missing}. Found: {list(od.columns)}")

flow_lines = []
for _, r in od.iterrows():
    o_hex = r["origin"]
    d_hex = r["destination"]

    o_lat, o_lon = h3_center_latlon(o_hex)
    d_lat, d_lon = h3_center_latlon(d_hex)

    flow_lines.append(
        {
            "origin": o_hex,
            "destination": d_hex,
            "trips": r["trips"],
            "geometry": LineString([(o_lon, o_lat), (d_lon, d_lat)]),
        }
    )

flows_gdf = gpd.GeoDataFrame(flow_lines, geometry="geometry", crs="EPSG:4326")

# -------------------------------------------------------
# SAVE (GeoPackage)
# -------------------------------------------------------
hex_gdf.to_file(output_file, layer="hex_zones", driver="GPKG")
flows_gdf.to_file(output_file, layer="od_flows", driver="GPKG")

print("✅ Created:", output_file)