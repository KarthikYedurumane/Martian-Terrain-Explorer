"""
Martian Terrain Explorer - Hazard Detection Module
Quantifies terrain difficulty and categorizes rover exploration risks:
- Low Hazard (0-8 deg): Safe plain, standard rover transit
- Medium Hazard (8-15 deg): Moderate slope, reduced speed required
- High Hazard (>15 deg): Steep scarps, crater walls, wheel slippage
- Critical (>25 deg): Impassable cliff, rover rollover threshold
"""

import math
import numpy as np

class MarsHazardDetector:
    def __init__(self, terrain_analyzer):
        self.terrain = terrain_analyzer
        self.slope_grid = self.terrain.slope_grid
        self.rows, self.cols = self.slope_grid.shape
        
        # Hazard classification thresholds in degrees (NASA Rover mobility standards)
        self.THRESH_LOW = 8.0     # Green / Safe
        self.THRESH_MED = 15.0    # Yellow / Caution
        self.THRESH_CRIT = 25.0   # Red / High Hazard & Impassable
        
        # Identified Landmark Hazard Zones
        self.known_hazard_features = [
            {
                "name": "Jezero Western Rim Scarp",
                "center": (18.60, 77.19),
                "radius_km": 4.5,
                "type": "Crater Wall",
                "risk": "High",
                "description": "Steep 900m relief crater rim with slopes exceeding 20°."
            },
            {
                "name": "Delta Front Cliff Scarp",
                "center": (18.42, 77.41),
                "radius_km": 2.5,
                "type": "Delta Front Escarpment",
                "risk": "High",
                "description": "Near-vertical delta deposits with 18-28° drop down to crater floor."
            },
            {
                "name": "Kodiak Butte Cliffs",
                "center": (18.410, 77.400),
                "radius_km": 0.8,
                "type": "Erosional Butte",
                "risk": "High",
                "description": "Steep 25-35° cliff perimeter around isolated sedimentary mesa."
            },
            {
                "name": "Belva Crater Inner Wall",
                "center": (18.480, 77.370),
                "radius_km": 0.9,
                "type": "Impact Crater Rim",
                "risk": "High",
                "description": "Excavated crater interior with severe inward wall slopes of 15-26°."
            },
            {
                "name": "Neretva Vallis Gorge",
                "center": (18.550, 77.230),
                "radius_km": 1.5,
                "type": "Inflow Canyon",
                "risk": "Medium-High",
                "description": "Ancient flood gorge incision through fractured bedrock."
            }
        ]
        
        # Compute global hazard area statistics
        self._calculate_statistics()

    def _calculate_statistics(self):
        """Calculates area coverage percentages for each hazard class."""
        total_px = self.slope_grid.size
        low_px = np.count_nonzero(self.slope_grid <= self.THRESH_LOW)
        med_px = np.count_nonzero((self.slope_grid > self.THRESH_LOW) & (self.slope_grid <= self.THRESH_MED))
        high_px = np.count_nonzero(self.slope_grid > self.THRESH_MED)
        crit_px = np.count_nonzero(self.slope_grid > self.THRESH_CRIT)
        
        self.stats = {
            "total_analyzed_area_km2": round((self.terrain.loader.max_x - self.terrain.loader.min_x) * 
                                             (self.terrain.loader.max_y - self.terrain.loader.min_y) / 1e6, 2),
            "low_hazard_pct": round(low_px / total_px * 100.0, 1),
            "med_hazard_pct": round(med_px / total_px * 100.0, 1),
            "high_hazard_pct": round(high_px / total_px * 100.0, 1),
            "critical_hazard_pct": round(crit_px / total_px * 100.0, 1),
            "mean_slope_deg": round(float(np.mean(self.slope_grid)), 2),
            "max_slope_deg": round(float(np.max(self.slope_grid)), 2)
        }

    def assess_point(self, lat, lon):
        """Returns detailed hazard assessment for a given (lat, lon)."""
        slope = self.terrain.get_slope_at(lat, lon)
        elev = self.terrain.get_elevation_at(lat, lon)
        
        if slope is None:
            return {
                "status": "outside_bounds",
                "level": "Unknown",
                "message": "Coordinates outside Jezero study area."
            }
            
        # Classify hazard level
        if slope <= self.THRESH_LOW:
            level = "Low"
            color = "#10b981" # Green
            rover_mobility = "Nominal transit (approved up to 100 m/hr)."
            risk_desc = "Gentle terrain with negligible risk of wheel slippage or tipping."
        elif slope <= self.THRESH_MED:
            level = "Medium"
            color = "#f59e0b" # Yellow / Amber
            rover_mobility = "Caution transit (low-gear drive, active slip monitoring)."
            risk_desc = "Moderate incline requiring careful waypoint placement and hazard avoidance."
        elif slope <= self.THRESH_CRIT:
            level = "High"
            color = "#ef4444" # Red
            rover_mobility = "Restricted (requires scientific override and steep-slope planning)."
            risk_desc = "Steep terrain prone to significant wheel sinkage, slippage, and obstacle collision."
        else:
            level = "Critical"
            color = "#991b1b" # Dark Red
            rover_mobility = "Impassable (exceeds 25° rover tip-over limit)."
            risk_desc = "Severe cliff face or crater scarp; direct rover traverse prohibited."

        # Check proximity to known morphological hazard features
        nearby_hazards = []
        for feat in self.known_hazard_features:
            f_lat, f_lon = feat["center"]
            d_lat_km = math.radians(lat - f_lat) * self.terrain.loader.mars_radius / 1000.0
            d_lon_km = math.radians(lon - f_lon) * math.cos(math.radians(lat)) * self.terrain.loader.mars_radius / 1000.0
            dist_km = math.sqrt(d_lat_km**2 + d_lon_km**2)
            if dist_km <= feat["radius_km"] + 1.0:
                nearby_hazards.append({
                    "name": feat["name"],
                    "type": feat["type"],
                    "distance_km": round(dist_km, 2),
                    "description": feat["description"]
                })

        return {
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "elevation_m": round(elev, 2) if elev is not None else None,
            "slope_deg": round(slope, 2),
            "hazard_level": level,
            "hazard_color": color,
            "rover_mobility": rover_mobility,
            "risk_description": risk_desc,
            "nearby_features": nearby_hazards
        }

    def get_hazard_grid(self):
        """
        Returns an integer matrix for fast routing penalty calculations:
        0 = Low, 1 = Med, 2 = High, 3 = Impassable
        """
        hazard_matrix = np.zeros_like(self.slope_grid, dtype=np.uint8)
        hazard_matrix[self.slope_grid > self.THRESH_LOW] = 1
        hazard_matrix[self.slope_grid > self.THRESH_MED] = 2
        hazard_matrix[self.slope_grid > self.THRESH_CRIT] = 3
        return hazard_matrix
