# Backward-compatible re-exports — prefer georef.affine and fayvadgeo.survey_math.
from georef.affine import apply_affine, fit_affine, gen_coeff_matrix as genCoeffMatrix
from fayvadgeo.survey_math import dec_deg as decDeg, deg2rad, deg_min_sec as degMinSec, get_sign as getSgn, rad2deg


def compute(x, l):
    coeff, residuals, ata_inv = fit_affine(x, l)
    return coeff, residuals, ata_inv


def genCoeffMatrix(x):
    return gen_coeff_matrix(x)
