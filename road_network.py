# road_network.py

import osmnx as ox

# OSMnx settings
ox.settings.timeout = 300  # increase from default 180 seconds to 300
ox.settings.overpass_url = "https://overpass-api.de/api/interpreter"
ox.settings.max_query_area_size = 50 * 1000 * 1000 * 1000

# Bounding box coordinates for Khopoli - Talegaon Dabhade corridor
north = 18.85
south = 18.65
east = 73.75
west = 73.30

# In OSMnx >= 2.0, bbox requires a tuple formatted as (west, south, east, north)
print("Fetching road network for Khopoli - Talegaon Dabhade corridor...")
G = ox.graph_from_bbox(
    bbox=(west, south, east, north),
    network_type="drive"
)

print(f"Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")
fig, ax = ox.plot_graph(G, node_size=0, edge_linewidth=0.5, figsize=(12, 12))
#ghat_G = ox.graph_from_bbox(
#    bbox=(73.35, 18.72, 73.45, 18.78),  # zoomed into Khandala/Lonavala area
#    network_type="drive"
#)
#fig, ax = ox.plot_graph(ghat_G, node_size=0, edge_linewidth=0.8, figsize=(12, 12))
#ghat_edges = ox.graph_to_gdfs(ghat_G, nodes=False)
#print(ghat_edges['highway'].value_counts())

ox.save_graphml(G, filepath="khopoli_talegaon_raw.graphml")
print("Graph saved successfully")