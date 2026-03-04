import os
os.environ["R5PY_USE_SYMLINKS"] = "0"  # Windows fix

import r5py
import geopandas as gpd
import pandas as pd
import datetime
from shapely.geometry import Point

# Paths
osm_pbf = r"data/OSM/rockingham.osm.pbf"
gtfs_files = [r"data/GTFS/part_gtfs.zip", r"data/GTFS/skat_gtfs.zip"]

zones_csv = r"data/processed/hex_zones_res7.csv"
out_csv = r"data/processed/travel_time_matrix_hex_res7_car.csv"

# Build transport network
transport_network = r5py.TransportNetwork(osm_pbf=osm_pbf, gtfs=gtfs_files)
print("✅ Transport network built")

# Load zones and convert to GeoDataFrame
zones = pd.read_csv(zones_csv)

zones_gdf = gpd.GeoDataFrame(
    zones,
    geometry=gpd.points_from_xy(zones["lon"], zones["lat"]),
    crs="EPSG:4326"
)

origins = zones_gdf[["zone_id", "geometry"]].rename(columns={"zone_id": "id"})
destinations = origins.copy()

# Travel time matrix
ttm = r5py.TravelTimeMatrix(
    transport_network,
    origins=origins,
    destinations=destinations,
    departure=datetime.datetime(2024, 1, 1, 8, 0),
    transport_modes=[r5py.TransportMode.CAR],
)

# Fix for your r5py version
ttm.transport_network = transport_network

matrix = ttm._compute()  # returns from_id, to_id, travel_time

matrix.to_csv(out_csv, index=False)
print("✅ Saved:", out_csv)
print(matrix.head())