/**
 * Martian Terrain Explorer - Autonomous A* Route Planning Module
 * Manages Start/Goal waypoints, presets, backend A* execution, and path visualization.
 */

class MarsRoutingManager {
    constructor(map, analysisManager) {
        this.map = map;
        this.analysis = analysisManager;
        
        this.startPoint = null;
        this.endPoint = null;
        this.pinMode = null; // 'start', 'dest', or null
        
        this.startMarker = null;
        this.endMarker = null;
        this.routePolyline = null;
        this.straightPolyline = null;
        this.waypointMarkers = L.layerGroup().addTo(this.map);
        
        this.initUI();
    }

    initUI() {
        const btnSetStart = document.getElementById('btn-set-start');
        const btnSetDest = document.getElementById('btn-set-dest');
        const btnCompute = document.getElementById('btn-compute-route');
        const btnClear = document.getElementById('btn-clear-route');

        if (btnSetStart) {
            btnSetStart.addEventListener('click', () => {
                this.pinMode = 'start';
                btnSetStart.textContent = 'Click on map...';
                btnSetStart.style.borderColor = '#10b981';
            });
        }

        if (btnSetDest) {
            btnSetDest.addEventListener('click', () => {
                this.pinMode = 'dest';
                btnSetDest.textContent = 'Click on map...';
                btnSetDest.style.borderColor = '#ef4444';
            });
        }

        if (btnCompute) {
            btnCompute.addEventListener('click', () => {
                this.computeRoute();
            });
        }

        if (btnClear) {
            btnClear.addEventListener('click', () => {
                this.clearRoute();
            });
        }

        // Preset Missions
        const p1 = document.getElementById('preset-mission-1');
        const p2 = document.getElementById('preset-mission-2');
        const p3 = document.getElementById('preset-mission-3');

        if (p1) {
            p1.addEventListener('click', () => {
                this.setStart(18.4446, 77.4509, "Perseverance Touchdown");
                this.setEnd(18.4350, 77.4150, "Western Delta Scarp");
                this.computeRoute();
            });
        }

        if (p2) {
            p2.addEventListener('click', () => {
                this.setStart(18.4350, 77.4150, "Western Delta Scarp");
                this.setEnd(18.4800, 77.3700, "Belva Impact Crater");
                this.computeRoute();
            });
        }

        if (p3) {
            p3.addEventListener('click', () => {
                this.setStart(18.4446, 77.4509, "Perseverance Touchdown");
                this.setEnd(18.4100, 77.4000, "Kodiak Butte");
                this.computeRoute();
            });
        }
    }

    handleMapClick(lat, lon) {
        if (this.pinMode === 'start') {
            this.setStart(lat, lon);
            this.pinMode = null;
            const btn = document.getElementById('btn-set-start');
            if (btn) {
                btn.textContent = 'Pin Start (A)';
                btn.style.borderColor = '';
            }
            return true;
        } else if (this.pinMode === 'dest') {
            this.setEnd(lat, lon);
            this.pinMode = null;
            const btn = document.getElementById('btn-set-dest');
            if (btn) {
                btn.textContent = 'Pin Goal (B)';
                btn.style.borderColor = '';
            }
            return true;
        }
        return false;
    }

    setStart(lat, lon, label = null) {
        this.startPoint = { lat, lon };
        document.getElementById('start-coord-text').textContent = 
            label ? `${label} (${lat.toFixed(4)}°, ${lon.toFixed(4)}°)` : `${lat.toFixed(6)}° N, ${lon.toFixed(6)}° E`;

        if (this.startMarker) {
            this.startMarker.setLatLng([lat, lon]);
        } else {
            const iconA = L.divIcon({
                html: `<div style="background: #10b981; border: 2px solid #fff; color: #fff; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11px; box-shadow: 0 0 10px #10b981;">A</div>`,
                className: 'route-marker-a',
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            });
            this.startMarker = L.marker([lat, lon], { icon: iconA }).addTo(this.map);
        }
    }

    setEnd(lat, lon, label = null) {
        this.endPoint = { lat, lon };
        document.getElementById('end-coord-text').textContent = 
            label ? `${label} (${lat.toFixed(4)}°, ${lon.toFixed(4)}°)` : `${lat.toFixed(6)}° N, ${lon.toFixed(6)}° E`;

        if (this.endMarker) {
            this.endMarker.setLatLng([lat, lon]);
        } else {
            const iconB = L.divIcon({
                html: `<div style="background: #ef4444; border: 2px solid #fff; color: #fff; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11px; box-shadow: 0 0 10px #ef4444;">B</div>`,
                className: 'route-marker-b',
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            });
            this.endMarker = L.marker([lat, lon], { icon: iconB }).addTo(this.map);
        }
    }

    computeRoute() {
        if (!this.startPoint || !this.endPoint) {
            alert("Please designate both a Start location (A) and Destination (B).");
            return;
        }

        const btn = document.getElementById('btn-compute-route');
        if (btn) btn.textContent = 'Calculating A*...';

        fetch('/api/route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_lat: this.startPoint.lat,
                start_lon: this.startPoint.lon,
                end_lat: this.endPoint.lat,
                end_lon: this.endPoint.lon
            })
        })
        .then(res => res.json())
        .then(data => {
            if (btn) btn.innerHTML = `
                <svg class="btn-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,6V11H6V13H11V18H13V13H18V11H13V6H11Z"/></svg>
                Plan Safe Route (A*)
            `;

            if (!data.success) {
                alert(`Routing Warning: ${data.error}`);
                return;
            }

            this.displayRouteResults(data);
        })
        .catch(err => {
            console.error("Routing request error:", err);
            if (btn) btn.textContent = 'Plan Safe Route (A*)';
            alert("Routing computation failed. Please ensure both points are inside Jezero Crater.");
        });
    }

    displayRouteResults(data) {
        // Clear previous polylines
        if (this.routePolyline) this.map.removeLayer(this.routePolyline);
        if (this.straightPolyline) this.map.removeLayer(this.straightPolyline);
        this.waypointMarkers.clearLayers();

        // 1. Draw Direct straight line (dashed gray)
        const straightCoords = data.straight_samples.map(s => [s.lat, s.lon]);
        this.straightPolyline = L.polyline(straightCoords, {
            color: '#64748b',
            weight: 2,
            dashArray: '6, 6',
            opacity: 0.7
        }).addTo(this.map);

        // 2. Draw A* Proposed Route (glowing orange)
        const routeCoords = data.waypoints.map(w => [w.lat, w.lon]);
        this.routePolyline = L.polyline(routeCoords, {
            color: '#ff643d',
            weight: 4,
            opacity: 0.95
        }).addTo(this.map);

        // Fit map bounds to encompass the route
        this.map.fitBounds(this.routePolyline.getBounds(), { padding: [50, 50] });

        // Populate Telemetry HUD
        const s = data.summary;
        document.getElementById('route-results-card').style.display = 'block';
        document.getElementById('r-dist-val').textContent = `${s.total_distance_km} km`;
        document.getElementById('r-straight-dist').textContent = `${s.straight_distance_km} km`;
        document.getElementById('r-max-slope').textContent = `${s.max_slope_deg}°`;
        document.getElementById('r-straight-slope').textContent = `${s.straight_max_slope_deg}°`;
        document.getElementById('r-elev-gain').textContent = `+${s.elevation_gain_m} m`;
        document.getElementById('r-elev-loss').textContent = `-${s.elevation_loss_m} m`;

        // Safety badge
        const badge = document.getElementById('route-safety-badge');
        badge.textContent = `${s.safety_badge.toUpperCase()} TRAVERSAL`;
        badge.className = 'badge';
        if (s.safety_badge === 'Safe') badge.classList.add('safe');
        else if (s.safety_badge === 'Moderate') badge.classList.add('caution');
        else badge.classList.add('high');

        document.getElementById('route-waypoints-badge').textContent = `${data.waypoints.length} Waypoints`;

        // Render Canvas Profile Chart
        this.analysis.renderProfileChart(data.waypoints, data.straight_samples);

        // Switch active tab to routing tab
        const routeTabBtn = document.querySelector('[data-tab="tab-routing"]');
        if (routeTabBtn) routeTabBtn.click();
    }

    clearRoute() {
        if (this.startMarker) {
            this.map.removeLayer(this.startMarker);
            this.startMarker = null;
        }
        if (this.endMarker) {
            this.map.removeLayer(this.endMarker);
            this.endMarker = null;
        }
        if (this.routePolyline) {
            this.map.removeLayer(this.routePolyline);
            this.routePolyline = null;
        }
        if (this.straightPolyline) {
            this.map.removeLayer(this.straightPolyline);
            this.straightPolyline = null;
        }
        this.waypointMarkers.clearLayers();
        this.startPoint = null;
        this.endPoint = null;

        document.getElementById('start-coord-text').textContent = 'Click map or set landmark';
        document.getElementById('end-coord-text').textContent = 'Click map or set landmark';
        document.getElementById('route-results-card').style.display = 'none';
    }
}
