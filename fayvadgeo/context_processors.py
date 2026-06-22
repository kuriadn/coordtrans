from django.conf import settings
from django.urls import reverse


def site(request):
    tools = [
        {
            'slug': 'coord-transform',
            'name': 'Coordinate Transform',
            'description': (
                'Affine Cassini-Soldner ↔ UTM: cadastral sheet mode (database controls) '
                'or custom control-point mode with fitted parameters and residuals.'
            ),
            'url': reverse('coords:enterpoints'),
            'status': 'live',
            'links': [
                {'label': 'Enter points', 'url': reverse('coords:enterpoints')},
                {'label': 'Upload file', 'url': reverse('coords:getfile')},
                {
                    'label': 'Manage data',
                    'url': reverse('coords:controlpoint_list'),
                    'staff_only': True,
                },
            ],
        },
        {
            'slug': 'crs-transform',
            'name': 'CRS Transform (PROJ)',
            'description': (
                'PROJ4 / EPSG reprojection via pyproj, plus NLIMS log-table Cassini '
                'with configurable central meridian. General-purpose; no sheet correction.'
            ),
            'url': reverse('crstrans:transform'),
            'status': 'live',
            'links': [
                {'label': 'Enter points', 'url': reverse('crstrans:transform')},
                {'label': 'Upload file', 'url': reverse('crstrans:upload')},
            ],
        },
        {
            'slug': 'traverse',
            'name': 'Traverse Adjustment',
            'description': (
                'Closed and open traverse computation with misclosure checks, '
                'Compass (Bowditch) or Transit rule adjustment, and coordinate propagation.'
            ),
            'url': reverse('traverse:adjust'),
            'status': 'live',
            'links': [
                {'label': 'Adjust traverse', 'url': reverse('traverse:adjust')},
            ],
        },
        {
            'slug': 'area',
            'name': 'Area & Perimeter',
            'description': (
                'Compute parcel area and boundary perimeter from surveyed coordinates '
                'using the shoelace method, with map preview and edge lengths.'
            ),
            'url': reverse('areacalc:compute'),
            'status': 'live',
            'links': [
                {'label': 'Compute parcel', 'url': reverse('areacalc:compute')},
            ],
        },
        {
            'slug': 'bearing-distance',
            'name': 'Bearing & Distance',
            'description': (
                'Forward (polar) and inverse (join) computations — '
                'coordinates from bearing and distance, or bearing and distance between two points.'
            ),
            'url': reverse('geocalc:compute'),
            'status': 'live',
            'links': [
                {'label': 'Polar / Join', 'url': reverse('geocalc:compute')},
            ],
        },
    ]

    is_staff = getattr(request.user, 'is_staff', False)
    if not is_staff:
        for tool in tools:
            tool['links'] = [
                link for link in tool.get('links', []) if not link.get('staff_only')
            ]

    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'SITE_TAGLINE': settings.SITE_TAGLINE,
        'SURVEY_TOOLS': tools,
    }
