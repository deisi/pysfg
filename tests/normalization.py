"""Test and example of how to import and average a norm/quartz spectrum"""
import numpy as np
import pysfg

# Global Vairables likely to be changed
fpath = './data'
norm_name = './data/sc_quartz.dat'
norm_spectrum_index = 0
background_name = './data/bg_quartz.dat'
background_spectrum_index = norm_spectrum_index

# Global Variables that usually are kept like this
norm_pp_delays = slice(None)
norm_scans = slice(None)
norm_pixel = slice(None)
background_pp_delays = norm_pp_delays
background_scans = norm_scans
background_pixel = slice(None)

# Import Data
all_data = pysfg.read.victor.folder(fpath)
norm_data = all_data[norm_name]
background_data = all_data[background_name]
norm = pysfg.Spectrum(
    intensity = np.median(
        norm_data['data'][
            norm_pp_delays,
            norm_scans,
            norm_spectrum_index,
            norm_pixel
        ],
        axis=(0, 1) # Median over pp_delay and scans
    ),
    baseline = np.median(
        background_data['data'][
            background_pp_delays,
            background_scans,
            background_spectrum_index,
            background_pixel
        ],
        axis=(0, 1)
    ),
    wavenumber = pysfg.calibration.from_victor_header(
        norm_data
    ).wavenumber
)

