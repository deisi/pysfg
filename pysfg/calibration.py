"""Calibration related module"""

import numpy as np

class Victor:
    def __init__(self, central_wl, vis_wl, calib_central_wl, calib_coeff, numberOfPixel=1600):
        """Calibration of Victor data.

        central_wl: float, central wavelength of the grating
        vis_wl: float, visible wavelength
        calib_central_wl: float, central wl during calibration
        calib_coeff: calibration coefficients. Calibration coeff in decreasing order.
        numberOfPixel: horizontal number of camera pixels
        """
        self.central_wl = float(central_wl)
        self.vis_wl = float(vis_wl)
        self.calib_coeff = tuple(calib_coeff)
        self.calib_central_wl = float(calib_central_wl)
        self.poly = np.poly1d(calib_coeff)
        self.pixel = np.arange(numberOfPixel)

    @property
    def wavelength(self):
        """Wavelength of spectrum in nm"""

        # central_wl and calib_wl correspond to a lateral translation of the calibration
        # assuming that the grating is chaning linear according to its setting
        return self.poly(self.pixel) + self.central_wl - self.calib_central_wl

    @property
    def frequency(self):
        """Frequency of the signal in wavenumbers. This is before vis subtraction."""

        # 10**7 is the translation factor for wavelength in nm to wavenumber in 1/cm
        return 10**7/self.wavelength

    @property
    def wavenumber(self):
        """The spectral wavenumber in 1/cm after subtraction of the upconversion."""

        # As the calibration is not that precise anyways,
        # rounding on 2 digits is more than enough
        return np.round(10**7/(1/(1/self.wavelength - 1/self.vis_wl)), 2)


def from_victor_header(header):
    calib = Victor(
        header['central_wl'],
        header['vis_wl'],
        header['calib_central_wl'],
        header['calib_coeff']
    )
    return calib

def from_victor_file(fpath):
    """Read a file header from a victor file to generate calibration data"""
    from . import read
    header = read.victor.header(fpath)
    return from_victor_header(header)

def from_victor_file_wavenumber(fpath):
    """Read a victor file and return list of wavenumbers."""
    cV = from_victor_file(fpath)
    return cV.wavenumber
