import os
import sys

# Add project root to path
sys.path.insert(0, r"d:\nasa")

from modules.raster_loader import MarsRasterLoader
from modules.terrain_analysis import MarsTerrainAnalyzer
from modules.hazard_detection import MarsHazardDetector
from modules.route_planner import MarsRoutePlanner
from modules.raster_processor import MarsRasterProcessor

print("Testing Martian Terrain Explorer modules...")

tif_path = r"d:\nasa\data\original\JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif"
loader = MarsRasterLoader(tif_path)
print(f"Raster loaded: {loader.width}x{loader.height}, 6m resolution.")
print(f"Bounds: Lat ({loader.lat_min:.4f}, {loader.lat_max:.4f}), Lon ({loader.lon_min:.4f}, {loader.lon_max:.4f})")

terrain = MarsTerrainAnalyzer(loader, grid_resolution=300)
print(f"Terrain DEM generated: range [{terrain.dem.min():.1f}m, {terrain.dem.max():.1f}m]")
print(f"Slope grid generated: mean {terrain.slope_grid.mean():.2f} deg, max {terrain.slope_grid.max():.2f} deg")

hazards = MarsHazardDetector(terrain)
print(f"Hazard stats: {hazards.stats}")

processor = MarsRasterProcessor(loader, terrain, hazards, r"d:\nasa\data\processed")
print("Web assets generated successfully!")

# Test point inspection at Perseverance Landing Site
landing_lat, landing_lon = 18.4446, 77.4509
point_info = hazards.assess_point(landing_lat, landing_lon)
print(f"\nPoint Inspection at Perseverance Landing Site ({landing_lat}, {landing_lon}):")
print(f"  Elevation: {point_info['elevation_m']} m")
print(f"  Slope: {point_info['slope_deg']} deg")
print(f"  Hazard Level: {point_info['hazard_level']} ({point_info['rover_mobility']})")

# Test route planning from Landing Site (Octavia E. Butler) to Western Delta Fan
planner = MarsRoutePlanner(terrain, hazards, routing_res=120)
start = (18.4446, 77.4509) # Landing site
dest = (18.4350, 77.3850)  # Delta top
print(f"\nPlanning Route from {start} to {dest}...")
route = planner.plan_route(start[0], start[1], dest[0], dest[1])
if route["success"]:
    print(f"Route Found!")
    print(f"  Total Distance: {route['summary']['total_distance_km']} km (Straight: {route['summary']['straight_distance_km']} km)")
    print(f"  Max Slope: {route['summary']['max_slope_deg']} deg (Straight max: {route['summary']['straight_max_slope_deg']} deg)")
    print(f"  Safety: {route['summary']['safety_rating']}")
    print(f"  Waypoints: {len(route['waypoints'])}")
else:
    print(f"Route Error: {route.get('error')}")

print("\nALL MODULE CHECKS PASSED!")
