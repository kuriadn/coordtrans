"""Cassini-Soldner / UTM georeferencing library."""

from georef.affine import (
    apply_affine,
    fit_affine,
    gen_coeff_matrix,
    transform_with_controls,
)
from georef.cassini_proj import cassini_proj4_with_cm, panel_central_meridian
from georef.cassini_tables import CassTable
from fayvadgeo.survey_math import dec_deg, deg2rad, deg_min_sec, get_sign, rad2deg

# Backward-compatible names
genCoeffMatrix = gen_coeff_matrix
compute = fit_affine
decDeg = dec_deg
degMinSec = deg_min_sec
getSgn = get_sign

__all__ = [
    'CassTable',
    'apply_affine',
    'cassini_proj4_with_cm',
    'compute',
    'decDeg',
    'dec_deg',
    'deg2rad',
    'degMinSec',
    'deg_min_sec',
    'fit_affine',
    'genCoeffMatrix',
    'gen_coeff_matrix',
    'getSgn',
    'get_sign',
    'panel_central_meridian',
    'rad2deg',
    'transform_with_controls',
]
