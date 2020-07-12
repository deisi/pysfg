from . import victor, vivian
import numpy as np
from scipy.stats import sem
from ..select import SelectorPP
from ..spectrum import Spectrum, PumpProbe
from ..calibration import Calibration



def spectrum(
        data,
        background_data=None,
        norm=None,
        data_select=SelectorPP(spectra=0),
        background_select=SelectorPP(spectra=0),
        calibration=None
):
    """Make Spectrum object from static SFG measurment.

    data: victor data dict
    background: victor data dict
    norm: pysfg.Spectrum, for normalization or array or integer
    data_select: pysfg.SelctorPP object.
    background_select: pysfg.SelectorPP object
    calibration: `pysfg.Calibration` object. if none given, the calibration
      is infered from the data. However this only works for victor data, as that
      is the only setup as of right now, that correctly exports all required information.

    Example:
      See `pysfg/test/spectrum.py` for example usage.

    Returns `pysfg.Spectrum` objecth
    """

    # Only Spectrum as input array is allowed, as background needs to be
    # subtracted prior to usage. This is not automatically possible from
    # raw_data file.
    if isinstance(norm, Spectrum):
        norm = norm.basesubed

    # Handle various background data inputs
    if isinstance(background_data, dict):
        baseline = np.median(
            background_data['data'][background_select.select],
            axis=(0, 1)
        )
    elif isinstance(background_data, Spectrum):
        baseline = background_data.intensity
    # Spectrum can handle the input or will fail
    else:
        baseline = background_data

    if not isinstance(data, dict):
        raise NotImplementedError
    intensity = np.median(
        data['data'][data_select.select],
        axis=(0, 1) # Median over pp_delay and scans
    )

    intensityE = sem(
        np.median(data['data'][data_select.select], axis=0),
        axis=(0) # Median over pp_delay sem over scans.
    )

    if isinstance(calibration, type(None)):
        calibration = Calibration(
            data['central_wl'], data['vis_wl'], data['calib_central_wl'], data['calib_coeff']
        )
    wavenumber = calibration.wavenumber[data_select.pixel]

    return Spectrum(
        intensity=intensity,
        baseline=baseline,
        norm=norm,
        wavenumber=wavenumber,
        intensityE=intensityE,
        pixel=data_select.pixel,
    )
