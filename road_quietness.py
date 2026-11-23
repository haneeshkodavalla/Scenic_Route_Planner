# road_quietness.py

import osmnx as ox
from config import road_type_scores

# Load the road network saved in Phase 2
G = ox.load_graphml("khopoli_talegaon_raw.graphml")
edges = ox.graph_to_gdfs(G, nodes=False)

def get_road_quietness(highway_tag):
    if isinstance(highway_tag, list):
        highway_tag = highway_tag[0]
    return road_type_scores.get(highway_tag, 0.5)

edges['road_quietness'] = edges['highway'].apply(get_road_quietness)

print("Road quietness scores computed")
print(edges[['highway', 'road_quietness']].head(10))
print(edges['road_quietness'].value_counts())

# Save just the segment ID and road_quietness score, so it can be merged later
edges_reset = edges.reset_index()  # osmid/u/v/key become columns instead of index
edges_reset[['u', 'v', 'key', 'road_quietness']].to_csv("road_quietness_results.csv", index=False)
print("Saved to road_quietness_results.csv")