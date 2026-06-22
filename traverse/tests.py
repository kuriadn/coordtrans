from django.test import SimpleTestCase

from .compute import LegInput, compute_traverse, dms_to_decimal, format_bearing_dms
from .map_utils import build_traverse_map_context


class TraverseComputeTests(SimpleTestCase):
    def test_dms_to_decimal(self):
        self.assertAlmostEqual(dms_to_decimal(45, 30, 0), 45.5)

    def test_closed_square_traverse(self):
        legs = [
            LegInput('A', 'B', 90, 100),
            LegInput('B', 'C', 180, 100),
            LegInput('C', 'D', 270, 100),
            LegInput('D', 'A', 0, 100),
        ]
        result = compute_traverse(legs, 'A', 1000.0, 2000.0, 'closed', 'compass')
        self.assertAlmostEqual(result.misclosure_linear, 0.0, places=6)
        end = result.stations[-1]
        self.assertAlmostEqual(end.easting, 1000.0, places=3)
        self.assertAlmostEqual(end.northing, 2000.0, places=3)

    def test_open_traverse_propagation(self):
        legs = [LegInput('P1', 'P2', 90, 50), LegInput('P2', 'P3', 0, 50)]
        result = compute_traverse(legs, 'P1', 500.0, 1000.0, 'open')
        self.assertEqual(len(result.stations), 3)
        self.assertAlmostEqual(result.stations[-1].easting, 550.0, places=3)
        self.assertAlmostEqual(result.stations[-1].northing, 1050.0, places=3)

    def test_format_bearing_dms(self):
        self.assertEqual(format_bearing_dms(90), '90°00\'00.00"')

    def test_map_context_includes_leg_labels(self):
        legs = [LegInput('A', 'B', 90, 100)]
        result = compute_traverse(legs, 'A', 100.0, 200.0, 'open')
        ctx = build_traverse_map_context(result)
        self.assertIn(ctx['mode'], ('plan', 'geographic'))
        self.assertEqual(len(ctx['legs']), 1)
        self.assertEqual(ctx['legs'][0]['distance_label'], '100.00 m')
        self.assertEqual(ctx['legs'][0]['bearing_label'], '90°00\'00.00"')
