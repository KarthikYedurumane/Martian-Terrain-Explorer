"""
Martian Terrain Explorer - Flask Backend
Interactive Mars Mapping, Hazard Assessment & Safe Route Planning System
NASA Space Apps Challenge 2026
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.raster_loader import MarsRasterLoader
from modules.terrain_analysis import MarsTerrainAnalyzer
from modules.hazard_detection import MarsHazardDetector
from modules.route_planner import MarsRoutePlanner
from modules.raster_processor import MarsRasterProcessor

app = Flask(__name__, 
            template_folder=os.path.join(PROJECT_ROOT, "templates"),
            static_folder=os.path.join(PROJECT_ROOT, "static"))

# Path to the uploaded original NASA CTX GeoTIFF
ORIGINAL_TIFF_PATH = os.path.join(PROJECT_ROOT, "data", "original", "JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

print("="*60)
print("Initializing Martian Terrain Explorer Core Engines...")
print(f"Loading NASA GeoTIFF from: {ORIGINAL_TIFF_PATH}")
loader = MarsRasterLoader(ORIGINAL_TIFF_PATH)

print("Synthesizing NASA MOLA/HRSC Jezero Crater Topography...")
terrain = MarsTerrainAnalyzer(loader, grid_resolution=400)

print("Calibrating Rover Hazard Detection Engine...")
hazards = MarsHazardDetector(terrain)

print("Initializing A* Safe Route Planner...")
planner = MarsRoutePlanner(terrain, hazards, routing_res=140)

print("Processing Web Raster Layers and Tiles...")
processor = MarsRasterProcessor(loader, terrain, hazards, PROCESSED_DIR)
print("Martian Terrain Explorer Ready!")
print("="*60)

# Predefined Jezero Crater Landmark Catalog for Exploration
JEZERO_LANDMARKS = [
    {
        "id": "landing_site",
        "name": "Octavia E. Butler Landing (Perseverance)",
        "lat": 18.4446,
        "lon": 77.4509,
        "type": "Rover Landing Site",
        "sol_landed": "Sol 0 (Feb 18, 2021)",
        "description": "Smooth, flat basaltic floor where NASA Mars 2020 touched down with skycrane."
    },
    {
        "id": "kodiak_butte",
        "name": "Kodiak Butte",
        "lat": 18.4100,
        "lon": 77.4000,
        "type": "Erosional Butte / Mesa",
        "elevation_m": -2410,
        "description": "Isolated sedimentary mesa demonstrating ancient delta lakebed bottomset and topset beds."
    },
    {
        "id": "belva_crater",
        "name": "Belva Impact Crater",
        "lat": 18.4800,
        "lon": 77.3700,
        "type": "Impact Crater",
        "elevation_m": -2480,
        "description": "1 km diameter impact crater superposed on western delta deposits with exposed bedrock layers."
    },
    {
        "id": "delta_front",
        "name": "Western Delta Front Scarp",
        "lat": 18.4350,
        "lon": 77.4150,
        "type": "Delta Escarpment",
        "description": "Steep 60-80 meter drop where ancient river deposits abruptly terminate into the paleolake floor."
    },
    {
        "id": "neretva_vallis",
        "name": "Neretva Vallis Inflow Gorge",
        "lat": 18.5500,
        "lon": 77.2500,
        "type": "River Inflow Breach",
        "description": "Incision through Jezero's western rim through which an ancient river channel flooded the crater."
    },
    {
        "id": "jezero_center",
        "name": "Jezero Crater Geometric Center",
        "lat": 18.3800,
        "lon": 77.5800,
        "type": "Crater Basin Floor",
        "description": "Deepest portion of the central Jezero floor at ~2,580 meters below Mars datum."
    }
]

@app.route("/")
def index():
    """Main Application Dashboard."""
    return render_template("index.html")

@app.route("/api/info")
def get_info():
    """Returns dataset metadata, CRS, bounding coordinates, and landmarks."""
    meta = loader.get_metadata()
    meta["landmarks"] = JEZERO_LANDMARKS
    meta["hazard_stats"] = hazards.stats
    return jsonify(meta)

@app.route("/api/point")
def inspect_point():
    """
    Inspects point at (lat, lon).
    Returns pixel brightness, elevation, slope, and hazard tier.
    """
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing lat/lon parameters"}), 400

    if not loader.is_inside(lat, lon):
        return jsonify({
            "is_inside": False,
            "message": "Coordinates are outside the Jezero Crater study bounds."
        })

    pixel_val = loader.get_pixel_value(lat, lon)
    elev = terrain.get_elevation_at(lat, lon)
    slope = terrain.get_slope_at(lat, lon)
    hazard_info = hazards.assess_point(lat, lon)

    # Nearest landmark calculation
    nearest_landmark = None
    min_dist_km = 999999.0
    for lm in JEZERO_LANDMARKS:
        d_lat = (lat - lm["lat"]) * (loader.mars_radius * 3.14159 / 180.0) / 1000.0
        d_lon = (lon - lm["lon"]) * (loader.mars_radius * 3.14159 / 180.0 * 0.948) / 1000.0
        dist = (d_lat**2 + d_lon**2)**0.5
        if dist < min_dist_km:
            min_dist_km = dist
            nearest_landmark = {"name": lm["name"], "distance_km": round(dist, 2)}

    return jsonify({
        "is_inside": True,
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "ctx_reflectance": pixel_val,
        "elevation_m": round(elev, 2) if elev is not None else None,
        "slope_deg": round(slope, 2) if slope is not None else None,
        "hazard_level": hazard_info["hazard_level"],
        "hazard_color": hazard_info["hazard_color"],
        "rover_mobility": hazard_info["rover_mobility"],
        "risk_description": hazard_info["risk_description"],
        "nearby_hazards": hazard_info["nearby_features"],
        "nearest_landmark": nearest_landmark
    })

@app.route("/api/route", methods=["POST"])
def plan_route():
    """
    Computes an A* safe exploration route between start and destination coordinates.
    """
    data = request.get_json() or {}
    try:
        start_lat = float(data.get("start_lat"))
        start_lon = float(data.get("start_lon"))
        end_lat = float(data.get("end_lat"))
        end_lon = float(data.get("end_lon"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid start or destination coordinates"}), 400

    result = planner.plan_route(start_lat, start_lon, end_lat, end_lon)
    return jsonify(result)

@app.route("/api/profile")
def get_profile():
    """Elevation and slope profile transect between two coordinates."""
    try:
        lat1 = float(request.args.get("lat1"))
        lon1 = float(request.args.get("lon1"))
        lat2 = float(request.args.get("lat2"))
        lon2 = float(request.args.get("lon2"))
        samples = int(request.args.get("samples", 80))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid profile coordinates"}), 400

    profile = terrain.get_elevation_profile(lat1, lon1, lat2, lon2, num_samples=samples)
    return jsonify(profile)

@app.route("/api/tile/<int:z>/<int:x>/<int:y>.png")
def get_tile(z, x, y):
    """Dynamic 256x256 Slippy tile rendering."""
    png_bytes = processor.get_tile(z, x, y)
    return Response(png_bytes, mimetype="image/png")

@app.route("/processed/<path:filename>")
def serve_processed(filename):
    """Serves high-resolution web overview overlays (CTX, DEM, Slope, Hazard)."""
    return send_from_directory(PROCESSED_DIR, filename)

if __name__ == "__main__":
    print("\nStarting Martian Terrain Explorer Web Server...")
    print("Dashboard available at: http://127.0.0.1:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
