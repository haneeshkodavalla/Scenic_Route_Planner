# ndvi_scoring.py

import ee

ee.Authenticate()
ee.Initialize(project='haneesh-gee-1')

# Define your area of interest (same bounding box as your road network)
aoi = ee.Geometry.Rectangle([73.30, 18.65, 73.75, 18.85])  # west, south, east, north

# Pull a Sentinel-2 image collection, filtered to your area, date range, and low cloud cover
collection = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate('2024-01-01', '2024-03-31')  # dry season, less cloud cover
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
)

print("Number of images found:", collection.size().getInfo())
# Create a cloud-free composite by taking the median across all matching images
composite = collection.median().clip(aoi)

print("Composite created successfully")
# Compute NDVI using Sentinel-2's NIR (B8) and Red (B4) bands
ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI')

print("NDVI band created successfully")



import osmnx as ox

# Load the road network saved in Phase 2
G = ox.load_graphml("khopoli_talegaon_raw.graphml")

# Convert to a GeoDataFrame of edges (road segments)
edges = ox.graph_to_gdfs(G, nodes=False)

print(f"Total road segments: {len(edges)}")
print(edges.iloc[0])


# Pick just the first road segment as a test
#test_segment = edges.iloc[0]

# Reproject to a metric CRS (meters) so we can buffer in real-world distance
#
#edges_projected = edges.to_crs(epsg=32643)  # UTM zone 43N, covers Maharashtra
#test_geom_projected = edges_projected.iloc[0].geometry

# Buffer the road segment by 50 meters
#buffered = test_geom_projected.buffer(50)

# Convert back to lat/lon (EPSG:4326) since Earth Engine expects that
import geopandas as gpd
import pandas as pd
#buffered_gdf = gpd.GeoSeries([buffered], crs=32643).to_crs(epsg=4326)
#buffered_geom = buffered_gdf.iloc[0]

#print("Buffer created successfully")
#print(buffered_geom)

# Convert the buffer polygon into an Earth Engine geometry
#ee_buffer = ee.Geometry(buffered_geom.__geo_interface__)

# Compute average NDVI within this buffer
#mean_ndvi = ndvi.reduceRegion(
#    reducer=ee.Reducer.mean(),
#    geometry=ee_buffer,
#    scale=10  # Sentinel-2 resolution is 10m per pixel
#).get('NDVI')

#print("Average NDVI for this segment:", mean_ndvi.getInfo())


# Reproject all edges to metric CRS and buffer all of them by 50m
edges_projected = edges.to_crs(epsg=32643)
edges_projected['buffered_geom'] = edges_projected.geometry.buffer(50)

# Create a buffered GeoDataFrame, reprojected back to lat/lon for Earth Engine
buffered_all = gpd.GeoDataFrame(
    geometry=edges_projected['buffered_geom'],
    crs=32643
).to_crs(epsg=4326)

# Give each segment a simple numeric ID so we can match results back later
buffered_all['segment_id'] = range(len(buffered_all))

print(f"Buffered {len(buffered_all)} segments successfully")
print(buffered_all.head())

import time

#chunk_size = 500
#all_results = []

#total_chunks = (len(buffered_all) // chunk_size) + 1

#for i in range(0, len(buffered_all), chunk_size):
#    chunk = buffered_all.iloc[i:i + chunk_size]

    # Build FeatureCollection for just this chunk
#    features = [
#        ee.Feature(ee.Geometry(row.geometry.__geo_interface__), {'segment_id': row['segment_id']})
#        for _, row in chunk.iterrows()
#    ]
#    fc = ee.FeatureCollection(features)

    # Compute mean NDVI for every feature in this chunk, in one batch call
#    result = ndvi.reduceRegions(
#        collection=fc,
#        reducer=ee.Reducer.mean(),
#        scale=10
#    )

#    chunk_results = result.getInfo()['features']
#    all_results.extend(chunk_results)

#    print(f"Processed chunk {i // chunk_size + 1} of {total_chunks}")
#    time.sleep(1)  # small pause to avoid overwhelming the server

#print(f"Finished processing all {len(all_results)} segments")

# Extract segment_id and NDVI value from each result
#ndvi_records = []
#for feature in all_results:
#    props = feature['properties']
#    ndvi_records.append({
#        'segment_id': props['segment_id'],
#        'ndvi_mean': props.get('NDVI')
#    })

#ndvi_df = pd.DataFrame(ndvi_records)

# Save to CSV so we never have to re-run the expensive batch step again
#ndvi_df.to_csv("ndvi_results.csv", index=False)
#print("NDVI results saved to ndvi_results.csv")
#print(f"Missing NDVI values: {ndvi_df['ndvi_mean'].isna().sum()}")

import os

chunk_size = 500
output_file = "ndvi_results.csv"
total_chunks = (len(buffered_all) // chunk_size) + 1

# Check how many chunks are already done (resume capability)
if os.path.exists(output_file):
    existing_df = pd.read_csv(output_file)
    done_segment_ids = set(existing_df['segment_id'])
    print(f"Resuming — {len(done_segment_ids)} segments already saved")
else:
    existing_df = pd.DataFrame(columns=['segment_id', 'ndvi_mean'])
    done_segment_ids = set()

if os.path.exists("ndvi_results.csv"):
    print("Loading existing NDVI results from CSV")
    ndvi_df = pd.read_csv("ndvi_results.csv")
else:
    for i in range(0, len(buffered_all), chunk_size):
        chunk = buffered_all.iloc[i:i + chunk_size]
        chunk_num = i // chunk_size + 1

        if set(chunk['segment_id']).issubset(done_segment_ids):
            print(f"Skipping chunk {chunk_num} of {total_chunks} (already done)")
            continue

        features = [
            ee.Feature(ee.Geometry(row.geometry.__geo_interface__), {'segment_id': row['segment_id']})
            for _, row in chunk.iterrows()
        ]
        fc = ee.FeatureCollection(features)

        result = ndvi.reduceRegions(
            collection=fc,
            reducer=ee.Reducer.mean(),
            scale=10
        )

        chunk_results = result.getInfo()['features']

        chunk_records = []
        for feature in chunk_results:
            props = feature['properties']
            chunk_records.append({
                'segment_id': props['segment_id'],
                'ndvi_mean': props.get('mean')
            })
        chunk_df = pd.DataFrame(chunk_records)

        write_header = not os.path.exists("ndvi_results.csv")
        chunk_df.to_csv("ndvi_results.csv", mode='a', header=write_header, index=False)

        print(f"Processed and saved chunk {chunk_num} of {total_chunks}")
        time.sleep(1)

    print("Finished processing all segments")

    print("--- Testing reduceRegions directly on 5 real segments ---")
final_check = pd.read_csv("ndvi_results.csv")
print(f"Total rows: {len(final_check)}")
print(f"Non-null ndvi_mean count: {final_check['ndvi_mean'].notna().sum()}")
print(final_check.head())