"""
Tulsa City Council District Data

This file contains district boundary information and representative mappings.
The district boundaries are loaded from real GeoJSON data from the City of Tulsa.

Official Sources:
- District Finder: https://cityoftulsa.maps.arcgis.com/apps/webappviewer/index.html?id=d0d03cae97d348b9a67ed1eff92d6ca0
- Open Tulsa Data Portal: https://www.cityoftulsa.org/government/departments/information-technology/open-tulsa
- City Council: https://www.tulsacouncil.org/councilors

GeoJSON Data:
- Source: Council_Districts.geojson (official Tulsa district boundaries)
- Format: GeoJSON FeatureCollection with Polygon geometries
- Coordinate System: WGS84 (lat/lng)
- Districts: All 9 Tulsa City Council districts included

The boundaries are automatically loaded from the GeoJSON file and used for
accurate district determination using point-in-polygon algorithms.
"""

import json
import os
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

def load_district_boundaries_from_geojson() -> Dict[str, List[Tuple[float, float]]]:
    """
    Load district boundaries from the GeoJSON file.
    
    Returns:
        Dictionary mapping district names to lists of coordinate tuples (lng, lat)
    """
    geojson_path = os.path.join(os.path.dirname(__file__), "Council_Districts.geojson")
    
    if not os.path.exists(geojson_path):
        print(f"Warning: GeoJSON file not found at {geojson_path}")
        return {}
    
    try:
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        boundaries = {}
        
        for feature in geojson_data.get('features', []):
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            district_name = properties.get('NAME', '')
            if not district_name:
                continue
                
            if geometry.get('type') == 'Polygon':
                # Extract coordinates from the polygon
                coordinates = geometry.get('coordinates', [])
                if coordinates:
                    # GeoJSON stores coordinates as [lng, lat] pairs
                    # Convert to list of tuples for easier use
                    boundary_coords = [(coord[0], coord[1]) for coord in coordinates[0]]
                    boundaries[district_name] = boundary_coords
                    
        return boundaries
        
    except Exception as e:
        print(f"Error loading GeoJSON boundaries: {e}")
        return {}

# Load real district boundaries from GeoJSON
DISTRICT_BOUNDARIES = load_district_boundaries_from_geojson()

def get_district_boundaries() -> Dict[str, List[Tuple[float, float]]]:
    """
    Get the current district boundaries.
    
    Returns:
        Dictionary mapping district names to coordinate lists
    """
    return DISTRICT_BOUNDARIES

def get_district_representatives() -> Dict[str, Dict[str, str]]:
    """
    Get the current district representatives.
    
    Returns:
        Dictionary mapping district names to representative info
    """
    return DISTRICT_REPRESENTATIVES
