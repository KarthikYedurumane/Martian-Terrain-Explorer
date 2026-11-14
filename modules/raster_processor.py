"""
Martian Terrain Explorer - Raster Processor Module
Prepares lightweight web-ready assets from the uploaded 35MB GeoTIFF:
- Generates high-resolution web overview image (2048x1939) for instant Leaflet overlay.
- Generates colorized DEM Topography overlay (transparent PNG).
- Generates Slope & Hazard overlay (transparent PNG).
- Provides dynamic XYZ slippy tile slicing for high-zoom interactive viewing.
"""

import os
import io
import math
import numpy as np
from PIL import Image

class MarsRasterProcessor:
    def __init__(self, raster_loader, terrain_analyzer, hazard_detector, output_dir):
        self.loader = raster_loader
        self.terrain = terrain_analyzer
        self.hazards = hazard_detector
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.overview_ctx_path = os.path.join(self.output_dir, "jezero_ctx_overview.jpg")
        self.overview_dem_path = os.path.join(self.output_dir, "jezero_dem_overlay.png")
        self.overview_slope_path = os.path.join(self.output_dir, "jezero_slope_overlay.png")
        self.overview_hazard_path = os.path.join(self.output_dir, "jezero_hazard_overlay.png")
        
        # Ensure processed web rasters are generated
        self.generate_web_assets()

    def generate_web_assets(self, max_dim=2048):
        """Generates optimized web-friendly layers for fast browser rendering."""
        print("Processing raster assets for web performance...")
        
        # 1. CTX Base Map Overview
        if not os.path.exists(self.overview_ctx_path):
            print(f"Generating optimized CTX overview image (max {max_dim}px)...")
            raw_data = self.loader.load_data()
            h, w = raw_data.shape
            scale = max_dim / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            
            img = Image.fromarray(raw_data)
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            resized.save(self.overview_ctx_path, "JPEG", quality=88, optimize=True)
            print(f"Saved CTX overview: {self.overview_ctx_path} ({os.path.getsize(self.overview_ctx_path)/1024:.1f} KB)")
        else:
            print("CTX overview already exists.")

        # 2. DEM Topography Colorized Heatmap
        if not os.path.exists(self.overview_dem_path):
            print("Generating DEM Topography colorized overlay...")
            dem = self.terrain.dem
            min_e, max_e = -2600.0, -1600.0 # Standard Jezero relief
            norm_dem = np.clip((dem - min_e) / (max_e - min_e), 0.0, 1.0)
            
            # Turbo / Terrain style colormap (RGB)
            # 0.0 (deep crater floor) -> blue/purple, 0.5 (delta) -> teal/green, 1.0 (crater rim) -> orange/red
            r = np.clip(np.where(norm_dem < 0.5, 0.1, (norm_dem - 0.5) * 2.0), 0.0, 1.0)
            g = np.clip(np.where(norm_dem < 0.5, norm_dem * 2.0, 2.0 * (1.0 - norm_dem)), 0.0, 1.0)
            b = np.clip(np.where(norm_dem < 0.5, 1.0 - norm_dem * 1.5, 0.1), 0.0, 1.0)
            
            rgba = np.zeros((dem.shape[0], dem.shape[1], 4), dtype=np.uint8)
            rgba[..., 0] = (r * 255).astype(np.uint8)
            rgba[..., 1] = (g * 255).astype(np.uint8)
            rgba[..., 2] = (b * 255).astype(np.uint8)
            rgba[..., 3] = 180 # semi-transparent alpha
            
            dem_img = Image.fromarray(rgba, mode="RGBA")
            dem_img = dem_img.resize((1024, 1024), Image.Resampling.BILINEAR)
            dem_img.save(self.overview_dem_path, "PNG", optimize=True)
            print(f"Saved DEM overlay: {self.overview_dem_path}")

        # 3. Slope Heatmap
        if not os.path.exists(self.overview_slope_path):
            print("Generating Slope overlay...")
            slope = self.terrain.slope_grid
            rgba = np.zeros((slope.shape[0], slope.shape[1], 4), dtype=np.uint8)
            
            # Green (0-8 deg)
            mask_low = slope <= 8.0
            rgba[mask_low] = [16, 185, 129, 140]
            
            # Yellow (8-15 deg)
            mask_med = (slope > 8.0) & (slope <= 15.0)
            rgba[mask_med] = [245, 158, 11, 170]
            
            # Red (>15 deg)
            mask_high = slope > 15.0
            rgba[mask_high] = [239, 68, 68, 200]
            
            slope_img = Image.fromarray(rgba, mode="RGBA")
            slope_img = slope_img.resize((1024, 1024), Image.Resampling.NEAREST)
            slope_img.save(self.overview_slope_path, "PNG", optimize=True)
            print(f"Saved Slope overlay: {self.overview_slope_path}")

        # 4. Hazard Mask Overlay
        if not os.path.exists(self.overview_hazard_path):
            print("Generating Hazard overlay...")
            slope = self.terrain.slope_grid
            rgba = np.zeros((slope.shape[0], slope.shape[1], 4), dtype=np.uint8)
            
            # Only highlight significant hazards (>10 deg)
            mask_haz = slope > 10.0
            # Red glow with alpha proportional to slope
            alpha = np.clip((slope - 10.0) / 15.0 * 220, 0, 220).astype(np.uint8)
            rgba[mask_haz, 0] = 239 # R
            rgba[mask_haz, 1] = 68  # G
            rgba[mask_haz, 2] = 68  # B
            rgba[mask_haz, 3] = alpha[mask_haz]
            
            haz_img = Image.fromarray(rgba, mode="RGBA")
            haz_img = haz_img.resize((1024, 1024), Image.Resampling.BILINEAR)
            haz_img.save(self.overview_hazard_path, "PNG", optimize=True)
            print(f"Saved Hazard overlay: {self.overview_hazard_path}")

    def get_tile(self, z, x, y):
        """
        Dynamically extracts a 256x256 tile for slippy map coordinates (z, x, y).
        Maps standard web mercator tile bounds or custom local coordinate bounds.
        """
        # For our local Jezero bounding box, we support a local tile indexing scheme
        # or render on-the-fly sub-windows from the full-resolution CTX mosaic.
        raw = self.loader.load_data()
        h, w = raw.shape
        
        # Determine number of tiles at this zoom level
        tiles_count = 2 ** max(0, z - 10)
        if tiles_count <= 0:
            tiles_count = 1
            
        tile_w = w / tiles_count
        tile_h = h / tiles_count
        
        c0 = int(x * tile_w)
        c1 = int(min(w, (x + 1) * tile_w))
        r0 = int(y * tile_h)
        r1 = int(min(h, (y + 1) * tile_h))
        
        if c0 >= w or r0 >= h or c1 <= c0 or r1 <= r0:
            # Blank tile
            blank = Image.new("L", (256, 256), color=0)
            buf = io.BytesIO()
            blank.save(buf, format="PNG")
            return buf.getvalue()
            
        sub = raw[r0:r1, c0:c1]
        img = Image.fromarray(sub)
        tile = img.resize((256, 256), Image.Resampling.BILINEAR)
        buf = io.BytesIO()
        tile.save(buf, format="PNG")
        return buf.getvalue()
