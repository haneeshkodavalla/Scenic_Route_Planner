# route_attractions.py

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
from router_core import get_route

# Same attractions list as attractions_distance.py
attractions = pd.read_pickle("attractions_raw.pkl")
named = attractions[attractions['name'].notna()].copy()
if 'waterway' in named.columns:
    named = named[named['waterway'] != 'dam']
if 'natural' in named.columns:
    named = named[named['natural'] != 'water']
named = named.to_crs(epsg=32643)

def check_route(alpha, limit=1000):
    r = get_route(18.7833, 73.3667, 18.7333, 73.6833, alpha)

    # route coordinates are [lat, lon], shapely wants (lon, lat)
    line = gpd.GeoSeries(
        [LineString([(lon, lat) for lat, lon in r['route']])], crs=4326
    ).to_crs(epsg=32643).iloc[0]

    named_d = named.assign(dist=named.geometry.distance(line))
    close = named_d[named_d['dist'] <= limit].sort_values('dist')
    loha = named_d[named_d['name'].str.contains('lohagad', case=False)]

    print(f"\nalpha={alpha}: {r['distance_km']} km, {r['time_min']} min "
          f"-> {len(close)} attractions within {limit} m of the route")
    for name, dist in zip(close['name'], close['dist']):
        print(f"   {name}: {dist:.0f} m")
    print("   Lohagad:", ", ".join(f"{n} {d:.0f} m" for n, d in zip(loha['name'], loha['dist'])))

for alpha in [1, 0.5, 0]:
    check_route(alpha)