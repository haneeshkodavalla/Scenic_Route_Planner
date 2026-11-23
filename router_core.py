# router_core.py

import ast
import networkx as nx
import osmnx as ox
import pandas as pd

LOCAL_ROADS = {'residential', 'living_street', 'unclassified'}
LOCAL_PENALTY = 3
REF_SPEED = 15  # m/s

def first_value(v):
    if isinstance(v, str) and v.startswith('['):
        v = ast.literal_eval(v)
    if isinstance(v, list):
        v = v[0]
    return v

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Load everything once, when this file is first imported ----
G = ox.load_graphml(os.path.join(BASE_DIR, "khopoli_talegaon_raw.graphml"))
scores = pd.read_csv(os.path.join(BASE_DIR, "final_scored_segments.csv"), low_memory=False)
for _, row in scores.iterrows():
    G[row['u']][row['v']][row['key']]['scenic_score'] = row['scenic_score']

G = ox.routing.add_edge_speeds(G)
G = ox.routing.add_edge_travel_times(G)

MAX_SCORE = max(d['scenic_score'] for _, _, d in G.edges(data=True))

def edge_cost(d, alpha):
    scenic_penalty = MAX_SCORE / d['scenic_score']
    if first_value(d.get('highway')) in LOCAL_ROADS:
        scenic_penalty *= LOCAL_PENALTY
    scenic_cost = (d['length'] / REF_SPEED) * scenic_penalty
    return alpha * d['travel_time'] + (1 - alpha) * scenic_cost

def get_route(start_lat, start_lon, end_lat, end_lon, alpha):
    start_node = ox.nearest_nodes(G, X=start_lon, Y=start_lat)
    end_node = ox.nearest_nodes(G, X=end_lon, Y=end_lat)

    def weight(u, v, keydict):
        return min(edge_cost(d, alpha) for d in keydict.values())

    nodes = nx.shortest_path(G, start_node, end_node, weight=weight)

    coords, km, minutes, scenic_sum = [], 0, 0, 0
    for a, b in zip(nodes[:-1], nodes[1:]):
        d = min(G.get_edge_data(a, b).values(), key=lambda e: edge_cost(e, alpha))
        if 'geometry' in d:
            coords.extend([lat, lon] for lon, lat in d['geometry'].coords)
        else:
            coords.append([G.nodes[a]['y'], G.nodes[a]['x']])
            coords.append([G.nodes[b]['y'], G.nodes[b]['x']])
        seg_km = d['length'] / 1000
        km += seg_km
        minutes += d['travel_time'] / 60
        scenic_sum += seg_km * d['scenic_score']

    return {
        "route": coords,
        "distance_km": round(km, 1),
        "time_min": round(minutes),
        "scenic_score": round(scenic_sum / km, 3),
    }

# This block only runs when you run this file directly, not when the API imports it
if __name__ == "__main__":
    for alpha in [1, 0.5, 0]:
        r = get_route(18.7833, 73.3667, 18.7333, 73.6833, alpha)
        print(f"alpha={alpha}: {r['distance_km']} km, {r['time_min']} min, "
              f"scenic {r['scenic_score']}, {len(r['route'])} coordinate points")