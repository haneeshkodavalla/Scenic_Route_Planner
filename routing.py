# routing.py

import osmnx as ox
import pandas as pd

# Load the road network graph
G = ox.load_graphml("khopoli_talegaon_raw.graphml")

# Load the scored data
scores = pd.read_csv("final_scored_segments.csv")

# Attach each segment's scenic_score onto the matching edge in the graph
for _, row in scores.iterrows():
    G[row['u']][row['v']][row['key']]['scenic_score'] = row['scenic_score']

print("Edges in graph:", len(G.edges))

missing = sum(1 for u, v, k, d in G.edges(keys=True, data=True) if 'scenic_score' not in d)
print("Edges missing scenic_score:", missing)
G = ox.routing.add_edge_speeds(G)
G = ox.routing.add_edge_travel_times(G)
# Highest scenic score in the whole graph (used to build the penalty)
max_score = max(d['scenic_score'] for u, v, k, d in G.edges(keys=True, data=True))

REF_SPEED = 15  # m/s (about 54 km/h), turns scenic cost into "seconds-equivalent"
LOCAL_ROADS = {'residential', 'living_street', 'unclassified'}
LOCAL_PENALTY = 3  # local streets cost 3x more on the scenic side

def set_edge_costs(G, alpha):
    for u, v, k, d in G.edges(keys=True, data=True):
        scenic_penalty = max_score / d['scenic_score']
        if first_value(d.get('highway')) in LOCAL_ROADS:
            scenic_penalty *= LOCAL_PENALTY
        scenic_cost = (d['length'] / REF_SPEED) * scenic_penalty
        d['edge_cost'] = alpha * d['travel_time'] + (1 - alpha) * scenic_cost

import networkx as nx

# Start and end points (lat, lon)
start_point = (18.7833, 73.3667)   # Khopoli
end_point = (18.7333, 73.6833)     # Talegaon Dabhade

# Find the nearest graph node to each point
start_node = ox.nearest_nodes(G, X=start_point[1], Y=start_point[0])
end_node = ox.nearest_nodes(G, X=end_point[1], Y=end_point[0])

import ast
from collections import defaultdict

def first_value(v):
    if isinstance(v, str) and v.startswith('['):
        v = ast.literal_eval(v)
    if isinstance(v, list):
        v = v[0]
    return v

def summarize(G, route):
    km_total, minutes, scenic_sum = 0, 0, 0
    by_type = defaultdict(float)
    for a, b in zip(route[:-1], route[1:]):
        best = min(G.get_edge_data(a, b).values(), key=lambda d: d['edge_cost'])
        km = best['length'] / 1000
        km_total += km
        minutes += best['travel_time'] / 60
        scenic_sum += km * best['scenic_score']
        by_type[first_value(best.get('highway'))] += km
    return km_total, minutes, scenic_sum / km_total, by_type

for alpha in [1, 0.75, 0.5, 0.25, 0]:
    set_edge_costs(G, alpha)
    route = nx.shortest_path(G, start_node, end_node, weight='edge_cost')
    km, mins, avg, by_type = summarize(G, route)
    types = ", ".join(f"{t} {v:.1f}" for t, v in sorted(by_type.items(), key=lambda x: -x[1])[:4])
    print(f"alpha={alpha}: {km:.1f} km, {mins:.0f} min, scenic {avg:.3f} | {types}")

#    routes = []
#for alpha in [1, 0.5, 0]:
#    set_edge_costs(G, alpha)
#    routes.append(nx.shortest_path(G, start_node, end_node, weight='edge_cost'))

#fig, ax = ox.plot_graph_routes(
#    G, routes,
#    route_colors=['blue', 'green', 'red'],
#    route_linewidths=3,
#    node_size=0,
#    figsize=(12, 12)
#)
def top_names(G, route, n=6):
    by_name = defaultdict(float)
    for a, b in zip(route[:-1], route[1:]):
        best = min(G.get_edge_data(a, b).values(), key=lambda d: d['edge_cost'])
        by_name[str(first_value(best.get('name', 'unnamed')))] += best['length'] / 1000
    return sorted(by_name.items(), key=lambda x: -x[1])[:n]

for alpha in [0.5, 0]:
    set_edge_costs(G, alpha)
    route = nx.shortest_path(G, start_node, end_node, weight='edge_cost')
    print(f"\nalpha={alpha} top roads:")
    for name, km in top_names(G, route):
        print(f"  {name}: {km:.1f} km")