"""
Martian Terrain Explorer - Automated Test Suite: Terrain Analysis & Hazards
Validates Horn slope calculations, topographic range, hazard classifications.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.raster_loader import MarsRasterLoader
from modules.terrain_analysis import MarsTerrainAnalyzer
from modules.hazard_detection import MarsHazardDetector

class TestTerrain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "original", "JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif"))
        cls.loader = MarsRasterLoader(tif_path)
        cls.terrain = MarsTerrainAnalyzer(cls.loader, grid_resolution=150)
        cls.hazards = MarsHazardDetector(cls.terrain)

    def test_elevation_range(self):
        # Jezero crater floor is around -2550m, rim rises to -1600m
        min_e = self.terrain.dem.min()
        max_e = self.terrain.dem.max()
        self.assertLess(min_e, -2500.0, "Crater basin floor must reach below -2,500 m")
        self.assertGreater(max_e, -1700.0, "Crater rim must rise above -1,700 m")

    def test_landing_site_slope(self):
        # Perseverance landing site was specifically chosen for low slope (< 3 deg)
        slope = self.terrain.get_slope_at(18.4446, 77.4509)
        self.assertIsNotNone(slope)
        self.assertLess(slope, 5.0, "Landing site slope must be nominal (< 5 degrees)")

    def test_hazard_classification(self):
        # Landing site must be Low Hazard
        assess = self.hazards.assess_point(18.4446, 77.4509)
        self.assertEqual(assess["hazard_level"], "Low")
        
        # Point on steep Neretva Vallis canyon breach (18.5466, 77.2509)
        canyon_assess = self.hazards.assess_point(18.5466, 77.2509)
        self.assertIn(canyon_assess["hazard_level"], ["Medium", "High", "Critical"])

    def test_elevation_profile(self):
        profile = self.terrain.get_elevation_profile(18.4446, 77.4509, 18.4350, 77.4150, num_samples=20)
        self.assertEqual(len(profile["samples"]), 20)
        self.assertGreater(profile["total_distance_km"], 0.0)

if __name__ == "__main__":
    unittest.main()
