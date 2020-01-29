"""Module to encapsulate common experiments."""
import numpy as np
from ..select import SelectorPP
from ..spectrum import Spectrum, PumpProbe
from ..calibration import from_victor_header

def spectrum(
        data,
        background_data=None,
        norm=None,
        data_select=SelectorPP(spectra=0),
        background_select=SelectorPP(spectra=0),
        wavenumber=None
):
    """Make Spectrum object from static SFG measurment.

    data: victor data dict
    background: victor data dict
    norm: pysfg.Spectrum, for normalization or array or integer
    data_select: pysfg.SelctorPP object.
    background_select: pysfg.SelectorPP object
    wavenumber: Only None implemented currently

    returns `pysfg.Spectrum` objecth
    """

    # Onlay Spectrum is array input is allowed, as background needs to be
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

    if not isinstance(wavenumber, type(None)):
        raise NotImplementedError
    wavenumber=from_victor_header(
        data
    ).wavenumber[data_select.pixel]

    if not isinstance(data, dict):
        raise NotImplementedError
    intensity = np.median(
        data['data'][data_select.select],
        axis=(0, 1) # Median over pp_delay and scans
    )

    return Spectrum(
        intensity= intensity,
        baseline=baseline,
        norm=norm,
        wavenumber=wavenumber
    )

def pumpProbe(
        data,
        background_data=None,
        norm=None,
        data_select=SelectorPP(spectra=0),
        background_select=SelectorPP(spectra=0),
        norm_select=SelectorPP(spectra=0),
        wavenumber=None,
        pp_delay=None,
):
    """Make pump-probe spectrum object"""

    if not isinstance(data, dict):
        raise NotImplementedError
    intensity = np.median(
        data['data'][data_select.select],
        axis=(1) # Median scans
    )

    # Handle various background data inputs
    if isinstance(background_data, dict):
        baseline = np.median(
            background_data['data'][background_select.select],
            axis=(1)
        )
    else:
        baseline = background_data

    # Assume norm is correct shape else it will fail
    # during assingment TODO: Add shape checking
    if isinstance(norm, PumpProbe):
        norm = norm.basesubed

    if not isinstance(wavenumber, type(None)):
        raise NotImplemented
    wavenumber=from_victor_header(
        data
    ).wavenumber[data_select.pixel]

    if not isinstance(pp_delay, type(None)):
        raise NotImplemented
    pp_delay = data['timedelay']

    return PumpProbe(
        intensity,
        baseline,
        norm,
        wavenumber,
        pp_delay
    )
