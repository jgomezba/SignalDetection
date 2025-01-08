import unittest
from geodesic_point import GeodesicPoint

class TestGeodesicPoint(unittest.TestCase):

    def test_haversine_distance_meters(self):
        point1 = GeodesicPoint(37.7749, -122.4194)
        point2 = GeodesicPoint(34.0522, -118.2437)
        expected_distance = 559120.5770615534  # in meters
        result = GeodesicPoint.haversine_distance(point1, point2)
        self.assertAlmostEqual(result, expected_distance, places=5)

    def test_haversine_distance_kilometers(self):
        point1 = GeodesicPoint(37.7749, -122.4194)
        point2 = GeodesicPoint(34.0522, -118.2437)
        expected_distance = 559.1205770615534  # in kilometers
        result = GeodesicPoint.haversine_distance(point1, point2, km=True)
        self.assertAlmostEqual(result, expected_distance, places=5)

    def test_repr(self):
        point = GeodesicPoint(51.8853, 0.2545)
        expected_repr = "GeodesicPoint(latitude=51.8853, longitude=0.2545, bearing=None)"
        self.assertEqual(repr(point), expected_repr)

    def test_bearing_assignment(self):
        point = GeodesicPoint(51.8853, 0.2545)
        point.bearing = 108.55
        self.assertEqual(point.bearing, 108.55)

    def test_compute_intersection(self):
        point1 = GeodesicPoint(51.8853, 0.2545, bearing=108.55)
        point2 = GeodesicPoint(49.0034, 2.5735, bearing=32.44)
        expected_intersection = (50.90760750047431, 4.5085746457704685)
        result = GeodesicPoint.compute_intersection(point1, point2)
        self.assertAlmostEqual(result[0], expected_intersection[0], places=5)
        self.assertAlmostEqual(result[1], expected_intersection[1], places=5)
    
    def test_wrong_compute_intersection(self):
        point1 = GeodesicPoint(51.8853, 0.2545, bearing=108.55)
        point2 = GeodesicPoint(51.8853, 0.2545, bearing=108.55)
        expected_intersection = (None, None)
        result = GeodesicPoint.compute_intersection(point1, point2)
        self.assertEqual(result[0], expected_intersection[0])
        self.assertEqual(result[1], expected_intersection[1])

if __name__ == "__main__":
    unittest.main()
