# scoring.py

from config import scenic_weights

def compute_scenic_score(norm_ndvi, norm_water_proximity, norm_road_quietness,
                          norm_elevation_variation, norm_landuse_bonus, norm_attractions):
    score = (
        scenic_weights["ndvi"] * norm_ndvi +
        scenic_weights["water_proximity"] * norm_water_proximity +
        scenic_weights["road_quietness"] * norm_road_quietness +
        scenic_weights["elevation_variation"] * norm_elevation_variation +
        scenic_weights["landuse_bonus"] * norm_landuse_bonus +
        scenic_weights["attractions"] * norm_attractions
    )
    return score