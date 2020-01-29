
import numpy as np
import pysfg

# Global Vairables likely to be changed
fpath = './data'
data_name = './data/cc_gold.dat'
spectrum_index = 0
pixel = slice(None)
background = 300 # Not really important for corsscorrelation (cc)


all_data = pysfg.read.victor.folder(fpath)
data = all_data[data_name]

cc = pysfg.experiments.victor.pumpProbe(
    data,
    background,
    data_select=pysfg.SelectorPP(spectra=spectrum_index, pixel=pixel),
)
