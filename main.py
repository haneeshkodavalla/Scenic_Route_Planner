# main.py

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx
from router_core import get_route

app = FastAPI()

# Lets a frontend page opened from anywhere call this API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/route")
def route(
    alpha: float = Query(0.5, ge=0, le=1),
    start_lat: float = 18.7833,
    start_lon: float = 73.3667,
    end_lat: float = 18.7333,
    end_lon: float = 73.6833,
):
    try:
        return get_route(start_lat, start_lon, end_lat, end_lon, alpha)
    except nx.NetworkXNoPath:
        raise HTTPException(status_code=404, detail="No route found between these points")

import os
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend"), html=True), name="frontend")