from math import radians, sin, cos, sqrt, atan2


class GeoService:

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = sin(dlat / 2)**2 + cos(radians(lat1)) * \
            cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    @classmethod
    def distance_between_locations(cls, loc1, loc2):
        if not loc1.latitude or not loc1.longitude:
            return None
        if not loc2.latitude or not loc2.longitude:
            return None

        return cls.haversine(
            loc1.latitude,
            loc1.longitude,
            loc2.latitude,
            loc2.longitude
        )
