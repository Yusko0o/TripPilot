import math

from .airport_provider import airport_index


def nearest_airport(latitude, longitude):
    closest = None
    for airport in airport_index():
        if airport.get("latitude") is None or airport.get("longitude") is None:
            continue
        distance = haversine(
            latitude,
            longitude,
            airport["latitude"],
            airport["longitude"],
        )
        if closest is None or distance < closest[0]:
            closest = (distance, airport)

    if closest is None:
        return None
    result = {
        key: value
        for key, value in closest[1].items()
        if not key.endswith("search")
    }
    result["distanceKm"] = round(closest[0], 1)
    return result


def haversine(latitude1, longitude1, latitude2, longitude2):
    radius = 6371.0
    lat1, lat2 = math.radians(latitude1), math.radians(latitude2)
    delta_latitude = math.radians(latitude2 - latitude1)
    delta_longitude = math.radians(longitude2 - longitude1)
    value = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_longitude / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))

