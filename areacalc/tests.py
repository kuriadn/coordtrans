from django.test import SimpleTestCase

from .compute import VertexInput, compute_area_perimeter, format_bearing_dms
from .map_utils import build_area_map_context


class AreaComputeTests(SimpleTestCase):
    def test_unit_square(self):
        vertices = [
            VertexInput('P1', 0, 0),
            VertexInput('P2', 10, 0),
            VertexInput('P3', 10, 10),
            VertexInput('P4', 0, 10),
        ]
        result = compute_area_perimeter(vertices, 'Test', closed=True)
        self.assertAlmostEqual(result.area_sq_m, 100.0, places=3)
        self.assertAlmostEqual(result.perimeter_m, 40.0, places=3)
        self.assertAlmostEqual(result.area_hectares, 0.01, places=5)

    def test_open_polyline_perimeter_only(self):
        vertices = [
            VertexInput('A', 0, 0),
            VertexInput('B', 3, 4),
        ]
        result = compute_area_perimeter(vertices, closed=False)
        self.assertIsNone(result.area_sq_m)
        self.assertAlmostEqual(result.perimeter_m, 5.0, places=3)
        self.assertEqual(len(result.edges), 1)

    def test_format_bearing_dms(self):
        self.assertEqual(format_bearing_dms(90), '90°00\'00.00"')

    def test_map_context(self):
        vertices = [
            VertexInput('P1', 0, 0),
            VertexInput('P2', 10, 0),
            VertexInput('P3', 10, 10),
        ]
        result = compute_area_perimeter(vertices, closed=True)
        ctx = build_area_map_context(result)
        self.assertEqual(len(ctx['vertices']), 3)
        self.assertEqual(len(ctx['edges']), 3)
        self.assertIn('distance_label', ctx['edges'][0])
