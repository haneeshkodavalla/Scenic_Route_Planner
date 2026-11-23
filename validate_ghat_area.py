# validate_ghat_area.py

import pandas as pd
import geopandas as gpd
from shapely import wkt

# Load the final scored data
df = pd.read_csv("final_scored_segments.csv")

# geometry was saved as text in the CSV, convert it back to real geometry
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# Filter to just the Khandala/Lonavala ghat area
ghat_area = gdf.cx[73.35:73.45, 18.72:18.78]

print(f"Segments in ghat area: {len(ghat_area)}")
print(ghat_area[['highway', 'scenic_score']].sort_values('scenic_score', ascending=False).head(15))
print("\n--- Ghat area, motorway vs trunk comparison ---")
print(ghat_area.groupby('highway')['scenic_score'].describe())

print("\n--- Individual factor breakdown: motorway vs trunk ---")
factor_cols = ['norm_ndvi', 'norm_water_proximity', 'norm_road_quietness', 'norm_elevation_variation', 'norm_landuse_bonus']

comparison = ghat_area[ghat_area['highway'].isin(['motorway', 'trunk'])].groupby('highway')[factor_cols].mean()
print(comparison)

print("\n--- Difference (trunk - motorway) per factor ---")
print(comparison.loc['trunk'] - comparison.loc['motorway'])

print("\n--- New attractions factor checks ---")
print("Rows:", len(gdf))
print("Missing scenic_score:", gdf['scenic_score'].isna().sum())
print("Segments with attractions bonus:", (gdf['norm_attractions'] > 0).sum())