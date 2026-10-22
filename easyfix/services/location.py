"""
Location and Geolocation Services
Implements the Haversine distance formula to calculate real-world
distance (in kilometers) between customer and skilled workers.
"""

import math

# Default coordinates for Chennai central location
DEFAULT_CHENNAI_LAT = 13.0827
DEFAULT_CHENNAI_LNG = 80.2707


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points on Earth
    in kilometers using the Haversine formula.
    """
    try:
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return None

        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

        # Convert decimal degrees to radians
        rad_lat1, rad_lon1, rad_lat2, rad_lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = rad_lat2 - rad_lat1
        dlon = rad_lon2 - rad_lon1
        a = (math.sin(dlat / 2.0) ** 2) + math.cos(rad_lat1) * math.cos(rad_lat2) * (math.sin(dlon / 2.0) ** 2)
        c = 2.0 * math.asin(math.sqrt(a))

        # Radius of Earth in kilometers
        earth_radius_km = 6371.0
        distance = c * earth_radius_km
        return round(distance, 1)
    except (ValueError, TypeError):
        return None
