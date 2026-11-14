"""
Martian Terrain Explorer - Automated Test Suite: Georeferencing & Metadata
Validates TIFF dimensions, binary GeoTIFF parsing, and Equirectangular projections.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.raster_loader import MarsRasterLoader

class TestGeoreference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "original", "JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif"))
        cls.loader = MarsRasterLoader(cls.tif_path)

    def test_file_exists(self):
        self.assertTrue(os.path.exists(self.tif_path), "Original TIFF must exist")

    def test_dimensions(self):
        self.assertEqual(self.loader.width, 5322, "Image width must be exactly 5,322 px")
        self.assertEqual(self.loader.height, 5040, "Image height must be exactly 5,040 px")
        self.assertEqual(self.loader.samples_per_pixel, 1, "Must be single-band panchromatic")
        self.assertEqual(self.loader.bits_per_sample, 8, "Must be 8-bit uint8 data")

    def test_resolution(self):
        self.assertEqual(self.loader.dx, 6.0, "X pixel resolution must be 6.0 m/px")
        self.assertEqual(self.loader.dy, 6.0, "Y pixel resolution must be 6.0 m/px")

    def test_mars_datum(self):
        self.assertEqual(self.loader.mars_radius, 3396190.0, "Mars IAU 2000 Sphere radius must be 3,396,190 m")

    def test_geographic_bounds(self):
        self.assertAlmostEqual(self.loader.lon_min, 77.1605, places=3)
        self.assertAlmostEqual(self.loader.lon_max, 77.6992, places=3)
        self.assertAlmostEqual(self.loader.lat_min, 18.2110, places=3)
        self.assertAlmostEqual(self.loader.lat_max, 18.7212, places=3)

    def test_landing_site_inside(self):
        # NASA Perseverance Landing Site (Octavia E. Butler)
        lat, lon = 18.4446, 77.4509
        self.assertTrue(self.loader.is_inside(lat, lon), "Perseverance landing site must be within bounds")
        px_val = self.loader.get_pixel_value(lat, lon)
        self.assertIsNotNone(px_val)
        self.assertGreater(px_val, 0)
        self.assertLessEqual(px_val, 255)

if __name__ == "__main__":
    unittest.main()
