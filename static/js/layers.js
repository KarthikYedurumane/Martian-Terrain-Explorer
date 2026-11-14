/**
 * Martian Terrain Explorer - Layer Management
 * Manages Leaflet image overlays and layer opacity controls.
 */

class MarsLayerManager {
    constructor(map, bounds) {
        this.map = map;
        this.bounds = bounds;
        
        // Define Image Overlays
        this.layers = {
            ctx: L.imageOverlay('/processed/jezero_ctx_overview.jpg', this.bounds, {
                opacity: 1.0,
                zIndex: 10,
                interactive: false
            }),
            dem: L.imageOverlay('/processed/jezero_dem_overlay.png', this.bounds, {
                opacity: 0.7,
                zIndex: 20,
                interactive: false
            }),
            slope: L.imageOverlay('/processed/jezero_slope_overlay.png', this.bounds, {
                opacity: 0.65,
                zIndex: 30,
                interactive: false
            }),
            hazards: L.imageOverlay('/processed/jezero_hazard_overlay.png', this.bounds, {
                opacity: 0.8,
                zIndex: 40,
                interactive: false
            }),
            landmarks: L.layerGroup()
        };

        // Add default active layers to map
        this.layers.ctx.addTo(this.map);
        this.layers.hazards.addTo(this.map);
        this.layers.landmarks.addTo(this.map);

        this.initControls();
    }

    initControls() {
        // CTX Layer Toggle & Opacity
        const ctxCheck = document.getElementById('layer-ctx');
        const ctxSlider = document.getElementById('opacity-ctx');
        if (ctxCheck) {
            ctxCheck.addEventListener('change', (e) => {
                if (e.target.checked) this.layers.ctx.addTo(this.map);
                else this.map.removeLayer(this.layers.ctx);
            });
        }
        if (ctxSlider) {
            ctxSlider.addEventListener('input', (e) => {
                this.layers.ctx.setOpacity(e.target.value / 100.0);
            });
        }

        // DEM Layer Toggle & Opacity
        const demCheck = document.getElementById('layer-dem');
        const demSlider = document.getElementById('opacity-dem');
        if (demCheck) {
            demCheck.addEventListener('change', (e) => {
                if (e.target.checked) this.layers.dem.addTo(this.map);
                else this.map.removeLayer(this.layers.dem);
            });
        }
        if (demSlider) {
            demSlider.addEventListener('input', (e) => {
                this.layers.dem.setOpacity(e.target.value / 100.0);
            });
        }

        // Slope Layer Toggle & Opacity
        const slopeCheck = document.getElementById('layer-slope');
        const slopeSlider = document.getElementById('opacity-slope');
        if (slopeCheck) {
            slopeCheck.addEventListener('change', (e) => {
                if (e.target.checked) this.layers.slope.addTo(this.map);
                else this.map.removeLayer(this.layers.slope);
            });
        }
        if (slopeSlider) {
            slopeSlider.addEventListener('input', (e) => {
                this.layers.slope.setOpacity(e.target.value / 100.0);
            });
        }

        // Hazards Layer Toggle & Opacity
        const hazCheck = document.getElementById('layer-hazards');
        const hazSlider = document.getElementById('opacity-hazards');
        if (hazCheck) {
            hazCheck.addEventListener('change', (e) => {
                if (e.target.checked) this.layers.hazards.addTo(this.map);
                else this.map.removeLayer(this.layers.hazards);
            });
        }
        if (hazSlider) {
            hazSlider.addEventListener('input', (e) => {
                this.layers.hazards.setOpacity(e.target.value / 100.0);
            });
        }

        // Landmarks Layer Toggle
        const landCheck = document.getElementById('layer-landmarks');
        if (landCheck) {
            landCheck.addEventListener('change', (e) => {
                if (e.target.checked) this.layers.landmarks.addTo(this.map);
                else this.map.removeLayer(this.layers.landmarks);
            });
        }
    }

    addLandmarkMarker(lm, onClick) {
        const iconHtml = `<div style="
            background: #ff643d; 
            border: 2px solid #fff; 
            width: 14px; 
            height: 14px; 
            border-radius: 50%;
            box-shadow: 0 0 10px #ff643d;"></div>`;
            
        const customIcon = L.divIcon({
            html: iconHtml,
            className: 'mars-landmark-pin',
            iconSize: [14, 14],
            iconAnchor: [7, 7]
        });

        const marker = L.marker([lm.lat, lm.lon], { icon: customIcon });
        
        const popupContent = `
            <div style="font-family: 'Rajdhani', sans-serif; padding: 4px;">
                <h4 style="color: #ff643d; margin: 0 0 4px 0; font-size: 14px; font-weight: 700;">${lm.name}</h4>
                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
                    Lat: ${lm.lat.toFixed(4)}°N | Lon: ${lm.lon.toFixed(4)}°E
                </div>
                <p style="font-size: 12px; margin: 0 0 8px 0; line-height: 1.3;">${lm.description}</p>
                <button onclick="window.marsApp.setRoutePointFromLandmark('${lm.id}', ${lm.lat}, ${lm.lon})" 
                    style="background: #1e293b; border: 1px solid #334155; color: #06b6d4; padding: 4px 8px; border-radius: 3px; font-size: 11px; cursor: pointer;">
                    Set as Route Point
                </button>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        this.layers.landmarks.addLayer(marker);
    }
}
