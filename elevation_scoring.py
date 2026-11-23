# elevation_scoring.py

import ee
import osmnx as ox
import pandas as pd
import os
import time

ee.Authenticate()
ee.Initialize(project='haneesh-gee-1')

# Load the road network saved in Phase 2
G = ox.load_graphml("khopoli_talegaon_raw.graphml")
edges = ox.graph_to_gdfs(G, nodes=False)

# Load SRTM elevation data (30m resolution, covers this region well)
dem = ee.Image('USGS/SRTMGL1_003')

print("DEM loaded successfully")

import geopandas as gpd

# Reproject and buffer all road segments by 50m (same as NDVI)
edges_projected = edges.to_crs(epsg=32643)
edges_projected['buffered_geom'] = edges_projected.geometry.buffer(50)

buffered_all = gpd.GeoDataFrame(
    geometry=edges_projected['buffered_geom'],
    crs=32643
).to_crs(epsg=4326)

# Use u, v, key as identifiers (same approach as road_quietness/water_proximity)
edges_reset = edges_projected.reset_index()
buffered_all['u'] = edges_reset['u'].values
buffered_all['v'] = edges_reset['v'].values
buffered_all['key'] = edges_reset['key'].values
buffered_all['segment_id'] = range(len(buffered_all))

print(f"Buffered {len(buffered_all)} segments successfully")

chunk_size = 500
output_file = "elevation_results.csv"
total_chunks = (len(buffered_all) // chunk_size) + 1

# Check how many chunks are already done (resume capability)
if os.path.exists(output_file):
    existing_df = pd.read_csv(output_file)
    done_segment_ids = set(existing_df['segment_id'])
    print(f"Resuming — {len(done_segment_ids)} segments already saved")
else:
    done_segment_ids = set()

for i in range(0, len(buffered_all), chunk_size):
    chunk = buffered_all.iloc[i:i + chunk_size]
    chunk_num = i // chunk_size + 1

    if set(chunk['segment_id']).issubset(done_segment_ids):
        print(f"Skipping chunk {chunk_num} of {total_chunks} (already done)")
        continue

    features = [
        ee.Feature(
            ee.Geometry(row.geometry.__geo_interface__),
            {'segment_id': row['segment_id'], 'u': row['u'], 'v': row['v'], 'key': row['key']}
        )
        for _, row in chunk.iterrows()
    ]
    fc = ee.FeatureCollection(features)

    # Compute both min and max elevation within each buffer, in one batch call
    result = dem.reduceRegions(
        collection=fc,
        reducer=ee.Reducer.minMax(),
        scale=30  # SRTM resolution is 30m per pixel
    )

    chunk_results = result.getInfo()['features']

    chunk_records = []
    for feature in chunk_results:
        props = feature['properties']
        elev_min = props.get('min')
        elev_max = props.get('max')
        elevation_range = (elev_max - elev_min) if (elev_min is not None and elev_max is not None) else None
        chunk_records.append({
            'segment_id': props['segment_id'],
            'u': props['u'],
            'v': props['v'],
            'key': props['key'],
            'elevation_range': elevation_range
        })
    chunk_df = pd.DataFrame(chunk_records)

    write_header = not os.path.exists(output_file)
    chunk_df.to_csv(output_file, mode='a', header=write_header, index=False)

    print(f"Processed and saved chunk {chunk_num} of {total_chunks}")
    time.sleep(1)

print("Finished processing all segments")

print("--- Testing minMax reducer property names ---")

final_check = pd.read_csv("elevation_results.csv")
print(f"Total rows: {len(final_check)}")
print(f"Non-null elevation_range count: {final_check['elevation_range'].notna().sum()}")
print(final_check.head())
print(final_check['elevation_range'].describe())