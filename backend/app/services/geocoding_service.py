import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import httpx
from app.core.config import Settings
from app.data.tulsa_districts import DISTRICT_REPRESENTATIVES, ZIP_TO_DISTRICT

logger = logging.getLogger(__name__)


class GeocodingService:
    """Simplified service for geocoding addresses and determining city council districts"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.google_api_key = settings.google_api_key

    async def geocode_address(
        self, address: str, city: str = "Tulsa", state: str = "OK"
    ) -> Optional[Tuple[float, float]]:
        """
        Geocode an address to latitude/longitude coordinates.

        Args:
            address: Street address
            city: City name (default: Tulsa)
            state: State abbreviation (default: OK)

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            full_address = f"{address}, {city}, {state}"

            # Try Google Geocoding API first if available
            if self.google_api_key:
                coords = await self._geocode_with_google(full_address)
                if coords:
                    return coords

            # For now, return a default Tulsa coordinate if geocoding fails
            # This is a fallback until we can implement proper geocoding
            return (36.1539, -95.9928)  # Downtown Tulsa coordinates

        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {str(e)}")

        return None

    async def _geocode_with_google(self, address: str) -> Optional[Tuple[float, float]]:
        """Use Google Geocoding API for more accurate results."""
        try:
            url = (
                f"https://maps.googleapis.com/maps/api/geocode/json"
                f"?address={quote(address)}"
                f"&key={self.google_api_key}"
            )

            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()

                if data.get("status") == "OK" and data.get("results"):
                    location = data["results"][0]["geometry"]["location"]
                    return (location["lat"], location["lng"])

        except Exception as e:
            logger.error(f"Google Geocoding API error: {str(e)}")

        return None

    def determine_district_by_coords(
        self, latitude: float, longitude: float
    ) -> Optional[str]:
        """
        Simplified district determination based on coordinates.
        For now, this is a basic implementation that would need real boundary data.
        """
        # This is a simplified approach - in production you'd use real boundary polygons
        # For now, we'll use approximate coordinate ranges for each district

        # These are very simplified boundaries - replace with real data
        if 36.17 <= latitude <= 36.20 and -96.00 <= longitude <= -95.95:
            return "District 1"  # North Tulsa
        elif 36.13 <= latitude <= 36.17 and -96.05 <= longitude <= -95.99:
            return "District 2"  # Northwest
        elif 36.09 <= latitude <= 36.13 and -96.05 <= longitude <= -95.99:
            return "District 3"  # West
        elif 36.05 <= latitude <= 36.09 and -96.00 <= longitude <= -95.95:
            return "District 4"  # Southwest
        elif 36.13 <= latitude <= 36.17 and -95.95 <= longitude <= -95.90:
            return "District 5"  # Central
        elif 36.09 <= latitude <= 36.13 and -95.90 <= longitude <= -95.85:
            return "District 6"  # East
        elif 36.09 <= latitude <= 36.13 and -95.95 <= longitude <= -95.90:
            return "District 7"  # Midtown
        elif 36.01 <= latitude <= 36.05 and -95.95 <= longitude <= -95.90:
            return "District 8"  # South
        elif 36.05 <= latitude <= 36.09 and -95.90 <= longitude <= -95.85:
            return "District 9"  # Southeast

        return None

    def determine_district_by_zip(self, address: str) -> Optional[str]:
        """
        Fallback method to determine district by ZIP code extracted from address.

        Args:
            address: Full address string

        Returns:
            District name or None if ZIP not found or not mapped
        """
        try:
            # Extract ZIP code using regex
            zip_match = re.search(r"\b(\d{5})\b", address)
            if zip_match:
                zip_code = zip_match.group(1)
                return ZIP_TO_DISTRICT.get(zip_code)

        except Exception as e:
            logger.error(
                f"Error determining district by ZIP from '{address}': {str(e)}"
            )

        return None

    async def find_district_by_address(self, address: str) -> Dict[str, Any]:
        """
        Find city council district for a given address using multiple methods.

        Args:
            address: Street address to lookup

        Returns:
            Dict containing district info, coordinates, and status
        """
        result: Dict[str, Any] = {
            "address": address,
            "coordinates": None,
            "district": None,
            "councilor": None,
            "success": False,
            "error": None,
            "method": None,
        }

        try:
            # Method 1: Try ZIP code mapping first (most reliable for now)
            zip_district = self.determine_district_by_zip(address)
            if zip_district:
                result["district"] = zip_district
                result["councilor"] = DISTRICT_REPRESENTATIVES.get(zip_district, {})
                result["success"] = True
                result["method"] = "zip_code"

                # Try to get coordinates too
                coords = await self.geocode_address(address)
                if coords:
                    result["coordinates"] = {"lat": coords[0], "lng": coords[1]}

                return result

            # Method 2: Try geocoding + coordinate-based district determination
            coords = await self.geocode_address(address)
            if coords:
                result["coordinates"] = {"lat": coords[0], "lng": coords[1]}

                district = self.determine_district_by_coords(coords[0], coords[1])
                if district:
                    result["district"] = district
                    result["councilor"] = DISTRICT_REPRESENTATIVES.get(district, {})
                    result["success"] = True
                    result["method"] = "geocoding"
                    return result

            # If no methods worked
            result["error"] = (
                "Address not found within Tulsa city limits or recognizable ZIP code"
            )

        except Exception as e:
            logger.error(f"Error finding district for address '{address}': {str(e)}")
            result["error"] = f"Service error: {str(e)}"

        return result

    def get_all_representatives(self) -> List[Dict[str, str]]:
        """Get all district representatives plus mayor."""
        representatives = []

        # Add Mayor
        representatives.append(
            {
                "name": "Monroe Nichols",
                "position": "Mayor",
                "email": "mayor@cityoftulsa.org",
                "phone": "(918) 596-7777",
            }
        )

        # Add all district councilors
        for district, rep_info in DISTRICT_REPRESENTATIVES.items():
            representatives.append(
                {
                    "name": rep_info["name"],
                    "position": rep_info["position"],
                    "email": rep_info["email"],
                    "phone": rep_info.get("phone", ""),
                    "district": district,
                }
            )

        return representatives
