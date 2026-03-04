# r5_travel_time.py

import os
os.environ["R5PY_USE_SYMLINKS"] = "0"

import r5py
import geopandas as gpd
import pandas as pd
import datetime
from pathlib import Path

# -----------------------------
# PATHS
# -----------------------------
OSM_PBF = r"data/OSM/rockingham.osm.pbf"
GTFS_FILES = [
    r"data/GTFS/part_gtfs.zip",
    r"data/GTFS/skat_gtfs.zip"
]

ORIGINS_FILE = Path("data/processed/origins.csv")
DESTINATIONS_FILE = Path("data/processed/destinations.csv")

OUTPUT_DIR = Path("network_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------------
# BUILD TRANSPORT NETWORK
# -----------------------------
print("Building R5 transport network...")
transport_network = r5py.TransportNetwork(
    osm_pbf=OSM_PBF,
    gtfs=GTFS_FILES
)
print("✅ Transport network built")

# -----------------------------
# LOAD ORIGINS & DESTINATIONS
# -----------------------------
orig_df = pd.read_csv(ORIGINS_FILE)
dest_df = pd.read_csv(DESTINATIONS_FILE)

# r5py REQUIRES column name 'id'
orig_df["id"] = orig_df["origin_id"]
dest_df["id"] = dest_df["destination_id"]

origins = gpd.GeoDataFrame(
    orig_df,
    geometry=gpd.points_from_xy(orig_df.lon, orig_df.lat),
    crs="EPSG:4326"
)

destinations = gpd.GeoDataFrame(
    dest_df,
    geometry=gpd.points_from_xy(dest_df.lon, dest_df.lat),
    crs="EPSG:4326"
)

# -----------------------------
# SET DEPARTURE TIME
# (placeholder for now)
# -----------------------------
departure_time = datetime.datetime(2024, 1, 1, 8, 0)

# -----------------------------
# CAR MATRIX
# -----------------------------
print("Computing CAR matrix...")
ttm_car = r5py.TravelTimeMatrix(
    transport_network,
    origins=origins,
    destinations=destinations,
    departure=departure_time,
    transport_modes=[r5py.TransportMode.CAR],
)

ttm_car.transport_network = transport_network
car_matrix = ttm_car._compute()

# Rename columns back to origin_id / destination_id
car_matrix = car_matrix.rename(columns={
    "from_id": "origin_id",
    "to_id": "destination_id"
})

car_matrix.to_csv(OUTPUT_DIR / "ttm_car.csv", index=False)
print("✅ Saved CAR matrix")

# -----------------------------
# TRANSIT MATRIX
# -----------------------------
print("Computing TRANSIT matrix...")
ttm_transit = r5py.TravelTimeMatrix(
    transport_network,
    origins=origins,
    destinations=destinations,
    departure=departure_time,
    transport_modes=[
        r5py.TransportMode.WALK,
        r5py.TransportMode.TRANSIT
    ],
)

ttm_transit.transport_network = transport_network
transit_matrix = ttm_transit._compute()

transit_matrix = transit_matrix.rename(columns={
    "from_id": "origin_id",
    "to_id": "destination_id"
})

transit_matrix.to_csv(OUTPUT_DIR / "ttm_transit.csv", index=False)
print("✅ Saved TRANSIT matrix")

print("All matrices computed successfully.")
