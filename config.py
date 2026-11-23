# config.py

scenic_weights = {
    "ndvi": 0.30,
    "road_quietness": 0.30,
    "attractions": 0.20,
    "water_proximity": 0.10,
    "elevation_variation": 0.05,
    "landuse_bonus": 0.05,
}

# config.py (add below scenic_weights)

road_type_scores = {
    "motorway": 0.0,
    "motorway_link": 0.1,
    "trunk": 0.2,
    "trunk_link": 0.3,
    "primary": 0.4,
    "primary_link": 0.4,
    "secondary": 0.6,
    "secondary_link": 0.6,
    "tertiary": 0.8,
    "tertiary_link": 0.8,
    "unclassified": 0.9,
    "residential": 1.0,
    "living_street": 1.0,
}