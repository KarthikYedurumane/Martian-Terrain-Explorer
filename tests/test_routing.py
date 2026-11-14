"""
Martian Terrain Explorer - Automated Test Suite: A* Route Planning
Validates A* pathfinding, obstacle avoidance, and distance metrics.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.raster_loader import MarsRasterLoader
from modules.terrain_analysis import MarsTerrainAnalyzer
from modules.hazard_detection import MarsHazardDetector
from modules.route_planner import MarsRoutePlanner

class TestRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "original", "JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif"))
        cls.loader = MarsRasterLoader(tif_path)
        cls.terrain = MarsTerrainAnalyzer(cls.loader, grid_resolution=150)
        cls.hazards = MarsHazardDetector(cls.terrain)
        cls.planner = MarsRoutePlanner(cls.terrain, cls.hazards, routing_res=80)

    def test_plan_nominal_route(self):
        # Route from Landing site towards delta
        start_lat, start_lon = 18.4446, 77.4509
        end_lat, end_lon = 18.4350, 77.4200
        result = self.planner.plan_route(start_lat, start_lon, end_lat, end_lon)
        
        self.assertTrue(result["success"], "A* must find a route between accessible waypoints")
        self.assertGreater(len(result["waypoints"]), 0)
        self.assertGreater(result["summary"]["total_distance_km"], 0.0)
        self.assertLessEqual(result["summary"]["max_slope_deg"], 25.0, "Path must not cross impassable >25° terrain")

    def test_out_of_bounds(self):
        # Points outside bounds
        result = self.planner.plan_route(0.0, 0.0, 18.4446, 77.4509)
        self.assertFalse(result["success"], "Must gracefully reject out-of-bounds coordinates")

if __name__ == "__main__":
    unittest.main()
