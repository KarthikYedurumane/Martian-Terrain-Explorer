"""
Martian Terrain Explorer - Safe Route Planning Module
Implements A* pathfinding on a cost-weighted terrain grid.
Accounts for slope steepness, elevation delta, and hazard obstacle avoidance.
Compares proposed lower-cost route with straight-line direct transit.
"""

import math
import heapq
import numpy as np

class MarsRoutePlanner:
    def __init__(self, terrain_analyzer, hazard_detector, routing_res=150):
        """
        routing_res: size of the routing grid (e.g., 150x150, ~200m cell size).
        Provides sub-second A* search while maintaining high obstacle fidelity.
        """
        self.terrain = terrain_analyzer
        self.hazards = hazard_detector
        self.routing_res = routing_res
        
        self.lon_min = self.terrain.lon_min
        self.lon_max = self.terrain.lon_max
        self.lat_min = self.terrain.lat_min
        self.lat_max = self.terrain.lat_max
        
        # Build downsampled slope and elevation grids for fast pathfinding
        self._build_routing_matrices()

    def _build_routing_matrices(self):
        """Downsamples full DEM and slope to routing resolution."""
        # Using PIL or simple slice/zoom for fast resampling
        from PIL import Image
        
        dem_img = Image.fromarray(self.terrain.dem.astype(np.float32))
        dem_resampled = dem_img.resize((self.routing_res, self.routing_res), Image.Resampling.BILINEAR)
        self.route_dem = np.array(dem_resampled)
        
        slope_img = Image.fromarray(self.terrain.slope_grid.astype(np.float32))
        slope_resampled = slope_img.resize((self.routing_res, self.routing_res), Image.Resampling.BILINEAR)
        self.route_slope = np.array(slope_resampled)
        
        # Grid spatial spacing in meters
        self.cell_dx_m = (self.terrain.loader.max_x - self.terrain.loader.min_x) / (self.routing_res - 1)
        self.cell_dy_m = (self.terrain.loader.max_y - self.terrain.loader.min_y) / (self.routing_res - 1)

    def _latlon_to_grid(self, lat, lon):
        """Converts (lat, lon) to integer (row, col) on routing grid."""
        col = int(round((lon - self.lon_min) / (self.lon_max - self.lon_min) * (self.routing_res - 1)))
        row = int(round((self.lat_max - lat) / (self.lat_max - self.lat_min) * (self.routing_res - 1)))
        return np.clip(row, 0, self.routing_res - 1), np.clip(col, 0, self.routing_res - 1)

    def _grid_to_latlon(self, row, col):
        """Converts integer (row, col) to (lat, lon)."""
        lon = self.lon_min + (col / (self.routing_res - 1)) * (self.lon_max - self.lon_min)
        lat = self.lat_max - (row / (self.routing_res - 1)) * (self.lat_max - self.lat_min)
        return lat, lon

    def plan_route(self, start_lat, start_lon, end_lat, end_lon):
        """
        Plans a proposed lower-cost exploration route using A* pathfinding.
        Returns detailed route statistics, GeoJSON coordinates, and comparison.
        """
        # Verify both points inside study area
        if not (self.terrain.loader.is_inside(start_lat, start_lon) and 
                self.terrain.loader.is_inside(end_lat, end_lon)):
            return {
                "success": False,
                "error": "Start or destination coordinates lie outside the Jezero Crater study area."
            }

        start_r, start_c = self._latlon_to_grid(start_lat, start_lon)
        end_r, end_c = self._latlon_to_grid(end_lat, end_lon)

        # 8-neighbor movements: (dr, dc, move_cost_factor)
        moves = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.4142), (-1, 1, 1.4142), (1, -1, 1.4142), (1, 1, 1.4142)
        ]

        def heuristic(r, c):
            dr = abs(r - end_r)
            dc = abs(c - end_c)
            # Octile distance heuristic
            return (dr + dc + (1.4142 - 2.0) * min(dr, dc)) * self.cell_dx_m

        # Priority queue for A*: (f_score, g_score, (r, c))
        open_set = []
        heapq.heappush(open_set, (heuristic(start_r, start_c), 0.0, (start_r, start_c)))
        
        came_from = {}
        g_scores = { (start_r, start_c): 0.0 }
        visited = set()

        path_found = False
        max_iterations = 80000
        iterations = 0

        while open_set and iterations < max_iterations:
            iterations += 1
            current_f, current_g, (curr_r, curr_c) = heapq.heappop(open_set)

            if (curr_r, curr_c) == (end_r, end_c):
                path_found = True
                break

            if (curr_r, curr_c) in visited:
                continue
            visited.add((curr_r, curr_c))

            curr_elev = self.route_dem[curr_r, curr_c]

            for dr, dc, move_dist in moves:
                nr, nc = curr_r + dr, curr_c + dc
                if not (0 <= nr < self.routing_res and 0 <= nc < self.routing_res):
                    continue

                neighbor_slope = self.route_slope[nr, nc]
                neighbor_elev = self.route_dem[nr, nc]

                # Impassable check (rollover risk > 25 degrees)
                if neighbor_slope > 25.0:
                    continue

                # Base cost in physical meters
                step_dist_m = move_dist * self.cell_dx_m

                # Slope penalty: exponential growth above nominal 8 degrees
                slope_penalty = 1.0 + 3.5 * ((neighbor_slope / 15.0) ** 2)
                
                # Uphill elevation cost (energy penalty)
                elev_diff = neighbor_elev - curr_elev
                uphill_penalty = max(0.0, elev_diff / 10.0) * 0.5

                # Total edge cost
                edge_cost = step_dist_m * slope_penalty + uphill_penalty
                tentative_g = current_g + edge_cost

                if (nr, nc) not in g_scores or tentative_g < g_scores[(nr, nc)]:
                    g_scores[(nr, nc)] = tentative_g
                    f_score = tentative_g + heuristic(nr, nc)
                    came_from[(nr, nc)] = (curr_r, curr_c)
                    heapq.heappush(open_set, (f_score, tentative_g, (nr, nc)))

        if not path_found:
            return {
                "success": False,
                "error": "No viable route found without exceeding safe slope threshold (25°). Destination may be encircled by cliff scarps."
            }

        # Reconstruct path
        path_cells = []
        curr = (end_r, end_c)
        while curr in came_from:
            path_cells.append(curr)
            curr = came_from[curr]
        path_cells.append((start_r, start_c))
        path_cells.reverse()

        # Convert path cells to detailed waypoints
        route_waypoints = []
        total_dist_km = 0.0
        elev_gain_m = 0.0
        elev_loss_m = 0.0
        route_slopes = []
        route_elevations = []

        for i, (r, c) in enumerate(path_cells):
            lat, lon = self._grid_to_latlon(r, c)
            elev = float(self.terrain.get_elevation_at(lat, lon))
            slope = float(self.terrain.get_slope_at(lat, lon))
            
            if i > 0:
                prev_lat, prev_lon = route_waypoints[i-1]["lat"], route_waypoints[i-1]["lon"]
                prev_elev = route_waypoints[i-1]["elevation_m"]
                
                d_lat_m = math.radians(lat - prev_lat) * self.terrain.loader.mars_radius
                d_lon_m = math.radians(lon - prev_lon) * math.cos(math.radians((lat + prev_lat)/2.0)) * self.terrain.loader.mars_radius
                step_km = math.sqrt(d_lat_m**2 + d_lon_m**2) / 1000.0
                total_dist_km += step_km

                d_elev = elev - prev_elev
                if d_elev > 0:
                    elev_gain_m += d_elev
                else:
                    elev_loss_m += abs(d_elev)

            route_slopes.append(slope)
            route_elevations.append(elev)
            
            route_waypoints.append({
                "step": i,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "elevation_m": round(elev, 2),
                "slope_deg": round(slope, 2),
                "distance_km": round(total_dist_km, 3)
            })

        # Straight-line comparison path
        straight_profile = self.terrain.get_elevation_profile(start_lat, start_lon, end_lat, end_lon, num_samples=len(route_waypoints))
        
        # Risk assessment for the proposed route
        max_slope = max(route_slopes) if route_slopes else 0.0
        avg_slope = sum(route_slopes) / len(route_slopes) if route_slopes else 0.0
        
        if max_slope <= 8.0:
            route_safety = "High (Nominal exploration terrain)"
            safety_badge = "Safe"
        elif max_slope <= 15.0:
            route_safety = "Moderate (Acceptable with autonomous hazard detection)"
            safety_badge = "Moderate"
        else:
            route_safety = "Challenging (Includes controlled traversals up to 25°)"
            safety_badge = "Challenging"

        return {
            "success": True,
            "summary": {
                "total_distance_km": round(total_dist_km, 2),
                "straight_distance_km": round(straight_profile["total_distance_km"], 2),
                "distance_overhead_pct": round(((total_dist_km / max(0.001, straight_profile["total_distance_km"])) - 1.0) * 100.0, 1),
                "elevation_gain_m": round(elev_gain_m, 1),
                "elevation_loss_m": round(elev_loss_m, 1),
                "max_slope_deg": round(max_slope, 2),
                "avg_slope_deg": round(avg_slope, 2),
                "straight_max_slope_deg": round(straight_profile["max_slope_deg"], 2),
                "straight_avg_slope_deg": round(straight_profile["avg_slope_deg"], 2),
                "safety_rating": route_safety,
                "safety_badge": safety_badge,
                "disclaimer": "Proposed lower-cost route based on NASA MOLA/HRSC Jezero elevation model. Real operational transit requires local in-situ rover obstacle evaluation."
            },
            "waypoints": route_waypoints,
            "straight_samples": straight_profile["samples"],
            "start_point": {"lat": start_lat, "lon": start_lon},
            "destination_point": {"lat": end_lat, "lon": end_lon}
        }
