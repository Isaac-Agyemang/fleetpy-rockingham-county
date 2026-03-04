import pandas as pd
import geopandas as gpd
import h3
from shapely.geometry import Polygon, Point, LineString

# =========================
# INPUT / OUTPUT
# =========================
INPUT_CSV = "od_with_travel_time_res7.csv"
OUT_GPKG  = r"D:\PROJECT_RA\fleetpy_rockingham\data\processed\rockingham_res7_qgis.gpkg"

# Column names (confirmed from your screenshot)
ORIGIN_COL = "o_hex"
DEST_COL   = "d_hex"
TRIPS_COL  = "trips"
TT_COL     = "travel_time"

# Keep EVERYTHING (full project / dashboard-ready)
TOP_N_OD_LINES = None     # keep all OD lines
MIN_TRIPS_PER_LINE = 1    # keep all flows >= 1


# 1) LOAD

od = pd.read_csv(INPUT_CSV)

required = {ORIGIN_COL, DEST_COL, TRIPS_COL, TT_COL}
missing = required - set(od.columns)
if missing:
    raise ValueError(f"Missing columns in CSV: {missing}")

od = od[od[TRIPS_COL] >= MIN_TRIPS_PER_LINE].copy()
print(f"✅ OD pairs loaded: {len(od):,}")

# 2) BUILD ZONES + CENTROIDS

zones = sorted(set(od[ORIGIN_COL]).union(set(od[DEST_COL])))
print(f"✅ Unique zones: {len(zones):,}")

zone_polys = []
zone_centroids = []

for h in zones:
    # H3 boundary is (lat, lon); shapely wants (x=lon, y=lat)
    boundary = h3.cell_to_boundary(h)
    poly = Polygon([(lon, lat) for lat, lon in boundary])

    lat, lon = h3.cell_to_latlng(h)
    pt = Point(lon, lat)

    zone_polys.append(poly)
    zone_centroids.append(pt)

gdf_zones = gpd.GeoDataFrame(
    {"zone_id": zones},
    geometry=zone_polys,
    crs="EPSG:4326"
)

gdf_centroids = gpd.GeoDataFrame(
    {"zone_id": zones},
    geometry=zone_centroids,
    crs="EPSG:4326"
)

# Zone totals for choropleth styling
orig_tot = od.groupby(ORIGIN_COL)[TRIPS_COL].sum().rename("orig_trips")
dest_tot = od.groupby(DEST_COL)[TRIPS_COL].sum().rename("dest_trips")

gdf_zones = gdf_zones.merge(orig_tot, left_on="zone_id", right_index=True, how="left")
gdf_zones = gdf_zones.merge(dest_tot, left_on="zone_id", right_index=True, how="left")
gdf_zones[["orig_trips", "dest_trips"]] = gdf_zones[["orig_trips", "dest_trips"]].fillna(0).astype(int)
gdf_zones["total_trips"] = gdf_zones["orig_trips"] + gdf_zones["dest_trips"]


# 3) BUILD OD LINES
centroid_lookup = dict(zip(gdf_centroids["zone_id"], gdf_centroids.geometry))

lines = []
orig_list = []
dest_list = []
trip_list = []
tt_list = []

for _, r in od.iterrows():
    o = r[ORIGIN_COL]
    d = r[DEST_COL]

    if o not in centroid_lookup or d not in centroid_lookup:
        continue

    p1 = centroid_lookup[o]
    p2 = centroid_lookup[d]

    lines.append(LineString([p1, p2]))
    orig_list.append(o)
    dest_list.append(d)
    trip_list.append(int(r[TRIPS_COL]))
    tt_list.append(float(r[TT_COL]))

gdf_lines = gpd.GeoDataFrame(
    {
        "origin": orig_list,
        "destination": dest_list,
        "trips": trip_list,
        "travel_time": tt_list
    },
    geometry=lines,
    crs="EPSG:4326"
)

# Keep all lines (since TOP_N_OD_LINES=None)
if TOP_N_OD_LINES is not None and len(gdf_lines) > TOP_N_OD_LINES:
    gdf_lines = gdf_lines.sort_values("trips", ascending=False).head(TOP_N_OD_LINES).copy()

print(f"✅ OD lines created: {len(gdf_lines):,}")

# =========================
# 4) EXPORT ONE GPKG (QGIS-ready)
# =========================
gdf_zones.to_file(OUT_GPKG, layer="zones", driver="GPKG")
gdf_centroids.to_file(OUT_GPKG, layer="centroids", driver="GPKG")
gdf_lines.to_file(OUT_GPKG, layer="od_lines", driver="GPKG")

print(f"✅ Saved GeoPackage: {OUT_GPKG}")
print("Layers inside:", ["zones", "centroids", "od_lines"])