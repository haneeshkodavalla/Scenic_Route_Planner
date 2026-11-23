# attractions_distance.py

import pandas as pd
import osmnx as ox

# Load the attractions saved earlier (no new download needed)
attractions = pd.read_pickle("attractions_raw.pkl")

# Keep named places only, and drop things that are not attractions
named = attractions[attractions['name'].notna()].copy()
if 'waterway' in named.columns:
    named = named[named['waterway'] != 'dam']
if 'natural' in named.columns:
    named = named[named['natural'] != 'water']
print(f"Attractions used: {len(named)} (from {len(attractions)})")

# Load the road network
G = ox.load_graphml("khopoli_talegaon_raw.graphml")
edges = ox.graph_to_gdfs(G, nodes=False)

# Reproject to meters so distances are real-world distances
edges_projected = edges.to_crs(epsg=32643)
attractions_projected = named.to_crs(epsg=32643)

# Merge all attractions into one shape, then measure from every road segment
attractions_union = attractions_projected.geometry.union_all()
edges_projected['attraction_distance'] = edges_projected.geometry.distance(attractions_union)

print(edges_projected['attraction_distance'].describe())
for limit in [500, 1000, 2000, 3000]:
    count = (edges_projected['attraction_distance'] <= limit).sum()
    print(f"Segments within {limit} m of an attraction: {count} of {len(edges_projected)}")

# Save for merging later
edges_reset = edges_projected.reset_index()
edges_reset[['u', 'v', 'key', 'attraction_distance']].to_csv("attractions_results.csv", index=False)
print("Saved to attractions_results.csv")