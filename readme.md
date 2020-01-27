# pysfg
Second attempt in getting a useful python library for our SFG setups.

## Install
- Install Anaconda for python3 64Bit
- Setup a conda environment with:
  `conda env create -f environment.yml`
- Activate the environment with:
  `conda activate sfg`
- Add a kernel to the default jupyterlab environment
  `ipython kernel install --user --name=sfg`
  
# Usage
## Read data
``` python3
import numpy as np
import pysfg

fpath = './data/00_sc_quartz_ssp_e10s_gal0.dat'
data = pysfg.read.victor.data_file(fpath)
# A dictionary with metadata and file data
data

# The raw file data
data['raw_data']

# Structured version of the data
data['data']

# The shape of the strcutured data is:
np.shape(data['data'])
(number_of_ppdelays, number_of_frames/scans, number_of_spectra, number_of_pixel)

# Import all data from a folder
all_data = pysfg.read.victor.folder('./')

# Data is a dict of dicts.
# Keys are the data file paths.
# Values is a data return dict
all_data.keys()
```

## Get calibration from data header
```python3
import pysfg

fname = './data/sc_quartz.dat'
data = pysfg.read.victor.data_file(fname)
wavenumber = pysfg.calibration.from_victor_header(data).wavenumber
```

Of if you just want to read the wavenumber from the file:
```python3

import pysfg
fname = './data/sc_quartz.dat'
wavenumber = pysfg.calibration.from_victor_file_wavenumber(fname)
```

