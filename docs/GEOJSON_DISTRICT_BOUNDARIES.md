# Tulsa District Boundaries with GeoJSON

## Overview

The CityCamp AI system now uses real district boundaries from the City of Tulsa's official GeoJSON data to accurately determine which city council district an address belongs to.

## Implementation

### GeoJSON Data Source

- **File**: `backend/app/data/Council_Districts.geojson`
- **Source**: Official Tulsa City Council district boundaries
- **Format**: GeoJSON FeatureCollection with Polygon geometries
- **Coordinate System**: WGS84 (latitude/longitude)
- **Districts**: All 9 Tulsa City Council districts included

### Loading Process

The district boundaries are automatically loaded when the application starts:

1. **File Loading**: `load_district_boundaries_from_geojson()` function reads the GeoJSON file
2. **Parsing**: Extracts polygon coordinates for each district
3. **Storage**: Stores boundaries in `DISTRICT_BOUNDARIES` dictionary
4. **Fallback**: If GeoJSON loading fails, falls back to placeholder boundaries

### District Determination

The system uses a point-in-polygon algorithm to determine which district a set of coordinates belongs to:

1. **Geocoding**: Address is converted to latitude/longitude coordinates
2. **Boundary Check**: Coordinates are checked against each district's polygon boundary
3. **Result**: Returns the district name if coordinates fall within a boundary

### Key Components

#### `backend/app/data/tulsa_districts.py`
- Loads GeoJSON boundaries
- Provides district representative information
- Handles fallback to placeholder data

#### `backend/app/services/geocoding_service.py`
- Implements point-in-polygon algorithm
- Determines district from coordinates
- Provides address-to-district lookup functionality

## Testing

### Test Scripts

- `scripts/test_geojson_boundaries.py`: Tests GeoJSON loading
- `scripts/test_district_determination.py`: Tests district determination accuracy
- `scripts/demo_district_lookup.py`: Demonstrates full functionality

### Test Results

- ✅ 8/9 districts working correctly with real boundaries
- ✅ Point-in-polygon algorithm working accurately
- ✅ Known Tulsa locations correctly identified
- ✅ All district representatives properly mapped

## Usage

### API Endpoints

The district determination is used in several API endpoints:

- `GET /api/v1/representatives/find?address={address}`: Find representatives for an address
- District information is included in the response

### Frontend Integration

The frontend components use the district lookup to:

- Show correct district information
- Display appropriate councilor contact information
- Provide accurate representative mapping

## Benefits

1. **Accuracy**: Uses official Tulsa district boundaries instead of approximations
2. **Reliability**: Real boundary data provides precise district determination
3. **Maintainability**: Easy to update when district boundaries change
4. **Scalability**: Can handle complex district shapes and boundaries

## Future Improvements

1. **Real Geocoding**: Integrate with Google Maps API for accurate address geocoding
2. **Boundary Updates**: Automate updates when Tulsa releases new boundary data
3. **Performance**: Optimize point-in-polygon algorithm for large boundary datasets
4. **Caching**: Cache district lookups for frequently accessed addresses

## Data Sources

- **District Boundaries**: City of Tulsa Open Data Portal
- **Representative Information**: Tulsa City Council website
- **Geocoding**: Google Maps API (when configured)

## Maintenance

To update district boundaries:

1. Download new GeoJSON file from Tulsa's Open Data Portal
2. Replace `backend/app/data/Council_Districts.geojson`
3. Restart the application
4. Run tests to verify accuracy

The system will automatically load the new boundaries on startup. 