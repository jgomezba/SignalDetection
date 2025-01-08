import math
from typing import Optional

class GeodesicPoint:
    def __init__(self, latitude:float, longitude:float, bearing:Optional[float]=None):
        """Initializes a GeodesicPoint object.

        Args:
            latitude (float): Latitude of the point in decimal degrees.
            longitude (float): Longitude of the point in decimal degrees.
            bearing (Optional[float]): Bearing in degrees from the point (default: None).
        """
        self.latitude = latitude
        self.longitude = longitude
        self.bearing = bearing
    
    def __repr__(self):
        """Returns a string representation of the GeodesicPoint."""
        return (f"GeodesicPoint(latitude={self.latitude}, longitude={self.longitude}, "
                f"bearing={self.bearing})")
    
    def __eq__(self, other):
        """Checks equality of two GeodesicPoint objects.

        Args:
            other (GeodesicPoint): Another GeodesicPoint object to compare.

        Returns:
            bool: True if the two points have the same latitude, longitude, bearing, and distance.
        """
        if not isinstance(other, GeodesicPoint):
            return NotImplemented
        return (self.latitude == other.latitude and
                self.longitude == other.longitude and
                self.bearing == other.bearing)

    def haversine_distance(point1, point2, km:Optional[bool]=False):
        """Calculates the Haversine distance between two GeodesicPoint objects.

        Args:
            point1 (GeodesicPoint): The first geodesic point.
            point2 (GeodesicPoint): The second geodesic point.
            km (bool): Result in km if True

        Returns:
            float: The distance in meters between the two points.
        """
        R = 6371000  # Radius of the Earth in meters
        lat1, lon1 = math.radians(point1.latitude), math.radians(point1.longitude)
        lat2, lon2 = math.radians(point2.latitude), math.radians(point2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        if km:
            return R * c / 1000
        else:
            return R * c
    
    def compute_intersection(point1, point2):
        """Calculates the intersection point between two GeodesicPoint objects.

        Args:
            point1 (GeodesicPoint): The first geodesic point.
            point2 (GeodesicPoint): The second geodesic point.

        Returns:
            tuple: The latitude and longitude of intersection.
        """
        lat1, lon1, brng1 = point1.latitude, point1.longitude, point1.bearing
        lat2, lon2, brng2 = point2.latitude, point2.longitude, point2.bearing
        
        if brng1 is None or brng2 is None or point1 == point2:
            return None, None
        
        # Convert degrees to radians
        lat1, lon1, brng1 = map(math.radians, [lat1, lon1, brng1])
        lat2, lon2, brng2 = map(math.radians, [lat2, lon2, brng2])

        # Angular distance between the points
        delta_12 = 2 * math.asin(math.sqrt(
            math.sin((lat2 - lat1) / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2)**2
        ))

        # Bearings between the two points
        if math.sin(lon2 - lon1) > 0:
            theta_12 = math.acos((math.sin(lat2) - math.sin(lat1) * math.cos(delta_12)) / (math.sin(delta_12) * math.cos(lat1)))
            theta_21 = 2 * math.pi - math.acos((math.sin(lat1) - math.sin(lat2) * math.cos(delta_12)) / (math.sin(delta_12) * math.cos(lat2)))
        else:
            theta_12 = 2 * math.pi - math.acos((math.sin(lat2) - math.sin(lat1) * math.cos(delta_12)) / (math.sin(delta_12) * math.cos(lat1)))
            theta_21 = math.acos((math.sin(lat1) - math.sin(lat2) * math.cos(delta_12)) / (math.sin(delta_12) * math.cos(lat2)))

        # Angles of intersection
        omega_1 = (brng1 - theta_12 + math.pi) % (2 * math.pi) - math.pi
        omega_2 = (theta_21 - brng2 + math.pi) % (2 * math.pi) - math.pi

        # Check for special cases
        if math.sin(omega_1) == 0 and math.sin(omega_2) == 0:
            return None, None
        if math.sin(omega_1) * math.sin(omega_2) < 0:
            return None, None

        # Absolute values of angles
        omega_1 = abs(omega_1)
        omega_2 = abs(omega_2)

        # Angular distance from point 1 to intersection
        omega_3 = math.acos(-math.cos(omega_1) * math.cos(omega_2) +
                            math.sin(omega_1) * math.sin(omega_2) * math.cos(delta_12))

        delta_13 = math.atan2(
            math.sin(delta_12) * math.sin(omega_1) * math.sin(omega_2),
            math.cos(omega_2) + math.cos(omega_1) * math.cos(omega_3)
        )

        # Latitude of intersection point
        lat3 = math.asin(math.sin(lat1) * math.cos(delta_13) +
                        math.cos(lat1) * math.sin(delta_13) * math.cos(brng1))

        # Longitude of intersection point
        dlon = math.atan2(
            math.sin(brng1) * math.sin(delta_13) * math.cos(lat1),
            math.cos(delta_13) - math.sin(lat1) * math.sin(lat3)
        )
        lon3 = (lon1 + dlon + math.pi) % (2 * math.pi) - math.pi

        # Convert results back to degrees
        lat3 = math.degrees(lat3)
        lon3 = math.degrees(lon3)

        return lat3, lon3

    def compute_stanfield_intersection(point1, point2):
            """Calculates the intersection point between two GeodesicPoint objects
                using Stanfield equations system

            Args:
                point1 (GeodesicPoint): The first geodesic point.
                point2 (GeodesicPoint): The second geodesic point.

            Returns:
                tuple: The latitude and longitude of intersection.
            """ 
            x1, y1, theta1 = point1.latitude, point1.longitude, point1.bearing
            x2, y2, theta2 = point2.latitude, point2.longitude, point2.bearing

            if theta1 is None or theta2 is None or point1 == point2:
                return None, None

            # Convert degrees to radians
            x1, y1, theta1 = map(math.radians, [x1, y1, theta1])
            x2, y2, theta2 = map(math.radians, [x2, y2, theta2])

            # Calculate tangent of azimuth angles
            tan_theta1 = math.tan(theta1)
            tan_theta2 = math.tan(theta2)

            # Avoid division by zero in case of parallel azimuths
            if math.isclose(tan_theta1, tan_theta2):
                raise ValueError("Azimuths are too similar; cannot triangulate position reliably.")

            # Solve for x_0 (lat of emitter)
            numerator_x = (y2 - y1) + x1 * tan_theta1 - x2 * tan_theta2
            denominator_x = tan_theta1 - tan_theta2
            lat = numerator_x / denominator_x

            # Solve for y_0 (lon of emitter) using one of the azimuth equations
            lon = y1 + tan_theta1 * (lat - x1)

            return math.degrees(lat), math.degrees(lon)

if __name__ == "__main__":
    point1 = GeodesicPoint(37.7749, -122.4194)
    point2 = GeodesicPoint(34.0522, -118.2437)

    print("Haversine Distance:", GeodesicPoint.haversine_distance(point1, point2), "meters")
    print("Haversine Distance:", GeodesicPoint.haversine_distance(point1, point2, True), "km")


    point3 = GeodesicPoint(51.8853, 0.2545)
    point4 = GeodesicPoint(49.0034, 2.5735)
    print(point3)
    point3.bearing = 108.55
    point4.bearing = 32.44
    print(point3)
    print("Intersection Point:", GeodesicPoint.compute_intersection(point3, point4))
    print("Intersection Point Stanfield:", GeodesicPoint.compute_stanfield_intersection(point3, point4))



