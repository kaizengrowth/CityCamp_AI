#!/usr/bin/env python3
"""
Test script with correct expected districts based on actual boundary analysis.
"""

import asyncio
import sys
import os

# Change to backend directory to find .env file
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
os.chdir(backend_dir)

# Add the backend directory to the Python path
sys.path.insert(0, backend_dir)

from app.core.config import Settings
from app.services.geocoding_service import GeocodingService


async def test_correct_districts():
    """Test with correct expected districts based on actual boundaries."""
    
    # Initialize the service
    settings = Settings()
    geocoding_service = GeocodingService(settings)
    
    # Test addresses with CORRECT expected districts based on boundary analysis
    test_cases = [
        ("175 E 2nd St, Tulsa, OK", "District 1"),
        ("7129 S Olympia Ave, Tulsa, OK", "District 2"),
        ("1708 N Sheridan Rd, Tulsa, OK", "District 3"),
        ("200 Civic Center, Tulsa, OK", "District 4"),
        ("10934 E 21st St, Tulsa, OK", "District 5"),
        ("14009 E 21st St, Tulsa, OK 74134", "District 6"),
        ("5817 S 118th E Ave, Tulsa, OK", "District 7"),
        ("8104 S Sheridan Rd, Tulsa, OK", "District 8"),
        ("1339 E 55th St, Tulsa, OK", "District 9"),
    ]
    
    print("Testing with CORRECT expected districts...")
    print("=" * 60)
    
    correct_count = 0
    total_count = 0
    
    for address, expected_district in test_cases:
        print(f"\nTesting: {address}")
        print(f"Expected District: {expected_district}")
        
        # Test geocoding
        coords = await geocoding_service.geocode_address(address)
        if coords:
            print(f"  ✓ Geocoded to: {coords}")
            
            # Test district determination
            district = geocoding_service.determine_district_by_coords(coords[0], coords[1])
            if district:
                print(f"  ✓ Found district: {district}")
                if district == expected_district:
                    print(f"  ✅ CORRECT - matches expected")
                    correct_count += 1
                else:
                    print(f"  ❌ WRONG - expected {expected_district}")
                total_count += 1
            else:
                print(f"  ✗ No district found")
        else:
            print(f"  ✗ Failed to geocode address")
    
    print(f"\n" + "=" * 60)
    print(f"RESULTS: {correct_count}/{total_count} correct ({correct_count/total_count*100:.1f}%)")
    
    if correct_count == total_count:
        print("🎉 ALL TESTS PASSED! District identification is working correctly.")
    else:
        print("⚠️  Some tests failed. District identification needs improvement.")


if __name__ == "__main__":
    asyncio.run(test_correct_districts()) 