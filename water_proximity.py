# water_proximity.py

import osmnx as ox
import geopandas as gpd

# Load the road network saved in Phase 2
G = ox.load_graphml("khopoli_talegaon_raw.graphml")
edges = ox.graph_to_gdfs(G, nodes=False)

# Same bounding box as before (west, south, east, north)
north, south, east, west = 18.85, 18.65, 73.75, 73.30

# Pull water features from OSM within your corridor
water_features = ox.features_from_bbox(
    bbox=(west, south, east, north),
    tags={"natural": "water", "waterway": True}
)

print(f"Water features found: {len(water_features)}")

# Reproject both roads and water features to a metric CRS (meters) for accurate distance calculation
edges_projected = edges.to_crs(epsg=32643)
water_projected = water_features.to_crs(epsg=32643)

# Combine all water geometries into one single shape for efficient distance checking
water_union = water_projected.geometry.union_all()

# Compute distance from each road segment to the nearest water feature
edges_projected['water_distance'] = edges_projected.geometry.distance(water_union)

print("Water distance computed")
print(edges_projected[['water_distance']].describe())

# Save just the segment ID and water_distance, so it can be merged later
edges_reset = edges_projected.reset_index()
edges_reset[['u', 'v', 'key', 'water_distance']].to_csv("water_proximity_results.csv", index=False)
print("Saved to water_proximity_results.csv")