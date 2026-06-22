from django.test import SimpleTestCase

from .compute import forward_polar, format_bearing_dms, inverse_join


class GeocalcTests(SimpleTestCase):
    def test_forward_polar_east(self):
        result = forward_polar('A', 100.0, 200.0, 'B', 90.0, 50.0)
        self.assertAlmostEqual(result.to_point.easting, 150.0, places=3)
        self.assertAlmostEqual(result.to_point.northing, 200.0, places=3)
        self.assertAlmostEqual(result.departure, 50.0, places=3)
        self.assertAlmostEqual(result.latitude, 0.0, places=3)

    def test_inverse_join(self):
        result = inverse_join('A', 100.0, 200.0, 'B', 150.0, 200.0)
        self.assertAlmostEqual(result.distance, 50.0, places=3)
        self.assertAlmostEqual(result.bearing_deg, 90.0, places=3)

    def test_forward_inverse_roundtrip(self):
        fwd = forward_polar('A', 500.0, 1000.0, 'B', 45.0, 100.0)
        inv = inverse_join(
            'A', 500.0, 1000.0,
            'B', fwd.to_point.easting, fwd.to_point.northing,
        )
        self.assertAlmostEqual(inv.distance, 100.0, places=3)
        self.assertAlmostEqual(inv.bearing_deg, 45.0, places=3)

    def test_format_bearing_dms(self):
        self.assertEqual(format_bearing_dms(90), '90°00\'00.00"')
