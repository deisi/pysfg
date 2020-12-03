import numpy as np
import logging
import os

# Just changing these wont work
PIXEL = 1600  # Number of pixel on camera
SPECS = 3  # Number of spectra recorded


def data_file(fpath, *args, **kwargs):
    """Read files saved by original veronica labview programm

    The function reads a file from veronika labview,
    and returns it as a unified 4 dimensional numpy array. And an
    array with all the pump probe time delays.

    Parameters
    ----------
    fpath: str
        Path to load data from.

    Returns
    -------
    tuple of two arrays.
    First array is:
        4 Dimensional numpy array with:
            0 index pp_delays,
            1 index number of repetitions
            2 index number of y-pixel/spectra/bins
            3 index x-pixel number
    """

    print(fpath)
    data = np.genfromtxt(fpath, *args, **kwargs)
    pp_delays = data[::PIXEL+2, 0]
    number_of_ppdelays = len(pp_delays)
    mask = np.hstack(list(((([i+j for j in range(SPECS)] for i in range(2, data.shape[-1]-SPECS, 6))))))
    data = data[:, mask]   # Only keep spectral data
    data = np.delete(data, list(range(0, len(data), PIXEL+2)), axis=0)   # remove redundant pp_delay lines
    data = np.delete(data, list(range(PIXEL, len(data), PIXEL+1)), axis=0)  # remove redundant
    data = data.T
    number_of_scans = data.shape[0]//3
    data = data.reshape((number_of_scans, SPECS, number_of_ppdelays, PIXEL), order='C')
    data = np.moveaxis(data, 1, 2)
    data = np.moveaxis(data, 0, 1)
    return data, pp_delays
