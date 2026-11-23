# landuse_scoring.py

import osmnx as ox
import geopandas as gpd

# Load the road network saved in Phase 2
G = ox.load_graphml("khopoli_talegaon_raw.graphml")
edges = ox.graph_to_gdfs(G, nodes=False)

# Same bounding box as before
north, south, east, west = 18.85, 18.65, 73.75, 73.30

# Pull landuse features from OSM within your corridor
landuse_features = ox.features_from_bbox(
    bbox=(west, south, east, north),
    tags={"landuse": ["forest", "farmland", "meadow", "orchard"], "natural": ["wood", "scrub"], "leisure": "park"}
)

print(f"Landuse features found: {len(landuse_features)}")

# Reproject both roads and landuse features to a metric CRS (meters)
edges_projected = edges.to_crs(epsg=32643)
landuse_projected = landuse_features.to_crs(epsg=32643)

# Combine all landuse geometries into one shape for efficient distance checking
landuse_union = landuse_projected.geometry.union_all()

# Compute distance from each road segment to the nearest landuse feature
edges_projected['landuse_distance'] = edges_projected.geometry.distance(landuse_union)

print("Landuse distance computed")
print(edges_projected[['landuse_distance']].describe())


# Save just the segment ID and landuse_distance, so it can be merged later
edges_reset = edges_projected.reset_index()
edges_reset[['u', 'v', 'key', 'landuse_distance']].to_csv("landuse_scoring_results.csv", index=False)
print("Saved to landuse_scoring_results.csv")