# attractions_scoring.py

import osmnx as ox
import geopandas as gpd

ox.settings.overpass_url = "https://overpass.kumi.systems/api/interpreter"
ox.settings.timeout = 300

# Same bounding box as before
north, south, east, west = 18.85, 18.65, 73.75, 73.30

attractions = ox.features_from_bbox(
    bbox=(west, south, east, north),
    tags={
        "tourism": ["attraction", "viewpoint", "picnic_site"],
        "historic": ["fort", "castle", "ruins", "archaeological_site", "monument"],
        "waterway": "waterfall",
        "natural": ["peak", "cave_entrance"],
    }
)

print(f"Attraction features found: {len(attractions)}")

attractions.to_pickle("attractions_raw.pkl")

# How many of each type exist in your corridor
for col in ['tourism', 'historic', 'waterway', 'natural']:
    if col in attractions.columns:
        print(f"\n{col}:")
        print(attractions[col].value_counts().to_string())

if 'name' in attractions.columns:
    names = attractions['name'].dropna()
    print(f"\nFeatures with a name: {len(names)}")
    print(names.head(30).to_string())
    print("Names containing 'loha':", names[names.str.contains('loha', case=False)].tolist())

