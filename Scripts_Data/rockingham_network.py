import osmnx as ox
import geopandas as gpd
from shapely.geometry import MultiPolygon

PLACE = "Rockingham County, North Carolina, USA"
CONDENSE_DEGREE2 = True

NODES_CSV = "rockingham_osmnx_nodes.csv"
EDGES_CSV = "rockingham_osmnx_edges.csv"

# Settings
ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.requests_timeout = 180

# 1) Get boundary and fix geometry
gdf = ox.geocode_to_gdf(PLACE)
poly = gdf.geometry.iloc[0].buffer(0)

if isinstance(poly, MultiPolygon):
    poly = max(poly.geoms, key=lambda p: p.area)

# 2) Download drivable network (original, unsimplified)
G = ox.graph_from_polygon(
    poly,
    network_type="drive",
    simplify=False,
    retain_all=False
)

# 3) Optional degree-2 condensation
if CONDENSE_DEGREE2 and not G.graph.get("simplified", False):
    G = ox.simplify_graph(G)

# 4) Add speeds + travel times
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# 5) Convert to tables
nodes_gdf, edges_gdf = ox.graph_to_gdfs(G, nodes=True, edges=True)

nodes_out = nodes_gdf.reset_index()
edges_out = edges_gdf.reset_index()

# 6) Export CSV
nodes_out[[c for c in ["osmid","x","y"] if c in nodes_out.columns]] \
    .to_csv(NODES_CSV, index=False)

edges_keep = [c for c in [
    "u","v","key",
    "length","speed_kph","travel_time",
    "highway","name","oneway","geometry"
] if c in edges_out.columns]

edges_out["geometry"] = edges_out["geometry"].astype(str)
edges_out[edges_keep].to_csv(EDGES_CSV, index=False)

print("✅ Saved:")
print(" -", NODES_CSV)
print(" -", EDGES_CSV)
print(f"✅ Nodes: {len(nodes_gdf):,} | Edges: {len(edges_gdf):,}")
