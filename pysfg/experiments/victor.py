"""Module to encapsulate common experiments.

I'm not sure if this is usefull, but I know, that in the end one does more ore
less always the same. This module should hold methods, that help redoing these
things easier and faster.

"""
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

    Example:
      See `pysfg/test/spectrum.py` for example usage.

    Returns `pysfg.Spectrum` objecth
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
    """Make pump-probe spectrum object taking the median over the scan axis.

    A pump-probe spectrum combines multiple vicotr `.dat` files into one
    `pysft.spectrum.PumpProbe` object.

    One must select a single `spectra` index. Thus the `SelectorPP(spectra=0)`
    in the default configuration. The selection of the data for `data`
    (data_select), the background (background_select) and the normalization
    (norm_select) are independent, but assignment will fail if background and
    norm can't be casted into the same shape as data.


    Arguments:
    data: A victor data dict as returned by `pysfg.vicotr.read.data_file`.
    background_data: Can be a constant number, or a numpy array with the same
      length as the pixel axis of `data`, or a `pysfg.read.victor.data_file`
      dictionary.
    norm: Can be a constant number, or a 1D array with the same length as pixel
      axis of `data` above, or a 2D array with the exact same shape as `data` above
    data_selectrion: `pysfg.SelectorPP` object. This is used to subselect data from
      the data['data'] entry of the passed data dict. The default is to take spectrum
      index 0 and leave the rest untouched.
    background_select: Same as `data_select` but for the background. Shapes of data
      and background must match or else a `ValueError` occurs.
    norm_select: Same as `data_select` but for the norm. Shape of data and norm must
      match. Else ValueError occurs.
    wavenumber: Not fully implemented, but if None. The calibration is read of
      the above passed data dict.
    pp_delay: Not fully impelemented, but if None, pp_delays is read of the `data`
      dict.

    Example:
      see `pysfg/test/pump_probe.py` for example usage.

    Returns:
      A `pysfg.PumpProbe` object
    """

    if not isinstance(data, dict):
        raise NotImplementedError
        # Need to implement alternative default wavenumber
        # Need to implement alternative for pp_delay
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
        raise NotImplementedError
    wavenumber=from_victor_header(
        data
    ).wavenumber[data_select.pixel]

    if not isinstance(pp_delay, type(None)):
        raise NotImplementedError
    pp_delay = data['timedelay']

    return PumpProbe(
        intensity,
        baseline,
        norm,
        wavenumber,
        pp_delay
    )
