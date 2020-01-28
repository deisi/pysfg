"""Module to encapsulate common experiments."""
import numpy as np
from ..select import SelectorPP
from ..spectrum import Spectrum
from ..calibration import from_victor_header

def spectrum(
        data,
        background_data,
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

    if isinstance(norm, Spectrum):
        norm = norm.basesubed

    return Spectrum(
        intensity = np.median(
            data['data'][data_select.select],
            axis=(0, 1) # Median over pp_delay and scans
        ),
        baseline = np.median(
            background_data['data'][background_select.select],
            axis=(0, 1)
        ),
        norm = norm,
        wavenumber = from_victor_header(
            data
        ).wavenumber[data_select.pixel]
    )
