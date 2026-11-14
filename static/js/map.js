/**
 * Martian Terrain Explorer - Main Application Entrypoint
 * Initializes Leaflet map, tabs, telemetry handlers, and coordinates HUD.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Exact geographic bounding box of the uploaded GeoTIFF
    // Lat: [18.211027, 18.721194], Lon: [77.160465, 77.699178]
    const jezeroBounds = [
        [18.211027, 77.160465], // South-West
        [18.721194, 77.699178]  // North-East
    ];

    const centerLat = 18.4446; // Centered near Perseverance Touchdown
    const centerLon = 77.4509;

    // Initialize Leaflet Map
    const map = L.map('mars-map', {
        center: [centerLat, centerLon],
        zoom: 12,
        minZoom: 10,
        maxZoom: 18,
        maxBounds: jezeroBounds,
        maxBoundsViscosity: 0.8,
        attributionControl: false
    });

    // Custom Scale Bar
    L.control.scale({ imperial: false, metric: true, position: 'bottomleft' }).addTo(map);

    // Initialize Managers
    const layerManager = new MarsLayerManager(map, jezeroBounds);
    const analysisManager = new MarsAnalysisManager(map);
    const routingManager = new MarsRoutingManager(map, analysisManager);

    // Live Coordinates HUD Tracker
    const hudLat = document.getElementById('hud-lat');
    const hudLon = document.getElementById('hud-lon');

    map.on('mousemove', (e) => {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;
        if (hudLat && hudLon) {
            hudLat.textContent = `${lat.toFixed(6)}° N`;
            hudLon.textContent = `${lon.toFixed(6)}° E`;
        }
    });

    // Map Click Handler: Dispatches between Route Pinning or Point Telemetry Inspection
    map.on('click', (e) => {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;

        // Check if routing manager is actively waiting for a pin
        const handledByRouting = routingManager.handleMapClick(lat, lon);
        if (!handledByRouting) {
            // Inspect clicked location
            analysisManager.inspectPoint(lat, lon);
            
            // Switch to inspector tab to show details
            const inspTabBtn = document.querySelector('[data-tab="tab-inspect"]');
            if (inspTabBtn) inspTabBtn.click();
        }
    });

    // Sidebar Tab Switcher
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            const targetContent = document.getElementById(targetId);
            if (targetContent) targetContent.classList.add('active');
        });
    });

    // Fetch Backend Info & Populate Landmarks
    fetch('/api/info')
        .then(res => res.json())
        .then(data => {
            const btnContainer = document.getElementById('landmark-buttons');
            if (btnContainer && data.landmarks) {
                btnContainer.innerHTML = '';
                data.landmarks.forEach(lm => {
                    // 1. Add map pin
                    layerManager.addLandmarkMarker(lm);

                    // 2. Add quick teleport button
                    const btn = document.createElement('button');
                    btn.className = 'btn-teleport';
                    btn.innerHTML = `<strong>${lm.name}</strong><br><span style="color:#64748b">${lm.type}</span>`;
                    btn.addEventListener('click', () => {
                        map.flyTo([lm.lat, lm.lon], 14, { duration: 1.2 });
                        analysisManager.inspectPoint(lm.lat, lm.lon);
                    });
                    btnContainer.appendChild(btn);
                });
            }

            // Perform initial point inspection at landing site
            analysisManager.inspectPoint(centerLat, centerLon);
        })
        .catch(err => {
            console.error("Failed to load /api/info:", err);
        });

    // Global App Bridge for Popup Button Triggers
    window.marsApp = {
        map: map,
        layers: layerManager,
        analysis: analysisManager,
        routing: routingManager,
        setRoutePointFromLandmark: (id, lat, lon) => {
            if (!routingManager.startPoint) {
                routingManager.setStart(lat, lon, id);
            } else {
                routingManager.setEnd(lat, lon, id);
            }
            const routeTabBtn = document.querySelector('[data-tab="tab-routing"]');
            if (routeTabBtn) routeTabBtn.click();
        }
    };
});
