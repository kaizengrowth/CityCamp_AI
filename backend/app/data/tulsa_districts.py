"""
Tulsa City Council District Data

This file contains district boundary information and representative mappings.
In production, this would be loaded from:
1. Tulsa's ArcGIS REST Services
2. Local GeoJSON files downloaded from City of Tulsa Open Data Portal
3. PostGIS database with current boundary data

Official Sources:
- District Finder: https://cityoftulsa.maps.arcgis.com/apps/webappviewer/index.html?id=d0d03cae97d348b9a67ed1eff92d6ca0
- Open Tulsa Data Portal: https://www.cityoftulsa.org/government/departments/information-technology/open-tulsa
- City Council: https://www.tulsacouncil.org/councilors
"""

from typing import Dict, List, Tuple

# District Representative Information (Updated with current 2025 officials)
DISTRICT_REPRESENTATIVES = {
    "District 1": {
        "name": "Vanessa Hall-Harper",
        "email": "dist1@tulsacouncil.org",
        "phone": "(918) 596-1921",
        "position": "City Councilor - District 1",
    },
    "District 2": {
        "name": "Anthony Archie",
        "email": "dist2@tulsacouncil.org",
        "phone": "(918) 596-1922",
        "position": "City Councilor - District 2",
    },
    "District 3": {
        "name": "Jackie Dutton",
        "email": "dist3@tulsacouncil.org",
        "phone": "(918) 596-1923",
        "position": "City Councilor - District 3",
    },
    "District 4": {
        "name": "Laura Bellis",
        "email": "dist4@tulsacouncil.org",
        "phone": "(918) 596-1924",
        "position": "City Councilor - District 4",
    },
    "District 5": {
        "name": "Karen Gilbert",
        "email": "dist5@tulsacouncil.org",
        "phone": "(918) 596-1925",
        "position": "City Councilor - District 5 (Vice Chair)",
    },
    "District 6": {
        "name": "Christian Bengel",
        "email": "dist6@tulsacouncil.org",
        "phone": "(918) 596-1926",
        "position": "City Councilor - District 6",
    },
    "District 7": {
        "name": "Lori Decter Wright",
        "email": "dist7@tulsacouncil.org",
        "phone": "(918) 596-1927",
        "position": "City Councilor - District 7",
    },
    "District 8": {
        "name": "Phil Lakin Jr.",
        "email": "dist8@tulsacouncil.org",
        "phone": "(918) 596-1928",
        "position": "City Councilor - District 8 (Chair)",
    },
    "District 9": {
        "name": "Carol Bush",
        "email": "dist9@tulsacouncil.org",
        "phone": "(918) 596-1929",
        "position": "City Councilor - District 9",
    },
}

# Simplified district boundaries (lat, lng coordinates)
# These are PLACEHOLDER boundaries - replace with actual data from Tulsa's ArcGIS
# Real boundaries would be complex polygons with hundreds of coordinate points
DISTRICT_BOUNDARIES = {
    "District 1": [
        # North Tulsa - approximate boundaries
        (-95.999, 36.200),
        (-95.950, 36.200),
        (-95.950, 36.170),
        (-95.999, 36.170),
        (-95.999, 36.200),  # Close polygon
    ],
    "District 2": [
        # Northwest Tulsa - approximate boundaries
        (-96.050, 36.170),
        (-95.999, 36.170),
        (-95.999, 36.130),
        (-96.050, 36.130),
        (-96.050, 36.170),
    ],
    "District 3": [
        # West Tulsa - approximate boundaries
        (-96.050, 36.130),
        (-95.999, 36.130),
        (-95.999, 36.090),
        (-96.050, 36.090),
        (-96.050, 36.130),
    ],
    "District 4": [
        # Southwest Tulsa - approximate boundaries
        (-96.000, 36.090),
        (-95.950, 36.090),
        (-95.950, 36.050),
        (-96.000, 36.050),
        (-96.000, 36.090),
    ],
    "District 5": [
        # Central Tulsa - approximate boundaries
        (-95.950, 36.170),
        (-95.900, 36.170),
        (-95.900, 36.130),
        (-95.950, 36.130),
        (-95.950, 36.170),
    ],
    "District 6": [
        # East Tulsa - approximate boundaries
        (-95.900, 36.130),
        (-95.850, 36.130),
        (-95.850, 36.090),
        (-95.900, 36.090),
        (-95.900, 36.130),
    ],
    "District 7": [
        # Midtown - approximate boundaries
        (-95.950, 36.130),
        (-95.900, 36.130),
        (-95.900, 36.090),
        (-95.950, 36.090),
        (-95.950, 36.130),
    ],
    "District 8": [
        # South Tulsa - approximate boundaries
        (-95.950, 36.050),
        (-95.900, 36.050),
        (-95.900, 36.010),
        (-95.950, 36.010),
        (-95.950, 36.050),
    ],
    "District 9": [
        # Southeast Tulsa - approximate boundaries
        (-95.900, 36.090),
        (-95.850, 36.090),
        (-95.850, 36.050),
        (-95.900, 36.050),
        (-95.900, 36.090),
    ],
}

# ZIP Code to District Mapping (approximate)
# This provides a fallback when exact geocoding fails
ZIP_TO_DISTRICT = {
    # North Tulsa
    "74126": "District 1",
    "74106": "District 1",
    "74108": "District 1",
    # Northwest
    "74127": "District 2",
    "74110": "District 2",
    # West Tulsa
    "74107": "District 3",
    "74128": "District 3",
    # Southwest
    "74132": "District 4",
    "74133": "District 4",
    # Central
    "74103": "District 5",
    "74120": "District 5",
    # East
    "74115": "District 6",
    "74129": "District 6",
    # Midtown
    "74104": "District 7",
    "74114": "District 7",
    "74119": "District 7",
    # South Tulsa
    "74135": "District 8",
    "74136": "District 8",
    "74137": "District 8",
    # Southeast
    "74105": "District 9",
    "74112": "District 9",
}

# ArcGIS REST Service URLs (to be verified/updated)
ARCGIS_SERVICES = {
    "district_boundaries": "https://services.arcgis.com/.../FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson",
    "city_limits": "https://services.arcgis.com/.../FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson",
}

# Instructions for updating boundary data
UPDATE_INSTRUCTIONS = """
To update with real Tulsa district boundaries:

1. Access Tulsa's ArcGIS REST Services:
   - Visit: https://cityoftulsa.maps.arcgis.com/
   - Find the district boundaries layer
   - Extract the REST service URL

2. Download GeoJSON data:
   - Use the service URL with f=geojson parameter
   - Save to backend/app/data/tulsa_districts.geojson

3. Update DISTRICT_BOUNDARIES with real coordinate data:
   - Parse the GeoJSON file
   - Convert to Shapely Polygon objects
   - Replace placeholder coordinates

4. Verify representative information:
   - Check https://www.tulsacouncil.org/councilors
   - Update DISTRICT_REPRESENTATIVES as needed
"""
