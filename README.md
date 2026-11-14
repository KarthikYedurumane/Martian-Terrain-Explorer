# Martian Terrain Explorer: Interactive Mars Mapping, Hazard Assessment & Safe Route Planning System

**NASA Space Apps Challenge 2026 Project**  
*Tagline: Explore Mars. Understand Terrain. Plan Safer Routes.*  
*Target Area: Jezero Crater, Mars (NASA Perseverance Rover Landing Site & Exploration Corridor)*

---

## 1. Project Overview

Martian Terrain Explorer is a college-level, full-stack geospatial application built on an actual **NASA MRO Context Camera (CTX)** high-resolution ($6.0\text{ m/pixel}$) GeoTIFF dataset downloaded from NASA Mars Trek.

Rather than a generic map, the application features a forensic raster-processing pipeline, an interactive aerospace-themed Leaflet dashboard, a calibrated NASA MOLA/HRSC Jezero Crater Digital Elevation Model (DEM), autonomous rover hazard classification, and an **A* pathfinding engine** that plots proposed lower-cost rover traverses around hazardous cliff scarps.

---

## 2. Forensic Inspection of Uploaded NASA GeoTIFF

- **Source File**: `data/original/JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif`
- **File Size**: $36,269,402\text{ bytes}$ ($34.59\text{ MB}$)
- **Format**: GeoTIFF (Standard TIFF v42, Little-Endian) with 17 IFD tags and 20 GeoKeys
- **Raster Dimensions**: $5,322 \times 5,040\text{ pixels}$ ($26,822,880\text{ pixels}$)
- **Resolution**: $6.000\text{ m/pixel}$ Ground Sample Distance
- **Coordinate Reference System (CRS)**: **Equirectangular Mars 2000 Sphere IAU**
  - Planetary Radius: $R = 3,396,190.0\text{ meters}$
  - Standard Parallel ($\phi_0$): $0.0^\circ$ | Central Meridian ($\lambda_0$): $0.0^\circ$
- **Geographic Extent**:
  - West Longitude: $77.1605^\circ\text{ E}$ | East Longitude: $77.6992^\circ\text{ E}$
  - South Latitude: $18.2110^\circ\text{ N}$ | North Latitude: $18.7212^\circ\text{ N}$
  - Ground Area: $31.93\text{ km} \times 30.24\text{ km}$ ($965.6\text{ km}^2$)
- **Data Classification**: **Optical Panchromatic Reflectance** (Calibrated albedo, values 1–255).
- **Landmarks Covered**:
  - *Octavia E. Butler Landing (Perseverance Touchdown)*: $18.4446^\circ\text{ N}, 77.4509^\circ\text{ E}$ (Pixel: $X=2869, Y=2733$)
  - *Western Delta Front Scarp*: $18.4350^\circ\text{ N}, 77.4150^\circ\text{ E}$
  - *Kodiak Butte*: $18.4100^\circ\text{ N}, 77.4000^\circ\text{ E}$
  - *Belva Impact Crater*: $18.4800^\circ\text{ N}, 77.3700^\circ\text{ E}$
  - *Neretva Vallis Inflow Gorge*: $18.5500^\circ\text{ N}, 77.2500^\circ\text{ E}$

---

## 3. Windows 11 Step-by-Step Installation & Run Guide

### Step 1: Open Command Prompt or PowerShell
Press `Win + R`, type `cmd` (or `powershell`), and press Enter. Navigate to the project root:
```cmd
cd d:\nasa
```

### Step 2: (Optional) Create and Activate a Python Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
All dependencies are standard open-source libraries:
```cmd
pip install -r requirements.txt
```
*(Dependencies: `Flask>=3.0.0`, `numpy>=2.0.0`, `Pillow>=10.0.0`, `tifffile>=2024.0.0`)*

### Step 4: Run the Automated Unit Tests
Verify all 12 tests for georeferencing, terrain slope, hazard detection, and A* routing:
```cmd
python -m unittest discover -s tests -p "test_*.py" -v
```

### Step 5: Start the Application
```cmd
python app.py
```
Open your web browser (Chrome, Edge, or Firefox) and navigate to:
```
http://127.0.0.1:5000
```

---

## 4. Key Application Features

1. **Interactive Mars Slippy Map**: High-performance multi-resolution CTX imagery with smooth panning, zooming, and live mouse pointer latitude/longitude telemetry.
2. **Scientific Layer Manager**: Toggle CTX optical imagery, NASA MOLA/HRSC DEM topography heatmap, Horn slope gradient, hazard zones, and exploration landmarks.
3. **Point Telemetry Inspector**: Click anywhere on the map to query real-time physical properties:
   - Latitude and Longitude
   - CTX 8-bit optical reflectance
   - Elevation relative to Mars 2000 MOLA datum ($-2,600\text{ m}$ to $-1,600\text{ m}$)
   - Terrain slope in degrees ($\text{Horn gradient}$)
   - Hazard tier (Low: $0-8^\circ$, Medium: $8-15^\circ$, High: $>15^\circ$, Critical: $>25^\circ$)
   - Rover mobility advisory & proximity to geological features
4. **Autonomous A* Safe Route Planner**:
   - Set Start (A) and Goal (B) pins on the map or choose recommended preset rover missions.
   - Computes lower-cost exploration corridors using cost weighting:
     $$\text{Cost} = \text{Distance} \times \left(1.0 + 3.5 \cdot \left(\frac{\text{Slope}}{15^\circ}\right)^2 + \text{Uphill Penalty}\right)$$
   - Avoids impassable cliff faces ($>25^\circ$).
   - Generates route distance vs straight-line distance, elevation gain/loss, max slope comparison, and interactive elevation profile canvas chart.

---

## 5. Team of Six Members: Suggested Work Distribution

| Role # | Member Role | Primary Responsibilities |
| :--- | :--- | :--- |
| **1** | **NASA Data & GIS Lead** | Forensic binary TIFF inspection, CRS validation, GeoTIFF IFD extraction, MOLA/HRSC datum alignment. |
| **2** | **Frontend & UI/UX Designer** | Dark aerospace HUD design, telemetry panels, responsive CSS, typography, icon styling. |
| **3** | **Interactive WebGIS Developer** | Leaflet.js map integration, image overlays, opacity controls, custom projection handling. |
| **4** | **Terrain Analysis & Hazard Engineer** | Horn slope algorithm, 2D gradient matrices, rover safety threshold categorization ($0-8^\circ, 8-15^\circ, >15^\circ$). |
| **5** | **Pathfinding & Algorithm Scientist** | A* pathfinding implementation on 8-connected grid, movement cost formulation, elevation profile generation. |
| **6** | **Backend Integration & QA Lead** | Flask REST API endpoints, automated unit test suite, performance optimization, academic documentation. |

---

## 6. Project Directory Structure

```
Martian-Terrain-Explorer/
├── app.py                      # Flask REST server & routing controller
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide and quick reference
│
├── data/
│   ├── original/               # Preserved uploaded NASA GeoTIFF (unmodified)
│   │   └── JEZ_ctx_B_soc_008_orthoMosaic_6m_Eqc_latTs0_lon0 (1).tif
│   └── processed/              # Optimized web assets (CTX, DEM, Slope, Hazards)
│       ├── jezero_ctx_overview.jpg
│       ├── jezero_dem_overlay.png
│       ├── jezero_slope_overlay.png
│       └── jezero_hazard_overlay.png
│
├── modules/
│   ├── raster_loader.py        # Binary GeoTIFF parser & coordinate transformation
│   ├── raster_processor.py     # Web raster pyramid & tile generation
│   ├── terrain_analysis.py     # Jezero MOLA/HRSC DEM & Horn slope engine
│   ├── hazard_detection.py     # Safety tier classification & hazard proximity
│   └── route_planner.py        # A* pathfinding engine & comparison analysis
│
├── templates/
│   └── index.html              # Scientific dashboard UI
│
├── static/
│   ├── css/
│   │   └── style.css           # Aerospace dark styling
│   └── js/
│       ├── map.js              # Leaflet setup & event handling
│       ├── layers.js           # Multi-layer management & opacity
│       ├── analysis.js         # Point inspection & canvas charting
│       └── routing.js          # A* route planning interface
│
├── tests/                      # Automated unit test suite (12 tests)
│   ├── test_georeference.py
│   ├── test_terrain.py
│   ├── test_routing.py
│   └── test_all_modules.py
│
└── outputs/
    └── reports/
        └── academic_project_report.md  # Complete 18-section academic report
```
