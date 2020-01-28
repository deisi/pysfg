"""Test and example of how to import and average a norm/quartz spectrum"""
import numpy as np
import pysfg

# Global Vairables likely to be changed
fpath = './data'
norm_name = './data/sc_quartz.dat'
norm_spectrum_index = 0
background_name = './data/bg_quartz.dat'
background_spectrum_index = norm_spectrum_index

# Import Data
all_data = pysfg.read.victor.folder(fpath)
# Select Data
norm_data = all_data[norm_name]
background_data = all_data[background_name]
# Generate Return object
norm = pysfg.experiments.victor.spectrum(
    norm_data,
    background_data,
    data_select=pysfg.SelectorPP(spectra=norm_spectrum_index),
    background_select=pysfg.SelectorPP(spectra=background_spectrum_index)
)

# Exercise:
# Use the pysfg.SelectorPP object to reduce the used pixels of norm
# into the range of 200-1400


# Exercise:
# Save norm as .json file and reimport the same with read_json
# from the spectrum module
norm.to_json('./data/norm.json')
