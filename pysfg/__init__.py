# pysfg init file

from . import calibration, read, spectrum

from .spectrum import *

def get_calibration_from_victor_header(header):
    calib = calibration.Victor(
        header['central_wl'],
        header['vis_wl'],
        header['calib_central_wl'],
        header['calib_coeff']
    )
    return calib

def get_calibration_from_victor_file(fpath):
    """Read a file header from a victor file to generate calibration data"""

    header = read.victor.header(fpath)
    return get_calibration_from_victor_header(header)

def get_wavenumber_from_victor_file(fpath):
    """Read a victor file and return list of wavenumbers."""
    cV = get_calibration_from_victor_file(fpath)
    return cV.wavenumber

