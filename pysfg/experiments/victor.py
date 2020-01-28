"""Module to encapsulate common experiments."""
import numpy as np
from ..select import SelectorPP
from ..spectrum import Spectrum, SpectrumPumpProbe
from ..calibration import from_victor_header

def spectrum(
        data,
        background_data=None,
        norm=None,
        data_select=SelectorPP(spectra=0),
        background_select=SelectorPP(spectra=0),
):
    """Make Spectrum object from static SFG measurment.

    data: victor data dict
    background: victor data dict
    norm: pysfg.Spectrum, for normalization or array or integer
    data_select: pysfg.SelctorPP object.
    background_select: pysfg.SelectorPP object

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

    return Spectrum(
        intensity = np.median(
            data['data'][data_select.select],
            axis=(0, 1) # Median over pp_delay and scans
        ),
        baseline = baseline,
        norm = norm,
        wavenumber = from_victor_header(
            data
        ).wavenumber[data_select.pixel]
    )

def spectrum_pp(
        data,
        background_data=None,
        norm=None,
        data_select=SelectorPP(spectra=0),
        background_select=SelectorPP(spectra=0),
        norm_select=SelectorPP(spectra=0),
):
    """Make pump-probe spectrum object"""

    if isinstance(data, dict):
        intensity = np.median(
            data['data'][data_select.select],
            axis=(1) # Median over pp_delay and scans
        ),
    else:
        intensity = data

    # Handle various background data inputs
    if isinstance(background_data, dict):
        baseline = np.median(
            background_data['data'][background_select.select],
            axis=(1)
        )
    else:
        baseline = background_data

    if isinstance(norm, SpectrumPumpProbe):
        pass

    return SpectrumPumpProbe(
        intensity,
        baseline,
        norm,
        wavenumber,
        pp_delay
    )
