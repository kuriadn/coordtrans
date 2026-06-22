from django.test import SimpleTestCase, override_settings

from .compute import read_points_file, transform_points
from .presets import resolve_preset


class CrsTransformTests(SimpleTestCase):
    def test_resolve_preset_cassini_utm(self):
        source, target = resolve_preset('cassini-utm')
        self.assertIn('cass', str(source).lower())
        self.assertEqual(int(target), 32637)

    def test_utm_to_wgs84(self):
        result = transform_points(
            32637, 4326, [(500000.0, 4649776.0)],
            preset='utm-wgs84',
            preset_label_text='UTM → WGS84',
        )
        self.assertEqual(result.success_count, 1)
        row = result.rows[0]
        self.assertTrue(result.target_geographic)
        self.assertTrue(-180 <= row.out_x <= 180)
        self.assertTrue(-90 <= row.out_y <= 90)

    def test_read_points_file(self):
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write('100,200\n# comment\n300,400\n')
            path = tmp.name
        try:
            pts = read_points_file(path)
            self.assertEqual(pts, [(100.0, 200.0), (300.0, 400.0)])
        finally:
            os.unlink(path)

    @override_settings(
        MAP_CASSINI_PROJ4=(
            '+proj=cass +lat_0=0 +lon_0=37.0 +k=0.99975 +x_0=500000 +y_0=0 '
            '+ellps=clrk80 +towgs84=-205,-48,153,0,0,0,0 +units=m +no_defs'
        ),
        MAP_UTM_EPSG=32637,
    )
    def test_preset_transform_roundtrip(self):
        utm_pt = (500000.0, 4649776.0)
        cass = transform_points(*resolve_preset('utm-cassini'), [utm_pt])
        back = transform_points(
            *resolve_preset('cassini-utm'),
            [(cass.rows[0].out_x, cass.rows[0].out_y)],
        )
        self.assertAlmostEqual(back.rows[0].out_x, utm_pt[0], delta=0.5)
        self.assertAlmostEqual(back.rows[0].out_y, utm_pt[1], delta=0.5)
