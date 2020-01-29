"""Test module and example for import of a pump probe scan."""

import numpy as np
import pysfg

# Global Vairables likely to be changed
fpath = './data'
data_name = './data/ts_gold.dat'
# This depends on the bin used during experiment
pumped_index = 1
probed_index = 0
pixel = slice(None) #, 1400) # it might be usefull to slice the pixel right here
norm_name = './data/norm.json' # cached version of norm
background_name = './data/bg_d2o-docpe.dat'
background_pumped_index = pumped_index
background_probed_index = probed_index # aka the unpumped

# Import Data
all_data = pysfg.read.victor.folder(fpath)
norm = pysfg.spectrum.json_to_spectrum(norm_name)
# Select Data
data = all_data[data_name]
background_data = all_data[background_name]

# Generate Return object
pumped = pysfg.experiments.victor.pumpProbe(
    data,
    background_data,
    norm=norm.basesubed[pixel],
    data_select=pysfg.SelectorPP(spectra=pumped_index, pixel=pixel),
    background_select=pysfg.SelectorPP(
        spectra=background_pumped_index, pixel=pixel
    )
)
probed = pysfg.experiments.victor.pumpProbe(
    data,
    background_data,
    norm=norm.basesubed[pixel],
    data_select=pysfg.SelectorPP(spectra=probed_index, pixel=pixel),
    background_select=pysfg.SelectorPP(
        spectra=background_probed_index, pixel=pixel
    )
)

bleach = probed - pumped
