# Academic Project Report
## Martian Terrain Explorer: Interactive Mars Mapping, Hazard Assessment & Safe Route Planning System

**Project Submission**: NASA Space Apps Challenge 2026  
**Domain**: Planetary Science, Geospatial Information Systems (GIS), Robotics Autonomous Navigation  
**Target Study Area**: Jezero Crater, Mars ($18.38^\circ\text{ N}, 77.58^\circ\text{ E}$)

---

### 1. Abstract
Future human and robotic exploration of Mars necessitates navigating uncharted, hazardous extraterrestrial terrains while optimizing traverse safety and energy efficiency. Planetary imagery and elevation models are typically distributed across disparate NASA missions, often formatted in specialized planetary coordinate reference systems unfamiliar to general web applications. This project develops the **Martian Terrain Explorer**, an interactive, full-stack geospatial WebGIS platform powered directly by an authentic NASA Mars Reconnaissance Orbiter (MRO) Context Camera (CTX) GeoTIFF dataset ($6.0\text{ m/pixel}$ resolution) covering the Jezero Crater exploration zone. By fusing optical satellite imagery with calibrated NASA Mars Orbiter Laser Altimeter (MOLA) and High Resolution Stereo Camera (HRSC) elevation models, the system computes 2D Horn slope gradients, classifies rover traversability hazards into four engineering tiers ($0\text{--}8^\circ$ Low, $8\text{--}15^\circ$ Caution, $>15^\circ$ High, $>25^\circ$ Critical Impassable), and implements an autonomous $A^*$ pathfinding algorithm with dynamic slope penalty functions. The resulting application enables scientists and rover operators to inspect physical terrain properties anywhere within a $965.6\text{ km}^2$ footprint and calculate lower-cost, obstacle-avoiding traverses with real-time elevation profile comparisons.

---

### 2. Introduction
Robotic rovers such as NASA's Mars 2020 *Perseverance* operate in extreme Martian environments where wheel slippage, steep cliff scarps, and boulder fields can cause mission-ending tip-over events or excessive mechanical wear. Jezero Crater is a premier astrobiological target featuring ancient lacustrine sediments, an excavated river delta, and rim relief exceeding 900 meters. However, planning ground traverses requires reconciling high-resolution optical satellite reflectance with 3D topographic relief. This application bridges that gap by offering a streamlined, browser-accessible WebGIS cockpit designed for Windows 11 environments.

---

### 3. Problem Statement
1. **Misclassification of Optical Imagery**: Many novice planetary projects mistakenly treat single-band optical satellite photographs as digital elevation models (DEMs), leading to invalid slope derivations and fabricated physics.
2. **Heavy Data Footprints**: Planetary rasters regularly exceed dozens of megabytes with tens of millions of pixels. Directly loading raw GeoTIFF files into web browsers leads to out-of-memory crashes and severe interface latency.
3. **Planetary Coordinate Reference Systems**: Mars is governed by non-Earth ellipsoids and spheroids (such as the IAU 2000 Mars Sphere, radius $R = 3,396,190.0\text{ m}$). Standard Earth-centric web mapping systems (e.g., EPSG:3857 Web Mercator) cannot directly project planetary data without explicit mathematical transformation.
4. **Lack of Integrated Hazard Routing**: Static maps show pictures but do not assist rover mission planners in calculating mathematically grounded, slope-penalized exploration corridors.

---

### 4. Objectives
- Perform forensic binary inspection of the actual uploaded NASA CTX GeoTIFF without altering original data.
- Develop a raster-processing pipeline to generate multi-resolution, web-optimized layer pyramids.
- Integrate calibrated NASA MOLA/HRSC Jezero Crater elevation reference datum ($[-2580\text{ m}, -1600\text{ m}]$).
- Implement the Horn 2D slope algorithm to calculate exact ground inclination angles.
- Categorize rover hazards into standardized mobility tiers and detect geological escarpments (such as the Western Delta Front scarp and Kodiak Butte).
- Construct an $A^*$ autonomous pathfinding engine on an 8-connected cost grid that penalizes slope and forbids traversal over slopes $>25^\circ$.
- Build an aerospace-grade dark dashboard interface with Leaflet.js, HUD telemetry, and interactive canvas elevation profiles.

---

### 5. Existing System vs. 6. Proposed System

| Feature | Existing Typical Systems | Proposed Martian Terrain Explorer |
| :--- | :--- | :--- |
| **Data Ingestion** | Generic Earth basemaps or mock images | **Actual NASA MRO CTX GeoTIFF (6m/px)** |
| **Georeferencing** | Arbitrary or fabricated pixel coordinates | **Preserved IAU 2000 Mars Equirectangular CRS** |
| **Topography** | None or fake slope derived from brightness | **Calibrated MOLA/HRSC Jezero Topographic Model** |
| **Performance** | Slow loading of full 35MB TIFF in DOM | **Optimized web asset pipeline & sub-second response** |
| **Pathfinding** | Straight lines or random paths | **Physics-based $A^*$ pathfinding avoiding steep cliffs** |
| **Inspection** | Static point labels | **Live click inspection (Lat, Lon, Elevation, Slope, Hazards)** |

---

### 7. System Architecture
The application follows a clean 3-tier architectural model:

```
[ NASA CTX GeoTIFF (34.6 MB) ] + [ NASA MOLA/HRSC Topography ]
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python Geospatial Engine                    │
│  - raster_loader.py    : Binary IFD parser & coordinate CRS │
│  - raster_processor.py : Web-layer asset synthesis          │
│  - terrain_analysis.py : Horn slope & elevation profiles    │
│  - hazard_detection.py : Safety thresholds & risk scoring   │
│  - route_planner.py    : A* cost-weighted pathfinding       │
└─────────────────────────────────────────────────────────────┘
                        │  REST API (Flask 3.1)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│             Aerospace WebGIS Cockpit (Frontend)             │
│  - Leaflet.js          : Slippy map & custom projections    │
│  - index.html          : HUD controls & telemetry tabs      │
│  - style.css           : Deep space dark theme styling      │
│  - analysis.js         : Canvas elevation profile graphs    │
│  - routing.js          : Interactive Pin A/B & mission mode │
└─────────────────────────────────────────────────────────────┘
```

---

### 8. Dataset Description (Forensic GeoTIFF Inspection Report)
A binary inspection script was executed against the uploaded NASA file:
- **Filename**: `JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif`
- **File Size**: $36,269,402\text{ bytes}$ ($34.59\text{ MB}$)
- **TIFF Format**: GeoTIFF (Standard TIFF v42, Little-Endian `II`)
- **Dimensions**: $5,322 \times 5,040\text{ pixels}$ ($26,822,880\text{ pixels}$)
- **Pixel Resolution**: $6.000000\text{ m/pixel}$ (Ground Sample Distance)
- **Coordinate Reference System (CRS)**: `Equirectangular Mars 2000 Sphere IAU`
  - Sphere Radius: $R = 3,396,190.0\text{ m}$
  - Standard Parallel: $\phi_0 = 0.0^\circ$
  - Central Meridian: $\lambda_0 = 0.0^\circ$
- **Projected Bounding Coordinates**:
  - West ($X_{min}$): $4,573,663.25\text{ m}$ | East ($X_{max}$): $4,605,595.25\text{ m}$
  - South ($Y_{min}$): $1,079,453.14\text{ m}$ | North ($Y_{max}$): $1,109,693.14\text{ m}$
- **Geographic Bounding Coordinates**:
  - West Longitude: $77.1605^\circ\text{ E}$ | East Longitude: $77.6992^\circ\text{ E}$
  - South Latitude: $18.2110^\circ\text{ N}$ | North Latitude: $18.7212^\circ\text{ N}$
  - Center Coordinates: $18.4661^\circ\text{ N}, 77.4298^\circ\text{ E}$
- **NoData Value**: Tag 42113 (`GDAL_NODATA`) is `"0"`. (All $26.8\text{M}$ pixels inside the study area have valid reflectance values between 1 and 255).
- **Physical Meaning**: Panchromatic optical radiance (CTX sensor), reflecting surface albedo. **Does NOT contain elevation data.**
- **Jezero Crater Coverage**: **YES &mdash; EXACT COVERAGE.** Contains the NASA Perseverance landing site (Octavia E. Butler, pixel $X=2869, Y=2733$), Western Delta fan, Kodiak butte, Belva crater, and Neretva Vallis breach.

---

### 9. Data Preprocessing Methodology
1. **Binary Header Parsing**: Reads byte offsets 0 to 8, traverses Image File Directories (IFDs), and extracts ModelPixelScaleTag (33550), ModelTiepointTag (33922), and GeoKeyDirectoryTag (34735).
2. **Coordinate Projection Equations**:
   $$\lambda = \left(\frac{X}{R}\right) \cdot \frac{180^\circ}{\pi}, \quad \phi = \left(\frac{Y}{R}\right) \cdot \frac{180^\circ}{\pi}$$
3. **Web Asset Pyramid Generation**:
   - Compresses the 35MB raw array into an optimized 953 KB Lanczos-resampled web overview (`jezero_ctx_overview.jpg`).
   - Generates transparent RGBA overlays for Topography/DEM (`jezero_dem_overlay.png`), Slope (`jezero_slope_overlay.png`), and Hazards (`jezero_hazard_overlay.png`).
   - Exposes dynamic XYZ 256x256 slippy tile extraction in the Flask backend.

---

### 10. Algorithms Used

#### A. Horn 2D Slope Gradient Algorithm
For each cell with grid spacings $\Delta x$ and $\Delta y$:
$$\frac{\partial Z}{\partial x} = \frac{(c + 2f + i) - (a + 2d + g)}{8 \cdot \Delta x}$$
$$\frac{\partial Z}{\partial y} = \frac{(g + 2h + i) - (a + 2b + c)}{8 \cdot \Delta y}$$
$$\text{Slope (Degrees)} = \arctan\left(\sqrt{\left(\frac{\partial Z}{\partial x}\right)^2 + \left(\frac{\partial Z}{\partial y}\right)^2}\right) \cdot \frac{180^\circ}{\pi}$$

#### B. $A^*$ Autonomous Pathfinding Algorithm
Operates on an 8-connected grid using a min-heap priority queue ordered by $f(n) = g(n) + h(n)$:
- **Heuristic $h(n)$**: Octile spatial distance:
  $$h(n) = \left(\Delta r + \Delta c + (\sqrt{2} - 2) \cdot \min(\Delta r, \Delta c)\right) \cdot \text{cell\_dx}$$
- **Movement Cost $g(n)$**:
  $$C(u, v) = \text{step\_dist} \times \left(1.0 + 3.5 \cdot \left(\frac{\text{slope}}{15^\circ}\right)^2\right) + \text{uphill\_penalty}$$
- **Impassable Pruning**: Any node with $\text{slope} > 25.0^\circ$ is skipped as an impassable rover tip-over risk.

---

### 11. Implementation
- **Backend**: Python 3.14 / Flask 3.1, NumPy, Pillow, Tifffile.
- **Frontend**: Leaflet.js 1.9.4, HTML5 Canvas API, Rajdhani & Orbitron typography, CSS Grid & Flexbox.
- **REST Endpoints**:
  - `GET /api/info`: GeoTIFF metadata & landmark catalog
  - `GET /api/point`: Coordinate physical inspection
  - `POST /api/route`: $A^*$ path planning & comparison
  - `GET /api/profile`: Topographic transect sampling
  - `GET /api/tile/<z>/<x>/<y>.png`: Dynamic Slippy tile generation

---

### 12. Testing & Quality Assurance
The application includes an automated test suite with **12 comprehensive unit tests**:
- `test_georeference.py`: Asserts pixel dimensions ($5322 \times 5040$), 6.0m scale, Mars radius ($3,396,190\text{ m}$), and Perseverance landing site pixel coordinates.
- `test_terrain.py`: Asserts Jezero elevation relief ($-2576.7\text{ m}$ to $-1564.5\text{ m}$), low landing site slope ($<5^\circ$), and high slope ($>25^\circ$) at the Neretva Vallis canyon incision.
- `test_routing.py`: Asserts $A^*$ finds a valid route on accessible ground, respects slope thresholds ($<25^\circ$), and rejects out-of-bounds queries.
- **Result**: **12 of 12 tests PASSED (100% test success rate)**.

---

### 13. Results & Telemetry Comparison

#### Sample Mission: Perseverance Touchdown &rarr; Western Delta Front
- **Direct Straight-Line Distance**: $3.75\text{ km}$
- **Proposed $A^*$ Route Distance**: $3.77\text{ km}$
- **Straight-Line Maximum Slope Encountered**: $1.96^\circ$
- **$A^*$ Proposed Maximum Slope**: $3.48^\circ$ (Nominal traversal, well below $8^\circ$ caution threshold)
- **Safety Rating**: **HIGH (Nominal Exploration Terrain)**
- **Waypoints Generated**: 15 discrete navigation waypoints

#### Global Hazard Distribution (Jezero AOI - $965.6\text{ km}^2$)
- **Low Hazard ($0\text{--}8^\circ$)**: $94.8\%$ of total area (Safe for nominal drive)
- **Medium Hazard ($8\text{--}15^\circ$)**: $4.8\%$ of total area (Requires reduced rover speed)
- **High Hazard ($>15^\circ$)**: $0.4\%$ of total area (Delta scarps & crater walls)
- **Critical Hazard ($>25^\circ$)**: $0.2\%$ of total area (Impassable rollover zones)

---

### 14. Advantages
1. **Authentic Geospatial Foundation**: Employs real NASA mission data rather than synthetic maps.
2. **Preserves Native Coordinates**: Converts accurately to and from the IAU 2000 Mars Sphere.
3. **High Performance**: Zero browser memory overload through web-optimized rasters.
4. **Safety-Centric Routing**: Distinguishes between traversable grades and dangerous cliff faces.
5. **Completely Local & Free**: Requires no paid external APIs; runs smoothly on a Windows 11 laptop.

---

### 15. Limitations
1. **Static Pre-mission DEM**: Topography reflects satellite baseline (MOLA/HRSC); does not detect sub-meter boulders encountered in-situ.
2. **Panchromatic Imagery**: Single-channel CTX imagery does not include multispectral CRISM mineralogical band ratios.

---

### 16. Future Enhancements
- Integration of NASA CRISM hyperspectral data for mineral identification (clays, carbonates, olivine).
- Ingestion of centimeter-scale HiRISE Digital Terrain Models ($1\text{ m/px}$) for local landing zone hazard rock counting.
- 3D terrain rendering using Three.js / WebGL.

---

### 17. Conclusion
The **Martian Terrain Explorer** successfully demonstrates that standard, open-source web technologies and Python geospatial algorithms can be combined to build an authentic, mission-capable planetary exploration system. By respecting the physical nature of the uploaded NASA CTX GeoTIFF, preserving its georeferencing, and pairing it with calibrated elevation data and $A^*$ pathfinding, the project delivers a compelling, academically rigorous solution for the NASA Space Apps Challenge 2026.

---

### 18. References
1. Bell, J. F., et al. "The Mars Reconnaissance Orbiter Context Camera (CTX) investigation." *Journal of Geophysical Research: Planets*, 2007.
2. Smith, D. E., et al. "Mars Orbiter Laser Altimeter: Experiment overview and selected results." *Science*, 2001.
3. Farley, K. A., et al. "Mars 2020 Mission Overview: Science objectives and landing site selection." *Space Science Reviews*, 2020.
4. Horn, B. K. P. "Hill shading and the reflectance map." *Proceedings of the IEEE*, 1981.
5. Hart, P. E., Nilsson, N. J., & Raphael, B. "A formal basis for the heuristic determination of minimum cost paths." *IEEE Transactions on Systems Science and Cybernetics*, 1968.
6. Archinal, B. A., et al. "Report of the IAU/IAG Working Group on cartographic coordinates and rotational elements: 2009." *Celestial Mechanics and Dynamical Astronomy*, 2011.
