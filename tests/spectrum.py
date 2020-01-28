"""Test and example of how to import a Simple SFG spectrum."""

import numpy as np
import pysfg

# Global Vairables likely to be changed
fpath = './data'
data_name = './data/sc_d2o-dopc.dat'
spectrum_index = 0
pixel = slice(200, 1400) # it might be usefull to slice the pixel right here
norm_name = './data/norm.json' # cached version of norm
background_name = './data/bg_d2o-docpe.dat'
background_spectrum_index = spectrum_index

# Import Data
all_data = pysfg.read.victor.folder(fpath)
norm = pysfg.spectrum.json_to_spectrum(norm_name)
# Select Data
data = all_data[data_name]
background_data = all_data[background_name]
# Generate Return object
spectrum = pysfg.experiments.victor.spectrum(
    data,
    background_data,
    norm=norm.basesubed[pixel],
    data_select=pysfg.SelectorPP(spectra=spectrum_index, pixel=pixel),
    background_select=pysfg.SelectorPP(spectra=background_spectrum_index, pixel=pixel)
)
