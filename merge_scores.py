# merge_scores.py
from scoring import compute_scenic_score
import osmnx as ox
import pandas as pd

# Load the road network fresh (same as always)
G = ox.load_graphml("khopoli_talegaon_raw.graphml")
edges = ox.graph_to_gdfs(G, nodes=False)
edges_reset = edges.reset_index()  # brings u, v, key out as columns

# Recreate the same segment_id used in NDVI and elevation scripts
# (both were generated in the same row order as this edges GeoDataFrame)
edges_reset['segment_id'] = range(len(edges_reset))

print(f"Base road network loaded: {len(edges_reset)} segments")
print(edges_reset[['u', 'v', 'key', 'segment_id']].head())

ndvi_df = pd.read_csv("ndvi_results.csv")
edges_reset = edges_reset.merge(ndvi_df[['segment_id', 'ndvi_mean']], on='segment_id', how='left')

print(f"After NDVI merge: {len(edges_reset)} rows")
print(f"Missing NDVI values: {edges_reset['ndvi_mean'].isna().sum()}")

# Merge road_quietness (matched by u, v, key)
road_quietness_df = pd.read_csv("road_quietness_results.csv")
edges_reset = edges_reset.merge(road_quietness_df, on=['u', 'v', 'key'], how='left')

print(f"After road_quietness merge: {len(edges_reset)} rows")
print(f"Missing road_quietness values: {edges_reset['road_quietness'].isna().sum()}")


# Merge water_proximity (matched by u, v, key)
water_df = pd.read_csv("water_proximity_results.csv")
edges_reset = edges_reset.merge(water_df, on=['u', 'v', 'key'], how='left')

print(f"After water_proximity merge: {len(edges_reset)} rows")
print(f"Missing water_distance values: {edges_reset['water_distance'].isna().sum()}")

# Merge landuse_bonus (matched by u, v, key)
landuse_df = pd.read_csv("landuse_scoring_results.csv")
edges_reset = edges_reset.merge(landuse_df, on=['u', 'v', 'key'], how='left')

print(f"After landuse merge: {len(edges_reset)} rows")
print(f"Missing landuse_distance values: {edges_reset['landuse_distance'].isna().sum()}")

# Merge elevation_variation (matched by u, v, key)
elevation_df = pd.read_csv("elevation_results.csv")
edges_reset = edges_reset.merge(elevation_df[['u', 'v', 'key', 'elevation_range']], on=['u', 'v', 'key'], how='left')

print(f"After elevation merge: {len(edges_reset)} rows")
print(f"Missing elevation_range values: {edges_reset['elevation_range'].isna().sum()}")

print("\n--- All 5 factors merged, final check ---")
print(edges_reset[['ndvi_mean', 'road_quietness', 'water_distance', 'landuse_distance', 'elevation_range']].describe())

# Merge attractions distance (matched by u, v, key)
attractions_df = pd.read_csv("attractions_results.csv")
edges_reset = edges_reset.merge(attractions_df, on=['u', 'v', 'key'], how='left')

print(f"After attractions merge: {len(edges_reset)} rows")
print(f"Missing attraction_distance values: {edges_reset['attraction_distance'].isna().sum()}")

def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def normalize_inverse(series):
    # For distance-based factors, closer = higher score
    return 1 - normalize(series)

edges_reset['norm_ndvi'] = normalize(edges_reset['ndvi_mean'])
edges_reset['norm_road_quietness'] = edges_reset['road_quietness']  # already 0-1 by design, no need to normalize
edges_reset['norm_water_proximity'] = normalize_inverse(edges_reset['water_distance'])
edges_reset['norm_landuse_bonus'] = normalize_inverse(edges_reset['landuse_distance'])
edges_reset['norm_elevation_variation'] = normalize(edges_reset['elevation_range'])

# Attractions: closer = higher, nothing beyond 2 km (a cutoff, not min-max)
edges_reset['norm_attractions'] = (1 - edges_reset['attraction_distance'] / 2000).clip(lower=0)
print("Segments with an attractions bonus:", (edges_reset['norm_attractions'] > 0).sum())

print("Normalization complete")
print(edges_reset[['norm_ndvi', 'norm_road_quietness', 'norm_water_proximity', 'norm_landuse_bonus', 'norm_elevation_variation']].describe())

edges_reset['scenic_score'] = edges_reset.apply(
    lambda row: compute_scenic_score(
        row['norm_ndvi'],
        row['norm_water_proximity'],
        row['norm_road_quietness'],
        row['norm_elevation_variation'],
        row['norm_landuse_bonus'],
        row['norm_attractions']
    ),
    axis=1
)

print("Scenic score computed for all segments")
print(edges_reset[['highway', 'scenic_score']].describe())
print(edges_reset[['highway', 'scenic_score']].sort_values('scenic_score', ascending=False).head(10))
print(edges_reset[['highway', 'scenic_score']].sort_values('scenic_score', ascending=True).head(10))

edges_reset.to_csv("final_scored_segments.csv", index=False)
print("Saved final scored segments to final_scored_segments.csv")