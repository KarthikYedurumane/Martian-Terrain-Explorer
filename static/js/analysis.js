/**
 * Martian Terrain Explorer - Analysis & Telemetry Module
 * Handles point inspection queries and elevation profile canvas charting.
 */

class MarsAnalysisManager {
    constructor(map) {
        this.map = map;
        this.inspectMarker = null;
        this.chartCanvas = document.getElementById('routeProfileChart');
    }

    inspectPoint(lat, lon, zoomTo = false) {
        if (zoomTo) {
            this.map.panTo([lat, lon]);
        }

        // Update inspector marker
        if (this.inspectMarker) {
            this.inspectMarker.setLatLng([lat, lon]);
        } else {
            const pinIcon = L.divIcon({
                html: `<div style="
                    background: #06b6d4; 
                    border: 2px solid #fff; 
                    width: 12px; 
                    height: 12px; 
                    border-radius: 50%;
                    box-shadow: 0 0 12px #06b6d4;"></div>`,
                className: 'inspect-pin',
                iconSize: [12, 12],
                iconAnchor: [6, 6]
            });
            this.inspectMarker = L.marker([lat, lon], { icon: pinIcon }).addTo(this.map);
        }

        // Fetch physical point data from backend
        fetch(`/api/point?lat=${lat}&lon=${lon}`)
            .then(res => res.json())
            .then(data => {
                this.updateInspectorUI(data);
            })
            .catch(err => {
                console.error("Point inspection failed:", err);
            });
    }

    updateInspectorUI(data) {
        if (!data.is_inside) {
            return;
        }

        document.getElementById('insp-lat').textContent = `${data.lat.toFixed(6)}° N`;
        document.getElementById('insp-lon').textContent = `${data.lon.toFixed(6)}° E`;
        document.getElementById('insp-pixel').textContent = data.ctx_reflectance !== null ? `${data.ctx_reflectance} / 255` : 'N/A';
        document.getElementById('insp-elev').textContent = data.elevation_m !== null ? `${data.elevation_m.toLocaleString()} m` : 'N/A';
        document.getElementById('insp-slope').textContent = `${data.slope_deg}°`;
        
        // Hazard badge
        const badge = document.getElementById('insp-hazard-tier');
        badge.textContent = `${data.hazard_level.toUpperCase()} HAZARD`;
        badge.className = 'hazard-badge';
        if (data.hazard_level === 'Low') badge.classList.add('safe');
        else if (data.hazard_level === 'Medium') badge.classList.add('caution');
        else badge.classList.add('high');

        document.getElementById('insp-mobility').textContent = data.rover_mobility;
        document.getElementById('insp-desc').textContent = data.risk_description;

        if (data.nearest_landmark) {
            document.getElementById('insp-nearest').textContent = `${data.nearest_landmark.name} (${data.nearest_landmark.distance_km} km)`;
        } else {
            document.getElementById('insp-nearest').textContent = 'None nearby';
        }
    }

    renderProfileChart(astarSamples, straightSamples) {
        if (!this.chartCanvas) return;
        const ctx = this.chartCanvas.getContext('2d');
        const w = this.chartCanvas.width;
        const h = this.chartCanvas.height;

        // Clear canvas
        ctx.clearRect(0, 0, w, h);

        // Find min and max elevations
        const astarElevs = astarSamples.map(s => s.elevation_m);
        const straightElevs = straightSamples.map(s => s.elevation_m);
        const allElevs = [...astarElevs, ...straightElevs];

        const minE = Math.min(...allElevs);
        const maxE = Math.max(...allElevs);
        const range = Math.max(10.0, maxE - minE);

        const padLeft = 40;
        const padRight = 10;
        const padTop = 15;
        const padBottom = 25;

        const chartW = w - padLeft - padRight;
        const chartH = h - padTop - padBottom;

        // Grid lines
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 1;
        ctx.fillStyle = '#64748b';
        ctx.font = '10px JetBrains Mono';

        // Draw 3 horizontal grid lines
        for (let i = 0; i <= 2; i++) {
            const y = padTop + (chartH / 2) * i;
            ctx.beginPath();
            ctx.moveTo(padLeft, y);
            ctx.lineTo(w - padRight, y);
            ctx.stroke();

            const elevVal = Math.round(maxE - (range / 2) * i);
            ctx.fillText(`${elevVal}m`, 4, y + 3);
        }

        // Draw straight-line profile (gray dashed)
        if (straightElevs.length > 1) {
            ctx.beginPath();
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = '#64748b';
            ctx.lineWidth = 1.5;

            for (let i = 0; i < straightElevs.length; i++) {
                const x = padLeft + (i / (straightElevs.length - 1)) * chartW;
                const y = padTop + (1.0 - (straightElevs[i] - minE) / range) * chartH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Draw A* proposed route profile (orange solid)
        if (astarElevs.length > 1) {
            ctx.beginPath();
            ctx.strokeStyle = '#ff643d';
            ctx.lineWidth = 2.5;

            for (let i = 0; i < astarElevs.length; i++) {
                const x = padLeft + (i / (astarElevs.length - 1)) * chartW;
                const y = padTop + (1.0 - (astarElevs[i] - minE) / range) * chartH;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        // Bottom distance labels
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('Start', padLeft, h - 6);
        ctx.fillText('Destination', w - padRight - 55, h - 6);
    }
}
