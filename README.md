# Most Scenic Route Planner

A Web GIS route-planning prototype that compares **fastest, balanced, and scenery-focused driving routes** in the Khopoli–Talegaon Dabhade corridor of Maharashtra, India.

Instead of optimizing only travel time, the project scores road segments using geospatial and environmental factors, then lets users explore a trade-off between travel time and scenery.

## Features

- Interactive **Leaflet** map with **OpenStreetMap** basemap tiles.
- Comparison of the fastest route with a scenery-weighted route.
- An `alpha` control to adjust the travel-time/scenery trade-off (`1` = fastest; `0` = most scenery-focused).
- Click-to-select start and destination points within the supported study area.
- Route distance, estimated travel time, and mean scenic score.
- **FastAPI** endpoint (`/route`) serving routes to the frontend.

## Technology stack

**Python**, OSMnx, GeoPandas, pandas, NetworkX (Dijkstra routing), Google Earth Engine, Sentinel-2 NDVI, SRTM elevation, FastAPI, Uvicorn, Leaflet, and OpenStreetMap.

## Study area and methodology

- **Study corridor:** Khopoli to Talegaon Dabhade, including roads around Khandala and Lonavala.
- **Road network:** 9,870 nodes and **22,974 road segments** extracted from OpenStreetMap.
- **Six scenic factors:** NDVI/vegetation, road quietness (proxy based on road class), water proximity, elevation variation, land-use proximity, and nearby named attractions.
- Factors are normalized and combined into a weighted scenic score.
- Routing uses a combined travel-time and scenery-aware edge cost, with an extra penalty on local residential streets to discourage impractical detours.

### Example results (default start and end points)

| Setting | Distance | Estimated travel time | Average scenic score |
| --- | ---: | ---: | ---: |
| Fastest (`alpha=1`) | 54.8 km | 50 min | 0.286 |
| Balanced (`alpha≈0.45`) | 45.4 km | 56 min | 0.317 |
| Most scenery-focused (`alpha=0`) | 59.7 km | 83 min | 0.439 |

These figures are from the project report. Travel times are based on assumed road speeds, **not live traffic**. The scenery scores have not been validated against human ratings.

## Running locally

### Prerequisites

- Python and `pip`
- Internet access for OpenStreetMap basemap tiles

From the repository's root directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --app-dir .
```

Open <http://127.0.0.1:8000> in a browser. The application loads the included processed road-network and scenic-score files; you do not need to recompute satellite scores just to run the map.

> If the commands differ for your environment, update this section after testing installation in a new virtual environment. The original project was developed and tested on Windows.

## Repository contents

- `main.py` — FastAPI server and frontend serving.
- `router_core.py` — route selection and calculation.
- `config.py`, `scoring.py` — scenic factor configuration and score logic.
- `frontend/` — interactive Leaflet map.
- `khopoli_talegaon_raw.graphml` — processed road graph.
- `final_scored_segments.csv` — processed road scenic scores.
- Other root-level `.py` files — source-data processing, scoring, experiments, and validation.
- `docs/` — detailed project report.
- `screenshots/` — application screenshots (add before publishing).

## Screenshots

_Add a screenshot to `screenshots/route-comparison.png`, then replace this sentence with:_

`![Route comparison](screenshots/route-comparison.png)`

## Limitations

- The study area is restricted to a defined corridor; arbitrary out-of-area routes are unsupported.
- NDVI is based on January–March 2024 imagery, not a seasonal live vegetation feed.
- Environmental scores use assumptions and weights tuned on one corridor.
- `alpha` may result in a small number of distinct practical routes rather than smoothly changing paths.
- The most scenery-focused result may include a substantial detour and has not been independently rated by travelers.
- No live traffic, road closures, or real-time safety conditions are modeled.

## Data attribution

Contains information derived from **OpenStreetMap**, © OpenStreetMap contributors. Satellite-derived indicators use Sentinel-2 and SRTM products processed with Google Earth Engine. Consult each provider's licensing and attribution requirements before redistributing derivative datasets. See the project report for methodology and data details.

## Project report

[Read the full project report](docs/Most_Scenic_Route_Planner_Project_Report.pdf) (add this PDF to `docs/` before publishing).
