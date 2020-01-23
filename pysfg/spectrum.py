"""Module to deal with SFG Spectral Data"""

import numpy as np

class Spectrum():
    def __init__(self, intensity, baseline=None, norm=None, wavenumber=None, vis=None):
        """1D SFG Spectrum

        Class to encapsulate Static SFG data.

        intensity: 1d array of intensity values
        baseline: 1d array of baseline values
        norm: 1d array of norm values
        wavelength: 1d array of wavelength
        vis: central wavelength if the vis in nm

        """
        self.intensity = intensity
        self.baseline = baseline
        self.norm = norm
        self.wavenumber = wavenumber


    @property
    def intensity(self):
        """Intensity values of the spectrum. Must be a 1D array"""
        return self._intensity

    @intensity.setter
    def intensity(self, intensity):
        if len(np.shape(intensity)) != 1:
            raise ValueError("Intensity must be 1 D array.")
        self._intensity = np.array(intensity)

    @property
    def baseline(self):
        """Baseline of the spectrum"""
        return self._baseline

    @baseline.setter
    def baseline(self, baseline):
        if isinstance(baseline, type(None)):
            self._baseline = np.zeros_like(self.intensity)
        elif isinstance(baseline, int) or isinstance(baseline, float):
            self._baseline = np.ones_like(self.intensity) * baseline
        else:
            if np.shape(baseline) != np.shape(self.intensity):
                raise ValueError('Baseline has not the same shape as intensity')
            self._baseline = np.array(baseline)

    @property
    def norm(self):
        return self._norm

    @norm.setter
    def norm(self, norm):
        if isinstance(norm, type(None)):
            self._norm = np.ones_like(self.intensity)
        elif isinstance(norm, int) or isinstance(norm, float):
            self._norm = np.ones_like(self.intensity) * norm
        else:
            if np.shape(norm) != np.shape(self.intensity):
                raise ValueError('Norm has not the same shape as intensity')
            self._norm = np.array(norm)

    @property
    def shape(self):
        """Shape of the intensity"""
        return np.shape(self.intensity)

    @property
    def basesubed(self):
        """Baseline subtracted intensity"""
        return self.intensity - self.baseline

    @property
    def normalized(self):
        """Normalized intensity"""
        return self.basesubed / self.norm

    @property
    def wavenumber(self):
        """Wavenumber values of the spectrum."""
        return self._wavenumber

    @wavenumber.setter
    def wavenumber(self, wavenumber):
        if isinstance(wavenumber, type(None)):
            # The camera record nm. Thus wavenumber order is typically
            # reversed. If we dont have the wavenumbers, we should
            # atleast have the right order.
            wavenumber = np.arange(self.shape[0], 0, -1)
        if np.shape(wavenumber) != self.shape:
            raise ValueError('Shape of wavenumber and intensity must match')
        self._wavenumber = wavenumber

