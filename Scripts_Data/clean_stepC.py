import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point
from pathlib import Path

INP = Path("data/processed/demand_stepB_bbox.csv")
OUT = Path("data/processed/demand_stepC_in_county.csv")

df = pd.read_csv(INP)

# County boundary polygon
county = ox.geocode_to_gdf("Rockingham County, North Carolina, USA")[["geometry"]].set_crs("EPSG:4326")
county_poly = county.geometry.iloc[0]

# Build GeoDataFrames for origins and destinations
gdf_o = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["OrigY"], df["OrigX"]), crs="EPSG:4326")
gdf_d = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["DestY"], df["DestX"]), crs="EPSG:4326")

# Keep rows where BOTH origin and destination are within the county
o_in = gdf_o.within(county_poly)
d_in = gdf_d.within(county_poly)

dfC = df[o_in & d_in].copy()

dfC.to_csv(OUT, index=False)

print("✅ Step C complete")
print("Rows in:", len(df))
print("Rows out:", len(dfC))
print("Dropped:", len(df) - len(dfC))
print("Saved to:", OUT)